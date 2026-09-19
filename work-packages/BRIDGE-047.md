# BRIDGE-0047 - B1 Schema-Basis: push_mode, Task-Felder, Fehlercodes

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0047 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel / FEATURE |
| Teile (alte Nummern) | 0047, 0048, 0050 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Additive Schema-/Loader-Aenderungen; hoechste Einzelstufe der Teile. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0046 |
| Gate | G1 |
| stop_conditions | CONCEPT_CONFLICT, SCOPE_VIOLATION |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0047` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

**Teile strikt nacheinander (A, B, ...). Pro Teil: Haken setzen, Commit, Push. Scheitert ein Teil: STOPP (BLOCKED), spaetere Teile nicht beginnen.**

### Teil A (alt 0047) - Profilfeld push_mode
**Ziel:** Optionales Feld `push_mode` (direct|draft, Default direct) im Projektprofil.
**Scope:** schemas/project.schema.yaml, src/bridge/profiles.py, tests/test_profiles.py, docs/architecture/ARCHITECTURE.md (1 Absatz).
1. VORAB: docs/concepts/ENTSCHEIDUNG-PUSH-MODELL.md muss `Status: FREIGEGEBEN` tragen, sonst STOPP (CONCEPT_CONFLICT).
2. Schema: `push_mode` enum [direct, draft], default direct. Additiv.
3. profiles.py: `get_push_mode(profile) -> str` (Default `direct`).
4. Alle 8 bestehenden Profile bleiben ohne Aenderung gueltig.
**Tests:** `python -m unittest tests.test_profiles`, dann volle Suite EINMAL.
- [x] Entscheidung war FREIGEGEBEN
- [x] push_mode im Schema, Default direct
- [x] get_push_mode vorhanden
- [x] Ungueltiger Wert wird abgelehnt (Test)
- [x] Alle Profile unveraendert gueltig

### Teil B (alt 0048) - Task-Schema: task_type, allowed_paths, forbidden_actions, stop_conditions
**Ziel:** Vier optionale Felder in task.schema.yaml. Kein CLI-Umbau.
**Scope:** schemas/task.schema.yaml, tests/test_store.py.
1. `task_type` enum [T0..T5], default null.
2. `allowed_paths`, `forbidden_actions`: array of string, default [].
3. `stop_conditions`: array, Enum [IDENTITY_MISMATCH, HEAD_MISMATCH, DIRTY_WORKTREE, CONCEPT_CONFLICT, SCOPE_VIOLATION], default [].
4. Bestehende task.yaml bleiben gueltig (Regressionstest).
**Tests:** `python -m unittest tests.test_store`.
- [x] 4 Felder additiv im Schema
- [x] Unbekannter stop_condition-Wert abgelehnt (Test)
- [x] Alte task.yaml weiter gueltig (Test)

### Teil C (alt 0050) - Fehlercodes als SSOT
**Ziel:** schemas/error-codes.yaml + Mini-Loader. Codes mappen auf Zustand BLOCKED (kein neuer Zustand).
**Scope:** schemas/error-codes.yaml (neu), src/bridge/errorcodes.py (neu), tests/test_errorcodes.py (neu).
1. error-codes.yaml: 5 Codes aus BRIDGE-0048, je `description`, `state: BLOCKED`.
2. errorcodes.py: `load_error_codes(schema_dir)`, `is_known(code)`.
3. Test: Schluessel == Enum `stop_conditions` in task.schema.yaml (SSOT-Gleichheit).
**Tests:** `python -m unittest tests.test_errorcodes`, dann volle Suite EINMAL.
- [x] error-codes.yaml + Loader vorhanden
- [x] SSOT-Gleichheitstest gruen
- [x] state-model.yaml unveraendert
