"""BRIDGE-0061 Teil B: Claim/Lease-API und CLI."""

import io
import json
import shutil
import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
