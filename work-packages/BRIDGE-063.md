# BRIDGE-0063 - B7 Ressourcenregel + Parallelitaetstests

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0063 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel / FEATURE |
| Teile (alte Nummern) | 0063, 0064 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Ressourcenregel + Parallel-/Ausfalltests, ein Bereich. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | BRIDGE-0061 |
| Gate | G4 |
| stop_conditions | CONCEPT_CONFLICT, SCOPE_VIOLATION |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0063` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

**Teile strikt nacheinander (A, B, ...). Pro Teil: Haken setzen, Commit, Push. Scheitert ein Teil: STOPP (BLOCKED), spaetere Teile nicht beginnen.**

### Teil A (alt 0063) - Ressourcenregel (repository, remote, branch)
**Ziel:** Genau eine Regel: nie zwei aktive Claims auf demselben Schluessel.
**Scope:** docs/concepts/ENTSCHEIDUNG-RESSOURCENREGEL.md (neu, max. 30 Zeilen), src/bridge/claim.py, schemas/error-codes.yaml + task.schema.yaml (Code `RESOURCE_CONFLICT`), tests/test_claim.py.
1. Schluessel = (repository, `git remote get-url origin`, branch).
2. `claim` lehnt ab, wenn anderer aktiver Claim denselben Schluessel hat -> BLOCKED-Grund `RESOURCE_CONFLICT`.
3. Code in error-codes.yaml UND task.schema.yaml ergaenzen (SSOT-Test aus 0050 bleibt gruen).
**Tests:** `python -m unittest tests.test_claim tests.test_errorcodes`, dann volle Suite EINMAL.
- [x] Regeldatei vorhanden
- [x] Zweiter Claim auf gleichen Schluessel abgelehnt (Test)
- [x] SSOT-Test weiter gruen

### Teil B (alt 0064) - Parallelitaets- und Ausfalltests
**Ziel:** Reproduzierbare Tests fuer Lock, Claim und Ausfall. Kein Produktcode.
**Scope:** tests/test_parallel.py (neu).
1. Zwei Subprozesse: gleicher Lock, gleicher Claim-Schluessel -> genau einer gewinnt.
2. Prozess bricht mitten im Schreiben ab -> Datei intakt, stale Lock/Claim erkannt.
3. Ohne Sleeps mit langen Wartezeiten (kurze Timeouts, Events).
**Tests:** `python -m unittest tests.test_parallel` 5x, dann volle Suite EINMAL.
- [x] Parallel-Test 5/5 gruen
- [x] Ausfalltest gruen
- [x] Keine Produktcode-Aenderung
