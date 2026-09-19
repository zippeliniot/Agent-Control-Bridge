# BRIDGE-0053 - B3 Draft write und import

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0053 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel / FEATURE |
| Teile (alte Nummern) | 0053, 0054 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Ein Modul (draft.py): write + import, sicherheitsrelevant. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | BRIDGE-0049 |
| Gate | G1 |
| stop_conditions | DIRTY_WORKTREE, SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0053` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

**Teile strikt nacheinander (A, B, ...). Pro Teil: Haken setzen, Commit, Push. Scheitert ein Teil: STOPP (BLOCKED), spaetere Teile nicht beginnen.**

### Teil A (alt 0053) - CLI: draft write (Executor-Seite)
**Ziel:** `bridge draft write <id> --status S --summary T [--tests P/F/B]`. Schreibt nur drafts/. Pusht nie.
**Scope:** src/bridge/draft.py (neu), src/bridge/cli.py (Verdrahtung), src/bridge/gitops.py (kind `draft_write`), tests/test_draft.py (neu).
1. Git-Nachweis ueber `importer.collect_git_info`; base_head = task.git.expected_head, fehlt er -> fail-closed.
2. Scope-Check: changed_files ausserhalb allowed_paths -> Draft-Status BLOCKED, error_code SCOPE_VIOLATION. Sauberer Worktree Pflicht sonst DIRTY_WORKTREE.
3. `--commit`: nur drafts/<id>/<run>/draft.yaml, push=False.
4. Schreibt NIE in tasks/, results/, audit/ (Test).
**Tests:** `python -m unittest tests.test_draft`, dann volle Suite EINMAL.
- [x] draft write erzeugt validen Draft
- [x] Scope-Verstoss -> BLOCKED + Code (Test)
- [x] Kein Push, keine Schreibzugriffe auf tasks/results/audit (Test)
- [x] --commit committet nur die Draft-Datei (Test)

### Teil B (alt 0054) - CLI: draft import (Board-Seite) mit --dry-run
**Ziel:** `bridge draft import <id> [--run RUN-yy] [--dry-run]`: Draft -> result.yaml + Statuswechsel + Audit ueber vorhandene Runner/Importer-Logik.
**Scope:** src/bridge/draft.py, src/bridge/cli.py, tests/test_draft.py.
1. Pruefungen vor Schreiben: Draft valide, Auftrag existiert, Zustandsuebergang erlaubt (state_machine), Idempotenz: gleicher Draft bereits importiert -> No-op Exit 0.
2. Wiederverwendung: `runner.start` (falls noetig) + `runner.finish` mit `git_info_fn` aus dem Draft. Kein neuer Statuspfad.
3. `--dry-run`: gibt geplante Schritte aus, schreibt NICHTS (Test per Datei-Snapshot).
4. Writer-Guard: Klonordner muss `board` heissen, ausser `ACB_ALLOW_ANY_CLONE=1` (nur Tests) -> sonst SCOPE_VIOLATION.
5. Erster echter Import nur nach Freigabe durch April.
**Tests:** `python -m unittest tests.test_draft`, dann volle Suite EINMAL.
- [x] --dry-run schreibt nichts (Test)
- [x] Import erzeugt result.yaml + Audit (Test)
- [x] Zweiter Import = No-op (Test)
- [x] Writer-Guard greift ausserhalb board (Test)

### Teil C (Nachtrag aus BRIDGE-0049) - task brief nachbessern
**Ziel:** `bridge task brief` korrigieren.
**Scope:** src/bridge/cli.py, tests/test_cli.py.
1. Work-Package-Pfad aus dem Praefix der Task-ID bilden (nicht fest BRIDGE-), Suffix -R<n> beibehalten; Logik aus gitops._workpackage_filename wiederverwenden, nicht duplizieren. Existiert die Datei nicht: `-`.
2. Jede Ausgabezeile auf max. 120 Zeichen kuerzen (Ende `...`).
3. Tests: DORF-Auftrag -> kein BRIDGE-Pfad; lange Kriterien werden gekuerzt.
**Tests:** `python -m unittest tests.test_cli`.
- [x] WP-Pfad praefixrichtig oder `-`
- [x] Zeilen max. 120 Zeichen
- [x] Tests gruen
