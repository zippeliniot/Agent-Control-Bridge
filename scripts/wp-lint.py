#!/usr/bin/env python
"""BRIDGE-0102 - WP-Kopf + Staging-YAML vor der Uebergabe pruefen (fail-closed).

Prueft, dass
  1. der WP-Kopf eine Tabellenzeile ``Modell / Denkstufe`` mit nichtleerem
     Modellnamen und gueltiger Denkstufe (LOW/MEDIUM/HIGH) enthaelt,
  2. die Staging-YAML gegen das Task-Schema validiert (``Store.validate``,
     keine eigene Feldliste) und ``model``/``reasoning_level`` nichtleer sind,
  3. Modell + Denkstufe aus WP und YAML exakt uebereinstimmen,
  4. die ``bridge_task_id`` der YAML in der WP-Ueberschrift vorkommt,
  5. jede ``ISSUE-NNNN``-Referenz im WP-Text als Datei
     ``open-issues/<project_id>/<project_id>-ISSUE-NNNN.yaml`` existiert,
  6. (nur Warnung) jede ``BRIDGE-NNNN``-Referenz, die in derselben Zeile mit
     ``ARCHIVED``/``COMPLETED`` steht, ein ``tasks/<id>/task.yaml`` hat
     (ISSUE-0006-Muster),
  7. das WP eine ``## Akzeptanzkriterien``-Sektion und in der Kopftabelle eine
     ``Scope``-Zeile mit nichtleerem Wert hat.

Exit 0 nur, wenn alles zutrifft (Warnungen aus 6 aendern den Exit nicht);
sonst alle Verstoesse auf stderr, Exit 1.

Aufruf:
    .venv/Scripts/python.exe scripts/wp-lint.py \
        --wp work-packages/BRIDGE-xxx.md --staging tasks/incoming/BRIDGE-0xxx.yaml
        [--root <Repo-Wurzel fuer open-issues/ und tasks/>]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

from bridge.store import Store, StoreError  # noqa: E402

LEVELS = ("LOW", "MEDIUM", "HIGH")
_ROW = re.compile(r"^\|\s*\**\s*Modell\s*/\s*Denkstufe\s*\**\s*\|(.*)\|\s*$", re.I)
_SCOPE = re.compile(r"^\|\s*\**\s*Scope\s*\**\s*\|(.*)\|\s*$", re.I)
_ISSUE = re.compile(r"ISSUE-(\d{4})")
_BRIDGE = re.compile(r"BRIDGE-(\d{3,4})")
_DONE = re.compile(r"\b(ARCHIVED|COMPLETED)\b")
_VALUE = re.compile(r"^(?P<model>.+?)\s*/\s*(?P<level>[A-Za-z]+)\b")


def parse_wp(path: Path) -> tuple[str, int | None, str | None, str | None, list[str]]:
    """Gibt (Ueberschrift, Zeile, Modell, Denkstufe, Fehler) zurueck."""
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return "", None, None, None, [f"{path}: nicht lesbar ({exc})"]
    heading = next((l for l in lines if l.startswith("# ")), "")
    if not heading:
        errors.append(f"{path}: keine Ueberschrift ('# ...') gefunden")
    for no, line in enumerate(lines, 1):
        m = _ROW.match(line.strip())
        if not m:
            continue
        cell = m.group(1).strip().replace("**", "").strip()
        v = _VALUE.match(cell)
        if not v or not v.group("model").strip():
            errors.append(f"{path}:{no}: Modell/Denkstufe-Zeile ohne "
                          f"'<Modell> / <Denkstufe>'")
            return heading, no, None, None, errors
        level = v.group("level").upper()
        if level not in LEVELS:
            errors.append(f"{path}:{no}: ungueltige Denkstufe "
                          f"'{v.group('level')}' (erlaubt: {', '.join(LEVELS)})")
            return heading, no, None, None, errors
        return heading, no, v.group("model").strip(), level, errors
    errors.append(f"{path}: Tabellenzeile 'Modell / Denkstufe' fehlt im WP-Kopf")
    return heading, None, None, None, errors


def check_structure(wp: Path) -> list[str]:
    """Pruefung 7: Akzeptanzkriterien-Sektion + nichtleere Scope-Zeile."""
    try:
        lines = wp.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []  # Lesefehler meldet parse_wp bereits
    errors: list[str] = []
    if not any(l.strip() == "## Akzeptanzkriterien" for l in lines):
        errors.append(f"{wp}: Ueberschrift '## Akzeptanzkriterien' fehlt")
    for no, line in enumerate(lines, 1):
        m = _SCOPE.match(line.strip())
        if m:
            if not m.group(1).replace("**", "").strip():
                errors.append(f"{wp}:{no}: Scope-Zeile in der Kopftabelle ist leer")
            return errors
    errors.append(f"{wp}: Tabellenzeile 'Scope' fehlt im WP-Kopf")
    return errors


def check_issue_refs(wp: Path, project_id: str, root: Path) -> list[str]:
    """Pruefung 5: ISSUE-NNNN muss als Datei unter open-issues/ existieren."""
    try:
        lines = wp.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    errors, seen = [], set()
    for no, line in enumerate(lines, 1):
        for num in _ISSUE.findall(line):
            if num in seen:
                continue
            seen.add(num)
            f = root / "open-issues" / project_id / f"{project_id}-ISSUE-{num}.yaml"
            if not f.is_file():
                errors.append(f"{wp}:{no}: ISSUE-{num} nicht aufloesbar "
                              f"(Datei fehlt: open-issues/{project_id}/"
                              f"{project_id}-ISSUE-{num}.yaml)")
    return errors


def check_closed_refs(wp: Path, root: Path) -> list[str]:
    """Pruefung 6 (Warnung): BRIDGE-Referenz + ARCHIVED/COMPLETED ohne task.yaml."""
    try:
        lines = wp.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    warnings, seen = [], set()
    for no, line in enumerate(lines, 1):
        if not _DONE.search(line):
            continue
        for num in _BRIDGE.findall(line):
            tid = f"BRIDGE-{int(num):04d}"
            if tid in seen:
                continue
            seen.add(tid)
            if not (root / "tasks" / tid / "task.yaml").is_file():
                warnings.append(f"{wp}:{no}: {tid} als abgeschlossen zitiert, "
                                f"aber tasks/{tid}/task.yaml fehlt")
    return warnings


def lint(wp: Path, staging: Path, root: Path | None = None,
         warnings: list[str] | None = None) -> list[str]:
    root = root or _REPO_ROOT
    heading, _no, wp_model, wp_level, errors = parse_wp(wp)
    errors += check_structure(wp)
    if warnings is not None:
        warnings += check_closed_refs(wp, root)

    doc = None
    try:
        doc = yaml.safe_load(staging.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{staging}: nicht lesbar/kein gueltiges YAML ({exc})")
    if doc is not None and not isinstance(doc, dict):
        errors.append(f"{staging}: kein Objekt")
        doc = None
    if doc is None:
        return errors

    try:
        Store(root=_REPO_ROOT, schema_dir=_REPO_ROOT / "schemas").validate(doc)
    except StoreError as exc:
        errors.append(f"{staging}: Schema-Verstoss: {exc}")

    y_model, y_level = doc.get("model"), doc.get("reasoning_level")
    if not (isinstance(y_model, str) and y_model.strip()):
        errors.append(f"{staging}: 'model' fehlt oder ist leer")
    if not (isinstance(y_level, str) and y_level.strip()):
        errors.append(f"{staging}: 'reasoning_level' fehlt oder ist leer")
    if wp_model is not None and isinstance(y_model, str) and y_model.strip() \
            and wp_model != y_model:
        errors.append(f"Modell weicht ab: WP '{wp_model}' != YAML '{y_model}'")
    if wp_level is not None and isinstance(y_level, str) and y_level.strip() \
            and wp_level != y_level:
        errors.append(f"Denkstufe weicht ab: WP '{wp_level}' != YAML '{y_level}'")

    task_id = doc.get("bridge_task_id")
    if not task_id:
        errors.append(f"{staging}: 'bridge_task_id' fehlt")
    elif heading and task_id not in heading:
        errors.append(f"{wp}: bridge_task_id '{task_id}' der YAML kommt in der "
                      f"WP-Ueberschrift nicht vor ('{heading}')")
    project_id = doc.get("project_id")
    if isinstance(project_id, str) and project_id:
        errors += check_issue_refs(wp, project_id, root)
    return errors


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--wp", required=True)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--root", default=None)
    args = ap.parse_args(argv)
    warnings: list[str] = []
    errors = lint(Path(args.wp), Path(args.staging),
                  Path(args.root) if args.root else None, warnings)
    for w in warnings:
        print(f"WARNUNG: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"FEHLER: {e}", file=sys.stderr)
        return 1
    print("OK: WP-Kopf und Staging-YAML konsistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
