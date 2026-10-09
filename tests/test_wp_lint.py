"""Tests fuer scripts/wp-lint.py (BRIDGE-0102). stdlib unittest, tempdir."""

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

    def run_main(self, wp, staging):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = wp_lint.main(["--wp", str(wp), "--staging", str(staging)])
        return code, out.getvalue(), err.getvalue()

    def test_wp_without_model_row_rejected(self):
        wp = self.wp_from("BRIDGE-095.md")
        code, _, err = self.run_main(wp, self.staging(bridge_task_id="BRIDGE-0095"))
        self.assertEqual(code, 1)
        self.assertIn("Modell / Denkstufe", err)

    def test_complete_pair_accepted(self):
        wp = self.wp_from("BRIDGE-090.md")
        code, out, err = self.run_main(wp, self.staging())
        self.assertEqual(code, 0, err)
        self.assertIn("OK", out)

    def test_level_mismatch_rejected(self):
        wp = self.wp_from("BRIDGE-090.md")  # WP: MEDIUM
        code, _, err = self.run_main(wp, self.staging(reasoning_level="LOW"))
        self.assertEqual(code, 1)
        self.assertIn("Denkstufe weicht ab", err)

    def test_model_mismatch_rejected(self):
        wp = self.wp_from("BRIDGE-090.md")
        code, _, err = self.run_main(wp, self.staging(model="Claude Opus 5"))
        self.assertEqual(code, 1)
        self.assertIn("Modell weicht ab", err)

    def test_task_id_inconsistency_rejected(self):
        wp = self.wp_from("BRIDGE-090.md")
        code, _, err = self.run_main(wp, self.staging(bridge_task_id="BRIDGE-0999"))
        self.assertEqual(code, 1)
        self.assertIn("WP-Ueberschrift", err)

    def test_schema_violation_detected_via_store_validation(self):
        wp = self.wp_from("BRIDGE-090.md")
        doc = staging_doc()
        del doc["title"]
        path = self.tmp / "bad.yaml"
        path.write_text(yaml.safe_dump(doc), encoding="utf-8")
        code, _, err = self.run_main(wp, path)
        self.assertEqual(code, 1)
        self.assertIn("Schema-Verstoss", err)

    def test_missing_model_fields_in_yaml_rejected(self):
        wp = self.wp_from("BRIDGE-090.md")
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


if __name__ == "__main__":
    unittest.main()
