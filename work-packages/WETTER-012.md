# WETTER-0012 - Tanken-Zahnrad-Panel responsiv: eigenes Overlay fuer iPhone/iPad/Desktop

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0012 |
| project_id | wetter-app |
| Typ / Klasse | BUGFIX |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0011 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0012 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss c0ceb80507a27734f75c59811d97b6c66c120e02 sein. Abweichung -> STOPP.
3. Scope NUR: `index.html`, `js/tanken.js`. NICHT `.settings-menu` (die Klasse des HAUPT-Zahnrad-Menues im Haupt-Header) veraendern - das ist ein separates Element mit kurzen Eintraegen, funktioniert bereits einwandfrei und darf nicht angefasst werden.

## Befund (Steuerchat, per Screenshot bestaetigt)
`#tanken-settings-menu` nutzt aktuell die geteilte Klasse `.settings-menu` (`position: absolute; right: 0; min-width: 190px;`, index.html ca. Zeile 69). Der Inhalt (5 Stations-Checkboxen mit teils langen Namen wie "CLASSIC Tankstellen GmbH & Co. KG · ARAL" + 3 Sorten-Checkboxen) ist deutlich breiter als 190px und hat kein `max-width` - auf schmalen iPhone-Bildschirmen wird das Panel dadurch nach links über den Bildschirmrand hinaus abgeschnitten (Text nicht mehr lesbar).

## Loesung: eigenes, dediziertes Overlay NUR fuer #tanken-settings-menu (3 Breakpoints)
Neue, eigene CSS-Klasse (z. B. `tanken-settings-menu`, NICHT `settings-menu` wiederverwenden) mit komplett eigenem Markup/Styling, angelehnt an das bereits bestehende, bewaehrte `.modal-overlay`/`.modal-box`-Muster (siehe `#impressum-overlay` in index.html, funktioniert bereits zuverlaessig zentriert mit Backdrop-Click-to-close):

1. **Mobil (< 768px, iPhone):** Bottom-Sheet - volle Breite, am unteren Bildschirmrand verankert (`position: fixed; inset: auto 0 0 0;` bzw. per Flexbox `align-items: flex-end` im Overlay-Container), abgerundete Ecken NUR oben, `max-height: 75vh`, `overflow-y: auto` falls Inhalt laenger als Bildschirm. Eigener Backdrop (halbtransparent, wie bei `#impressum-overlay`), Klick auf Backdrop schliesst das Panel. Am Ende ein "Fertig"-Button (schliesst, analog `.modal-close`).
2. **Tablet (768-1199px, iPad):** Zentriertes Modal - `max-width: 480px`, zentriert (horizontal + vertikal wie `.modal-overlay`), abgerundete Ecken ringsum, `max-height: 80vh` scrollbar, gleicher Backdrop wie mobil.
3. **Desktop (>= 1200px):** Verankerter Dropdown NEBEN dem Zahnrad-Button (wie das bisherige Verhalten), aber mit `max-width: 340px` UND `overflow-y: auto; max-height: 70vh;`, damit auch dort nichts mehr abgeschnitten werden kann, egal wie lang Stationsnamen werden. KEIN Vollbild-Backdrop auf diesem Breakpoint (bleibt ein normaler Dropdown, schliesst wie bisher nur ueber den Zahnrad-Button selbst - kein Klick-Ausserhalb-Schliessen noetig, das gab es vorher auch nicht).

## Umsetzung (index.html + js/tanken.js)
1. In `index.html`: neue CSS-Regeln fuer `.tanken-settings-menu` + zugehoerigen Backdrop (z. B. `#tanken-settings-backdrop`, per Default `display:none`, nur in den Mobil/Tablet-Media-Queries als `position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:199;` sichtbar wenn `.open`). Markup um `#tanken-settings-menu` entsprechend ergaenzen (Backdrop-Div davor, "Fertig"-Button am Ende des Panels). Bestehende IDs (`tanken-station-checks`, `tanken-fuel-e5` usw.) NICHT umbenennen - `js/tanken.js` liest diese IDs bereits, keine JS-Anpassung an der Checkbox-Logik noetig.
2. In `js/tanken.js`: neue `export function closeSettings()` (schliesst Panel + Backdrop, analog zu `hide()`), exportiert als `window.tankenCloseSettings` (analog `window.closeImpressum`) - vom Backdrop-`onclick` UND vom neuen "Fertig"-Button aufgerufen. Bestehende `tankenToggleSettings(event)` unveraendert lassen (oeffnet weiterhin ueber den Zahnrad-Button).
3. Keine Aenderung an der Speicher-/Filter-Logik (`prefsChanged`, `isStationChecked`, `render()` usw.) - nur Darstellung/Layout des Panels.

## Pflicht: echte Browser-Verifikation bei ALLEN 3 Breakpoints
`python -m http.server` im Ziel-Repo. Pruefe per Chrome-Tool mit simulierten Viewport-Groessen (z. B. 390px iPhone, 820px iPad, 1440px Desktop):
1. iPhone-Breite: Zahnrad oeffnen - Bottom-Sheet erscheint vollstaendig sichtbar, kein abgeschnittener Text, Backdrop-Klick schliesst, "Fertig"-Button schliesst.
2. iPad-Breite: zentriertes Modal, vollstaendig sichtbar, Backdrop-Klick schliesst.
3. Desktop-Breite (>=1200px): Dropdown neben dem Zahnrad wie bisher, vollstaendig sichtbar auch mit langen Stationsnamen, kein Abschneiden.
4. Bei allen 3: Checkbox-Aenderungen wirken weiterhin sofort auf Liste/Chart (Funktionalitaet aus WETTER-0010/0007 unveraendert).
5. Haupt-Zahnrad-Menue (`#settings-menu` im Haupt-Header) unveraendert getestet - funktioniert weiterhin wie vorher (Regressionscheck, da geteilte CSS-Klasse `.settings-menu` NICHT veraendert wurde).
6. Browser-Konsole bei allen 3 Breakpoints ohne Fehler.

## Abschluss
`BR run finish WETTER-0012 --status COMPLETED --actor claude-code --commit --summary "<HEAD-SHA, Befund je Breakpoint, Regressionscheck Haupt-Zahnrad>"`, `git push`.
Ausgabe NUR: Footer + max. 5 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Befund je der 3 Breakpoints, Regressionscheck-Befund.
- [ ] Mobil: Bottom-Sheet vollstaendig sichtbar, Backdrop+Fertig-Button schliessen
- [ ] Tablet: zentriertes Modal vollstaendig sichtbar
- [ ] Desktop: Dropdown vollstaendig sichtbar (max-width+scroll), kein Abschneiden mehr
- [ ] Haupt-Zahnrad-Menue unveraendert funktionsfaehig (Regressionscheck)
- [ ] Filter-Funktionalitaet (Stationen/Sorten) bei allen 3 Breakpoints unveraendert
- [ ] Scope eingehalten (nur index.html, js/tanken.js; .settings-menu selbst unangetastet)
