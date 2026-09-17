# BRIDGE-036 — Umbenennung Teil A: Agent Control Bridge (Projektprofil, CLI-Default, CCB-*-Dateinamen)

| Feld | Wert |
|------|------|
| bridge_task_id | BRIDGE-0036 |
| project_id | codex-control-bridge (Ausgangszustand — ändert sich erst **durch** diesen Auftrag, siehe unten) |
| task_class | FEATURE |
| depends_on | (keine, aber siehe Vorbedingung unten) |
| permission | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| executor | claude-code |
| review_roles | lead: anthropic, support: openai (aus Projektprofil übernommen) |
| Modell/Denkstufe | Claude Sonnet 5, Denkstufe LOW — reine, vollständig vorspezifizierte Umbenennungen (Ordner, Dateien, ein CLI-Default, Querverweise), keine einzige offene Design-Entscheidung mehr (Präfix `BRIDGE` bleibt, per Nutzer-Entscheidung bestätigt). |

> **Verbindlich für diesen und jeden CCB-Auftrag:**
> - Jede Zustandsänderung läuft über die Bridge-CLI, kein direktes Bearbeiten
>   von Store-Dateien.
> - `GIT_PUSH` steht im Profil — nach `run finish` **muss** gepusht werden,
>   idealerweise über `--commit`, und **sofort**, nicht gesammelt.

> **Vorbedingung, vor dem Start dieses Auftrags von Mensch/April zu
> bestätigen, nicht von Claude Code zu prüfen:** Das GitHub-Repo muss zu
> diesem Zeitpunkt bereits auf `Agent-Control-Bridge` umbenannt sein
> (reiner GitHub-Vorgang, kein CCB-Auftrag). Dieser Auftrag ändert nur
> Inhalte **innerhalb** des Repos — den Zeitpunkt des GitHub-Renames selbst
> steuert dieser Auftrag nicht.

## Kontext

Teil A der zweigeteilten Umbenennung (siehe Steuerchat-Gespräch): dieser
Auftrag deckt die **strukturell/funktionalen** Änderungen ab — Ordner,
Dateinamen, den einen echten CLI-Code-Default. Die restlichen ca. 30
Dateien mit reinem Textbezug (README, CLAUDE.md, CODEX.md, Schema-
Kommentare, Tests, Web-UI-Titel) sind bewusst **Teil B**, ein späterer,
eigener Auftrag — nicht Teil dieses Auftrags.

**Bewusst NICHT Teil dieses Auftrags** (historisches Volumen, laut
etablierter Praxis dieses Projekts — z. B. BRIDGE-034 — nicht rückwirkend
korrigiert):
- Die 37 bestehenden `tasks/*/task.yaml`/`results/*/*/result.yaml` mit
  `project_id: codex-control-bridge`.
- Die 6 `docs/handover/CCB-UEBERGABE-v*.md` (Dateiname **und** Inhalt).
- Die 20 `work-packages/*.md`, die den alten Namen erwähnen.
- `task_prefix: BRIDGE` bleibt unverändert (Nutzer-Entscheidung: „Bridge"
  ist weiterhin Teil des neuen Namens, kein Bezeichnungskonflikt wie bei
  „Codex").

## Von Claude Code umzusetzen

1. Auftrag anlegen und starten:
   ```
   bridge task create tasks/incoming/BRIDGE-0036.yaml
   bridge run start BRIDGE-0036 --actor claude-code
   ```

2. **`projects/codex-control-bridge/` → `projects/agent-control-bridge/`**
   (git mv, Historie erhalten):
   - `project_id: codex-control-bridge` → `project_id: agent-control-bridge`.
   - `repository: Codex-Control-Bridge` → `repository:
     Agent-Control-Bridge/claude` (Unterpfad, siehe Steuerchat-Diskussion
     zur Zwei-Klon-Struktur — zeigt konkret auf den Claude-Klon, nicht nur
     den übergeordneten Ordner).
   - `github_repo: zippeliniot/Codex-Control-Bridge` →
     `github_repo: zippeliniot/Agent-Control-Bridge`.
   - Kommentar am Dateianfang ergänzen: kurzer Verweis auf BRIDGE-036 und
     den ursprünglichen Namen, analog zum Muster aus dem
     Dorfschaft-Profil-Kommentar (BRIDGE-034).

3. **`src/bridge/cli.py`, `--project`-Default des `commands`-Befehls**
   (aktuell Zeile ~128–129): `default="codex-control-bridge"` →
   `default="agent-control-bridge"`, Hilfetext entsprechend anpassen.

4. **Fünf aktive Dateien umbenennen** (git mv, Historie erhalten):
   - `docs/CCB-STEUERCHAT-STANDARDSTART.md` → `docs/ACB-STEUERCHAT-STANDARDSTART.md`
   - `docs/CCB-STEUERCHAT-ARBEITSWEISE.md` → `docs/ACB-STEUERCHAT-ARBEITSWEISE.md`
   - `docs/CCB-STEUERCHAT-REFERENZ.md` → `docs/ACB-STEUERCHAT-REFERENZ.md`
   - `docs/CCB-ORCHESTRATOR-KONZEPT.md` → `docs/ACB-ORCHESTRATOR-KONZEPT.md`
   - `docs/CCB-PROJEKT-INTEGRATION.md` → `docs/ACB-PROJEKT-INTEGRATION.md`
   - **`docs/handover/CCB-UEBERGABE-v*.md` NICHT umbenennen** (historisch,
     siehe Kontext).

5. **Querverweise auf die fünf umbenannten Dateien korrigieren** (per
   `grep` gefunden, nur diese drei Dateien betroffen, keine anderen
   aktiven Fundstellen):
   - `docs/ACB-STEUERCHAT-STANDARDSTART.md` selbst: die Pflichtlektüre-
     Liste (Abschnitt 2) nennt alle vier anderen beim alten Dateinamen —
     auf die neuen Namen umstellen. Die Klon-URL in Abschnitt 1 auf
     `https://github.com/zippeliniot/Agent-Control-Bridge.git`
     aktualisieren (GitHub-Rename ist laut Vorbedingung zu diesem
     Zeitpunkt bereits erfolgt, die alte URL würde zwar per Redirect noch
     funktionieren, aber die Datei soll den korrekten, aktuellen Namen
     zeigen). Lokalen Scratch-Klon-Pfad (`/home/claude/ccb-session`)
     unverändert lassen — das ist ein reiner Sandbox-Pfad des Steuerchats,
     kein Bezug zum Projektnamen.
   - `docs/ACB-STEUERCHAT-REFERENZ.md`: Verweis auf
     `CCB-STEUERCHAT-ARBEITSWEISE.md` → `ACB-STEUERCHAT-ARBEITSWEISE.md`.
   - `docs/ACB-PROJEKT-INTEGRATION.md`: falls dort ein Verweis auf einen
     der anderen vier Dateinamen steht, ebenfalls korrigieren (beim
     Umsetzen gegenprüfen, in der Voranalyse keine gefunden, aber
     Verifikationspflicht Nr. 3 gilt — echten Inhalt lesen, nicht nur der
     Auflistung hier vertrauen).
   - `docs/handover/CCB-UEBERGABE-v*.md`: **nicht** anfassen, auch wenn
     dort einer der alten Dateinamen erwähnt wird (historisch).

6. **Tests, die den `--project`-Default direkt prüfen** (`tests/
   test_cli.py`, nach `codex-control-bridge` als erwartetem Default-Wert
   suchen): Erwartung auf `agent-control-bridge` anpassen. Alle übrigen
   Tests mit Namensbezug (README-/Doku-Inhalt betreffend) bleiben **Teil
   B**, hier nicht anfassen, außer sie prüfen exakt diesen einen
   CLI-Default.

7. Volle Testsuite frisch laufen lassen, dreimal, tatsächlich nachzählen.

8. Pflicht-Footer + Abschluss, `--commit` nutzen, **sofort pushen**:
   ```
   bridge run finish BRIDGE-0036 --status COMPLETED --actor claude-code \
     --commit \
     --summary "Umbenennung Teil A (strukturell/funktional) auf Agent Control Bridge: projects/codex-control-bridge/ zu projects/agent-control-bridge/ verschoben (project_id, repository: Agent-Control-Bridge/claude, github_repo aktualisiert). --project-CLI-Default in cli.py auf agent-control-bridge geaendert. Fuenf aktive CCB-*.md-Dateien zu ACB-*.md umbenannt (STANDARDSTART, ARBEITSWEISE, REFERENZ, ORCHESTRATOR-KONZEPT, PROJEKT-INTEGRATION), Querverweise innerhalb dieser Dateien korrigiert, Klon-URL in STANDARDSTART aktualisiert. Handover-Dokumente (docs/handover/CCB-UEBERGABE-v*.md) und alle bestehenden task.yaml/result.yaml/work-packages bewusst NICHT rueckwirkend geaendert (historisch). task_prefix bleibt BRIDGE. Teil B (README, CLAUDE.md, CODEX.md, Schema-Kommentare, uebrige Tests, Web-UI-Titel - ca. 30 Dateien mit reinem Textbezug) folgt als eigener, spaeterer Auftrag."
   git push
   ```
   `Auftrag: BRIDGE-0036 / Lauf: RUN-01 / Status: COMPLETED`

## Akzeptanzkriterien

- [x] `projects/agent-control-bridge/project.yaml` existiert (per `git mv`,
      Historie erhalten), `projects/codex-control-bridge/` existiert nicht
      mehr.
- [x] `project_id: agent-control-bridge`, `repository:
      Agent-Control-Bridge/claude`, `github_repo:
      zippeliniot/Agent-Control-Bridge`.
- [x] `--project`-Default in `cli.py` ist `agent-control-bridge`.
- [x] Alle fünf aktiven `CCB-*.md`-Dateien in `docs/` sind zu `ACB-*.md`
      umbenannt (per `git mv`).
- [x] `docs/handover/CCB-UEBERGABE-v*.md` unverändert (Name **und**
      Inhalt).
- [x] Alle Querverweise innerhalb der fünf umbenannten Dateien zeigen auf
      die neuen Dateinamen.
- [x] Klon-URL in `ACB-STEUERCHAT-STANDARDSTART.md` zeigt auf
      `zippeliniot/Agent-Control-Bridge.git`.
- [x] Bestehende `tasks/*/task.yaml`, `results/*/*/result.yaml`,
      `work-packages/*.md` unverändert (keine rückwirkende Korrektur).
- [x] `task_prefix: BRIDGE` unverändert.
- [x] Betroffener `--project`-Default-Test angepasst. Abweichung von der
      Voranalyse: nicht in `test_cli.py` gefunden (dort keine Assertion auf
      den Default-Wert), sondern in `tests/test_profiles.py` — vier Tests
      luden das echte Repo-Profil per `profiles.load_profile(REPO_ROOT,
      "codex-control-bridge")`, angepasst auf `"agent-control-bridge"`.
- [x] Volle Testsuite dreimal frisch grün (363 Tests, inkl. eingebettetem
      Fresh-Clone-Integrationstest), frischer Klon verifiziert.
- [x] Jeder Commit sofort gepusht, nicht gesammelt.
