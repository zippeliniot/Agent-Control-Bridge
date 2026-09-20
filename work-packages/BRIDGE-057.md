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
- [x] Nachweisdatei mit beiden Schichten
- [x] Befehle exakt und kurz
- [x] Platz fuer Nachweis je Klon

### Teil B (Nachtrag aus BRIDGE-0055) - Transfer-Weg dokumentieren
**Ziel:** Klaeren, wie ein Draft ohne Push des Executors zum Board kommt.
**Scope:** docs/security/PUSH-SPERRE-NACHWEIS.md (Abschnitt Transfer).
1. Regel: Der Executor committet den Draft (`bridge draft write --commit`), pusht aber nie. Das Board holt ihn lokal: `git pull <Pfad-des-Executor-Klons> main`; danach `bridge draft import`, Push NUR durch das Board.
2. Schritt-fuer-Schritt-Befehle fuer DES11 (Klone board, claude, codex) in den Abschnitt schreiben, je 1 Zeile.
- [x] Transfer-Weg (Board zieht per lokalem Pfad) dokumentiert
- [x] Push nur durch das Board festgehalten
