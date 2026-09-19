# BRIDGE-0061 - B6 Stufe B: Version/CAS + Claim/Lease

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0061 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel / FEATURE |
| Teile (alte Nummern) | 0061, 0062 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Stufe B: CAS + Claim/Lease, beides mit Freigabe G3. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | BRIDGE-0060 |
| Gate | G3 |
| stop_conditions | CONCEPT_CONFLICT |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0061` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

**Teile strikt nacheinander (A, B, ...). Pro Teil: Haken setzen, Commit, Push. Scheitert ein Teil: STOPP (BLOCKED), spaetere Teile nicht beginnen.**

### Teil A (alt 0061) - Version und CAS (Stufe B)
**Ziel:** `task_version` + optionales `expected_version` in set_status/save_task.
**Scope:** schemas/task.schema.yaml, src/bridge/store.py, tests/test_store.py.
1. VORAB: ausdrueckliche Stufe-B-Freigabe von April im Chat (G3), sonst STOPP.
2. Schema: `task_version` int, default 1. Erhoeht sich bei jedem Speichern.
3. `expected_version` optional; Abweichung -> StoreError `VERSION_CONFLICT`, nichts geschrieben.
4. Ohne expected_version: Verhalten unveraendert.
**Tests:** `python -m unittest tests.test_store`, dann volle Suite EINMAL.
- [ ] Freigabe G3 dokumentiert
- [ ] CAS-Konflikt lehnt ab (Test)
- [ ] Altes Verhalten unveraendert (Test)

### Teil B (alt 0062) - Claim/Lease-API
**Ziel:** Python-API + CLI `bridge claim/release` mit Lease (Ablaufzeit).
**Scope:** src/bridge/claim.py (neu), src/bridge/cli.py, tests/test_claim.py (neu).
1. `claim(store, id, actor, machine, lease_seconds)` schreibt results/<id>/claim.json (actor, machine, expires_at).
2. Aktiver fremder Claim -> Fehler. Abgelaufener Claim darf uebernommen werden (Audit-Reason).
3. `release`, `renew`. Alles ueber writer_lock.
**Tests:** `python -m unittest tests.test_claim`, dann volle Suite EINMAL.
- [ ] claim/release/renew vorhanden
- [ ] Fremder aktiver Claim abgelehnt (Test)
- [ ] Abgelaufener Claim uebernehmbar (Test)
