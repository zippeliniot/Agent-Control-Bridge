#!/usr/bin/env python
"""BRIDGE-0071 - Steuerchat-Vorlage aus projects/<id>/project.yaml fuellen.

Liest die Vorlage docs/ACB-STEUERCHAT-VORLAGE.md und ersetzt deren
Platzhalter mit Werten aus dem Projektprofil (--project-id Pflichtargument).
executor-abhaengig wird ein passender EXECUTOR_HINWEIS eingesetzt (bekannter
Text fuer claude-code, ehrlich als vorlaeufig gekennzeichneter Platzhaltertext
fuer codex). Fail-closed: fehlt ein Pflichtfeld im Profil oder ist executor
weder claude-code noch codex, wird NICHT geraten, sondern mit Fehlermeldung
auf stderr und Exit-Code != 0 abgebrochen.

Aufruf:
    .venv/Scripts/python.exe scripts/steuerchat-vorlage.py --project-id wetter-app

Ausgabe: gefuellte Vorlage auf stdout (kein Datei-Write).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]

EXECUTOR_HINWEIS_CLAUDE_CODE = """\
Diese Ausführungsinstanz ist Claude Code mit Slash-Befehl `/acb-auftrag`
(`.claude/commands/acb-auftrag.md`). Der Skill greift für Nicht-BRIDGE-IDs
fälschlich eine alte BRIDGE-ID auf (siehe WETTER-0001-Vorfall) — deshalb bei
Aufträgen mit anderem Präfix NIE den Slash-Befehl oder das Wort
„Auftrag"/„acb-auftrag" in der ersten Anweisung verwenden, sondern wörtlich
auf die Work-Package-Datei verweisen."""

EXECUTOR_HINWEIS_CODEX = """\
Diese Ausführungsinstanz ist Codex, läuft nativ in PowerShell und kennt keine
Skills/Slash-Befehle. Vorläufiger Hinweis (noch keine dokumentierte Erfahrung
mit diesem Profil): der Steuerchat soll beim ersten Auftrag besonders genau
prüfen und Abweichungen hier nachtragen."""

REQUIRED_FIELDS = ("project_id", "task_prefix", "github_repo")


def _project_name(profile: dict) -> str:
    description = profile.get("description")
    if description:
        return str(description)
    return str(profile["project_id"])


def _executor_hinweis(executor: str) -> str:
    if executor == "claude-code":
        return EXECUTOR_HINWEIS_CLAUDE_CODE
    if executor == "codex":
        return EXECUTOR_HINWEIS_CODEX
    raise ValueError(
        f"Unbekannter executor-Wert: {executor!r} (erwartet: claude-code oder codex)")


def build(project_id: str, repo_root: Path = _REPO_ROOT) -> str:
    profile_path = repo_root / "projects" / project_id / "project.yaml"
    if not profile_path.is_file():
        raise ValueError(f"Kein Projektprofil gefunden: {profile_path}")

    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}

    missing = [field for field in REQUIRED_FIELDS if not profile.get(field)]
    if missing:
        raise ValueError(f"Profilfeld(er) fehlen in {profile_path}: {', '.join(missing)}")

    executor = profile.get("executor")
    if not executor:
        raise ValueError(f"Profilfeld fehlt in {profile_path}: executor")

    github_repo = str(profile["github_repo"])
    if "/" not in github_repo:
        raise ValueError(
            f"github_repo muss als '<org>/<repo>' vorliegen, ist: {github_repo!r}")
    github_org, _, github_repo_name = github_repo.partition("/")

    executor_hinweis = _executor_hinweis(str(executor))

    template_path = repo_root / "docs" / "ACB-STEUERCHAT-VORLAGE.md"
    full_template = template_path.read_text(encoding="utf-8")
    # Der Kopfbereich vor der ersten "---"-Trennlinie ist Meta-Dokumentation
    # der Vorlagendatei selbst (nennt die Platzhalter literal) und ist NICHT
    # Teil des zu fuellenden Steuerchat-Texts.
    _, _, template = full_template.partition("\n---\n")
    if not template:
        raise ValueError(f"Vorlage ohne '---'-Trennlinie: {template_path}")

    replacements = {
        "{{PROJEKTNAME}}": _project_name(profile),
        "{{GITHUB_ORG}}": github_org,
        "{{GITHUB_REPO}}": github_repo_name,
        "{{PROJEKT_ID}}": str(profile["project_id"]),
        "{{PRAEFIX}}": str(profile["task_prefix"]),
        "{{EXECUTOR_HINWEIS}}": executor_hinweis,
    }
    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)
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
