# BRIDGE-0079: Claim-Commit-Pfad auf gitops.git_commit konsolidieren (autostash)

## Hintergrund

BRIDGE-0078 (claim/renew/release) führte in `claim.py` einen eigenständigen
Commit/Push-Pfad ein (`_sync_claim_commit`), der komplett an
`gitops.git_commit()` vorbei committet und pusht — inklusive eigener
Non-Fast-Forward-Erkennung und Branch-Prüfung. Grund: `gitops.git_commit()`
unterstützt beim Rebase-Retry kein `--autostash`, wäre also bei einem parallel
anstehenden, nicht committeten Audit-Eintrag fehlgeschlagen.

Der dafür bereits angelegte, getestete Whitelist-Eintrag für `kind="claim"`
in `expected_git_files()` (`gitops.py`) wird aktuell von niemandem
aufgerufen — totes Gleis. Damit existieren zwei parallele, nach `main`
schreibende Commit-Pfade im Repo.

## Ziel

Nur noch **ein** whitelist-geguardeter Commit/Push-Pfad im gesamten Repo.

## Umsetzung

- [ ] `gitops.git_commit()` um Parameter `autostash: bool = False` erweitern
- [ ] Bei `autostash=True`: Rebase-Retry nutzt `git rebase --autostash origin/<branch>` statt `git rebase origin/<branch>`
- [ ] Bei `autostash=False` (Default): bestehendes Verhalten für `cli.py`/`webui.py` unverändert
- [ ] `claim()`/`renew()`/`release()` in `claim.py` rufen `gitops.git_commit(store.root, "claim", task_id, actor, push=True, autostash=True, source=...)` auf
- [ ] `_sync_claim_commit` und zugehöriger Push-Retry-Code vollständig aus `claim.py` entfernt

## Checkpoints (Definition of Done)

- [ ] `test_claim_exact_path_only` bleibt grün
- [ ] Neuer Test: `autostash=True` end-to-end gegen echtes bare-Repo mit paralleler, nicht committeter Datei (Nachbau des ursprünglichen Problemfalls)
- [ ] Gesamte Testsuite grün, Testanzahl ≥ 536 (BRIDGE-0078-Stand)
- [ ] `git diff --stat` zeigt ausschließlich Änderungen in `gitops.py`, `claim.py`, zugehörigen Testdateien — keine Schema-/Profil-Änderungen

## Betroffene Dateien

- `src/bridge/gitops.py`
- `src/bridge/claim.py`
- `tests/test_gitops.py`
- `tests/test_claim.py`
