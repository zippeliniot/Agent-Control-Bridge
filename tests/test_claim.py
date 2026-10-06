"""BRIDGE-0061 Teil B: Claim/Lease-API und CLI."""

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from bridge import claim as claim_mod  # noqa: E402
from bridge import cli  # noqa: E402
from bridge.claim import ClaimError  # noqa: E402
from bridge.store import Store, StoreError  # noqa: E402
from tests.test_store import valid_task  # noqa: E402

SCHEMA_DIR = REPO_ROOT / "schemas"
T0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
TID = "BRIDGE-0900"


def _git(*args, cwd):
    """Fuehrt ein git-Kommando aus und gibt stdout zurueck (dekodiert)."""
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} fehlgeschlagen: {result.stderr.strip()}")
    return result.stdout.strip()


class ClaimTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="acb-claim-"))
        for name in ("tasks", "results", "audit"):
            (self.tmp / name).mkdir()
        self.store = Store(root=self.tmp, schema_dir=SCHEMA_DIR)
        self.store.create_task(valid_task())
        self.claim_file = self.tmp / "results" / TID / "claim.json"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def audit(self):
        f = self.tmp / "audit" / "audit.jsonl"
        return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]

    def stored(self):
        return json.loads(self.claim_file.read_text(encoding="utf-8"))

    # -- claim / release / renew ---------------------------------------

    def test_claim_writes_file_and_audit(self):
        doc = claim_mod.claim(self.store, TID, "claude-code", "HAM01", 600, now=T0)
        self.assertEqual(doc, self.stored())
        self.assertEqual(doc["actor"], "claude-code")
        self.assertEqual(doc["machine"], "HAM01")
        self.assertEqual(doc["expires_at"], "2026-01-01T12:10:00Z")
        last = self.audit()[-1]
        self.assertEqual(last["event_type"], "TASK_CLAIMED")
        self.assertIn("claim", last["reason"])

    def test_claim_unknown_task_rejected(self):
        with self.assertRaises(StoreError):
            claim_mod.claim(self.store, "BRIDGE-0999", "a", "M", 60, now=T0)

    def test_invalid_lease_rejected(self):
        for bad in (0, -5, "60", 1.5, True):
            with self.assertRaises(ClaimError):
                claim_mod.claim(self.store, TID, "a", "M", bad, now=T0)
        self.assertFalse(self.claim_file.exists())

    def test_foreign_active_claim_rejected(self):
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        before = self.claim_file.read_bytes()
        with self.assertRaises(ClaimError) as ctx:
            claim_mod.claim(self.store, TID, "b", "DES01", 600, now=T0 + timedelta(seconds=599))
        self.assertIn("CLAIM_CONFLICT", str(ctx.exception))
        self.assertEqual(self.claim_file.read_bytes(), before)

    def test_expired_claim_can_be_taken_over_with_audit_reason(self):
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        later = T0 + timedelta(seconds=600)
        doc = claim_mod.claim(self.store, TID, "b", "DES01", 300, now=later)
        self.assertEqual((doc["actor"], doc["machine"]), ("b", "DES01"))
        self.assertEqual(self.stored()["actor"], "b")
        reason = self.audit()[-1]["reason"]
        self.assertIn("takeover", reason)
        self.assertIn("a@HAM01", reason)

    def test_same_owner_reclaim_extends_without_audit(self):
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        n = len(self.audit())
        doc = claim_mod.claim(self.store, TID, "a", "HAM01", 900, now=T0 + timedelta(seconds=10))
        self.assertEqual(doc["expires_at"], "2026-01-01T12:15:10Z")
        self.assertEqual(doc["claimed_at"], "2026-01-01T12:00:00Z")
        self.assertEqual(len(self.audit()), n)

    def test_renew_by_owner_and_rejected_for_foreign_or_missing(self):
        with self.assertRaises(ClaimError):
            claim_mod.renew(self.store, TID, "a", "HAM01", 60, now=T0)
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        doc = claim_mod.renew(self.store, TID, "a", "HAM01", 600, now=T0 + timedelta(seconds=500))
        self.assertEqual(doc["expires_at"], "2026-01-01T12:18:20Z")
        with self.assertRaises(ClaimError):
            claim_mod.renew(self.store, TID, "b", "DES01", 600, now=T0)
        self.assertEqual(self.stored()["actor"], "a")

    def test_release_owner_removes_foreign_active_rejected(self):
        with self.assertRaises(ClaimError):
            claim_mod.release(self.store, TID, "a", "HAM01", now=T0)
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        with self.assertRaises(ClaimError):
            claim_mod.release(self.store, TID, "b", "DES01", now=T0 + timedelta(seconds=1))
        self.assertTrue(self.claim_file.exists())
        claim_mod.release(self.store, TID, "a", "HAM01", now=T0 + timedelta(seconds=1))
        self.assertFalse(self.claim_file.exists())
        self.assertIsNone(claim_mod.get_claim(self.store, TID))

    def test_release_expired_foreign_claim_allowed(self):
        claim_mod.claim(self.store, TID, "a", "HAM01", 60, now=T0)
        claim_mod.release(self.store, TID, "b", "DES01", now=T0 + timedelta(seconds=60))
        self.assertFalse(self.claim_file.exists())

    def test_corrupt_claim_file_fails_closed(self):
        self.claim_file.parent.mkdir(parents=True)
        self.claim_file.write_text("{kaputt", encoding="utf-8")
        with self.assertRaises(ClaimError):
            claim_mod.claim(self.store, TID, "a", "HAM01", 60, now=T0)

    # -- Ressourcenregel (BRIDGE-0063 Teil A) --------------------------

    def test_second_claim_on_same_resource_key_rejected(self):
        other = "BRIDGE-0901"
        self.store.create_task(valid_task(bridge_task_id=other))
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        with self.assertRaises(ClaimError) as ctx:
            claim_mod.claim(self.store, other, "b", "DES01", 600, now=T0 + timedelta(seconds=10))
        self.assertIn("RESOURCE_CONFLICT", str(ctx.exception))
        self.assertFalse((self.tmp / "results" / other / "claim.json").exists())

    def test_resource_conflict_gone_after_expiry_release_or_other_branch(self):
        other = "BRIDGE-0901"
        self.store.create_task(valid_task(bridge_task_id=other))
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        claim_mod.claim(self.store, other, "b", "DES01", 600, now=T0 + timedelta(seconds=600))
        claim_mod.release(self.store, other, "b", "DES01")
        claim_mod.release(self.store, TID, "a", "HAM01", now=T0)
        third = "BRIDGE-0902"
        self.store.create_task(valid_task(bridge_task_id=third, branch="feature-x"))
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        claim_mod.claim(self.store, third, "b", "DES01", 600, now=T0)

    def test_claim_file_does_not_disturb_next_run_id(self):
        claim_mod.claim(self.store, TID, "a", "HAM01", 60, now=T0)
        self.assertEqual(self.store.next_run_id(TID), "RUN-01")

    def test_runs_under_writer_lock(self):
        from bridge import lock as _lock
        with _lock.writer_lock(self.tmp):
            pass  # Lock frei -> claim funktioniert
        held = Store(root=self.tmp, schema_dir=SCHEMA_DIR, lock_timeout=0.1)
        lock_file = _lock.lock_path(self.tmp)
        lock_file.write_text('{"pid": 1}\n', encoding="utf-8")  # fremder Halter
        try:
            with self.assertRaises(ClaimError):
                claim_mod.claim(held, TID, "a", "HAM01", 60, now=T0)
        finally:
            lock_file.unlink()
        self.assertFalse(self.claim_file.exists())


class ClaimCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="acb-claimcli-"))
        for name in ("tasks", "results", "audit"):
            (self.tmp / name).mkdir()
        Store(root=self.tmp, schema_dir=SCHEMA_DIR).create_task(valid_task())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = cli.main(["--root", str(self.tmp), "--schema-dir", str(SCHEMA_DIR), *argv])
        return rc, out.getvalue(), err.getvalue()

    def test_claim_renew_release_cycle(self):
        rc, out, _ = self.run_cli("claim", TID, "--actor", "a", "--machine", "HAM01",
                                  "--lease-seconds", "600")
        self.assertEqual(rc, 0)
        self.assertIn("expires_at=", out)
        rc, _, _ = self.run_cli("renew", TID, "--actor", "a", "--machine", "HAM01")
        self.assertEqual(rc, 0)
        rc, _, _ = self.run_cli("release", TID, "--actor", "a", "--machine", "HAM01")
        self.assertEqual(rc, 0)
        self.assertFalse((self.tmp / "results" / TID / "claim.json").exists())

    def test_foreign_claim_exit_1(self):
        self.run_cli("claim", TID, "--actor", "a", "--machine", "HAM01")
        rc, _, err = self.run_cli("claim", TID, "--actor", "b", "--machine", "DES01")
        self.assertEqual(rc, 1)
        self.assertIn("CLAIM_CONFLICT", err)


class ClaimGitSyncTests(unittest.TestCase):
    """BRIDGE-0078: claim/renew/release committen+pushen, Push-Race-Rollback,
    klonuebergreifende Sichtbarkeit - mit echten bare-Repos (Infrastruktur
    analog tests/test_gitops.py GitCommitRetryTests/GitPullTests).

    - self.tmp         = eigener Klon, hier laufen die claim_mod-Aufrufe.
    - self.bare         = bare-Repo als gemeinsamer 'origin'.
    - self.other/_store = zweiter Klon, simuliert die andere Maschine.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="acb-claimgit-"))
        self.bare = Path(tempfile.mkdtemp(prefix="acb-claimgit-bare-"))
        _git("init", "-b", "main", cwd=self.tmp)
        _git("config", "user.email", "test@example.com", cwd=self.tmp)
        _git("config", "user.name", "Test", cwd=self.tmp)
        for name in ("tasks", "results", "audit"):
            (self.tmp / name).mkdir()
        self.store = Store(root=self.tmp, schema_dir=SCHEMA_DIR)
        self.store.create_task(valid_task())
        _git("add", "-A", cwd=self.tmp)
        _git("commit", "-m", "initial store", cwd=self.tmp)
        _git("clone", "--bare", str(self.tmp), str(self.bare), cwd=self.tmp)
        _git("remote", "add", "origin", str(self.bare), cwd=self.tmp)
        _git("push", "--set-upstream", "origin", "main", cwd=self.tmp)

        # Zweiter Klon NACH dem initialen Push - simuliert die andere Maschine.
        self.other = Path(tempfile.mkdtemp(prefix="acb-claimgit-other-"))
        _git("clone", str(self.bare), str(self.other), cwd=self.tmp)
        _git("config", "user.email", "test@example.com", cwd=self.other)
        _git("config", "user.name", "Test", cwd=self.other)
        for name in ("results", "audit"):
            (self.other / name).mkdir(exist_ok=True)
        self.other_store = Store(root=self.other, schema_dir=SCHEMA_DIR)
        self.claim_file = self.tmp / "results" / TID / "claim.json"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(self.bare, ignore_errors=True)
        shutil.rmtree(self.other, ignore_errors=True)

    def _head(self, repo):
        return _git("rev-parse", "HEAD", cwd=repo)

    def _push_conflicting_claim(self, content: str, delete: bool = False):
        """'other' setzt results/<TID>/claim.json auf einen abweichenden
        Inhalt (oder loescht sie) und pusht - erzwingt beim naechsten Push
        aus self.tmp einen echten Rebase-Konflikt auf genau dieser Datei
        (Push-Race-Simulation, WP-Vorgabe)."""
        _git("fetch", "origin", cwd=self.other)
        _git("reset", "--hard", "origin/main", cwd=self.other)
        path = self.other / "results" / TID / "claim.json"
        if delete:
            path.unlink()
            _git("add", "results/BRIDGE-0900/claim.json", cwd=self.other)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            _git("add", "results/BRIDGE-0900/claim.json", cwd=self.other)
        _git("commit", "-m", "conflicting claim change", cwd=self.other)
        _git("push", cwd=self.other)

    # -- Teil B Punkt 2/3: committen+pushen -----------------------------

    def test_claim_commits_and_pushes(self):
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        self.assertEqual(
            _git("log", "-1", "--format=%s", cwd=self.tmp),
            "Ops: BRIDGE-0900 claim claim (Steuerchat-Aktion via CLI)")
        # Im bare-Repo sichtbar (gepusht), nicht nur lokal.
        remote_text = _git("show", "origin/main:results/BRIDGE-0900/claim.json", cwd=self.tmp)
        self.assertEqual(json.loads(remote_text)["actor"], "a")

    def test_renew_and_release_also_push(self):
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        claim_mod.renew(self.store, TID, "a", "HAM01", 900,
                        now=T0 + timedelta(seconds=10))
        self.assertIn("renew", _git("log", "-1", "--format=%s", cwd=self.tmp))
        claim_mod.release(self.store, TID, "a", "HAM01",
                          now=T0 + timedelta(seconds=20))
        self.assertIn("release", _git("log", "-1", "--format=%s", cwd=self.tmp))
        with self.assertRaises(RuntimeError):
            # Datei existiert weder lokal noch im Remote mehr.
            _git("show", "origin/main:results/BRIDGE-0900/claim.json", cwd=self.tmp)

    # -- Teil B Punkt 48: Cross-Klon-Sichtbarkeit ------------------------

    def test_cross_clone_second_claim_on_same_resource_rejected(self):
        # 'other' hat lokal noch nichts von diesem Claim - ohne BRIDGE-0078
        # waere 'current' dort None und der zweite claim() wuerde einfach
        # durchgehen. Mit versioniertem claim.json erkennt _synced_claim den
        # fremden Claim ueber origin/main und lehnt mit CLAIM_CONFLICT ab
        # (derselbe Auftrag ist fremd geclaimt - nicht RESOURCE_CONFLICT,
        # das gilt fuer EINEN anderen Auftrag auf demselben Schluessel).
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        with self.assertRaises(ClaimError) as ctx:
            claim_mod.claim(self.other_store, TID, "b", "DES01", 600, now=T0)
        self.assertIn("CLAIM_CONFLICT", str(ctx.exception))
        self.assertIn("a@HAM01", str(ctx.exception))

    def test_cross_clone_visible_after_expiry_allows_takeover(self):
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        later = T0 + timedelta(seconds=601)
        doc = claim_mod.claim(self.other_store, TID, "b", "DES01", 600, now=later)
        self.assertEqual((doc["actor"], doc["machine"]), ("b", "DES01"))

    # -- Teil B Punkt 3/4: Push-Race-Rollback, je Aktion -----------------

    def test_claim_push_race_rolls_back_new_claim(self):
        # Echte Race: 'other' claimt UND pusht erst NACHDEM die eigene
        # Pruefung (_synced_claim) schon "nichts gefunden" gemeldet hat -
        # genau das wird hier simuliert, indem _synced_claim fuer diesen
        # einen Aufruf auf "kein Claim bekannt" gepatcht wird. Der danach
        # folgende echte Commit+Push trifft auf den laengst von 'other'
        # gepushten Claim und muss am Push scheitern + zurueckrollen.
        claim_mod.claim(self.other_store, TID, "other", "DES01", 600, now=T0)
        head_before = self._head(self.tmp)
        with unittest.mock.patch.object(claim_mod, "_synced_claim", lambda *a, **k: None):
            with self.assertRaises(ClaimError) as ctx:
                claim_mod.claim(self.store, TID, "me", "HAM01", 300, now=T0)
        self.assertIn("RESOURCE_CONFLICT", str(ctx.exception))
        self.assertFalse(self.claim_file.exists())
        self.assertEqual(self._head(self.tmp), head_before)

    def test_renew_push_race_rolls_back_to_previous_claim(self):
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        before_text = self.claim_file.read_text(encoding="utf-8")
        own_claim = json.loads(before_text)
        head_before = self._head(self.tmp)
        # Race: 'other' pusht eine abweichende claim.json fuer denselben
        # Auftrag, NACHDEM die eigene Pruefung (hier gepatcht) bereits den
        # eigenen Claim als massgeblich gemeldet hat.
        self._push_conflicting_claim('{"actor": "x", "machine": "Y", '
                                     '"claimed_at": "2026-01-01T12:00:00Z", '
                                     '"expires_at": "2099-01-01T00:00:00Z", '
                                     '"lease_seconds": 60}')
        with unittest.mock.patch.object(claim_mod, "_synced_claim", lambda *a, **k: own_claim):
            with self.assertRaises(ClaimError) as ctx:
                claim_mod.renew(self.store, TID, "a", "HAM01", 900,
                                now=T0 + timedelta(seconds=10))
        self.assertIn("RESOURCE_CONFLICT", str(ctx.exception))
        self.assertEqual(self.claim_file.read_text(encoding="utf-8"), before_text)
        self.assertEqual(self._head(self.tmp), head_before)

    def test_release_push_race_rolls_back_restores_claim(self):
        claim_mod.claim(self.store, TID, "a", "HAM01", 600, now=T0)
        before_text = self.claim_file.read_text(encoding="utf-8")
        own_claim = json.loads(before_text)
        head_before = self._head(self.tmp)
        self._push_conflicting_claim('{"actor": "x", "machine": "Y", '
                                     '"claimed_at": "2026-01-01T12:00:00Z", '
                                     '"expires_at": "2099-01-01T00:00:00Z", '
                                     '"lease_seconds": 60}')
        with unittest.mock.patch.object(claim_mod, "_synced_claim", lambda *a, **k: own_claim):
            with self.assertRaises(ClaimError) as ctx:
                claim_mod.release(self.store, TID, "a", "HAM01",
                                  now=T0 + timedelta(seconds=20))
        self.assertIn("RESOURCE_CONFLICT", str(ctx.exception))
        self.assertTrue(self.claim_file.exists())
        self.assertEqual(self.claim_file.read_text(encoding="utf-8"), before_text)
        self.assertEqual(self._head(self.tmp), head_before)

    # -- Kein Git-Repo (hermetisch) bleibt no-op -------------------------

    def test_no_git_repo_sync_is_noop(self):
        tmp2 = Path(tempfile.mkdtemp(prefix="acb-claimgit-plain-"))
        try:
            for name in ("tasks", "results", "audit"):
                (tmp2 / name).mkdir()
            store2 = Store(root=tmp2, schema_dir=SCHEMA_DIR)
            store2.create_task(valid_task())
            doc = claim_mod.claim(store2, TID, "a", "HAM01", 600, now=T0)
            self.assertEqual(doc["actor"], "a")
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
