# BRIDGE-0057 - Zweischichtige Push-Sperre: Nachweis

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0057 |
| project_id | agent-control-bridge |
| Typ / Klasse | T0 / DOCS |
| Teile (alte Nummern) | 0057 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Sicherheitsnachweis, Anleitung muss exakt stimmen. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0055 |
| Gate | G2 |
| stop_conditions | CONCEPT_CONFLICT |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0057` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

## Auftrag
**Ziel:** Nachweisdatei anlegen; April fuehrt die Pruefung manuell in den Klonen claude und codex aus.
**Scope:** Neu: docs/security/PUSH-SPERRE-NACHWEIS.md. NICHT in dev oder board sperren.
1. Schicht 1 (Tool): in `claude`/`codex` Deny fuer `git push` (Claude Code: .claude/settings.local.json, nicht committen).
2. Schicht 2 (Git): `git remote set-url --push origin DISABLED` in `claude` und `codex`.
3. Nachweis je Klon: `git push --dry-run` muss scheitern. Ausgabe als Zeile in die Datei (April fuellt).
4. dev und board behalten Push-Recht (Writer).
**Tests:** Keine.
- [ ] Nachweisdatei mit beiden Schichten
- [ ] Befehle exakt und kurz
- [ ] Platz fuer Nachweis je Klon
