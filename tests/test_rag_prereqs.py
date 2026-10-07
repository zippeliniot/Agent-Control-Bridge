"""Tests fuer rag_prereqs.check() (BRIDGE-0083): reine Erkennung von
Ollama-Erreichbarkeit, Embedding-Modell und Index-Klon, fail-soft."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bridge import rag_prereqs  # noqa: E402


class _FakeResponse:
    def __init__(self, payload):
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


class RagPrereqsCheckTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _make_clone(self):
        clone = self.tmp / "rag-index"
        (clone / ".git").mkdir(parents=True)
        return clone

    def test_all_present(self):
        clone = self._make_clone()
        with mock.patch(
            "bridge.rag_prereqs.urllib.request.urlopen",
            return_value=_FakeResponse({"models": [{"name": "nomic-embed-text:latest"}]}),
        ):
            result = rag_prereqs.check(clone)
        self.assertEqual(result, {
            "ollama_reachable": True,
            "embed_model_present": True,
            "index_clone_exists": True,
            "missing": [],
            "all_ok": True,
        })

    def test_ollama_unreachable(self):
        clone = self._make_clone()
        with mock.patch(
            "bridge.rag_prereqs.urllib.request.urlopen",
            side_effect=OSError("connection refused"),
        ):
            result = rag_prereqs.check(clone)
        self.assertFalse(result["ollama_reachable"])
        self.assertFalse(result["embed_model_present"])
        self.assertTrue(result["index_clone_exists"])
        self.assertIn("ollama", result["missing"])
        self.assertFalse(result["all_ok"])

    def test_embed_model_missing(self):
        clone = self._make_clone()
        with mock.patch(
            "bridge.rag_prereqs.urllib.request.urlopen",
            return_value=_FakeResponse({"models": [{"name": "llama3:latest"}]}),
        ):
            result = rag_prereqs.check(clone)
        self.assertTrue(result["ollama_reachable"])
        self.assertFalse(result["embed_model_present"])
        self.assertIn("embed_model:nomic-embed-text", result["missing"])
        self.assertFalse(result["all_ok"])

    def test_index_clone_missing(self):
        missing_path = self.tmp / "rag-index"  # nie erzeugt
        with mock.patch(
            "bridge.rag_prereqs.urllib.request.urlopen",
            return_value=_FakeResponse({"models": [{"name": "nomic-embed-text:latest"}]}),
        ):
            result = rag_prereqs.check(missing_path)
        self.assertFalse(result["index_clone_exists"])
        self.assertIn("index_clone", result["missing"])
        self.assertFalse(result["all_ok"])

    def test_all_missing_at_once(self):
        missing_path = self.tmp / "rag-index"
        with mock.patch(
            "bridge.rag_prereqs.urllib.request.urlopen",
            side_effect=TimeoutError("timed out"),
        ):
            result = rag_prereqs.check(missing_path)
        self.assertEqual(result["missing"],
                         ["ollama", "embed_model:nomic-embed-text", "index_clone"])
        self.assertFalse(result["all_ok"])

    def test_malformed_response_is_fail_soft(self):
        clone = self._make_clone()
        with mock.patch(
            "bridge.rag_prereqs.urllib.request.urlopen",
            return_value=_FakeResponse({"unexpected": "shape"}),
        ):
            result = rag_prereqs.check(clone)
        self.assertFalse(result["ollama_reachable"])
        self.assertFalse(result["all_ok"])


if __name__ == "__main__":
    unittest.main()
