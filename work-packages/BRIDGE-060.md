# BRIDGE-0060 - B5 Store-Haertung: atomar + Writer-Lock

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0060 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel / FEATURE |
| Teile (alte Nummern) | 0058, 0060 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Store-Haertung: atomare Writes + Writer-Lock, Nebenlaeufigkeit. |
| Modellwechsel zum Vorgaenger | JA |
| depends_on | BRIDGE-0059 |
| Gate | G2 |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0060` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

**Teile strikt nacheinander (A, B, ...). Pro Teil: Haken setzen, Commit, Push. Scheitert ein Teil: STOPP (BLOCKED), spaetere Teile nicht beginnen.**

### Teil A (alt 0058) - Atomare Store-Writes
**Ziel:** Schreiben ueber Temp-Datei im selben Ordner + `os.replace`.
**Scope:** src/bridge/store.py, src/bridge/heartbeat.py, tests/test_store.py.
1. Helper `_atomic_write(path, text)` (Temp im Zielordner, flush+fsync, `os.replace`).
2. Einsetzen bei create_task, save_task, write_result, write_draft, Heartbeat.
3. Test: Fehler zwischen Schreiben und Replace laesst Originaldatei unveraendert.
**Tests:** `python -m unittest tests.test_store tests.test_watcher`, dann volle Suite EINMAL.
- [x] Alle Schreibpfade atomar
- [x] Fehlerfall-Test gruen
- [x] Kein Temp-Rest nach Fehler (Test)

### Teil B (alt 0060) - Writer-Lock und sicheres Audit-Append
**Ziel:** Dateilock `.acb-writer.lock` fuer alle Store-Schreibpfade + Append nach Entscheidung 0059.
**Scope:** src/bridge/lock.py (neu), src/bridge/store.py, .gitignore (1 Zeile), tests/test_lock.py (neu).
1. VORAB: ENTSCHEIDUNG-AUDIT.md `Status: FREIGEGEBEN`, sonst STOPP.
2. `writer_lock(root, timeout)`: exklusives Anlegen (O_EXCL) mit pid+Zeit; reentrant im selben Prozess; alter Lock (>300 s) -> Fehler mit Hinweis, NICHT automatisch brechen.
3. Alle Store-Schreibmethoden nutzen den Lock.
4. Audit-Append laut Entscheidung.
**Tests:** `python -m unittest tests.test_lock tests.test_store`, dann volle Suite EINMAL.
- [x] Lock schuetzt alle Schreibpfade
- [x] Zweiter Writer wartet/scheitert sauber (Test)
- [x] Stale Lock wird gemeldet, nicht gebrochen (Test)
- [x] Lockdatei in .gitignore
