# ENTSCHEIDUNG: Formalisierung von "Decision" - Nachtrag zu BRIDGE-0073 (V2)

**Status: ENTWURF - ENTSCHEIDUNG AUSSTEHEND.** BRIDGE-0073 (`ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH.md`)
bleibt bis zu einer ausdruecklichen Entscheidung durch April unveraendert gueltig. Dieses Dokument
aendert nichts am Repo-Verhalten; es ist ein Vorschlag zur Diskussion, erstellt im Rahmen von BRIDGE-0088.

Stand 2026-10-07. Nachtrag, kein Ersatz fuer V1.

## 1. Was BRIDGE-0073 wirklich entschieden hat (Wortlaut)

V1, Objekttabelle, Zeile "Decision": Gegenstueck `docs/concepts/ENTSCHEIDUNG-*.md` (4 Dateien),
Zustaende `REVIEW_REQUIRED`/`APPROVAL_REQUIRED`, Deckung "teilweise (Prosa, kein Schema)",
**Option B** - mit der Begruendung: *"Entscheidungen sind bewusst menschlicher Text"*. Das ist ein
bewusstes, begruendetes Verdikt, kein Versaeumnis - jede Formalisierung muss sich dagegen
rechtfertigen, nicht nur dagegen argumentieren, dass ein Schema technisch moeglich waere.

## 2. Anlass fuer den Nachtrag

BRIDGE-0088 (RAG-Retrieval-Pipeline-Spezifikation, Handover v16 §6 Punkt 4/5) braucht belastbare
Quellenbindung: welche Information gilt noch, welche wurde ersetzt, wodurch. Ohne ein strukturiertes
Decision-Objekt bleibt das reine Prosa-Verlinkung zwischen `ENTSCHEIDUNG-*.md`-Dateien - fuer eine
Handvoll Dateien (heute: 5) trotzdem tragbar, fuer eine RAG-gestuetzte Suche ueber viele Sitzungen
hinweg zunehmend ungenau. Das ist der einzige neue Fakt gegenueber V1; alles andere unten ist
Verfeinerung derselben Ausgangsfrage.

## 3. Vorschlag (nur bei Annahme wirksam)

### 3a. Append-only ohne rueckwirkende Aenderung

V1 hat `superseded_by` nicht spezifiziert; ein nachtraeglich auf einen alten Eintrag geschriebenes
`superseded_by` wuerde Append-only verletzen. Vorschlag: eine neue Entscheidung traegt `supersedes`
(Verweis auf die alte), dazu ein eigenes Ereignis fuer Annahme/Ablösung. `superseded_by` existiert
nur in einer daraus berechneten, nicht gespeicherten Ansicht. Eine neu *vorgeschlagene* Entscheidung
verdraengt eine bereits akzeptierte nicht automatisch - erst das Akzeptanz-Ereignis tut das.

### 3b. Entscheidung ist nicht an genau einen Task gebunden

Vier getrennte Felder statt einem: `origin_task_id` (Entstehung), `applies_to` (Geltungsbereich),
`affected_task_ids` (zu ueberpruefende Arbeiten), `source_refs` (Begruendungsquellen). Eine
Architekturentscheidung kann mehrere Auftraege betreffen oder ihnen vorausgehen - ein einzelnes
`task_id`-Feld (wie bei `OpenIssue.origin_task_id`) bildet das nicht ab.

### 3c. Code-Bezug getrennt von Entscheidung

Drei Beziehungen statt `files_touched`: `affects` (betroffene Komponente/Datei, ohne dass schon
Code geaendert wurde), `implemented_by` (konkrete Umsetzung), `verified_by` (Pruefnachweis). Jeder
Codebezug ist an Repository + Commit (oder definierten Snapshot) gebunden, nicht nur an Dateipfade -
sonst liefert er nach Umbenennungen veralteten Kontext.

## 4. Was das NICHT ist

Kein Vorschlag fuer einen Code-Symbolgraphen - den gibt es im Repo nicht, und dieses Dokument fuehrt
keinen ein. Fuer Dorfschaft muessen ohnehin zuerst Fachkonzepte, Kapitel, Ownership und Schnittstellen
referenzierbar sein, lange bevor ein Code-Symbolgraph ueberhaupt in Frage kaeme - das ist eine andere,
spaetere Frage.

## 5. Folgefragen, falls angenommen (hier nicht entschieden)

- Neues `schemas/decision.schema.yaml` noetig (analog `open-issue.schema.yaml`, BRIDGE-0075-Muster).
- `task.schema.yaml`-Erweiterung um `requirement_refs`, `preconditions`, `evidence_refs`, `blockers`
  ist eine **eigene, hier nicht mitentschiedene** Frage (`priority`, `depends_on`,
  `acceptance_criteria`, `git.expected_head`, `resume_hint` decken bereits Teile ab - siehe BRIDGE-0088
  Teil A, Pruefung gegen den echten Schema-Stand).
- Governance-Pfad wie bei jeder Schema-Aenderung: eigener BRIDGE-Auftrag, `additionalProperties: false`
  bleibt die Grundhaltung, keine stillschweigende Erweiterung.

## 6. Offene Frage an April

Soll BRIDGE-0073s Decision-Verdikt (Option B) aufgehoben und durch die Formalisierung aus Abschnitt 3
ersetzt werden - mit allen Folgefragen aus Abschnitt 5 als eigene, spaetere Auftraege? Bis zur
ausdruecklichen Zustimmung bleibt V1 massgeblich.
