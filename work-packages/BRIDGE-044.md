# BRIDGE-0044 - Namensreste beseitigen (Punkt 5)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0044 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / CHORE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - Mechanische Umbenennung, vollstaendig vorgegeben. |
| Modellwechsel zum Vorgaenger | JA |
| depends_on | BRIDGE-0043 |
| Gate | G1 |
| stop_conditions | SCOPE_VIOLATION |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Alten Namen 'Codex Control Bridge'/'CCB'/'codex-control-bridge' in aktiven Dateien ersetzen. 'Codex' als Agent bleibt.

## Scope
requirements.txt, scripts/*, README.md (nur Zeile zu integration_readonly-Default), tests/test_integration_readonly.py (nur falls Default geprueft wird).

## Schritte
1. `git grep -n -i -E 'codex control bridge|codex-control-bridge|CCB' -- requirements.txt scripts README.md tests` - Trefferliste.
2. Ersetzen per Einzel-Edit (kein Volltext-Output). integration_readonly.py: Default `--project-id` -> `agent-control-bridge`, Temp-Prefix `ccb-int-out-` -> `acb-int-out-`.
3. scripts/board-watch.bat: REPO_PATH -> `E:\_DEV\Agent-Control-Bridge\board`, Kommentar: nur DES11 (HAM11 nach Umstellung).
4. Zeilenenden NICHT aendern (.ps1/.bat = CRLF).
5. Historische Dateien NICHT anfassen (work-packages/*, tasks/*, results/*, docs/handover/CCB-*).

## Tests
`python -m unittest tests.test_integration_readonly`, dann volle Suite EINMAL (nur letzte 3 Zeilen ausgeben).

## Akzeptanzkriterien
- [x] Keine Namensreste mehr in requirements.txt, scripts/, README.md
- [x] Default project-id = agent-control-bridge
- [x] board-watch.bat zeigt auf ...\board
- [x] Historische Dateien unveraendert
- [x] Tests gruen
