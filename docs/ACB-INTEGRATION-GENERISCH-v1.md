# ACB — Projektintegration (generisch, v1)

Stand: 2026-09-23. Gilt für jedes Projekt, das über die Agent Control Bridge (ACB) gesteuert wird.
Setzt kein Wissen über andere Projekte voraus. Platzhalter in spitzen Klammern (`<id>`) sind
Schreibweise dieses Dokuments: Der Steuerchat setzt vor jeder Ausgabe an April konkrete Werte ein,
nie Platzhalter in PowerShell.

## 1. Prinzip

- **Steuerchat** (Browser-Claude): plant, schneidet Aufträge zu, prüft Ergebnisse. Schreibt nie ins Repo, hat keinen Push-Zugang.
- **Ausführungsinstanz** (Claude Code, Windows-nativ; Codex nur, wenn das Profil es festlegt): setzt Aufträge um, committet, pusht.
- **April** kontrolliert, legt Dateien ab, führt Governance-Aktionen aus (Web-UI/CLI).
- **GitHub** ist der einzige Austauschkanal und die einzige Wahrheit (SSOT).
- ACB enthält keine Projektlogik. Projektspezifisch ist nur das Profil `projects/<id>/project.yaml`.

**Zwei Repositories pro Projekt — nie verwechseln:**

| | ACB-Repo (Koordination) | Zielrepo (Produkt) |
|---|---|---|
| GitHub | `zippeliniot/Agent-Control-Bridge` | eigenes Repo des Projekts |
| Inhalt | Profil, Tasks, Results, Audit, Work-Packages | Produktcode |
| Lokal | `E:\_DEV\Agent-Control-Bridge\projects\<repo>` (ein Klon je Projekt) | `<Basis>\<repository>` (Basis aus `registry.yaml`, aktuell `E:\_DEV`) |

Projektaufträge ändern **nie** den ACB-Kern (`src/`, `schemas/`, `docs/`, `tests/`). Im ACB-Klon
entstehen nur Store-Dateien, die Work-Package-Datei und ihre Haken.

**Maschinen:** HAM11 und DES11 sind physisch getrennt (`E:` nur namensgleich). Vor jedem Wechsel
muss alles gepusht sein (`scripts\handover-check.ps1`). Die Web-UI (`webui serve`) läuft nur im
`board`-Klon, nie in einem Projektklon.

## 2. Einmalige Einrichtung eines Projekts

| # | Schritt | Wer |
|---|---|---|
| 1 | `project_id` (Kleinbuchstaben, Bindestrich) und `task_prefix` (1–8 Großbuchstaben, eindeutig) festlegen. Bestehende Präfixe zeigt `project list`; bei Kollision lehnt `task create` fail-closed ab. | Steuerchat + April |
| 2 | Zielrepo lokal auschecken unter `<Basis>\<repository>`, Branch `main`, Working Tree sauber. Das Verzeichnis muss real existieren, die Bridge legt es nicht an. | April |
| 3 | Profil `projects/<id>/project.yaml` anlegen (Vorlage unten), mit `project validate` prüfen, im ACB-Repo committen und pushen. | Steuerchat liefert Datei, April committet |
| 4 | ACB-Klon für das Projekt anlegen und `.venv` einrichten (unten). | April |
| 5 | Im Zielrepo ein eigenes `CLAUDE.md` mit Regeln für den Executor anlegen (Scope, Tests, Fail-closed). Das Profil schützt nur begrenzt (siehe unten). | Steuerchat entwirft, April committet im Zielrepo |
| 6 | Neues claude.ai-Projekt/Chat mit dem Steuerchat-Startprompt (`ACB-STEUERCHAT-START-GENERISCH-v2.md`) anlegen. Fertig befüllt per `scripts\steuerchat-vorlage.py --project-id <id>`. | April |

**Profil-Vorlage (schreibend):**

```yaml
schema_version: "1.0"
kind: bridge_project_profile
project_id: <id>
description: <ein Satz: was das Projekt ist>
repository: <Verzeichnisname des Zielrepos unter der Basis>
default_branch: main
task_prefix: <PRAEFIX>
read_only: false
executor: claude-code
controller: human
github_repo: <org>/<repo>
allowed_machines: [HAM11, DES11]
git_policy:
  allow_push: true
  allow_merge: false
  allow_force_push: false
  protected_branches: [main]
test_policy:
  command: null
  required: false
handover_policy:
  branch: main
  require_clean: true
migration_policy:
  allow_production: false
```

Unbekannte Felder lehnt das Schema ab (`additionalProperties: false`), `project_id` muss dem
Verzeichnisnamen unter `projects/` entsprechen. `test_policy.command` mit dem echten Testbefehl
füllen, sobald das Zielrepo Tests hat, und dann `required: true` setzen.

**Was hart erzwungen wird und was nicht:** `read_only: true` schaltet auf eine reine Lese-Allowlist
um (hart, im Code). `allowed_machines`, `git_policy`, `migration_policy` sind aktuell reine
Absichtserklärungen ohne Laufzeitsperre. Schutz für `--force`, Merge, Deploy entsteht durch das
Auftragsprofil (`permissions`), die `--commit`-Whitelist der CLI und das `CLAUDE.md` im Zielrepo.

**ACB-Klon anlegen (WO: PowerShell, konkrete Werte vom Steuerchat):**

```powershell
git clone https://github.com/zippeliniot/Agent-Control-Bridge.git E:\_DEV\Agent-Control-Bridge\projects\<repo>
cd E:\_DEV\Agent-Control-Bridge\projects\<repo>
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Ablauf pro Auftrag

**IDs:** Auftrag `<PRAEFIX>-<4 Ziffern>` (z. B. `ABC-0001`), Work-Package-Datei
`work-packages/<PRAEFIX>-<3 Ziffern>.md` (`ABC-001.md`). Die höchste vergebene ID ermittelt der
Steuerchat selbst aus `tasks/` und `work-packages/`, nie aus einem Dokument.
**Ein Auftrag zur Zeit:** Ein neuer Auftrag wird erst zugeschnitten, wenn der vorige `ARCHIVED`
und vom Steuerchat verifiziert ist.

**Schritte:**

1. **Steuerchat** prüft frisch: Vorgänger `ARCHIVED`, nächste ID, Zielrepo-HEAD.
2. **Steuerchat liefert als Download:** Work-Package, Staging-YAML, PowerShell-Ablageblock, Claude-Code-Anweisung.
3. **April** legt WP nach `work-packages\` und Staging-YAML nach `tasks\incoming\` im ACB-Klon ab; nur das WP wird committet und gepusht (`tasks/incoming/` ist gitignored).
4. **Claude Code** wird im ACB-Klon geöffnet und bekommt die Anweisung (unten). Es arbeitet das WP ab: `task create` → `run start --commit` → Teile mit Haken je Teil, jeweils committen und pushen → `run finish --commit --summary` → push.
5. **Steuerchat prüft** (Abschnitt 4).
6. **April** führt in der Web-UI oder CLI `Kopiert → Review` und `Archivieren` aus. Steuerchat verifiziert `ARCHIVED` per frischem Klon.

### 3.1 Staging-YAML (Vorlage)

```yaml
schema_version: '1.0'
kind: bridge_task
bridge_task_id: <PRAEFIX>-<4 Ziffern>
project_id: <id>
title: <Einzeiler>
description: 'Details: work-packages/<PRAEFIX>-<3 Ziffern>.md'
task_class: FEATURE            # INIT ARCHITECTURE FEATURE BUGFIX REFACTOR TEST DOCS INTEGRATION READONLY_CHECK CHORE
repository: <repository>
branch: main
git:
  expected_head: EXPECTED_HEAD
  allowed_changed_files: []    # Scope-Whitelist des Zielrepos, wenn eng begrenzt
model: <Modell>
reasoning_level: LOW           # LOW | MEDIUM | HIGH
executor: claude-code
permissions:
- WORKTREE_WRITE
- TEST_EXECUTION
- GIT_PUSH
acceptance_criteria:
- <prüfbares Kriterium>
status: CREATED
created_at: '<Datum>T00:00:00Z'
created_by: browser-claude
```

Regeln: `permissions` minimal (Standard read-only; `MERGE`, `DEPLOY`, `DATABASE_WRITE`,
`FORCE_PUSH` nur ausdrücklich). Berechtigungen sind nach `task create` unveränderlich, `GIT_PUSH`
muss also vorab drinstehen. `model` und `reasoning_level` sind immer gesetzt (niedrigste
ausreichende Stufe), im WP und im YAML.

**`expected_head` = HEAD des ACB-Klons** (Executor ersetzt `EXPECTED_HEAD` durch
`git rev-parse HEAD` im ACB-Klon; steht schon ein SHA drin, wird er nicht geändert). Grund:
`run finish` bildet `commits` und `changed_files` im ACB-Klon gegen diesen Wert. Der Ausgangs-HEAD
des Zielrepos ist eine Vorbedingung im WP, nicht `expected_head`.

### 3.2 Work-Package (Vorlage)

```markdown
# <ID> - <Titel>

| Feld | Wert |
|---|---|
| bridge_task_id | <ID> |
| project_id | <id> |
| Typ / Klasse | <task_class> |
| Rechte | <permissions> |
| **Modell / Denkstufe** | **<Modell> / <Stufe>** (ein Satz Begründung) |
| depends_on | <ID oder keine> |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Zwei Repos: (1) ACB-Klon <Pfad> nur für Task/Result/Audit/diese WP-Datei.
> (2) Zielrepo <Pfad>, Branch main.
> MODELL-GATE: erste Antwortzeile "MODELL: <Modell> / DENKSTUFE: <Stufe>". Abweichung = STOPP.

## Ablauf
BR = .venv\Scripts\python.exe src\bridge\cli.py --root <ACB-Klon> --schema-dir <ACB-Klon>\schemas ; Actor = claude-code
1. ACB-Klon: git pull. In tasks\incoming\<ID>.yaml EXPECTED_HEAD durch `git rev-parse HEAD` ersetzen.
   `BR task create tasks\incoming\<ID>.yaml --commit`, dann `BR run start <ID> --actor claude-code --commit`, git push.
2. VORAB Zielrepo: git pull, git status sauber, HEAD muss <SHA> sein. Abweichung = STOPP (CONCEPT_CONFLICT), nichts ändern.
3. Scope nur im Zielrepo: <Dateien>. Im ACB-Klon nur diese WP-Datei (Haken) und Store-Dateien.

## Teil A - <Titel>
<Befund, konkrete Änderung, Prüfung>
- [ ] <Haken je prüfbarem Ergebnis>

## Abschluss
git status muss in beiden Repos sauber sein.
`BR run finish <ID> --status COMPLETED --actor claude-code --commit --summary "<max. 3 Sätze, inkl. HEAD-SHA des Zielrepos>"`, git push.
Ausgabe nur: Footer (Auftrag / Lauf / Status) + max. 4 Zeilen: ACB-HEAD, Zielrepo-HEAD, Befunde.
Unklar oder Stopp-Bedingung: Status BLOCKED, Fehlercode, ein Beweis, aufhören.
```

Nach jedem Teil: Haken im WP setzen, nur die genannten Pfade `git add`, committen, pushen
(kein `git add -A`, nie `--force`). Bei Unterbrechung (Usage-Limit, Fensterwechsel) keine neue ID:
`BR run resume <ID> --actor claude-code`, weiter am ersten offenen Haken.

### 3.3 Anweisung an Claude Code

Der Slash-Befehl `/acb-auftrag` ist nur für `BRIDGE-`-IDs geschrieben und greift bei anderen
Präfixen an einer alten `BRIDGE-`-ID an. Daher gilt für jedes Projekt außer der ACB-Entwicklung:
**in der ersten Anweisung weder `/acb-auftrag` noch die Wörter „Auftrag" oder „acb-auftrag"
verwenden**, sondern wörtlich auf die WP-Datei verweisen. Vorlage (kopierfertig, vom Steuerchat
mit konkreten Werten geliefert):

```
Lies work-packages\<PRAEFIX>-<3 Ziffern>.md im aktuellen Ordner und befolge die Datei wörtlich.

PFLICHT:
1. Jede Zustandsänderung nur über die Bridge-CLI, nie Store-Dateien direkt bearbeiten.
2. Am Ende git push (GIT_PUSH steht im Berechtigungsprofil); ohne Push kann der Steuerchat nichts prüfen. Nie --force.
```

## 4. Prüfung durch den Steuerchat (nie der Selbstauskunft glauben)

Nach jedem Footer, in **frischen** Klons beider Repos (`bash_tool`, nicht `web_fetch`):

1. `task show <ID>`, Status, `model`/`reasoning_level` wie im WP.
2. `result.yaml`: `head`, `commits`, `changed_files` gleich `git diff --name-only <base_head> <head>` (`base_head` aus der `result.yaml` übernehmen).
3. Alle Haken im WP gesetzt; ein ungesetzter Haken trotz erledigter Arbeit wird beim Prüfen mitgezogen.
4. ACB-Klon: `HEAD == origin/main`.
5. **Zielrepo separat klonen**: `result.yaml` kennt nur ein Repository, der Ziel-SHA steht nur im `summary`. SHA verifizieren, Diff gegen den Scope des WP prüfen, Tests bzw. Ersatzprüfung selbst ausführen.
6. Jedes Akzeptanzkriterium einzeln gegen den echten Code prüfen, nicht gegen die Zusammenfassung.

Der Steuerchat führt `run finish`, `task copied` und `task archive` nie selbst aus.

## 5. CLI-Kurzreferenz

Aufruf immer: `.venv\Scripts\python.exe src\bridge\cli.py --root <ACB-Klon> --schema-dir <ACB-Klon>\schemas <befehl>`

| Befehl | Zweck |
|---|---|
| `project list` / `project show <id>` / `project validate <Pfad>` | Profile |
| `task create <Pfad> --commit` | Auftrag aus Staging-YAML anlegen |
| `task show <ID>` / `task list` | Status |
| `run start <ID> --actor <Name> --commit` | Lauf starten |
| `run beat <ID> --actor <Name>` | Heartbeat |
| `run finish <ID> --status COMPLETED --actor <Name> --commit --summary "..."` | Lauf abschließen (nie ohne `--summary`) |
| `run resume <ID> --actor <Name>` | Wiederaufnahme |
| `task copied <ID>` / `task archive <ID>` | Governance (April) |
| `audit show <ID>` / `overview --project <id>` | Diagnose, lesend |

Typischer Zustandsweg: `CREATED → RUNNING → COMPLETED → WAITING_FOR_COPY_TO_CONTROL →
REVIEW_REQUIRED → ARCHIVED`. `COMPLETED` heißt „Ergebnisvertrag erfüllt", nicht „fachlich
freigegeben". Das Board zeigt nur die zwei Wartezustände; laufende Aufträge stehen nicht im Board.
Für den echten Stand `task show` und `audit show` nutzen.

Exit-Codes: `0` Erfolg, `1` fachlicher Fehler (z. B. `base_head` fehlt), `2` Nutzungsfehler,
`3` Git-Whitelist-/Branch-Fehler bei `--commit` (die Store-Aktion bleibt bestehen).

## 6. Grenzen und Regeln

- Fail-closed: bei Unsicherheit (falscher Branch, unerwarteter HEAD, nötige Systemänderung) anhalten, `BLOCKED`, Fehlercode, ein Beweis.
- Keine Erfindungen: Aussagen über den Repo-Zustand (auch von April: „ist gepusht") per frischem Klon prüfen.
- Aufträge anderer Präfixe gehören nicht in diesen Chat und werden nicht mitgeprüft.
- Änderungen am ACB selbst (Skills, Schemas, CLI, diese Doku) laufen als `BRIDGE-`Aufträge im ACB-Steuerchat, nie über ein Projekt.
- Bekannte Struktur-Grenzen: `result.yaml` hat nur ein Repository-Feld (siehe 4.5). Der Slash-Befehl gilt nur für `BRIDGE-` (siehe 3.3).
