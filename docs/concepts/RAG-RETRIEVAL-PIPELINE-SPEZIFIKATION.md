# RAG-Retrieval-/Injection-Pipeline - Spezifikation

**Spezifikation, keine Implementierung.** Stand BRIDGE-0088 (Handover v16 §6 Punkte 4/5).
Kein Code, kein Schema-Eintrag; legt nur fest, was `rag query` kuenftig liefern muss und
woran sich das gegen den bestehenden Code (`rag_prereqs.py`, `gitops.rag_index_sync`,
`project.schema.yaml`, `task.schema.yaml`, `result.schema.yaml`) bindet.

## 1. Begriffe

| Begriff | Definition | Feldort | Code-Bezug |
|---|---|---|---|
| `structured_coverage` | Welche Quellen (Dateien/Dokumente/Steuerchat-Sessions) je Projekt bereits strukturiert konsolidiert sind - der jeweils aktuelle Ist-Zustand (kein fester Zielwert/Soll definiert). | Neues, hier nicht spezifiziertes Feld je Projekt (kuenftiger eigener Auftrag); **kein** Ersatz fuer `rag_enabled`/`rag_index_repo`. | Muss gegen `projects/<id>/project.yaml: rag_enabled` (`project.schema.yaml:62`) und `rag_index_repo` (`:70`) gelesen werden: `rag_enabled=false` -> `structured_coverage` fuer dieses Projekt irrelevant (keine Retrieval-Anfrage), `rag_enabled=true` ohne `rag_index_repo` -> `structured_coverage` kann sich nur auf den strukturierten Bestand beziehen, nie auf das Archiv (Punkt 3 unten). |
| `migration_status` | Was am strukturierten Bestand noch fehlt (offene Quellen, teilweise erfasste Dateien) - die Luecke zwischen diesem Ist-Zustand und vollstaendiger Konsolidierung (kein fester Soll-Wert definiert). | Siehe `structured_coverage`, gleicher Ort, kuenftiger Auftrag. | **`rag_used_since` taugt dafuer nicht** (siehe Abschnitt 2) - eigenes Feld noetig. |
| `archive_fallback_policy` | Regel, wann ein Archivtreffer (Vektor-RAG aus `rag-index`) ueberhaupt herangezogen werden darf. | Policy-Text, kein Datenfeld. | Bindet an `gitops.rag_index_sync` (liefert nur den *Klon-Stand*, keine inhaltliche Pruefung) und `rag_prereqs.check()` (liefert nur *Erreichbarkeit*). Keines der beiden Module bewertet die inhaltliche Gueltigkeit eines Treffers - das ist Aufgabe dieser Policy, nicht der Infrastrukturschicht. |
| `context_sources_used` | Welche Quellen eine konkrete Steuerchat-Sitzung tatsaechlich als Kontext erhalten haben - Protokollfeld (Ist, pro Sitzung), kein Soll. | Neues Feld im kuenftigen `result.yaml` einer Retrieval-Anfrage oder in `rag/sources.yaml` (Abschnitt 3) - hier nicht final verortet. | Abgrenzung: `structured_coverage` = Ist-Stand je Projekt (zeitlos, zum jeweiligen Abfragezeitpunkt), `migration_status` = Luecke zwischen diesem Ist-Stand und vollstaendiger Konsolidierung (zeitlos), `context_sources_used` = Ist einer einzelnen Sitzung (zeitpunktgebunden). Keine der drei Grossen ersetzt eine andere. |
| Quellenprioritaet | Rangfolge bei Konflikt: strukturierter Bestand (`structured_coverage`) hat Vorrang vor Archivtreffern. | Policy-Regel, kein Feld. | Folgt direkt aus `archive_fallback_policy` (Punkt 3): ein Archivtreffer darf einen bereits strukturiert konsolidierten Stand nie stillschweigend ueberschreiben, nur als Hintergrundmaterial ergaenzen, solange er ungeprueft ist. |
| Revisionsbindung | Jede gelieferte Quelle ist an Repository + Commit (oder definierten Snapshot) gebunden, nie nur an einen Dateipfad - wichtig nach Umbenennungen. | Kein Parallelmechanismus; nutzt dieselben Felder wie bestehende Lauf-Ergebnisse. | Bindet an `result.schema.yaml`: `head` (`:190`, Pflichtfeld, HEAD-SHA am Lauf-Ende), `base_head` (`:185`, HEAD-SHA zu Laufbeginn), `task_hash` (`:224`, optionaler Hash der Task-Datei). Eine Retrieval-Quelle traegt denselben Dreiklang (Repo-Pfad + SHA, nicht Dateipfad allein) statt eines eigenen Formats. |
| Pflichtkontext | Quellen, die eine Steuerchat-Sitzung *immer* erhaelt, unabhaengig vom Suchtreffer. | Policy-Liste, kein Datenfeld. | Mindestens: aktueller Stand aller offenen `work-packages/BRIDGE-xxx.md` (laufende Auftraege), die zuletzt committete Handover-Datei (`docs/handover/ACB-UEBERGABE-v*.md`), offene `OpenIssue`-Eintraege (`schemas/open-issue.schema.yaml`). Keine Retrieval-Logik ersetzt diese drei - sie werden immer mitgeliefert, nicht gesucht. |
| Blocker bei fehlenden Quellen | Verhalten, wenn Pflichtkontext nicht lieferbar ist (z. B. `rag_prereqs.check()` meldet fehlende Infrastruktur). | Policy-Entscheidung auf Ebene der Retrieval-Pipeline, **nicht** auf Ebene von `rag_prereqs`/`rag_index_sync` selbst. | `rag_prereqs.check()` und `gitops.rag_index_sync()` bleiben unveraendert fail-soft (werfen nie, melden `missing`/`error`, Handover v16 §3) - das aendert diese Spezifikation nicht. Die Retrieval-Pipeline *darueber* entscheidet: fehlt **Pflichtkontext** (s. o.), wird die Sitzung mit einem `BLOCKED`/Klaerungsauftrag markiert, statt ohne diesen Kontext fortzufahren. Fehlt nur ein **optionaler** Archivtreffer, bleibt es fail-soft (Sitzung laeuft ohne ihn weiter) - genau dieselbe Unterscheidung wie Pflicht- vs. Archivquelle in den Punkten 3/5/7. |
| Herkunftsnachweis | Jede injizierte Information traegt Datei + Revision (bzw. definierter Snapshot) **und** konkrete Fundstelle; ein reiner Steuerchat-Session-Verweis reicht allein **nicht** - Steuerchat-Sitzungen sind keine dauerhaft referenzierbare, versionierte Quelle, jede Aussage muss auf eine dauerhaft zugaengliche Quelle zurueckfuehrbar sein. | Folgt direkt aus Revisionsbindung (s. o.) + `context_sources_used`. | Kein eigenes Feld - Kombination aus den beiden genannten Mechanismen deckt dies ab. |

## 2. `rag_used_since` - explizite Antwort

`rag_used_since` (`task.schema.yaml:158`, aktuell immer `null`, "reserviert fuer eine
kuenftige Retrieval-Pipeline") ist ein **Task-Feld**: ein Zeitpunkt, seit dem *ein einzelner
Auftrag* RAG-Kontext bezieht. `migration_status` ist dagegen ein **Projekt-weiter Soll/Ist-
Abgleich** (welche Quellen insgesamt fehlen) - unabhaengig davon, ob und wann ein einzelner
Task RAG genutzt hat. Ein Projekt kann `migration_status` = "60 % erfasst" haben, obwohl noch
kein einziger Task `rag_used_since` gesetzt hat (RAG noch nie tatsaechlich abgefragt), und
umgekehrt kann ein Task laengst `rag_used_since` tragen, ohne dass sich `migration_status`
dadurch aendert (die Abfrage bezieht sich auf den jeweils aktuellen Stand, konsolidiert nichts
nachtraeglich). `rag_used_since` bleibt also als reiner Nutzungs-Zeitstempel pro Task bestehen;
`migration_status` braucht ein eigenes, hier nicht spezifiziertes Projekt-Feld (siehe Tabelle
oben).

## 3. Archiv vs. strukturierter Bestand

Ein Treffer aus dem Vektor-Archiv (`rag-index`, `gitops.rag_index_sync`) ist **Hintergrund-
material**, bis seine Aussage geprueft und in den strukturierten Bestand uebernommen ist. Ein
Aehnlichkeitswert oder ein Datum allein macht einen Treffer nicht verbindlich - weder "neuer"
noch "aehnlicher" heisst "gueltiger". Verbindlich wird eine Aussage erst durch Uebernahme in
`structured_coverage` (Quellenprioritaet, Abschnitt 1).

## 4. Quellen-Manifest `rag/sources.yaml` (Grundlage)

Grobstruktur je Eintrag (kein Schema, nur Grundlage fuer einen kuenftigen Auftrag):

- `source_path` - Pfad relativ zum jeweiligen Repo.
- `repo` + `revision` - Revisionsbindung (Abschnitt 1), kein Dateipfad allein.
- `coverage_state` - `structured` | `archived_only` | `missing` (verbindet `structured_coverage`
  und `migration_status`).
- `[entscheidungsabhaengig, siehe ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2]`: `supersedes`/
  `affects`/`implemented_by`/`verified_by` wuerden die Quellenabdeckung praeziser machen (klaert,
  *warum* ein Dokument nicht mehr fuehrend ist, statt nur *dass* es das nicht mehr ist) - ohne
  diese Struktur bleibt `coverage_state` grobkoernig, aber vollstaendig nutzbar: ein fehlender
  oder veralteter Eintrag ist ueber `migration_status` trotzdem sichtbar, nur ohne die feinere
  Begruendung.

Coverage-Check: ein kuenftiger Lauf vergleicht `rag/sources.yaml` gegen den tatsaechlichen
Dateibestand der referenzierten Repos (fehlende/neue Dateien, geaenderte Revision seit letztem
Eintrag) - reine Lesepruefung, analog `rag_prereqs.check()`, nie werfend.

## 5. Pipeline-Ablauf (zusammengefasst)

1. Pflichtkontext laden (Abschnitt 1) - fehlt er, Abschnitt "Blocker bei fehlenden Quellen".
2. `structured_coverage` fuer das Projekt pruefen (nur wenn `rag_enabled=true`).
3. Bei Luecke (`migration_status`): optional Archivtreffer aus `rag-index` ergaenzen, markiert
   als ungeprueftes Hintergrundmaterial (Abschnitt 3), niemals als gleichrangig zum
   strukturierten Bestand.
4. Jede tatsaechlich gelieferte Quelle in `context_sources_used` protokollieren, mit
   Revisionsbindung + Herkunftsnachweis (Abschnitt 1).

Alle entscheidungsabhaengigen Praezisierungen sind im Text mit
`[entscheidungsabhaengig, siehe ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2]` markiert; ohne
sie bleibt diese Spezifikation vollstaendig umsetzbar.
