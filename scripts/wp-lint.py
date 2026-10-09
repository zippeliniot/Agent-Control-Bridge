#!/usr/bin/env python
"""BRIDGE-0102 - WP-Kopf + Staging-YAML vor der Uebergabe pruefen (fail-closed).

Prueft, dass
  1. der WP-Kopf eine Tabellenzeile ``Modell / Denkstufe`` mit nichtleerem
     Modellnamen und gueltiger Denkstufe (LOW/MEDIUM/HIGH) enthaelt,
  2. die Staging-YAML gegen das Task-Schema validiert (``Store.validate``,
     keine eigene Feldliste) und ``model``/``reasoning_level`` nichtleer sind,
  3. Modell + Denkstufe aus WP und YAML exakt uebereinstimmen,
  4. die ``bridge_task_id`` der YAML in der WP-Ueberschrift vorkommt.

Exit 0 nur, wenn alles zutrifft; sonst alle Verstoesse auf stderr, Exit 1.

Aufruf:
    .venv/Scripts/python.exe scripts/wp-lint.py \
        --wp work-packages/BRIDGE-xxx.md --staging tasks/incoming/BRIDGE-0xxx.yaml
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


def lint(wp: Path, staging: Path) -> list[str]:
    heading, _no, wp_model, wp_level, errors = parse_wp(wp)

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
    return errors


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--wp", required=True)
    ap.add_argument("--staging", required=True)
    args = ap.parse_args(argv)
    errors = lint(Path(args.wp), Path(args.staging))
    if errors:
        for e in errors:
            print(f"FEHLER: {e}", file=sys.stderr)
        return 1
    print("OK: WP-Kopf und Staging-YAML konsistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
