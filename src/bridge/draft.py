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
import os
import re
import sys
from pathlib import Path

# src-Layout: direkter Skriptaufruf braucht das Paketverzeichnis auf dem Pfad.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml

from bridge import importer, runner, state_machine
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
    # Lauf-ID wie im Import bestimmen - kein ``run start`` noetig (schriebe
    # tasks/results/audit, im Draft-Modus dem Executor verboten).
    task_status = task.get("status")
    if task_status == "RUNNING":
        run_id = runner.current_run_id(store, task_id)
        if run_id is None:
            raise DraftError(f"Kein laufender RUN fuer {task_id} vorhanden.")
    elif task_status in runner._START_FROM:
        run_id = store.next_run_id(task_id)
    else:
        raise DraftError(f"Draft nicht moeglich: Auftrag ist {task_status}.")

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


# --------------------------------------------------------------------------- #
# Import (Board-Seite, BRIDGE-0053 Teil B)
# --------------------------------------------------------------------------- #

BOARD_DIR_NAME = "board"
ALLOW_ANY_CLONE_ENV = "ACB_ALLOW_ANY_CLONE"

_RUN_DIR_RE = re.compile(r"^RUN-[0-9]{2,}$")


def writer_guard_ok(store) -> bool:
    """Nur der Klon ``board`` darf importieren (``ACB_ALLOW_ANY_CLONE=1``: nur Tests)."""
    return (store.root.name == BOARD_DIR_NAME
            or os.environ.get(ALLOW_ANY_CLONE_ENV) == "1")


def _latest_draft_run(store, task_id):
    base = store.drafts_dir / task_id
    runs = sorted((e.name for e in base.iterdir()
                   if e.is_dir() and _RUN_DIR_RE.match(e.name)),
                  key=lambda r: int(r.split("-")[1])) if base.exists() else []
    if not runs:
        raise DraftError(f"Kein Draft fuer {task_id} vorhanden.")
    return runs[-1]


def _draft_git_info(doc):
    """Git-Nachweis aus dem Draft (kein Git-Zugriff im Import)."""
    def fn(root, base_head=None):
        return {"repository": doc["repository"], "branch": doc["branch"],
                "head": doc["head_after"], "base_head": doc["base_head"],
                "commits": [], "changed_files": list(doc["changed_files"])}
    return fn


def plan_import(store, task_id, run_id=None) -> dict:
    """Rein lesende Vorpruefung. Gibt ``{draft, run_id, noop, steps}`` zurueck;
    wirft ``DraftError`` bei jedem Verstoss (Draft ungueltig, Zustandsuebergang
    nicht erlaubt, Lauf-Konflikt)."""
    task = store.load_task(task_id)
    run_id = run_id or _latest_draft_run(store, task_id)
    doc = store.load_draft(task_id, run_id)
    store.validate(doc)
    if doc["bridge_task_id"] != task_id or doc["run_id"] != run_id:
        raise DraftError(
            f"Draft-Inhalt passt nicht zu {task_id}/{run_id} (fail-closed).")

    result_path = store.results_dir / task_id / run_id / "result.yaml"
    if result_path.exists():
        existing = yaml.safe_load(result_path.read_text(encoding="utf-8")) or {}
        if (existing.get("status") == doc["status"]
                and existing.get("head") == doc["head_after"]):
            return {"draft": doc, "run_id": run_id, "noop": True,
                    "steps": [f"Draft {task_id} {run_id} bereits importiert - nichts zu tun"]}
        raise DraftError(
            f"Ergebnis {task_id} {run_id} existiert bereits und weicht vom Draft ab.")

    status = task.get("status")
    steps = []
    if status in runner._START_FROM:
        if store.next_run_id(task_id) != run_id:
            raise DraftError(
                f"Draft-Lauf {run_id} passt nicht zum naechsten Lauf "
                f"{store.next_run_id(task_id)} (fail-closed).")
        steps.append(f"runner.start {task_id}: {status} -> RUNNING ({run_id})")
    elif status == "RUNNING":
        if runner.current_run_id(store, task_id) != run_id:
            raise DraftError(
                f"Laufender Lauf ist {runner.current_run_id(store, task_id)}, "
                f"Draft ist {run_id} (fail-closed).")
    else:
        raise DraftError(f"Import nicht moeglich: Auftrag ist {status}.")
    if not state_machine.is_allowed("RUNNING", doc["status"]):
        raise DraftError(
            f"Uebergang RUNNING -> {doc['status']} nicht erlaubt (fail-closed).")
    steps.append(f"runner.finish {task_id}: RUNNING -> {doc['status']}; "
                 f"schreibt results/{task_id}/{run_id}/result.yaml + Audit")
    return {"draft": doc, "run_id": run_id, "noop": False, "steps": steps}


def import_draft(store, task_id, run_id=None, *, actor, machine=None,
                 dry_run=False) -> dict:
    """Draft -> result.yaml + Statuswechsel + Audit (runner.start/finish).

    ``dry_run`` schreibt nichts. Idempotent: ein bereits importierter Draft
    ist ein No-op."""
    plan = plan_import(store, task_id, run_id)
    plan["dry_run"] = dry_run
    plan["guard_ok"] = writer_guard_ok(store)
    if plan["noop"] or dry_run:
        return plan
    if not plan["guard_ok"]:
        raise DraftError(
            f"Import nur im Klon '{BOARD_DIR_NAME}' erlaubt (Klon: {store.root.name}).",
            code="SCOPE_VIOLATION")
    doc = plan["draft"]
    if store.load_task(task_id)["status"] in runner._START_FROM:
        runner.start(store, task_id, actor, machine)
    summary = doc["summary"]
    if doc.get("error_code"):
        summary = f"[{doc['error_code']}] {summary}"
    runner.finish(store, task_id, doc["status"],
                  draft={"tests": doc.get("tests"), "findings": doc.get("findings")},
                  base_head=doc["base_head"], actor=actor, machine=machine,
                  summary=summary, git_info_fn=_draft_git_info(doc))
    return plan
