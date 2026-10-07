# BRIDGE-0083 - Pfadkorrektur Vier-Wege-Topologie + RAG-Infrastruktur-Erkennung

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0083 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel / BUGFIX+FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | BRIDGE-0082 (ARCHIVED) |

> Kombiniert drei RAG-Bereiche in einem Auftrag (April-Entscheidung 07.10., token-sparsam).
> Ausdrücklich NICHT Teil: Ollama/Modell-Installation selbst (reserviert fuer BRIDGE-0084,
> "Skript bereit, Mensch bestaetigt Klick"), Retrieval-Pipeline.

**Anlass fuer Teil A:** April (07.10.): "Vier-Wege-Topologie (board/dev/claude/codex) nutzen,
nicht neues erfinden was nicht in das Gesamtkonzept passt." Die in BRIDGE-0082 getroffene Annahme
(`<store.root>/../../acb-rag-index`, zwei Ebenen hoch) widerspricht dem echten, in
`docs/architecture/machines.md` festgehaltenen Register: `board`, `dev`, `claude`, `codex` sowie
`projects\<projekt-id>` sind **Geschwisterverzeichnisse innerhalb** von
`E:\_DEV\Agent-Control-Bridge\`, nicht eine Ebene darueber. Der BRIDGE-0082-Pfad landet also
faktisch ausserhalb des gesamten ACB-Wurzelverzeichnisses - ein erfundener fuenfter Ort statt
eines passenden fuenften Geschwisterklons. Das wird hier korrigiert, bevor Teil B/C darauf aufbauen.

### Teil A - Pfadkorrektur: `rag-index` als fuenfter Geschwisterklon

**Scope:** `src/bridge/runner.py`, `docs/architecture/machines.md`.

1. `runner.maybe_sync_rag_index`: `index_path` von `Path(store.root).resolve().parent.parent /
   "acb-rag-index"` auf `Path(store.root).resolve().parent / "rag-index"` korrigieren - eine
   Ebene hoch (Geschwister von `dev`/`board`/`claude`/`codex`), nicht zwei. Docstring-Hinweis auf
   die bisherige, falsche Annahme entfernen/ersetzen.
2. `docs/architecture/machines.md`: neue Zeile im Klon-Register fuer `rag-index`
   (`E:\_DEV\Agent-Control-Bridge\rag-index`, Zweck: lokaler Klon von `zippeliniot/acb-rag-index`
   fuer RAG-Steering-Continuity, Betrieb durch Claude Code bei Bedarf/Sync).
- [x] `index_path` zeigt auf Geschwisterverzeichnis (Test: `tmp_path`-Fixture, keine Mock-Pfade)
- [x] `machines.md`-Registerzeile ergaenzt, bestehende Tabelle sonst unveraendert

**Offene Bestaetigung an April (bleibt auch nach Teil A offen):** der Klonname `rag-index` ist mein
Vorschlag passend zur bestehenden Rollen-Namenskonvention (`board`/`dev`/`claude`/`codex`) - bitte
bestaetigen oder korrigieren, und den Klon bei Gelegenheit auf HAM11/DES11 tatsaechlich anlegen
(`git clone` von `zippeliniot/acb-rag-index` nach `E:\_DEV\Agent-Control-Bridge\rag-index`), sonst
liefert Teil B/C-Sync dort nur "kein Repo am Pfad" zurueck (fail-soft, kein Absturz).

### Teil B - Infrastruktur-Erkennung (Ollama + Modell + Index-Klon), reine Erkennung

**Scope:** neues Modul `src/bridge/rag_prereqs.py`, `tests/test_rag_prereqs.py`.

1. Neue Funktion `check(index_path, *, ollama_url="http://localhost:11434",
   embed_model="nomic-embed-text") -> dict`:
   - `ollama_reachable`: `GET {ollama_url}/api/tags` (kurzer Timeout, `urllib`), fail-soft bei
     jedem Fehler (Verbindung, Timeout, ungueltiges JSON) -> `False`, nie eine Exception nach aussen.
   - `embed_model_present`: nur geprueft wenn `ollama_reachable`; `embed_model` (ggf. mit
     `:latest`-Suffix) in der Namensliste der Antwort.
   - `index_clone_exists`: `index_path.is_dir()` und `(index_path / ".git").exists()`.
   - `missing`: Liste lesbarer Bezeichner fuer fehlende Voraussetzungen (z. B. `"ollama"`,
     `"embed_model:nomic-embed-text"`, `"index_clone"`).
   - `all_ok`: `True` nur wenn alle drei Pruefungen erfolgreich.
   - Nie werfen (gleiches Fail-soft-Muster wie `gitops.git_pull`/`rag_index_sync`).
2. Kein Installationsversuch, keine Seiteneffekte - reine Erkennung.
- [x] Implementiert + getestet (alles vorhanden, Ollama nicht erreichbar, Modell fehlt,
      Index-Klon fehlt, alle drei Kombinationen gemischt)

### Teil C - Verdrahtung in `run start` (Anzeige, kein Block) + GitHub-Dokumentation

**Scope:** `src/bridge/runner.py`, `src/bridge/cli.py`, `tests/test_runner.py`,
neues `docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md`.

1. `runner.maybe_check_rag_prereqs(store, task_id) -> dict | None`: laedt Projektprofil (fail-soft
   `None` bei fehlendem/ungueltigem Profil oder `rag_enabled: false`), ruft sonst
   `rag_prereqs.check(index_path)` auf demselben Geschwisterpfad wie Teil A/BRIDGE-0082 auf.
2. `cli.py::_cmd_run` (`run start`): wenn Ergebnis vorhanden und `not all_ok`, fehlende Punkte
   zeilenweise auf stderr ausgeben (Hinweis auf die neue Doku-Datei), **kein** Abbruch von
   `run start` - der eigentliche Lauf bleibt davon unabhaengig (gleiches Prinzip wie Teil C aus
   BRIDGE-0082).
3. `docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md`: dokumentiert, was fuer RAG auf einer
   Maschine (HAM11/DES11) manuell vorhanden sein muss - Ollama-Installation, Pull von
   `nomic-embed-text`, Anlegen des `rag-index`-Klons (Teil A) - als Nachschlage-Beschreibung in
   GitHub (April: "dokumentieren was gemacht werden muss in github beschreibung"). Ausdruecklich
   **kein** automatisches Installationsskript hier; das bleibt BRIDGE-0084
   ("Skript bereit, Mensch bestaetigt Klick" - Installation selbst, nicht nur Erkennung).
- [x] Wechsel/Fehlen erkannt -> Hinweis ausgegeben (Test mit gemocktem `rag_prereqs.check`)
- [x] Kein `rag_enabled` -> keine Pruefung/Ausgabe (Test)
- [x] Pruef-Fehler blockiert `run start` nicht (Test: Lauf startet trotzdem)
- [x] Doku-Datei committet und lesbar (keine Platzhalter, konkrete Schritte je Komponente)

## Abschluss
1. Volle Suite EINMAL, letzte 3 Zeilen zeigen.
2. `git status` sauber.
- [x] Volle Suite gruen
