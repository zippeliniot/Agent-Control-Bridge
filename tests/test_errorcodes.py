"""Hermetische Tests fuer die Fehlercodes (BRIDGE-0047 Teil C). stdlib unittest."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import yaml  # noqa: E402

from bridge import errorcodes  # noqa: E402

SCHEMA_DIR = REPO_ROOT / "schemas"


class ErrorCodesTests(unittest.TestCase):
    def test_load_and_state_blocked(self):
        codes = errorcodes.load_error_codes(SCHEMA_DIR)
        self.assertEqual(len(codes), 5)
        for entry in codes.values():
            self.assertEqual(entry["state"], "BLOCKED")
            self.assertTrue(entry["description"])

    def test_is_known(self):
        errorcodes.load_error_codes(SCHEMA_DIR)
        self.assertTrue(errorcodes.is_known("HEAD_MISMATCH"))
        self.assertFalse(errorcodes.is_known("EXPLODE"))
        self.assertFalse(errorcodes.is_known(None))
        self.assertTrue(errorcodes.is_known("SCOPE_VIOLATION", SCHEMA_DIR))

    def test_ssot_equals_stop_conditions_enum(self):
        task_schema = yaml.safe_load(
            (SCHEMA_DIR / "task.schema.yaml").read_text(encoding="utf-8"))
        enum = task_schema["properties"]["stop_conditions"]["items"]["enum"]
        self.assertEqual(set(errorcodes.load_error_codes(SCHEMA_DIR)), set(enum))

    def test_codes_map_to_existing_state(self):
        model = (SCHEMA_DIR / "state-model.yaml").read_text(encoding="utf-8")
        self.assertIn("BLOCKED", model)

    def test_missing_file_fails_closed(self):
        tmp = Path(tempfile.mkdtemp(prefix="acb-errcodes-"))
        try:
            with self.assertRaises(errorcodes.ErrorCodeError):
                errorcodes.load_error_codes(tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
