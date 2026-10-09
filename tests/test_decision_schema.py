"""Schema-Smoke-Test fuer decision.schema.yaml (BRIDGE-0097).

Reiner Schema-Entwurf, keine Store-/CLI-Anbindung - deshalb kein Store-Objekt
nötig, nur der generische JSON-Schema-Validator direkt gegen Beispieldokumente.
stdlib unittest, hermetisch.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import yaml  # noqa: E402
from jsonschema import Draft202012Validator, FormatChecker  # noqa: E402
from jsonschema.exceptions import SchemaError, ValidationError  # noqa: E402

SCHEMA_PATH = REPO_ROOT / "schemas" / "decision.schema.yaml"
TS = "2026-10-09T14:00:00Z"


def _load_validator() -> Draft202012Validator:
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def valid_event(**over):
    doc = {
        "schema_version": "1.0",
        "kind": "decision_event",
        "decision_id": "agent-control-bridge-DECISION-0001",
        "project_id": "agent-control-bridge",
        "event_type": "PROPOSED",
        "event_at": TS,
        "actor": "april",
        "title": "Testentscheidung",
        "doc_ref": "docs/concepts/ENTSCHEIDUNG-TEST.md",
    }
    doc.update(over)
    return doc


class DecisionSchemaTests(unittest.TestCase):
    def setUp(self):
        self.validator = _load_validator()

    def test_schema_itself_is_valid_json_schema(self):
        # Wirft SchemaError bei Fehler - bereits in _load_validator via
        # check_schema geprueft, hier nur als eigener, benannter Testfall.
        _load_validator()

    def test_minimal_valid_event_passes(self):
        self.validator.validate(valid_event())

    def test_missing_required_field_rejected(self):
        doc = valid_event()
        del doc["doc_ref"]
        with self.assertRaises(ValidationError):
            self.validator.validate(doc)

    def test_wrong_kind_rejected(self):
        with self.assertRaises(ValidationError):
            self.validator.validate(valid_event(kind="something_else"))

    def test_unknown_event_type_rejected(self):
        with self.assertRaises(ValidationError):
            self.validator.validate(valid_event(event_type="MAYBE"))

    def test_malformed_decision_id_rejected(self):
        with self.assertRaises(ValidationError):
            self.validator.validate(valid_event(decision_id="not-a-valid-id"))

    def test_additional_property_rejected(self):
        with self.assertRaises(ValidationError):
            self.validator.validate(valid_event(unexpected_field="x"))

    def test_superseded_event_with_scoped_reference_passes(self):
        doc = valid_event(
            event_type="SUPERSEDED",
            supersedes=[{
                "decision_id": "agent-control-bridge-DECISION-0000",
                "scope": "Abschnitt 3 (Formalisierungsebene)",
            }],
        )
        self.validator.validate(doc)

    def test_revision_bound_affects_entry_passes(self):
        doc = valid_event(affects=[{
            "repo": "zippeliniot/Agent-Control-Bridge",
            "revision": "454050b9b7501cdcdef5393b1fa55ec2f3f257ee",
            "path": "docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md",
        }])
        self.validator.validate(doc)

    def test_revision_ref_without_path_rejected(self):
        doc = valid_event(affects=[{
            "repo": "zippeliniot/Agent-Control-Bridge",
            "revision": "454050b9b7501cdcdef5393b1fa55ec2f3f257ee",
        }])
        with self.assertRaises(ValidationError):
            self.validator.validate(doc)


if __name__ == "__main__":
    unittest.main()
