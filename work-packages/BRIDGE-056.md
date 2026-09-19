# BRIDGE-0056 - Executor-Regeln auf Draft-Modus pruefen

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0056 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / DOCS |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - Textregeln mit Widerspruchssuche. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | BRIDGE-0055 |
| Gate | G2 |
| stop_conditions | CONCEPT_CONFLICT |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
CLAUDE.md und CODEX.md um kurzen Abschnitt 'Draft-Modus' ergaenzen, Widersprueche zu 'Sofort pushen' aufloesen.

## Scope
CLAUDE.md, CODEX.md.

## Schritte
1. Neuer Abschnitt je Datei (max. 12 Zeilen): gilt nur bei `push_mode: draft` - `bridge draft write`, kein Push, kein Schreiben in tasks/results/audit.
2. 'Sofort pushen' explizit auf `push_mode: direct` begrenzen.
3. Widerspruchssuche: `git grep -n -i push -- CLAUDE.md CODEX.md CONTROL.md`, Befund in --summary.

## Tests
Keine (nur Doku).

## Akzeptanzkriterien
- [ ] Abschnitt Draft-Modus in CLAUDE.md und CODEX.md
- [ ] Push-Regel eindeutig begrenzt
- [ ] Keine Widersprueche in CLAUDE/CODEX/CONTROL
