# BRIDGE-0051 - Draft-Ablage im Store

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0051 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Store-Erweiterung, Schreibpfad, fail-closed. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0050 |
| Gate | G1 |
| stop_conditions | SCOPE_VIOLATION |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
`Store.write_draft/load_draft` unter drafts/<id>/RUN-yy/draft.yaml. Kein Ueberschreiben.

## Scope
src/bridge/store.py, docs/protocols/storage-layout.md (4 Zeilen), tests/test_store.py.

## Schritte
1. `write_draft(doc)`: validiert gegen draft.schema, Auftrag muss existieren, Ziel darf nicht existieren, Pfad nur unter drafts/.
2. `load_draft(id, run_id)`.
3. Kein Audit-Ereignis, kein Statuswechsel (das macht der Import).
4. Layout-Doku: drafts/ ergaenzen.

## Tests
`python -m unittest tests.test_store`.

## Akzeptanzkriterien
- [ ] write_draft/load_draft vorhanden
- [ ] Ueberschreiben abgelehnt (Test)
- [ ] Pfad ausserhalb drafts/ abgelehnt (Test)
- [ ] Kein Audit-Eintrag durch write_draft (Test)
