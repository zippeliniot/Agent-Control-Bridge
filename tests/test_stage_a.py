"""Stufe-A-Abnahmetest (BRIDGE-0055 Teil A). stdlib unittest, hermetisch.

Ablauf: create (Board) -> draft write (Executor-Klon) -> Transfer (Mensch) ->
import --dry-run -> import (Board-Klon). Kein Produktcode, nur Pruefung.
"""

import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import yaml
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from bridge.cli import main  # noqa: E402
from bridge.store import Store  # noqa: E402

SCHEMA_DIR = REPO_ROOT / "schemas"
TASK_ID = "BRIDGE-0900"


def _git(cwd, *args):
    proc = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True,
                          text=True, check=True)
    return proc.stdout.strip()


def _snapshot(root, names=("tasks", "results", "audit")):
    snap = {}
    for name in names:
        base = Path(root) / name
        for path in sorted(base.rglob("*")):
            if path.is_file():
                snap[str(path.relative_to(root))] = hashlib.sha256(
                    path.read_bytes()).hexdigest()
    return snap


def _cli(root, *argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = main(["--root", str(root), "--schema-dir", str(SCHEMA_DIR), *argv])
    return rc, out.getvalue(), err.getvalue()


class StageAAcceptance(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="acb-stage-a-"))
        self.origin = self.tmp / "origin.git"
        _git(self.tmp, "init", "--bare", "-b", "main", str(self.origin))
        seed = self.tmp / "seed"
        _git(self.tmp, "clone", str(self.origin), str(seed))
        for key, val in (("user.email", "test@example.com"), ("user.name", "Test")):
            _git(seed, "config", key, val)
        _git(seed, "checkout", "-b", "main")
        (seed / "README.md").write_text("init\n", encoding="utf-8")
        _git(seed, "add", "README.md")
        _git(seed, "commit", "-m", "initial")
        self.base_head = _git(seed, "rev-parse", "HEAD")
        for name in ("tasks", "results", "audit"):
            (seed / name).mkdir()
        store = Store(root=seed, schema_dir=SCHEMA_DIR)
        store.create_task({
            "schema_version": "1.0", "kind": "bridge_task",
            "bridge_task_id": TASK_ID, "project_id": "codex-control-bridge",
            "title": "Abnahme", "description": "Stufe A.",
            "task_class": "FEATURE", "repository": "x", "branch": "main",
            "permissions": ["READ_ONLY"], "status": "CREATED",
            "created_at": "2026-01-01T00:00:00Z", "created_by": "steuerprozess",
            "git": {"expected_head": self.base_head},
            "allowed_paths": ["src/"],
        })
        store.set_status(TASK_ID, "READY", "a")
        store.set_status(TASK_ID, "WAITING_FOR_HANDOFF_TO_EXECUTOR", "a")
        _git(seed, "add", "-A")
        _git(seed, "commit", "-m", "create task")
        _git(seed, "push", "-u", "origin", "main")
        self.executor = self.tmp / "executor"
        self.board = self.tmp / "board"
        for clone in (self.executor, self.board):
            _git(self.tmp, "clone", str(self.origin), str(clone))
            _git(clone, "config", "user.email", "test@example.com")
            _git(clone, "config", "user.name", "Test")
        self.store = Store(root=self.board, schema_dir=SCHEMA_DIR)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _executor_writes_draft(self):
        (self.executor / "src").mkdir()
        (self.executor / "src" / "a.py").write_text("x\n", encoding="utf-8")
        _git(self.executor, "add", "src/a.py")
        _git(self.executor, "commit", "-m", "work")
        rc, out, err = _cli(self.executor, "draft", "write", TASK_ID,
                            "--status", "COMPLETED", "--summary", "fertig",
                            "--tests", "5/0/0")
        self.assertEqual(rc, 0, err)

    def _transfer_to_board(self):
        """Uebergabe durch den Menschen (nicht der Executor pusht)."""
        _git(self.executor, "add", "drafts")
        _git(self.executor, "commit", "-m", "draft")
        _git(self.executor, "push", "origin", "main")
        _git(self.board, "pull", "--ff-only")

    def test_stage_a_end_to_end(self):
        origin_before = _git(self.origin, "rev-parse", "main")
        snap_exec = _snapshot(self.executor)

        self._executor_writes_draft()

        # Kein Push im Executor-Pfad; Executor schreibt nur drafts/ (+ Arbeitscode).
        self.assertEqual(_git(self.origin, "rev-parse", "main"), origin_before)
        self.assertEqual(_snapshot(self.executor), snap_exec)
        untracked = _git(self.executor, "status", "--porcelain", "-uall").splitlines()
        self.assertTrue(untracked)
        self.assertTrue(all(line[3:].startswith("drafts/") for line in untracked),
                        untracked)

        self._transfer_to_board()
        self.assertTrue(list((self.board / "drafts" / TASK_ID).rglob("draft.yaml")))

        # Dry-run: nichts wird geschrieben.
        snap_board = _snapshot(self.board)
        status_before = _git(self.board, "status", "--porcelain")
        with mock.patch.dict(os.environ, {"ACB_ALLOW_ANY_CLONE": "1"}):
            rc, out, err = _cli(self.board, "draft", "import", TASK_ID, "--dry-run")
        self.assertEqual(rc, 0, err)
        self.assertEqual(_snapshot(self.board), snap_board)
        self.assertEqual(_git(self.board, "status", "--porcelain"), status_before)
        self.assertEqual(self.store.load_task(TASK_ID)["status"],
                         "WAITING_FOR_HANDOFF_TO_EXECUTOR")

        # Import: Status + result.yaml + Audit.
        with mock.patch.dict(os.environ, {"ACB_ALLOW_ANY_CLONE": "1"}):
            rc, out, err = _cli(self.board, "draft", "import", TASK_ID)
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.store.load_task(TASK_ID)["status"],
                         "WAITING_FOR_COPY_TO_CONTROL")
        result_path = self.board / "results" / TASK_ID / "RUN-01" / "result.yaml"
        self.assertTrue(result_path.exists())
        result = yaml.safe_load(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["summary"], "fertig")
        self.assertIn("src/a.py", result["changed_files"])
        audit = (self.board / "audit" / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn(TASK_ID, audit)
        self.assertIn("RUN-01", audit)


if __name__ == "__main__":
    unittest.main()
