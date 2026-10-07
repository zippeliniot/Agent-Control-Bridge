# ACB - Uebergabe v16 (Stand 2026-10-07, Zusammenfuehrung zweier parallel gelaufener Steuerchats)

**Repo-HEAD bei Erstellung:** 20d0b87 | **Tests:** 576/576 gruen (unabhaengig frisch nachgelaufen,
nicht nur aus Footern uebernommen)
**Fuer den neuen Steuerchat:** docs/ACB-STEUERCHAT-STANDARDSTART.md, docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md
(V2.1), docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md (neu seit 0083) und diese Datei. v15 nicht
loeschen (Historie).

**Hinweis zu dieser Version:** v15 (BRIDGE-0079 BLOCKED) und der tatsaechliche weitere Verlauf
(BRIDGE-0080 bis 0086) liefen in zwei getrennten Steuerchats parallel. v16 fuehrt beide zusammen - der
Browser-Chat, der v15 geschrieben hat, hatte den Fortschritt von 0080-0086 bis zur Erstellung dieser
Datei nicht gesehen und mehrfach Planung (Checkpoint-Register) vorgeschlagen, die in der Zwischenzeit
bereits umgesetzt war. Ab jetzt nur noch EIN Steuerchat fuer ACB.

## 1. Was sich seit v15 geaendert hat

**BRIDGE-0079-Entscheidung: Option 2 (Konsolidierung verworfen).** `_sync_claim_commit` bleibt
bestehen, wie in v14 bereits empfohlen. Task formal `task_archive`t ohne Code-Aenderung
(`results/BRIDGE-0079/RUN-01/result.yaml`: `status: BLOCKED`, Grund im Summary-Feld). Toter
Whitelist-Eintrag `kind="claim"` in `expected_git_files` bisher **weder entfernt noch genutzt** -
keine neue Entscheidung dazu getroffen, bleibt offen (siehe §6).

**BRIDGE-0080 (Web-UI Projekt-Spalte) umgesetzt und abgeschlossen** - `board_payload()`s `other`-Liste
nutzt jetzt `_board_project()` wie die Gesamtuebersicht, beide Tabellen konsistent auf `task_prefix`.

**RAG-Infrastruktur: Grundgeruest vollstaendig umgesetzt (0081-0086), noch NICHT die eigentliche
Retrieval-Pipeline.** Alle sechs Auftraege mit `depends_on`-Kette 0080->0081->...->0086, jeweils
"April-Entscheidung 07.10." als Anlass dokumentiert:

- **0081**: Schema-Felder `rag_used_since` (Task) und `rag_enabled`/`rag_index_repo` (Projekt) +
  `profiles.write_profile()` (atomares Schreiben, fail-closed bei Schemafehler) + neuer Whitelist-`kind=
  "project_settings"` + Web-Endpunkte `GET/POST /api/project/<id>/settings`. **`rag_used_since` ist
  reserviert fuer eine kuenftige Retrieval-Pipeline, aktuell ueberall `null`.**
- **0082**: `Store.last_machine_for_project()` (liest `audit.jsonl` rueckwaerts) + `gitops.rag_index_sync()`
  (`git_pull` + fail-soft `git lfs pull`) + Verdrahtung in `run start`. **Pfadannahme bei Erstellung
  falsch** (zwei Ebenen ueber dem Checkout) - durch 0083 korrigiert.
- **0083**: **Pfadkorrektur** - `rag-index` ist fuenfter Geschwisterklon neben `board`/`dev`/`claude`/
  `codex` (`E:\_DEV\Agent-Control-Bridge\rag-index`), nicht ausserhalb der Topologie. `docs/architecture/
  machines.md` entsprechend ergaenzt. Dazu `rag_prereqs.check()` (reine Erkennung: Ollama erreichbar,
  Modell vorhanden, Index-Klon vorhanden - nie werfend, nie blockierend) + Anzeige in `run start` +
  neue Doku `docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md`. **Weiterhin offene Bestaetigung an
  April:** Klonname `rag-index` ist Vorschlag, noch nicht gegengeprueft; Klon muss auf HAM11/DES11
  tatsaechlich noch angelegt werden (`git clone zippeliniot/acb-rag-index` -> `rag-index`-Pfad), sonst
  liefert der Sync nur "kein Repo am Pfad" (fail-soft, kein Absturz, aber wirkungslos).
- **0084**: `scripts/rag-setup.ps1` - erkennt fehlende Voraussetzungen, installiert **nur nach
  expliziter Mensch-Bestaetigung** (nie automatisch). **Ungetestet in dieser Cloud-Umgebung** (kein
  `pwsh`) - nur durch Review geprueft, erster echter Lauf auf HAM11/DES11 steht aus, ausdruecklich
  offen vermerkt im eigenen Task.
- **0085**: Nachbesserung - `rag-setup.ps1` setzt `OLLAMA_MODELS` auf `E:\_DEV\ollama-models` **vor**
  der Installation (nur wenn noch nicht gesetzt), da der erste echte Lauf auf HAM11 Modelle auf `C:`
  installiert haette. Dazu `rag-ollama-inventory.ps1` (reine Erkennung/Auflistung von Mehrfach-
  Installationen) - **Loeschung bleibt bewusst manueller, von April bestaetigter Schritt, nicht
  automatisiert.** Unklar aus den Unterlagen, ob die auf HAM11 tatsaechlich vermutete
  Doppelinstallation inzwischen bereinigt wurde - **mit April klaeren, nicht annehmen.**
- **0086**: Nachbesserung - `rag-setup.ps1` unterscheidet jetzt "installiert" (winget/Pfad-Check) von
  "erreichbar" (HTTP); bei installiert-aber-nicht-erreichbar wird der vorhandene Dienst gestartet statt
  erneut `winget install` auszufuehren (verhinderte vorher eine unnoetige Re-Installation auf HAM11,
  als der Dienst beim Pruefzeitpunkt zufaellig nicht lief).

**Ausdruecklich NICHT Teil von 0081-0086 (in jedem Auftrag wiederholt festgehalten):** die eigentliche
Retrieval-/Injection-Pipeline (`rag query`, das tatsaechlich eine Kontextdatei fuer den naechsten
Steuerchat liefert) und das Quellen-Manifest (`rag/sources.yaml` + Coverage-Check) sind **komplett
unangetastet.** Bisher existiert nur die Infrastruktur drumherum (Flags, Pfade, Erkennung, Installation),
kein tatsaechlicher Such-/Embed-/Retrieval-Mechanismus.

**Governance-Ruecklage:** BRIDGE-0084, -0085, -0086 sind `COMPLETED`, aber weiterhin
`WAITING_FOR_COPY_TO_CONTROL` - die Web-UI-Aktion (`copied`+`archive`) steht fuer alle drei noch aus.

## 2. G-Status
Unveraendert zu v15 (G0-G5 wie dort, G6 weiterhin nicht konzipiert).

## 3. Strukturelle Befunde (kumulativ aus v14/v15, durch 0081-0086 ergaenzt)
- (unveraendert aus v14/v15:) `gitops.git_commit`s Ganzbaum-Whitelist-Scan vor jedem Rebase-Versuch -
  `claim.py` bleibt bewusst separat, NICHT auf `gitops.git_commit` umstellen (zweifach belegt, siehe v15).
- **Neu:** `gitops.py` kennt jetzt zwei weitere `kind`-Werte neben `claim`: `project_settings`
  (`projects/<id>/project.yaml`, exakter Pfad) - folgt demselben Whitelist-Muster, aber ueber den
  regulaeren `gitops.git_commit`-Pfad (nicht isoliert wie `claim`), da Projekt-Settings keine
  Parallelitaets-/Dirty-Tree-Problematik wie Claims haben.
- **Neu:** Vier-Wege-Topologie ist jetzt faktisch eine **Fuenf-Wege-Topologie** (`board`/`dev`/`claude`/
  `codex`/`rag-index`), `docs/architecture/machines.md` ist die SSOT dafuer - jede kuenftige Pfadannahme
  gegen diese Datei pruefen, nicht neu herleiten (genau das ist in 0082 schiefgelaufen).
- **Neu:** `rag_prereqs.check()` und `rag_index_sync()` sind beide bewusst fail-soft/nie-werfend
  (gleiches Muster wie `gitops.git_pull`/`git_fetch`) - RAG-Abwesenheit blockiert nie einen normalen
  ACB-Auftrag, zeigt nur fehlende Voraussetzungen an.

## 4. Arbeitsweise (unveraendert, siehe v12 §3 / v13 §4 / v14 §4 / v15 §4)
Frischer Klon vor jeder Pruefung, echter Diff statt Selbstauskunft, Haken/HEAD/Suite/Verhalten pruefen,
jedes im Lauf behauptete Befund-Zitat gegen den echten Code nachschlagen, nie selbst ins Repo schreiben,
Governance-Aktionen nie selbst ausfuehren, Gegenbeweis-Experiment vor Code-Aenderung wenn pruefbar.
**Neu bestaetigt in 0082/0083: eine Pfad-/Strukturannahme, die nicht gegen eine bestehende SSOT-Doku
(hier `machines.md`) geprueft wurde, war falsch und musste nachgebessert werden - solche Annahmen
immer zuerst gegen vorhandene Dokumentation pruefen, nicht herleiten.**

## 5. Nicht von selbst anfangen bei (geklaert, nicht erneut hinterfragen)
(unveraendert aus v14/v15, zusaetzlich:)
- BRIDGE-0079-Entscheidung ist gefallen (Option 2) - nicht erneut vorschlagen, `_sync_claim_commit`
  auf `gitops.git_commit` umzustellen, ausser April bringt es selbst wieder auf.
- RAG-Installationsmechanik ist bewusst "Erkennung automatisch, Installation nur nach Mensch-Klick" -
  nicht versuchen, das in einen vollautomatischen Mechanismus umzubauen, das war eine explizite
  April-Entscheidung (BRIDGE-0084).
- `rag-index` als fuenfter Geschwisterklon (nicht aussserhalb der Topologie) ist die korrigierte,
  gueltige Annahme (BRIDGE-0083 Teil A) - nicht auf die in 0082 verworfene Zwei-Ebenen-Annahme
  zurueckfallen.

## 6. Offene Punkte - in dieser Reihenfolge

1. **Governance nachholen:** BRIDGE-0084, -0085, -0086 im Web-UI `copied`+`archive`n - stehen seit
   `COMPLETED` noch aus.
2. **Klaeren mit April:** ist der `rag-index`-Klon auf HAM11/DES11 tatsaechlich schon angelegt? Ist
   die vermutete Ollama-Doppelinstallation auf HAM11 inzwischen bereinigt (0085 lieferte nur
   Erkennung, keine automatische Loeschung)? Beides nicht aus den Unterlagen ablesbar, nicht annehmen.
3. **Toter Whitelist-Eintrag `kind="claim"`** (seit BRIDGE-0079 unveraendert offen) - entfernen oder
   bewusst als zukuenftige Reserve stehenlassen, einmal final entscheiden.
4. **Retrieval-/Injection-Pipeline spezifizieren** (das eigentliche `rag query`) - bisher nur
   Infrastruktur drumherum existiert, keine tatsaechliche Such-/Kontext-Lieferung.
5. **Quellen-Manifest (`rag/sources.yaml`) + Coverage-Check** - vom Browser-Chat konzeptionell
   vorbereitet (automatischer Vorschlag aus ACB-Standardpfaden, Checkbox-Bestaetigung im Web-UI,
   Hash-basierter inkrementeller Abgleich, Chunking-Regeln pro Dateityp), noch nicht als Auftrag
   spezifiziert oder umgesetzt.
6. **Mehrprojekt-Parallelitaet** - Ziel laut April (07.10., Browser-Chat): ACB soll beliebige Projekte
   mit unterschiedlichen Executors (Claude Code, Codex, weitere) parallel steuern, RAG darf dabei kein
   Engpass sein. Konzept vorbereitet (ein Index-Repo mit Unterordner pro `project_id` statt N
   getrennter Repos, Push-Retry fuer parallele Builds), noch nicht spezifiziert/umgesetzt. Bisher
   existiert nur ein Index fuer `agent-control-bridge` selbst.
7. **RAG-Status-Seite im Web-UI** - zentrale Oberflaeche, die 1-6 zu einem sichtbaren Status + einem
   Update-Button buendelt (kein Script/keine Merkliste fuer April). Teilweise durch die
   Settings-Seite aus 0081 vorbereitet, aber noch kein vollstaendiges Status-Dashboard.
8. (unveraendert aus v14 §6, Punkte 2-4:) Generische Steuerchat-Vorlage braucht `OpenIssue`-Referenz,
   FK00/Dorfschaft-Einbindung noch zu klaeren, Draft-Modus weiterhin offen, WinError 10053 harmlos.

## 7. Referenz: Checkpoint-Register aus dem Browser-Chat

Der Browser-Chat hat parallel ein Checkpoint-Register fuer die Punkte 5-7 oben erarbeitet
(acht Abschnitte: Projekt-Flag, Auftrags-Flag, Prerequisite-Check, Update-Aktualitaets-Check,
Machine-Switch-Trigger, Mehrprojekt-Parallelitaet, Quellen-Manifest, RAG-Status-Seite). Abschnitte
1-5 sind durch 0081-0083 inzwischen umgesetzt (teils mit abweichenden Detailentscheidungen, siehe
§1) - Abschnitte 6-8 sind der tatsaechlich noch offene Rest. Datei liegt bei April als
`BRIDGE-RAG-Flag-Checkpoints.md`, nicht im Repo versioniert - bei Bedarf fuer Punkt 5/6/7 oben als
Ausgangspunkt nutzen, aber gegen den jetzigen Code-Stand gegenpruefen, nicht ungeprueft uebernehmen.
