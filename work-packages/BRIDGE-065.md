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
2. Checkliste (Stand 2026-09-21, von April bestaetigt): Codex laeuft nativ unter Windows/PowerShell (kein WSL mehr). Hauptrepo `E:\_DEV\dorfschaft` (Remote git@github.com:zippeliniot/dorfschaft.git, Branch main, HEAD 138f9717c0de4224859494a07a1366fc1faa0cfa) ist unter Windows-Git normal nutzbar. Der zuletzt von Codex bearbeitete Stand liegt vermutlich in einem der Worktrees unter `E:\_DEV\Dorfschaft-worktrees\` (u. a. AP15-RP2-HAM01, Branch codex/AP15-RP2-corrected-review-pending-des11-checkpoint, HEAD c4407b743ab098d9604a91e60822fce5914ec044) - diese sind mit `git worktree list --porcelain` alle als 'prunable, gitdir file points to non-existent location' markiert und unter Windows-Git NICHT oeffenbar (Ursache: unter der frueheren WSL-Umgebung angelegt, WSL inzwischen entfernt).
3. Offene Pflichtpunkte, VOR BRIDGE-0066 durch April zu klaeren (nicht durch Raten zu schliessen): (a) ob April `git worktree repair` im Hauptrepo ausfuehrt und welcher Worktree danach der massgebliche ist, oder ob stattdessen main als Pilotgrundlage dient; (b) expected_branch und expected_head fuer den so bestaetigten Stand; (c) ob Codex fuer BRIDGE-0066 mit Windows-Git im reparierten Worktree oder im Hauptrepo (main) arbeiten soll.
4. Keine Dorfschaft-Datei lesen oder aendern.
**Tests:** `python -m unittest tests.test_profiles`.
- [ ] Profil read-only bestaetigt
- [ ] Checkliste mit Windows-Pfad, Worktree-Status und den drei offenen Pflichtpunkten (a)-(c)
- [ ] Kein Dorfschaft-Zugriff
