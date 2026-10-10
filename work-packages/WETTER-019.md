# WETTER-0019: Wind-Card Umbau — Header analog Taschensee, Tabs, Tages-Max-Linien

## Kontext

Die Wind-Card (`#wind-card` in `index.html`) bekommt wie die Taschensee-Card (`#taschensee-card`,
`js/seewasser.js`) ein Tab-System mit Historienansicht. Grundlage: WETTER-0016 (Layout/Legende),
WETTER-0017 (Pi-Export gemessener Wind, GW2000A) und WETTER-0018 (Historie
`wind_gust_max_monthly`) sind bereits ausgeliefert.

**Nicht anfassen:** `js/seewasser.js` und das Markup von `#taschensee-card` — nur als Vorbild lesen,
keine Änderung an Struktur, Funktionen oder Verhalten der Taschensee-Card.

## 1. Header (`index.html`, `#wind-card`)

Aktuell:
```html
<div class="card" id="wind-card">
  <div class="chart-head">
    <span class="card-title" id="wind-card-title" onclick="window.openFS('wind')">Wind · Gronenberg km/h ↗</span>
    <div class="chart-head-value">
      <span id="wind-current" class="wind-current" ...>...</span>
      <div class="wind-thr">...4 wt-item...</div>
    </div>
  </div>
  <div class="wind-stats" id="wind-stats">...3 ws-item...</div>
  <div class="chart-wrapper" style="height: 280px;"><canvas id="wind-chart"></canvas></div>
</div>
```

Änderung:
- `#wind-stats` (Aktuell/Max/Ø-Zeile, WETTER-0016) **komplett entfernen** — Markup, zugehörige
  `.wind-stats`-CSS kann bleiben falls noch anderweitig genutzt, sonst ebenfalls entfernen.
- `#wind-current` und `.wind-thr` bleiben **beide** erhalten, genau wie heute im
  `chart-head-value`-Bereich (Wert + Legende nebeneinander, Anordnung analog `#sw-current` +
  `.sw-legend` bei Taschensee — strukturell, nicht inhaltlich verändern).
- `updateWindHeader()` / `highlightWindZone()` / `rotateWindArrow()` in `main.js` bleiben
  funktional unverändert (arbeiten weiter auf denselben Element-IDs).
- `updateWindStatLine()` in `main.js` und alle Aufrufe davon **entfernen** (Funktion wird durch
  Wegfall von `#wind-stats` obsolet — aktuell aufgerufen aus `updateWindHeader()` und den
  Stellen, die `windChart` neu befüllen, siehe `main.js` Zeilen ~223/251/314).
- Neu einfügen: Tab-Leiste analog `.sw-tabs` + Subcontrol-Container:
```html
<div class="range-toggle wind-tabs" role="group" style="margin-bottom:4px;">
  <button class="range-btn active" data-tab="aktuell"   onclick="window.windSetTab('aktuell')">Aktuell</button>
  <button class="range-btn"        data-tab="woche"     onclick="window.windSetTab('woche')">Woche</button>
  <button class="range-btn"        data-tab="monat"     onclick="window.windSetTab('monat')">Monat</button>
  <button class="range-btn"        data-tab="jahr"      onclick="window.windSetTab('jahr')">Jahr</button>
  <button class="range-btn"        data-tab="vergleich" onclick="window.windSetTab('vergleich')">Vergleich</button>
</div>
<div class="wind-subctrl" id="wind-subctrl"></div>
```
- `windZonesPlugin` in `charts.js` (4-Farbzonen + gestrichelte 15/25/50-Linien im Chart) **bleibt
  unverändert**.

## 2. Neues Modul `js/wind.js`

Struktur direkt nach Vorbild `js/seewasser.js` (gleiche Funktionsnamen, Präfix `wind` statt `sw`
bzw. eigene Namen wo sinnvoll):

- `getJSON(url)`, `loadLive()`, `loadMonth(key)`, `loadHistory()` — gleiche Datenquellen
  (`data/live.json`, `data/months/YYYY-MM.json`, `data/history.json`), nur die relevanten
  Wind-Felder extrahieren (`wind_gust_max` aus `live.json`; `wind_gust_max_max` aus den
  Monatsdateien — einzige sinnvolle Spalte laut WETTER-0018-Dokukopf in `export_daily.py`;
  `wind_gust_max_monthly` aus `history.json`).
- `activeTab` State-Variable, `buildConfig()`-Dispatcher analog `seewasser.js`:
  - `aktuell` → neue Funktion (siehe Abschnitt 3), ersetzt/erweitert bisheriges
    `getWindChartConfig()` aus `charts.js`.
  - `woche` → Tagesmaxima letzte 7 Tage aus `months/*.json` (`wind_gust_max_max`), heutiger Tag
    ggf. aus `live.json → wind_gust_max` nachgezogen (Pattern wie `cfgDailyWindow()` bei
    sw40/swgr in `seewasser.js`).
  - `monat` → aktueller Monat aus `months/YYYY-MM.json`, fehlende/heutige Tage wie oben ergänzt.
  - `jahr` → `history.json → wind_gust_max_monthly` für ein Jahr, Navigation wie `cfgJahr()`
    (Jahr-Cursor, `window.windYearDelta()`).
  - `vergleich` → `wind_gust_max_monthly` über mehrere Jahre, Jahr-Ein-/Ausblenden analog
    `cfgVergleich()`/`ensureCmpDefaultVisibility()`.
- `renderSubctrl()` analog: Monat-/Jahr-Navigation (‹ Monat/Jahr ›), Vergleich-Jahr-Buttons;
  bei `aktuell` leer (Legende steht schon im Header).
- `render()` analog: `buildConfig()` awaiten, Chart auf `#wind-chart` neu aufbauen
  (`new Chart(...)`, vorherige Instanz `destroy()`).
- `refreshLive()` (export, wie `seewasser.refreshLive`): `loadLive()` neu laden, bei
  `activeTab === 'aktuell'` neu rendern (für die heutige Max-Linie, siehe unten).
- `initWind()` (export): initiale Daten laden, `render()` aufrufen.
- window-Handler: `window.windSetTab(tab)` (analog `window.swSetTab`), `window.windMonth(delta)`,
  `window.windYearDelta(delta)`, `window.windCmpYear(key)` — nur die für die jeweiligen Tabs
  tatsächlich benötigten.

## 3. Tab "Aktuell" — Balkenchart + Tages-Max-Linien

- Der bestehende Balkenchart bleibt **unverändert**: `charts.getWindChartConfig()`
  (Wetter-API-Forecast, `hourly.wind_speed_10m`), 1-Tag/3-Tage-Range wie heute, inkl.
  `dayNightPlugin`/`windZonesPlugin`/`windArrowPlugin`.
- Neu: pro angezeigtem Kalendertag ein zusätzliches Chart.js-Dataset, das eine horizontale Linie
  nur über die Stunden-Indizes dieses einen Tages zeichnet (restliche Indizes `null`,
  `spanGaps: false`, `stepped: true`, dünn, gestrichelt — Stil analog `atBand()`'s
  `borderDash`-Linien in `seewasser.js`, eigene dezente Farbe z. B. `rgba(255,255,255,0.55)`).
- **Wertequelle pro Tag:**
  - **Heute:** `live.json → wind_gust_max` (gemessener GW2000A-Tagesmaximalwert, live — NICHT
    der Mittelwert/Durchschnitt aus den Forecast-Balken).
  - **Zukünftige Tage** (nur im 3-Tage-Modus sichtbar): `max()` über die Forecast-Stundenwerte
    (`hourly.wind_speed_10m`) der Stunden-Indizes, die zu diesem Kalendertag gehören.
- Tooltip für dieses Dataset: z. B. „Tagesmax: X km/h (gemessen)“ bzw. „… (Vorhersage)“ je nach
  Quelle, damit der Unterschied sichtbar ist.
- Implementierung kann in `wind.js` erfolgen (Datum-Grenzen aus den Chart-Labels ableiten, analog
  `getStartIndex`/`getSharedTimeRange` in `charts.js`) oder als zusätzlicher Export aus
  `charts.js`, der von `wind.js` aufgerufen wird — Claude Code entscheidet nach bestehendem
  Codestil, was sauberer ist.

## 4. Tabs "Woche"/"Monat"/"Jahr"/"Vergleich"

Gemessene GW2000A-Historiendaten, siehe Abschnitt 2. Keine Forecast-Daten in diesen Tabs.
Darstellung als einfache Linie (kein Band nötig, da nur ein Max-Wert pro Tag/Monat — kein
Min/Mittel sinnvoll, siehe WETTER-0018-Dokukommentare in `export_daily.py`/`export_history.py`).

## 5. main.js — Wiring

- `import * as wind from './wind.js';` ergänzen.
- In `DOMContentLoaded`: `wind.initWind();` neben `seewasser.initSeewasser();` aufrufen.
- Im periodischen Live-Refresh (dort wo `seewasser.refreshLive();` steht, Zeile ~465):
  `wind.refreshLive();` ergänzen.
- Alten Code entfernen, der jetzt obsolet ist: `windChart`-Variable, direkte
  `charts.getWindChartConfig()`-Aufrufe in `main.js` (Zeilen ~220–251, ~337–342),
  `updateWindStatLine()` und deren Aufrufe — das übernimmt ab jetzt `wind.js` intern
  (analog dazu, dass `seewasser.js` seinen Chart komplett selbst verwaltet und `main.js` davon
  nichts weiß außer `initSeewasser()`/`refreshLive()`).
- `updateWindHeader()` (Wert + Pfeil + Legenden-Highlight) bleibt in `main.js`, ruft aber nicht
  mehr `updateWindStatLine()` auf.
- Stadt-Umschaltung (`setLocation`) für den Wind-Chart-Titel bleibt wie bisher — die
  Forecast-Balken in "Aktuell" sind weiterhin stadtabhängig; Woche/Monat/Jahr/Vergleich sind
  ausschließlich Gronenberg (einziger GW2000A-Standort), das ist in `wind.js` zu berücksichtigen
  (Tabs ggf. ausblenden/Hinweis bei anderer Stadt — Claude Code soll dafür eine sinnvolle,
  unaufdringliche Lösung wählen, analog wie andere standortgebundene Cards im Projekt gehandhabt
  werden).

## 6. Nicht Teil dieses WP

- Keine Änderung an `pi-scripts/*` (Datenpipeline ist seit WETTER-0017/0018 fertig).
- Keine Änderung an `js/seewasser.js` oder `#taschensee-card`.

## 7. Nach Abschluss

- Review in diesem Steuerchat wie gehabt.
- **Manueller `deploy_web.py`-Lauf nötig** (Frontend-Änderung, lädt sich nicht selbst hoch).

---

Hinweise für Claude Code (Windows), wie in der Chat-Übergabe festgehalten:
- Vor Ausführung `/model` auf Claude Sonnet 5 / MEDIUM setzen und in der ersten Antwortzeile
  bestätigen.
- Bei `run finish`: `--base-head <ACB-Repo-HEAD-SHA bei run start>` explizit übergeben
  (`git.expected_head`-Doppelnutzung).
