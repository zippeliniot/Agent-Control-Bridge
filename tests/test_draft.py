"""Tests fuer draft write (BRIDGE-0053 Teil A). stdlib unittest, echtes Temp-Git."""

import hashlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from bridge import draft, gitops, runner  # noqa: E402
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


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="acb-draft-"))
        _git(self.tmp, "init", "-b", "main")
        _git(self.tmp, "config", "user.email", "test@example.com")
        _git(self.tmp, "config", "user.name", "Test")
        (self.tmp / "README.md").write_text("init\n", encoding="utf-8")
        _git(self.tmp, "add", "README.md")
        _git(self.tmp, "commit", "-m", "initial")
        self.base_head = _git(self.tmp, "rev-parse", "HEAD")
        for name in ("tasks", "results", "audit"):
            (self.tmp / name).mkdir()
        self.store = Store(root=self.tmp, schema_dir=SCHEMA_DIR)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make_task(self, **over):
        doc = {
            "schema_version": "1.0", "kind": "bridge_task",
            "bridge_task_id": TASK_ID, "project_id": "codex-control-bridge",
            "title": "Testauftrag", "description": "Nur fuer Tests.",
            "task_class": "FEATURE", "repository": "x", "branch": "main",
            "permissions": ["READ_ONLY"], "status": "CREATED",
            "created_at": "2026-01-01T00:00:00Z", "created_by": "steuerprozess",
            "git": {"expected_head": self.base_head},
            "allowed_paths": ["src/"],
        }
        doc.update(over)
        self.store.create_task(doc)
        runner.start(self.store, TASK_ID, "claude-code", machine="HAM11")
        self.commit_all("ops")

    def commit_all(self, msg):
        _git(self.tmp, "add", "-A")
        _git(self.tmp, "commit", "-m", msg)

    def work_commit(self, relpath):
        path = self.tmp / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n", encoding="utf-8")
        self.commit_all("work")

    def cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(["--root", str(self.tmp), "--schema-dir", str(SCHEMA_DIR), *argv])
        return rc, out.getvalue(), err.getvalue()


class WriteTests(Base):
    def test_write_creates_valid_draft(self):
        self.make_task()
        self.work_commit("src/a.py")
        rc, out, err = self.cli("draft", "write", TASK_ID, "--status", "COMPLETED",
                                "--summary", "fertig", "--tests", "5/0/1")
        self.assertEqual(rc, 0, err)
        doc = self.store.load_draft(TASK_ID, "RUN-01")
        self.store.validate(doc)
        self.assertEqual(doc["status"], "COMPLETED")
        self.assertEqual(doc["tests"], {"passed": 5, "failed": 0, "blocked": 1})
        self.assertEqual(doc["base_head"], self.base_head)
        self.assertIn("src/a.py", doc["changed_files"])
        self.assertNotIn("error_code", doc)

    def test_missing_expected_head_fails_closed(self):
        self.make_task(git={"allowed_changed_files": ["src/"]})
        rc, _, err = self.cli("draft", "write", TASK_ID, "--status", "COMPLETED",
                              "--summary", "x")
        self.assertEqual(rc, 1)
        self.assertIn("expected_head", err)
        self.assertFalse((self.tmp / "drafts").exists())

    def test_scope_violation_blocks_with_code(self):
        self.make_task()
        self.work_commit("docs/out.md")
        rc, out, err = self.cli("draft", "write", TASK_ID, "--status", "COMPLETED",
                                "--summary", "x")
        self.assertEqual(rc, 0, err)
        doc = self.store.load_draft(TASK_ID, "RUN-01")
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertEqual(doc["error_code"], "SCOPE_VIOLATION")
        self.assertIn("docs/out.md", doc["findings"][0]["text"])

    def test_dirty_worktree_refused(self):
        self.make_task()
        (self.tmp / "loose.txt").write_text("x", encoding="utf-8")
        rc, _, err = self.cli("draft", "write", TASK_ID, "--status", "COMPLETED",
                              "--summary", "x")
        self.assertEqual(rc, 1)
        self.assertIn("DIRTY_WORKTREE", err)
        self.assertFalse((self.tmp / "drafts").exists())

    def test_bad_tests_format_rejected(self):
        with self.assertRaises(draft.DraftError):
            draft.parse_tests("12")

    def test_no_writes_to_tasks_results_audit_and_no_push(self):
        self.make_task()
        self.work_commit("src/a.py")
        before = _snapshot(self.tmp)
        rc, _, err = self.cli("draft", "write", TASK_ID, "--status", "COMPLETED",
                              "--summary", "x", "--commit")
        self.assertEqual(rc, 0, err)
        self.assertEqual(_snapshot(self.tmp), before)
        # kein Remote konfiguriert: ein Push waere gescheitert, der Commit ist lokal
        self.assertEqual(_git(self.tmp, "remote"), "")

    def test_commit_commits_only_draft_file(self):
        self.make_task()
        self.work_commit("src/a.py")
        rc, out, err = self.cli("draft", "write", TASK_ID, "--status", "COMPLETED",
                                "--summary", "x", "--commit")
        self.assertEqual(rc, 0, err)
        files = _git(self.tmp, "show", "--name-only", "--format=", "HEAD").split()
        self.assertEqual(files, [f"drafts/{TASK_ID}/RUN-01/draft.yaml"])
        self.assertEqual(_git(self.tmp, "status", "--porcelain"), "")

    def test_commit_whitelist_is_draft_file_only(self):
        self.assertEqual(gitops.expected_git_files("draft_write", TASK_ID, "RUN-01"),
                         [f"drafts/{TASK_ID}/RUN-01/draft.yaml"])
        self.assertEqual(gitops.expected_git_files("draft_write", TASK_ID), [])


if __name__ == "__main__":
    unittest.main()
