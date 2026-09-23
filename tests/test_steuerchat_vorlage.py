"""Test fuer scripts/steuerchat-vorlage.py (BRIDGE-0071). stdlib unittest.

Nutzt ein synthetisches Fake-project.yaml in einem temp-Repo-Root (Kopie der
echten Vorlage docs/ACB-STEUERCHAT-VORLAGE.md), unabhaengig vom echten
projects/-Stand.
"""

import importlib.util
import shutil
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_SPEC = importlib.util.spec_from_file_location(
    "steuerchat_vorlage", REPO_ROOT / "scripts" / "steuerchat-vorlage.py")
steuerchat_vorlage = importlib.util.module_from_spec(_SPEC)
sys.modules["steuerchat_vorlage"] = steuerchat_vorlage
_SPEC.loader.exec_module(steuerchat_vorlage)


def _write_profile(root: Path, project_id: str, executor: str, extra: str = "") -> None:
    project_dir = root / "projects" / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "project.yaml").write_text(
        "schema_version: \"1.0\"\n"
        "kind: bridge_project_profile\n"
        f"project_id: {project_id}\n"
        "description: Testprojekt fuer die Steuerchat-Vorlage\n"
        f"task_prefix: TEST\n"
        f"executor: {executor}\n"
        "github_repo: testorg/testrepo\n"
        f"{extra}",
        encoding="utf-8",
    )


class SteuerchatVorlageTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmp = tempfile.mkdtemp(prefix="steuerchat-vorlage-test-")
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)
        self.root = Path(self._tmp)
        (self.root / "docs").mkdir(parents=True, exist_ok=True)
        template = (REPO_ROOT / "docs" / "ACB-STEUERCHAT-VORLAGE.md").read_text(encoding="utf-8")
        (self.root / "docs" / "ACB-STEUERCHAT-VORLAGE.md").write_text(template, encoding="utf-8")

    def test_claude_code_fuellt_mit_skill_hinweis(self):
        _write_profile(self.root, "proj-cc", "claude-code")
        result = steuerchat_vorlage.build("proj-cc", repo_root=self.root)
        self.assertIn("Testprojekt fuer die Steuerchat-Vorlage", result)
        self.assertIn("testorg", result)
        self.assertIn("testrepo", result)
        self.assertIn("TEST", result)
        self.assertIn("acb-auftrag", result)
        self.assertIn("WETTER-0001-Vorfall", result)
        self.assertNotIn("{{", result)

    def test_codex_fuellt_mit_platzhaltertext(self):
        _write_profile(self.root, "proj-codex", "codex")
        result = steuerchat_vorlage.build("proj-codex", repo_root=self.root)
        self.assertIn("Codex, läuft nativ in PowerShell", result)
        self.assertIn("noch keine dokumentierte Erfahrung", result)
        self.assertNotIn("{{", result)

    def test_fehlendes_pflichtfeld_gibt_fehler(self):
        project_dir = self.root / "projects" / "proj-unvollstaendig"
        project_dir.mkdir(parents=True)
        (project_dir / "project.yaml").write_text(
            "schema_version: \"1.0\"\n"
            "kind: bridge_project_profile\n"
            "project_id: proj-unvollstaendig\n"
            "executor: claude-code\n",
            encoding="utf-8",
        )
        with self.assertRaises(ValueError):
            steuerchat_vorlage.build("proj-unvollstaendig", repo_root=self.root)

    def test_unbekannter_executor_gibt_fehler(self):
        _write_profile(self.root, "proj-unbekannt", "irgendwas-anderes")
        with self.assertRaises(ValueError):
            steuerchat_vorlage.build("proj-unbekannt", repo_root=self.root)

    def test_unbekannte_project_id_gibt_fehler(self):
        with self.assertRaises(ValueError):
            steuerchat_vorlage.build("does-not-exist", repo_root=self.root)


if __name__ == "__main__":
    unittest.main()
