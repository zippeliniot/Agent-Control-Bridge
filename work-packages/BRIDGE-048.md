# BRIDGE-0048 - Task-Schema: task_type, allowed_paths, forbidden_actions, stop_conditions

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0048 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - Additive optionale Felder nach Muster. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0047 |
| Gate | G1 |
| stop_conditions | SCOPE_VIOLATION |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Vier optionale Felder in task.schema.yaml. Kein CLI-Umbau.

## Scope
schemas/task.schema.yaml, tests/test_store.py.

## Schritte
1. `task_type` enum [T0..T5], default null.
2. `allowed_paths`, `forbidden_actions`: array of string, default [].
3. `stop_conditions`: array, Enum [IDENTITY_MISMATCH, HEAD_MISMATCH, DIRTY_WORKTREE, CONCEPT_CONFLICT, SCOPE_VIOLATION], default [].
4. Bestehende task.yaml bleiben gueltig (Regressionstest).

## Tests
`python -m unittest tests.test_store`.

## Akzeptanzkriterien
- [ ] 4 Felder additiv im Schema
- [ ] Unbekannter stop_condition-Wert abgelehnt (Test)
- [ ] Alte task.yaml weiter gueltig (Test)
