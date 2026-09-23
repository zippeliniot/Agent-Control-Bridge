"""Test fuer scripts/steuerchat-vorlage.py (BRIDGE-0072). stdlib unittest.

Nutzt eine Kopie des echten docs/ACB-STEUERCHAT-START-GENERISCH-v2.md und
synthetische Fake-project.yaml in einem temp-Repo-Root, unabhaengig vom
echten projects/-Stand.
"""

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_SPEC = importlib.util.spec_from_file_location(
    "steuerchat_vorlage", REPO_ROOT / "scripts" / "steuerchat-vorlage.py")
steuerchat_vorlage = importlib.util.module_from_spec(_SPEC)
sys.modules["steuerchat_vorlage"] = steuerchat_vorlage
_SPEC.loader.exec_module(steuerchat_vorlage)


def _write_profile(root: Path, project_id: str, *, task_prefix="TEST",
                    github_repo="testorg/testrepo", repository="testrepo",
                    executor=None, profile_project_id=None) -> None:
    project_dir = root / "projects" / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "schema_version: \"1.0\"",
        "kind: bridge_project_profile",
        f"project_id: {profile_project_id if profile_project_id is not None else project_id}",
        "description: Testprojekt fuer die Steuerchat-Vorlage",
    ]
    if task_prefix is not None:
        lines.append(f"task_prefix: {task_prefix}")
    if github_repo is not None:
        lines.append(f"github_repo: {github_repo}")
    if repository is not None:
        lines.append(f"repository: {repository}")
    if executor is not None:
        lines.append(f"executor: {executor}")
    (project_dir / "project.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


class SteuerchatVorlageTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="steuerchat-vorlage-test-")
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)
        self.root = Path(self._tmp)
        (self.root / "docs").mkdir(parents=True, exist_ok=True)
        self.echt_template = (
            REPO_ROOT / "docs" / "ACB-STEUERCHAT-START-GENERISCH-v2.md"
        ).read_text(encoding="utf-8")
        (self.root / "docs" / "ACB-STEUERCHAT-START-GENERISCH-v2.md").write_text(
            self.echt_template, encoding="utf-8"
        )

    # (a) fuellt die ID ein, kein {{ im Ergebnis
    def test_a_fuellt_projekt_id_ein_kein_platzhalter(self):
        _write_profile(self.root, "proj-a")
        result = steuerchat_vorlage.build("proj-a", repo_root=self.root)
        self.assertIn("proj-a", result)
        self.assertNotIn("{{", result)

    # (b) Ergebnis enthaelt nicht den Kopfbereich vor der ---Linie
    def test_b_kopfbereich_fehlt_im_ergebnis(self):
        _write_profile(self.root, "proj-b")
        result = steuerchat_vorlage.build("proj-b", repo_root=self.root)
        self.assertNotIn("Einziges Feld:", result)
        self.assertNotIn("Text ab der Linie.", result)

    # (c) funktioniert mit \r\n-Zeilenenden der Vorlage
    def test_c_funktioniert_mit_crlf_vorlage(self):
        _write_profile(self.root, "proj-c")
        crlf = self.echt_template.replace("\n", "\r\n")
        (self.root / "docs" / "ACB-STEUERCHAT-START-GENERISCH-v2.md").write_text(
            crlf, encoding="utf-8"
        )
        result = steuerchat_vorlage.build("proj-c", repo_root=self.root)
        self.assertIn("proj-c", result)
        self.assertNotIn("{{", result)

    # (d) unbekannte project-id -> Fehler, der eine vorhandene ID nennt
    def test_d_unbekannte_project_id_nennt_vorhandene_id(self):
        _write_profile(self.root, "proj-vorhanden")
        with self.assertRaises(ValueError) as ctx:
            steuerchat_vorlage.build("does-not-exist", repo_root=self.root)
        self.assertIn("proj-vorhanden", str(ctx.exception))

    # (e) fehlendes Pflichtfeld -> Fehler
    def test_e_fehlendes_pflichtfeld_gibt_fehler(self):
        _write_profile(self.root, "proj-e", github_repo=None)
        with self.assertRaises(ValueError):
            steuerchat_vorlage.build("proj-e", repo_root=self.root)

    # (f) project_id im Profil weicht vom Argument ab -> Fehler
    def test_f_abweichende_project_id_gibt_fehler(self):
        _write_profile(self.root, "proj-f", profile_project_id="proj-f-anders")
        with self.assertRaises(ValueError):
            steuerchat_vorlage.build("proj-f", repo_root=self.root)

    # (g) Profil ohne executor ist zulaessig
    def test_g_profil_ohne_executor_ist_zulaessig(self):
        _write_profile(self.root, "proj-g", executor=None)
        result = steuerchat_vorlage.build("proj-g", repo_root=self.root)
        self.assertIn("proj-g", result)
        self.assertNotIn("{{", result)


if __name__ == "__main__":
    unittest.main()
