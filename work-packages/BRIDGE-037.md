# BRIDGE-037 — Umbenennung Teil B: Textstellen, `CCB_PROJECT_BASE`→`ACB_PROJECT_BASE`, Pfad-Dokumentation

| Feld | Wert |
|------|------|
| bridge_task_id | BRIDGE-0037 |
| project_id | agent-control-bridge |
| task_class | FEATURE |
| depends_on | (keine) |
| permission | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| executor | claude-code |
| review_roles | lead: anthropic, support: openai (aus Projektprofil übernommen) |
| Modell/Denkstufe | Claude Sonnet 5, Denkstufe MEDIUM — der Großteil (Textersetzung) ist LOW, aber `CCB_PROJECT_BASE`→`ACB_PROJECT_BASE` ist ein funktionaler Vertragsname mit Testabdeckung (Bruchrisiko bei Unachtsamkeit), und `machines.md`/`CLAUDE.md` brauchen echte inhaltliche Aktualisierung (neue Zwei-Klon-Struktur), nicht nur Find-Replace — deshalb insgesamt MEDIUM, nicht LOW. |

> **Verbindlich für diesen und jeden CCB-Auftrag:**
> - Jede Zustandsänderung läuft über die Bridge-CLI, kein direktes Bearbeiten
>   von Store-Dateien.
> - `GIT_PUSH` steht im Profil — nach `run finish` **muss** gepusht werden,
>   idealerweise über `--commit`, und **sofort**, nicht gesammelt.

## Kontext

Teil B der zweigeteilten Umbenennung (Teil A: BRIDGE-036, bereits
abgeschlossen und archiviert — Projektprofil, `--project`-CLI-Default,
die fünf `CCB-*.md`→`ACB-*.md`-Dateinamen). Dieser Auftrag deckt den Rest:
reine Textstellen, einen funktionalen Umgebungsvariablennamen, und zwei
Dokumente, die inhaltlich veraltet sind, weil sich die tatsächliche lokale
Struktur seit Teil A geändert hat (nicht nur der Name).

**Wichtige Unterscheidung, vor dem Umsetzen zu beachten:** „Codex" als
Name des OpenAI-Coding-Agenten bleibt überall unverändert (`CODEX.md`,
`CONTROL.md`, `executor: codex` im Schema, `codex-executor` als
Akteursname usw.) — betroffen ist **ausschließlich** „Codex Control
Bridge"/„Codex-Control-Bridge"/„CCB" als **Projektname**. Bei jeder
Fundstelle einzeln prüfen, welcher der beiden Fälle vorliegt, nicht
pauschal jedes Vorkommen von „Codex" ersetzen.

**Reale Vorbedingung, bereits erfüllt** (keine Aktion in diesem Auftrag
nötig, nur als Kontext): GitHub ist bereits auf `Agent-Control-Bridge`
umbenannt, lokal existieren bereits zwei getrennte Klone auf HAM11
(`E:\_DEV\Agent-Control-Bridge\claude`, `E:\_DEV\Agent-Control-Bridge\codex`).
`machines.md`/`CLAUDE.md` beschreiben noch die alte Ein-Klon-Struktur unter
dem alten Pfad — dieser Auftrag bringt sie auf den tatsächlichen Stand.

## Von Claude Code umzusetzen

1. Auftrag anlegen und starten:
   ```
   bridge task create tasks/incoming/BRIDGE-0037.yaml
   bridge run start BRIDGE-0037 --actor claude-code
   ```

2. **Reine Textersetzung** — „Codex-Control-Bridge"/„Codex Control
   Bridge"→„Agent-Control-Bridge"/„Agent Control Bridge",
   „CCB"→„ACB" (nur wo es das Projekt meint, siehe Unterscheidung oben),
   in diesen Dateien:
   - `README.md` (u. a. Kopfzeile „Projekt-ID: CCB" → „Projekt-ID: ACB",
     „Arbeitsname: Codex Control Bridge" → „Arbeitsname: Agent Control
     Bridge").
   - `docs/PROJEKTKONZEPT.md` (dieselben Kopfzeilen-Felder, plus die
     übrigen Fließtext-Stellen).
   - `docs/architecture/ARCHITECTURE.md` (Titel + Fließtext).
   - `docs/security/SECURITY-MODEL.md`, `docs/architecture/directory-structure.md`,
     `docs/SETUP.md`, `schemas/README.md` (je 1 Fundstelle).
   - `docs/ACB-PROJEKT-INTEGRATION.md`, `docs/ACB-STEUERCHAT-STANDARDSTART.md`,
     `docs/ACB-STEUERCHAT-ARBEITSWEISE.md`, `docs/ACB-STEUERCHAT-REFERENZ.md`,
     `docs/ACB-ORCHESTRATOR-KONZEPT.md` — restliche Fließtext-Stellen
     (Dateinamen und Querverweise bereits durch BRIDGE-036 erledigt, hier
     nur noch Prosa-Erwähnungen wie „CCB-eigenen Aufträgen").
   - `schemas/task.schema.yaml`, `schemas/result.schema.yaml`,
     `schemas/registry.schema.yaml`, `schemas/project.schema.yaml`,
     `schemas/heartbeat.schema.yaml`, `schemas/audit-event.schema.yaml`,
     `schemas/watcher-policy.yaml`, `schemas/state-model.yaml`,
     `schemas/git-readonly-allowlist.yaml`, `schemas/audit-event-map.yaml`
     (alle je 1–4 Kommentar-Fundstellen, keine funktionalen Feldwerte).
   - `src/bridge/store.py`, `src/bridge/importer.py`, `src/bridge/cli.py`
     (Modul-Docstrings bzw. Argparse-Beschreibungstext).
   - `src/bridge/webui.py`, Zeilen ~312/344: `<title>`/`<h1>` von „Codex
     Control Bridge" auf „Agent Control Bridge".
   - `src/bridge/adapter.py`: „CCB-Store" im Docstring → „ACB-Store".
   - `registry.yaml`: Kommentarzeile 1.
   - `CODEX.md`, `CLAUDE.md`: **nur** die Projektname-Stellen (siehe
     Unterscheidung oben — `CODEX.md` referenziert an einer Stelle
     `Codex-Control-Bridge` als Projektname, das ändert sich; „Codex" als
     Agentenname im Rest der Datei bleibt).

3. **`CCB_PROJECT_BASE` → `ACB_PROJECT_BASE`** (funktionaler Name, mit
   Tests):
   - `src/bridge/registry.py`: Docstring (Zeile ~10) und der tatsächliche
     Default-Parameter `env_override_name="CCB_PROJECT_BASE"` (Zeile
     ~100) → `"ACB_PROJECT_BASE"`.
   - `tests/test_cli.py` (Zeilen ~448, 453, 464, 486) und
     `tests/test_registry.py` (Zeilen ~52, 93, 110): alle
     `CCB_PROJECT_BASE`-Vorkommen auf `ACB_PROJECT_BASE` umstellen —
     sowohl das Setzen/Löschen der Umgebungsvariable als auch die
     Assertion auf den Namen in Fehlermeldungen.
   - Da bisher **niemand** `CCB_PROJECT_BASE` produktiv gesetzt hat (Codex-
     WSL-Einrichtung steht noch aus, siehe Kontext), kein Migrationspfad
     für Altwerte nötig — reine Umbenennung, kein Fallback auf den alten
     Namen.

4. **`docs/architecture/machines.md`** — inhaltliche Aktualisierung, nicht
   nur Textersatz:
   - Tabellenzeilen (aktuell `E:\_DEV\Codex-Control-Bridge` für
     HAM11/DES11): auf die tatsächliche Zwei-Klon-Struktur umstellen —
     `E:\_DEV\Agent-Control-Bridge\claude` (Claude Code) und
     `E:\_DEV\Agent-Control-Bridge\codex` (Codex, eigener Klon, siehe
     Steuerchat-Diskussion zur sicheren Parallelverarbeitung) als zwei
     getrennte Zeilen/Spalten ergänzen, nicht nur den alten Pfad
     umbenennen.
   - Abschnitt zu Claude Codes Arbeitsverzeichnis (Zeile ~24, ~45): auf
     `E:\_DEV\Agent-Control-Bridge\claude` präzisieren.
   - Kurzer neuer Hinweis: Codex nutzt unter WSL die Umgebungsvariable
     `ACB_PROJECT_BASE`, zeigt auf den eigenen `codex`-Klon, keine
     Registry-Änderung nötig (Muster aus der Steuerchat-Diskussion
     übernehmen).

5. **`CLAUDE.md`**: die beiden Pfad-Referenzen (Zeilen ~14, ~28) von
   `E:\_DEV\Codex-Control-Bridge` auf `E:\_DEV\Agent-Control-Bridge\claude`
   aktualisieren — reale, funktionale Korrektur (Claude Code liest diese
   Datei bei jedem Start), nicht nur kosmetisch.

6. Volle Testsuite frisch laufen lassen, dreimal, tatsächlich nachzählen
   (Referenzwert vor diesem Auftrag: 363 Tests — plus die angepassten,
   nicht neuen, Tests aus Schritt 3).

7. Pflicht-Footer + Abschluss, `--commit` nutzen, **sofort pushen**:
   ```
   bridge run finish BRIDGE-0037 --status COMPLETED --actor claude-code \
     --commit \
     --summary "Umbenennung Teil B abgeschlossen: alle verbliebenen Textstellen (README, PROJEKTKONZEPT, ARCHITECTURE, SECURITY-MODEL, Schema-Kommentare, Docstrings in store.py/importer.py/cli.py/adapter.py, webui.py-Seitentitel, registry.yaml-Kommentar, CODEX.md/CLAUDE.md-Projektnamenstellen) von Codex-Control-Bridge/CCB auf Agent-Control-Bridge/ACB umgestellt - 'Codex' als Name des OpenAI-Agenten blieb ueberall unangetastet. CCB_PROJECT_BASE zu ACB_PROJECT_BASE umbenannt (registry.py Default-Parameter + Docstring, test_cli.py und test_registry.py angepasst) - funktionaler Name, noch nie produktiv gesetzt, daher kein Migrationspfad noetig. machines.md inhaltlich auf die tatsaechliche Zwei-Klon-Struktur aktualisiert (E:\\_DEV\\Agent-Control-Bridge\\claude und \\codex getrennt dokumentiert, ACB_PROJECT_BASE fuer Codex/WSL erwaehnt). CLAUDE.md-Pfadreferenzen auf den neuen Claude-Klon-Pfad korrigiert."
   git push
   ```
   `Auftrag: BRIDGE-0037 / Lauf: RUN-01 / Status: COMPLETED`

## Akzeptanzkriterien

- [ ] Alle in Schritt 2 gelisteten Dateien enthalten keine
      Projektname-Erwähnung von „Codex-Control-Bridge"/„Codex Control
      Bridge"/„CCB" mehr — „Codex" als Agentenname bleibt überall
      unverändert erhalten.
- [ ] `registry.py`: `env_override_name`-Default ist
      `"ACB_PROJECT_BASE"`, Docstring aktualisiert.
- [ ] `test_cli.py` und `test_registry.py`: alle `CCB_PROJECT_BASE`-
      Vorkommen auf `ACB_PROJECT_BASE` umgestellt.
- [ ] `machines.md` beschreibt die tatsächliche Zwei-Klon-Struktur
      (`...\claude`, `...\codex`), nicht mehr einen einzelnen Pfad.
- [ ] `CLAUDE.md`-Pfadreferenzen zeigen auf
      `E:\_DEV\Agent-Control-Bridge\claude`.
- [ ] `CODEX.md`/`CONTROL.md`: „Codex" als Agentenname unangetastet,
      nur die eine Projektname-Stelle in `CODEX.md` geändert.
- [ ] Bestehende `tasks/*/task.yaml`, `results/*/*/result.yaml`,
      `work-packages/*.md`, `docs/handover/*.md` unverändert (keine
      rückwirkende Korrektur, wie bei Teil A).
- [ ] `task_prefix: BRIDGE` unverändert.
- [ ] Volle Testsuite dreimal frisch grün, frischer Klon verifiziert.
- [ ] Jeder Commit sofort gepusht, nicht gesammelt.
