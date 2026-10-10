# ENTSCHEIDUNG: Drei-Schichten-Modell — Folgeschritte nach externer Pruefung

**Status: ENTWURF — ENTSCHEIDUNG AUSSTEHEND.** Kein Auftrag, keine Schema-Aenderung, keine
Repo-Schreibaktion ausser dieser Datei. Beantwortet v23 §5 Punkt 1 ("Drei-Schichten-
Umsetzungsplan bestaetigen oder korrigieren"), angestossen durch eine von April angehaengte
externe Pruefung des in v22 §2c / v23 §5 Punkt 1 zusammengefassten Fuenf-Schritt-Vorschlags.

## 1. Anlass

April hat eine externe, textuelle Pruefung des in v23 zusammengefassten Umsetzungsplans
angehaengt (sechs Tabellenpunkte zur Schichteinordnung, sechs Teile einer vorgeschlagenen
Reihenfolge, sechs konkrete Empfehlungen). Auftrag: Anmerkungen einordnen, Architektur/
fachliche Vorbereitung zuerst, danach erst Aufteilung in Arbeitsauftraege.

## 2. Verifikation gegen den echten Repo-Stand (vor Bewertung der Anmerkung durchgefuehrt)

Die externe Pruefung bezieht sich ausschliesslich auf die in v23 zusammengefasste Skizze aus
v22 §2c. Der tatsaechliche Stand im frischen Klon (HEAD `4426e0a`, Pflichtdokumente und
Primaerquellen `BRIDGE-093.md` bis `BRIDGE-100.md` sowie die zugehoerigen
`docs/concepts/*.md` vollstaendig gelesen) ist bereits deutlich weiter, als aus der
Zusammenfassung ersichtlich war:

| # | v22-Schritt | Tatsaechlicher, verifizierter Stand |
|---|---|---|
| 1 | Decision-Log-CLI/Store | Formalisierungsebene von April angenommen (`ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` §7). Schema entworfen (`BRIDGE-0097`, `schemas/decision.schema.yaml`) — bewusst **ohne** CLI-/Store-Anbindung (explizite Scope-Abgrenzung im WP). Ablageform (eine Datei je `decision_id` vs. Verzeichnis je Ereignis) weiterhin offen. |
| 2 | Symbol-/Datei-Graph: Traegerfrage + Indexer | Architektur spezifiziert (`BRIDGE-0094` §4, gegen realen Dorfschaft-Stack PHP 8.x/JS/PowerShell, konkrete Kantentypen benannt). Technischer Spike durchgefuehrt und erfolgreich (`BRIDGE-0098`): Tree-sitter deckt alle geforderten Kantentypen ab, inkl. PowerShell-Grammatik, Parser-Eigenheit dokumentiert. Traegerfrage (wer baut/pflegt) weiterhin offen, Indexer-Code nicht begonnen. |
| 3 | Context-Assembler-Schema | Nur Sketch (`BRIDGE-0094` §3: `session_delta`, Schreibzeitpunkt Sitzungsende, fail-soft) — kein Schema entworfen. |
| 4 | Routing-Feld | Nicht entschieden (`BRIDGE-0094` §5, vierstufige Routing-Reihenfolge skizziert, aber kein Schema-Feld benannt). |
| 5 | RAG als vollwertiger Fallback | Bereits spezifiziert (`RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md`, `BRIDGE-0088`): Revisionsbindung, Herkunftsnachweis, Quellenprioritaet, `rag/sources.yaml`-Grundstruktur. Mehrprojekt-Faehigkeit geloest (`BRIDGE-0093`). |

Zusaetzlich bereits entschieden, der externen Pruefung naturgemaess nicht bekannt:

- **Governance-Pfad:** kein eigenes Gate (`BRIDGE-0096`) — die Architektur laeuft im normalen
  `task create → run start → run finish`-Flow, ein bestehendes Gate (G0–G5) gilt nur
  zusaetzlich, wenn eine spaetere Implementierung eine dort bereits geregelte
  Infrastruktur-Faehigkeit beruehrt.
- **Mehrprojekt-RAG-Vorbedingung:** aufgeloest (`BRIDGE-0093`, Konvention: ein Repo/Klon,
  Unterordner pro `project_id`).

**Folge fuer die Bewertung:** Die externe Anmerkung bewertet eine bereits ueberholte
Zwischenstufe — nicht, weil sie falsch liegt, sondern weil ihr die Primaerquellen
`BRIDGE-0093`–`0100` nicht vorlagen. Mehrere ihrer Empfehlungen sind inhaltlich bereits
umgesetzt bzw. spezifiziert.

## 3. Bewertung der sechs konkreten Empfehlungen aus der Anmerkung, gegen den echten Stand

1. **Qualitaetskriterien fuer Steuerchat-Uebergaben zuerst festlegen.** Nirgends im Repo als
   eigenstaendiges Dokument spezifiziert — existiert nur implizit, verteilt ueber
   `docs/ACB-STEUERCHAT-STANDARDSTART.md` (Abschnitt 5) und
   `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` (Abschnitte 1, 5). **Echt neu, begruendet —
   uebernehmen.**
2. **`wp-lint.py` erweitern** (referentielle Integritaet, Vollstaendigkeit von Scope/
   Abnahmekriterien/Uebergabeinfo). Baut auf real existierendem Skript auf (`BRIDGE-0102`,
   in der vorigen Sitzung gegen den echten Code verifiziert). **Konkret umsetzbar, begruendet
   — uebernehmen.**
3. **Selbstblockaden vor Draft-Modus-Reaktivierung verhindern.** Deckt sich bereits mit v23 §6
   ("`push_mode: draft` … nicht ohne neue Web-UI-Task-Erstellung erneut aktivieren"). Keine
   neue Erkenntnis, zutreffende Bestaetigung — als Vorbedingung vermerkt, kein eigener Auftrag,
   solange niemand Draft-Modus reaktivieren will.
4. **Projektuebergreifende Audit-Nachvollziehbarkeit verbessern.** Deckt sich mit v23 §1a
   (bereits als akzeptierte, dokumentierte Einschraenkung gefuehrt; `BRIDGE-0101` Teil B /
   `filter_project_files()` hat das technisch Moegliche bereits getan). Keine neue Erkenntnis
   — kein neuer Auftrag.
5. **Fehlende formale Auftragszyklen als eigene Fehlerklasse fuehren.** Deckt sich mit
   `ISSUE-0006` (bereits OPEN, exakt dieses Muster: `BRIDGE-0092` real committet, aber ohne
   formalen Auftragszyklus). Die Anmerkung liefert einen Mehrwert **ueber** `ISSUE-0006`
   hinaus: diese Pruefung systematisch statt als Einzelfall zu behandeln — siehe Punkt 2/F
   unten.
6. **Drei-Schichten-Modell nicht als Ersatz der Uebergabedatei.** Bereits exakt so
   spezifiziert (`RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md`, Begriff "Pflichtkontext": die
   Handover-Datei wird immer mitgeliefert, Schritt 1 vor jeder Schicht-Abfrage,
   `DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md` §2 uebernimmt das unveraendert). Keine neue
   Erkenntnis, zutreffende Bestaetigung.

**Ergebnis:** Zwei der sechs Empfehlungen sind tatsaechlich neu und wertvoll (1 und 2, mit 5
als Teilaspekt von 2 verknuepfbar), vier bestaetigen bereits getroffene Entscheidungen bzw.
bereits spezifiziertes Verhalten, ohne etwas daran zu aendern.

## 4. Tatsaechlich verbleibende offene Punkte (nach Verifikation, nicht aus der Anmerkung allein)

A. **Context-Assembler-Schema entwerfen** (bisher nur Sketch, `BRIDGE-0094` §3).
B. **Decision-Log: Ablageform + CLI-/Store-Anbindung entscheiden und umsetzen**
   (`BRIDGE-0097`-Scope-Grenze, bisher nur Ereignis-Schema ohne Anbindung).
C. **Routing-Feld entscheiden** (welches Schema-Feld steuert die Schicht-Auswahl,
   `BRIDGE-0094` §5).
D. **Symbol-Graph: Traegerfrage + Indexer-Implementierung** (wer baut/pflegt, welche Kanten
   tatsaechlich gespeichert werden, Ablageform — nach erfolgreichem Spike `BRIDGE-0098`).
E. **(Neu, aus der Anmerkung) Qualitaetsrahmen fuer Steuerchat-Uebergaben** als eigenstaendiges
   Dokument.
F. **(Neu, aus der Anmerkung) `wp-lint.py`-Erweiterung** um referentielle Integritaet
   (Issues/Entscheidungen auflosbar) und Vollstaendigkeitspruefung (Scope, Abnahmekriterien,
   Uebergabeinformationen vorhanden), inkl. der `ISSUE-0006`-Fehlerklasse (unvollstaendiger
   formaler Auftragszyklus) als wiederkehrende statt einmalige Pruefung.

## 5. Vorgeschlagene Reihenfolge (Empfehlung des Steuerchats)

Die Anmerkung hat in der Grundidee recht — "Uebergabequalitaet vor Architekturdetails" — nur
angewandt auf den tatsaechlichen, nicht den vermuteten Stand:

1. **E zuerst** (Qualitaetsrahmen Uebergaben). Unabhaengig von A–D umsetzbar, wirkt sofort auf
   jede kuenftige Sitzung, keine Abhaengigkeit zu den anderen Punkten.
2. **F** (`wp-lint.py`-Erweiterung). Haengt an E (die neuen Pruefregeln brauchen den in 1
   definierten Rahmen als Massstab), baut auf bestehendem Skript auf.
3. **B** (Decision-Log Ablageform/CLI). Jetzt, nicht vor E/F — ohne einen klaren
   Qualitaetsrahmen besteht sonst das Risiko, ein technisch funktionierendes, aber am
   eigentlichen Uebergabe-Zweck vorbei entworfenes Store-Schema zu bauen.
4. **A** (Context-Assembler-Schema). Haengt an B (der Assembler konsolidiert u. a.
   Decision-Log-Treffer, kann also nicht vor dessen Ablageform entworfen werden) und an E
   (die Assembler-Ausgabe muss den Qualitaetsrahmen erfuellen).
5. **C** (Routing-Feld). Haengt an A (Routing ist Teil des Assembler-Ablaufs,
   `DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md` §2).
6. **D** (Graph-Implementierung). Unveraendert zuletzt, wie in der urspruenglichen
   Architektur-Spezifikation vorgesehen — Spike bereits erfolgreich abgeschlossen, die
   Implementierungsentscheidung ist die einzig verbleibende Huerde, keine Vorbedingung fuer
   die anderen fuenf Punkte.

Begruendung Reihenfolge B vor A: B liefert das Datenmodell, das A konsumiert — umgekehrt zu
entwerfen hiesse, den Assembler gegen ein noch nicht existierendes Store-Verhalten zu
spezifizieren.

## 6. Was das NICHT ist

Keine Auftragsanlage, kein Schema-Entwurf, keine Code-Aenderung. Legt nur die Reihenfolge der
verbleibenden Spezifikationsarbeit fest. Jeder der sechs Punkte (E, F, B, A, C, D) wird — nach
Bestaetigung dieser Reihenfolge — als eigener Auftrag spezifiziert ("ein Auftrag = ein
Bereich", `ACB-UMSETZUNGSKONZEPT-V2.md` §1), nicht gebuendelt, da die Punkte inhaltlich
unterschiedliche Bereiche betreffen und teils type T1 (Entscheidung, E/B/C) teils T2
(Konzeptarbeit, A/F) sind.

## 7. Offene Frage an April

Reihenfolge aus Abschnitt 5 (E → F → B → A → C → D) bestaetigen oder korrigieren? Nach
Bestaetigung spezifiziert der Steuerchat Punkt E als erstes Work-Package.
