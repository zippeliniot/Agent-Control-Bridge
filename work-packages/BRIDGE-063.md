# BRIDGE-0063 - Ressourcenregel (repository, remote, branch)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0063 |
| project_id | agent-control-bridge |
| Typ / Klasse | T1 / ARCHITECTURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Opus 5 / MEDIUM** - Regel + kleine Umsetzung, betrifft Multi-Agenten-Sicherheit. |
| Modellwechsel zum Vorgaenger | JA |
| depends_on | BRIDGE-0062 |
| Gate | G4 |
| stop_conditions | CONCEPT_CONFLICT |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Genau eine Regel: nie zwei aktive Claims auf demselben Schluessel.

## Scope
docs/concepts/ENTSCHEIDUNG-RESSOURCENREGEL.md (neu, max. 30 Zeilen), src/bridge/claim.py, schemas/error-codes.yaml + task.schema.yaml (Code `RESOURCE_CONFLICT`), tests/test_claim.py.

## Schritte
1. Schluessel = (repository, `git remote get-url origin`, branch).
2. `claim` lehnt ab, wenn anderer aktiver Claim denselben Schluessel hat -> BLOCKED-Grund `RESOURCE_CONFLICT`.
3. Code in error-codes.yaml UND task.schema.yaml ergaenzen (SSOT-Test aus 0050 bleibt gruen).

## Tests
`python -m unittest tests.test_claim tests.test_errorcodes`, dann volle Suite EINMAL.

## Akzeptanzkriterien
- [ ] Regeldatei vorhanden
- [ ] Zweiter Claim auf gleichen Schluessel abgelehnt (Test)
- [ ] SSOT-Test weiter gruen
