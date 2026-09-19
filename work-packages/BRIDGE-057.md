# BRIDGE-0057 - Zweischichtige Push-Sperre: Nachweis

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0057 |
| project_id | agent-control-bridge |
| Typ / Klasse | T0 / DOCS |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Sicherheitsnachweis, Anleitung muss exakt stimmen. |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0056 |
| Gate | G2 |
| stop_conditions | CONCEPT_CONFLICT |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Nachweisdatei anlegen; April fuehrt die Pruefung manuell in den Klonen claude und codex aus.

## Scope
Neu: docs/security/PUSH-SPERRE-NACHWEIS.md. NICHT in dev oder board sperren.

## Schritte
1. Schicht 1 (Tool): in `claude`/`codex` Deny fuer `git push` (Claude Code: .claude/settings.local.json, nicht committen).
2. Schicht 2 (Git): `git remote set-url --push origin DISABLED` in `claude` und `codex`.
3. Nachweis je Klon: `git push --dry-run` muss scheitern. Ausgabe als Zeile in die Datei (April fuellt).
4. dev und board behalten Push-Recht (Writer).

## Tests
Keine.

## Akzeptanzkriterien
- [ ] Nachweisdatei mit beiden Schichten
- [ ] Befehle exakt und kurz
- [ ] Platz fuer Nachweis je Klon
