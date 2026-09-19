# BRIDGE-0049 - B2 Draft-Grundlage: Schema, Ablage, task brief

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0049 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel / FEATURE |
| Teile (alte Nummern) | 0049, 0051, 0052 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Draft-Schema + Store-Erweiterung + kleines Lese-CLI, ein Bereich. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | BRIDGE-0047 |
| Gate | G1 |
| stop_conditions | SCOPE_VIOLATION |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0049` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

**Teile strikt nacheinander (A, B, ...). Pro Teil: Haken setzen, Commit, Push. Scheitert ein Teil: STOPP (BLOCKED), spaetere Teile nicht beginnen.**

### Teil A (alt 0049) - Draft-Schema draft-a-1
**Ziel:** Neues Schema fuer Executor-Drafts + optionale Felder tests/findings im Result-Schema.
**Scope:** schemas/draft.schema.yaml (neu), schemas/result.schema.yaml (additiv), schemas/README.md (1 Zeile), tests/test_store.py.
1. draft.schema.yaml: kind `bridge_draft`, `draft_version` const `draft-a-1`, bridge_task_id, run_id, status (COMPLETED|BLOCKED|FAILED|INTERRUPTED), summary, base_head, head_after, branch, repository, changed_files, tests{passed,failed,blocked}, findings[{id,severity,text}], next_action, error_code (optional). additionalProperties false.
2. result.schema.yaml: optional `tests` und `findings` (gleiche Form). Additiv.
3. Tests: gueltiger Draft, fehlendes Pflichtfeld, unbekanntes Feld, falsche draft_version.
**Tests:** `python -m unittest tests.test_store`.
- [x] draft.schema.yaml gueltig (Draft 2020-12)
- [x] result.schema additiv erweitert
- [x] 4 Schema-Tests gruen
- [x] Alte result.yaml weiter gueltig

### Teil B (alt 0051) - Draft-Ablage im Store
**Ziel:** `Store.write_draft/load_draft` unter drafts/<id>/RUN-yy/draft.yaml. Kein Ueberschreiben.
**Scope:** src/bridge/store.py, docs/protocols/storage-layout.md (4 Zeilen), tests/test_store.py.
1. `write_draft(doc)`: validiert gegen draft.schema, Auftrag muss existieren, Ziel darf nicht existieren, Pfad nur unter drafts/.
2. `load_draft(id, run_id)`.
3. Kein Audit-Ereignis, kein Statuswechsel (das macht der Import).
4. Layout-Doku: drafts/ ergaenzen.
**Tests:** `python -m unittest tests.test_store`.
- [ ] write_draft/load_draft vorhanden
- [ ] Ueberschreiben abgelehnt (Test)
- [ ] Pfad ausserhalb drafts/ abgelehnt (Test)
- [ ] Kein Audit-Eintrag durch write_draft (Test)

### Teil C (alt 0052) - CLI: task brief (tokenarmer Kurzauftrag)
**Ziel:** `bridge task brief <id>`: max. 15 Zeilen Pflichtkontext (Klasse A). Rein lesend.
**Scope:** src/bridge/cli.py, tests/test_cli.py.
1. Ausgabe: id, status, task_type, model, reasoning_level, expected_head, allowed_paths, forbidden_actions, stop_conditions, erste 5 acceptance_criteria, Pfad des Work-Packages.
2. Fehlende Felder als `-`. Unbekannte ID -> Exit 1.
3. Kein Schreibzugriff.
**Tests:** `python -m unittest tests.test_cli`.
- [ ] Kommando vorhanden, max. 15 Zeilen
- [ ] Unbekannte ID Exit 1 (Test)
- [ ] Alter Auftrag ohne neue Felder funktioniert (Test)
