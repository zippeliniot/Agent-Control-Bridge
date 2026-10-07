# BRIDGE-0081 - RAG-Flags: Auftrags-Anzeige + Projekt-Einstellungsseite

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0081 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | BRIDGE-0080 (ARCHIVED) |

> Kombiniert zwei RAG-Bereiche in einem Auftrag (April-Entscheidung 07.10., token-sparsam).
> Ausdrücklich NICHT Teil: die Retrieval-/Injection-Pipeline selbst.

### Teil A - Auftrags-Flag `rag_used_since` (Schema + Anzeige)

**Scope:** `schemas/task.schema.yaml`, `src/bridge/webui.py`, `tests/test_webui.py`.

1. `task.schema.yaml`: neues Feld `rag_used_since` (`["string","null"]`, RFC3339-Pattern wie `started_at`,
   default `null`). Backend-gesetzt durch eine künftige Retrieval-Pipeline, nicht manuell setzbar -
   Doku-Hinweis im Feld-Kommentar.
2. `webui.py`: Feld in `board_payload()` (board + other) durchreichen, analog `machine`.
- [ ] Schema-Feld ergänzt, rückwärtskompatibel (fehlt -> `null`)
- [ ] `rag_used_since` in Board- und Other-Zeilen sichtbar (Test: Feld vorhanden, Wert `null` ohne Pipeline)

### Teil B - Projekt-Flag `rag_enabled` + Einstellungsseite

**Scope:** `schemas/project.schema.yaml`, `src/bridge/profiles.py`, `src/bridge/gitops.py`,
`src/bridge/webui.py`, `tests/test_profiles.py`, `tests/test_gitops.py`, `tests/test_webui.py`.

1. `project.schema.yaml`: `rag_enabled` (bool, default `false`), `rag_index_repo` (`["string","null"]`,
   default `null`).
2. `profiles.py`: neue Funktion `write_profile(root, project_id, updates, schema_dir)` - lädt bestehendes
   Profil, merged `updates`, validiert, schreibt atomar zurück (Fail-closed bei Schemafehler, kein
   Teilschreiben).
3. `gitops.py` `expected_git_files`: neuer `kind="project_settings"` -> `[f"projects/{project_id}/project.yaml"]`
   (exakter Pfad, analog `kind="claim"`).
4. `webui.py`: `GET /api/project/<id>` (Profil lesen) + `POST /api/project/<id>/settings` (Body
   `{"rag_enabled": bool}`, nur dieses Feld), committet+gepusht über `_git_commit_and_push(..., kind=
   "project_settings", task_id=project_id)`. Minimale HTML-Sektion: Projekt-Auswahl + Checkbox, kein
   neues Seiten-Layout.
- [ ] Schema-Felder ergänzt
- [ ] `write_profile` implementiert + getestet (gültiges Update, Schema-Verstoss -> Fehler ohne Teilschreiben)
- [ ] `project_settings`-Whitelist exakt auf die eine Profildatei begrenzt (Test)
- [ ] Web-Endpunkt + minimale UI, Checkbox-Toggle committet+pusht automatisch

## Abschluss
1. Volle Suite EINMAL, letzte 3 Zeilen zeigen.
2. `git status` sauber.
- [ ] Volle Suite gruen
