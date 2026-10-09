# BRIDGE-0093: Mehrprojekt-RAG spezifizieren (Vorbedingung Drei-Schichten-Architektur)

| Feld | Wert |
|---|---|
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| Scope | `docs/concepts/MEHRPROJEKT-RAG-SPEZIFIKATION.md` |

## Anlass

`ENTSCHEIDUNG-DREI-SCHICHTEN-STEERING-CONTINUITY.md` §3 nennt die Mehrprojekt-RAG-Frage
(v16 §6 Punkt 6, seitdem unveraendert bis v18 §6 Punkt 5) als Vorbedingung, bevor die
Drei-Schichten-Architektur fuer Steering Continuity spezifiziert werden kann. April hat
09.10.2026 im Steuerchat bestaetigt: zuerst Mehrprojekt-RAG loesen, danach erst die
Drei-Schichten-Spezifikation beginnen.

## Ergebnis

Konvention festgelegt: ein Repo/ein Klon (`rag-index`, unveraendert), Unterordner pro
`project_id` darin. Kein Code-/Schema-Bedarf, da `rag_index_clone_path()` und
`rag_index_sync()` bereits projekt-unabhaengig korrekt sind (gegen echten Code in
`src/bridge/runner.py`/`gitops.py` geprueft) und kein Indexer-/Query-Code existiert, der
geaendert werden muesste. Details: `docs/concepts/MEHRPROJEKT-RAG-SPEZIFIKATION.md`.

## Akzeptanzkriterien

- [x] Ist-Zustand gegen echten Code geprueft (`runner.rag_index_clone_path`,
  `gitops.rag_index_sync`), nicht aus einer Uebergabedatei rekonstruiert
- [x] Zielkonvention (Unterordner pro `project_id`) spezifiziert, Code-Aenderungsbedarf
  explizit auf "keiner jetzt, erst mit erstem Indexer-Auftrag" eingegrenzt
- [x] Push-Retry-Frage (v16 Punkt 6) beantwortet - bestehender BRIDGE-029-Mechanismus
  wiederverwendbar, kein neuer Mechanismus
- [x] Vorbedingung fuer Drei-Schichten-Architektur ausdruecklich als aufgeloest markiert
