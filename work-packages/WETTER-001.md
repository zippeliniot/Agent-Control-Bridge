# WETTER-0001 - Regen-Nowcast genauer (Wahrscheinlichkeit, mehr Punkte, DWD-Radar pruefen)

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0001 |
| project_id | wetter-app |
| Typ / Klasse | FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | keine |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> ERSTER Auftrag ueberhaupt fuer das Profil `projects/wetter-app/project.yaml`
> UND erster Auftrag ueberhaupt mit der neuen Klon-Konvention `projects\<projekt-id>`.
> Laeuft in einem ZWEITEN, separaten Claude-Code-Fenster im Klon
> `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (falls noch nicht vorhanden:
> frisch klonen von https://github.com/zippeliniot/Agent-Control-Bridge.git).
> ZWEI Repositories, nicht verwechseln:
> (1) ACB-Repo, lokal `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` - NUR fuer Task/Result/Audit/diese WP-Datei.
> (2) Ziel-Repo `zippeliniot/wetter-app`, lokal `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo (E:\_DEV\Agent-Control-Bridge\projects\wetter-app): git pull. `BR task create` mit dieser WP als Grundlage (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0001 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` muss sauber sein, HEAD muss 914a9ee4e31563921ef1b515c8848a2f2d08ce9e sein (von April bestaetigt). Abweichung -> STOPP (CONCEPT_CONFLICT), nichts aendern.
3. Scope NUR im Ziel-Repo: js/api.js, js/regen.js, js/config.js, js/charts.js. Im ACB-Repo (Klon `projects\wetter-app`) NUR diese WP-Datei (Haken) + die Store-Dateien aus Schritt 1/5.

## Teil A - Regenwahrscheinlichkeit + dichtere Abtastung (im Ziel-Repo)
1. In `fetchRegenNowcast` (js/api.js) den Parameter `minutely_15` um `precipitation_probability` erweitern.
2. In `regen.js`: `precipitation_probability` durch die Kette ziehen (Timeline-Eintraege, Hero-Anzeige z. B. "70% Wahrscheinlichkeit", Tooltip im Chart).
3. Abtastung verdichten: RING_KM um einen nahen Ring erweitern (z. B. [2, 5, 10, 20, 30]) UND/ODER DIRS auf 16 Richtungen (22.5-Grad-Schritte) verdoppeln. Wahl und Begruendung (Rate-Limit-Guard in js/api.js beachten) kurz im Commit-Text.
4. Manuelle Pruefung: `python -m http.server` im Ziel-Repo, Seite im Browser oeffnen, Regenansicht fuer Hamburg UND Gronenberg oeffnen, Browser-Konsole ohne Fehler, Netzwerk-Tab zeigt precipitation_probability im Response. Kein Screenshot noetig, nur Befund in der Zusammenfassung.
5. Commit im Ziel-Repo (eigene Historie, eigener Push), NICHT im ACB-Repo. Danach im ACB-Repo (Klon `projects\wetter-app`): Haken in dieser WP-Datei setzen, committen, pushen.

## Teil B - DWD-Radar als Datenquelle pruefen (Recherche zuerst)
1. Recherchieren, ob eine CORS-faehige, bereits als JSON aufbereitete Quelle fuer DWD-RADOLAN-Niederschlagsradar existiert, die OHNE eigenen Server aus einer statischen GitHub-Pages-Seite abrufbar ist (roh-RADOLAN ist binaer, opendata.dwd.de hat nach bisherigem Kenntnisstand keine bekannte CORS-Freigabe - das VOR Ort pruefen, nicht annehmen).
2. Gibt es keine machbare Quelle ohne eigenen Server: NICHTS integrieren, Befund mit Begruendung in die Zusammenfassung, Teil B als "nicht umgesetzt, Grund: <kurz>" abschliessen. Das ist kein Fehler und kein STOPP.
3. Gibt es eine machbare Quelle: NICHT selbststaendig integrieren, sondern nur als Vorschlag in der Zusammenfassung nennen (neuer Datenpunkt, eigener Umfang, eigener Auftrag).

## Abschluss
`BR run finish WETTER-0001 --status COMPLETED --actor claude-code --commit --summary "<inkl. HEAD-SHA von E:\_DEV\Wetter-App nach Teil A>"`, `git push` (ACB-Repo, Klon `projects\wetter-app`).
Ausgabe NUR: Footer (Auftrag/Lauf/Status) + max. 4 Zeilen: ACB-HEAD, Ziel-Repo-HEAD (SHA), Teil-A-Befund, Teil-B-Befund.
- [ ] Teil A umgesetzt, im Ziel-Repo committet und gepusht
- [ ] Manuelle Pruefung ohne Konsolenfehler, beide Standorte
- [ ] Teil B: Befund dokumentiert (umgesetzt ODER begruendet nicht umgesetzt)
- [ ] Scope eingehalten (nur genannte Dateien in beiden Repos)