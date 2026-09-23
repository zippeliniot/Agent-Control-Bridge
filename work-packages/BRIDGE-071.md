# BRIDGE-0071 - Steuerchat-Vorlage automatisch aus project.yaml fuellen (executor-bewusst)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0071 |
| project_id | agent-control-bridge |
| Typ / Klasse | DOCS |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - Vorlage plus kleines Fuell-Skript. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | keine |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0071` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung = STOPP.

## Auftrag
**Ziel:** Der generische Steuerchat-Prompt soll automatisch aus einem `projects/<id>/project.yaml` gefuellt werden, OHNE manuelles Abtippen, UND je nach `executor`-Feld (claude-code ODER codex) den passenden Hinweistext einsetzen. Grund: Bei Claude Code muss vor dem `/acb-auftrag`-Skill fuer Nicht-BRIDGE-IDs gewarnt werden (siehe WETTER-0001-Vorfall: Skill griff faelschlich eine alte BRIDGE-ID auf). Bei Codex (laeuft nativ in PowerShell, keine Skills/Slash-Befehle) ist dieser Hinweis falsch und muss durch einen neutralen Platzhaltertext ersetzt werden - es gibt noch keine dokumentierte Codex-Erfahrung, das ehrlich als offenen Punkt kennzeichnen, nicht erfinden.
**Scope:** Neu: docs/ACB-STEUERCHAT-VORLAGE.md (Template mit Platzhaltern, inkl. Executor-Block), scripts/steuerchat-vorlage.py, tests/test_steuerchat_vorlage.py. Sonst nichts.
1. docs/ACB-STEUERCHAT-VORLAGE.md: Klartext-Template mit Platzhaltern (doppelte geschweifte Klammern): {{PROJEKTNAME}}, {{GITHUB_ORG}}, {{GITHUB_REPO}}, {{PROJEKT_ID}}, {{PRAEFIX}}, {{EXECUTOR_HINWEIS}}. Rollentext und START-Ablauf inhaltlich wie fuer wetter-app im Steuerchat erstellt (siehe docs/handover/WETTER-STEUERCHAT-UEBERGABE.md als Vorbild), aber der Executor-spezifische Absatz (bisher: "NIE den /acb-auftrag-Slash-Befehl ... woertlich auf die WP-Datei verweisen") wird durch {{EXECUTOR_HINWEIS}} ersetzt.
2. scripts/steuerchat-vorlage.py: liest projects/<id>/project.yaml (--project-id Pflichtargument). Entnimmt project_id, task_prefix, github_repo, executor. PROJEKTNAME wie gehabt aus description ableiten oder project_id. EXECUTOR_HINWEIS: bei executor == claude-code der bekannte Text (Skill-Vermeidung, woertlich auf WP-Datei verweisen, Beispiel WETTER-0001 nennen); bei executor == codex ein kurzer, EHRLICH als vorlaeufig gekennzeichneter Platzhaltertext ("Codex laeuft nativ in PowerShell, keine Skills bekannt - noch keine dokumentierte Erfahrung mit diesem Profil, Steuerchat soll beim ersten Auftrag besonders genau pruefen und Abweichungen hier nachtragen"); bei jedem anderen/fehlenden Wert: Fehlermeldung auf stderr, Exit-Code != 0 (fail-closed, nicht raten). Fehlt project_id/task_prefix/github_repo im Profil: ebenfalls Fehler statt Raten. Ausgabe auf stdout (kein Datei-Write).
3. Tests mit Fake-project.yaml (temp dir): (a) executor claude-code fuellt korrekt inkl. Skill-Hinweis, (b) executor codex fuellt korrekt inkl. Codex-Platzhaltertext, (c) fehlendes Pflichtfeld -> Fehler, (d) unbekannter executor-Wert -> Fehler, (e) unbekannte project-id -> Fehler.
**Tests:** `python -m unittest tests.test_steuerchat_vorlage`, danach volle Suite EINMAL.
- [ ] Vorlage mit den 6 Platzhaltern (inkl. EXECUTOR_HINWEIS) angelegt
- [ ] Skript fuellt korrekt fuer claude-code UND codex (beide per Test belegt)
- [ ] Fehlendes Profilfeld / unbekannter executor fuehrt zu Fehler, nicht zu Raten (Test)
- [ ] Volle Suite gruen