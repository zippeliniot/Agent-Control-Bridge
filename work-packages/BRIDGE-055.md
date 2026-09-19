# BRIDGE-0055 - B4 Stufe-A-Abnahme + Executor-Regeln

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0055 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel / FEATURE |
| Teile (alte Nummern) | 0055, 0056 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - Nur Tests und Textregeln nach Muster. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0053 |
| Gate | G2 |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0055` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

**Teile strikt nacheinander (A, B, ...). Pro Teil: Haken setzen, Commit, Push. Scheitert ein Teil: STOPP (BLOCKED), spaetere Teile nicht beginnen.**

### Teil A (alt 0055) - Stufe-A-Abnahmetest
**Ziel:** Hermetischer End-to-End-Test: create -> draft write -> import --dry-run -> import. Danach PASS/FAIL/BLOCKED-Zusammenfassung.
**Scope:** tests/test_stage_a.py (neu). Keine Produktcode-Aenderung.
1. Temp-Git-Repo + lokales bare 'origin' (Muster: tests/test_gitops.py).
2. Pruefen: Executor-Klon pusht nicht, schreibt nur drafts/; Dry-run aendert nichts; Import setzt Status + result.yaml + Audit.
3. Bei PASS: April setzt in ENTSCHEIDUNG-PUSH-MODELL.md `G2: IN KRAFT` (nicht Claude Code).
**Tests:** `python -m unittest tests.test_stage_a`, dann volle Suite EINMAL.
- [x] Abnahmetest gruen
- [x] Kein Push im Executor-Pfad belegt
- [x] Dry-run ohne Schreibzugriff belegt
- [x] Import-Ergebnis vollstaendig belegt

### Teil B (alt 0056) - Executor-Regeln auf Draft-Modus pruefen
**Ziel:** CLAUDE.md und CODEX.md um kurzen Abschnitt 'Draft-Modus' ergaenzen, Widersprueche zu 'Sofort pushen' aufloesen.
**Scope:** CLAUDE.md, CODEX.md.
1. Neuer Abschnitt je Datei (max. 12 Zeilen): gilt nur bei `push_mode: draft` - `bridge draft write`, kein Push, kein Schreiben in tasks/results/audit.
2. 'Sofort pushen' explizit auf `push_mode: direct` begrenzen.
3. Widerspruchssuche: `git grep -n -i push -- CLAUDE.md CODEX.md CONTROL.md`, Befund in --summary.
**Tests:** Keine (nur Doku).
- [x] Abschnitt Draft-Modus in CLAUDE.md und CODEX.md
- [x] Push-Regel eindeutig begrenzt
- [ ] Keine Widersprueche in CLAUDE/CODEX/CONTROL
