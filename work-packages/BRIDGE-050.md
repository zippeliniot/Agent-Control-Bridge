# BRIDGE-0050 - Fehlercodes als SSOT

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0050 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - Kleine SSOT-Datei + Loader. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0049 |
| Gate | G1 |
| stop_conditions | SCOPE_VIOLATION |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
schemas/error-codes.yaml + Mini-Loader. Codes mappen auf Zustand BLOCKED (kein neuer Zustand).

## Scope
schemas/error-codes.yaml (neu), src/bridge/errorcodes.py (neu), tests/test_errorcodes.py (neu).

## Schritte
1. error-codes.yaml: 5 Codes aus BRIDGE-0048, je `description`, `state: BLOCKED`.
2. errorcodes.py: `load_error_codes(schema_dir)`, `is_known(code)`.
3. Test: Schluessel == Enum `stop_conditions` in task.schema.yaml (SSOT-Gleichheit).

## Tests
`python -m unittest tests.test_errorcodes`, dann volle Suite EINMAL.

## Akzeptanzkriterien
- [ ] error-codes.yaml + Loader vorhanden
- [ ] SSOT-Gleichheitstest gruen
- [ ] state-model.yaml unveraendert
