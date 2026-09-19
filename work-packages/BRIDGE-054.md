# BRIDGE-0054 - CLI: draft import (Board-Seite) mit --dry-run

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0054 |
| project_id | agent-control-bridge |
| Typ / Klasse | T4 / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Import schreibt den Store - sicherheitsrelevant, deshalb Freigabe durch April vor echtem Einsatz. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | BRIDGE-0053 |
| Gate | G1 |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
`bridge draft import <id> [--run RUN-yy] [--dry-run]`: Draft -> result.yaml + Statuswechsel + Audit ueber vorhandene Runner/Importer-Logik.

## Scope
src/bridge/draft.py, src/bridge/cli.py, tests/test_draft.py.

## Schritte
1. Pruefungen vor Schreiben: Draft valide, Auftrag existiert, Zustandsuebergang erlaubt (state_machine), Idempotenz: gleicher Draft bereits importiert -> No-op Exit 0.
2. Wiederverwendung: `runner.start` (falls noetig) + `runner.finish` mit `git_info_fn` aus dem Draft. Kein neuer Statuspfad.
3. `--dry-run`: gibt geplante Schritte aus, schreibt NICHTS (Test per Datei-Snapshot).
4. Writer-Guard: Klonordner muss `board` heissen, ausser `ACB_ALLOW_ANY_CLONE=1` (nur Tests) -> sonst SCOPE_VIOLATION.
5. Erster echter Import nur nach Freigabe durch April.

## Tests
`python -m unittest tests.test_draft`, dann volle Suite EINMAL.

## Akzeptanzkriterien
- [ ] --dry-run schreibt nichts (Test)
- [ ] Import erzeugt result.yaml + Audit (Test)
- [ ] Zweiter Import = No-op (Test)
- [ ] Writer-Guard greift ausserhalb board (Test)
