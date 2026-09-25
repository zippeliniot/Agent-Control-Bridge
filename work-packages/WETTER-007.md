# WETTER-0007 - Tanken: Preisverlauf-Chart (3 Tage) + Zahnrad-Auswahl Stationen/Sorten pro Geraet

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0007 |
| project_id | wetter-app |
| Typ / Klasse | FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0006 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.
> **HINWEIS:** Kein SSH-Zugriff auf pi5-01 in dieser Session - NICHT versuchen. Aktivierung/Verifikation mit echten Daten macht der Steuerchat anschliessend manuell.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0007 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss 64896c9db3ba68a778a80e9831bc88bf728fc600 sein. Abweichung -> STOPP.
3. Scope NUR: `pi-scripts/export_tanken_prices.py`, `index.html`, `js/tanken.js`, `js/main.js`.

## Wichtiger Hinweis zu den Daten
Tankerkoenig liefert nur AKTUELLE Preise, keine Historie. Ein Verlauf kann erst AB Aktivierung dieses Features entstehen (kein rueckwirkendes Auffuellen moeglich) - nach 3 Tagen ist die Grafik dann voll. Das ist normal, nicht als Fehler werten.

## Architektur-Entscheid (mit April abgestimmt)
Kein festes "guenstigste Station"-Aggregat. Stattdessen: Zahnrad-Icon (analog zum bestehenden `.settings-btn`/`.settings-menu`-Muster im Haupt-Header) oben rechts im Tanken-Screen. Darueber waehlt der Nutzer PRO GERAET (persistiert in `localStorage`, kein Server-State), welche Stationen und welche Kraftstoffsorten im Verlaufs-Chart als Linien erscheinen sollen - damit steuert der Nutzer selbst die Uebersichtlichkeit.

## Teil A - Historie sammeln (NUR pi-scripts/export_tanken_prices.py erweitern)
Dieses Skript laeuft schon alle 15 Min (Timer bereits aktiv) und holt ohnehin alle Preise. Zusaetzlich:
1. Nach dem gewohnten `data/tanken.json`-Update: einen kompakten Verlaufspunkt an eine lokale/oeffentliche `data/tanken_history.json` anhaengen:
```json
   {
     "updated_at": "2026-09-25T15:05:00+02:00",
     "retained_days": 3,
     "points": [
       {"t": "2026-09-25T15:05:00+02:00", "prices": {"<station_id>": {"e5":2.389,"e10":2.329,"diesel":2.449}, "...": {...}}}
     ]
   }
```
2. Existierende `data/tanken_history.json` per SFTP-Download lesen (falls vorhanden - `ClimacSFTP` hat dafuer schon eine Download-Methode, siehe `climac_sftp.py`), neuen Punkt anhaengen, alle Punkte AELTER als 3 Tage (`retained_days`) verwerfen (Vergleich ueber `t`, nicht ueber Anzahl - robust gegen Ausfaelle/Luecken), dann hochladen. Falls kein Download moeglich (Datei existiert noch nicht): frisch anlegen.
3. Kein Crash, falls das fehlschlaegt - Preis-Update selbst (`data/tanken.json`) darf davon nicht abhaengen; History-Schreibfehler nur loggen.

## Teil B - Zahnrad + Einstellungen (index.html + js/tanken.js)
1. In `#tanken-header`: neuer Button analog `.settings-btn` (gleiche Optik, eigene ID z. B. `#tanken-settings-btn`), oeffnet ein Panel `#tanken-settings-menu` (gleiches `.settings-menu`-Muster) mit:
   - Checkbox je Station (Name/Marke), Default: alle angehakt.
   - Checkbox je Sorte E5/E10/Diesel, Default: E10 + Diesel angehakt (E5 nicht, wie von April vorgegeben).
2. Auswahl bei jeder Aenderung sofort in `localStorage` unter `tanken-chart-prefs` als JSON `{"stationIds": [...], "fuels": [...]}` speichern; beim Laden der Ansicht aus `localStorage` lesen (fehlt der Eintrag: Default wie oben).
3. Titel "Preisverlauf ↗" als eigene Card/Zeile im Tanken-Screen (analog `<span class="card-title" onclick="window.openFS('tanken')">`), oeffnet das bestehende Vollbild-Chart-Modal.
4. `export function getFSConfig()` in `js/tanken.js` (analog `seewasser.getFSConfig()`): baut eine Chart.js-Konfiguration aus `data/tanken_history.json`, gefiltert auf die per Einstellungen gewaehlten Stationen+Sorten (eine Linie je Kombination aus Station und Sorte), mit 1-Tag/3-Tage-Umschalter (eigener kleiner State in `tanken.js`, gleiches `range-btn`-Muster wie anderswo, NICHT `currentRange` aus `main.js` wiederverwenden - eigener Kontext). Keine Daten/Datei fehlt: sinnvoller Leerzustand statt Fehler.

5. Auto-Refresh: solange `#tanken-view` sichtbar ist, alle 5 Minuten `data/tanken.json` automatisch neu laden (Preis-Update-Timer auf dem Pi laeuft alle 15 Min, 5 Min Frontend-Intervall reicht). Umsetzung: neuer `remainingTanken`/`TANKEN_INTERVAL = 300`-Zweig im bestehenden globalen 1-Sekunden-Tick in `main.js` (Zeile ~431, gleiches Muster wie `remainingRegen`/`remainingWeather`), ruft bei Ablauf eine neue `export function refresh()` in `js/tanken.js` auf (laedt nur neu, wenn `isActive()` true ist - sonst no-op, kein unnoetiger Fetch im Hintergrund).

## Teil C - Anbindung ans Vollbild-Modal (NUR main.js, minimal)
In `window.openFS(type)`: einen `else if (type === 'tanken')`-Zweig ergaenzen, der wie beim `seewasser`-Fall `tanken.getFSConfig()` aufruft und den Titel setzt (z. B. "Tankstellenpreise Verlauf"). Keine sonstigen Aenderungen an `openFS`/`closeFS`.

## Pflicht: echte Browser-Verifikation
`python -m http.server` im Ziel-Repo. Lokale Testdateien `data/tanken.json` (wie gehabt) UND `data/tanken_history.json` mit ein paar Testpunkten ueber >1 Tag anlegen, NICHT committen. Pruefe per Chrome-Tool:
1. Zahnrad oeffnet Einstellungen, Checkboxen fuer Stationen/Sorten vorhanden, Default E10+Diesel angehakt, alle Stationen angehakt.
2. Auswahl aendern, Seite neu laden (F5) - Auswahl bleibt erhalten (localStorage funktioniert).
3. "Preisverlauf ↗" oeffnet Vollbild-Chart, zeigt nur die ausgewaehlten Linien, 1-Tag/3-Tage-Umschalter funktioniert.
4. Browser-Konsole ohne Fehler.

## Abschluss
`BR run finish WETTER-0007 --status COMPLETED --actor claude-code --commit --summary "<HEAD-SHA, Teil A/B/C-Befund, Browser-Verifikations-Befund>"`, `git push`.
Ausgabe NUR: Footer + max. 5 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Teil-A-Befund, Teil-B/C-Befund, Browser-Verifikation.
- [x] Teil A: Verlaufs-Sammlung in export_tanken_prices.py, 3-Tage-Trimming ueber Zeitstempel, kein Crash bei Fehlern (0e962db)
- [x] Teil B: Zahnrad+Panel, localStorage-Persistenz, getFSConfig() mit Stations-/Sorten-Filter + 1-Tag/3-Tage, Auto-Refresh alle 5 Min nur wenn Ansicht aktiv (0e962db)
- [x] Teil C: openFS('tanken')-Anbindung, minimal (0e962db)
- [x] Browser-Verifikation bestanden (inkl. F5-Persistenz-Test)
- [x] Scope eingehalten (nur die 4 genannten Dateien)
