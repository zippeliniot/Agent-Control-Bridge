# BRIDGE-0070 - Toast-Kennung fuer Windows (Fix zu BRIDGE-0069)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0070 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Teile (alte Nummern) | 0070 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - Eine Konstante und ein Test. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | BRIDGE-0069 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0070` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

## Auftrag
**Ziel:** Der Toast aus BRIDGE-0069 wird auf HAM11 nicht angezeigt, weil Windows die eigene Kennung 'Agent Control Bridge' still verwirft. Mit der PowerShell-Kennung erscheint er (von April nachgewiesen).
**Scope:** src/bridge/notify.py, tests/test_notify.py. Sonst nichts.
1. In notify.py eine Konstante `_TOAST_APP_ID` mit dem Wert `{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe` anlegen. Kommentar: eigene Kennung wird von Windows verworfen, Kopfzeile des Toasts zeigt deshalb "Windows PowerShell".
2. `_TOAST_SCRIPT` verwendet diese Konstante statt `'Agent Control Bridge'` (als PowerShell-Stringliteral in Einzelanfuehrungszeichen, per Stringverkettung einsetzen, nicht per .format oder f-String wegen der geschweiften Klammern). Alles andere im Skript und im Notifier bleibt unveraendert (ID und Titel weiter nur per Umgebungsvariablen, kein shell, Timeout, fail-open).
3. Test: Das Skript enthaelt die Kennung, enthaelt 'Agent Control Bridge' nicht mehr, und ID/Titel stehen weiterhin nicht im Skript.
**Tests:** `python -m unittest tests.test_notify`, dann volle Suite EINMAL.
- [x] Kennung als Konstante, eigene Kennung entfernt
- [x] Test auf Kennung im Skript
- [x] Suite gruen

Hinweis: Der echte Toast wird nach der Archivierung erneut von April auf HAM11 abgenommen.