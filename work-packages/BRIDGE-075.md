# BRIDGE-0075 - Implementierung OpenIssue (Schema, Store, CLI, Tests)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0075 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel / FEATURE |
| Teile (alte Nummern) | keine (neuer Auftrag, kein Buendel-Altbestand) |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - additive Implementierung nach bereits freigegebener Entscheidung, kein T1. |
| Modellwechsel zum Vorgaenger | JA (BRIDGE-0074 war Claude Opus 5 / MEDIUM, T1-Entscheidung; dies ist T2-Implementierung) |
| depends_on | BRIDGE-0074 (ARCHIVED) |
| Gate | keines |
| stop_conditions | CONCEPT_CONFLICT, SCOPE_VIOLATION |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0075` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

**Teile strikt nacheinander (A, B, C). Pro Teil: Haken setzen, Commit, Push. Scheitert ein Teil: STOPP (BLOCKED), spaetere Teile nicht beginnen.**

**Vorbedingung (vor Teil A pruefen, nicht annehmen):** `docs/concepts/ENTSCHEIDUNG-OPENISSUE-FORMALISIERUNG.md` muss Status `FREIGEGEBEN` tragen. Steht dort noch `ENTWURF`: STOPP, `CONCEPT_CONFLICT`.

## Auftrag

**Ziel:** Option A aus `ENTSCHEIDUNG-OPENISSUE-FORMALISIERUNG.md` umsetzen: ein eigenstaendiges, projektunabhaengiges `OpenIssue`-Objekt mit Schema, Store-Anbindung und CLI-Unterbefehlen, damit offene Punkte ueber beliebig viele Steuerchat-Sitzungen strukturiert gefuehrt (angelegt, geschlossen, gefiltert gelistet) werden koennen, statt handgetragen in Freitext-Handover-Dateien fortgeschrieben zu werden. Keine Projekt-Fachwerte (kein Dorfschaft-Bezug in Schema/Code).

### Teil A - Schema und Store

**Scope:** `schemas/open-issue.schema.yaml` (neu), `src/bridge/store.py`, `tests/test_store.py`.

1. Neues Schema `schemas/open-issue.schema.yaml`, `additionalProperties: false` wie alle bestehenden Schemas. Pflichtfelder (aus `ENTSCHEIDUNG-OPENISSUE-FORMALISIERUNG.md` §2): `schema_version`, `kind: open_issue`, `issue_id` (Format `<project_id>-ISSUE-NNNN` oder analog, eindeutig je Projekt), `project_id`, `status` (geschlossenes Enum `[OPEN, CLOSED]`), `summary` (Kurzbezug, `minLength: 1`), `origin_task_id` (Bezug auf die entstehende `bridge_task_id` bzw. projektfremdes Pendant ueber `task_prefix`, `type: string`), `created_at`. Optional: `closed_at`, `closed_by`, `note`.
2. Store-Methoden in `store.py` analog zu `write_result`/`task show`-Mustern: `open_issue(...)` legt `open-issues/<project_id>/<issue_id>.yaml` an (neu, `_write_new`, Audit-Ereignis `ISSUE_OPENED`); `close_issue(issue_id, project_id, ...)` aendert `status` auf `CLOSED` plus `closed_at`/`closed_by` (einzige erlaubte Aenderung an einer bestehenden `open-issue.yaml`, unter Writer-Lock, Audit-Ereignis `ISSUE_CLOSED`); `list_open_issues(project_id=None)` liest alle Dateien unter `open-issues/` (optional nach `project_id` gefiltert), gibt nur `status: OPEN` zurueck sofern nicht `include_closed=True` uebergeben wird.
3. `issue_id`-Eindeutigkeit je `project_id` serverseitig erzwingen (Kollision -> `StoreError`), analog zu `_check_id` fuer `bridge_task_id`.
**Tests:** `python -m unittest tests.test_store`, dann volle Suite EINMAL.
- [ ] Schema vorhanden, `additionalProperties: false`
- [ ] `open_issue`/`close_issue`/`list_open_issues` implementiert und getestet
- [ ] Kollidierende `issue_id` abgelehnt (Test)
- [ ] `close_issue` auf bereits geschlossenem Issue -> Fehler, kein stiller Erfolg (Test)

### Teil B - CLI-Unterbefehle

**Scope:** `src/bridge/cli.py`, `tests/test_cli.py` (bzw. vorhandene CLI-Testdatei ergaenzen, Dateiname gegen echten Bestand pruefen statt annehmen).

1. Neue Befehlsgruppe `issue` nach dem Muster von `task`/`claim`/`run` (siehe `add_parser`-Struktur in `cli.py`):
   - `issue open --project-id <id> --summary "<text>" --origin-task-id <id>` -> legt an, gibt `issue_id` aus.
   - `issue close <issue_id> --project-id <id> [--note "<text>"]` -> schliesst.
   - `issue list [--project-id <id>] [--include-closed]` -> listet, Default nur offene.
2. Fehlermeldungen fail-closed (fehlendes Pflichtargument, unbekannte `issue_id`, unbekannte `project_id` gegen `projects/<id>/project.yaml` pruefen) - kein Raten, kein stiller Erfolg bei falscher ID.
**Tests:** CLI-Testdatei gezielt, dann volle Suite EINMAL.
- [ ] `issue open/close/list` funktionsfaehig (Test je Unterbefehl)
- [ ] Unbekannte `project_id`/`issue_id` -> klarer Fehler, kein stiller Erfolg (Test)

### Teil C - Dokumentations-Minimalverweis (kein Ablauf-Rewrite)

**Scope:** NUR `docs/ACB-STEUERCHAT-ARBEITSWEISE.md`, Abschnitt 4 ("ACB-Nutzung — Kurzreferenz"). Sonst nichts - insbesondere NICHT `docs/ACB-STEUERCHAT-STANDARDSTART.md`, NICHT `docs/handover/*` (das bleibt dem naechsten Handover-Update vorbehalten).

1. In Abschnitt 4 einen neuen Punkt ergaenzen: `issue open/close/list` als Mechanismus fuer offene Punkte ueber Sitzungen hinweg nennen (ein bis zwei Saetze, kein Ablauf-Rewrite, kein Verweis auf ein konkretes Projekt).
**Tests:** keine (reine Doku-Ergaenzung).
- [ ] Ein neuer, kurzer Verweis in Abschnitt 4, sonst keine Aenderung an der Datei

## Abschluss

1. Volle Suite EINMAL, nur die letzten 3 Zeilen zeigen.
2. `git status` sauber, dann Abschluss wie im Slash-Befehl.
- [ ] Volle Suite gruen
