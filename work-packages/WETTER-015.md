# WETTER-0015 - Vergleich-Tab: Luft Min/Max pro Jahr und Monat, Jahre ein-/ausblendbar

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0015 |
| project_id | wetter-app |
| Typ / Klasse | FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0014 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` mit docs/handover/staging-v12/WETTER-0015.yaml (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0015 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss bcae82b0e51f052ba4e4c7df220084cd00aa48ab sein (Stand nach WETTER-0014). Abweichung -> STOPP.
3. Scope NUR: `js/seewasser.js`. KEINE Aenderung an index.html, anderen js/*.js oder pi-scripts/*.

## Befund (Steuerchat, gegen HEAD bcae82b geprueft)
- Taschensee-Karte, Tab "Vergleich": `cfgVergleich()` in js/seewasser.js zeichnet je Jahr eine Wasserlinie (`history.years[cmpSensor]`, alle in Abstufungen EINER Farbe), aber das Luft-Band nur fuer das AKTUELLE Jahr: `history.at_monthly[cy]` mit `cy = new Date().getFullYear()` -> `atBand(...)`. Deshalb sieht man pro Monat nur ein Min und ein Max statt der Werte jedes Jahres.
- Die Daten sind schon vollstaendig vorhanden: `history.at_monthly` = `{ "<Jahr>": { min:[12], max:[12], avg:[12] }, ... }` fuer ALLE Jahre ab 2015 (export_history.py, `AT_START = 2015-01-01`). Wasserdaten (`history.years.sw40/swgr`) gibt es erst ab 2023. Es ist KEINE Aenderung am Export noetig.
- `monthlyToDoy(arr12)` wandelt 12 Monatswerte in 365 DOY-Stufenwerte um und bleibt die Basis.
- Legende ist per `baseOptions()` aus (`legend: { display: false }`), der Tooltip filtert Labels mit `_`-Praefix.
- Sub-Steuerung des Vergleich-Tabs: `renderSubctrl()` -> Buttons "40 cm" / "Grund" in `#sw-subctrl` (`window.swCmp`).
- Vollbild nutzt `lastCfg` (Kopie der aktuellen Chart-Config) - ausgeblendete Jahre muessen dort ebenfalls fehlen.

## Umsetzung (NUR js/seewasser.js)
1. **Jahresliste im Vergleich:** Vereinigung der Jahre aus `history.years[cmpSensor]` und `history.at_monthly`, aufsteigend sortiert.
2. **Eine feste Farbe pro Jahr:** Palette mit gut unterscheidbaren Farben auf dunklem Hintergrund, die Zuordnung Jahr -> Farbe ist stabil (haengt nur von der sortierten Gesamt-Jahresliste ab, NICHT davon, welche Jahre gerade sichtbar sind oder welcher Sensor gewaehlt ist). Bei mehr Jahren als Palettenfarben: HSL-Farben gleichmaessig verteilt. Die Farbe gilt fuer ALLE Linien dieses Jahres.
3. **Datasets je sichtbarem Jahr** (in cfgVergleich, ersetzt das bisherige Einfarb-Schema und das atBand des aktuellen Jahres):
   - Wasserlinie (nur wenn fuer das Jahr vorhanden): Label = Jahr (z. B. "2025"), Jahresfarbe, durchgezogen, borderWidth 1.6, aktuelles Jahr 2.5.
   - "Luft max. <Jahr>": `monthlyToDoy(at_monthly[Jahr].max)`, Jahresfarbe, gestrichelt `[6, 3]`, borderWidth 1.2, `tension: 0`, `pointRadius: 0`, `spanGaps: false`, keine Fuellung.
   - "Luft min. <Jahr>": wie oben mit `.min`, gepunktet `[2, 3]`.
   - Kein Luft-Ø und KEIN Fuellband im Vergleich-Tab (bei mehreren Jahren unlesbar). Die Referenzlinie (`history.ref`, C_REF) bleibt unveraendert als letztes Dataset.
   - Tooltip (mode index) zeigt damit je Jahr Wasser / Luft max. / Luft min. - bestehende Tooltip-Logik unveraendert lassen.
4. **Jahre ein-/ausblenden:** In `renderSubctrl()` im Vergleich-Tab unter den Buttons "40 cm"/"Grund" eine zweite Zeile mit einem Button je Jahr (Inline-Style fuer den Zeilen-Container: `display:flex; flex-wrap:wrap; justify-content:center; gap:6px; width:100%`, damit auch 12 Jahre auf dem Handy umbrechen; `#sw-subctrl` selbst bekommt fuer diesen Tab per Inline-Style `flex-wrap:wrap`, in anderen Tabs zuruecksetzen).
   - Sichtbares Jahr: Button mit Rand und Hintergrund in Jahresfarbe (Hintergrund halbtransparent), ausgeblendetes Jahr: neutral/gedimmt (opacity 0.4).
   - Klick schaltet das Jahr um (neue globale Funktion `window.swCmpYear(jahr)`) und rendert neu. Ausgeblendete Jahre werden NICHT als Datasets erzeugt (damit sind sie auch im Vollbild weg).
   - Zustand als Modul-Variable (Set der ausgeblendeten Jahre), bleibt beim Wechsel 40 cm/Grund und beim Tab-Wechsel innerhalb der Sitzung erhalten. Kein localStorage.
   - **Standard beim ersten Oeffnen:** die letzten 3 Jahre sichtbar, alle aelteren ausgeblendet.
   - Das letzte sichtbare Jahr darf nicht ausgeblendet werden koennen (Klick darauf ignorieren), damit der Chart nie leer ist.
5. Info-Text (`ensureInfoText`) um einen Satz ergaenzen: "Vergleich: je Jahr eine Farbe - Linie = Wasser, gestrichelt = Luft max., gepunktet = Luft min. (Monatswerte); Jahre per Button ein-/ausblendbar."
6. Tabs Aktuell/Woche/Monat/Jahr und das dortige Luft-Band (`atBand`) bleiben komplett unveraendert.

## Pflicht: echte Browser-Verifikation (Chrome-Tool oder Playwright/headless-Chromium-Fallback)
`node --check js/seewasser.js`. Dann `python -m http.server` im Ziel-Repo. Da `data/history.json` lokal fehlt: aktuelle Live-Datei `https://wetter.gronenberg.info/data/history.json` herunterladen und NUR fuer den Test nach `data/history.json` legen (NICHT committen, danach loeschen; falls der Download scheitert: Testdatei mit mind. 4 Jahren at_monthly und 3 Jahren sw40/swgr erzeugen, ebenfalls nicht committen).
1. Tab Vergleich bei 390px und 1366px: je sichtbarem Jahr eine Farbe; pro Monat sind fuer JEDES sichtbare Jahr eigene Luft-max.- und Luft-min.-Stufen in der Jahresfarbe zu sehen; Wasserlinie gleiche Farbe.
2. Standard: genau die letzten 3 Jahre sichtbar, aeltere Jahres-Buttons gedimmt.
3. Jahr ausblenden -> alle drei Linien dieses Jahres verschwinden; wieder einblenden -> gleiche Farbe wie vorher. Letztes sichtbares Jahr laesst sich nicht ausblenden.
4. Umschalten 40 cm <-> Grund: Jahresauswahl und Farben bleiben erhalten.
5. Tooltip zeigt fuer einen Tag je sichtbarem Jahr Wasser / Luft max. / Luft min. mit Jahreszahl im Label.
6. Vollbild (Kartentitel mit "↗") im Vergleich-Tab: zeigt nur die sichtbaren Jahre.
7. Regressionscheck Tabs Aktuell, Woche, Monat, Jahr: unveraendert (Luft-Band orange wie bisher).
8. Handy 390px: Jahres-Buttons brechen sauber um, kein horizontaler Ueberlauf.
9. Browser-Konsole ohne neue Fehler (erwartete 404 auf lokal fehlende Datenfiles sind ok, im Summary nennen).
Testdatei data/history.json vor dem Commit loeschen, `git status` darf nur js/seewasser.js zeigen.

## Abschluss
Im Ziel-Repo committen und pushen (Commit-Message beginnt mit "WETTER-0015:"). Dann im ACB-Repo:
`BR run finish WETTER-0015 --status COMPLETED --actor claude-code --commit --summary "<Ziel-Repo-HEAD-SHA, Befund Jahresfarben/Luft min-max je Jahr, Befund Ein-/Ausblenden + Standard, Regressionscheck andere Tabs>"`, `git push`.
Ausgabe NUR: Footer + max. 5 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Befund Luft min/max je Jahr, Befund Ein-/Ausblenden, Regressionscheck.
- [ ] Vergleich-Tab zeigt pro Monat Luft max./min. fuer jedes sichtbare Jahr in dessen Jahresfarbe
- [ ] Wasserlinie und Luftlinien eines Jahres in derselben, stabilen Farbe
- [ ] Jahre per Button ein-/ausblendbar, Standard letzte 3 Jahre, nie leerer Chart, gilt auch im Vollbild
- [ ] Tabs Aktuell/Woche/Monat/Jahr unveraendert
- [ ] Scope eingehalten (nur js/seewasser.js)
