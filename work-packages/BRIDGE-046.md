# BRIDGE-0046 - Housekeeping: Haken und fehlende Handover (Punkt 7)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0046 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / DOCS |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - Abgleich Haken gegen Nachweis, keine Entwurfsentscheidung. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0045 |
| Gate | G1 |
| stop_conditions | SCOPE_VIOLATION |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Offene Akzeptanz-Haken in WP 027, 028, 029, 0039, 0040 gegen Nachweis pruefen. Fehlende Handover v4/v5 vermerken.

## Scope
work-packages/BRIDGE-027.md, -028.md, -029.md, -0039.md, -0040.md, docs/handover/HANDOVER.md.

## Schritte
1. Je offenem `[ ]`: Nachweis in results/<ID>/RUN-*/result.yaml (acceptance_results) oder `git log`/Tests suchen.
2. Nur mit Nachweis auf `[x]`. Ohne Nachweis offen lassen und in --summary listen (kein Raten).
3. HANDOVER.md: 1 Zeile 'CCB-UEBERGABE-v4/v5 nicht im Repo (Stand 2026-09-19), nicht rekonstruiert'.
4. Nur MELDEN (nicht aendern): WP-Dateien 0039-0041 sind 4-stellig benannt, `--commit`-Whitelist erwartet 3-stellig.
5. Commit: `git add` NUR die genannten Pfade (Whitelist deckt sie nicht ab), `git commit`, `git push`.

## Tests
Keine (nur Doku).

## Akzeptanzkriterien
- [ ] Haken nur mit Nachweis gesetzt
- [ ] Nicht belegte Haken in --summary gelistet
- [ ] HANDOVER.md-Vermerk zu v4/v5
- [ ] Hinweis zu 4-stelligen WP-Namen gemeldet
