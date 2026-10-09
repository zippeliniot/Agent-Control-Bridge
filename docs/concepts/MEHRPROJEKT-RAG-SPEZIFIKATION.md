# Mehrprojekt-RAG - Spezifikation

**Spezifikation, keine Implementierung.** Stand BRIDGE-0093 (v16 §6 Punkt 6, zuletzt
unveraendert in v18 §6 Punkt 5). Kein Code, kein Schema-Eintrag. Loest die in
`ENTSCHEIDUNG-DREI-SCHICHTEN-STEERING-CONTINUITY.md` §3 genannte Vorbedingung
("Diese Architektur setzt die Loesung von v16 §6 Punkt 6 voraus, loest sie aber nicht
selbst") auf Konventionsebene, bevor die Drei-Schichten-Architektur selbst spezifiziert wird.

## 1. Ist-Zustand (gegen echten Code geprueft)

Ein einziger, projekt-unabhaengiger lokaler Klon:

- `runner.rag_index_clone_path(store)` (`src/bridge/runner.py:213-218`): immer
  `<store.root>/../rag-index` - **kein** `project_id`-Parameter.
- `gitops.rag_index_sync(repo_root)` (`src/bridge/gitops.py:383-...`): reiner
  `git pull` + `git lfs pull` auf genau diesem einen Pfad, ebenfalls ohne `project_id`.
- Kein Indexer-/Query-Code existiert bisher (`rag query` ist laut
  `RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md` noch nicht spezifiziert). Das heisst:
  die Mehrprojekt-Frage ist **nicht** durch bestehenden Code blockiert, sondern eine
  Konventionsfrage, die vor dem ersten Indexer/Query-Code entschieden sein muss, damit
  der keine abweichende Struktur erfindet.

## 2. Zielkonvention

Ein Repo (`zippeliniot/acb-rag-index`), ein lokaler Klon pro Maschine (unveraendert:
`rag-index` als fuenfter Geschwisterklon, `rag_index_clone_path()` bleibt
unveraendert - der Klonpfad selbst ist projekt-unabhaengig, die Aufteilung passiert
**innerhalb** des Klons):

```
rag-index/
  <project_id>/
    sources.yaml        # Quellen-Manifest (RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md §4) - pro Projekt, nicht global
    chunks/              # projektspezifische Chunk-/Embedding-Artefakte (Format: kuenftiger Indexer-Auftrag)
```

Begruendung fuer Unterordner statt N getrennter Repos (v16 Punkt 6, hier bestaetigt statt
nur wiederholt): ein Repo haelt `git lfs`-Setup, Auth und `rag_index_sync()` fuer beliebig
viele Projekte identisch - jedes weitere Projekt (Dorfschaft eingeschlossen) braucht keinen
neuen Klon-Pfad, keine neue `rag_index_repo`-Zeile pro Projekt in `project.schema.yaml`,
sondern nur einen neuen Unterordner im selben, bereits funktionierenden Klon.

## 3. Was sich am bestehenden Code ändert - und was nicht

- `rag_index_clone_path()`: **unveraendert.** Liefert weiterhin den einen Klonpfad, nicht
  projektabhaengig - das ist richtig so, da es sich um denselben lokalen Klon fuer alle
  Projekte handelt.
- `rag_index_sync()`: **unveraendert.** Pull/LFS-Pull betrifft den gesamten Klon auf
  einmal, nicht einen Unterordner - ein Projekt, das zuerst synct, bringt automatisch auch
  die Unterordner aller anderen Projekte mit. Kein Mehrprojekt-spezifischer Code hier noetig.
- **Neu, aber erst mit dem ersten Indexer-/Query-Auftrag relevant:** jeder kuenftige Code,
  der in den Klon **schreibt** (Chunking, Embedding-Erzeugung) oder daraus **liest**
  (`rag query`), muss `project_id` als Pfadsegment verwenden
  (`rag_index_clone_path(store) / project_id / ...`), nie auf Klon-Wurzelebene schreiben.
  Diese Spezifikation legt die Konvention fest, ohne dass der Indexer-Code selbst hier
  mitgezogen wird (eigener, spaeterer Auftrag, siehe `RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md`).

## 4. Parallele Builds (Push-Retry)

v16 Punkt 6 nennt "Push-Retry fuer parallele Builds" als Teil des Konzepts. Kein neuer
Mechanismus noetig: `gitops.py` hat bereits einen generischen Non-Fast-Forward-Retry
(BRIDGE-029, `git fetch` + `git rebase` + ein weiterer Push-Versuch, siehe Modul-Docstring
`src/bridge/gitops.py:23-35`). Ein kuenftiger Indexer, der in `rag-index` pusht, **muss**
diesen bestehenden Mechanismus wiederverwenden (z. B. ueber `gitops.git_push_with_retry`,
falls so benannt, oder den gleichen Code-Pfad wie `git_commit(..., push=True)`) - keine
eigene Retry-Logik erfinden. Mehrere Projekte, die gleichzeitig in verschiedene
Unterordner desselben Klons schreiben, lösen Merge-/Rebase-Konflikte nur dann aus, wenn sie
in derselben Sekunde denselben Unterordner treffen - bei getrennten `project_id`-Unterordnern
betrifft ein Rebase-Konflikt (Audit-Log-Append o.ä., siehe Vorfall mit `audit/audit.jsonl`
in dieser Sitzung) nur Dateien **ausserhalb** der `project_id`-Trennung, also selten.

## 5. Ergebnis fuer die Drei-Schichten-Architektur

Die Vorbedingung aus `ENTSCHEIDUNG-DREI-SCHICHTEN-STEERING-CONTINUITY.md` §3 ist mit dieser
Konvention aufgeloest: Dorfschaft bekommt einen eigenen `dorfschaft/`-Unterordner im
bestehenden `rag-index`-Klon, ohne neuen Klon, neue Schema-Zeile oder neuen Sync-Code.
Die Drei-Schichten-Architektur kann die "Vektor-RAG (Archiv)"-Schicht damit als
projekt-parametrisierten Zugriff auf `rag_index_clone_path(store) / project_id / ...`
spezifizieren, statt die Mehrprojekt-Frage erneut offenzulassen.

## 6. Was das NICHT ist

Kein Indexer, kein `rag query`, keine Aenderung an `rag_prereqs.py` (Erreichbarkeits-Check
bleibt projekt-unabhaengig - Ollama/Modell sind Maschineneigenschaften, nicht
Projekteigenschaften). Keine Aenderung an `project.schema.yaml` - `rag_index_repo` bleibt
ein einzelner, globaler Repo-Slug, da es weiterhin nur ein Repo gibt.
