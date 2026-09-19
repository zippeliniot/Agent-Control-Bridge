# BRIDGE-0047 - Profilfeld push_mode

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0047 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Schema + Loader + Tests, additiv. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0046 |
| Gate | G1 |
| stop_conditions | CONCEPT_CONFLICT |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Optionales Feld `push_mode` (direct|draft, Default direct) im Projektprofil.

## Scope
schemas/project.schema.yaml, src/bridge/profiles.py, tests/test_profiles.py, docs/architecture/ARCHITECTURE.md (1 Absatz).

## Schritte
1. VORAB: docs/concepts/ENTSCHEIDUNG-PUSH-MODELL.md muss `Status: FREIGEGEBEN` tragen, sonst STOPP (CONCEPT_CONFLICT).
2. Schema: `push_mode` enum [direct, draft], default direct. Additiv.
3. profiles.py: `get_push_mode(profile) -> str` (Default `direct`).
4. Alle 8 bestehenden Profile bleiben ohne Aenderung gueltig.

## Tests
`python -m unittest tests.test_profiles`, dann volle Suite EINMAL.

## Akzeptanzkriterien
- [ ] Entscheidung war FREIGEGEBEN
- [ ] push_mode im Schema, Default direct
- [ ] get_push_mode vorhanden
- [ ] Ungueltiger Wert wird abgelehnt (Test)
- [ ] Alle Profile unveraendert gueltig
