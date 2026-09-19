# BRIDGE-0067 - Nachbesserung draft write/import (Einschub nach 0053, vor 0055)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0067 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel (T2) / BUGFIX |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - sicherheitsrelevante Aenderung an draft write/import |
| depends_on | BRIDGE-0053 |
| Gate | G2 (muss vor BRIDGE-0055 laufen) |
| stop_conditions | HEAD_MISMATCH, SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0067`. Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` Par. 3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung = STOPP.
> Scope gesamt: src/bridge/draft.py, src/bridge/importer.py, tests/test_draft.py. Nichts sonst.

**Teile strikt nacheinander (A, B, C). Pro Teil: Haken setzen, Commit, Push.**

### Teil A - draft write ohne vorherigen run start
**Ziel:** Im Draft-Modus darf der Executor nicht `run start` ausfuehren (schreibt tasks/results/audit). `write_draft` muss trotzdem laufen.
1. Lauf-ID bestimmen wie `plan_import`: Status RUNNING -> `runner.current_run_id`; Status in `runner._START_FROM` -> `store.next_run_id`; sonst DraftError. Kein `run start` noetig.
2. Test: Auftrag direkt nach `task create` (WAITING_FOR_HANDOFF_TO_EXECUTOR) -> `draft write` liefert RUN-01; danach `draft import` klappt (Start + Finish).
- [ ] draft write ohne run start moeglich (Test)
- [ ] Status RUNNING nutzt weiter den laufenden Lauf (Test)

### Teil B - Import uebernimmt tests und findings
**Ziel:** result.yaml darf keine Draft-Information verlieren.
1. `importer.build_result`: `tests` und `findings` aus `draft` durchreichen (Result-Schema kennt beide optional).
2. `draft.import_draft`: `draft={"tests":..., "findings":...}` an `runner.finish` uebergeben. Bei `error_code` im Draft: summary mit Praefix `[<CODE>] `.
3. Test: BLOCKED-Draft (SCOPE_VIOLATION, 3/1/0) -> result.yaml enthaelt tests, findings und den Code im summary.
- [ ] tests + findings im result.yaml (Test)
- [ ] Fehlercode im summary (Test)

### Teil C - Import prueft Draft selbst nach
**Ziel:** Das Board vertraut dem Executor nicht blind.
1. `plan_import`: `draft.base_head` muss zu `task.git.expected_head` passen (Praefixvergleich kurz/lang), sonst DraftError Code HEAD_MISMATCH.
2. `plan_import`: `scope_violations(task, draft.changed_files)` nicht leer UND Draft-Status nicht BLOCKED -> DraftError Code SCOPE_VIOLATION.
3. Tests: fremder base_head abgelehnt; Draft mit Dateien ausserhalb allowed_paths und Status COMPLETED abgelehnt; regulaerer Draft weiter importierbar.
**Tests gesamt:** `python -m unittest tests.test_draft`, dann volle Suite EINMAL.
- [ ] fremder base_head abgelehnt (Test)
- [ ] Scope-Verstoss mit Status COMPLETED abgelehnt (Test)
- [ ] regulaerer Draft importierbar (Test)
