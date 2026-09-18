# ACB-Übergabe v10

Stand: HEAD `e328975`, Repo `zippeliniot/Agent-Control-Bridge` (bis
17.09.2026 `zippeliniot/Codex-Control-Bridge`). Letzter archivierter
Auftrag: **BRIDGE-0037**. Kein Auftrag aktuell `RUNNING`.

---

## 0. Was hat sich geändert (zuerst lesen)

**Das gesamte Projekt wurde umbenannt: „Codex Control Bridge"/„CCB" →
„Agent Control Bridge"/„ACB".** Grund: „Codex" im Namen implizierte
fälschlich eine reine OpenAI-Codex-Bindung, obwohl das Projekt von Anfang
an sowohl Claude Code als auch Codex orchestrieren sollte. „Bridge" und
der `task_prefix: BRIDGE` blieben unverändert — kein Bezeichnungskonflikt,
„Bridge" ist weiterhin Teil des neuen Namens.

- **GitHub-Repo umbenannt** auf `zippeliniot/Agent-Control-Bridge` (alte
  URL leitet automatisch weiter, funktioniert aber nicht mehr dauerhaft
  verlassen — neue URL überall verwenden).
- **BRIDGE-036** (strukturell): `projects/codex-control-bridge/` →
  `projects/agent-control-bridge/` (`project_id`, `repository:
  Agent-Control-Bridge/claude`, `github_repo`), `--project`-CLI-Default,
  fünf `CCB-*.md` → `ACB-*.md` umbenannt (`STANDARDSTART`,
  `ARBEITSWEISE`, `REFERENZ`, `ORCHESTRATOR-KONZEPT`,
  `PROJEKT-INTEGRATION`), Querverweise + Klon-URL korrigiert.
- **BRIDGE-037** (Text/Doku, über einen Systemwechsel HAM11→DES11 hinweg
  fortgesetzt — Checkpoint & Resume real genutzt, nicht nur theoretisch):
  alle verbliebenen Textstellen (README, PROJEKTKONZEPT, ARCHITECTURE,
  SECURITY-MODEL, Schema-Kommentare, Docstrings, Web-UI-Seitentitel,
  `registry.yaml`) umgestellt. **`CCB_PROJECT_BASE` → `ACB_PROJECT_BASE`**
  (Umgebungsvariable in `registry.py`s `resolve_base()`) — falls das
  irgendwo schon als Env-Var gesetzt wurde, muss das nachgezogen werden.
  „Codex" als Name des OpenAI-Agenten (`CODEX.md`, `CONTROL.md`,
  `executor: codex`) blieb bewusst überall unangetastet.
- **Bewusst NICHT rückwirkend geändert** (Historie bleibt beim alten
  Namen): alle bestehenden `tasks/*/task.yaml`/`results/*/*/result.yaml`,
  `work-packages/*.md`, `docs/handover/CCB-UEBERGABE-v2..v9.md` (Name
  **und** Inhalt). Ein paar Test-Fixture-Werte in `tests/test_*.py`
  nutzen weiterhin `"codex-control-bridge"` als beliebigen synthetischen
  Platzhalter-String, unkritisch, nicht an das echte Profil gebunden.

**Lokale Struktur grundlegend geändert** — nicht mehr ein Checkout pro
Maschine, sondern **mehrere getrennte Klone pro Maschine**, wegen eines
sonst realen Git-Kollisionsrisikos (siehe Abschnitt 3):

```
E:\_DEV\Agent-Control-Bridge\claude\   <- Claude Code
E:\_DEV\Agent-Control-Bridge\codex\    <- Codex (WSL, ACB_PROJECT_BASE-Override)
```
Auf **beiden** Maschinen (HAM11 und DES11) eingerichtet. Der alte
Ordner `E:\_DEV\Codex-Control-Bridge` existiert auf beiden Maschinen
z. T. noch als leere Leiche (Windows-Datei-Lock verhinderte vollständiges
Löschen) — funktional bedeutungslos, kann bei Gelegenheit/Neustart
aufgeräumt werden, keine Eile.

**`registry.yaml` unverändert** — `HAM11`/`DES11` zeigen weiterhin nur auf
`E:\_DEV` als Basis; kombiniert mit `repository: Agent-Control-Bridge/claude`
im Projektprofil ergibt das automatisch den richtigen Pfad. Codex
überschreibt für sich selbst per `ACB_PROJECT_BASE`-Umgebungsvariable,
ohne die Registry anzufassen.

---

## 1. Offene Aufträge — Reihenfolge

1. **BRIDGE-0035** — spezifiziert, `project_id`/Dateipfade jetzt auf
   `agent-control-bridge` korrigiert (war ursprünglich noch mit dem alten
   Namen erstellt, dann nie ausgeführt). Bereit zum Start. Macht
   `scripts/integration_readonly.py` projektparametrisierbar + fügt
   Pre-Flight-Head-Check hinzu — Vorbereitung für den späteren
   Dorfschaft-Piloten, **kein** Zugriff auf das echte Dorfschaft-Repo.
2. **BRIDGE-0038** — spezifiziert, noch nicht gestartet. Periodisches
   Auto-`git pull` für den Web-UI-Server, damit ein künftiger
   `board`-Klon (siehe Abschnitt 3, noch nicht angelegt) automatisch
   Aufträge aus **allen** Projekten/Klonen zeigt, ohne manuelles Pullen.
   Enthält eine notwendige Nebenkorrektur: die Web-UI ist entgegen ihrem
   eigenen Hilfetext „rein lesend" bereits schreibfähig
   (Aktions-Buttons committen echt) — neuer Hintergrund-Pull-Thread
   braucht ein `threading.Lock` gegen die bestehenden Aktions-Endpunkte,
   sonst reales Kollisionsrisiko innerhalb eines Prozesses.

Beide Work-Packages liegen als Dateien vor, noch nicht ins Repo committet
— `git add work-packages/BRIDGE-035.md work-packages/BRIDGE-038.md` steht
noch aus.

---

## 2. Wichtige technische Entscheidungen dieser Sitzung (gesetzt, nicht
erneut aufrollen, außer der Nutzer bringt es selbst wieder auf)

- **Drei getrennte Klone statt Unterordner** für Parallelverarbeitung
  (`claude`/`codex`/optional `board`) — Unterordner in **einem** Checkout
  hätten das Git-Kollisionsproblem (`index.lock`, siehe BRIDGE-031-
  Vorfall `f6b26c2`) nicht gelöst, da Git auf Repo-Ebene arbeitet, nicht
  pro Unterordner. `git worktree` wurde geprüft und verworfen —
  `git_commit()` erzwingt `branch == main`, Git selbst verbietet
  denselben Branch in zwei Worktrees gleichzeitig.
- **„Ein-Auftrag-zur-Zeit" gilt pro `task_prefix`/Projekt, nicht mehr
  global.** War in `ACB-STEUERCHAT-ARBEITSWEISE.md` bisher global
  formuliert — **Doku-Korrektur dazu steht noch aus**, nicht vergessen
  (siehe „Noch zu tun" unten).
- **`task_prefix: BRIDGE` bleibt.** Keine Umstellung auf `ACB-0001`.
- **Dorfschaft-Profil auf `read_only: true` zurückgesetzt** (BRIDGE-034)
  — war zwischenzeitlich bewusst auf `false` gestellt gewesen (Commit
  `69a5d9b`), jetzt wieder read-only für den ersten Piloten. Wichtige
  Einschränkung: das greift technisch **nur** für den separaten
  Beobachtungs-Adapter (`adapter.py`, BRIDGE-011/012) — **keine**
  allgemeine Durchsetzung von `read_only` gegen normale
  `task_class: FEATURE`-Aufträge (bewusst offen, eigenes,
  nicht angefangenes Thema).
- **`task_prefix`-Kollision jetzt fail-closed geprüft** (BRIDGE-034,
  `create_task()`).
- **Review-Unternummern-Schema** (`-R<n>`-Suffix, `READONLY_CHECK` ⇒
  zwingend `permissions: [READ_ONLY]`, fail-closed) — BRIDGE-032,
  vollständig umgesetzt.
- **`registry.machine_name()`/COMPUTERNAME-Autodefault** jetzt an allen
  Audit-Schreibstellen verdrahtet (BRIDGE-031) — Maschine erscheint
  seitdem korrekt in neuen Audit-Einträgen, `result.yaml`,
  `created_by`.
- **Work-Package-Dateinamen-Whitelist-Bug behoben** (BRIDGE-033) —
  `--commit` scheiterte vorher systematisch am Checkbox-Commit
  (4-stellig vs. etablierte 3-stellige Dateinamenskonvention). Bestätigt
  behoben (BRIDGE-033s eigener `run finish --commit` lief danach sauber
  automatisch durch).
- **ChatGPT/Codex-Pilot bewusst noch nicht gestartet.** Nach fachlicher
  Prüfung von ChatGPTs vollem Anforderungskatalog (Executor-Dienst,
  API-Adapter, Locking, Identitätsprüfung) wurde entschieden: für **einen
  einzelnen, von einem Menschen begleiteten** Read-only-Piloten ist das
  meiste davon Überbau, nicht Blocker. Schlanker Gegenvorschlag
  umgesetzt/in Vorbereitung: nur BRIDGE-034 (Profil) + BRIDGE-035
  (Skript-Parametrisierung) — kein Executor-Dienst, kein API-Adapter,
  kein Locking, keine Identitätsverifikation.

---

## 3. Noch zu tun, bewusst benannt statt vergessen

- **Doku-Korrektur „Ein-Auftrag-zur-Zeit" pro Projekt statt global** in
  `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` — reine Textänderung, noch nicht
  gemacht.
- **`board`-Klon** (dritter, neutraler Checkout nur für den Web-UI-
  Server) — besprochen, noch **nicht** angelegt. Bisher läuft der Server
  weiterhin aus `claude` heraus.
- **Codex-WSL-Setup real durchführen** — `ACB_PROJECT_BASE` muss dort
  tatsächlich gesetzt werden, bisher nur besprochen, nie ausgeführt.
- **Realer Zwei-Schreiber-Test** (Codex + Claude Code gleichzeitig,
  echte Pushes gegen denselben Remote) — die Retry-Logik (BRIDGE-029)
  existiert, wurde aber nie unter echter Last mit zwei realen Prozessen
  geprüft. Vor dem ersten echten parallelen Doppellauf empfohlen, nicht
  danach.
- **Reste des alten `E:\_DEV\Codex-Control-Bridge`-Ordners** auf HAM11
  und DES11 — funktional bedeutungslos, Aufräumen bei Gelegenheit.
- **WSL-Worktree-Pfad für den Dorfschaft-Piloten** weiterhin nicht
  bestätigt (`/mnt/e/_DEV/Dorfschaft-worktrees/AP15-RP2-HAM01`, laut
  ChatGPT „voraussichtlich", nie verifiziert).

## 4. Nicht von selbst anfangen bei

- Kein echter `DORF-*`-Pilotauftrag, bevor BRIDGE-0035 durch ist **und**
  der WSL-Pfad bestätigt wurde.
- Keine allgemeine `read_only`-Durchsetzung für alle `task_class`-Werte
  bauen (eigenes, bewusst zurückgestelltes Thema).
- Kein Linux-Executor-Dienst, kein API-/MCP-Steueradapter für ChatGPT,
  kein Auftrags-Locking, keine Actor-Identitätsverifikation — alles
  bewusst als „für den Piloten nicht nötig" eingeordnet, nicht als
  „vergessen".
- `task_prefix: BRIDGE` nicht erneut zur Debatte stellen, außer der
  Nutzer bringt es selbst wieder auf.
