# BRIDGE-0061 - Version und CAS (Stufe B)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0061 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Konflikterkennung, Stufe B - nur mit Freigabe. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | BRIDGE-0060 |
| Gate | G3 |
| stop_conditions | CONCEPT_CONFLICT |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
`task_version` + optionales `expected_version` in set_status/save_task.

## Scope
schemas/task.schema.yaml, src/bridge/store.py, tests/test_store.py.

## Schritte
1. VORAB: ausdrueckliche Stufe-B-Freigabe von April im Chat (G3), sonst STOPP.
2. Schema: `task_version` int, default 1. Erhoeht sich bei jedem Speichern.
3. `expected_version` optional; Abweichung -> StoreError `VERSION_CONFLICT`, nichts geschrieben.
4. Ohne expected_version: Verhalten unveraendert.

## Tests
`python -m unittest tests.test_store`, dann volle Suite EINMAL.

## Akzeptanzkriterien
- [ ] Freigabe G3 dokumentiert
- [ ] CAS-Konflikt lehnt ab (Test)
- [ ] Altes Verhalten unveraendert (Test)
