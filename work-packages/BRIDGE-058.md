# BRIDGE-0058 - Atomare Store-Writes

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0058 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Schreibpfade der Kernmechanik, Fehlerfall muss getestet werden. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | BRIDGE-0057 |
| Gate | G2 |
| stop_conditions | SCOPE_VIOLATION |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Schreiben ueber Temp-Datei im selben Ordner + `os.replace`.

## Scope
src/bridge/store.py, src/bridge/heartbeat.py, tests/test_store.py.

## Schritte
1. Helper `_atomic_write(path, text)` (Temp im Zielordner, flush+fsync, `os.replace`).
2. Einsetzen bei create_task, save_task, write_result, write_draft, Heartbeat.
3. Test: Fehler zwischen Schreiben und Replace laesst Originaldatei unveraendert.

## Tests
`python -m unittest tests.test_store tests.test_watcher`, dann volle Suite EINMAL.

## Akzeptanzkriterien
- [ ] Alle Schreibpfade atomar
- [ ] Fehlerfall-Test gruen
- [ ] Kein Temp-Rest nach Fehler (Test)
