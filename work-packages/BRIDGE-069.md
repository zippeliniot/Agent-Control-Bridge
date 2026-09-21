# BRIDGE-0069 - Windows-Benachrichtigung bei Fertigmeldung (webui serve --notify)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0069 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / FEATURE |
| Teile (alte Nummern) | 0069 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Kleiner Codeteil mit Prozessaufruf (sicherheitsrelevant). |
| Modellwechsel zum Vorgaenger | JA |
| depends_on | BRIDGE-0068 |
| Gate | keines |
| stop_conditions | CONCEPT_CONFLICT, SCOPE_VIOLATION |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0069` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

## Auftrag
**Ziel:** Umsetzung von `docs/concepts/ENTSCHEIDUNG-BENACHRICHTIGUNG.md` (Option A, nur Fertigmeldung).
**Scope:** Neu: src/bridge/notify.py, tests/test_notify.py. Aenderung: src/bridge/cli.py, docs/ACB-STEUERCHAT-REFERENZ.md (Abschnitt `webui serve`, max. 3 Zeilen). Sonst nichts.
1. VORAB: Entscheidungsdatei lesen. Status muss FREIGEGEBEN sein, sonst STOPP (CONCEPT_CONFLICT).
2. notify.py: reine Funktion fuer neu eingetretene Auftraege in WAITING_FOR_COPY_TO_CONTROL (Basis = Menge der IDs beim letzten Abgleich, Aktuell = ID -> Titel). Notifier-Schnittstelle: Callable (task_id, title). Null-Notifier und PowerShell-Toast-Notifier.
3. Toast-Notifier: nur unter Windows, sonst still. `powershell.exe -NoProfile -NonInteractive`, kein shell=True, Timeout. Texte (ID, Titel) NIE in den Befehlsstring einbetten, sondern per Umgebungsvariablen uebergeben. Alle Fehler (fehlt, Timeout, Exit-Code) nur nach stderr loggen (fail-open).
4. cli.py: Flag `--notify` bei `webui serve` (Standard aus). `_pull_loop` bekommt einen optionalen Callback `after_pull` (Standard None), Aufruf nach jedem Pull-Versuch, Exceptions abfangen (Thread darf nie sterben). Beim Start wird der Bestand als Basis gemerkt, Altbestand wird nicht gemeldet. Mit `--pull-interval 0` und `--notify`: Hinweis ausgeben, kein Fehler. Vorhandene Lesehelfer nutzen, kein neuer Store-Code.
5. Der Hook ist rein lesend: kein Store-Write, kein Audit, kein Statuswechsel, kein zusaetzlicher git-Aufruf.
6. Tests (Linux, Fake-Notifier und Fake-Runner): Erkennung, Altbestand still, Wiedereintritt nach Verlassen meldet erneut, fail-open (Notifier wirft, Thread lebt), Nicht-Windows ohne Prozessaufruf, Windows-Pfad mit Fake-Runner (Argumentliste, kein shell, Texte nur in Umgebungsvariablen, Timeout gesetzt), ohne `--notify` unveraendertes Verhalten, Hook schreibt weder Store noch Audit. Kein echter Toast in Tests.
7. Doku: `--notify` im Abschnitt `webui serve` von docs/ACB-STEUERCHAT-REFERENZ.md ergaenzen.
**Tests:** `python -m unittest tests.test_notify`, dann volle Suite EINMAL.
- [x] Freigabe der Entscheidungsdatei geprueft
- [x] Erkennung und Entprellung (Test)
- [x] fail-open (Test)
- [x] Hook ohne Store-Write und Audit (Test)
- [x] Ohne --notify unveraendert (Test)
- [x] Doku ergaenzt

Hinweis: Der echte Toast wird nach der Archivierung manuell von April auf HAM11 abgenommen, nicht vom Executor.