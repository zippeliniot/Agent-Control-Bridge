"""Hermetische Tests für den Writer-Lock (BRIDGE-0060 Teil B). stdlib unittest."""

import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from bridge.lock import LOCK_NAME, WriterLockError, lock_path, writer_lock  # noqa: E402
from bridge.store import Store, StoreError  # noqa: E402

SCHEMA_DIR = REPO_ROOT / "schemas"
TS = "2026-01-01T00:00:00Z"


def valid_task(**over):
    doc = {
        "schema_version": "1.0",
        "kind": "bridge_task",
        "bridge_task_id": "BRIDGE-0900",
        "project_id": "codex-control-bridge",
        "title": "Testauftrag",
        "description": "Nur für Tests.",
        "task_class": "FEATURE",
        "repository": "Codex-Control-Bridge",
        "branch": "main",
        "permissions": ["READ_ONLY"],
        "status": "CREATED",
        "created_at": TS,
        "created_by": "steuerprozess",
    }
    doc.update(over)
    return doc


class WriterLockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="acb-lock-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_creates_lockfile_with_pid_and_removes_it(self):
        with writer_lock(self.tmp):
            data = json.loads(lock_path(self.tmp).read_text(encoding="utf-8"))
            self.assertEqual(data["pid"], os.getpid())
            self.assertIn("time", data)
        self.assertFalse(lock_path(self.tmp).exists())

    def test_lockfile_removed_after_exception(self):
        with self.assertRaises(RuntimeError):
            with writer_lock(self.tmp):
                raise RuntimeError("boom")
        self.assertFalse(lock_path(self.tmp).exists())

    def test_reentrant_in_same_thread(self):
        with writer_lock(self.tmp):
            with writer_lock(self.tmp, timeout=0.1):
                self.assertTrue(lock_path(self.tmp).exists())
            # innerer Ausgang gibt den Lock nicht frei
            self.assertTrue(lock_path(self.tmp).exists())
        self.assertFalse(lock_path(self.tmp).exists())

    def test_second_writer_fails_cleanly_after_timeout(self):
        errors = []

        def other():
            try:
                with writer_lock(self.tmp, timeout=0.2):
                    pass
            except WriterLockError as exc:
                errors.append(exc)

        with writer_lock(self.tmp):
            t = threading.Thread(target=other)
            t.start()
            t.join(5)
        self.assertEqual(len(errors), 1)
        self.assertIn("nicht erhalten", str(errors[0]))
        self.assertFalse(lock_path(self.tmp).exists())

    def test_second_writer_waits_for_release(self):
        acquired = []
        entered = threading.Event()
        release = threading.Event()

        def first():
            with writer_lock(self.tmp):
                entered.set()
                release.wait(5)

        def second():
            with writer_lock(self.tmp, timeout=5):
                acquired.append(True)

        t1 = threading.Thread(target=first)
        t1.start()
        self.assertTrue(entered.wait(5))
        t2 = threading.Thread(target=second)
        t2.start()
        t2.join(0.3)
        self.assertEqual(acquired, [])  # wartet noch
        release.set()
        t1.join(5)
        t2.join(5)
        self.assertEqual(acquired, [True])

    def test_stale_lock_is_reported_not_broken(self):
        path = lock_path(self.tmp)
        path.write_text('{"pid": 4242, "time": "2020-01-01T00:00:00Z"}\n',
                        encoding="utf-8")
        old = path.stat().st_mtime - 1000
        os.utime(path, (old, old))
        with self.assertRaises(WriterLockError) as ctx:
            with writer_lock(self.tmp, timeout=0.2):
                self.fail("Lock darf nicht erteilt werden")
        self.assertIn("Veralteter", str(ctx.exception))
        self.assertIn("4242", str(ctx.exception))
        self.assertTrue(path.exists())  # nicht gebrochen
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["pid"], 4242)


class StoreLockTests(unittest.TestCase):
    """Alle Store-Schreibpfade laufen unter dem Lock."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="acb-storelock-"))
        for name in ("tasks", "results", "audit"):
            (self.tmp / name).mkdir()
        self.store = Store(root=self.tmp, schema_dir=SCHEMA_DIR, lock_timeout=0.2)
        self.store.create_task(valid_task())
        self.lockfile = self.tmp / LOCK_NAME

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _hold_foreign_lock(self):
        # Fremder Halter: frische Lockdatei, die nicht von diesem Thread stammt.
        self.lockfile.write_text('{"pid": 1, "time": "2026-01-01T00:00:00Z"}\n',
                                 encoding="utf-8")

    def test_lock_released_after_each_write(self):
        self.assertFalse(self.lockfile.exists())
        self.store.set_priority("BRIDGE-0900", "HIGH", actor="t")
        self.assertFalse(self.lockfile.exists())

    def test_every_write_path_is_blocked_by_foreign_lock(self):
        self._hold_foreign_lock()
        calls = {
            "create_task": lambda: self.store.create_task(
                valid_task(bridge_task_id="BRIDGE-0901")),
            "save_task": lambda: self.store.save_task(valid_task(title="X")),
            "set_status": lambda: self.store.set_status(
                "BRIDGE-0900", "WAITING_FOR_HANDOFF_TO_EXECUTOR", actor="t"),
            "set_priority": lambda: self.store.set_priority(
                "BRIDGE-0900", "HIGH", actor="t"),
            "append_audit": lambda: self.store.append_audit({
                "event_type": "TASK_CREATED", "timestamp": TS, "actor": "t",
                "bridge_task_id": "BRIDGE-0900"}),
        }
        for name, call in calls.items():
            with self.subTest(name):
                with self.assertRaises(StoreError) as ctx:
                    call()
                self.assertIn("Writer-Lock", str(ctx.exception))
        self.assertTrue(self.lockfile.exists())  # Fremdlock unangetastet

    def test_stale_foreign_lock_raises_store_error_with_hint(self):
        self._hold_foreign_lock()
        old = self.lockfile.stat().st_mtime - 1000
        os.utime(self.lockfile, (old, old))
        with self.assertRaises(StoreError) as ctx:
            self.store.set_priority("BRIDGE-0900", "HIGH", actor="t")
        self.assertIn("Veralteter", str(ctx.exception))
        self.assertTrue(self.lockfile.exists())

    def test_audit_append_writes_complete_lf_lines(self):
        self.store.set_priority("BRIDGE-0900", "HIGH", actor="t")
        raw = (self.tmp / "audit" / "audit.jsonl").read_bytes()
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"\r", raw)
        for line in raw.splitlines():
            json.loads(line.decode("utf-8"))


class GitignoreTests(unittest.TestCase):
    def test_lockfile_in_gitignore(self):
        lines = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(LOCK_NAME, [x.strip() for x in lines])


if __name__ == "__main__":
    unittest.main()
