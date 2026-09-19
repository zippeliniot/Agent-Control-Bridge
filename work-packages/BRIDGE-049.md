# BRIDGE-0049 - Draft-Schema draft-a-1

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0049 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Neuer Vertrag (draft-a-1), Konsistenz zum Result-Schema. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0048 |
| Gate | G1 |
| stop_conditions | SCOPE_VIOLATION |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Neues Schema fuer Executor-Drafts + optionale Felder tests/findings im Result-Schema.

## Scope
schemas/draft.schema.yaml (neu), schemas/result.schema.yaml (additiv), schemas/README.md (1 Zeile), tests/test_store.py.

## Schritte
1. draft.schema.yaml: kind `bridge_draft`, `draft_version` const `draft-a-1`, bridge_task_id, run_id, status (COMPLETED|BLOCKED|FAILED|INTERRUPTED), summary, base_head, head_after, branch, repository, changed_files, tests{passed,failed,blocked}, findings[{id,severity,text}], next_action, error_code (optional). additionalProperties false.
2. result.schema.yaml: optional `tests` und `findings` (gleiche Form). Additiv.
3. Tests: gueltiger Draft, fehlendes Pflichtfeld, unbekanntes Feld, falsche draft_version.

## Tests
`python -m unittest tests.test_store`.

## Akzeptanzkriterien
- [ ] draft.schema.yaml gueltig (Draft 2020-12)
- [ ] result.schema additiv erweitert
- [ ] 4 Schema-Tests gruen
- [ ] Alte result.yaml weiter gueltig
