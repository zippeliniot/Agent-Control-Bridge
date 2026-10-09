# WETTER-0016 - Wind-Karte: Kopf vervollstaendigen (Legende + Statzeile) und Animationen

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0016 |
| project_id | wetter-app |
| Typ / Klasse | FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0015 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` mit docs/handover/staging-v12/WETTER-0016.yaml (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0016 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss 7df36e7a6a38c36512a9fa58b2665e1c13545a4e sein (Stand nach WETTER-0015). Abweichung -> STOPP.
3. Scope NUR: `index.html` (CSS + Markup der Wind-Karte, `#wind-card`), `js/charts.js` (NUR `getWindChartConfig`, `windArrowPlugin`, `windZonesPlugin`, `windFill`/`windBorder`), `js/main.js` (NUR `updateWindHeader`, der Wind-Teil von `updateCharts`/`initCharts`, ggf. eine neue kleine Hilfsfunktion fuer die Statzeile). KEINE Aenderung an Temperatur/Taschensee/Ostsee/Tanken/Regen/Blitz-Bloecken, KEINEN gemeinsamen CSS-Klassen ausserhalb der neu angelegten wind-spezifischen Klassen, KEINE Pi-seitigen Dateien (`pi-scripts/*`), KEINE neuen Sensordaten/Historie (folgt separat in WETTER-0017, gemessener Wind `sensor.gw2000a_wind_speed`/`_gust`/`_direction`/`max_daily_gust_3` - hier NICHT vorgreifen, weiterhin ausschliesslich die bestehende Open-Meteo-API als Datenquelle).

## Befund (Steuerchat, gegen HEAD 7df36e7 geprueft)
- `#wind-card` (index.html) hat anders als `#taschensee-card` keine Tabs-/Subctrl-Zeile und keine ausfuehrliche Legende - nur `.wind-thr` mit 4 reinen Farb-Dots ohne Text-Label (`.wt-item`/`.wt-dot`). Chart-Hoehe `.chart-wrapper` bei Wind 240px, bei Temperatur 300px, bei Taschensee 280px - dadurch wirkt die Karte deutlich leerer.
- Die vier Schwellen (15/25/50 km/h) inkl. Farben existieren schon doppelt im Code: als CSS-Dots (`.wt-dot`, index.html) UND als Logik in `charts.js` (`windFill`/`windBorder`-Funktionen, `windZonesPlugin`-Bandfarben) - Werte muessen konsistent bleiben, NICHT neu erfinden.
- `getWindChartConfig` (charts.js) liefert ein reines Balkendiagramm aus `cityData.hourly.wind_speed_10m`/`wind_direction_10m` (Open-Meteo), inkl. `windArrowPlugin` (zeichnet pro Balken einen kleinen Richtungspfeil per Canvas) und `windZonesPlugin` (Hintergrundbaender je Schwelle). `animation: { duration: 350 }` ist gesetzt, aber ungenutzt fuer gestaffeltes Einblenden o. ae.
- `updateWindHeader()` (main.js) zeigt den aktuellen Wert als reinen Text ("<speed> km/h <Himmelsrichtung>"), kein Icon, keine Animation.
- **Gefundene Inkonsistenz** (im Zuge der Pruefung, nicht Kern des Auftrags aber im bearbeiteten Code): `updateWindHeader()` liest hart `cachedData?.[1]` (fest Gronenberg), waehrend `updateTempHeader()` und der Wind-Chart selbst korrekt `getWindCityIdx()` nutzen (reagiert auf die Standortauswahl Hamburg/Kiel/Luebeck/Alle). Dadurch zeigt der Wind-Kopfwert bei Standortwechsel weiterhin Gronenberg, obwohl der Chart korrekt umschaltet. Da dieselbe Funktion ohnehin fuer die Statzeile angefasst wird: auf `getWindCityIdx()` umstellen (identisch zum Muster in `updateTempHeader()`).
- `updateCharts()` ruft bei Hintergrund-Updates `windChart.update('none')` auf (Kommentar im Code: "verhindert Animationen beim Hintergrund-Update") - dieses Verhalten MUSS erhalten bleiben; neue Animationen duerfen nur bei echten Nutzeraktionen/initialem Laden/Range-Wechsel greifen, nicht beim automatischen Poll.
- Keine SVG-/Icon-Infrastruktur fuer Himmelsrichtungen vorhanden; `getWindDir()` (utils.js, unveraendert) liefert nur Text ("NW" etc.).

## Umsetzung
1. **Legende ausbauen** (`.wind-thr`/`.wt-item` in index.html): Text-Labels ergaenzen, Werte decken sich mit `windFill`/`windZonesPlugin` in charts.js (15/25/50 km/h): z. B. "Schwach ≤ 15", "Maessig ≤ 25", "Stark ≤ 49", "Sturm ≥ 50" (km/h im Kartentitel bereits vorhanden, hier nicht wiederholen). Gleiches visuelles Muster wie `.chart-legend`/`.cl-item` (Temp-Karte), aber eigene Klassen behalten (`.wind-thr`/`.wt-item` erweitern, nicht `.cl-item` umbauen).
2. **Statzeile ergaenzen**: neue Zeile zwischen `.chart-head` und `.chart-wrapper` in `#wind-card` mit drei Werten aus den im Chart bereits geladenen `winds`-Daten (KEIN neuer API-Call): "Aktuell", "Max (sichtbarer Zeitraum)", "Ø (sichtbarer Zeitraum)" - "sichtbarer Zeitraum" = aktuell gewaehlter Range (1 Tag/3 Tage), aus denselben Werten wie der Chart. Neue, eigene CSS-Klasse(n) im bestehenden Kartenstil (Glass-Look wie `.card`), responsive (flex-wrap, kein Overflow bei 390px).
3. **Chart-Hoehe angleichen**: `#wind-card .chart-wrapper` von 240px auf 280px (wie Taschensee).
4. **Bugfix**: `updateWindHeader()` auf `getWindCityIdx()` statt hartem Index 1 umstellen (siehe Befund).
5. **Animationen** (neue Werte duerfen bei echten Aenderungen weich uebergehen, NICHT bei `update('none')`-Hintergrund-Polls):
   a. Zahlenwerte im Kopf/Statzeile (aktuell, Max, Ø): sanftes Hochzaehlen bei tatsaechlicher Wertaenderung (kurze JS-Animation, ca. 400-600ms, z. B. ueber `requestAnimationFrame`), kein Sprung. Bei unveraendertem Wert keine Animation ausloesen (keine Dauerschleife, kein Flackern beim 15-Minuten-Poll).
   b. Kleines Richtungs-Pfeil-Icon neben dem aktuellen Wert im Kartenkopf (CSS `transform: rotate(...)`, `transition: transform 0.6s ease` o. ae.), das bei Richtungswechsel ueber den kuerzesten Drehweg sanft dreht (nicht ueber den vollen Kreis, z. B. 350° -> 10° als +20°, nicht als -340°).
   c. Chart: beim initialen Laden/Range-Wechsel dezentes gestaffeltes Einblenden der Balken (Chart.js `animation.delay`-Callback je Bar-Index), bestehende `duration: 350` beibehalten oder moderat anpassen. `windArrowPlugin` folgt dem Chart-Redraw automatisch (Canvas-Plugin, zeichnet pro Frame neu) - hier keine zusaetzliche Logik noetig, nur sicherstellen, dass nichts bricht.
   d. Legenden-/Statzeile-Badge der aktuell zutreffenden Windstaerke-Zone dezent hervorheben (z. B. kurzer Puls/Scale beim Erreichen einer neuen Zone, danach Ruhezustand - kein Dauerblinken).
6. **Responsive**: alles bei 390px und 1366px+ sauber (kein horizontaler Overflow), Legende/Statzeile brechen bei Bedarf um (bestehende flex-wrap-Patterns verwenden).
7. **Datenquelle unveraendert**: ausschliesslich Open-Meteo API (`wind_speed_10m`/`wind_direction_10m`), keine Pi-/Sensordaten, keine neuen Fetches.

## Pflicht: echte Browser-Verifikation (Chrome-Tool oder Playwright/headless-Chromium-Fallback)
`node --check js/charts.js` und `node --check js/main.js`. Dann `python -m http.server` im Ziel-Repo - Wind-/Temp-Block laden Live-Daten direkt von Open-Meteo (kein lokales JSON noetig, anders als Taschensee/Ostsee/Tanken - diese bleiben unberuehrt).
1. Wind-Karte bei 390px und 1366px: Legende mit Text-Labels sichtbar und lesbar, Statzeile (Aktuell/Max/Ø) gefuellt, Chart sichtbar hoeher als vorher (280px), Karte wirkt insgesamt gefuellt (kein grosser Leerraum mehr).
2. Standort wechseln (Zahnrad -> Hamburg/Kiel/Luebeck/Alle, dann zurueck Gronenberg): Kopfwert UND Chart wechseln synchron (Bugfix-Check aus Befund Punkt 5).
3. Seite frisch laden: Balken blenden gestaffelt ein (sichtbar langsamer/gestuft, kein harter Sofort-Sprung).
4. Range wechseln (1 Tag <-> 3 Tage) bzw. Standort wechseln: Zahlen im Kopf/Statzeile zaehlen sichtbar hoch/runter statt zu springen; Richtungspfeil dreht sanft (kuerzester Weg).
5. Manuelles "Aktualisieren" (Hintergrund-Update-Pfad, `update('none')`): KEINE Balken-Neueinblend-Animation, Verhalten wie bisher (Regressionscheck des bestehenden Kommentars "verhindert Animationen beim Hintergrund-Update").
6. Regressionscheck: Temperatur/Taschensee/Ostsee/Tanken/Regen/Blitz-Bloecke optisch und funktional unveraendert.
7. Browser-Konsole ohne neue Fehler.

## Abschluss
Im Ziel-Repo committen und pushen (Commit-Message beginnt mit "WETTER-0016:"). Dann im ACB-Repo:
`BR run finish WETTER-0016 --status COMPLETED --actor claude-code --commit --summary "<Ziel-Repo-HEAD-SHA, Befund Legende/Statzeile/Hoehe, Befund Bugfix getWindCityIdx, Befund Animationen, Regressionscheck andere Bloecke>"`, `git push`.
Ausgabe NUR: Footer + max. 5 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Befund Kopf/Statzeile, Befund Animationen, Regressionscheck.
- [x] Wind-Karte nutzt die volle Kartenhoehe (Legende mit Labels, Statzeile Aktuell/Max/Ø, Chart 280px)
- [x] Standortwechsel aktualisiert Kopfwert UND Chart synchron (Bugfix getWindCityIdx)
- [x] Zahlen/Richtungspfeil animieren sanft bei echten Aenderungen, Hintergrund-Poll bleibt animationsfrei
- [x] Balken blenden beim initialen Laden/Range-Wechsel gestaffelt ein
- [x] Scope eingehalten (nur index.html Wind-Teil, charts.js Wind-Funktionen, main.js Wind-Funktionen) - andere Bloecke unveraendert
