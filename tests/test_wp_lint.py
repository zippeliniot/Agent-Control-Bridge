"""Tests fuer scripts/wp-lint.py (BRIDGE-0102, BRIDGE-0104). stdlib unittest, tempdir."""

import importlib.util
import io
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

_SPEC = importlib.util.spec_from_file_location(
    "wp_lint", REPO_ROOT / "scripts" / "wp-lint.py")
wp_lint = importlib.util.module_from_spec(_SPEC)
sys.modules["wp_lint"] = wp_lint
_SPEC.loader.exec_module(wp_lint)


def staging_doc(**over):
    doc = {
        "schema_version": "1.0",
        "kind": "bridge_task",
        "bridge_task_id": "BRIDGE-0090",
        "project_id": "agent-control-bridge",
        "title": "Test",
        "description": "Nur fuer Tests.",
        "task_class": "ARCHITECTURE",
        "repository": "Agent-Control-Bridge/dev",
        "branch": "main",
        "permissions": ["WORKTREE_WRITE"],
        "status": "CREATED",
        "created_at": "2026-01-01T00:00:00Z",
        "created_by": "test",
        "model": "Claude Sonnet 5",
        "reasoning_level": "MEDIUM",
    }
    doc.update(over)
    return doc


class WpLintTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ccb-wplint-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def staging(self, **over):
        path = self.tmp / "s.yaml"
        path.write_text(yaml.safe_dump(staging_doc(**over)), encoding="utf-8")
        return path

    def wp_from(self, name):
        dst = self.tmp / name
        shutil.copy(REPO_ROOT / "work-packages" / name, dst)
        return dst

    def good_wp(self, extra="", scope="`scripts/x.py`", criteria=True):
        """Minimales gueltiges WP (Claude Sonnet 5 / MEDIUM, ID BRIDGE-0090)."""
        text = ("# BRIDGE-0090: Test\n\n| Feld | Wert |\n|---|---|\n"
                "| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |\n")
        if scope is not None:
            text += f"| Scope | {scope} |\n"
        if criteria:
            text += "\n## Akzeptanzkriterien\n\n- [ ] x\n"
        text += extra
        path = self.tmp / "BRIDGE-0090.md"
        path.write_text(text, encoding="utf-8")
        return path

    def fake_root(self, issues=(), tasks=()):
        root = self.tmp / "root"
        root.mkdir(parents=True, exist_ok=True)
        for n in issues:
            f = (root / "open-issues" / "agent-control-bridge"
                 / f"agent-control-bridge-ISSUE-{n}.yaml")
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("x: 1\n", encoding="utf-8")
        for t in tasks:
            f = root / "tasks" / t / "task.yaml"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("x: 1\n", encoding="utf-8")
        return root

    def run_main(self, wp, staging, root=None):
        argv = ["--wp", str(wp), "--staging", str(staging)]
        if root is not None:
            argv += ["--root", str(root)]
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = wp_lint.main(argv)
        return code, out.getvalue(), err.getvalue()

    def run_root(self, wp, root):
        return self.run_main(wp, self.staging(), root)

    def test_wp_without_model_row_rejected(self):
        wp = self.wp_from("BRIDGE-095.md")
        code, _, err = self.run_main(wp, self.staging(bridge_task_id="BRIDGE-0095"))
        self.assertEqual(code, 1)
        self.assertIn("Modell / Denkstufe", err)

    def test_complete_pair_accepted(self):
        wp = self.good_wp()
        code, out, err = self.run_main(wp, self.staging())
        self.assertEqual(code, 0, err)
        self.assertIn("OK", out)

    def test_level_mismatch_rejected(self):
        wp = self.good_wp()  # WP: MEDIUM
        code, _, err = self.run_main(wp, self.staging(reasoning_level="LOW"))
        self.assertEqual(code, 1)
        self.assertIn("Denkstufe weicht ab", err)

    def test_model_mismatch_rejected(self):
        wp = self.good_wp()
        code, _, err = self.run_main(wp, self.staging(model="Claude Opus 5"))
        self.assertEqual(code, 1)
        self.assertIn("Modell weicht ab", err)

    def test_task_id_inconsistency_rejected(self):
        wp = self.good_wp()
        code, _, err = self.run_main(wp, self.staging(bridge_task_id="BRIDGE-0999"))
        self.assertEqual(code, 1)
        self.assertIn("WP-Ueberschrift", err)

    def test_schema_violation_detected_via_store_validation(self):
        wp = self.good_wp()
        doc = staging_doc()
        del doc["title"]
        path = self.tmp / "bad.yaml"
        path.write_text(yaml.safe_dump(doc), encoding="utf-8")
        code, _, err = self.run_main(wp, path)
        self.assertEqual(code, 1)
        self.assertIn("Schema-Verstoss", err)

    def test_missing_model_fields_in_yaml_rejected(self):
        wp = self.good_wp()
        doc = staging_doc()
        del doc["model"]
        doc["reasoning_level"] = ""
        path = self.tmp / "nomodel.yaml"
        path.write_text(yaml.safe_dump(doc), encoding="utf-8")
        code, _, err = self.run_main(wp, path)
        self.assertEqual(code, 1)
        self.assertIn("'model' fehlt", err)
        self.assertIn("'reasoning_level' fehlt", err)

    def test_invalid_level_in_wp_rejected(self):
        wp = self.tmp / "BRIDGE-0090.md"
        wp.write_text("# BRIDGE-0090 - x\n\n| Feld | Wert |\n|---|---|\n"
                      "| **Modell / Denkstufe** | **Claude Sonnet 5 / EXTREM** |\n",
                      encoding="utf-8")
        code, _, err = self.run_main(wp, self.staging())
        self.assertEqual(code, 1)
        self.assertIn("ungueltige Denkstufe", err)

    # --- BRIDGE-0104 Pruefung 5: ISSUE-Referenzen ---
    def test_nonexistent_issue_ref_rejected(self):
        wp = self.good_wp("\nSiehe ISSUE-9999.\n")
        code, _, err = self.run_root(wp, self.fake_root(issues=["0006"]))
        self.assertEqual(code, 1)
        self.assertIn("ISSUE-9999 nicht aufloesbar", err)

    def test_existing_issue_ref_accepted(self):
        wp = self.good_wp("\nSiehe ISSUE-0006.\n")
        code, _, err = self.run_root(wp, self.fake_root(issues=["0006"]))
        self.assertEqual(code, 0, err)

    def test_existing_issue_ref_in_real_repo_accepted(self):
        wp = self.good_wp("\nSiehe ISSUE-0006.\n")
        code, _, err = self.run_main(wp, self.staging())
        self.assertEqual(code, 0, err)

    # --- BRIDGE-0104 Pruefung 6: abgeschlossen zitiert ohne task.yaml ---
    def test_completed_ref_without_task_yaml_warns_exit_zero(self):
        wp = self.good_wp("\nBRIDGE-0092 ist COMPLETED.\n")
        code, _, err = self.run_root(wp, self.fake_root())
        self.assertEqual(code, 0, err)
        self.assertIn("WARNUNG", err)
        self.assertIn("BRIDGE-0092", err)

    def test_short_id_normalized_for_task_yaml_lookup(self):
        wp = self.good_wp("\nBRIDGE-092 ARCHIVED.\n")
        code, _, err = self.run_root(wp, self.fake_root())
        self.assertEqual(code, 0, err)
        self.assertIn("tasks/BRIDGE-0092/task.yaml fehlt", err)

    def test_completed_ref_with_task_yaml_no_warning(self):
        wp = self.good_wp("\nBRIDGE-0092 ist COMPLETED.\n")
        code, _, err = self.run_root(wp, self.fake_root(tasks=["BRIDGE-0092"]))
        self.assertEqual(code, 0, err)
        self.assertNotIn("WARNUNG", err)

    def test_bridge_ref_without_closing_word_no_warning(self):
        wp = self.good_wp("\nSiehe BRIDGE-0092.\n")
        code, _, err = self.run_root(wp, self.fake_root())
        self.assertEqual(code, 0, err)
        self.assertNotIn("WARNUNG", err)

    # --- BRIDGE-0104 Pruefung 7: Akzeptanzkriterien + Scope ---
    def test_missing_acceptance_section_rejected(self):
        wp = self.good_wp(criteria=False)
        code, _, err = self.run_main(wp, self.staging())
        self.assertEqual(code, 1)
        self.assertIn("## Akzeptanzkriterien", err)

    def test_missing_scope_row_rejected(self):
        wp = self.good_wp(scope=None)
        code, _, err = self.run_main(wp, self.staging())
        self.assertEqual(code, 1)
        self.assertIn("'Scope' fehlt", err)

    def test_empty_scope_row_rejected(self):
        wp = self.good_wp(scope="  ")
        code, _, err = self.run_main(wp, self.staging())
        self.assertEqual(code, 1)
        self.assertIn("Scope-Zeile", err)


if __name__ == "__main__":
    unittest.main()
