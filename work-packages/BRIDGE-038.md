# BRIDGE-038 — Periodisches Auto-`git pull` für den Web-UI-Server

| Feld | Wert |
|------|------|
| bridge_task_id | BRIDGE-0038 |
| project_id | agent-control-bridge |
| task_class | FEATURE |
| depends_on | (keine) |
| permission | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| executor | claude-code |
| review_roles | lead: anthropic, support: openai (aus Projektprofil übernommen) |
| Modell/Denkstufe | Claude Sonnet 5, Denkstufe MEDIUM — führt echte Nebenläufigkeit ein (Hintergrund-Thread neben dem HTTP-Server), die mit den bestehenden, ebenfalls Git-schreibenden Aktions-Endpunkten im selben Prozess kollidieren kann, wenn nicht sauber synchronisiert — echtes Korrektheitsrisiko bei falscher Umsetzung, aber eng umrissen (ein Modul, ein Lock, keine neue Architektur/kein neuer Zustand). |

> **Verbindlich für diesen und jeden CCB-Auftrag:**
> - Jede Zustandsänderung läuft über die Bridge-CLI, kein direktes Bearbeiten
>   von Store-Dateien.
> - `GIT_PUSH` steht im Profil — nach `run finish` **muss** gepusht werden,
>   idealerweise über `--commit`, und **sofort**, nicht gesammelt.

## Kontext

Der `board`-Klon (dritter, neutraler Checkout, siehe Steuerchat-Diskussion)
soll Aufträge aus **allen** Projekten zeigen, unabhängig davon, ob sie über
den `claude`- oder den `codex`-Klon gepusht wurden. Die Anzeige-Logik
selbst ist dafür bereits generisch (liest `tasks/*/task.yaml`
projektübergreifend) — es fehlt nur die **Aktualität**: der Web-UI-Prozess
sieht ausschließlich den lokalen Stand seines eigenen Checkouts, der ohne
manuelles `git pull` veraltet, sobald `claude`/`codex` zwischenzeitlich
gepusht haben.

**Wichtiger, im Code verifizierter Befund (Verifikationspflicht Nr. 3),
der die eigentliche Design-Entscheidung dieses Auftrags bestimmt:** Die
Hilfetexte der CLI (`wserve = websub.add_parser("serve", ...)`) nennen
die Web-UI „rein lesend" — das stimmt aber **nicht mehr**: die
Aktions-Endpunkte (`copied`, `archive`, `priority`) schreiben und
committen bereits (`task_copied()`/`task_archive()`/`task_set_priority()`,
alle über `gitops.git_commit()`). Das heißt: ein periodischer
Hintergrund-`git pull` im selben Prozess **kann mit einem gerade laufenden
Aktions-Commit desselben Servers kollidieren** — der `ThreadingHTTPServer`
bedient mehrere Anfragen gleichzeitig in eigenen Threads. Das ist dieselbe
Art Git-Kollisionsrisiko, die in der Steuerchat-Diskussion zur
Parallelverarbeitung zwischen zwei **Prozessen** besprochen wurde — hier
jetzt innerhalb **eines** Prozesses zwischen zwei **Threads**. Löst sich
hier aber einfacher: ein gemeinsames `threading.Lock`, das sowohl der
Pull-Hintergrund-Thread als auch jeder Aktions-Endpunkt vor jeder
Git-Operation hält, reicht aus (kein Datei-Lock nötig wie bei
prozessübergreifender Nebenläufigkeit).

## Von Claude Code umzusetzen

1. Auftrag anlegen und starten:
   ```
   bridge task create tasks/incoming/BRIDGE-0038.yaml
   bridge run start BRIDGE-0038 --actor claude-code
   ```

2. **Neue Funktion `git_pull(repo_root)` in `src/bridge/gitops.py`:**
   - Führt `git pull` im `repo_root` aus (kein Rebase-Zwang wie bei
     `git_commit()` — reiner Fast-Forward-Pull reicht für den Lesefall;
     falls der lokale Checkout durch eine vorherige fehlgeschlagene
     Operation divergiert sein sollte, `git pull --ff-only` verwenden und
     bei Fehlschlag **nicht** automatisch mergen/rebasen — fail-soft
     loggen, nicht die Datenlage verändern, siehe Punkt 4).
   - Gibt ein strukturiertes Ergebnis zurück (Erfolg/Fehler, `stdout`/
     `stderr`, evtl. „bereits aktuell" vs. „neue Commits geholt"),
     analog zum Rückgabemuster von `git_commit()`.
   - **Kein** Retry/Rebase-Verhalten wie bei `git_commit()` übernehmen —
     das ist für den Schreibfall gedacht, hier reicht ein einfacher,
     idempotenter Pull, der bei Konflikt sauber fehlschlägt statt
     einzugreifen.

3. **Hintergrund-Thread in `src/bridge/webui.py` oder `cli.py`**
   (Platzierungsentscheidung: da der Thread eng an den Serverlebenszyklus
   gekoppelt ist, in `_cmd_webui()` in `cli.py` starten, analog zur
   bestehenden Trennung „webui.py macht HTTP, cli.py orchestriert den
   Prozess"):
   - `threading.Thread(target=_pull_loop, args=(...), daemon=True)`,
     gestartet nach `webui.serve(...)`, vor `httpd.serve_forever()`.
   - `_pull_loop(repo_root, interval_seconds, stop_event, git_lock)`:
     Schleife, die alle `interval_seconds` `git_lock` hält, `git_pull()`
     aufruft, Ergebnis nach `stderr`/Konsole loggt (mit Zeitstempel —
     „neue Commits geholt" vs. „bereits aktuell" vs. „Pull
     fehlgeschlagen: <Grund>"), Lock wieder freigibt, dann wartet (über
     `stop_event.wait(interval_seconds)`, nicht `time.sleep`, damit ein
     sauberes Beenden ohne Wartezeit möglich ist).
   - **Fail-soft, zwingend:** Ein fehlgeschlagener Pull (Netzwerk,
     Konflikt, was auch immer) darf den Server **nicht** zum Absturz
     bringen — Exception im Pull-Versuch abfangen, loggen, beim nächsten
     Intervall erneut versuchen. Der Server bedient währenddessen weiter
     mit dem letzten bekannten lokalen Stand.
   - `stop_event.set()` beim Beenden des Servers (`finally`-Block in
     `_cmd_webui`, dort wo aktuell schon `httpd.server_close()` steht) —
     sauberes Herunterfahren des Threads, kein Geisterprozess.

4. **`git_lock` (ein `threading.Lock`) gemeinsam nutzen** zwischen dem
   neuen Pull-Thread und den bestehenden Aktions-Endpunkten
   (`_apply_action()` in `webui.py`, dort wo aktuell `task_copied()`/
   `task_archive()`/`task_set_priority()`/`runner.finish()` aufgerufen
   werden): vor jedem dieser Aufrufe den Lock halten, danach freigeben.
   Verhindert, dass ein Klick auf „Archivieren" mitten in einem laufenden
   Hintergrund-Pull passiert (oder umgekehrt) — genau das im Kontext
   beschriebene Kollisionsrisiko.

5. **CLI-Flag `--pull-interval`** am `webui serve`-Unterbefehl:
   - `type=int, default=30` (Sekunden) — bewusst nicht identisch mit dem
     client-seitigen `REFRESH_MS` (15s) gewählt, da ein Git-Pull über das
     Netzwerk teurer ist als ein lokaler Datei-Read; 30s ist ein
     vernünftiger Standard, per Flag änderbar.
   - `--pull-interval 0` deaktiviert den Hintergrund-Pull vollständig
     (kein Thread wird gestartet) — für Tests oder Fälle, in denen
     bewusst nur der lokale Stand gezeigt werden soll.
   - Hilfetext von `wserve` („rein lesend") **nicht** unverändert lassen
     — das war schon vor diesem Auftrag ungenau (siehe Kontext), hier
     mit korrigieren: die Web-UI ist nicht rein lesend, sie holt jetzt
     zusätzlich aktiv neue Daten.

6. **Konsolen-Startmeldung ergänzen** (`_cmd_webui`, wo aktuell die
   `Web-UI: http://...`-Zeile ausgegeben wird): zweite Zeile, die den
   aktiven Pull-Intervall nennt (oder „Auto-Pull deaktiviert" bei
   `--pull-interval 0`) — damit auf einen Blick klar ist, ob der
   Mechanismus läuft.

7. **Tests** (`tests/test_webui.py`, `tests/test_gitops.py`, bestehende
   Muster wiederverwenden — **nicht** mit echten Zeitintervallen testen,
   das wäre langsam/flaky):
   - `git_pull()` isoliert testen: zwei synthetische Temp-Repos (analog
     zum Muster in `test_gitops.py`), einer pusht einen Commit, der
     andere pullt — Ergebnis zeigt „neue Commits geholt".
   - `git_pull()` bei divergentem/nicht-fast-forward-fähigem Zustand:
     fail-soft, kein Absturz, sauberes Fehlerergebnis.
   - `_pull_loop()` **nicht** über echtes Warten testen — stattdessen die
     Kernlogik (ein Durchlauf: Lock halten, `git_pull` aufrufen, Lock
     freigeben, Ergebnis loggen) als eigene, direkt aufrufbare Funktion
     testen, `stop_event`/Intervall-Schleife nur mit einem sehr kurzen
     Intervall (z. B. 0.01s) und `stop_event.set()` nach einer kurzen
     bekannten Zeitspanne im Test selbst, um zu prüfen, dass der Thread
     sauber stoppt.
   - Lock-Synchronisation: ein Test, der `git_lock` von außen hält,
     während `_apply_action()` aufgerufen wird, bestätigt, dass die
     Aktion blockiert, bis der Lock freigegeben wird (kein „daran
     vorbei" möglich).
   - `--pull-interval 0` startet keinen Thread (per `threading.enumerate()`
     oder Mock prüfbar).

8. Volle Testsuite frisch laufen lassen, dreimal, tatsächlich nachzählen
   (Referenzwert vor diesem Auftrag: 363 Tests).

9. Pflicht-Footer + Abschluss, `--commit` nutzen, **sofort pushen**:
   ```
   bridge run finish BRIDGE-0038 --status COMPLETED --actor claude-code \
     --commit \
     --summary "Periodisches Auto-git-pull fuer den Web-UI-Server: neue git_pull()-Funktion in gitops.py (einfacher, idempotenter Fast-Forward-Pull, fail-soft, kein Retry/Rebase wie git_commit()). Hintergrund-Thread in cli.py/_cmd_webui, konfigurierbar ueber --pull-interval (Standard 30s, 0 deaktiviert). Gemeinsames threading.Lock zwischen Pull-Thread und den bestehenden schreibenden Aktions-Endpunkten (copied/archive/priority) verhindert Kollisionen innerhalb desselben Prozesses - Befund: die Web-UI war entgegen ihrem eigenen Hilfetext (\"rein lesend\") bereits vorher schreibfaehig, Hilfetext korrigiert. Sauberes Thread-Herunterfahren ueber stop_event beim Serverende. Tests ohne echte Wartezeiten (kurze Intervalle, direkte Funktionsaufrufe statt Sleep-basiertem Timing)."
   git push
   ```
   `Auftrag: BRIDGE-0038 / Lauf: RUN-01 / Status: COMPLETED`

## Akzeptanzkriterien

- [ ] `git_pull(repo_root)` in `gitops.py`: Fast-Forward-Pull, fail-soft,
      strukturiertes Ergebnis, kein automatisches Rebase/Merge bei
      Konflikt.
- [ ] Hintergrund-Thread startet mit dem Server, stoppt sauber beim
      Serverende (`stop_event`), kein Geisterthread.
- [ ] `--pull-interval` (Standard 30s) konfigurierbar, `0` deaktiviert den
      Thread vollständig.
- [ ] Gemeinsames `threading.Lock` zwischen Pull-Thread und den
      bestehenden Aktions-Endpunkten (`copied`/`archive`/`priority`) —
      keine gleichzeitige Git-Operation aus beiden Quellen möglich.
- [ ] Fehlgeschlagener Pull bringt den Server nicht zum Absturz, wird
      geloggt, nächster Versuch beim folgenden Intervall.
- [ ] Konsolen-Startmeldung nennt den aktiven Pull-Intervall (oder
      „deaktiviert").
- [ ] Hilfetext von `webui serve` korrigiert (nicht mehr „rein lesend").
- [ ] Neue Tests: `git_pull()` isoliert (Erfolg + Konfliktfall),
      Lock-Synchronisation, `--pull-interval 0` startet keinen Thread —
      keiner davon mit echten Wartezeiten/Sleep-Timing.
- [ ] Volle Testsuite (bestehend + neu) dreimal frisch grün, frischer
      Klon verifiziert.
- [ ] Jeder Commit sofort gepusht, nicht gesammelt.
