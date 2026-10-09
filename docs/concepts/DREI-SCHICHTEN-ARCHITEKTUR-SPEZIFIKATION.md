# Drei-Schichten-Architektur fuer Steering Continuity - Spezifikation

**Spezifikation, keine Implementierung.** Stand BRIDGE-0094. Kein Code, kein Schema-Eintrag.
Baut auf drei bereits bestehenden/entschiedenen Grundlagen auf, ersetzt keine:

- `docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` §7: April hat der
  Formalisierungsebene (append-only Ereignisse, `supersedes`, `affects`/`implemented_by`/
  `verified_by`) zugestimmt - Voraussetzung fuer ein strukturiert durchsuchbares Decision-Log
  (`ENTSCHEIDUNG-DREI-SCHICHTEN-STEERING-CONTINUITY.md` §2, Punkt "Bereits spezifiziert").
- `docs/concepts/RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md`: Quellenprioritaet
  (strukturiert vor Archiv), `archive_fallback_policy`, `context_sources_used` - unveraendert
  uebernommen, nicht neu erfunden.
- `docs/concepts/MEHRPROJEKT-RAG-SPEZIFIKATION.md` (BRIDGE-0093): loest die Vorbedingung
  "ein Repo/Klon, Unterordner pro `project_id`" - die Vektor-RAG-Schicht unten baut darauf auf.

Reihenfolge-Empfehlung aus `ENTSCHEIDUNG-DREI-SCHICHTEN-STEERING-CONTINUITY.md` §5 von April
bestaetigt (09.10.2026): BRIDGE-0090 -> V2 §6 -> Mehrprojekt-RAG -> diese Spezifikation.
Alle drei Vorbedingungen sind damit erfuellt.

## 1. Die drei Schichten (Begriffstabelle)

| Schicht | Rolle | Grundlage | Neu in dieser Spec |
|---|---|---|---|
| Decision-Log | strukturiert, primaer - Entscheidungen, offene Punkte | `ENTSCHEIDUNG-*.md`-Prosa + `OpenIssue` (BRIDGE-0075) + V2§3-Formalisierung | Nein - nur die Zusammenfuehrung der drei bestehenden Teile unter einem Namen |
| Symbol-/Datei-Graph | strukturiert, primaer - Code-Abhaengigkeiten | keine | **Ja - vollstaendig neu, Abschnitt 4** |
| Vektor-RAG-Archiv | nachrangig, Fallback - Freitext-Aehnlichkeit | `RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md` + `MEHRPROJEKT-RAG-SPEZIFIKATION.md` | Nein - unveraendert, jetzt mehrprojektfaehig |

Quellenprioritaet bei Konflikt (uebernommen aus RAG-Pipeline-Spec §1, hier auf alle drei
Schichten erweitert): Decision-Log und Symbol-Graph sind gleichrangig strukturiert und haben
beide Vorrang vor einem Vektor-RAG-Archivtreffer; ein Archivtreffer bleibt ungeprueftes
Hintergrundmaterial, bis er in eine der beiden strukturierten Schichten uebernommen ist.

## 2. Flag-Routing nach Schicht (neues Entscheidungskriterium)

`rag_enabled`/`rag_used_since` regeln bisher nur, *ob* RAG laeuft (An/Aus). Fehlendes Stueck:
*welche* Schicht eine konkrete Anfrage bedient. Vorgeschlagene Routing-Reihenfolge (jede
Stufe optional, naechste nur bei Luecke):

1. **Pflichtkontext** (RAG-Pipeline-Spec §1: offene Work-Packages, letzte Handover-Datei,
   offene `OpenIssue`-Eintraege) - immer, unabhaengig vom Treffer.
2. **Decision-Log-Abfrage** - strukturierte Suche nach `supersedes`/`affects` fuer die
   betroffene Einheit (Konzept/Komponente/Datei).
3. **Symbol-/Datei-Graph-Abfrage** - nur wenn die Anfrage eine konkrete Datei/Funktion
   betrifft (Code-Aenderung, Bugfix, Refactoring) - liefert die Menge der Dateien/Symbole,
   die wegen realer Abhaengigkeiten mitverstanden werden muessen (Abschnitt 4).
4. **Vektor-RAG-Archiv** - nur als Fallback bei Luecke in 2+3 (`migration_status`,
   RAG-Pipeline-Spec §3), markiert als ungeprueftes Hintergrundmaterial.

Welches `project.schema.yaml`/`task.schema.yaml`-Feld dieses Routing konkret steuert, ist
hier **nicht entschieden** - eigene Schema-Frage (Abschnitt 5).

## 3. Context-Assembler (benannte Komponente mit Rueckfluss)

Neu gegenueber der RAG-Pipeline-Spec (die ist reine Leserichtung): der Context-Assembler
fuehrt Pflichtkontext + Schicht-Treffer (Abschnitt 2) zusammen, protokolliert sie wie bisher
in `context_sources_used`, UND schreibt am Sitzungsende ein Delta zurueck ins Decision-Log
(neue Schreibrichtung, kein Rueckschreiben in den Symbol-Graph oder das Vektor-Archiv).

Sketch (kein Schema, Diskussionsgrundlage fuer den Folgeauftrag aus Abschnitt 5):

- `session_delta` - Liste neuer/veraenderter Entscheidungen oder OpenIssues aus genau dieser
  Sitzung, mit Revisionsbindung (Repo+Commit, wie `RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md`
  Abschnitt 1 "Revisionsbindung" verlangt).
- Schreibzeitpunkt: Sitzungsende, nicht laufend - vermeidet Teilzustaende im Decision-Log
  waehrend eine Sitzung noch laeuft.
- Fail-soft wie alle bestehenden RAG-Module (`rag_prereqs.check()`, `gitops.rag_index_sync()`):
  ein fehlgeschlagener Ruecklauf blockiert nicht die eigentliche Sitzung, landet aber nicht
  stillschweigend verloren - mindestens eine Audit-Zeile, auch im Fehlerfall.

## 4. Symbol-/Datei-Graph (vollstaendig neue Quelle)

Stack-Grundlage fuer Dorfschaft (April, 09.10.2026, diese Sitzung): PHP 8.x (Backend,
modular), MariaDB/MySQL, serverseitig gerenderte HTML-Templates, natives/modulares
JavaScript (kein React/Vue/Angular), modulbezogenes CSS, PHP+PowerShell fuer Tests/Verifier,
SQL fuer Migrationen/Seeds, PowerShell fuer Deployment/Pruefskripte, Git/GitHub, Zielbetrieb
Namecheap/cPanel.

**Primaersprache PHP, Nebensprachen JavaScript und PowerShell** (Tests/Verifier/Deployment
tragen einen erheblichen Teil der technischen Abhaengigkeiten). Werkzeugvorgabe:
parserbasiert, nicht embeddingbasiert - **Tree-sitter als bevorzugter Kandidat**, PHP/
JavaScript/PowerShell-Grammatiken vorausgesetzt, aber **nicht als einzig zulaessiges
Werkzeug festgelegt** - der konkrete Parser-/Symbolumfang wird in einem technischen Spike
bestaetigt, bevor Code geschrieben wird (siehe Abschnitt 5, kein Spike in dieser Spec).

Mindestens zu erfassende Kantentypen (April, woertlich uebernommen):

- Datei -> Datei
- Namespace -> Klasse
- Klasse -> Klasse/Interface/Trait (`extends`/`implements`/Trait-Nutzung)
- Konstruktor-/Service-Abhaengigkeiten
- Funktions-/Methodenreferenzen, soweit statisch bestimmbar
- `require`/`include`
- Template-Abhaengigkeiten
- JavaScript-Imports
- PowerShell-Script-/Funktionsabhaengigkeiten
- Tests -> getestete Produktdateien/Klassen
- Migration -> betroffene Tabellen
- Repository/Service -> verwendete Tabellen, soweit statisch zuverlaessig ableitbar

Zweck ueber reine Navigation hinaus: Grundlage fuer ein kuenftiges Context-Budget-/
Wartbarkeits-Gate - nicht nur "welche Dateien werden geaendert?" (wie heute
`gitops.expected_git_files()`/`allowed_changed_files`), sondern "welche Dateien/Symbole
muessen wegen realer Abhaengigkeiten gleichzeitig verstanden werden?".

## 5. Offene Fragen, falls angenommen (hier nicht entschieden)

- **Governance-Pfad**: eigenes Gate/eigene BRIDGE-Auftragsfolge, nicht im laufenden Auftrag
  mitgezogen (wie bei jeder neuen Architektur, `ACB-UMSETZUNGSKONZEPT-V2.md` §1 "ein Auftrag
  = ein Bereich").
- **Technischer Spike vor Festlegung**: Tree-sitter-Grammatik-Abdeckung fuer PHP/JS/
  PowerShell real pruefen, bevor der Symbol-Graph-Indexer beauftragt wird.
- **Wer baut/pflegt** den Symbol-/Datei-Graph (Claude Code, Codex, eigenes Tooling) - nicht
  Teil dieser Spezifikation.
- **Schema fuer Context-Assembler** (Abschnitt 3) - neue Datei/neues Objekt oder Erweiterung
  von `result.schema.yaml`? Nur als Sketch vorbereitet, nicht entworfen.
- **Routing-Feld** (Abschnitt 2) - welches Schema-Feld das Flag-Routing konkret trägt, ist
  offen.
- **Decision-Log-Schema** selbst (`schemas/decision.schema.yaml`) bleibt die bereits in
  `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` §5 benannte, eigene Folgefrage.

## 6. Was das NICHT ist

Keine Aenderung an `CLAUDE.md`, `project.schema.yaml` oder `task.schema.yaml`. Kein
Indexer-Code, kein Symbol-Graph-Code, kein Context-Assembler-Code. Keine Festlegung auf
Tree-sitter ohne Spike. Keine Aussage zu BRIDGE-0073 Option B selbst (unveraendert gueltig,
siehe ENTSCHEIDUNG-V2 §7).
