"""Hermetische Tests für den Result-Importer (BRIDGE-007). stdlib unittest.

Der Git-Zugriff wird über git_info_fn bzw. Monkeypatch von
importer.collect_git_info gestubbt - kein echtes Git nötig.
"""

import io
import os
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import yaml  # noqa: E402

from bridge import importer  # noqa: E402
from bridge.cli import main  # noqa: E402
from bridge.store import Store, StoreError, SchemaValidationError  # noqa: E402

SCHEMA_DIR = REPO_ROOT / "schemas"
TS = "2026-01-01T00:00:00Z"
RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


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


def git_stub(root=None, base_head=None):
    return {
        "repository": "Codex-Control-Bridge",
        "branch": "feature/importer",
        "head": "a" * 40,
        "base_head": base_head,
        "commits": [
            {"sha": "b" * 40, "message": "erster commit"},
            {"sha": "c" * 40, "message": "zweiter commit"},
        ],
        "changed_files": ["src/bridge/importer.py", "tests/test_importer.py"],
    }


class ImporterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ccb-importer-"))
        for name in ("tasks", "results", "audit"):
            (self.tmp / name).mkdir()
        self.store = Store(root=self.tmp, schema_dir=SCHEMA_DIR)
        self.store.create_task(valid_task())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def audit_types(self):
        f = self.tmp / "audit" / "audit.jsonl"
        return [yaml.safe_load(x)["event_type"]
                for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]

    def result_on_disk(self, run_id="RUN-01"):
        path = self.tmp / "results" / "BRIDGE-0900" / run_id / "result.yaml"
        return path, yaml.safe_load(path.read_text(encoding="utf-8"))

    # -- Grundfall -----------------------------------------------------

    def test_completed_draft_writes_valid_result_and_audit(self):
        res = importer.import_result(
            self.store, "BRIDGE-0900", "COMPLETED",
            draft={"summary": "fertig", "started_at": TS},
            git_info_fn=git_stub,
        )
        path, doc = self.result_on_disk()
        self.assertTrue(path.exists())
        self.assertEqual(doc, res)
        self.store.validate(doc)  # schema-valide
        self.assertIn("RESULT_WRITTEN", self.audit_types())
        self.assertEqual(doc["summary"], "fertig")

    def test_project_id_taken_from_task(self):
        doc = importer.build_result(self.store, "BRIDGE-0900", "COMPLETED",
                                    git_info_fn=git_stub)
        self.assertEqual(doc["project_id"], "codex-control-bridge")

    def test_run_id_default_and_explicit(self):
        importer.import_result(self.store, "BRIDGE-0900", "COMPLETED",
                               git_info_fn=git_stub)
        _, doc = self.result_on_disk("RUN-01")
        self.assertEqual(doc["run_id"], "RUN-01")
        importer.import_result(self.store, "BRIDGE-0900", "COMPLETED",
                               run_id="RUN-07", git_info_fn=git_stub)
        _, doc = self.result_on_disk("RUN-07")
        self.assertEqual(doc["run_id"], "RUN-07")

    def test_timestamps(self):
        doc = importer.build_result(
            self.store, "BRIDGE-0900", "COMPLETED",
            draft={"started_at": "2025-12-31T09:00:00Z"}, git_info_fn=git_stub,
        )
        self.assertRegex(doc["ended_at"], RFC3339)
        self.assertEqual(doc["started_at"], "2025-12-31T09:00:00Z")

    def test_started_at_defaults_to_ended_at(self):
        doc = importer.build_result(self.store, "BRIDGE-0900", "COMPLETED",
                                    git_info_fn=git_stub)
        self.assertEqual(doc["started_at"], doc["ended_at"])

    def test_git_fields_from_stub(self):
        doc = importer.build_result(self.store, "BRIDGE-0900", "COMPLETED",
                                    git_info_fn=git_stub)
        self.assertEqual(doc["repository"], "Codex-Control-Bridge")
        self.assertEqual(doc["branch"], "feature/importer")
        self.assertEqual(doc["head"], "a" * 40)
        self.assertEqual([c["sha"] for c in doc["commits"]], ["b" * 40, "c" * 40])
        self.assertEqual(doc["changed_files"],
                         ["src/bridge/importer.py", "tests/test_importer.py"])

    def test_flag_beats_draft(self):
        doc = importer.build_result(
            self.store, "BRIDGE-0900", "COMPLETED",
            draft={"summary": "aus entwurf"}, summary="aus flag",
            git_info_fn=git_stub,
        )
        self.assertEqual(doc["summary"], "aus flag")

    # -- Maschinenaufloesung (BRIDGE-031) -----------------------------

    def test_machine_resolved_from_computername_when_not_given(self):
        """Ohne expliziten machine-Parameter: COMPUTERNAME statt 'unknown'
        (ersetzt die frueher genutzte, nie gesetzte BRIDGE_MACHINE-Env-Var)."""
        with mock.patch.dict(os.environ,
                             {"COMPUTERNAME": "TESTHOST-IMPORT"}, clear=False):
            os.environ.pop("BRIDGE_MACHINE", None)
            doc = importer.build_result(self.store, "BRIDGE-0900", "COMPLETED",
                                        git_info_fn=git_stub)
        self.assertEqual(doc["physical_machine"], "TESTHOST-IMPORT")
        self.assertEqual(doc["created_by"], "claude-code@TESTHOST-IMPORT")

    def test_machine_explicit_wins_over_computername(self):
        """Expliziter machine-Parameter hat weiterhin Vorrang vor COMPUTERNAME."""
        with mock.patch.dict(os.environ,
                             {"COMPUTERNAME": "TESTHOST-IMPORT"}, clear=False):
            doc = importer.build_result(self.store, "BRIDGE-0900", "COMPLETED",
                                        machine="EXPLICIT-MACHINE",
                                        git_info_fn=git_stub)
        self.assertEqual(doc["physical_machine"], "EXPLICIT-MACHINE")
        self.assertEqual(doc["created_by"], "claude-code@EXPLICIT-MACHINE")

    # -- INTERRUPTED / fail-closed -----------------------------------

    def test_interrupted_without_reason_fails_closed(self):
        with self.assertRaises(SchemaValidationError):
            importer.import_result(self.store, "BRIDGE-0900", "INTERRUPTED",
                                   git_info_fn=git_stub)
        self.assertFalse((self.tmp / "results" / "BRIDGE-0900" / "RUN-01").exists())

    def test_interrupted_with_reason_and_resumable_ok(self):
        doc = importer.import_result(
            self.store, "BRIDGE-0900", "INTERRUPTED",
            draft={"interruption_reason": "USAGE_LIMIT", "resumable": True,
                   "resume_hint": "ab Kriterium 3"},
            git_info_fn=git_stub,
        )
        self.assertEqual(doc["interruption_reason"], "USAGE_LIMIT")
        self.assertTrue(doc["resumable"])

    def test_unknown_task_fails_closed(self):
        with self.assertRaises(StoreError):
            importer.import_result(self.store, "BRIDGE-0404", "COMPLETED",
                                   git_info_fn=git_stub)

    def test_git_error_fails_closed(self):
        def boom(root=None, base_head=None):
            raise importer.ImporterError("git kaputt")
        with self.assertRaises(importer.ImporterError):
            importer.import_result(self.store, "BRIDGE-0900", "COMPLETED",
                                   git_info_fn=boom)

    # -- CLI --------------------------------------------------------

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["--root", str(self.tmp),
                         "--schema-dir", str(SCHEMA_DIR), *args])
        return code, out.getvalue(), err.getvalue()

    def test_cli_import_completed(self):
        with mock.patch.object(importer, "collect_git_info", git_stub):
            code, out, err = self.cli("result", "import", "BRIDGE-0900",
                                      "--status", "COMPLETED",
                                      "--base-head", "a" * 40)
        self.assertEqual(code, 0, err)
        self.assertIn("RUN-01", out)
        self.assertTrue((self.tmp / "results" / "BRIDGE-0900" / "RUN-01"
                         / "result.yaml").exists())

    def test_cli_import_without_status_is_usage_error(self):
        with mock.patch.object(importer, "collect_git_info", git_stub):
            code, _, err = self.cli("result", "import", "BRIDGE-0900")
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", err)

    # -- Maschinenaufloesung (BRIDGE-031) -----------------------------

    def test_cli_import_resolves_computername_without_machine_flag(self):
        with mock.patch.dict(os.environ, {"COMPUTERNAME": "TESTHOST-IMPORT"},
                             clear=False), \
             mock.patch.object(importer, "collect_git_info", git_stub):
            code, out, err = self.cli("result", "import", "BRIDGE-0900",
                                      "--status", "COMPLETED",
                                      "--base-head", "a" * 40)
        self.assertEqual(code, 0, err)
        doc = yaml.safe_load((self.tmp / "results" / "BRIDGE-0900" / "RUN-01"
                              / "result.yaml").read_text(encoding="utf-8"))
        self.assertEqual(doc["physical_machine"], "TESTHOST-IMPORT")

    def test_cli_import_explicit_machine_wins(self):
        with mock.patch.dict(os.environ, {"COMPUTERNAME": "TESTHOST-IMPORT"},
                             clear=False), \
             mock.patch.object(importer, "collect_git_info", git_stub):
            code, out, err = self.cli("result", "import", "BRIDGE-0900",
                                      "--status", "COMPLETED",
                                      "--base-head", "a" * 40,
                                      "--machine", "EXPLICIT-M")
        self.assertEqual(code, 0, err)
        doc = yaml.safe_load((self.tmp / "results" / "BRIDGE-0900" / "RUN-01"
                              / "result.yaml").read_text(encoding="utf-8"))
        self.assertEqual(doc["physical_machine"], "EXPLICIT-M")


# --------------------------------------------------------------------------- #
# collect_git_info / _is_ancestor gegen echtes Git (BRIDGE-0095, ISSUE-0003
# zweiter Teilbefund: Live-HEAD-Durchsetzung statt reinem Fallback-Wert)
# --------------------------------------------------------------------------- #

class CollectGitInfoLiveHeadTests(unittest.TestCase):
    """Reales Git-Repo (kein Stub) - prueft die neue Vorfahr-Pruefung in
    collect_git_info() direkt, unabhaengig vom CLI/Runner-Umweg."""

    def setUp(self):
        import subprocess
        self.tmp = Path(tempfile.mkdtemp(prefix="ccb-gitinfo-"))
        self._sp = lambda *args: subprocess.run(
            ["git", *args], cwd=self.tmp, capture_output=True, text=True, timeout=30)
        self._sp("init", "-b", "main")
        self._sp("config", "user.email", "test@example.com")
        self._sp("config", "user.name", "Test")
        (self.tmp / "a.txt").write_text("1\n", encoding="utf-8")
        self._sp("add", "a.txt")
        self._sp("commit", "-m", "erster Commit")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _head(self):
        return self._sp("rev-parse", "HEAD").stdout.strip()

    def test_ancestor_base_head_succeeds(self):
        base = self._head()
        (self.tmp / "b.txt").write_text("2\n", encoding="utf-8")
        self._sp("add", "b.txt")
        self._sp("commit", "-m", "zweiter Commit")
        info = importer.collect_git_info(self.tmp, base_head=base)
        self.assertIn("b.txt", info["changed_files"])

    def test_mixed_projects_diff_is_filtered_to_own_prefix(self):
        # BRIDGE-0101 (ISSUE-0005): zwei Projekte im selben base_head..HEAD-Bereich.
        base = self._head()
        files = [
            "tasks/BRIDGE-0100/task.yaml", "results/BRIDGE-0100/RUN-01/result.yaml",
            "work-packages/BRIDGE-100.md", "open-issues/acb/ISSUE-1.yaml",
            "tasks/WETTER-0015/task.yaml", "results/WETTER-0015/RUN-01/result.yaml",
            "work-packages/WETTER-015.md", "open-issues/wetter/ISSUE-2.yaml",
            "src/code.py", "audit/audit.jsonl",
        ]
        for rel in files:
            p = self.tmp / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x\n", encoding="utf-8")
        self._sp("add", "-A")
        self._sp("commit", "-m", "gemischt")
        info = importer.collect_git_info(self.tmp, base_head=base,
                                         task_prefix="BRIDGE", project_id="acb")
        got = set(info["changed_files"])
        self.assertEqual(got, {
            "tasks/BRIDGE-0100/task.yaml", "results/BRIDGE-0100/RUN-01/result.yaml",
            "work-packages/BRIDGE-100.md", "open-issues/acb/ISSUE-1.yaml",
            "src/code.py", "audit/audit.jsonl"})
        # ohne Prefix: unveraendert (Rueckwaertskompatibilitaet)
        raw = importer.collect_git_info(self.tmp, base_head=base)
        self.assertEqual(len(raw["changed_files"]), len(files))

    def test_filter_keeps_incoming_of_own_prefix(self):
        out = importer.filter_project_files(
            ["tasks/incoming/BRIDGE-0101.yaml", "tasks/incoming/WETTER-0015.yaml"],
            "BRIDGE", "acb")
        self.assertEqual(out, ["tasks/incoming/BRIDGE-0101.yaml"])

    def test_non_ancestor_base_head_fails_closed(self):
        # Ein Commit auf einem Nebenzweig ist kein Vorfahr von main -
        # muss die neue Pruefung mit ImporterError ablehnen, nicht
        # stillschweigend einen falschen Diff liefern (BRIDGE-0089-Befund:
        # base_head 815ec26 statt echtem Parent c01c5b4).
        self._sp("checkout", "-b", "side")
        (self.tmp / "side.txt").write_text("seite\n", encoding="utf-8")
        self._sp("add", "side.txt")
        self._sp("commit", "-m", "Seitenzweig-Commit")
        side_head = self._head()
        self._sp("checkout", "main")
        with self.assertRaises(importer.ImporterError) as ctx:
            importer.collect_git_info(self.tmp, base_head=side_head)
        self.assertIn("kein Vorfahr", str(ctx.exception))

    def test_unknown_sha_fails_closed(self):
        with self.assertRaises(importer.ImporterError):
            importer.collect_git_info(self.tmp, base_head="f" * 40)

    def test_is_ancestor_helper_direct(self):
        base = self._head()
        (self.tmp / "c.txt").write_text("3\n", encoding="utf-8")
        self._sp("add", "c.txt")
        self._sp("commit", "-m", "dritter Commit")
        head = self._head()
        self.assertTrue(importer._is_ancestor(self.tmp, base, head))
        self.assertFalse(importer._is_ancestor(self.tmp, head, base))
        self.assertFalse(importer._is_ancestor(self.tmp, "f" * 40, head))


if __name__ == "__main__":
    unittest.main()
