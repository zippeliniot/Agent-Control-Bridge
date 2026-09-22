# ACB-Dorfschaft-Pilot — Checkliste (Stand 2026-09-21)

## Profil (gepruft)
- `projects/dorfschaft/project.yaml`: `read_only: true`, `git_policy.allow_push: false` — bestaetigt.
- Kein Zugriff auf das Dorfschaft-Repo im Rahmen dieses Auftrags.

## Umgebung (von April bestaetigt)
- Codex laeuft nativ unter Windows/PowerShell (kein WSL mehr).
- Hauptrepo `E:\_DEV\dorfschaft` (Remote `git@github.com:zippeliniot/dorfschaft.git`,
  Branch `main`, HEAD `138f9717c0de4224859494a07a1366fc1faa0cfa`) ist unter
  Windows-Git normal nutzbar.
- Worktree-Status: Der zuletzt von Codex bearbeitete Stand liegt vermutlich in
  einem Worktree unter `E:\_DEV\Dorfschaft-worktrees\` (u. a. `AP15-RP2-HAM01`,
  Branch `codex/AP15-RP2-corrected-review-pending-des11-checkpoint`, HEAD
  `c4407b743ab098d9604a91e60822fce5914ec044`). Alle Worktrees sind laut
  `git worktree list --porcelain` als „prunable, gitdir file points to
  non-existent location" markiert und unter Windows-Git NICHT oeffenbar
  (Ursache: unter frueherer WSL-Umgebung angelegt, WSL inzwischen entfernt).

## Offene Pflichtpunkte — VOR BRIDGE-0066 durch April zu klaeren
(a) Ob April `git worktree repair` im Hauptrepo ausfuehrt und welcher Worktree
    danach massgeblich ist, oder ob main als Pilotgrundlage dient.
(b) `expected_branch` und `expected_head` fuer den so bestaetigten Stand.
(c) Ob Codex fuer BRIDGE-0066 im reparierten Worktree oder im Hauptrepo
    (`main`) arbeiten soll.
