# BRIDGE-0082 - Maschinenwechsel-Erkennung + RAG-Index-Sync

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0082 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | BRIDGE-0081 (ARCHIVED) |

> Ausdrücklich NICHT Teil: Ollama/Modell-Installation (BRIDGE-0083), Retrieval-Pipeline.

**Offene Annahme, von April zu bestätigen:** lokaler Klonpfad des Index-Repos wird als
Geschwisterverzeichnis zum ACB-Checkout angenommen (`<E:\_DEV>/acb-rag-index`, eine Ebene über
`Agent-Control-Bridge/`) - passend zur Vier-Wege-Verzeichnistopologie (`board/`, `dev/`, `claude/`,
`codex/`), aber nicht verifiziert gegen den echten HAM11-Pfad.

### Teil A - Maschinenwechsel-Erkennung

**Scope:** `src/bridge/store.py`, `tests/test_store.py`.

1. Neue Methode `Store.last_machine_for_project(project_id) -> str | None`: liest `audit.jsonl`
   rueckwaerts (neuester Eintrag zuerst), fuer jeden Eintrag mit `machine`-Feld wird `bridge_task_id`
   gegen sein `project_id` aufgeloest (`load_task`, Cache je Scan), erster Treffer mit passendem
   `project_id` gewinnt. `None` wenn keiner gefunden.
- [x] Implementiert + getestet (Treffer, kein Treffer, mehrere Projekte gemischt im Audit)

### Teil B - RAG-Index-Sync (reiner Git-Vorgang)

**Scope:** `src/bridge/gitops.py`, `tests/test_gitops.py`.

1. Neue Funktion `rag_index_sync(repo_root) -> dict`: ruft `git_pull(repo_root)` auf; bei Erfolg
   zusaetzlich `git lfs pull` (fail-soft, eigenes `error`-Feld, kein Block wenn `git-lfs` fehlt).
   Nie werfen (gleiches Muster wie `git_pull`/`git_fetch`).
- [x] Implementiert + getestet (Erfolg, kein Repo am Pfad -> Fehler im Rueckgabewert, nie Exception)

### Teil C - Verdrahtung in `run start`

**Scope:** `src/bridge/runner.py`, `tests/test_runner.py`.

1. `runner.start()`: nach Laden des Task-Dokuments `project_id` ermitteln, `profiles.load_profile`
   pruefen (fail-soft `False` bei fehlendem/ungueltigem Profil - gleiches Muster wie `_board_project`).
   Nur wenn `rag_enabled`: `last_machine_for_project(project_id)` gegen das aktuelle `machine`
   vergleichen. Bei Unterschied (oder `None`, d.h. erster Lauf): `rag_index_sync()` auf dem
   Geschwisterpfad aufrufen, Ergebnis im Rueckgabewert von `start()` als `rag_sync` (optional,
   `None` wenn nicht ausgeloest) mitgeben - **kein Blockieren des eigentlichen Laufs bei Sync-Fehler**,
   nur sichtbar im CLI-Output.
2. `cli.py::_cmd_run` (`run start`): `rag_sync`-Ergebnis zusaetzlich ausgeben, falls vorhanden.
- [ ] Wechsel erkannt -> Sync ausgeloest (Test mit gemocktem `rag_index_sync`)
- [ ] Kein `rag_enabled` -> keine Erkennung/Sync (Test)
- [ ] Sync-Fehler blockiert `start()` nicht (Test: `start()` liefert weiterhin `run_id`)

## Abschluss
1. Volle Suite EINMAL, letzte 3 Zeilen zeigen.
2. `git status` sauber.
- [ ] Volle Suite gruen
