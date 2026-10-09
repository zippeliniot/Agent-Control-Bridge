# ENTSCHEIDUNG: Drei-Schichten-Modell fuer Steering Continuity (Decision-Log / Symbol-Graph / Vektor-RAG)

**Status: ENTWURF - ENTSCHEIDUNG AUSSTEHEND.** Kein Auftrag, keine Schema-Aenderung, keine
Repo-Schreibaktion. Erstellt im Steuerchat am 08.10.2026 aus Aprils Architekturskizze (Bild +
Zielvorstellung, diese Sitzung). Baut auf drei bestehenden Dokumenten auf, ersetzt keines:
`docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH.md` (BRIDGE-0073, V1, gueltig),
`docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` (Nachtrag, ENTWURF, Issue 1 aus
`KONZEPT-PRUEFRUNDEN-INTEGRATION_V3.md` offen), `docs/concepts/RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md`
(BRIDGE-0088, Spezifikation einer einzelnen Vektor-RAG-Archivschicht).

## 1. Ausgangslage (Aprils Problemstellung, woertlich uebernommen)

- Ueber 1000 geplante Steuerchats fuers Dorfschaft-Projekt muessen bei jedem Handover mit offenen
  Tasks und bisherigen Entscheidungen gefuettert werden - token-sparsam.
- Reine Aehnlichkeitssuche ueber archivierte Chat-Texte liefert bei Code-lastigem Inhalt oft
  Treffer, die textlich aehnlich, aber fachlich veraltet sind (z. B. ein frueher verworfener
  Loesungsansatz fuer dieselbe Funktion).
- Die zeitliche/kausale Reihenfolge - was wurde spaeter revidiert, was ist der aktuell gueltige
  Stand - geht bei Vektor-Aehnlichkeit verloren.
- Das geplante `rag_enabled`/`rag_used_since`-Flag-Paar regelt bisher nur, ob RAG ueberhaupt
  laeuft - nicht, welche Schicht bei einer Anfrage tatsaechlich den Kontext liefert.

## 2. Verhaeltnis zu bestehenden Dokumenten - was ist neu, was bereits spezifiziert

Die bestehende `RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md` (BRIDGE-0088) kennt bereits eine
Zwei-Schichten-Unterscheidung in der Sache, nur nicht in dieser Form benannt: `structured_coverage`
(strukturierter Bestand, Vorrang) vs. Archivtreffer aus `rag-index` (Vektor-RAG, nachrangig,
"Hintergrundmaterial bis geprueft", §3 dort). Das entspricht in Aprils Skizze der Beziehung
Decision-Log/Symbol-Graph (strukturiert, primaer) vs. Vektor-RAG-Archiv (Fallback).

**Tatsaechlich neu gegenueber der bestehenden Spezifikation:**

1. **Symbol-/Datei-Graph als eigene, dritte Quelle.** Bisher nicht spezifiziert und in keinem
   Dokument erwaehnt (auch nicht in `RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md`). Adressiert gezielt
   Aprils zweiten Befund (Code-Beziehungen gehen bei reiner Textaehnlichkeit verloren) - das ist ein
   anderes Werkzeug als Vektorsuche (Code-/Datei-Abhaengigkeitsgraph, z. B. ueber
   Tree-sitter/Call-Graph-Extraktion, nicht ueber Embeddings).
2. **Flag-Routing nach Schicht statt nur An/Aus.** `rag_enabled`/`rag_used_since`
   (`project.schema.yaml:62`, `task.schema.yaml:158`) regeln heute nur, *ob* RAG laeuft. Die
   Skizze verlangt zusaetzlich, *welche* Schicht eine konkrete Anfrage bedient - das ist ein neues
   Entscheidungskriterium, kein reines Erweiterungsfeld.
3. **Context-Assembler als benannte Komponente mit Rueckfluss.** "Delta bei Session-Ende" zurueck
   ins Decision-Log ist ein expliziter Schreibpfad, den `RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md`
   nicht kennt (die dortige Pipeline ist reine Leserichtung: Kontext liefern, in
   `context_sources_used` protokollieren - kein Rueckschreiben ins Decision-Log).

**Bereits spezifiziert, nur umbenannt/umsortiert:**

- "Decision-Log" setzt die Formalisierung aus `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md`
  §3a voraus (append-only Ereignisse, `supersedes`, kein `superseded_by`-Feld). Ohne diese
  Formalisierung ist das "Decision-Log" in der Skizze nichts anderes als die heutigen
  `ENTSCHEIDUNG-*.md`-Prosadateien plus `OpenIssue` - strukturiert durchsuchbar wird es erst mit
  der V2-Formalisierung. **Diese Architektur haengt also direkt an der noch offenen Frage in
  `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` §6.**
- "Vektor-RAG (Archiv)" entspricht der bestehenden `archive_fallback_policy`
  (`RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md` §1, §3): Archivtreffer sind nachrangig, nie
  gleichrangig zum strukturierten Bestand. Unveraendert uebernehmbar.
- "Steuerchat-Session" als Senke/Quelle entspricht `context_sources_used` (Ist-Protokoll pro
  Sitzung, §1 dort).

## 3. Ungeklaerte Abhaengigkeit: Mehrprojekt-RAG existiert noch nicht

`docs/handover/ACB-UEBERGABE-v16.md` §6 Punkt 6: bisher existiert nur ein RAG-Index fuer
`agent-control-bridge` selbst, ein Index-Repo mit Unterordner pro `project_id` fuer
Mehrprojekt-Parallelitaet ist "noch nicht spezifiziert/umgesetzt". Die Drei-Schichten-Architektur
zielt aber explizit auf Dorfschaft (1000+ Steuerchats) - ein Fremdprojekt, fuer das weder ein
RAG-Index noch (nach Kenntnis dieser Sitzung) ein Symbol-/Datei-Graph existiert. **Diese
Architektur setzt die Loesung von v16 §6 Punkt 6 voraus, loest sie aber nicht selbst.**

## 4. Offene Fragen, falls angenommen (hier nicht entschieden)

- Governance-Pfad wie bei jeder neuen Architektur: eigenes Gate/eigene BRIDGE-Auftragsfolge, nicht
  im laufenden BRIDGE-0090 (reine Dokumentkorrektur) mitgezogen.
- Wer baut/pflegt den Symbol-/Datei-Graph (eigenes Tooling? bestehende Bibliothek? welche Sprachen -
  Dorfschaft-Stack muesste dafuer bekannt sein, hier nicht geprueft)?
- Schema fuer den Context-Assembler (neue Datei/neues Objekt oder Erweiterung von
  `result.schema.yaml`?) - noch nicht entworfen.
- Reihenfolge: erst `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` §6 entscheiden (Decision-Log-
  Formalisierung), dann diese Architektur spezifizieren - oder beides zusammen, da eng gekoppelt?

## 5. Empfehlung des Steuerchats

Reihenfolge einhalten statt parallelisieren: (1) BRIDGE-0090 abschliessen (laufende
Dokumentkorrektur), (2) `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` §6 entscheiden
(Formalisierung ja/nein - Voraussetzung fuer ein echtes Decision-Log), (3) erst danach diese
Drei-Schichten-Architektur als eigenen Auftrag/eigene Auftragsfolge spezifizieren, mit v16 §6
Punkt 6 (Mehrprojekt-RAG) als expliziter Vorbedingung, nicht als Nebenaspekt. Grund: Punkt 2 und 3
auf einmal zu entscheiden hiesse, eine noch offene Formalisierungsfrage implizit durch eine groessere
Architekturentscheidung mitzuentscheiden - das widerspricht "ein Auftrag = ein Bereich"
(`ACB-UMSETZUNGSKONZEPT-V2.md` §1) und macht eine spaetere Revision einer der beiden Fragen fuer
die jeweils andere schwerer nachvollziehbar.

## 6. Offene Frage an April

Reihenfolge aus Abschnitt 5 bestaetigen, oder bewusst anders entscheiden (z. B. beide Fragen -
Decision-Log-Formalisierung und Drei-Schichten-Architektur - in einem Zug spezifizieren, weil sie
ohnehin nicht sinnvoll getrennt zu entwerfen sind)?
