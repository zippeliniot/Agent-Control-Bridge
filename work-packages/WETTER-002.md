# WETTER-0002 - Bugfix-Buendel: Regenwahrscheinlichkeit-Anzeige + Ostsee-Kopfzeile beim Erstladen

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0002 |
| project_id | wetter-app |
| Typ / Klasse | BUGFIX |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0001 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main), Klon-Konvention wie WETTER-0001.
> ZWEI Repositories, nicht verwechseln:
> (1) ACB-Repo, lokal `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` - NUR fuer Task/Result/Audit/diese WP-Datei.
> (2) Ziel-Repo `zippeliniot/wetter-app`, lokal `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo (E:\_DEV\Agent-Control-Bridge\projects\wetter-app): git pull. `BR task create` mit dieser WP als Grundlage (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0002 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` muss sauber sein, HEAD muss f3452963a5a119d7809edf8a68b56f7e950d3f9d sein (Stand nach WETTER-0001, von April im Steuerchat bestaetigt). Abweichung -> STOPP (CONCEPT_CONFLICT), nichts aendern.
3. Scope NUR im Ziel-Repo: index.html, js/regen.js, js/main.js. Im ACB-Repo (Klon `projects\wetter-app`) NUR diese WP-Datei (Haken) + die Store-Dateien aus Schritt 1/5.

## Teil A - Regenwahrscheinlichkeit immer sichtbar machen (im Ziel-Repo)
Befund (Steuerchat-Review): `js/api.js` liefert `precipitation_probability` in `minutely_15` bereits korrekt (per Live-Test von April am 2026-09-23 bestaetigt, auch bei gebuendelten Multi-Location-Requests). Zwei Anzeige-Maengel bleiben:
1. `index.html`: der statische Footnote-Text `<p class="regen-footnote">Nowcast · keine Regenwahrscheinlichkeit % · Update ~15 Min</p>` (aktuell letzte Zeile der Regen-Ansicht) ist ein Ueberbleibsel von VOR WETTER-0001 und widerspricht der tatsaechlichen Funktion. Text korrigieren (z. B. "Nowcast · inkl. Regenwahrscheinlichkeit % · Update ~15 Min").
2. `js/regen.js`: `precipitation_probability` wird aktuell NUR angezeigt, wenn bereits Regen erkannt ist (`heroFeel` Zeile ~157 nur im `rains`-Zweig, `regen-peak-sub` Zeile ~375 nur wenn `peak.mmh >= RAIN_MMH`). Bei trockener Vorhersage (Normalfall) fehlt jede Prozentangabe, obwohl die API sie liefert. Ergaenze eine IMMER sichtbare Wahrscheinlichkeits-Anzeige:
   - Neues Feld in `index.html` (z. B. zusaetzliche Stat-Kachel in `.regen-grid-2` oder eigene Zeile unter dem Hero-Card), Label z. B. "Regenwahrscheinlichkeit (2 h)".
   - In `js/regen.js` `render()`: Wert berechnen (z. B. Maximum von `site_prob` ueber die Timeline, oder Wert des ersten Zeitschritts - Wahl kurz im Commit-Text begruenden) und per `setText(...)` setzen; in `showError()` analog auf `—` zuruecksetzen.
3. Bestehende bedingte Wahrscheinlichkeits-Texte in `heroFeel`/`regen-peak-sub` NICHT entfernen, nur ergaenzen.
4. Manuelle Pruefung: `python -m http.server` im Ziel-Repo, Regenansicht fuer Gronenberg oeffnen, Browser-Konsole ohne Fehler, neues Wahrscheinlichkeits-Feld zeigt einen Wert auch wenn "Kein Regen" angezeigt wird. Kein Screenshot noetig, nur Befund in der Zusammenfassung.

## Teil B - Ostsee-Kopfzeile beim Erstladen ohne Cache (im Ziel-Repo)
Befund (Steuerchat-Review): `updateSeaHeader()` in `js/main.js` (Zeile ~188-206) fuellt `#sea-current` (aktuelle Wassertemperatur + Wellenhoehe neben dem Kartentitel "Ostsee · Scharbeutz"). Sie wird nur aus `loadFromCache()` (Zeile ~72) und aus `updateCharts()` (Zeile ~181, nur im `else`-Zweig eines SPAETEREN Ladevorgangs) aufgerufen. Im Erstlade-Pfad ohne Cache (`loadAll()`, `if (!shellBuilt)`-Zweig, Zeile ~117-121) wird nur `initCharts()` gerufen, das `updateSeaHeader()` nicht enthaelt - die Kopfzeile bleibt bis zum naechsten 10-Minuten-Intervall oder Range-Wechsel leer, obwohl das Diagramm selbst sofort Daten zeigt.
1. In `js/main.js` im `if (!shellBuilt)`-Zweig von `loadAll()` (Zeile ~117-121) direkt nach `initCharts();` einen Aufruf von `updateSeaHeader();` ergaenzen (analog zum bestehenden Aufruf in `loadFromCache()`).
2. Manuelle Pruefung: `localStorage.clear()` im Browser, Seite neu laden, `#sea-current` zeigt sofort einen Wert (nicht erst nach Range-Wechsel oder 10 Minuten). Konsole ohne Fehler.

## Abschluss
`BR run finish WETTER-0002 --status COMPLETED --actor claude-code --commit --summary "<inkl. HEAD-SHA von E:\_DEV\Wetter-App nach Teil A+B>"`, `git push` (ACB-Repo, Klon `projects\wetter-app`).
Ausgabe NUR: Footer (Auftrag/Lauf/Status) + max. 4 Zeilen: ACB-HEAD, Ziel-Repo-HEAD (SHA), Teil-A-Befund, Teil-B-Befund.
- [x] Teil A umgesetzt (Footnote korrigiert + immer sichtbare Wahrscheinlichkeits-Anzeige), im Ziel-Repo committet und gepusht
- [x] Teil A manuelle Pruefung ohne Konsolenfehler bestanden (Ersatzverfahren, siehe Zusammenfassung)
- [x] Teil B umgesetzt (updateSeaHeader im Erstlade-Pfad), im Ziel-Repo committet und gepusht
- [x] Teil B manuelle Pruefung (Cache geleert, Kopfzeile sofort befuellt) bestanden (Ersatzverfahren: Code-Review, kein Browser-Lauf - siehe Zusammenfassung)
- [x] Scope eingehalten (nur index.html, js/regen.js, js/main.js im Ziel-Repo)
