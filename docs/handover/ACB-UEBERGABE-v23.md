# ACB - Uebergabe v23 (Stand 2026-10-10)

**Repo-HEAD bei Erstellung:** `5d5afc3ae36048c5b65bedc11aee2062c41db181` (`5d5afc3`) | **Tests:**
607/607 (12 Subtests) - frisch nachgelaufen in dieser Sitzung gegen genau diesen HEAD, nicht
uebernommen.

**Fuer den neuen Steuerchat:** `docs/ACB-STEUERCHAT-STANDARDSTART.md`, diese Datei. v19-v22 nicht
loeschen (Historie).

**Anlass dieser Version:** Kontextfenster der vorherigen Steuerchat-Sitzung voll. v23 schliesst
BRIDGE-0101/BRIDGE-0102 und ISSUE-0006 ab, dokumentiert zwei neue Dauerregeln und uebernimmt die
unveraenderten offenen Punkte aus v22.

## 1. Neu in dieser Version: abgeschlossen seit v22

### 1a. `BRIDGE-0101` (ISSUE-0005, Teil A+B) - ARCHIVED, verifiziert

Teil A: `push_mode: draft`-Durchsetzung in `src/bridge/cli.py` (`task create`/`run start`/
`run finish`/`task copied`/`task archive` lehnen bei `draft` fail-closed ab, verweisen auf
`bridge draft write`). Code ist korrekt und getestet - **aber nicht produktiv aktiv**: nach
kurzem Test mit `agent-control-bridge` auf `push_mode: draft` zeigte sich ein
Selbstbezueglichkeits-Problem (`task create` fuer ACBs eigene Weiterentwicklung war dadurch
selbst blockiert, keine Web-UI-Alternative zum Anlegen neuer Tasks vorhanden). April hat
`projects/agent-control-bridge/project.yaml` direkt per PowerShell (nicht ueber einen BRIDGE-Task,
um den Deadlock zu vermeiden) zurueck auf `push_mode: direct` gesetzt (Commit `2ea9d87`). **Der
Durchsetzungscode selbst bleibt gueltig und einsatzbereit fuer ein externes Pilotprojekt** (z. B.
`wetter-app`), nur `agent-control-bridge` nutzt ihn (noch) nicht.

Teil B: `src/bridge/importer.collect_git_info()` liefert `changed_files`/`base_head` jetzt
projektbezogen (`filter_project_files()`, neu) - Pfade anderer Projekte werden aus dem Diff
herausgefiltert statt nur zusaetzlich mitgelistet. Bewusst nicht geloest: `audit/audit.jsonl` ist
eine gemeinsam genutzte Append-only-Datei, pfadbasiertes Filtern kann sie keinem Projekt eindeutig
zuordnen - im Code und im WP dokumentiert, kein Regressionsproblem.

**ISSUE-0005 bleibt bewusst OPEN** - Teil B ist umgesetzt, aber `push_mode: draft` ist bei keinem
der sieben Projekte aktiv (M1 Single-Writer weiterhin nirgends scharf). Nicht mit einem
abgeschlossenen Issue verwechseln.

### 1b. `BRIDGE-0102` (`wp-lint.py`) - ARCHIVED, verifiziert

Neues `scripts/wp-lint.py`: prueft fail-closed vor Auftragsuebergabe, dass (1) der WP-Kopf eine
nichtleere `Modell / Denkstufe`-Zeile mit gueltiger Stufe hat, (2) die Staging-YAML gegen
`schemas/task.schema.yaml` validiert und `model`/`reasoning_level` nichtleer sind, (3) WP-Angabe
und YAML-Angabe exakt uebereinstimmen (genau die Luecke, die bei BRIDGE-0101 zum `BLOCKED` fuehrte),
(4) die `bridge_task_id` aus der YAML im WP-Titel vorkommt. `.claude/commands/acb-auftrag.md` §0
und `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` Abschnitt 3 referenzieren das Skript (beide Referenzen
nach dem Merge verifiziert, nicht nur behauptet).

### 1c. `ISSUE-0006` (BRIDGE-0092-Luecke) - angelegt, OPEN, verifiziert in `origin/main`

Dokumentiert abschliessend: `BRIDGE-0092` existiert nicht als formaler Auftrag (kein
`tasks/BRIDGE-0092/`, kein `work-packages/BRIDGE-092.md`), der reale Commit `7fa95f9` lief ohne
Auftrags-Zyklus, wird aber an drei Stellen als abgeschlossen zitiert (v19 Zeilen 5/33/44/74,
ISSUE-0003:16, BRIDGE-097.md:20). **Entscheidung (April, 09.10.2026): keine rueckwirkende
Nachbuchung** - die drei Zitierstellen bleiben unveraendert, das Issue dokumentiert die Luecke nur.
Commit `5d5afc3`, verifiziert per `git ls-tree origin/main` (nicht per `reset --hard`, das zeigt
untracked Dateien faelschlich als vorhanden an - Lektion aus einem eigenen Fehler dieser
Sitzung, siehe §2 Punkt 4).

## 2. Neue Dauerregeln dieser Sitzung (verbindlich, nicht erneut hinterfragen)

1. **Immer Empfehlung ausgeben:** sobald dem Steuerchat mehrere Optionen vorgelegt werden, muss
   er von sich aus eine konkrete Empfehlung mit kurzer Begruendung mitliefern, nicht nur die
   Optionen aufzaehlen.
2. **Eindeutige Dateinamen bei jeder Neulieferung:** wird eine Datei nach einer Korrektur erneut
   an April geliefert, bekommt sie einen neuen, unterscheidbaren Dateinamen (z. B. `-v2`-Suffix) -
   Windows haengt bei gleichem Namen sonst automatisch `(1)` an, was zu veralteten Kopien fuehrt,
   die PowerShell-Befehle sonst unbemerkt gegen die falsche Datei laufen lassen.
3. **`wp-lint.py` vor jeder WP-Lieferung lokal selbst aufrufen** (seit BRIDGE-0102 verfuegbar),
   statt sich nur auf Claude Codes eigene Pruefung zu verlassen.
4. **Verifikation von "Datei ist im Repo" ausschliesslich per `git ls-tree origin/main -- <pfad>`
   (oder `git show origin/main:<pfad>`), niemals per `ls` nach `git reset --hard origin/main`.**
   `reset --hard` setzt nur getrackte Dateien zurueck und laesst untracked Dateien unberuehrt -
   eine lokal erzeugte, nie gepushte Datei erscheint danach im Arbeitsverzeichnis exakt so, als
   waere sie Teil des Remote-Stands. Fehler dieser Sitzung (§1c): ISSUE-0006 wurde faelschlich
   als "bereits im echten Repo" gemeldet, bevor es tatsaechlich gepusht war.

## 3. Aus v22 vollstaendig uebernommen (unveraendert, nicht umgesetzt)

### 3a. Alte Konfliktmarker in `audit/audit.jsonl` (v22 §1b) - entschieden: Option 1 (nichts tun)

April hat sich fuer Option 1 entschieden (nur dokumentieren, kein Korrektur-Commit, kein neues
Issue). Begruendung (diese Sitzung, durch Code-Pruefung bestaetigt statt nur behauptet): alle drei
realen Parser im Code (`store.py:last_transition_at`, `store.py:last_machine_for_project`,
`cli.py` Audit-Lesecode ~Zeile 552/814) umschliessen `json.loads(line)` bereits mit
`try/except JSONDecodeError: continue` - die zwei defekten Zeilen (824/839) werden also bereits
heute von jedem echten Parser im Repo klaglos uebersprungen. Die in v22 geaeusserte Sorge ("jedes
Tool, das zeilenweise JSON parst, bricht ab") trifft auf den tatsaechlichen Code nicht zu. Damit
abgeschlossen, keine weitere Aktion.

### 3b. Drei-Schichten-Modell: Umsetzungsplan (v22 §2c) - weiterhin offen, naechster Punkt

### 3c. Projekt-ID-Dropdown (v22 Punkt 5) - weiterhin offen

### 3d. Hamburger-Menue-Scope (v22 Punkt 6) - weiterhin offen, mit April zu klaeren

### 3e. `--machine`-Regel in ARBEITSWEISE.md (v22 Punkt 7) - weiterhin offen

### 3f. Neu seit dieser Sitzung (Punkt 8, von April als Erweiterung der Liste benannt):
RUNNING/CLAIMED im Board sichtbar machen, mit einer neuen Spalte rechts neben "Maschine", die
unterscheidet, ob der Akteur **Steuerchat** oder eine **Coding-Einheit** war. "Maschine" bleibt
dabei die physische Einheit (HAM11/DES11) - die neue Spalte ist eine zusaetzliche, orthogonale
Unterscheidung, kein Ersatz.

## 4. G-Status
Unveraendert zu v16-v22 (G0-G5, G6 weiterhin nicht konzipiert).

## 5. Offene Punkte - in dieser Reihenfolge

1. **Drei-Schichten-Umsetzungsplan bestaetigen oder korrigieren** (v22 §2c, 5-Schritt-Vorschlag:
   Decision-Log-CLI/Store -> Symbol-/Datei-Graph Traegerfrage+Indexer -> Context-Assembler-Schema
   -> Routing-Feld -> RAG als vollwertiger Fallback).
2. **Projekt-ID-Dropdown** statt Freitextfeld im Stammdaten-Block (Quelle:
   `profiles.list_profiles(store.root)`, noch nicht ueber die Web-UI-API exponiert).
3. **Hamburger-Menue-Scope klaeren** (Inhalt/Layout noch unentschieden) - mit April abstimmen,
   bevor ein Auftrag abgeleitet wird.
4. **`--machine`-Regel** in `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` nachtragen (Steuerchat soll bei
   eigenen CLI-Aufrufen immer explizit `--machine browser-claude` setzen statt `platform.node()`
   den Default bestimmen zu lassen).
5. **RUNNING/CLAIMED im Board sichtbar machen** mit neuer Spalte "Akteur" (Steuerchat /
   Coding-Einheit) neben der bestehenden Spalte "Maschine" (physische Einheit bleibt unveraendert).

**Empfehlung fuer den naechsten Schritt:** Punkt 1 (Drei-Schichten-Umsetzungsplan) zuerst, weil er
das grundlegende RAG/Decision-Log/Graph-Fundament betrifft, auf das Punkte 2-5 (UI-Details) keinen
Einfluss haben - die Reihenfolge innerhalb der UI-Punkte (2-5) ist dagegen beliebig vertauschbar,
ohne Abhaengigkeiten untereinander.

**Naechste freie BRIDGE-ID: `BRIDGE-0103`** (0101 und 0102 verbraucht). **Naechste freie Issue-ID:
`ISSUE-0007`** (0006 bereits vergeben und gepusht) - vor jeder Neuvergabe zuerst
`bridge issue list --include-closed` gegen den frischen `origin/main`-Stand laufen lassen.

## 6. Nicht von selbst anfangen bei (geklaert, nicht erneut hinterfragen)
(unveraendert aus v16-v22:) `machine: vm` in alten Audit-Eintraegen ist erklaert, bewusst nicht
korrigiert. Kein neues Gate fuer die Drei-Schichten-Architektur (BRIDGE-0096, entschieden) - nur
die Umsetzungsreihenfolge ist offen. **Neu in v23:** Konfliktmarker in `audit.jsonl` (Zeilen
824/839) sind entschieden dokumentiert, nicht korrigiert (§3a) - nicht erneut als offenes Problem
vorlegen. `push_mode: draft` fuer `agent-control-bridge` ist bewusst zurueckgesetzt (§1a) - nicht
ohne neue Web-UI-Task-Erstellung erneut aktivieren.

## 7. Referenz
v20-v22 bleiben Primaerquellen im Detail. v23 fasst die seit v22 abgeschlossenen Punkte zusammen
(BRIDGE-0101, BRIDGE-0102, ISSUE-0006) und uebernimmt die unveraenderten offenen Punkte 4-8 aus
v22 als neue Punkte 1-5.
