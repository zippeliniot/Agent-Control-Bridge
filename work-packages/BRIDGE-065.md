# BRIDGE-0065 - Dorfschaft: read-only Profil + Checkliste

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0065 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / DOCS |
| Teile (alte Nummern) | 0065 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Pilotvorbereitung, Fremdprojekt darf nicht beruehrt werden. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | BRIDGE-0063 |
| Gate | G5 |
| stop_conditions | IDENTITY_MISMATCH, SCOPE_VIOLATION |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0065` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

## Auftrag
**Ziel:** Profil pruefen, Checkliste schreiben. KEIN Zugriff auf das Dorfschaft-Repo.
**Scope:** projects/dorfschaft/project.yaml (nur pruefen/ggf. `push_mode: draft`), docs/ACB-DORFSCHAFT-PILOT.md (neu, max. 30 Zeilen).
1. Pruefen: `read_only: true`, `git_policy.allow_push: false`.
2. Checkliste: expected_head, expected_branch, WSL-Pfad (bisher NICHT bestaetigt -> Pflichtfeld fuer April), Executor codex, Befehl `scripts/integration_readonly.py --project-id dorfschaft --task-prefix DORF ...`.
3. Keine Dorfschaft-Datei lesen oder aendern.
**Tests:** `python -m unittest tests.test_profiles`.
- [ ] Profil read-only bestaetigt
- [ ] Checkliste mit WSL-Pfad als offener Pflichtangabe
- [ ] Kein Dorfschaft-Zugriff
