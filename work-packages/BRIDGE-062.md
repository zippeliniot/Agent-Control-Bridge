# BRIDGE-0062 - Claim/Lease-API

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0062 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Neue API-Schicht, klar begrenzt. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | BRIDGE-0061 |
| Gate | G3 |
| stop_conditions | CONCEPT_CONFLICT |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Python-API + CLI `bridge claim/release` mit Lease (Ablaufzeit).

## Scope
src/bridge/claim.py (neu), src/bridge/cli.py, tests/test_claim.py (neu).

## Schritte
1. `claim(store, id, actor, machine, lease_seconds)` schreibt results/<id>/claim.json (actor, machine, expires_at).
2. Aktiver fremder Claim -> Fehler. Abgelaufener Claim darf uebernommen werden (Audit-Reason).
3. `release`, `renew`. Alles ueber writer_lock.

## Tests
`python -m unittest tests.test_claim`, dann volle Suite EINMAL.

## Akzeptanzkriterien
- [ ] claim/release/renew vorhanden
- [ ] Fremder aktiver Claim abgelehnt (Test)
- [ ] Abgelaufener Claim uebernehmbar (Test)
