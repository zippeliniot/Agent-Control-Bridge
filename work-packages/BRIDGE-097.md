# BRIDGE-0097: Decision-Log-Schema entwerfen

| Feld | Wert |
|---|---|
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| Scope | `schemas/decision.schema.yaml`, `tests/test_decision_schema.py` |

## Anlass

`ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` §5 nennt `schemas/decision.schema.yaml`
als eigene, hier nicht mitentschiedene Folgefrage - April hat der Formalisierungsebene aus
§3 zugestimmt (§7), das Schema selbst war noch nicht entworfen.

## Entscheidung zum Umfang (bewusste Abgrenzung)

Nur das Schema fuer **ein Ereignis** (append-only, analog `audit/audit.jsonl`-Zeilen) -
**keine** CLI-Anbindung (`bridge decision ...`), **keine** Store-Methode, **keine**
Festlegung der Ablageform (eine Datei pro `decision_id` mit Ereignisliste vs. ein
Verzeichnis mit einer Datei pro Ereignis). Das waere ein eigener, grösserer
Implementierungsauftrag (konsistent mit der bereits in BRIDGE-0092/0095 gelebten
Scope-Disziplin).

## Ergebnis

`schemas/decision.schema.yaml`: `decision_event`-Objekt mit den vier Ereignistypen
(PROPOSED/ACCEPTED/REJECTED/REVOKED/SUPERSEDED - fuenf, PROPOSED ergaenzt die drei in
§3a genannten um die Entstehung selbst), `supersedes` mit Geltungsbereich pro Eintrag
(§3a, teilweise Abloesung), getrennte `origin_task_id`/`applies_to`/`affected_task_ids`/
`source_refs` (§3b) statt einem Feld, `affects`/`implemented_by`/`verified_by` als
Repo+Commit-gebundene Referenzen (§3c, `$defs/revision_ref`). `superseded_by` bewusst
**nicht** als Feld modelliert - laut §3a nur eine berechnete Ansicht.

## Akzeptanzkriterien

- [x] Schema ist valides JSON-Schema (Draft 2020-12), `additionalProperties: false`
- [x] Alle vier/fuenf Ereignistypen aus §3a abgedeckt
- [x] `supersedes` traegt einen Geltungsbereich pro Eintrag, nicht nur einen Verweis
- [x] `affects`/`implemented_by`/`verified_by`/`source_refs` sind Repo+Commit-gebunden
- [x] 10 neue Tests (gueltiges Dokument, jede Ablehnungsart, Teil-Abloesung,
  Revisionsbindung) - volle Suite gruen (591/591)
- [x] Scope-Abgrenzung (kein CLI/Store) explizit begruendet
