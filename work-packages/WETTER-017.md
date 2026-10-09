# WETTER-0017 - Export-Pipeline fuer gemessenen Wind (GW2000A) - Pi-seitig

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0017 |
| project_id | wetter-app |
| Typ / Klasse | FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0016 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.
>
> **Besonderheit dieses Auftrags:** reine Pi-/Datenpipeline-Aenderung, KEIN Frontend. Der Windows-Klon
> `E:\_DEV\Wetter-App` hat KEINEN InfluxDB-/SQLite-Zugriff - eine echte Ausfuehrung der geaenderten
> Skripte ist von dort aus NICHT moeglich. Verifikation hier daher NUR statisch (`python -m py_compile`).
> Die echte Datenverifikation (laeuft der Export wirklich, sind die neuen Felder in live.json/
> months/*.json/history.json korrekt befuellt) erfolgt NICHT durch dich, sondern separat durch den
> Steuerchat zusammen mit April auf pi5-01 selbst, NACH deinem Push, VOR der Archivierung. Das ist
> normal fuer diesen Auftrag, kein Grund zum Anhalten.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` mit docs/handover/staging-v12/WETTER-0017.yaml (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0017 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss 17a6d6a1224b7c96ed451b41e4462011233efbb1 sein (Stand nach WETTER-0016). Abweichung -> STOPP.
3. Scope NUR: `pi-scripts/climac_sftp.py`, `pi-scripts/export_live.py`, `pi-scripts/export_daily.py`, `pi-scripts/export_history.py`. KEINE Aenderung an `index.html`, `js/*.js`, `pi-scripts/export_tanken_*.py`, `pi-scripts/deploy_web.py`, `pi-scripts/systemd/*`, `pi-scripts/test_export.py` (letztere nur lesen, falls es hilft die Testerwartungen zu verstehen, aber nicht aendern - Scope-Erweiterung auf Tests nur nach Rueckfrage).

## Befund (Steuerchat, gegen HEAD 17a6d6a geprueft)
- `climac_sftp.py` haelt `SENSOR_MEASUREMENTS` zentral (Logik-Key -> Liste von HA-Measurement-Namen); `export_live.py`/`export_daily.py`/`export_history.py` lesen ausschliesslich daraus, nie eigene Sensornamen.
- Vier neue, von April bestaetigte Sensoren (GW2000A), Messdaten in InfluxDB vorhanden **seit 2025-01-22**:
  - `sensor.gw2000a_wind_speed` - aktuelle Windgeschwindigkeit (das, was im Frontend kuenftig als "gemessen, aktuell herrschend" gezeigt wird)
  - `sensor.gw2000a_wind_gust` - aktuelle Boe
  - `sensor.gw2000a_wind_direction` - aktuelle Richtung (Grad)
  - `sensor.gw2000a_max_daily_gust_3` - von der Station selbst gefuehrter Tageshoechstwert der Boe (resettet taeglich, kein eigenes Aggregat noetig)
- `export_live.py`: `SENSORS`-Dict liefert aktuelle Werte fuer `live.json` (Muster `at`/`ah`: `{"m": [...], "nd": <Nachkommastellen>, "range": "-30m"}`, kein `track`/Offline-Fallback noetig wie bei sw40/swgr). `HOURS_KEYS` (72h-Reihe `hours.json`) wird fuer diesen Auftrag NICHT erweitert - wird aktuell von keinem geplanten Wind-Tab benoetigt (Woche-Tab nutzt bei Taschensee Monatsdateien + live.json, nicht hours.json).
- `export_daily.py`: `SENSORS`-Tupel (`{key: SENSOR_MEASUREMENTS[key] for key in (...)}`) erzeugt automatisch `<key>_min`/`<key>_max`/`<key>_mean`-Spalten in `months/YYYY-MM.json`; ein zusaetzlicher Key erweitert `COLS` automatisch (Schleife existiert bereits).
- `export_history.py`: feste Konstanten `SW40_START`/`SWGR_START`/`AT_START` + `query_years`/`query_months` liefern `years`/`at_monthly` im `history.json`-Payload - neuer Wind-Zweig analog `at`/`at_monthly`, eigene Start-Konstante.
- `BACKFILL_START = (2023, 6)` in `export_daily.py` ist global fuer alle Sensoren; vor dem tatsaechlichen Wind-Datenbeginn (2025-01-22) liefert die InfluxDB-Abfrage fuer Wind einfach keine Punkte -> Spalten bleiben `null`, genau wie bei SWGR vor dessen Start (kein Sonderfall noetig).

## Umsetzung
1. **`climac_sftp.py`**: `SENSOR_MEASUREMENTS` um vier neue Keys erweitern:
   ```python
   "wind_speed": ["sensor.gw2000a_wind_speed"],
   "wind_gust":  ["sensor.gw2000a_wind_gust"],
   "wind_dir":   ["sensor.gw2000a_wind_direction"],
   "wind_gust_max": ["sensor.gw2000a_max_daily_gust_3"],
   ```
   Kommentarzeile am Dateikopf (`#   sw40 : ...`) um die vier neuen Keys ergaenzen (Konsistenz mit bestehendem Stil).
2. **`export_live.py`**: `SENSORS`-Dict um die vier Keys erweitern (Muster `at`/`ah`, `range: "-30m"`, `nd`: 1 fuer `wind_speed`/`wind_gust`/`wind_gust_max`, `nd`: 0 fuer `wind_dir`). Kein `track`. Docstring-Kopf entsprechend ergaenzen (Beispiel-JSON-Ausgabe aktualisieren). `HOURS_KEYS`/`query_hours` NICHT anfassen (siehe Befund).
3. **`export_daily.py`**: `SENSORS`-Tupel um `"wind_speed"` erweitern (liefert `wind_speed_min`/`wind_speed_max`/`wind_speed_mean` in `months/YYYY-MM.json`). Docstring-Kopf entsprechend ergaenzen. `wind_gust`/`wind_dir`/`wind_gust_max` NICHT in die taegliche Min/Max/Mittel-Aggregation aufnehmen (nicht sinnvoll fuer Boe/Richtung/bereits-Tagesmaximum) - nur `wind_speed`.
4. **`export_history.py`**:
   - Neue Konstante `WIND_START = "2025-01-22T00:00:00Z"`.
   - `WIND_MEASUREMENTS = SENSOR_MEASUREMENTS["wind_speed"]`.
   - In `main()`: `wind = query_years(client, WIND_MEASUREMENTS, WIND_START)` und `wind_monthly = query_months(client, WIND_MEASUREMENTS, WIND_START)`, analog `at`/`at_monthly`.
   - Payload erweitern: `"years": {"sw40": sw40, "swgr": swgr, "at": at, "wind": wind}`, zusaetzliches Top-Level-Feld `"wind_monthly": wind_monthly`.
   - Logging-Zeilen analog `at`/`at_monthly` fuer `wind`/`wind_monthly` ergaenzen.
   - Docstring-Kopf um den neuen Sensor/Zeitraum ergaenzen.
5. Keine Aenderung an SQLite-Zugriff (`load_reference`), an `ClimacSFTP`, an den SFTP-Upload-Pfaden oder an bestehenden Sensor-Logiken (sw40/swgr/at/ah/bld/blt/bln bleiben unberuehrt).
6. `pi-scripts/test_export.py` (vorhanden) nur LESEN, falls es helfen soll Erwartungen an Datenformate zu verstehen - NICHT aendern (Tests anzupassen ist nicht Teil dieses Scopes).

## Pflicht: Verifikation (angepasst - kein Browser, keine lokale Ausfuehrung moeglich)
`python -m py_compile pi-scripts/climac_sftp.py pi-scripts/export_live.py pi-scripts/export_daily.py pi-scripts/export_history.py`. Mehr ist von `E:\_DEV\Wetter-App` aus NICHT moeglich (kein InfluxDB-/SQLite-Zugriff). Keine Playwright-/Browser-Verifikation noetig (kein Frontend betroffen). Im Abschluss-Summary explizit vermerken, dass die echte Datenverifikation separat auf pi5-01 erfolgt.

## Abschluss
Im Ziel-Repo committen und pushen (Commit-Message beginnt mit "WETTER-0017:"). Dann im ACB-Repo:
`BR run finish WETTER-0017 --status COMPLETED --actor claude-code --commit --summary "<Ziel-Repo-HEAD-SHA, welche vier Keys/Sensoren in welchen der vier Dateien ergaenzt wurden, py_compile-Ergebnis, Hinweis dass echte Datenverifikation auf pi5-01 durch den Steuerchat erfolgt>"`, `git push`.
Ausgabe NUR: Footer + max. 5 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, welche Dateien/Keys ergaenzt, py_compile-Ergebnis, Hinweis Pi-Verifikation steht aus.
- [x] `climac_sftp.py`: vier neue `SENSOR_MEASUREMENTS`-Keys (`wind_speed`/`wind_gust`/`wind_dir`/`wind_gust_max`)
- [x] `export_live.py`: alle vier Keys liefern aktuelle Werte in `live.json`
- [x] `export_daily.py`: `wind_speed_min`/`_max`/`_mean` in `months/YYYY-MM.json`
- [x] `export_history.py`: `years.wind` (Jahresreihe) + `wind_monthly` (Monats-Min/Max/Ø) ab 2025-01-22 in `history.json`
- [x] Scope eingehalten (nur die vier genannten `pi-scripts/*.py`-Dateien), `py_compile` fehlerfrei
