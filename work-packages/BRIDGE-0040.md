# BRIDGE-0040 — Parallel-Schreib-Test Teil B (Codex, Windows-nativ)

| Feld | Wert |
|------|------|
| bridge_task_id | BRIDGE-0040 |
| project_id | agent-control-bridge |
| task_class | TEST |
| depends_on | (keine, läuft koordiniert parallel zu BRIDGE-0039) |
| permission | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT (bewusst **kein** GIT_PUSH) |
| executor | codex |
| Modell/Denkstufe | **April: bitte hier das tatsächlich verwendete Codex-Modell eintragen** — Denkstufe LOW reicht: rein mechanischer CLI-Lebenszyklus, kein Code geändert. |

> **Ausdrückliche Abweichung von der Standardarchitektur, nur für diesen
> Test:** Codex läuft hier **nativ unter Windows** in
> `E:\_DEV\Agent-Control-Bridge\codex`, **nicht** in der Ubuntu/WSL-Umgebung
> wie sonst in `CODEX.md`/`machines.md` beschrieben. Keine dauerhafte
> Architekturänderung — gilt nur für BRIDGE-0040.

> **Verbindlich für diesen Auftrag — mit AUSNAHME markiert, wo abweichend:**
> - Jede Zustandsänderung läuft über die Bridge-CLI, kein direktes Bearbeiten
>   von Store-Dateien.
> - **AUSNAHME von `CODEX.md` „Sofort pushen, nicht sammeln":** Für diesen
>   Testauftrag **NICHT** sofort pushen. Lokal committen (`--commit`),
>   dann **warten** — der Push erfolgt erst auf ausdrückliches Signal von
>   April, zeitgleich mit dem Push von BRIDGE-0039 (Claude-Code-Seite).
>   Das ist der eigentliche Testpunkt: ein echter Non-Fast-Forward-Konflikt
>   auf `audit/audit.jsonl`.

## Zweck

Teil B eines zweigeteilten Tests gegen `BRIDGE-0039` (Claude Code). Prüft,
ob die Push-Retry-Logik (BRIDGE-029) und der Auto-Pull der Web-UI
(BRIDGE-038) einen echten, zeitgleichen Zweischreiber-Konflikt auf den
gemeinsamen Store sauber auflösen.

## Ablauf (genau in dieser Reihenfolge, **nach jedem Schritt anhalten und
auf Bestätigung von April warten** — nicht die ganze Kette am Stück)

**Schritt 1 — Auftrag anlegen:**
```
.venv\Scripts\python.exe src\bridge\cli.py --root . --schema-dir schemas task create tasks\incoming\BRIDGE-0040.yaml --commit
.venv\Scripts\python.exe src\bridge\cli.py --root . --schema-dir schemas task show BRIDGE-0040
```
→ Ergebnis (Status, HEAD-SHA des Commits) zurückmelden. **Hier anhalten.**

**Schritt 2 — Lauf starten (erst nach Freigabe durch April):**
```
.venv\Scripts\python.exe src\bridge\cli.py --root . --schema-dir schemas run start BRIDGE-0040 --actor codex-executor --commit
```
→ Ergebnis zurückmelden. **Hier anhalten.**

**Schritt 3 — Lauf abschließen, lokal committen, NICHT pushen (erst nach
Freigabe durch April):**
```
.venv\Scripts\python.exe src\bridge\cli.py --root . --schema-dir schemas run finish BRIDGE-0040 --status COMPLETED --actor codex-executor --summary "Parallel-Schreib-Test Teil B: reiner Lebenszyklus-Lauf, keine Code-Aenderung." --commit
git log --oneline -1
git status
```
→ Pflicht-Footer ausgeben:
```
Auftrag: BRIDGE-0040
Lauf:    RUN-01
Status:  COMPLETED
```
→ **NICHT pushen.** Auf das Push-Signal von April warten (Schritt 4 kommt
erst, wenn auch die Claude-Code-Seite/BRIDGE-0039 an derselben Stelle steht).

**Schritt 4 — Push (nur auf explizites Signal „jetzt pushen" von April,
zeitgleich mit BRIDGE-0039):**
```
git push
```
→ Exakten Output (inkl. eventueller `rejected`/`non-fast-forward`-Meldung)
an April/den Steuerchat zurückmelden — das ist die eigentliche
Testauswertung.

## Akzeptanzkriterien

- [x] `run start` ausgeführt, Status `CLAIMED`→`RUNNING`, Heartbeat gesetzt
- [ ] `run finish --commit` ausgeführt (lokal committet, **nicht** gepusht),
      Status `COMPLETED`
- [ ] Kein Push ohne ausdrückliches Signal
- [ ] Pflicht-Footer ausgegeben und zurückgemeldet
- [ ] Nach jedem Schritt angehalten, nicht die Kette am Stück durchlaufen
