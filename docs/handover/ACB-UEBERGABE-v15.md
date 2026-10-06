# ACB - Uebergabe v15 (Stand 2026-10-06)

**Repo-HEAD bei Erstellung:** 4dee1a5 | **Tests:** 536/536 gruen (unveraendert seit 0078 - BRIDGE-0079 hat
nichts implementiert, siehe unten)
**Fuer den neuen Steuerchat:** docs/ACB-STEUERCHAT-STANDARDSTART.md, docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md
(V2.1) und diese Datei. v14 nicht loeschen (Historie).

## 1. Was sich seit v14 geaendert hat

**BRIDGE-0079 begonnen (Claim-Commit-Pfad auf gitops.git_commit konsolidieren, autostash) - BLOCKED,
keine Code-Aenderung im Repo.**

- Vom Steuerchat als Nachbesserung zu 0078 vorgeschlagen: `_sync_claim_commit` (eigener Commit/Push-Pfad in
  `claim.py`) durch den gemeinsamen `gitops.git_commit(kind="claim", autostash=True)` ersetzen.
- **Wichtig: dieser Vorschlag widersprach bereits v14 §3** ("Bei jeder weiteren Aenderung an `claim.py` diese
  Besonderheit beachten, nicht einfach auf `gitops.git_commit` umstellen.") - der Steuerchat hat das beim
  Formulieren des Auftrags uebersehen.
- Claude Code hat vor jeder Umsetzung ein Gegenbeweis-Experiment mit echtem Bare-Repo gefahren (BRIDGE-0078-
  Szenario nachgebaut: neuer Claim + paralleler unversionierter Audit-Eintrag + NFF-Lage) und zwei
  **unabhaengige** Blockaden gefunden, nicht nur eine:
  1. `gitops.git_commit`s Whitelist-Pruefung (Schritt 3) scannt den GANZEN Arbeitsbaum
     (`git status --porcelain --untracked-files=all`) und bricht bei jeder Datei ausserhalb der Whitelist
     sofort ab - lange bevor Schritt 6b (Rebase, wo `autostash` greifen wuerde) erreicht wird.
  2. Selbst wenn Schritt 3 den dirty `audit.jsonl` ignorieren wuerde (scope-begrenzter Status-Scan nur auf
     Whitelist-Pfade): `git rebase` selbst verlangt ohne `--autostash` ebenfalls einen sauberen GESAMTEN
     Arbeitsbaum, nicht nur einen sauberen Index - `autostash` waere also zusaetzlich noetig, nicht alternativ.
  - Beide Fixes zusammen (scope-begrenzter Status-Scan fuer `kind="claim"` + `autostash`) wuerden funktionieren,
    aendern aber eine Stelle, deren Ganzbaum-Scan die Docstring ausdruecklich als **"nicht verhandelbar,
    BRIDGE-024 Sicherheitsentscheid"** bezeichnet.
- **Status: BLOCKED, CONCEPT_CONFLICT. Offene Entscheidung fuer den neuen Steuerchat (siehe §6).**
  Keine Code-Aenderung vorgenommen, Baum sauber, nichts als erledigt markiert.

**BRIDGE-0080 vorbereitet (Web-UI Projekt-Spalte vereinheitlichen), noch NICHT angelegt.**

- Befund: "Offene Auftraege ausserhalb des Boards" zeigt rohes `project_id` (`agent-control-bridge`),
  "Alle Projekte - Gesamtuebersicht" zeigt bereits `task_prefix` (`BRIDGE`) ueber die vorhandene Funktion
  `_board_project()` (`cli.py:601`). April-Entscheidung (06.10.): beide Tabellen auf `task_prefix`
  vereinheitlichen - `webui.py:157` (`board_payload()`) soll `_board_project(store, task)` statt
  `task.get("project_id", "?")` nutzen.
- Work-Package (`work-packages/BRIDGE-080.md`) und Staging-YAML liegen vor, `depends_on: BRIDGE-0079`.
  **`git.expected_head` in der Staging-YAML ist noch Platzhalter** (`SETZEN_VOR_TASK_CREATE`) - vor
  `task create` auf den dann aktuellen HEAD setzen.
- Haengt NICHT inhaltlich an BRIDGE-0079 (anderer Scope, nur `webui.py`/Tests) - `depends_on` ist rein
  sequenziell gesetzt (Parallel-Vermeidungs-Regel), kein technischer Zusammenhang. Kann nach Aufloesung
  von BRIDGE-0079 (in welcher Form auch immer, siehe §6) direkt angelegt werden.

**RAG/Steering-Continuity-Infrastruktur (ausserhalb ACB-Repo) - Grundgeruest steht, nicht angebunden.**

- Neues privates Repo `zippeliniot/acb-rag-index` angelegt, auf HAM11 geklont, Git LFS installiert,
  `*.db`-Tracking aktiv und gepusht (Commit `16e31b7`). LFS-Kontingent 10 GB Storage/Bandbreite, 0 GB genutzt -
  reicht komfortabel.
- **Offen: DES11-Sync** (`git clone` + `git lfs install` auf DES11) noch nicht durchgefuehrt.
- Checkpoint-Register fuer Projekt-/Auftrags-Flags (`rag_enabled` am Projektprofil, `rag_used_since` am
  Auftrag, Prerequisite-Check, Machine-Switch-Trigger) wurde als Dokument erstellt, **ist aber noch kein
  BRIDGE-Auftrag** - weder Schema-Erweiterung noch Web-UI-Formular umgesetzt. Kein `gitops.git_commit`-
  Beruehrungspunkt geplant, der dem BRIDGE-0079-Problem aehnelt (Settings-Formular committet projektweite
  Konfiguration, kein Pendant zur claim.py-Einzelpfad-Problematik - zur Sicherheit bei Umsetzung trotzdem
  gegen §3 (unten) pruefen).

## 2. G-Status
- G0-G5: unveraendert zu v14 (G5-Blocker weiterhin aufgeloest, BRIDGE-0066 Dorfschaft-Pilot weiterhin nicht
  gestartet, gehoert in den Dorfschaft-Steuerchat).
- G6 weiterhin nicht konzipiert.

## 3. Strukturelle Befunde (unveraendert aus v14, durch BRIDGE-0079-Experiment zusaetzlich empirisch bestaetigt)
- `gitops.git_commit` bricht beim kleinsten Fund ausserhalb der Whitelist fuer den jeweiligen `kind` komplett
  ab (`git status --porcelain` scannt den GANZEN Baum, Schritt 2/3, VOR jedem Rebase-Versuch in Schritt 6b).
  Das ist jetzt zweifach belegt: dokumentiert in v14 UND durch ein echtes Bare-Repo-Experiment in BRIDGE-0079
  reproduziert. **Jede kuenftige Idee, `claim.py` auf `gitops.git_commit` umzustellen, muss diesen Fund
  explizit adressieren (scope-begrenzter Status-Scan + autostash, siehe §1), nicht wiederholt uebersehen.**
- `claim`/`renew`/`release` committen weiterhin ueber die isolierte `_sync_claim_commit`-Sequenz in `claim.py`
  (unveraendert seit 0078), brauchen Netzwerkzugriff.
- `expected_git_files` (`gitops.py`) hat weiterhin den ungenutzten `kind="claim"`-Whitelist-Eintrag (totes
  Gleis, siehe v14/BRIDGE-0079-Diskussion) - Entscheidung ueber Entfernen oder Belassen haengt an der
  Entscheidung aus §6.
- (unveraendert aus v13/v14:) `result.yaml` kennt nur EIN Repository; `.acb-writer.lock` root-lokal, gitignored.

## 4. Arbeitsweise (unveraendert, siehe v12 §3 / v13 §4 / v14 §4)
Frischer Klon vor jeder Pruefung, echter Diff statt Selbstauskunft, Haken/HEAD/Suite/Verhalten pruefen, jedes
im Lauf behauptete Befund-Zitat (Dateiname+Zeile) gegen den echten Code nachschlagen, nie selbst ins Repo
schreiben, Governance-Aktionen (copied/archive/run finish) nie selbst ausfuehren. **Neu bestaetigt in
BRIDGE-0079: vor Code-Aenderung ein Gegenbeweis-Experiment gegen die WP-Praemisse fahren, wenn die Praemisse
pruefbar ist - hat hier eine fehlerhafte Konsolidierungsidee rechtzeitig gestoppt.**

## 5. Nicht von selbst anfangen bei (geklaert, nicht erneut hinterfragen)
- (unveraendert aus v14:) MULTI-AGENT bleibt NEIN, OpenIssue Option A freigegeben/umgesetzt, Claim-Sichtbarkeit
  Option B freigegeben/umgesetzt, G3-Klon-Konvention, WETTER-Auftraege in den Wetter-Steuerchat.
- **Neu: `claim.py` NICHT ungeprueft auf `gitops.git_commit` umstellen** - siehe §1/§3, zweifach belegte
  Blockade. Falls doch gewuenscht: beide Fixes (Scope-Status + autostash) explizit als Umfang benennen, nicht
  nur autostash.

## 6. Offene Punkte - in dieser Reihenfolge
1. **BRIDGE-0079-Entscheidung (April):** Option 1 - Scope-begrenzten Status-Scan fuer `kind="claim"` PLUS
   `autostash` umsetzen (aendert die als "nicht verhandelbar" dokumentierte Ganzbaum-Pruefung, wenn auch nur
   scope-begrenzt) vs. Option 2 - Konsolidierung verwerfen, `_sync_claim_commit` als bewusst richtige Loesung
   akzeptieren (deckt sich mit der schon in v14 dokumentierten Warnung), toten Whitelist-Eintrag entfernen
   oder stehenlassen. **Muss zuerst geklaert werden, dann BRIDGE-0079 entweder neu spezifizieren oder formal
   abschliessen** (kein `CANCELLED`-Status im Schema - vermutlich BLOCKED->ARCHIVED mit Begruendung im
   Audit, falls Option 2).
2. **BRIDGE-0080 anlegen**, sobald Punkt 1 geklaert ist (`expected_head` vorher aktualisieren).
3. **DES11-Sync fuer `acb-rag-index`** nachholen (Clone + `git lfs install`).
4. **RAG-Flag-Umsetzung** (Checkpoint-Register vorhanden) als eigener BRIDGE-Auftrag noch zu spezifizieren -
   nicht angefangen.
5. (unveraendert aus v14 §6, Punkte 2-4:) Generische Steuerchat-Vorlage braucht `OpenIssue`-Referenz, FK00/
   Dorfschaft-Einbindung noch zu klaeren mit April, Draft-Modus weiterhin offen, WinError 10053 weiterhin
   harmlos.
