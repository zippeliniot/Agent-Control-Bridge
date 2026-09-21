"""BRIDGE-0063 Teil B: Parallelitaets- und Ausfalltests fuer Lock und Claim.

Echte Subprozesse (dieselbe Datei als Worker). Synchronisation ueber Dateien
(``go``/``release``), keine langen Wartezeiten: der Verlierer eines Locks gibt
nach 0.5 s auf. stdlib unittest, kein Produktcode.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

from bridge import claim as claim_mod  # noqa: E402
from bridge import lock as lock_mod  # noqa: E402
from bridge import store as store_mod  # noqa: E402
from bridge.store import Store  # noqa: E402

SCHEMA_DIR = REPO_ROOT / "schemas"
LOSER_TIMEOUT = 0.5
WAIT_LIMIT = 30.0
T0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _wait_for(predicate, limit=WAIT_LIMIT):
    deadline = time.monotonic() + limit
    while not predicate():
        if time.monotonic() > deadline:
            raise TimeoutError("Bedingung nicht eingetreten")
        time.sleep(0.005)


# -- Worker (Subprozess) -------------------------------------------------

def _worker(argv):
    mode, root = argv[0], Path(argv[1])
    if mode == "lock":
        tag, go, release = argv[2], Path(argv[3]), Path(argv[4])
        _wait_for(go.exists)
        try:
            with lock_mod.writer_lock(root, LOSER_TIMEOUT):
                (root / f"held-{tag}").write_text("1", encoding="utf-8")
                _wait_for(release.exists)
        except lock_mod.WriterLockError:
            print("LOST")
            return
        print("WON")
    elif mode == "claim":
        task_id, actor, go = argv[2], argv[3], Path(argv[4])
        _wait_for(go.exists)
        store = Store(root=root, schema_dir=SCHEMA_DIR)
        try:
            claim_mod.claim(store, task_id, actor, "M-" + actor, 600)
        except claim_mod.ClaimError as exc:
            print(json.dumps({"ok": False, "error": str(exc)}))
            return
        print(json.dumps({"ok": True, "error": ""}))
    elif mode == "crash_write":
        target = argv[2]
        store_mod.os.replace = lambda *a, **k: os._exit(3)
        store_mod._atomic_write(target, "neu\n")
    elif mode == "crash_lock":
        with lock_mod.writer_lock(root, LOSER_TIMEOUT):
            os._exit(9)
    elif mode == "crash_claim":
        task_id = argv[2]
        store = Store(root=root, schema_dir=SCHEMA_DIR)
        store.append_audit = lambda *a, **k: os._exit(9)  # stirbt nach claim.json, vor Freigabe
        claim_mod.claim(store, task_id, "dead", "M-dead", 60, now=T0)
    else:
        raise SystemExit(f"unbekannter Modus: {mode}")


def _spawn(*args):
    return subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), *map(str, args)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        cwd=str(REPO_ROOT))


def _finish(proc):
    out, err = proc.communicate(timeout=WAIT_LIMIT)
    return proc.returncode, out.strip(), err


# -- Tests ---------------------------------------------------------------

class ParallelBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="acb-parallel-"))
        for name in ("tasks", "results", "audit"):
            (self.tmp / name).mkdir()
        self.store = Store(root=self.tmp, schema_dir=SCHEMA_DIR)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def new_task(self, task_id):
        from tests.test_store import valid_task
        self.store.create_task(valid_task(bridge_task_id=task_id))


class ParallelTests(ParallelBase):
    def test_same_lock_exactly_one_wins(self):
        go, release = self.tmp / "go", self.tmp / "release"
        procs = {tag: _spawn("lock", self.tmp, tag, go, release) for tag in ("a", "b")}
        go.write_text("1", encoding="utf-8")
        _wait_for(lambda: any((self.tmp / f"held-{t}").exists() for t in procs))
        holders = [t for t in procs if (self.tmp / f"held-{t}").exists()]
        self.assertEqual(len(holders), 1)
        loser = next(t for t in procs if t not in holders)
        self.assertEqual(_finish(procs[loser])[:2], (0, "LOST"))
        release.write_text("1", encoding="utf-8")
        self.assertEqual(_finish(procs[holders[0]])[:2], (0, "WON"))
        self.assertFalse(lock_mod.lock_path(self.tmp).exists())

    def _race_claims(self, jobs):
        go = self.tmp / "go"
        procs = [_spawn("claim", self.tmp, tid, actor, go) for tid, actor in jobs]
        go.write_text("1", encoding="utf-8")
        results = []
        for proc in procs:
            code, out, err = _finish(proc)
            self.assertEqual(code, 0, err)
            results.append(json.loads(out))
        self.assertEqual(sum(r["ok"] for r in results), 1, results)
        return next(r for r in results if not r["ok"])["error"]

    def test_same_claim_exactly_one_wins(self):
        self.new_task("BRIDGE-0900")
        error = self._race_claims([("BRIDGE-0900", "a"), ("BRIDGE-0900", "b")])
        self.assertIn("CLAIM_CONFLICT", error)

    def test_same_resource_key_exactly_one_wins(self):
        self.new_task("BRIDGE-0900")
        self.new_task("BRIDGE-0901")
        error = self._race_claims([("BRIDGE-0900", "a"), ("BRIDGE-0901", "b")])
        self.assertIn("RESOURCE_CONFLICT", error)


class CrashTests(ParallelBase):
    def test_crash_mid_write_keeps_file_intact(self):
        target = self.tmp / "daten.txt"
        target.write_text("alt\n", encoding="utf-8")
        code, _, _ = _finish(_spawn("crash_write", self.tmp, target))
        self.assertEqual(code, 3)
        self.assertEqual(target.read_text(encoding="utf-8"), "alt\n")

    def test_dead_lock_holder_detected_as_stale(self):
        code, _, _ = _finish(_spawn("crash_lock", self.tmp))
        self.assertEqual(code, 9)
        path = lock_mod.lock_path(self.tmp)
        self.assertTrue(path.exists())
        old = time.time() - lock_mod.STALE_SECONDS - 60
        os.utime(path, (old, old))
        with self.assertRaises(lock_mod.WriterLockError) as ctx:
            with lock_mod.writer_lock(self.tmp, LOSER_TIMEOUT):
                self.fail("veralteter Lock darf nicht erhalten werden")
        self.assertIn("Veralteter", str(ctx.exception))
        self.assertTrue(path.exists(), "Lock wird nicht automatisch gebrochen")

    def test_dead_claimant_claim_becomes_stale_and_is_taken_over(self):
        self.new_task("BRIDGE-0900")
        code, _, _ = _finish(_spawn("crash_claim", self.tmp, "BRIDGE-0900"))
        self.assertEqual(code, 9)
        dead = claim_mod.get_claim(self.store, "BRIDGE-0900")
        self.assertEqual(dead["actor"], "dead")  # Datei intakt und lesbar
        # Der tote Prozess hat den Writer-Lock nicht freigegeben -> von Hand entfernt.
        lock_mod.lock_path(self.tmp).unlink()
        later = T0 + timedelta(seconds=61)
        doc = claim_mod.claim(self.store, "BRIDGE-0900", "b", "M-b", 60, now=later)
        self.assertEqual(doc["actor"], "b")
        audit = (self.tmp / "audit" / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn("takeover expired claim", audit)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        _worker(sys.argv[1:])
    else:
        unittest.main()
