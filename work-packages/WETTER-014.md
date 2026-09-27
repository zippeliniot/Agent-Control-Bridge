# WETTER-0014 - Mehrspalten-Grid fuer Tablet-Querformat und grosse Monitore

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0014 |
| project_id | wetter-app |
| Typ / Klasse | FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0013 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` mit docs/handover/staging-v12/WETTER-0014.yaml (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0014 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss 5b9179fb8505841395dd7df3e88497662eb6d222 sein (Stand nach WETTER-0013). Abweichung -> STOPP.
3. Scope NUR: `index.html` (CSS im `<style>`-Block + eine id am 7-Tage-Vorschau-Card). KEINE Aenderung an js/*.js.

## Befund (Steuerchat, gegen HEAD 5b9179f geprueft)
- `.page { max-width: 760px; margin: 0 auto; }` (ca. Zeile 18) - auf iPad-Querformat und grossen Monitoren bleibt die App eine schmale Spalte in der Mitte.
- `#main-view` (ca. Zeile 317) hat keine eigene Layout-Regel. Direkte Kinder: `#no-weather-notice`, `#temp-card`, `#wind-card`, `#taschensee-card`, `#sea-card`, `#blitz-card`, 7-Tage-Vorschau-Card (ohne id, enthaelt `#fc-table`), `.controls`, `p.updated`.
- `#main-view` wird von js/regen.js und js/tanken.js per Klasse `.hidden` ausgeblendet (`.hidden { display: none !important; }`) - bleibt wirksam, auch wenn `#main-view` `display: grid` bekommt (wegen `!important`). NICHT anfassen.
- js/main.js blendet `#taschensee-card`, `#blitz-card`, `#sea-card` je Standort per `style.display = ''/'none'` ein/aus - das Grid muss sich dabei sauber neu anordnen.
- Regen-Ansicht (`#regen-header`, `#regen-view`) und Tanken-Ansicht (`#tanken-header`, `#tanken-view`) liegen ebenfalls in `.page` und sollen durch die Verbreiterung NICHT mitwachsen (sonst werden Liste/Radar auf 1800px auseinandergezogen).
- Bestehende Media-Queries (420px, 767px, 768-1199px, 1199px) betreffen nur Header/Kartenkoepfe/Tanken-Overlay - unveraendert lassen.

## Umsetzung (NUR index.html)
1. Der 7-Tage-Vorschau-Card (`<div class="card">` direkt vor `<div class="card-title">7-Tage-Vorschau</div>`) bekommt `id="fc-card"`. Sonst keine Markup-Aenderung.
2. Am Ende des `<style>`-Blocks (direkt vor `</style>`, NACH allen bestehenden Media-Queries) diese zwei neuen Bloecke ergaenzen:
```css
    /* WETTER-0014: Mehrspalten-Grid Tablet-Quer / Desktop */
    @media (min-width: 1000px) {
      .page { max-width: 1240px; }
      #main-view { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; align-items: stretch; }
      #main-view > .card { margin-bottom: 0; }
      #no-weather-notice, #fc-card, #main-view > .controls, #main-view > .updated { grid-column: 1 / -1; }
      #regen-header, #regen-view, #tanken-header, #tanken-view { max-width: 760px; margin-left: auto; margin-right: auto; }
    }
    @media (min-width: 1600px) {
      .page { max-width: 1860px; }
      #main-view { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    }
```
   Hinweise: `minmax(0, 1fr)` ist Pflicht (sonst laufen Chart.js-Canvases ueber die Spalte hinaus). `#regen-header`/`#tanken-header` behalten ihr `margin-bottom` aus `.header-bar` - nur links/rechts auf auto setzen, wie oben. Unter 1000px (Phones, iPad hochkant) bleibt ALLES exakt wie bisher.
3. Keine Aenderung an Chart-Hoehen (Inline `height` der `.chart-wrapper`), an JS-Logik oder an bestehenden CSS-Regeln ausserhalb der zwei neuen Bloecke.

## Pflicht: echte Browser-Verifikation (Chrome-Tool oder Playwright/headless-Chromium-Fallback)
`python -m http.server` im Ziel-Repo. Viewports:
1. **390px** und **820px** (Phone, iPad hochkant): Layout identisch zu vorher - eine Spalte, max. 760px, keine Aenderung sichtbar (Screenshot-Vergleich mit HEAD 5b9179f).
2. **1180px** (iPad Air quer) und **1366px** (iPad Pro quer): zwei Spalten; Temperatur|Wind, Taschensee|Ostsee, Blitz in eigener Zeile links; 7-Tage-Vorschau, Aktualisieren-Leiste und "Stand"-Zeile ueber die volle Breite.
3. **1920px** und **2560px** (grosser Monitor): drei Spalten; 7-Tage-Vorschau/Controls/Stand volle Breite.
4. Bei 1366px und 1920px: alle vier Charts fuellen ihre Spalte, kein horizontaler Scrollbalken (`document.documentElement.scrollWidth <= window.innerWidth`), Fenster-Resize 1920 -> 1180 -> 390 passt die Charts ohne Reload an.
5. Standortwechsel per Zahnrad auf Hamburg (Taschensee/Blitz/Ostsee werden ausgeblendet) und zurueck auf Gronenberg bei 1920px: Grid ordnet sich ohne Luecken/Fehler neu.
6. Bei 1920px: Tanken-Button -> Tanken-Ansicht und Kein-Regen-Button -> Regen-Ansicht bleiben 760px breit und zentriert; Zurueck zur Hauptansicht zeigt wieder das Grid (`.hidden` wirkt weiterhin).
7. Vollbild-Chart (Klick auf einen Kartentitel mit "↗") funktioniert bei 1920px unveraendert.
8. Browser-Konsole ohne neue Fehler (erwartete 404 auf lokal fehlende Datenfiles sind ok, im Summary nennen).

## Abschluss
Im Ziel-Repo committen und pushen (Commit-Message beginnt mit "WETTER-0014:"). Dann im ACB-Repo:
`BR run finish WETTER-0014 --status COMPLETED --actor claude-code --commit --summary "<Ziel-Repo-HEAD-SHA, Befund je Viewport-Gruppe, Regressionscheck Phone/Regen/Tanken>"`, `git push`.
Ausgabe NUR: Footer + max. 5 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Befund Phone/iPad hoch, Befund 2-/3-Spalten, Regressionscheck.
- [x] Unter 1000px (390/820px) Layout unveraendert
- [x] Ab 1000px zwei Spalten, ab 1600px drei Spalten, Vorschau/Controls/Stand volle Breite
- [x] Kein horizontaler Ueberlauf, Charts passen sich beim Resize an, Standortwechsel ordnet Grid sauber neu
- [x] Regen-/Tanken-Ansicht bei grossen Screens weiterhin 760px zentriert
- [x] Scope eingehalten (nur index.html)
