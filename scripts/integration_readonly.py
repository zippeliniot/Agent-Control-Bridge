#!/usr/bin/env python
"""BRIDGE-012 - Read-only-Integrationstest gegen ein echtes Git-Repo.

Beobachtet ein Zielrepo (Default: das ACB-Repo, in dem dieses Skript liegt) rein
lesend über den Read-only-Adapter (BRIDGE-011) und legt ALLE Bridge-Ausgaben in
einem separaten Store-root ab (Default: neues Temp-Verzeichnis). Weist nach,
dass das Zielrepo dabei unverändert bleibt (HEAD + Working Tree vorher == nachher).

Aufruf über den venv-Python:
    .venv/Scripts/python.exe scripts/integration_readonly.py [--target <pfad>] [--out <pfad>]

Exit 0 = PASS (Zielrepo unverändert, Ergebnis valide), != 0 = FAIL (fail-closed).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

from bridge import adapter, importer
from bridge.store import Store

DEFAULT_TASK_ID = "BRIDGE-0912"  # interner Beobachtungs-Auftrag (nur im Scratch-Store)


def _git(target, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(target), *args],
                          capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} rc={proc.returncode}: {proc.stderr.strip()}")
    return proc.stdout


def _snapshot(target) -> dict:
    return {
        "head": _git(target, "rev-parse", "HEAD").strip(),
        "status": _git(target, "status", "--porcelain"),
    }


def _observation_task(task_id: str, target_name: str, project_id: str) -> dict:
    return {
        "schema_version": "1.0",
        "kind": "bridge_task",
        "bridge_task_id": task_id,
        "project_id": project_id,
        "title": f"Read-only-Beobachtung von {target_name}",
        "description": "BRIDGE-012 Integrationstest: Zielrepo wird ausschliesslich gelesen.",
        "task_class": "READONLY_CHECK",
        "repository": target_name,
        "branch": "main",
        "permissions": ["READ_ONLY"],
        "status": "CREATED",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_by": "integration_readonly.py",
    }


def run(target: Path, out: Path, schema_dir: Path, task_id: str = DEFAULT_TASK_ID, *,
        project_id: str = "agent-control-bridge", task_prefix: str = "BRIDGE",
        expected_branch: str | None = None, expected_head: str | None = None) -> dict:
    """Führt die Read-only-Beobachtung aus und gibt einen Report (dict) zurück.
    Wirft bei jedem Fehler (fail-closed)."""
    target = Path(target).resolve()
    out = Path(out).resolve()
    if out == target or target in out.parents or out in target.parents:
        raise RuntimeError("--out darf nicht im Zielrepo liegen (oder umgekehrt).")

    before = _snapshot(target)

    if expected_head is not None and not before["head"].startswith(expected_head):
        raise RuntimeError(
            f"Pre-Flight-Head-Check fehlgeschlagen: erwartet {expected_head}, "
            f"tatsaechlich {before['head']}.")

    default_branch = expected_branch if expected_branch else "main"
    profile = {
        "schema_version": "1.0", "kind": "bridge_project_profile",
        "project_id": project_id, "repository": target.name,
        "default_branch": default_branch, "task_prefix": task_prefix, "read_only": True,
    }
    ro = adapter.ReadOnlyProjectAdapter(profile, target, schema_dir=schema_dir)
    git_info = ro.git_info()

    for name in ("tasks", "results", "audit"):
        (out / name).mkdir(parents=True, exist_ok=True)
    store = Store(root=out, schema_dir=schema_dir)
    store.create_task(_observation_task(task_id, target.name, project_id))
    result = importer.import_result(
        store, task_id, "COMPLETED",
        draft={"summary": f"Zielrepo {target.name} read-only beobachtet "
                          f"(HEAD {git_info['head'][:12]})."},
        git_info_fn=ro.as_git_info_fn(),
    )

    after = _snapshot(target)
    result_path = out / "results" / task_id / result["run_id"] / "result.yaml"

    checks = {
        "head_unchanged": before["head"] == after["head"],
        "worktree_unchanged": before["status"] == after["status"],
        "result_written_in_out": result_path.is_file() and out in result_path.parents,
        "result_head_matches_target": result["head"] == after["head"],
        "result_provenance_is_target": result["repository"] == target.name,
    }
    if expected_head is not None:
        checks["head_matches_expected"] = before["head"].startswith(expected_head)
    return {
        "target": target, "out": out, "before": before, "after": after,
        "git_info": git_info, "result": result, "result_path": result_path,
        "checks": checks, "passed": all(checks.values()),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="BRIDGE-012 Read-only-Integrationstest (Zielrepo bleibt unverändert)")
    parser.add_argument("--target", default=str(_REPO_ROOT),
                        help="zu beobachtendes Git-Repo (Default: ACB-Repo)")
    parser.add_argument("--out", default=None,
                        help="separater Store-root (Default: neues Temp-Verzeichnis)")
    parser.add_argument("--schema-dir", default=str(_REPO_ROOT / "schemas"))
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--project-id", default="agent-control-bridge",
                        help="project_id des synthetischen Profils/Auftrags (Default: agent-control-bridge)")
    parser.add_argument("--task-prefix", default="BRIDGE",
                        help="task_prefix des synthetischen Profils (Default: BRIDGE)")
    parser.add_argument("--expected-branch", default=None,
                        help="nur informativ, kein Abbruch bei fehlendem Wert")
    parser.add_argument("--expected-head", default=None,
                        help="Pre-Flight-Check: bricht ab, wenn der tatsaechliche HEAD "
                             "nicht mit diesem Wert beginnt (kurze oder lange SHA)")
    args = parser.parse_args(argv)

    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="acb-int-out-"))

    try:
        report = run(Path(args.target), out, Path(args.schema_dir), args.task_id,
                     project_id=args.project_id, task_prefix=args.task_prefix,
                     expected_branch=args.expected_branch, expected_head=args.expected_head)
    except Exception as exc:  # fail-closed
        print(f"FAIL: {exc}")
        return 1

    print(f"Zielrepo:      {report['target']}")
    print(f"Store-root:    {report['out']}")
    print(f"HEAD vorher:   {report['before']['head']}")
    print(f"HEAD nachher:  {report['after']['head']}")
    print(f"Branch:        {report['git_info']['branch']}")
    if args.expected_branch:
        print(f"Branch (erwartet): {args.expected_branch}")
    print(f"result.yaml:   {report['result_path']}")
    print("Pruefungen:")
    for name, ok in report["checks"].items():
        print(f"  [{'OK' if ok else 'XX'}] {name}")

    if report["passed"]:
        print("PASS: Zielrepo unveraendert, Ergebnis valide.")
        return 0
    print("FAIL: mindestens eine Pruefung fehlgeschlagen.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
