# BRIDGE-0064 - Parallelitaets- und Ausfalltests

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0064 |
| project_id | agent-control-bridge |
| Typ / Klasse | T3 / TEST |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - Nur Tests, Muster vorhanden. |
| Modellwechsel zum Vorgaenger | JA |
| depends_on | BRIDGE-0063 |
| Gate | G4 |
| stop_conditions | SCOPE_VIOLATION |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Reproduzierbare Tests fuer Lock, Claim und Ausfall. Kein Produktcode.

## Scope
tests/test_parallel.py (neu).

## Schritte
1. Zwei Subprozesse: gleicher Lock, gleicher Claim-Schluessel -> genau einer gewinnt.
2. Prozess bricht mitten im Schreiben ab -> Datei intakt, stale Lock/Claim erkannt.
3. Ohne Sleeps mit langen Wartezeiten (kurze Timeouts, Events).

## Tests
`python -m unittest tests.test_parallel` 5x, dann volle Suite EINMAL.

## Akzeptanzkriterien
- [ ] Parallel-Test 5/5 gruen
- [ ] Ausfalltest gruen
- [ ] Keine Produktcode-Aenderung
