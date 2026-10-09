# ACB - Uebergabe v20 (Stand 2026-10-09)

**Repo-HEAD bei Erstellung:** `0c9fff8` | **Tests:** 594/594 gruen (Stand nach BRIDGE-0099,
BRIDGE-0100 ist reine Layout-Aenderung ohne neue Tests).

**Fuer den neuen Steuerchat:** `docs/ACB-STEUERCHAT-STANDARDSTART.md`, diese Datei. v19 nicht
loeschen (Historie).

**Anlass dieser Version:** April hat diese Sitzung als zu weit fortgeschritten/kontextverloren
eingestuft ("dieser Chat hat zuviel vergessen") und ausdruecklich **keine weitere Ausfuehrung
in diesem Chat** angefordert - nur noch Dokumentation der offenen Punkte fuer einen neuen
Steuerchat. Diese Datei ist diese Dokumentation. Kein Code-/Repo-Zugriff mehr nach diesem
Commit in dieser Sitzung.

## 1. Was seit v19 fertig ist (BRIDGE-0093 bis BRIDGE-0100)

Alle folgenden Auftraege sind `ARCHIVED`, Tests jeweils gruen, gepusht:

- **BRIDGE-0093**: Mehrprojekt-RAG-Spezifikation (`docs/concepts/MEHRPROJEKT-RAG-SPEZIFIKATION.md`)
  - Subfolder-pro-`project_id`-Konvention im gemeinsamen `rag-index`-Klon, kein Code noetig
    (`runner.rag_index_clone_path()`/`gitops.rag_index_sync()` bereits projekt-agnostisch).
- **BRIDGE-0094**: Drei-Schichten-Architektur-Spezifikation
  (`docs/concepts/DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md`) - Decision-Log/Symbol-Graph/
  Vektor-RAG, Flag-Routing, Context-Assembler-Skizze, Edge-Typ-Liste gegen den realen
  Dorfschaft-Stack (PHP/JS/PowerShell).
- **BRIDGE-0096**: Governance-Pfad-Entscheidung - kein neues Gate, bleibt im bestehenden
  `ARCHITECTURE`-task_class-Fluss (Ergaenzung in derselben Spezifikationsdatei).
- **BRIDGE-0097**: `schemas/decision.schema.yaml` - Decision-Event-Schema (append-only,
  fuenf Ereignistypen, `supersedes` mit Geltungsbereich, Repo+Commit-gebundene
  `affects`/`implemented_by`/`verified_by`). Reiner Schema-Entwurf, bewusst **ohne**
  CLI-/Store-Anbindung (eigener Folgeauftrag).
- **BRIDGE-0098**: Tree-sitter-Spike (`docs/concepts/TREE-SITTER-SPIKE-ERGEBNIS.md`) - alle
  vier benoetigten PyPI-Pakete inkl. PowerShell-Grammatik bestaetigt, alle in BRIDGE-0094 §4
  geforderten Kantentypen fuer PHP/JS/PowerShell erfolgreich extrahiert. Ein Parser-Fund
  dokumentiert: `child_by_field_name()` liefert bei `base_clause`/`class_interface_clause`
  der PHP-Grammatik `None`, Typ-basierter Zugriff als Workaround noetig.
- **BRIDGE-0099**: neuer Endpunkt `GET /api/project/<id>/rag-status` + Web-UI-Button
  "RAG-Einrichtung pruefen" - zeigt `rag_prereqs.check()`-Ergebnis (Ollama/Modell/Index-Klon)
  und Pfade zu den **bereits vorhandenen** Setup-Skripten (`scripts/rag-setup.ps1`,
  `scripts/rag-ollama-inventory.ps1`) und zur Installations-Doku
  (`docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md`), die zuvor im Web UI nirgends
  verlinkt waren. Kein Skriptstart aus dem Web UI (fail-closed, BRIDGE-0084-Grundsatz).
- **BRIDGE-0100**: reine Platzierungskorrektur - der Stammdaten-Block steht jetzt direkt
  neben den anderen Eingabebereichen (Akteur/Filter) statt unterhalb aller Tabellen.

## 2. Offene Punkte aus dieser Sitzung (NICHT umgesetzt, fuer neuen Steuerchat)

### 2a. Projekt-ID-Feld im Stammdaten-Block: Dropdown statt Freitext

**Befund (April, 09.10.2026):** Die bestehende Filter-Dropdown "Projekt" oben auf der Seite
zeigt bewusst `task_prefix` (z. B. `BRIDGE`), nicht die rohe `project_id` (z. B.
`agent-control-bridge`) - siehe `cli.py:_board_project()`, Docstring: "Projekt-Spalte:
task_prefix aus dem Profil, Fail-soft auf project_id roh". Das neue Stammdaten-Feld
"Projekt-ID:" (BRIDGE-0099) ist dagegen ein Freitextfeld, das die **rohe** `project_id`
erwartet. Unterschiedliche Begriffe fuer unterschiedliche Werte an zwei Stellen derselben
Seite - verwirrend, kein Datenfehler.

**Von April bestaetigter naechster Schritt (noch nicht umgesetzt):** Stammdaten-Feld auf eine
Dropdown mit den echten `project_id`-Werten umstellen. Dafuer noetig:
- Neuer, lesender Endpunkt, der alle echten `project_id`-Werte liefert (z. B.
  `profiles.list_profiles(store.root)` - existiert bereits in `src/bridge/profiles.py:127`,
  bisher nicht ueber die Web-UI-API exponiert).
- `ps-projekt` von `<input>` auf `<select>` umstellen, analog zum bestehenden Muster in
  `updateProjektList()` (`src/bridge/webui.py`, BRIDGE-030).
- Tests analog zu `test_project_settings_get_returns_rag_enabled` etc.

### 2b. Hamburger-Menue mit Beschreibungsseiten

**Befund (April, 09.10.2026):** "es fehlt noch das hamburger menüe mit den
beschreibungsseiten" - auf Rueckfrage zum Umfang: **keine Praeferenz geaeussert**. Muss im
neuen Steuerchat zuerst geklaert werden, bevor ein Auftrag entsteht:
- Welche Inhalte? (Reine Links auf bestehende `docs/concepts/*.md`-Dateien im Repo? Eigene,
  im Web UI gerenderte Seiten? Nur ein Platzhalter-Menuepunkt, Inhalte spaeter?)
- Wo im Layout? (Position des Hamburger-Icons, welche Seiten/Abschnitte sollen ueberhaupt
  "Beschreibungsseiten" sein - vermutlich u. a. die neuen Konzeptdokumente aus Abschnitt 1
  dieser Datei, ggf. auch `RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md` passend zu BRIDGE-0099.)

### 2c. `machine: vm` in Audit-Eintraegen von BRIDGE-0093 bis BRIDGE-0100

**Befund (April, 09.10.2026):** Die Maschinen-Spalte zeigt fuer die neuesten Auftraege `vm`
statt eines echten Systemnamens (`HAM11`/`DES11`).

**Ursache (geklaert, kein Code-Fehler):** `registry.machine_name()`
(`src/bridge/registry.py:87`) faellt ohne `--machine`-Flag auf `platform.node()` zurueck -
diese Auftraege wurden vom Steuerchat selbst in dieser Cloud-Sitzung direkt per CLI
ausgefuehrt (nicht ueber Claude Code auf HAM11/DES11), `vm` ist der Hostname dieses
Cloud-Containers. **Nicht** rueckwirkend korrigierbar: `audit/audit.jsonl` ist bewusst
append-only (fail-closed-Grundsatz), bestehende Eintraege werden nicht veraendert.

**Fuer den neuen Steuerchat (Arbeitsweisen-Hinweis, noch nicht in
`ACB-STEUERCHAT-ARBEITSWEISE.md` festgehalten):** Fuehrt ein Steuerchat selbst (nicht Claude
Code auf HAM11/DES11) `bridge run start`/`run finish`/`task ...`-Befehle mit `--commit` aus,
sollte er **immer** ein explizites, aussagekraeftiges `--machine`-Flag setzen (z. B.
`--machine browser-claude`), statt den zufaelligen Cloud-Hostnamen in die Audit-Historie
einfliessen zu lassen. Diese Regel ist noch nicht verbindlich dokumentiert - ggf. als
Abschnitt 5 Punkt 8 in `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` ergaenzen.

## 3. Repo-Zustand bei Uebergabe

- HEAD: `0c9fff8`, `origin/main` identisch (alles gepusht).
- Tests: 594/594 gruen (unabhaengig im Steuerchat nachgelaufen vor dieser Datei).
- Keine offenen OpenIssues (`ISSUE-0001` bis `-0004` alle `CLOSED`, Stand v19).
- Naechste freie BRIDGE-ID: **BRIDGE-0101**.
