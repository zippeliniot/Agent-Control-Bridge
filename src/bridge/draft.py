"""Executor-Draft schreiben (BRIDGE-0053 Teil A).

Die Ausfuehrungsinstanz legt ihr Ergebnis als Draft unter
``drafts/<id>/RUN-yy/draft.yaml`` ab. Der Import (Board-Seite) folgt getrennt.

Sicherheits-Leitplanken:
- Geschrieben wird nur ``drafts/`` (ueber ``Store.write_draft``); nie tasks/,
  results/ oder audit/, kein Statuswechsel, nie Push.
- Git-Nachweis ueber ``importer.collect_git_info`` (injizierbar per
  ``git_info_fn``); ``git.expected_head`` des Auftrags ist Pflicht (fail-closed).
- Unsauberer Worktree -> ``DIRTY_WORKTREE``, kein Draft.
- Geaenderte Dateien ausserhalb des erlaubten Scopes -> Draft-Status BLOCKED
  mit ``error_code`` SCOPE_VIOLATION.
"""

from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path

# src-Layout: direkter Skriptaufruf braucht das Paketverzeichnis auf dem Pfad.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bridge import importer, runner
from bridge.store import StoreError

DRAFT_VERSION = "draft-a-1"

_TESTS_RE = re.compile(r"^([0-9]+)/([0-9]+)/([0-9]+)$")


class DraftError(StoreError):
    """Draft nicht schreibbar (fail-closed). ``code`` = Fehlercode oder None."""

    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


def parse_tests(text) -> dict:
    """``P/F/B`` -> ``{passed, failed, blocked}``; ``None`` -> alles 0."""
    if text is None:
        return {"passed": 0, "failed": 0, "blocked": 0}
    match = _TESTS_RE.match(str(text).strip())
    if match is None:
        raise DraftError(f"--tests erwartet P/F/B (z. B. 12/0/0), erhalten: {text!r}")
    passed, failed, blocked = (int(g) for g in match.groups())
    return {"passed": passed, "failed": failed, "blocked": blocked}


def _worktree_dirty(root) -> bool:
    return bool(importer._lines(importer._git(root, "status", "--porcelain")))


def _allowed(path: str, allowed: list[str]) -> bool:
    path = path.replace("\\", "/")
    for entry in allowed:
        entry = entry.replace("\\", "/")
        if entry.endswith("/"):
            if path.startswith(entry):
                return True
        elif path == entry or fnmatch.fnmatchcase(path, entry):
            return True
    return False


def _bridge_managed(path: str, task_id: str) -> bool:
    """Vom Bridge-Lebenszyklus (task create / run start) selbst erzeugte
    Dateien des eigenen Auftrags - kein Scope-Verstoss des Executors."""
    return (path == "audit/audit.jsonl"
            or path.startswith((f"tasks/{task_id}/", f"results/{task_id}/",
                                f"drafts/{task_id}/")))


def scope_violations(task: dict, changed_files: list[str]) -> list[str]:
    """Geaenderte Dateien ausserhalb von ``allowed_paths`` (bzw. Fallback
    ``git.allowed_changed_files``). Deklariert der Auftrag keinen Scope, gibt
    es nichts zu pruefen. Bridge-verwaltete Dateien des eigenen Auftrags
    (tasks/results/drafts/<id>/, audit.jsonl) zaehlen nicht."""
    allowed = list(task.get("allowed_paths") or [])
    if not allowed:
        allowed = list((task.get("git") or {}).get("allowed_changed_files") or [])
    if not allowed:
        return []
    task_id = task.get("bridge_task_id", "")
    return sorted(p for p in changed_files
                  if not _bridge_managed(p, task_id) and not _allowed(p, allowed))


def write_draft(store, task_id, status, summary, tests=None, *,
                git_info_fn=importer.collect_git_info) -> dict:
    """Erzeugt und legt einen validen Draft ab; gibt das Draft-Dokument zurueck."""
    task = store.load_task(task_id)
    base_head = (task.get("git") or {}).get("expected_head")
    if not base_head:
        raise DraftError(
            f"git.expected_head fehlt in task.yaml von {task_id} (fail-closed).")
    run_id = runner.current_run_id(store, task_id)
    if run_id is None:
        raise DraftError(f"Kein Lauf fuer {task_id} vorhanden (erst run start).")

    if _worktree_dirty(store.root):
        raise DraftError("Working Tree nicht sauber - vor draft write committen.",
                         code="DIRTY_WORKTREE")

    info = git_info_fn(store.root, base_head)
    draft = {
        "kind": "bridge_draft",
        "draft_version": DRAFT_VERSION,
        "bridge_task_id": task_id,
        "run_id": run_id,
        "status": status,
        "summary": summary,
        "base_head": base_head,
        "head_after": info["head"],
        "branch": info["branch"],
        "repository": info["repository"],
        "changed_files": list(info["changed_files"]),
        "tests": parse_tests(tests),
        "findings": [],
        "next_action": "",
    }
    violations = scope_violations(task, draft["changed_files"])
    if violations:
        draft["status"] = "BLOCKED"
        draft["error_code"] = "SCOPE_VIOLATION"
        draft["findings"] = [{
            "id": "SCOPE-1", "severity": "high",
            "text": "Aenderungen ausserhalb allowed_paths: " + ", ".join(violations),
        }]
    return store.write_draft(draft)
