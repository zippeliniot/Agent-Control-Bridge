# BRIDGE-0039 — Parallel-Schreib-Test Teil A (Claude Code)

| Feld | Wert |
|------|------|
| bridge_task_id | BRIDGE-0039 |
| project_id | agent-control-bridge |
| task_class | TEST |
| depends_on | (keine, läuft koordiniert parallel zu BRIDGE-0040) |
| permission | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT (bewusst **kein** GIT_PUSH) |
| executor | claude-code |
| Modell/Denkstufe | Claude Sonnet 5, Denkstufe LOW — rein mechanischer CLI-Lebenszyklus (`run start`/`run finish`), keine Entwurfsentscheidung, kein Code geändert. |

> **Verbindlich für diesen Auftrag — mit AUSNAHME markiert, wo abweichend:**
> - Jede Zustandsänderung läuft über die Bridge-CLI, kein direktes Bearbeiten
>   von Store-Dateien.
> - **AUSNAHME von `CLAUDE.md` „Sofort pushen, nicht sammeln":** Für diesen
>   Testauftrag **NICHT** sofort pushen. Lokal committen (`--commit`),
>   dann **warten** — der Push erfolgt erst auf ausdrückliches Signal des
>   Steuerchats/April, zeitgleich mit dem Push von BRIDGE-0040 (Codex-Seite).
>   Das ist der eigentliche Testpunkt: ein echter Non-Fast-Forward-Konflikt
>   auf `audit/audit.jsonl`.

## Zweck

Teil A eines zweigeteilten Tests gegen `BRIDGE-0040` (Codex, Windows-nativ).
Prüft, ob die Push-Retry-Logik (BRIDGE-029) und der Auto-Pull der Web-UI
(BRIDGE-038) einen echten, zeitgleichen Zweischreiber-Konflikt auf den
gemeinsamen Store sauber auflösen — bisher nur in Unit-Tests geprüft, nie
unter echter Last mit zwei realen Prozessen (siehe Übergabe v11, Abschnitt 3).

## Ablauf (genau in dieser Reihenfolge, **nach jedem Schritt anhalten und
auf Bestätigung des Steuerchats warten** — nicht die ganze Kette am Stück)

**Schritt 1 — Auftrag anlegen:**
```powershell
.venv\Scripts\python.exe src\bridge\cli.py --root . --schema-dir schemas task create tasks\incoming\BRIDGE-0039.yaml --commit
.venv\Scripts\python.exe src\bridge\cli.py --root . --schema-dir schemas task show BRIDGE-0039
```
→ Ergebnis (Status, HEAD-SHA des Commits) an den Steuerchat zurückmelden.
**Hier anhalten.**

**Schritt 2 — Lauf starten (erst nach Freigabe durch Steuerchat):**
```powershell
.venv\Scripts\python.exe src\bridge\cli.py --root . --schema-dir schemas run start BRIDGE-0039 --actor claude-code --commit
```
→ Ergebnis zurückmelden. **Hier anhalten.**

**Schritt 3 — Lauf abschließen, lokal committen, NICHT pushen (erst nach
Freigabe durch Steuerchat):**
```powershell
.venv\Scripts\python.exe src\bridge\cli.py --root . --schema-dir schemas run finish BRIDGE-0039 --status COMPLETED --actor claude-code --summary "Parallel-Schreib-Test Teil A: reiner Lebenszyklus-Lauf, keine Code-Aenderung." --commit
git log --oneline -1
git status
```
→ Pflicht-Footer ausgeben:
```
Auftrag: BRIDGE-0039
Lauf:    RUN-01
Status:  COMPLETED
```
→ **NICHT pushen.** Auf das Push-Signal des Steuerchats warten (Schritt 4
kommt erst, wenn auch die Codex-Seite/BRIDGE-0040 an derselben Stelle steht).

**Schritt 4 — Push (nur auf explizites Signal „jetzt pushen" vom
Steuerchat, zeitgleich mit BRIDGE-0040):**
```powershell
git push
```
→ Exakten Output (inkl. eventueller `rejected`/`non-fast-forward`-Meldung)
an den Steuerchat zurückmelden — das ist die eigentliche Testauswertung.

## Akzeptanzkriterien

- [x] `run start` ausgeführt, Status `CLAIMED`→`RUNNING`, Heartbeat gesetzt
- [ ] `run finish --commit` ausgeführt (lokal committet, **nicht** gepusht),
      Status `COMPLETED`
- [ ] Kein Push ohne ausdrückliches Signal des Steuerchats
- [ ] Pflicht-Footer ausgegeben und zurückgemeldet
- [ ] Nach jedem Schritt angehalten, nicht die Kette am Stück durchlaufen
