"""Hermetische Tests für die Ablage-Schicht (BRIDGE-005). stdlib unittest."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import yaml  # noqa: E402
from jsonschema import Draft202012Validator  # noqa: E402

from bridge import state_machine  # noqa: E402
from bridge.store import (  # noqa: E402
    Store,
    StoreError,
    SchemaValidationError,
    _FORMAT_CHECKER,
)

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


def valid_result(**over):
    doc = {
        "schema_version": "1.0",
        "kind": "bridge_result",
        "bridge_task_id": "BRIDGE-0900",
        "project_id": "codex-control-bridge",
        "run_id": "RUN-01",
        "status": "COMPLETED",
        "repository": "Codex-Control-Bridge",
        "branch": "main",
        "head": "0" * 40,
        "executor": "claude-code",
        "started_at": TS,
        "ended_at": TS,
        "created_by": "claude-code",
    }
    doc.update(over)
    return doc


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ccb-store-"))
        for name in ("tasks", "results", "audit"):
            (self.tmp / name).mkdir()
        self.store = Store(root=self.tmp, schema_dir=SCHEMA_DIR)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def audit_events(self):
        f = self.tmp / "audit" / "audit.jsonl"
        if not f.exists():
            return []
        return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]

    def event_types(self):
        return [e["event_type"] for e in self.audit_events()]

    # -- create_task ---------------------------------------------------

    def test_valid_task_writes_file_and_audit(self):
        self.store.create_task(valid_task())
        path = self.tmp / "tasks" / "BRIDGE-0900" / "task.yaml"
        self.assertTrue(path.exists())
        self.assertEqual(yaml.safe_load(path.read_text(encoding="utf-8"))["status"], "CREATED")
        self.assertEqual(self.event_types(), ["TASK_CREATED"])

    def test_invalid_task_missing_field_rejected(self):
        bad = valid_task()
        del bad["title"]
        with self.assertRaises(SchemaValidationError):
            self.store.create_task(bad)
        self.assertFalse((self.tmp / "tasks" / "BRIDGE-0900").exists())
        self.assertEqual(self.audit_events(), [])

    def test_invalid_task_unknown_field_rejected(self):
        with self.assertRaises(SchemaValidationError):
            self.store.create_task(valid_task(unerwartetes_feld="x"))
        self.assertEqual(self.audit_events(), [])

    def test_task_executor_controller_review_roles_override_valid(self):
        # additiv (BRIDGE-019): neue optionale Task-Felder
        self.store.create_task(valid_task(
            executor="codex", controller="openai",
            review_roles={"lead": "openai", "support": "anthropic"}))
        self.assertEqual(self.event_types(), ["TASK_CREATED"])

    def test_task_without_new_override_fields_still_valid(self):
        self.store.create_task(valid_task())
        self.assertEqual(self.event_types(), ["TASK_CREATED"])

    def test_task_invalid_executor_enum_rejected(self):
        with self.assertRaises(SchemaValidationError):
            self.store.create_task(valid_task(executor="gemini"))
        self.assertEqual(self.audit_events(), [])

    def test_task_invalid_review_role_enum_rejected(self):
        with self.assertRaises(SchemaValidationError):
            self.store.create_task(valid_task(
                review_roles={"lead": "someone-else"}))
        self.assertEqual(self.audit_events(), [])

    def test_create_task_twice_rejected(self):
        self.store.create_task(valid_task())
        with self.assertRaises(StoreError):
            self.store.create_task(valid_task())
        self.assertEqual(self.event_types(), ["TASK_CREATED"])

    # -- set_status --------------------------------------------------

    def test_allowed_transition(self):
        self.store.create_task(valid_task())
        self.store.set_status("BRIDGE-0900", "READY", actor="steuerprozess")
        self.assertEqual(self.store.load_task("BRIDGE-0900")["status"], "READY")
        self.assertEqual(self.event_types(), ["TASK_CREATED", "TASK_READY"])

    def test_disallowed_transition_no_side_effects(self):
        self.store.create_task(valid_task())
        with self.assertRaises(state_machine.TransitionError):
            self.store.set_status("BRIDGE-0900", "RUNNING", actor="x")
        self.assertEqual(self.store.load_task("BRIDGE-0900")["status"], "CREATED")
        self.assertEqual(self.event_types(), ["TASK_CREATED"])

    def test_resume_special_case(self):
        self.store.create_task(valid_task())
        for state in ("READY", "CLAIMED", "RUNNING", "INTERRUPTED", "WAITING_FOR_RESUME"):
            self.store.set_status("BRIDGE-0900", state, actor="x")
        ev = self.store.set_status("BRIDGE-0900", "RUNNING", actor="x")
        self.assertEqual(ev["event_type"], "TASK_RESUMED")
        self.assertEqual(self.event_types()[-1], "TASK_RESUMED")

    # -- runs / results --------------------------------------------

    def test_next_run_id(self):
        self.store.create_task(valid_task())
        self.assertEqual(self.store.next_run_id("BRIDGE-0900"), "RUN-01")
        self.store.write_result(valid_result(run_id="RUN-01"))
        self.assertEqual(self.store.next_run_id("BRIDGE-0900"), "RUN-02")

    def test_write_result_writes_file_and_audit(self):
        self.store.create_task(valid_task())
        self.store.write_result(valid_result())
        self.assertTrue((self.tmp / "results" / "BRIDGE-0900" / "RUN-01" / "result.yaml").exists())
        self.assertEqual(self.event_types(), ["TASK_CREATED", "RESULT_WRITTEN"])

    def test_result_without_task_rejected(self):
        with self.assertRaises(StoreError):
            self.store.write_result(valid_result(bridge_task_id="BRIDGE-0901"))

    def test_result_existing_run_rejected(self):
        self.store.create_task(valid_task())
        self.store.write_result(valid_result())
        with self.assertRaises(StoreError):
            self.store.write_result(valid_result())

    # -- audit / pfade ---------------------------------------------

    def test_audit_append_only_and_schema_conform(self):
        self.store.create_task(valid_task())
        self.store.set_status("BRIDGE-0900", "READY", actor="x")
        first = (self.tmp / "audit" / "audit.jsonl").read_text(encoding="utf-8")
        self.store.set_status("BRIDGE-0900", "CLAIMED", actor="x")
        second = (self.tmp / "audit" / "audit.jsonl").read_text(encoding="utf-8")
        self.assertTrue(second.startswith(first))
        schema = yaml.safe_load((SCHEMA_DIR / "audit-event.schema.yaml").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=_FORMAT_CHECKER)
        for event in self.audit_events():
            validator.validate(event)

    # -- last_transition_at (BRIDGE-016) --------------------------

    def test_last_transition_at_finds_timestamp(self):
        self.store.create_task(valid_task())
        self.store.set_status("BRIDGE-0900", "READY", actor="x")
        self.store.set_status("BRIDGE-0900", "WAITING_FOR_HANDOFF_TO_EXECUTOR", actor="x")
        ts = self.store.last_transition_at(
            "BRIDGE-0900", "WAITING_FOR_HANDOFF_TO_EXECUTOR")
        match = [e for e in self.audit_events()
                 if e.get("new_state") == "WAITING_FOR_HANDOFF_TO_EXECUTOR"]
        self.assertEqual(ts, match[-1]["timestamp"])

    def test_last_transition_at_returns_last_occurrence(self):
        self.store.create_task(valid_task())
        for state in ("READY", "CLAIMED", "RUNNING", "FAILED", "READY"):
            self.store.set_status("BRIDGE-0900", state, actor="x")
        ready = [e for e in self.audit_events() if e.get("new_state") == "READY"]
        self.assertEqual(len(ready), 2)
        self.assertEqual(
            self.store.last_transition_at("BRIDGE-0900", "READY"),
            ready[-1]["timestamp"])

    def test_last_transition_at_none_without_match(self):
        self.store.create_task(valid_task())
        self.assertIsNone(self.store.last_transition_at("BRIDGE-0900", "ARCHIVED"))
        self.assertIsNone(self.store.last_transition_at("BRIDGE-9999", "READY"))

    def test_path_escaping_rejected(self):
        with self.assertRaises(StoreError):
            self.store.load_task("../../evil")
        with self.assertRaises(StoreError):
            self.store.next_run_id("BRIDGE-0900/../../evil")

    # -- set_priority (BRIDGE-028) -------------------------------------------

    def test_set_priority_changes_field_and_writes_audit(self):
        """set_priority schreibt das Feld und einen PRIORITY_CHANGED-Eintrag."""
        self.store.create_task(valid_task())
        event = self.store.set_priority("BRIDGE-0900", "HIGH", actor="test")
        self.assertEqual(event["event_type"], "PRIORITY_CHANGED")
        self.assertEqual(event["reason"], "MEDIUM -> HIGH")
        task = self.store.load_task("BRIDGE-0900")
        self.assertEqual(task["priority"], "HIGH")
        self.assertIn("PRIORITY_CHANGED", self.event_types())

    def test_set_priority_readable_reason_format(self):
        """reason enthaelt den alten und neuen Wert lesbar (z.B. 'MEDIUM -> LOW')."""
        self.store.create_task(valid_task())
        event = self.store.set_priority("BRIDGE-0900", "LOW", actor="test")
        self.assertIn("->", event["reason"])
        old, new = event["reason"].split("->")
        self.assertEqual(old.strip(), "MEDIUM")   # Default
        self.assertEqual(new.strip(), "LOW")

    def test_set_priority_invalid_value_rejected(self):
        """Ungueltige Prioritaet wird fail-closed abgelehnt."""
        self.store.create_task(valid_task())
        with self.assertRaises(StoreError):
            self.store.set_priority("BRIDGE-0900", "URGENT", actor="test")
        # Auftrags-Feld unveraendert
        task = self.store.load_task("BRIDGE-0900")
        self.assertNotIn("priority", task)

    def test_set_priority_unknown_task_rejected(self):
        """Unbekannte task_id -> StoreError (fail-closed)."""
        with self.assertRaises(StoreError):
            self.store.set_priority("BRIDGE-9999", "HIGH", actor="test")

    def test_task_priority_field_optional_default_medium(self):
        """Bestehende task.yaml ohne priority-Feld bleibt gueltig (Default MEDIUM)."""
        doc = valid_task()
        self.assertNotIn("priority", doc)
        # validate darf keinen Fehler werfen
        self.store.validate(doc)

    def test_task_priority_valid_values_accepted(self):
        """Schema akzeptiert priority: LOW, MEDIUM, HIGH."""
        for val in ("LOW", "MEDIUM", "HIGH"):
            doc = valid_task(priority=val)
            self.store.validate(doc)   # kein Fehler

    def test_task_priority_invalid_value_rejected_by_schema(self):
        """Schema lehnt ungueltige priority-Werte ab (fail-closed)."""
        doc = valid_task(priority="URGENT")
        with self.assertRaises(SchemaValidationError):
            self.store.validate(doc)

    # -- task_type / allowed_paths / forbidden_actions / stop_conditions (BRIDGE-0047) --

    def test_task_new_fields_valid(self):
        self.store.validate(valid_task(
            task_type="T2", allowed_paths=["schemas/", "src/bridge/"],
            forbidden_actions=["git push --force"],
            stop_conditions=["CONCEPT_CONFLICT", "SCOPE_VIOLATION"]))
        self.store.validate(valid_task(task_type=None))

    def test_task_unknown_stop_condition_rejected(self):
        with self.assertRaises(SchemaValidationError):
            self.store.validate(valid_task(stop_conditions=["EXPLODE"]))

    def test_task_invalid_task_type_rejected(self):
        with self.assertRaises(SchemaValidationError):
            self.store.validate(valid_task(task_type="T9"))

    def test_task_without_new_fields_still_valid(self):
        # Regression: alte task.yaml ohne die vier Felder bleiben gueltig
        doc = valid_task()
        for key in ("task_type", "allowed_paths", "forbidden_actions", "stop_conditions"):
            self.assertNotIn(key, doc)
        self.store.validate(doc)
        self.store.create_task(doc)


class IdFormatTests(unittest.TestCase):
    """BRIDGE-015: <PRAEFIX bis 8 Grossbuchstaben>-<4 Ziffern>."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ccb-idfmt-"))
        for name in ("tasks", "results", "audit"):
            (self.tmp / name).mkdir()
        self.store = Store(root=self.tmp, schema_dir=SCHEMA_DIR)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_non_bridge_prefix_accepted(self):
        doc = self.store.create_task(valid_task(bridge_task_id="DORF-0001"))
        self.assertEqual(doc["bridge_task_id"], "DORF-0001")
        self.assertTrue((self.tmp / "tasks" / "DORF-0001" / "task.yaml").exists())
        self.store.validate(valid_task(bridge_task_id="DORF-0001"))

    def test_three_digit_number_rejected(self):
        with self.assertRaises(StoreError):
            self.store.create_task(valid_task(bridge_task_id="BRIDGE-042"))
        self.assertFalse((self.tmp / "tasks" / "BRIDGE-042").exists())

    def test_nine_letter_prefix_rejected(self):
        with self.assertRaises(StoreError):
            self.store.create_task(valid_task(bridge_task_id="ABCDEFGHI-0001"))


class ReviewSuffixTests(unittest.TestCase):
    """BRIDGE-032: -R<n>-Unternummern + fail-closed READONLY_CHECK-Durchsetzung."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ccb-review-"))
        for name in ("tasks", "results", "audit"):
            (self.tmp / name).mkdir()
        self.store = Store(root=self.tmp, schema_dir=SCHEMA_DIR)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_review_suffix_without_readonly_check_task_class_rejected(self):
        self.store.create_task(valid_task(bridge_task_id="BRIDGE-0900"))
        with self.assertRaises(StoreError):
            self.store.create_task(valid_task(
                bridge_task_id="BRIDGE-0900-R1",
                task_class="FEATURE",
                permissions=["READ_ONLY"],
            ))
        self.assertFalse((self.tmp / "tasks" / "BRIDGE-0900-R1").exists())

    def test_readonly_check_with_extra_permissions_rejected(self):
        with self.assertRaises(StoreError):
            self.store.create_task(valid_task(
                task_class="READONLY_CHECK",
                permissions=["READ_ONLY", "WORKTREE_WRITE"],
            ))
        self.assertFalse((self.tmp / "tasks" / "BRIDGE-0900").exists())

    def test_readonly_check_missing_read_only_rejected(self):
        with self.assertRaises(StoreError):
            self.store.create_task(valid_task(
                task_class="READONLY_CHECK",
                permissions=["WORKTREE_WRITE"],
            ))
        self.assertFalse((self.tmp / "tasks" / "BRIDGE-0900").exists())

    def test_review_suffix_without_existing_base_task_rejected(self):
        with self.assertRaises(StoreError):
            self.store.create_task(valid_task(
                bridge_task_id="BRIDGE-0901-R1",
                task_class="READONLY_CHECK",
                permissions=["READ_ONLY"],
            ))
        self.assertFalse((self.tmp / "tasks" / "BRIDGE-0901-R1").exists())

    def test_review_suffix_with_existing_base_task_accepted(self):
        self.store.create_task(valid_task(bridge_task_id="BRIDGE-0900"))
        doc = self.store.create_task(valid_task(
            bridge_task_id="BRIDGE-0900-R1",
            task_class="READONLY_CHECK",
            permissions=["READ_ONLY"],
        ))
        self.assertEqual(doc["bridge_task_id"], "BRIDGE-0900-R1")
        self.assertTrue(
            (self.tmp / "tasks" / "BRIDGE-0900-R1" / "task.yaml").exists())

    def test_save_task_rejects_permission_escalation_on_readonly_check(self):
        self.store.create_task(valid_task(bridge_task_id="BRIDGE-0900"))
        doc = self.store.create_task(valid_task(
            bridge_task_id="BRIDGE-0900-R1",
            task_class="READONLY_CHECK",
            permissions=["READ_ONLY"],
        ))
        doc = dict(doc)
        doc["permissions"] = ["READ_ONLY", "GIT_PUSH"]
        with self.assertRaises(StoreError):
            self.store.save_task(doc)

    def test_readonly_check_without_review_suffix_still_accepted(self):
        """Regressionscheck: BRIDGE-0912-artiger Fall (integration_readonly.py)
        bleibt unveraendert lauffaehig."""
        doc = self.store.create_task(valid_task(
            bridge_task_id="BRIDGE-0912",
            task_class="READONLY_CHECK",
            permissions=["READ_ONLY"],
        ))
        self.assertEqual(doc["bridge_task_id"], "BRIDGE-0912")
        self.assertTrue(
            (self.tmp / "tasks" / "BRIDGE-0912" / "task.yaml").exists())


def _write_profile(projects_dir: Path, project_id: str, task_prefix: str) -> None:
    """Minimales, schema-gueltiges Projektprofil fuer Tests (BRIDGE-034)."""
    proj_dir = projects_dir / project_id
    proj_dir.mkdir(parents=True, exist_ok=True)
    doc = {
        "schema_version": "1.0",
        "kind": "bridge_project_profile",
        "project_id": project_id,
        "repository": project_id,
        "default_branch": "main",
        "task_prefix": task_prefix,
        "read_only": True,
    }
    (proj_dir / "project.yaml").write_text(
        yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


class TaskPrefixCollisionTests(unittest.TestCase):
    """BRIDGE-034: create_task() lehnt Auftraege fail-closed ab, wenn das
    Zielprojekt einen mit einem anderen Projektprofil kollidierenden
    task_prefix traegt. Nur create_task(), nicht save_task() (task_prefix
    ist eine Projekt-, keine Auftragseigenschaft)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ccb-prefix-"))
        for name in ("tasks", "results", "audit"):
            (self.tmp / name).mkdir()
        self.store = Store(root=self.tmp, schema_dir=SCHEMA_DIR)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_synthetic_collision_rejected(self):
        projects_dir = self.tmp / "projects"
        _write_profile(projects_dir, "proj-a", "DUP")
        _write_profile(projects_dir, "proj-b", "DUP")
        with self.assertRaises(StoreError):
            self.store.create_task(valid_task(
                bridge_task_id="DUP-0001", project_id="proj-b"))
        self.assertFalse((self.tmp / "tasks" / "DUP-0001").exists())

    def test_no_collision_without_projects_dir(self):
        """Hermetischer Store ohne projects/-Verzeichnis: Pruefung greift
        nicht (kein falsches Positiv fuer bestehende Tests ohne Profile)."""
        doc = self.store.create_task(valid_task())
        self.assertEqual(doc["bridge_task_id"], "BRIDGE-0900")

    def test_real_seven_profiles_collision_free(self):
        """Regressionscheck gegen die echten projects/*/project.yaml-Dateien
        (nicht nur synthetisch): kein falsches Positiv unter den sieben
        bestehenden Profilen."""
        from bridge import profiles
        real_store = Store(root=REPO_ROOT, schema_dir=SCHEMA_DIR)
        real_project_ids = profiles.list_profiles(REPO_ROOT)
        self.assertGreaterEqual(len(real_project_ids), 7)
        for project_id in real_project_ids:
            doc = valid_task(project_id=project_id)
            # Nur die private Pruefmethode, nicht create_task() - schreibt
            # nichts ins echte Repo.
            real_store._check_task_prefix_collision(doc)


class DorfschaftProfileTests(unittest.TestCase):
    """BRIDGE-034: Regressionsanker gegen versehentliches erneutes
    Zurueckflippen von read_only ohne bewusste Entscheidung."""

    def test_dorfschaft_profile_is_read_only(self):
        from bridge import profiles
        profile = profiles.load_profile(REPO_ROOT, "dorfschaft", schema_dir=SCHEMA_DIR)
        self.assertIs(profile.get("read_only"), True)
        git_policy = profile.get("git_policy") or {}
        self.assertIs(git_policy.get("allow_push"), False)


def valid_draft(**over):
    doc = {
        "kind": "bridge_draft",
        "draft_version": "draft-a-1",
        "bridge_task_id": "BRIDGE-0900",
        "run_id": "RUN-01",
        "status": "COMPLETED",
        "summary": "Draft-Test",
        "base_head": "0" * 40,
        "head_after": "1" * 40,
        "branch": "main",
        "repository": "Agent-Control-Bridge",
        "changed_files": ["schemas/draft.schema.yaml"],
        "tests": {"passed": 4, "failed": 0, "blocked": 0},
        "findings": [{"id": "F1", "severity": "LOW", "text": "Hinweis"}],
        "next_action": "Import",
    }
    doc.update(over)
    return doc


class DraftSchemaTests(unittest.TestCase):
    """BRIDGE-0049 Teil A: draft.schema.yaml + additive result-Felder."""

    def setUp(self):
        schema = yaml.safe_load((SCHEMA_DIR / "draft.schema.yaml").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        self.validator = Draft202012Validator(schema, format_checker=_FORMAT_CHECKER)

    def errors(self, doc):
        return list(self.validator.iter_errors(doc))

    def test_valid_draft(self):
        self.assertEqual(self.errors(valid_draft()), [])
        self.assertEqual(self.errors(valid_draft(error_code="SCOPE_VIOLATION")), [])

    def test_missing_required_field(self):
        doc = valid_draft()
        del doc["summary"]
        self.assertTrue(self.errors(doc))

    def test_unknown_field_rejected(self):
        self.assertTrue(self.errors(valid_draft(bogus=1)))

    def test_wrong_draft_version(self):
        self.assertTrue(self.errors(valid_draft(draft_version="draft-a-2")))

    def test_result_accepts_optional_tests_and_findings(self):
        store_schema = yaml.safe_load((SCHEMA_DIR / "result.schema.yaml").read_text(encoding="utf-8"))
        v = Draft202012Validator(store_schema, format_checker=_FORMAT_CHECKER)
        self.assertEqual(list(v.iter_errors(valid_result())), [])
        extended = valid_result(
            tests={"passed": 1, "failed": 0, "blocked": 0},
            findings=[{"id": "F1", "severity": "LOW", "text": "x"}],
        )
        self.assertEqual(list(v.iter_errors(extended)), [])
        self.assertTrue(list(v.iter_errors(valid_result(tests={"passed": 1}))))


if __name__ == "__main__":
    unittest.main()
