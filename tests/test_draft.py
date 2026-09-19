"""Tests fuer draft write (BRIDGE-0053 Teil A). stdlib unittest, echtes Temp-Git."""

import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import yaml
from unittest import mock
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

    def make_task(self, start=True, **over):
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
        if start:
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

    def test_write_without_run_start(self):
        self.make_task(start=False)
        self.store.set_status(TASK_ID, "READY", "a")
        self.store.set_status(TASK_ID, "WAITING_FOR_HANDOFF_TO_EXECUTOR", "a")
        self.commit_all("ops")
        self.work_commit("src/a.py")
        before = _snapshot(self.tmp)
        rc, out, err = self.cli("draft", "write", TASK_ID, "--status", "COMPLETED",
                                "--summary", "fertig", "--tests", "1/0/0")
        self.assertEqual(rc, 0, err)
        self.assertEqual(_snapshot(self.tmp), before)
        self.assertEqual(self.store.load_task(TASK_ID)["status"],
                         "WAITING_FOR_HANDOFF_TO_EXECUTOR")
        self.assertEqual(self.store.load_draft(TASK_ID, "RUN-01")["run_id"], "RUN-01")
        with mock.patch.dict(os.environ, {"ACB_ALLOW_ANY_CLONE": "1"}):
            rc, out, err = self.cli("draft", "import", TASK_ID)
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.store.load_task(TASK_ID)["status"],
                         "WAITING_FOR_COPY_TO_CONTROL")

    def test_write_uses_running_run(self):
        self.make_task()
        self.work_commit("src/a.py")
        rc, _, err = self.cli("draft", "write", TASK_ID, "--status", "COMPLETED",
                              "--summary", "x")
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.store.load_draft(TASK_ID, "RUN-01")["run_id"],
                         runner.current_run_id(self.store, TASK_ID))

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


class ImportTests(Base):
    def setUp(self):
        super().setUp()
        patcher = mock.patch.dict(os.environ, {"ACB_ALLOW_ANY_CLONE": "1"})
        patcher.start()
        self.addCleanup(patcher.stop)

    def created_task(self, task_over=None, **draft_over):
        """Auftrag im Status CREATED (kein Lauf) + Draft RUN-01."""
        task = {
            "schema_version": "1.0", "kind": "bridge_task",
            "bridge_task_id": TASK_ID, "project_id": "codex-control-bridge",
            "title": "Testauftrag", "description": "Nur fuer Tests.",
            "task_class": "FEATURE", "repository": "x", "branch": "main",
            "permissions": ["READ_ONLY"], "status": "CREATED",
            "created_at": "2026-01-01T00:00:00Z", "created_by": "steuerprozess",
            "git": {"expected_head": self.base_head},
        }
        task.update(task_over or {})
        self.store.create_task(task)
        doc = {
            "kind": "bridge_draft", "draft_version": "draft-a-1",
            "bridge_task_id": TASK_ID, "run_id": "RUN-01", "status": "COMPLETED",
            "summary": "fertig", "base_head": self.base_head,
            "head_after": self.base_head, "branch": "main", "repository": "x",
            "changed_files": ["src/a.py"],
            "tests": {"passed": 1, "failed": 0, "blocked": 0},
            "findings": [], "next_action": "",
        }
        doc.update(draft_over)
        self.store.write_draft(doc)

    def test_dry_run_writes_nothing(self):
        self.created_task()
        before = _snapshot(self.tmp, ("tasks", "results", "audit", "drafts"))
        rc, out, err = self.cli("draft", "import", TASK_ID, "--dry-run")
        self.assertEqual(rc, 0, err)
        self.assertIn("DRY-RUN", out)
        self.assertIn("runner.start", out)
        self.assertIn("runner.finish", out)
        self.assertEqual(_snapshot(self.tmp, ("tasks", "results", "audit", "drafts")),
                         before)

    def test_import_creates_result_and_audit(self):
        self.created_task()
        rc, out, err = self.cli("draft", "import", TASK_ID)
        self.assertEqual(rc, 0, err)
        result = yaml.safe_load(
            (self.tmp / "results" / TASK_ID / "RUN-01" / "result.yaml")
            .read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["summary"], "fertig")
        self.assertEqual(result["head"], self.base_head)
        self.assertEqual(self.store.load_task(TASK_ID)["status"],
                         "WAITING_FOR_COPY_TO_CONTROL")
        audit = (self.tmp / "audit" / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn("TASK_STARTED", audit)
        self.assertIn("RESULT", audit.upper())

    def test_import_keeps_tests_findings_and_code(self):
        finding = {"id": "SCOPE-1", "severity": "high", "text": "ausserhalb"}
        self.created_task(status="BLOCKED", error_code="SCOPE_VIOLATION",
                          summary="Abbruch", tests={"passed": 3, "failed": 1, "blocked": 0},
                          findings=[finding])
        rc, out, err = self.cli("draft", "import", TASK_ID)
        self.assertEqual(rc, 0, err)
        result = yaml.safe_load(
            (self.tmp / "results" / TASK_ID / "RUN-01" / "result.yaml")
            .read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["tests"], {"passed": 3, "failed": 1, "blocked": 0})
        self.assertEqual(result["findings"], [finding])
        self.assertTrue(result["summary"].startswith("[SCOPE_VIOLATION] "))
        self.assertIn("Abbruch", result["summary"])

    def test_foreign_base_head_rejected(self):
        self.created_task(base_head="f" * 40)
        before = _snapshot(self.tmp)
        rc, _, err = self.cli("draft", "import", TASK_ID)
        self.assertEqual(rc, 1)
        self.assertIn("HEAD_MISMATCH", err)
        self.assertEqual(_snapshot(self.tmp), before)

    def test_short_base_head_prefix_accepted(self):
        self.created_task(base_head=self.base_head[:7])
        rc, _, err = self.cli("draft", "import", TASK_ID)
        self.assertEqual(rc, 0, err)

    def test_scope_violation_with_completed_rejected(self):
        self.created_task(task_over={"allowed_paths": ["src/"]},
                          changed_files=["docs/out.md"])
        before = _snapshot(self.tmp)
        rc, _, err = self.cli("draft", "import", TASK_ID)
        self.assertEqual(rc, 1)
        self.assertIn("SCOPE_VIOLATION", err)
        self.assertEqual(_snapshot(self.tmp), before)

    def test_regular_draft_importable_with_scope(self):
        self.created_task(task_over={"allowed_paths": ["src/"]})
        rc, _, err = self.cli("draft", "import", TASK_ID)
        self.assertEqual(rc, 0, err)

    def test_second_import_is_noop(self):
        self.created_task()
        self.assertEqual(self.cli("draft", "import", TASK_ID)[0], 0)
        before = _snapshot(self.tmp)
        rc, out, err = self.cli("draft", "import", TASK_ID)
        self.assertEqual(rc, 0, err)
        self.assertIn("bereits importiert", out)
        self.assertEqual(_snapshot(self.tmp), before)

    def test_writer_guard_outside_board(self):
        self.created_task()
        with mock.patch.dict(os.environ, {"ACB_ALLOW_ANY_CLONE": ""}):
            before = _snapshot(self.tmp)
            rc, _, err = self.cli("draft", "import", TASK_ID)
        self.assertEqual(rc, 1)
        self.assertIn("SCOPE_VIOLATION", err)
        self.assertEqual(_snapshot(self.tmp), before)

    def test_writer_guard_allows_board_dir(self):
        board = self.tmp / "board"
        board.mkdir()
        store = Store(root=board, schema_dir=SCHEMA_DIR)
        with mock.patch.dict(os.environ, {"ACB_ALLOW_ANY_CLONE": ""}):
            self.assertTrue(draft.writer_guard_ok(store))

    def test_invalid_draft_rejected(self):
        self.created_task()
        path = self.tmp / "drafts" / TASK_ID / "RUN-01" / "draft.yaml"
        path.write_text("kind: bridge_draft\n", encoding="utf-8")
        rc, _, err = self.cli("draft", "import", TASK_ID)
        self.assertEqual(rc, 1)
        self.assertFalse((self.tmp / "results" / TASK_ID).exists())

    def test_wrong_state_rejected(self):
        self.created_task()
        self.store.set_status(TASK_ID, "READY", "a")
        self.store.set_status(TASK_ID, "ARCHIVED", "a")
        rc, _, err = self.cli("draft", "import", TASK_ID)
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
