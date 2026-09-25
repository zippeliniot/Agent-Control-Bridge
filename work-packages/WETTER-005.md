# WETTER-0005 - Tankstellenpreise (Tankerkoenig-API): Pi-Export + Frontend-Ansicht

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0005 |
| project_id | wetter-app |
| Typ / Klasse | FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0004 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.
> **WICHTIG:** Dieser Auftrag laeuft auf Windows (Claude Code hat KEINEN SSH-Zugriff auf pi5-01). Teil A schreibt/committet nur den Code fuer den Pi - die Aktivierung dort (git pull, systemd install, Credential eintragen) macht der Steuerchat anschliessend manuell mit April per SSH. NICHT versuchen, sich mit dem Pi zu verbinden.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0005 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss 3873bff1be18976a47a89f0d34f6c4a8bfca98d7 sein. Abweichung -> STOPP.
3. Scope NUR: siehe Dateiliste je Teil unten. **Teil C (Nav-Button) NICHT umsetzen** - eigener, spaeterer Schritt, erst nach Live-Verifikation mit echten Daten.

## Hintergrund / Architektur-Entscheid (mit April abgestimmt)
Kein API-Key im Frontend (das ist eine oeffentlich einsehbare statische Seite). Stattdessen exakt das bestehende Muster von Taschensee/Ostsee: ein Python-Skript auf pi5-01 holt die Daten serverseitig (Key aus der SQLite-DB `/opt/climac/data/climac.db`, Tabelle `credentials`, wie in `pi-scripts/climac_sftp.py` `get_credential()`), schreibt eine JSON-Datei, die per SFTP hochgeladen wird. Das Frontend liest nur noch diese statische JSON (`data/tanken.json`), exakt wie `data/live.json`.

Tankerkoenig-API (offiziell dokumentiert, Basis `https://creativecommons.tankerkoenig.de/json/`):
- `list.php?lat=..&lng=..&rad=..(max 25)&type=all&sort=dist&apikey=..` - Umkreissuche, liefert Stationsliste INKL. Preisen.
- `prices.php?ids=<kommagetrennte Stations-IDs>&apikey=..` - reine Preis-Aktualisierung fuer bekannte Stationen (leichter Call).
- Tankerkoenig empfiehlt selbst (Support-Antwort): NICHT bei jedem Refresh `list.php` neu abfragen, sondern `list.php` selten (z. B. taeglich, da sich die Stationsliste kaum aendert) und `prices.php` fuer die regelmaessigen Preis-Updates.
- Lizenz verlangt sichtbare Quellenangabe "Daten von Tankerkoenig" mit Link auf `https://creativecommons.tankerkoenig.de` im Frontend, sobald live.

GROUPS (von April vorgegeben, aktuell nur eine Gruppe, aber als Liste anlegen fuer spaetere Erweiterung):
```python
GROUPS = [
    {"name": "OH1", "lat": 54.0441, "lng": 10.7080, "radius_km": 5.0, "desc": "Gronenberg 5 km"},
]
```

## Teil A - Pi-Export-Skripte (NUR im Ziel-Repo: pi-scripts/)
Dateien: `pi-scripts/export_tanken_stations.py`, `pi-scripts/export_tanken_prices.py`, `pi-scripts/systemd/climac-tanken-stations.service`, `pi-scripts/systemd/climac-tanken-stations.timer`, `pi-scripts/systemd/climac-tanken-prices.service`, `pi-scripts/systemd/climac-tanken-prices.timer`, `pi-scripts/systemd/install.sh` (UNITS-Liste erweitern).

1. In `climac_sftp.py`: NICHTS aendern, nur `get_credential("tankerkoenig_api")` wiederverwenden - neue `cred_id`-Konstante `TANKERKOENIG_CRED_ID = "tankerkoenig_api"` in einem der neuen Skripte definieren (Key liegt im Feld `secret` des Credential-Datensatzes, `target`/`port`/`user`/`path` bleiben bei diesem Credential-Typ leer).
2. `export_tanken_stations.py` (taeglich): fuer jede Gruppe in `GROUPS` `list.php` aufrufen, Ergebnis (Stations-IDs + Stammdaten: name, brand, street, houseNumber, postCode, place, lat, lng, dist) in einen lokalen Cache schreiben: `/opt/climac/data/tanken_stations_cache.json` (NICHT oeffentlich, nur Pi-lokal). Danach direkt `data/tanken.json` mit den frisch geholten Preisen aus derselben list.php-Antwort erzeugen und per `ClimacSFTP().upload_file(...)` hochladen (Struktur wie unten).
3. `export_tanken_prices.py` (alle 15 Min, wie `climac-live-export`): liest den lokalen Stations-Cache aus Schritt 2, ruft `prices.php` mit den gecachten IDs auf, aktualisiert NUR die Preise + `updated_at` in `data/tanken.json`, laedt per SFTP hoch. Falls der Cache fehlt (noch kein taeglicher Lauf): sauber ueberspringen und loggen, kein Crash.
4. `data/tanken.json`-Schema:
```json
   {
     "updated_at": "2026-09-25T14:30:00+02:00",
     "attribution": "Daten von Tankerkoenig (https://creativecommons.tankerkoenig.de)",
     "groups": [
       {"name": "OH1", "lat": 54.0441, "lng": 10.708, "radius_km": 5.0, "desc": "Gronenberg 5 km",
        "stations": [
          {"id": "...", "name": "...", "brand": "...", "street": "...", "houseNumber": "...",
           "postCode": "...", "place": "...", "lat": 0.0, "lng": 0.0, "dist": 0.0,
           "isOpen": true, "diesel": 1.699, "e5": 1.859, "e10": 1.799}
        ]}
     ]
   }
```
5. Beide Skripte: `Type=oneshot`, `User=mp01`, `WorkingDirectory=/opt/climac/web/wetter-app/pi-scripts` (exakt wie `climac-live-export.service`). Timer: `climac-tanken-stations.timer` taeglich (`OnCalendar=*-*-* 00:10:00`, nach dem bestehenden Daily-Export um 00:05), `climac-tanken-prices.timer` alle 15 Min (`OnCalendar=*:0/15`, wie `climac-live-export.timer`).
6. `install.sh`: die vier neuen Units in die `UNITS`-Liste und die Enable-Schleife aufnehmen (nur ergaenzen, bestehende Eintraege nicht anfassen).
7. `node --check` entfaellt (Python) - stattdessen `python3 -m py_compile pi-scripts/export_tanken_stations.py pi-scripts/export_tanken_prices.py` lokal auf Windows zur Syntaxpruefung (kein echter API-Call moeglich ohne Key - das macht der Steuerchat spaeter auf dem Pi).

## Teil B - Frontend-Ansicht (index.html + neues js/tanken.js)
1. Neues `#tanken-view` (hidden by default) in `index.html`, strukturell analog `#regen-view`: eigener Zurueck-Button `#btn-tanken-back`, Card mit Liste der Stationen.
2. Neues `js/tanken.js`, strukturell analog `js/regen.js`: `export function show()` (zeigt `#tanken-view`, laedt `data/tanken.json` per `fetch(..., {cache:'no-store'})`, rendert), `export function hide()`.
3. Anzeige je Station: Name/Marke, Adresse, Entfernung, Preise E5/E10/Diesel, offen/geschlossen-Badge. Sortierung: Umschalter E5/E10/Diesel (aehnlich `range-toggle`-Muster), Default sortiert nach E5 aufsteigend (guenstigste zuerst). Offline/fehlende Preise (`null`) dimmen statt Fehler.
4. Pflicht (Lizenzbedingung): Attribution-Zeile am Ende sichtbar - "Daten von Tankerkoenig" verlinkt auf `https://creativecommons.tankerkoenig.de` - sowie `updated_at` als "Stand: ..." Zeitstempel.
5. In `index.html`: `<script type="module">`-Import von `tanken.js` ergaenzen (wie bei `regen.js` in `main.js` oder direkt, je nachdem wie die anderen Module eingebunden sind - bestehendes Muster in `index.html`/`main.js` uebernehmen, nicht neu erfinden).
6. **KEIN Button im Header** in diesem Teil - `window.showTanken`/`window.hideTanken` als globale Funktionen exportieren (wie `window.showRegen`/`window.showMain`), aber noch nirgends im sichtbaren UI verlinken. Testen laesst sich das trotzdem ueber die Browser-Konsole (`window.showTanken()`).

## Teil C - NICHT in diesem Lauf umsetzen
Der Button neben `#btn-regen` (`.header-left`) kommt erst in einem eigenen, spaeteren Schritt, nachdem die Pi-Skripte aktiviert sind, ein echter API-Key eingetragen ist und echte Daten sichtbar live gepueft wurden. Falls du versucht bist, den Button trotzdem schon einzubauen: NICHT TUN, das ist expliziter Scope.

## Pflicht: Browser-Verifikation
`python -m http.server` im Ziel-Repo. Da `data/tanken.json` ohne echten Pi-Lauf nicht existiert: lege lokal eine Testdatei `data/tanken.json` mit 2-3 Beispielstationen (Fantasiewerte, klar als Test erkennbar) an, NUR um das Rendering zu pruefen - NICHT committen (in `.gitignore` oder vor dem Commit wieder loeschen). Pruefe per Chrome-Tool: `window.showTanken()` in der Konsole ausfuehren, Liste erscheint, Sortierung/Umschalter funktionieren, Attribution sichtbar, Konsole ohne Fehler.

## Abschluss
`BR run finish WETTER-0005 --status COMPLETED --actor claude-code --commit --summary "<HEAD-SHA, Teil A/B-Befund, Browser-Verifikations-Befund>"`, `git push`.
Ausgabe NUR: Footer + max. 5 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Teil-A-Befund, Teil-B-Befund, Browser-Verifikation.
- [x] Teil A: beide Export-Skripte + 4 systemd-Units + install.sh-Ergaenzung, nur pi-scripts/, committet+gepusht (1ab7db7)
- [x] Teil B: tanken-view + tanken.js, nur index.html (Ergaenzung) + js/tanken.js, committet+gepusht (9e31fe7)
- [x] Teil C NICHT umgesetzt (kein Header-Button)
- [x] Browser-Verifikation mit lokaler Testdatei bestanden, Testdatei NICHT committet
- [x] Attribution + Zeitstempel im Frontend vorhanden
- [x] Scope eingehalten (siehe Dateiliste je Teil)
