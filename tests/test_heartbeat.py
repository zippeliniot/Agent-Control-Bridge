"""Minimaltests für src/bridge/heartbeat.py (BRIDGE-032: ID-Muster)."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from bridge import heartbeat  # noqa: E402
from bridge.store import StoreError  # noqa: E402


class HeartbeatIdPatternTests(unittest.TestCase):
    """BRIDGE-032: eigene _ID_RE-Kopie in heartbeat.py akzeptiert -R<n>-IDs
    ebenso wie store.py."""

    def test_review_suffix_id_accepted(self):
        # wirft nicht -> bridge_task_id mit -R<n>-Suffix ist zulässig.
        heartbeat._check("BRIDGE-0900-R1", "RUN-01")

    def test_plain_id_still_accepted(self):
        heartbeat._check("BRIDGE-0900", "RUN-01")

    def test_malformed_id_rejected(self):
        with self.assertRaises(StoreError):
            heartbeat._check("BRIDGE-042", "RUN-01")


if __name__ == "__main__":
    unittest.main()
