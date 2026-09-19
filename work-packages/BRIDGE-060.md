# BRIDGE-0060 - Writer-Lock und sicheres Audit-Append

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0060 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Nebenlaeufigkeit, reentrant, Fehlerfaelle. |
| Modellwechsel zum Vorgaenger | JA |
| depends_on | BRIDGE-0059 |
| Gate | G2 |
| stop_conditions | CONCEPT_CONFLICT |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Dateilock `.acb-writer.lock` fuer alle Store-Schreibpfade + Append nach Entscheidung 0059.

## Scope
src/bridge/lock.py (neu), src/bridge/store.py, .gitignore (1 Zeile), tests/test_lock.py (neu).

## Schritte
1. VORAB: ENTSCHEIDUNG-AUDIT.md `Status: FREIGEGEBEN`, sonst STOPP.
2. `writer_lock(root, timeout)`: exklusives Anlegen (O_EXCL) mit pid+Zeit; reentrant im selben Prozess; alter Lock (>300 s) -> Fehler mit Hinweis, NICHT automatisch brechen.
3. Alle Store-Schreibmethoden nutzen den Lock.
4. Audit-Append laut Entscheidung.

## Tests
`python -m unittest tests.test_lock tests.test_store`, dann volle Suite EINMAL.

## Akzeptanzkriterien
- [ ] Lock schuetzt alle Schreibpfade
- [ ] Zweiter Writer wartet/scheitert sauber (Test)
- [ ] Stale Lock wird gemeldet, nicht gebrochen (Test)
- [ ] Lockdatei in .gitignore
