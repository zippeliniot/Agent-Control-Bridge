# CCB — Übergabe an neuen Steuerchat (Stand: 13.09.2026, nach BRIDGE-028/029/030, vor Archivierung von BRIDGE-030, Systemwechsel zu HAM11)

Ersetzt `docs/handover/CCB-UEBERGABE-v8.md`. **Abschnitt 0 ist bindend.**
Diese Übergabe ergänzt (ersetzt nicht) `docs/CCB-STEUERCHAT-ARBEITSWEISE.md`
und `docs/CCB-STEUERCHAT-REFERENZ.md` — beide zusätzlich lesen, siehe
Sitzungsstart-Pflichtablauf dort. Geschrieben unmittelbar vor einem geplanten
Systemwechsel des Nutzers (April) auf die Maschine **HAM11** — diese Übergabe
ist bewusst so geschrieben, dass eine neue Steuerchat-Sitzung auf HAM11 ohne
Rückfragen an den vorherigen Chat anschließen kann, rein aus Repo +
Übergabe.

## Abschnitt 0 — Was sich seit v8 geändert hat (wichtigste Punkte zuerst)

1. **`BRIDGE-0028` (Prioritätsfeld) abgeschlossen und archiviert.**
   Optionales Feld `priority` (`LOW`/`MEDIUM`/`HIGH`, Default `MEDIUM`) in
   `task.schema.yaml`, neue `Store.set_priority()`-Methode (unabhängig von
   `state_machine`/`set_status`), CLI-Befehl `bridge task set-priority`,
   Web-UI-Endpunkt für manuelle Zuweisung, Priorität als Zusatzkriterium in
   der Overview-Sortierung (innerhalb Aktiv/Inaktiv-Gruppe) und im Board
   (vor `bridge_task_id`). Neuer `event_type: PRIORITY_CHANGED` in
   `audit-event.schema.yaml`. Vollständig verifiziert (frischer Klon, Diff,
   Tests, Code gegengelesen).

2. **`BRIDGE-0029` (Git-Push-Retry) abgeschlossen und archiviert.**
   `git_commit()` in `src/bridge/gitops.py` erkennt Non-Fast-Forward-
   Push-Fehler (`rejected`/`non-fast-forward`/`fetch first` in `stderr`)
   und macht genau **einen** Ausgleichsversuch (`git fetch` + `git rebase
   origin/main`, dann erneuter Push). Rebase-Konflikt ist fail-closed
   (`git rebase --abort`, Commit bleibt lokal, kein `--force`). Neues
   optionales Rückgabefeld `retried` (bool). Betrifft nur den
   `push=True`-Pfad (Web-UI); CLI-Pfad (`push=False`) unverändert. **Eine
   Nacharbeit war nötig:** Claude Code hatte `SECURITY-MODEL.md` Abschnitt
   5c korrekt ergänzt, aber die widersprüchliche alte Zeile in Abschnitt
   5b („Kein automatisches `pull --rebase`... keine Wiederholung") stehen
   lassen — bei der Vier-Punkte-Prüfung aufgefallen, per Korrektur-Commit
   behoben, danach erneut verifiziert.

3. **`BRIDGE-0030` (Web-UI: Maschine überall, sortierbare Übersicht,
   Projekt-Dropdown) — fertig, verifiziert, aber noch NICHT archiviert.**
   Kein Punkt aus der ursprünglichen Orchestrator-Roadmap, sondern ein
   fachlicher Wunsch aus dem Steuerchat, deshalb vor das
   Review-Unternummern-Schema eingeschoben (das rückt auf `BRIDGE-0031`).
   Umgesetzt:
   - Maschinen-Spalte jetzt auch in „Board" und „Offene Aufträge außerhalb
     des Boards" (vorher nur in „Alle Projekte – Gesamtübersicht"),
     gleiche Ermittlungslogik wiederverwendet, ein gemeinsamer Audit-Scan
     für Board+Other statt zwei. `_board_text()` (Terminal-Ausgabe von
     `bridge board`) entpackt das erweiterte Tupel korrekt, druckt aber
     bewusst **keine** Maschinen-Spalte (Design-Entscheidung, nicht
     vergessen).
   - Neues Feld `last_activity_ts` (roher Unix-Zeitstempel) zusätzlich in
     `overview_payload()`, weil der bisherige `last_activity`-Wert nur
     bereits formatierter Anzeigetext ist (z. B. „vor 5 Min") und für
     chronologische Sortierung ungeeignet gewesen wäre — dieser Fund kam
     erst durch Code-Verifikation vor der Spezifikation zutage, nicht aus
     der Doku.
   - Spaltenköpfe der Tabelle „Alle Projekte – Gesamtübersicht" (außer
     `#`) klickbar, 3-Stufen-Sortierung (1. Klick auf, 2. Klick ab,
     3. Klick zurück zu Standard). Trennzeile „— inaktiv / unterbrochen —"
     nur bei Standard-Sortierung sichtbar.
   - Projekt-Filter (`#f-projekt`) von Freitext zu `<select>`, Werte
     dynamisch aus geladenen Daten abgeleitet (wie `updateStatusList()`),
     kein hartkodierter Projekt-Katalog. Status- und Auftrag-Filter bewusst
     unverändert gelassen (Teilstring-Suche bleibt nützlich bzw. Wertemenge
     zu groß für ein Dropdown).
   - Vollständig verifiziert (frischer Klon, 322 Tests dreimal grün, Diff
     exakt gegen `changed_files`, jede Design-Entscheidung im Code
     gegengelesen).
   - **Aktueller Zustand: `REVIEW_REQUIRED`** (per Web-UI `task copied`
     ausgeführt, `task archive` steht noch aus — bitte auf HAM11 zuerst
     erledigen, bevor `BRIDGE-0031` gestartet wird, Ein-Auftrag-zur-Zeit).

4. **Neuer, noch offener Fund — kein BRIDGE-0030-Fehler, sondern ein
   vorbestehender, bisher unbemerkter Bug:** April meldete nach BRIDGE-030,
   dass die Maschinen-Spalte überall nur `"?"` zeigt. Root Cause
   verifiziert: `registry.py` hat eine fertige Funktion `machine_name
   (explicit=None)`, die `--machine` mit `COMPUTERNAME`-Fallback auflöst
   (genau das, was die CLI-Hilfetexte „Standard: COMPUTERNAME" versprechen)
   — wird aber **nur** bei der Pfad-Auflösung (`resolve_base()`, BRIDGE-016)
   verwendet, **nicht** dort, wo Audit-Einträge geschrieben werden. Alle
   Befehle, die `machine=args.machine` an den Store reichen, bekommen
   `None`, außer man tippt bei **jedem einzelnen Befehl** manuell
   `--machine <name>`. Am echten Store nachgezählt: **0 von 144**
   Audit-Einträgen im gesamten Projektverlauf haben je einen
   `machine`-Wert gesetzt — betrifft auch die länger bestehende „Alle
   Projekte"-Spalte, nur bisher nicht aufgefallen. **Entscheidung
   getroffen:** wird bewusst **nicht** jetzt gefixt, sondern **auf HAM11**
   angegangen — bis dahin bleibt das „?" in der Maschinen-Spalte
   erwartungsgemäß stehen, ist kein neuer/anderer Fehler, kein Grund zur
   erneuten Fehlersuche.

## Verifikationsmethode — unverändert, hat sich in dieser Sitzung erneut
bewährt (bitte beibehalten)

Bei **jedem** `run finish`-Footer volle Vier-Punkte-Prüfung, Footer-Text/
`result.yaml` nie ungeprüft glauben:
1. Frischer Klon (`rm -rf` + `git clone`), nie den lokalen Checkout des
   vorherigen Auftrags weiterverwenden.
2. Testsuite frisch laufen lassen und **tatsächlich nachzählen** — in
   dieser Sitzung einmal ein isolierter, nicht reproduzierbarer
   Einzel-Fehlschlag beobachtet (BRIDGE-029-Nachprüfung), fünf direkt
   folgende Wiederholungen liefen sauber. Bei Verdacht auf Flakiness:
   mehrfach laufen lassen, nicht am ersten Ergebnis festhalten in beide
   Richtungen.
3. `git diff --name-only <base_head> <head>` gegen die in `result.yaml`
   behauptete `changed_files`-Liste — **`base_head` aus `result.yaml`
   übernehmen**, nicht selbst raten (in dieser Sitzung einmal falsch
   gewählt, dadurch fälschlich eine Lücke vermutet, nach Korrektur
   deckte sich alles).
4. Jede Akzeptanzkriterium-Zeile einzeln gegen den echten Code prüfen,
   nicht gegen die Zusammenfassung im Footer.

Und: **vor** jeder Work-Package-Spezifikation den echten Funktionskörper
lesen, nicht nur Schema/Doku (Verifikationspflicht Nr. 3 aus
`CCB-STEUERCHAT-ARBEITSWEISE.md`) — hat in dieser Sitzung mehrfach
Annahmen widerlegt, die aus der Doku allein falsch gewesen wären
(z. B. `last_activity_ts`, `_board_text()`-Tupel-Länge, fehlendes
Antwort-Schema für `git_commit()`).

## Sieben Projekte (unverändert seit v7/v8)

| project_id | executor | controller | review_roles (lead/support) | github_app |
|---|---|---|---|---|
| codex-control-bridge | claude-code | human | anthropic / openai | true |
| dorfschaft | codex | openai | openai / anthropic | true |
| bess-msrechner | codex | openai | openai / anthropic | false |
| bess-platform | codex | openai | openai / anthropic | false |
| wetter-app | claude-code | human | anthropic / openai | false |
| climac | claude-code | human | anthropic / openai | false |
| tanken-monitor | claude-code | human | anthropic / openai | false |

## Aktueller Stand (verifiziert per frischem Klon via `bash_tool`, HEAD `0d7e04a`)

- `BRIDGE-0017` bis `BRIDGE-0029`: alle **`ARCHIVED`**.
- `BRIDGE-0030`: **`REVIEW_REQUIRED`** — `task archive` steht noch aus.
- Testsuite-Stand zuletzt verifiziert: **322 Tests grün** (frisch
  nachgezählt, dreimal wiederholt zur Flakiness-Kontrolle).
- Nächste freie ID: **`BRIDGE-0031`** — Review-Unternummern-Schema
  (ursprünglich als `BRIDGE-0030` in der Orchestrator-Roadmap geplant,
  durch das eingeschobene Web-UI-Paket auf `0031` verschoben). Work-Package
  **noch nicht erstellt**.

## Nicht von selbst anfangen bei

- `BRIDGE-0031` starten, bevor `BRIDGE-0030` archiviert ist
  (Ein-Auftrag-zur-Zeit-Disziplin, siehe Abschnitt 0 Punkt 3).
- Den COMPUTERNAME-Autodefault-Bugfix von selbst vorziehen oder ihm
  Priorität vor `BRIDGE-0031` geben — bewusst auf HAM11 verschoben
  (Abschnitt 0 Punkt 4), nicht ungefragt vorher anpacken.
- `BRIDGE-0028`-Sortierannahme (Board: Priorität vor `bridge_task_id`) oder
  `BRIDGE-0029`-Retry-Tiefe (genau ein Versuch) in Frage stellen — beide
  wurden in der vorherigen Sitzung ausdrücklich bestätigt, nicht erneut
  zur Debatte stellen.
- GitHub-App-Repository-Freigabe für die restlichen sechs Repos (nur
  `dorfschaft` bisher bestätigt) — nicht ungefragt erweitern.
- `review_roles`/`executor`/`controller` weiterer Projekte ändern, ohne
  erneute ausdrückliche Angabe wie in vorherigen Sitzungen.

## Offene nächste Schritte (Reihenfolge)

1. `BRIDGE-0030` archivieren (`task archive`, April/Nutzer-Aktion, nicht
   automatisch durch den Steuerchat).
2. Auf HAM11: COMPUTERNAME-Autodefault-Bugfix angehen (Abschnitt 0
   Punkt 4) — Work-Package dafür noch nicht erstellt, vor der
   Spezifikation `registry.py`/alle `args.machine`-Übergabestellen erneut
   frisch gegen den Code prüfen, nicht diese Übergabe als Spezifikation
   nehmen.
3. Danach `BRIDGE-0031` (Review-Unternummern-Schema) spezifizieren — vor der
   Spezifikation den echten Code lesen (`audit-event.schema.yaml`,
   `state-model.yaml`, wie Reviews aktuell modelliert sind), nicht nur aus
   der Orchestrator-Konzept-Doku übernehmen.
4. Wie gewohnt an Claude Code übergeben, `run finish`-Footer **nicht**
   ungeprüft glauben — volle Vier-Punkte-Prüfung (siehe oben).
