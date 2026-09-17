"""Hermetischer Test des Read-only-Integrationstests (BRIDGE-012). stdlib unittest.

Führt denselben Ablauf wie scripts/integration_readonly.py gegen ein
synthetisches Wegwerf-Git-Repo aus - unabhängig vom echten CCB-Git-Stand.
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import yaml  # noqa: E402

import integration_readonly as intgr  # noqa: E402
from bridge import adapter  # noqa: E402

SCHEMA_DIR = REPO_ROOT / "schemas"


def _run_git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args],
                   check=True, capture_output=True, text=True)


def _git_out(repo, *args) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args],
                          check=True, capture_output=True, text=True)
    return proc.stdout.strip()


def _commit(repo, msg):
    _run_git(repo, "-c", "user.email=test@example.com", "-c", "user.name=Test",
             "commit", "-m", msg)


def make_target_repo(base) -> Path:
    repo = base / "target"
    repo.mkdir()
    _run_git(repo, "init", "-q")
    (repo / "a.txt").write_text("A\n", encoding="utf-8")
    _run_git(repo, "add", "a.txt")
    _commit(repo, "erster commit")
    (repo / "b.txt").write_text("B\n", encoding="utf-8")
    _run_git(repo, "add", "b.txt")
    _commit(repo, "zweiter commit")
    return repo


class IntegrationReadonlyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ccb-int-"))
        self.repo = make_target_repo(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_observation_leaves_target_unchanged(self):
        head_before = _git_out(self.repo, "rev-parse", "HEAD")
        out = self.tmp / "store-out"
        report = intgr.run(self.repo, out, SCHEMA_DIR)

        self.assertTrue(report["passed"], report["checks"])
        self.assertEqual(_git_out(self.repo, "rev-parse", "HEAD"), head_before)
        self.assertEqual(_git_out(self.repo, "status", "--porcelain"), "")

        rp = report["result_path"]
        self.assertTrue(rp.is_file())
        self.assertIn(out.resolve(), rp.resolve().parents)
        doc = yaml.safe_load(rp.read_text(encoding="utf-8"))
        self.assertEqual(doc["head"], head_before)
        self.assertEqual(doc["repository"], self.repo.name)

        # kein Schreibzugriff aufs Zielrepo
        self.assertFalse((self.repo / "tasks").exists())
        self.assertFalse((self.repo / "results").exists())
        self.assertFalse((self.repo / "audit").exists())

    def test_out_inside_target_is_rejected(self):
        with self.assertRaises(RuntimeError):
            intgr.run(self.repo, self.repo / "sub-out", SCHEMA_DIR)

    def test_write_attempt_via_adapter_is_rejected(self):
        ro = adapter.ReadOnlyProjectAdapter({"read_only": True}, self.repo,
                                            schema_dir=SCHEMA_DIR)
        head_before = _git_out(self.repo, "rev-parse", "HEAD")
        with self.assertRaises(adapter.ReadOnlyViolation):
            adapter.run_readonly_git(self.repo,
                                     ["commit", "--allow-empty", "-m", "x"],
                                     allowlist=ro.allowlist)
        self.assertEqual(_git_out(self.repo, "rev-parse", "HEAD"), head_before)

    def test_main_pass_exit_zero(self):
        code = intgr.main(["--target", str(self.repo),
                           "--out", str(self.tmp / "o2"),
                           "--schema-dir", str(SCHEMA_DIR)])
        self.assertEqual(code, 0)

    def test_custom_project_id_and_task_prefix_land_in_result(self):
        out = self.tmp / "store-out"
        report = intgr.run(self.repo, out, SCHEMA_DIR,
                            project_id="dorfschaft", task_prefix="DORF")
        self.assertTrue(report["passed"], report["checks"])
        doc = yaml.safe_load(report["result_path"].read_text(encoding="utf-8"))
        task_doc = yaml.safe_load(
            (out / "tasks" / intgr.DEFAULT_TASK_ID / "task.yaml").read_text(encoding="utf-8"))
        self.assertEqual(task_doc["project_id"], "dorfschaft")
        self.assertNotEqual(doc["repository"], "codex-control-bridge")

    def test_expected_head_correct_passes_with_check(self):
        head = _git_out(self.repo, "rev-parse", "HEAD")
        out = self.tmp / "store-out"
        report = intgr.run(self.repo, out, SCHEMA_DIR, expected_head=head)
        self.assertTrue(report["passed"], report["checks"])
        self.assertTrue(report["checks"]["head_matches_expected"])

    def test_expected_head_wrong_fails_with_both_heads_in_message(self):
        wrong_head = "0" * 40
        out = self.tmp / "store-out"
        with self.assertRaises(RuntimeError) as ctx:
            intgr.run(self.repo, out, SCHEMA_DIR, expected_head=wrong_head)
        message = str(ctx.exception)
        self.assertIn(wrong_head, message)
        self.assertIn(_git_out(self.repo, "rev-parse", "HEAD"), message)

    def test_expected_head_short_sha_is_accepted_via_prefix(self):
        head = _git_out(self.repo, "rev-parse", "HEAD")
        out = self.tmp / "store-out"
        report = intgr.run(self.repo, out, SCHEMA_DIR, expected_head=head[:7])
        self.assertTrue(report["passed"], report["checks"])
        self.assertTrue(report["checks"]["head_matches_expected"])

    def test_head_matches_expected_absent_when_expected_head_not_set(self):
        out = self.tmp / "store-out"
        report = intgr.run(self.repo, out, SCHEMA_DIR)
        self.assertNotIn("head_matches_expected", report["checks"])

    def test_main_with_wrong_expected_head_exits_one(self):
        code = intgr.main(["--target", str(self.repo),
                           "--out", str(self.tmp / "o3"),
                           "--schema-dir", str(SCHEMA_DIR),
                           "--expected-head", "0" * 40])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
