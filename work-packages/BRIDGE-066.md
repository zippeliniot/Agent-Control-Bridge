# BRIDGE-0066 - Dorfschaft Read-only-Pilot

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0066 |
| project_id | agent-control-bridge |
| Typ / Klasse | T3 / INTEGRATION |
| Rechte | READ_ONLY, GIT_PUSH |
| **Modell / Denkstufe** | **Codex-Modell (April tragen ein) / LOW** - Mechanischer Read-only-Lauf durch Codex unter ChatGPT-Kontrolle. |
| Modellwechsel zum Vorgaenger | JA |
| depends_on | BRIDGE-0065 |
| Gate | G5 |
| stop_conditions | IDENTITY_MISMATCH, HEAD_MISMATCH |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
integration_readonly.py gegen das echte Dorfschaft-Repo, rein lesend, mit Pre-Flight-Head-Check.

## Scope
Nur lesen. Ausgabe in separaten --out-Ordner ausserhalb des Zielrepos.

## Schritte
1. VORAB: WSL-Pfad + erwarteter HEAD von April bestaetigt (aus docs/ACB-DORFSCHAFT-PILOT.md), sonst BLOCKED (IDENTITY_MISMATCH).
2. Befehl laut Checkliste mit `--expected-head`.
3. Ergebnis: PASS/FAIL/BLOCKED + Pfad der result.yaml in --summary. Bei PASS: Empfehlung 'Integrationsfreigabe' (Entscheidung bei April).

## Tests
Keine weiteren.

## Akzeptanzkriterien
- [ ] Pre-Flight-Check bestanden oder BLOCKED gemeldet
- [ ] Zielrepo unveraendert (HEAD+Status vorher==nachher)
- [ ] Ergebnis in --summary
