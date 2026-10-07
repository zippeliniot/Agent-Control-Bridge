# BRIDGE-0088 - RAG-Retrieval-/Injection-Pipeline spezifizieren + Entscheidungsvorlage V2 fuer Decision-Formalisierung

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0088 |
| project_id | agent-control-bridge |
| Typ / Klasse | ARCHITECTURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Konzept-/Spezifikationsarbeit mit Entscheidungscharakter (wie BRIDGE-0073), kein Widerspruchs-/Sicherheitsfall (daher nicht HIGH), kein Code-Risiko (daher nicht LOW). |
| Modellwechsel zum Vorgaenger | NEIN (Vorgaenger BRIDGE-0087: Claude Sonnet 5 / LOW, REFACTOR - Modell bleibt Sonnet 5, Denkstufe angehoben auf MEDIUM, siehe Begruendung oben) |
| depends_on | BRIDGE-0087 (ARCHIVED) |
| Gate | keines (reine Konzept-/Spezifikationsarbeit, kein G2/G3/G4-Scope beruehrt) |
| stop_conditions | CONCEPT_CONFLICT |
| Multi-Agent | NEIN |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0088` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: Claude Sonnet 5 / DENKSTUFE: MEDIUM`. Abweichung von der Tabelle = STOPP.

## Auftrag

**Ziel:** Zwei neue Dokumente, beide ohne Implementierung und ohne Schema-Aenderung:

1. Eine Spezifikation der RAG-Retrieval-/Injection-Pipeline (Handover v16 §6 Punkt 4: "das eigentliche `rag query`, das tatsaechlich eine Kontextdatei fuer den naechsten Steuerchat liefert") inklusive der Grundlage fuer das Quellen-Manifest (Handover v16 §6 Punkt 5: `rag/sources.yaml` + Coverage-Check).
2. Eine neue Entscheidungsvorlage, die BRIDGE-0073 (`docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH.md`) anhand ihres tatsaechlichen Wortlauts prueft und die Formalisierung von "Decision" als Aenderungsvorschlag darstellt - **nicht** als Entscheidung selbst. BRIDGE-0073s Verdikt zu "Decision" (Option B, Zeile 17: "Entscheidungen sind bewusst menschlicher Text") bleibt bis zu einer ausdruecklichen neuen Entscheidung durch April unveraendert gueltig.

**Scope:** Neu: `docs/concepts/RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md`, `docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md`. Sonst nichts. Kein Code, kein `schemas/`-Eintrag, keine Aenderung an `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH.md` (V1 bleibt unveraendert stehen), keine Aenderung an `task.schema.yaml`/`project.schema.yaml`.

### Teil A - RAG-Retrieval-/Injection-Pipeline-Spezifikation

**Scope:** `docs/concepts/RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md` (max. 150 Zeilen, Tabellen-/Abschnittsform wie `RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md`).

Jeder der folgenden Begriffe wird mit **Definition, Feldtyp/Ort und Bezug zum realen Code** festgehalten (nicht nur benannt):

1. **`structured_coverage`** - welche Quellen (Dateien/Dokumente/Steuerchat-Sessions) bereits strukturiert konsolidiert wurden, je Projekt. Muss gegen `project.yaml: rag_enabled/rag_index_repo` (BRIDGE-0081) abgeglichen werden, nicht als neues Projektfeld ohne Bezug dazu entworfen.
2. **`migration_status`** - was am strukturierten Bestand noch fehlt (offene Quellen, teilweise erfasste Dateien). Muss `rag_used_since` (aktuell `null`, BRIDGE-0081 "reserviert fuer eine kuenftige Retrieval-Pipeline") erstmals mit echter Semantik verbinden oder begruenden, warum `rag_used_since` dafuer NICHT als Gueltigkeitsgrenze taugt (siehe Punkt 4 unten) und welches Feld stattdessen.
3. **`archive_fallback_policy`** - wann ein Archivtreffer (Vektor-RAG) ueberhaupt herangezogen werden darf. Muss ausdruecklich festhalten: Archivtreffer sind Hintergrundmaterial, bis ihre Aussage geprueft und strukturiert uebernommen ist; ein Datum oder Aehnlichkeitswert allein macht einen Treffer nicht verbindlich.
4. **`context_sources_used`** - welche Quellen einer konkreten Steuerchat-Sitzung tatsaechlich Kontext geliefert haben (Protokollfeld, nicht Policy). Abgrenzung zu `structured_coverage` (Soll-Zustand) und `migration_status` (Luecke) explizit machen.
5. **Quellenprioritaet** - Rangfolge, wenn mehrere Quellenarten (strukturierter Bestand vs. Archiv) denselben Sachverhalt beruehren; strukturierter Bestand hat Vorrang vor Archivtreffern (siehe Punkt 3).
6. **Revisionsbindung** - jede gelieferte Quelle ist an Repository + Commit (bzw. definierten Snapshot) gebunden, nie nur an einen Dateipfad - besonders wichtig nach Umbenennungen. Gegen das reale `result.schema.yaml` (`head`, `base_head`, `task_hash`) abgleichen, kein Parallelmechanismus erfinden.
7. **Pflichtkontext** - welche Quellen eine Steuerchat-Sitzung *immer* erhaelt, unabhaengig vom Suchtreffer (z. B. aktueller `work-packages/BRIDGE-xxx.md`-Stand offener Auftraege, letzte Handover-Datei, offene `OpenIssue`-Eintraege).
8. **Blocker bei fehlenden Quellen** - Verhalten, wenn Pflichtkontext nicht lieferbar ist (z. B. `rag_prereqs.check()` meldet fehlende Infrastruktur). Muss an das bestehende fail-soft-Prinzip anschliessen (`rag_prereqs`/`rag_index_sync` sind "bewusst fail-soft/nie-werfend", Handover v16 §3) - die Pipeline-Spezifikation legt fest, ob und wann daraus trotzdem ein `BLOCKED`/Klaerungsauftrag entstehen soll, ohne das fail-soft-Prinzip der Infrastrukturschicht selbst aufzuweichen.
9. **Herkunftsnachweis** - jede in eine Steuerchat-Sitzung injizierte Information traegt eine nachvollziehbare Quellenangabe (Datei + Revision, oder Steuerchat-Session-Verweis).

**Ausdruecklich referenzieren, nicht voraussetzen:** Ein Abschnitt haelt fest, dass eine formalisierte Decision-Struktur (`supersedes`/`applies_to`/`affects`/`implemented_by`/`verified_by`, siehe Teil B) die Quellenabdeckung praeziser machen *wuerde*, markiert aber ausdruecklich jeden darauf aufbauenden Punkt als **entscheidungsabhaengig** (Kennzeichnung im Text: "[entscheidungsabhaengig, siehe ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2]"). Die Spezifikation muss ohne diese Struktur vollstaendig und umsetzbar bleiben.

- [ ] Alle neun Begriffe mit Definition, Feldort und Code-Bezug dokumentiert
- [ ] `rag_used_since`-Frage (Punkt 2) explizit beantwortet, nicht offengelassen
- [ ] Entscheidungsabhaengige Abschnitte eindeutig gekennzeichnet, Spezifikation ohne sie vollstaendig lesbar
- [ ] Explizit "Spezifikation, keine Implementierung" im Dateikopf vermerkt

### Teil B - Entscheidungsvorlage V2 (Verweis)

**Scope:** `docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md`.

Inhalt wie im Steuerchat vom 07.10. vorbereitet und als eigenes Dokument mitgeliefert (siehe Lieferung). Claude Code uebernimmt die gelieferte Fassung unveraendert in den Commit, prueft nur Format (max. 80 Zeilen wie V1, Tabellenform) und dass `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH.md` (V1) dabei nicht angefasst wird.

- [ ] `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` liegt unveraendert gegenueber der gelieferten Fassung im Repo
- [ ] V1-Datei unangetastet (`git diff` zeigt keine Aenderung an `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH.md`)
- [ ] Status-Zeile "ENTWURF - ENTSCHEIDUNG AUSSTEHEND" vorhanden

## Abschluss

1. Volle Suite EINMAL, nur die letzten 3 Zeilen zeigen (keine Code-Aenderung erwartet, Suite dient nur als Regressions-Nachweis).
2. `git status` sauber.
- [ ] Volle Suite gruen (576/576 erwartet - keine Tests entfernt oder neu)
