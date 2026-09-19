# BRIDGE-0046 - Housekeeping (Punkt 7) + M4-Tippfehler

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0046 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / DOCS |
| Teile (alte Nummern) | 0046 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - Abgleich Haken gegen Nachweis, keine Entwurfsentscheidung. |
| Modellwechsel zum Vorgaenger | - |
| depends_on | BRIDGE-0045 |
| Gate | G1 |
| stop_conditions | SCOPE_VIOLATION |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0046` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

## Auftrag
**Ziel:** Offene Akzeptanz-Haken in WP 027, 028, 029, 0039, 0040 gegen Nachweis pruefen. Fehlende Handover v4/v5 vermerken.
**Scope:** work-packages/BRIDGE-027.md, -028.md, -029.md, -0039.md, -0040.md, docs/handover/HANDOVER.md. docs/concepts/ENTSCHEIDUNG-PUSH-MODELL.md (nur Tippfehler + 1 Zeile). docs/ACB-STEUERCHAT-REFERENZ.md, docs/ACB-STEUERCHAT-STANDARDSTART.md (nur Pfadverweise).
1. Je offenem `[ ]`: Nachweis in results/<ID>/RUN-*/result.yaml (acceptance_results) oder `git log`/Tests suchen.
2. Nur mit Nachweis auf `[x]`. Ohne Nachweis offen lassen und in --summary listen (kein Raten).
3. HANDOVER.md: 1 Zeile 'CCB-UEBERGABE-v4/v5 nicht im Repo (Stand 2026-09-19), nicht rekonstruiert'.
4. Nur MELDEN (nicht aendern): WP-Dateien 0039-0041 sind 4-stellig benannt, `--commit`-Whitelist erwartet 3-stellig.
5. Commit: `git add` NUR die genannten Pfade (Whitelist deckt sie nicht ab), `git commit`, `git push`.
6. ENTSCHEIDUNG-PUSH-MODELL.md: in M4 `ird` -> `wird`. Am Ende 1 Zeile: `Nummern: Teilpakete 0048,0050 -> 0047; 0051,0052 -> 0049; 0054 -> 0053; 0056 -> 0055; 0058 -> 0060; 0062 -> 0061; 0064 -> 0063 (siehe Konzept §2).` Rest der Datei NICHT aendern (Status bleibt FREIGEGEBEN).
7. Pfadverweise `...\Agent-Control-Bridge\claude` als ACB-Entwicklungsklon -> `...\dev`: docs/ACB-STEUERCHAT-REFERENZ.md Z.25, docs/ACB-STEUERCHAT-STANDARDSTART.md Z.115 und Z.230 (per `git grep -n` pruefen). Historische Hinweise (REFERENZ Z.370) und machines.md NICHT aendern.
**Tests:** Keine (nur Doku).
- [ ] Haken nur mit Nachweis gesetzt
- [ ] Nicht belegte Haken in --summary gelistet
- [ ] HANDOVER.md-Vermerk zu v4/v5
- [ ] Hinweis zu 4-stelligen WP-Namen gemeldet
- [ ] Pfadverweise in REFERENZ und STANDARDSTART auf dev angeglichen
- [ ] Tippfehler M4 behoben, Nummern-Vermerk vorhanden, Status weiter FREIGEGEBEN
