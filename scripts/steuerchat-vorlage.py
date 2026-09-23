#!/usr/bin/env python
"""BRIDGE-0072 - Generischen Startprompt v2 mit der Projekt-ID fuellen.

Liest docs/ACB-STEUERCHAT-START-GENERISCH-v2.md, prueft die uebergebene
--project-id gegen projects/<id>/project.yaml (Pflichtfelder, ID-Konsistenz)
und ersetzt {{PROJEKT_ID}} im Text ab der ersten '---'-Trennlinie (der
Kopfbereich davor ist Meta-Dokumentation der Vorlage selbst und nicht Teil
des Steuerchat-Texts). Fail-closed: fehlt ein Pflichtfeld, weicht die
project_id im Profil vom Argument ab, fehlt die Trennlinie oder bleibt
danach ein unaufgeloester Platzhalter stehen, wird NICHT geraten, sondern
mit Fehlermeldung auf stderr und Exit-Code != 0 abgebrochen.

Aufruf:
    .venv/Scripts/python.exe scripts/steuerchat-vorlage.py --project-id wetter-app

Ausgabe: gefuellter Text ab der Trennlinie auf stdout (kein Datei-Write).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FIELDS = ("task_prefix", "github_repo", "repository")


def _existing_project_ids(repo_root: Path) -> list[str]:
    projects_dir = repo_root / "projects"
    if not projects_dir.is_dir():
        return []
    return sorted(
        p.name for p in projects_dir.iterdir()
        if p.is_dir() and (p / "project.yaml").is_file()
    )


def build(project_id: str, repo_root: Path = _REPO_ROOT) -> str:
    profile_path = repo_root / "projects" / project_id / "project.yaml"
    if not profile_path.is_file():
        known = ", ".join(_existing_project_ids(repo_root)) or "(keine gefunden)"
        raise ValueError(
            f"Kein Projektprofil gefunden: {profile_path}. "
            f"Vorhandene Verzeichnisse unter projects/: {known}"
        )

    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}

    profile_project_id = profile.get("project_id")
    if profile_project_id != project_id:
        raise ValueError(
            f"project_id im Profil ({profile_project_id!r}) weicht vom "
            f"Argument ({project_id!r}) ab: {profile_path}"
        )

    missing = [field for field in REQUIRED_FIELDS if not profile.get(field)]
    if missing:
        raise ValueError(f"Profilfeld(er) fehlen in {profile_path}: {', '.join(missing)}")

    github_repo = str(profile["github_repo"])
    if "/" not in github_repo:
        raise ValueError(
            f"github_repo muss als '<org>/<repo>' vorliegen, ist: {github_repo!r}")

    template_path = repo_root / "docs" / "ACB-STEUERCHAT-START-GENERISCH-v2.md"
    full_template = template_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    # Der Kopfbereich vor der ersten "---"-Trennlinie ist Meta-Dokumentation
    # der Vorlagendatei selbst und NICHT Teil des zu fuellenden Steuerchat-Texts.
    _, sep, template = full_template.partition("\n---\n")
    if not sep:
        raise ValueError(f"Vorlage ohne '---'-Trennlinie: {template_path}")

    result = template.replace("{{PROJEKT_ID}}", project_id)
    if "{{" in result:
        raise ValueError(
            f"Nach dem Ersetzen bleibt ein unaufgeloester Platzhalter stehen: {template_path}"
        )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-id", required=True, help="z. B. wetter-app")
    args = parser.parse_args(argv)

    try:
        output = build(args.project_id)
    except ValueError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1

    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
