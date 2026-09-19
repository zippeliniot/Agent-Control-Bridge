# BRIDGE-0055 - Stufe-A-Abnahmetest

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0055 |
| project_id | agent-control-bridge |
| Typ / Klasse | T3 / TEST |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - Nur Testlogik, Muster vorhanden. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0054 |
| Gate | G2 |
| stop_conditions | SCOPE_VIOLATION |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Hermetischer End-to-End-Test: create -> draft write -> import --dry-run -> import. Danach PASS/FAIL/BLOCKED-Zusammenfassung.

## Scope
tests/test_stage_a.py (neu). Keine Produktcode-Aenderung.

## Schritte
1. Temp-Git-Repo + lokales bare 'origin' (Muster: tests/test_gitops.py).
2. Pruefen: Executor-Klon pusht nicht, schreibt nur drafts/; Dry-run aendert nichts; Import setzt Status + result.yaml + Audit.
3. Bei PASS: April setzt in ENTSCHEIDUNG-PUSH-MODELL.md `G2: IN KRAFT` (nicht Claude Code).

## Tests
`python -m unittest tests.test_stage_a`, dann volle Suite EINMAL.

## Akzeptanzkriterien
- [ ] Abnahmetest gruen
- [ ] Kein Push im Executor-Pfad belegt
- [ ] Dry-run ohne Schreibzugriff belegt
- [ ] Import-Ergebnis vollstaendig belegt
