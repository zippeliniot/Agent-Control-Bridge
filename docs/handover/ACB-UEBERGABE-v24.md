# ACB - Uebergabe v24 (Stand 2026-10-10)

**Repo-HEAD bei Erstellung:** `4426e0a2bf6bf61c1dfee5e9fb59a44edd1ec216` (`4426e0a`) | **Tests:**
607/607 - frisch nachgelaufen in dieser Sitzung gegen genau diesen HEAD (eigenes `.venv`,
`requirements.txt` installiert, `python -m unittest discover -s tests`), nicht uebernommen.

**Fuer den neuen Steuerchat:** `docs/ACB-STEUERCHAT-STANDARDSTART.md`, diese Datei. v19-v23 nicht
loeschen (Historie).

**WICHTIG - noch nicht gepusht:** Diese Datei UND
`docs/concepts/ENTSCHEIDUNG-DREISCHICHTEN-NAECHSTE-SCHRITTE.md` liegen beide nur lokal im
Sitzungs-Klon (`/home/claude/ccb-session`) vor. Der Steuerchat hat in dieser Sitzung **keine**
Push-Credentials (per `git push --dry-run` verifiziert: `403`, siehe Abschnitt 5). April muss
beide Dateien gemeinsam per PowerShell committen/pushen, bevor ein neuer Steuerchat sie per
frischem Klon sehen kann - siehe WO-Block am Ende dieser Datei.

**Anlass dieser Version:** April legte eine externe, textuelle Pruefung des in v22 §2c / v23 §5
Punkt 1 zusammengefassten Drei-Schichten-Umsetzungsplans vor. v24 haelt den dabei entstandenen
Kernbefund fest, damit ein Folgechat ihn nicht erneut verifizieren muss.

## 1. Neu in dieser Version

### 1a. Kernbefund: externe Pruefung bewertete einen bereits ueberholten Zwischenstand

**Nicht erneut verifizieren - siehe Abschnitt 6.** Die externe Pruefung bezog sich
ausschliesslich auf die in v23 zusammengefasste Fuenf-Schritt-Skizze aus v22 §2c. Der
tatsaechliche Stand im Repo (verifiziert durch vollstaendiges Lesen von `BRIDGE-093.md` bis
`BRIDGE-100.md` und der zugehoerigen `docs/concepts/*.md` - nicht nur aus der v23-Zusammenfassung
rekonstruiert) ist deutlich weiter:

| # | v22-Schritt | Tatsaechlicher, verifizierter Stand |
|---|---|---|
| 1 | Decision-Log-CLI/Store | Formalisierungsebene von April angenommen (`ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` §7). Ereignis-Schema entworfen (`BRIDGE-0097`, `schemas/decision.schema.yaml`), bewusst **ohne** CLI-/Store-Anbindung. Ablageform weiterhin offen. |
| 2 | Symbol-/Datei-Graph: Traegerfrage + Indexer | Architektur spezifiziert (`BRIDGE-0094` §4, gegen realen Dorfschaft-Stack PHP 8.x/JS/PowerShell). Technischer Spike durchgefuehrt und **erfolgreich** (`BRIDGE-0098`): Tree-sitter deckt alle geforderten Kantentypen ab, inkl. PowerShell-Grammatik. Traegerfrage weiterhin offen, Indexer-Code nicht begonnen. |
| 3 | Context-Assembler-Schema | Nur Sketch (`BRIDGE-0094` §3) - kein Schema entworfen. |
| 4 | Routing-Feld | Nicht entschieden (`BRIDGE-0094` §5). |
| 5 | RAG als vollwertiger Fallback | Bereits spezifiziert (`RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md`, `BRIDGE-0088`): Revisionsbindung, Herkunftsnachweis, Quellenprioritaet. Mehrprojekt-Faehigkeit geloest (`BRIDGE-0093`). |

Zusaetzlich bereits entschieden, der externen Pruefung naturgemaess nicht bekannt: Governance-Pfad
= kein eigenes Gate (`BRIDGE-0096`); Mehrprojekt-RAG-Vorbedingung = aufgeloest (`BRIDGE-0093`).

**Bewertung der sechs konkreten Empfehlungen aus der Anmerkung** (Details:
`docs/concepts/ENTSCHEIDUNG-DREISCHICHTEN-NAECHSTE-SCHRITTE.md` §3): vier bestaetigen bereits
Getroffenes, ohne etwas zu aendern (Graph-Spike zuerst, RAG nachrangig, Drei-Schichten ersetzt
nicht die Uebergabedatei, Draft-Modus-Selbstblockade). **Zwei sind echt neu und wertvoll:**
(1) ein eigenstaendiger Qualitaetsrahmen fuer Steuerchat-Uebergaben (existiert bisher nur
implizit, verteilt ueber `STANDARDSTART.md`/`ARBEITSWEISE.md`), (2) eine `wp-lint.py`-Erweiterung
um referentielle Integritaet + Vollstaendigkeitspruefung, verknuepfbar mit der bereits offenen
`ISSUE-0006`-Fehlerklasse (unvollstaendiger formaler Auftragszyklus).

### 1b. Tatsaechlich verbleibende offene Punkte (ersetzt die alten fuenf v22-Schritte)

A. Context-Assembler-Schema entwerfen (bisher nur Sketch).
B. Decision-Log: Ablageform + CLI-/Store-Anbindung entscheiden und umsetzen.
C. Routing-Feld entscheiden (welches Schema-Feld steuert die Schicht-Auswahl).
D. Symbol-Graph: Traegerfrage + Indexer-Implementierung (nach erfolgreichem Spike).
E. **(Neu)** Qualitaetsrahmen fuer Steuerchat-Uebergaben als eigenstaendiges Dokument.
F. **(Neu)** `wp-lint.py`-Erweiterung um referentielle Integritaet + Vollstaendigkeitspruefung.

### 1c. Vorgeschlagene Reihenfolge (ENTWURF, Freigabe durch April noch ausstehend)

**E -> F -> B -> A -> C -> D.** Begruendung: E ist unabhaengig von allem anderen umsetzbar und
wirkt sofort; F haengt an E (Pruefregeln brauchen den Qualitaetsrahmen als Massstab); B vor A,
weil der Context-Assembler (A) Decision-Log-Treffer konsolidiert und nicht gegen eine noch nicht
entschiedene Ablageform entworfen werden kann; C haengt an A (Routing ist Teil des
Assembler-Ablaufs); D bleibt zuletzt (Spike erfolgreich, Implementierungsentscheidung ist keine
Vorbedingung fuer die anderen fuenf Punkte). Volle Herleitung:
`docs/concepts/ENTSCHEIDUNG-DREISCHICHTEN-NAECHSTE-SCHRITTE.md` §5.

**Status: ENTWURF.** April muss die Reihenfolge noch bestaetigen oder korrigieren (§7 dort),
bevor der erste Auftrag (Punkt E) spezifiziert wird.

## 2. Neue Dauerregeln dieser Sitzung

Keine neuen Dauerregeln. v23 §2 (Punkte 1-4) bleibt unveraendert in Kraft.

## 3. Aus v23 vollstaendig uebernommen (unveraendert)

- §1a/§1b/§1c (BRIDGE-0101, BRIDGE-0102, ISSUE-0006) - unveraendert, keine neue Aktivitaet
  dieser Sitzung.
- §3a-§3f (alte Konfliktmarker entschieden/Option 1; Drei-Schichten-Umsetzungsplan - jetzt durch
  §1 dieser Version ersetzt/konkretisiert, nicht mehr "weiterhin offen" im alten Wortlaut;
  Projekt-ID-Dropdown; Hamburger-Menue-Scope; `--machine`-Regel; RUNNING/CLAIMED-Spalte) -
  unveraendert offen, keine Bearbeitung dieser Sitzung.
- §6 (Nicht von selbst anfangen bei) - vollstaendig uebernommen, siehe Abschnitt 6 unten.

## 4. G-Status

Unveraendert zu v16-v23 (G0-G5, G6 weiterhin nicht konzipiert).

## 5. Verifikation dieser Sitzung (zusaetzlich zum Standardstart-Ablauf)

- `git push --dry-run`: `403` - keine Push-Credentials in dieser Sitzung, wie in
  `ACB-STEUERCHAT-ARBEITSWEISE.md` §5 Punkt 6 vorausgesetzt - erneut bestaetigt, nicht nur
  angenommen.
- Store-Stand frisch ermittelt (nicht aus v23 uebernommen): alle `tasks/BRIDGE-*` und
  `tasks/WETTER-*` `ARCHIVED`, hoechste WP-ID `BRIDGE-102.md`, hoechste Issue-ID `ISSUE-0006`
  (OPEN, zusammen mit `ISSUE-0005`), `push_mode: direct` fuer `agent-control-bridge` bestaetigt -
  alles deckungsgleich mit v23.

## 6. Offene Punkte - in dieser Reihenfolge

1. **Reihenfolge E->F->B->A->C->D bestaetigen oder korrigieren** (§1c, Details in
   `ENTSCHEIDUNG-DREISCHICHTEN-NAECHSTE-SCHRITTE.md` §5/§7). Nach Bestaetigung: Punkt E als
   erstes Work-Package spezifizieren.
2. **Diese Datei und das Entscheidungsdokument pushen** (siehe Warnhinweis oben, WO-Block unten) -
   ohne Push sieht kein neuer Steuerchat diesen Stand.
3. **Projekt-ID-Dropdown** (unveraendert aus v22/v23).
4. **Hamburger-Menue-Scope klaeren** (unveraendert, mit April abzustimmen).
5. **`--machine`-Regel** in `ACB-STEUERCHAT-ARBEITSWEISE.md` nachtragen (unveraendert).
6. **RUNNING/CLAIMED im Board sichtbar machen** mit neuer Spalte "Akteur" (unveraendert).

**Naechste freie BRIDGE-ID:** `BRIDGE-0103` (unveraendert aus v23). **Naechste freie Issue-ID:**
`ISSUE-0007` (unveraendert) - vor jeder Neuvergabe `bridge issue list --include-closed` gegen den
frischen `origin/main`-Stand pruefen.

## 7. Nicht von selbst anfangen bei (geklaert, nicht erneut hinterfragen)

(unveraendert aus v16-v23:) `machine: vm` in alten Audit-Eintraegen ist erklaert, bewusst nicht
korrigiert. Kein neues Gate fuer die Drei-Schichten-Architektur (`BRIDGE-0096`, entschieden).
Konfliktmarker in `audit.jsonl` (Zeilen 824/839) sind entschieden dokumentiert, nicht korrigiert.
`push_mode: draft` fuer `agent-control-bridge` ist bewusst zurueckgesetzt - nicht ohne neue
Web-UI-Task-Erstellung erneut aktivieren.

**Neu in v24:** Die in Abschnitt 1a tabellierten fuenf v22-Schritte sind **nicht** mehr als
offener Fuenf-Schritt-Plan zu behandeln - vier von fuenf sind spezifiziert/entschieden (nur
Implementierung fehlt), einer (Context-Assembler) ist nur ein Sketch. Ein Folgechat soll **nicht**
erneut bei `BRIDGE-093`-`100` nachlesen, ob der Stand stimmt, ausser ein konkreter Zweifel an
einer einzelnen Zeile der Tabelle in Abschnitt 1a besteht - die Tabelle selbst ist das Ergebnis
dieser Verifikation, keine Vermutung.

## 8. Referenz

v20-v23 bleiben Primaerquellen im Detail fuer alles ausser dem Drei-Schichten-Themenkomplex. Fuer
den Drei-Schichten-Themenkomplex ist `docs/concepts/ENTSCHEIDUNG-DREISCHICHTEN-NAECHSTE-SCHRITTE.md`
jetzt die primaere Quelle (zusammen mit `DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md`,
`BRIDGE-093.md`-`100.md`) - nicht mehr v22 §2c alleine.
