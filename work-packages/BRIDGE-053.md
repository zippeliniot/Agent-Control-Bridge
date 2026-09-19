# BRIDGE-0053 - CLI: draft write (Executor-Seite)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0053 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Neue Logik mit Git-Nachweis und Scope-Pruefung. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0052 |
| Gate | G1 |
| stop_conditions | DIRTY_WORKTREE, SCOPE_VIOLATION |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
`bridge draft write <id> --status S --summary T [--tests P/F/B]`. Schreibt nur drafts/. Pusht nie.

## Scope
src/bridge/draft.py (neu), src/bridge/cli.py (Verdrahtung), src/bridge/gitops.py (kind `draft_write`), tests/test_draft.py (neu).

## Schritte
1. Git-Nachweis ueber `importer.collect_git_info`; base_head = task.git.expected_head, fehlt er -> fail-closed.
2. Scope-Check: changed_files ausserhalb allowed_paths -> Draft-Status BLOCKED, error_code SCOPE_VIOLATION. Sauberer Worktree Pflicht sonst DIRTY_WORKTREE.
3. `--commit`: nur drafts/<id>/<run>/draft.yaml, push=False.
4. Schreibt NIE in tasks/, results/, audit/ (Test).

## Tests
`python -m unittest tests.test_draft`, dann volle Suite EINMAL.

## Akzeptanzkriterien
- [ ] draft write erzeugt validen Draft
- [ ] Scope-Verstoss -> BLOCKED + Code (Test)
- [ ] Kein Push, keine Schreibzugriffe auf tasks/results/audit (Test)
- [ ] --commit committet nur die Draft-Datei (Test)
