# BRIDGE-0052 - CLI: task brief (tokenarmer Kurzauftrag)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0052 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - Reine Leseausgabe, kleines CLI-Kommando. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0051 |
| Gate | G1 |
| stop_conditions | SCOPE_VIOLATION |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
`bridge task brief <id>`: max. 15 Zeilen Pflichtkontext (Klasse A). Rein lesend.

## Scope
src/bridge/cli.py, tests/test_cli.py.

## Schritte
1. Ausgabe: id, status, task_type, model, reasoning_level, expected_head, allowed_paths, forbidden_actions, stop_conditions, erste 5 acceptance_criteria, Pfad des Work-Packages.
2. Fehlende Felder als `-`. Unbekannte ID -> Exit 1.
3. Kein Schreibzugriff.

## Tests
`python -m unittest tests.test_cli`.

## Akzeptanzkriterien
- [ ] Kommando vorhanden, max. 15 Zeilen
- [ ] Unbekannte ID Exit 1 (Test)
- [ ] Alter Auftrag ohne neue Felder funktioniert (Test)
