# WETTER-0018 - Historie fuer Tages-Boenhoechstwert (max_daily_gust_3) - Pi-seitig

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0018 |
| project_id | wetter-app |
| Typ / Klasse | FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0017 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.
>
> **Besonderheit (wie WETTER-0017):** reine Pi-/Datenpipeline-Aenderung, KEIN Frontend. Der Windows-Klon
> `E:\_DEV\Wetter-App` hat KEINEN InfluxDB-/SQLite-Zugriff - Verifikation hier NUR statisch
> (`python -m py_compile`). Die echte Datenverifikation erfolgt separat durch den Steuerchat mit
> April auf pi5-01, NACH deinem Push, VOR der Archivierung.
>
> **Korrektur zu WETTER-0017:** dort wurde `wind_gust_max` (`sensor.gw2000a_max_daily_gust_3`) bewusst
> NICHT in die Tages-/Jahres-Historie aufgenommen, mit der (fuer die DAMALIGE Spalten-Logik richtigen)
> Begruendung "ist bereits ein Tagesmaximum, Min/Max/Mittel ergibt darauf keinen Sinn". Das uebersah
> aber Aprils eigentlichen Wunsch: die vom Sensor selbst gefuehrten Tageshoechstwerte sollen historisch
> vergleichbar sein (Tag/Monat/Jahr). Dieser Auftrag holt das nach.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` mit docs/handover/staging-v12/WETTER-0018.yaml (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0018 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss f6efb5907e5ddff2986c709c1b0849968798d236 sein (Stand nach WETTER-0017). Abweichung -> STOPP.
3. Scope NUR: `pi-scripts/export_daily.py`, `pi-scripts/export_history.py`. KEINE Aenderung an `climac_sftp.py` (der Key `wind_gust_max` existiert dort bereits aus WETTER-0017, nichts zu tun), `export_live.py` (unveraendert, liefert `wind_gust_max` schon live), `export_tanken_*.py`, `deploy_web.py`, `systemd/*`, oder Frontend-Dateien.
4. **Wichtiger fachlicher Hinweis zum Verstaendnis, NICHT zum Nachbauen - nur zur Einordnung:** `sensor.gw2000a_max_daily_gust_3` ist ein vom Sensor selbst gefuehrter, INNERHALB des Tages monoton steigender Zaehler, der um Mitternacht auf ~0 resettet. Eine InfluxDB-`aggregateWindow`-Abfrage mit `fn: max` ueber einen vollen Kalendertag liefert daher exakt den vom Sensor erreichten Tageshoechstwert (der Tagesmaximalwert der Rohreihe IST der gesuchte Wert) - `fn: min`/`fn: mean` ergeben auf dieser Rohreihe dagegen KEINEN sinnvollen Wert (sie wuerden den Reset-nahen Niedrigwert bzw. einen bedeutungslosen Mittelwert ueber Reset-Zyklen hinweg liefern). Das gilt genauso fuer eine Monats-Aggregation: `fn: max` ueber einen vollen Kalendermonat liefert exakt den Monats-Hoechstwert der Boe.

## Umsetzung
1. **`export_daily.py`**: `"wind_gust_max"` zusaetzlich in das bestehende `SENSORS`-Tupel aufnehmen (gleiche Zeile wie `wind_speed` aus WETTER-0017: `SENSORS = {key: SENSOR_MEASUREMENTS[key] for key in ("sw40", "swgr", "at", "ah", "wind_speed", "wind_gust_max")}`). Das erzeugt automatisch drei Spalten `wind_gust_max_min`/`wind_gust_max_max`/`wind_gust_max_mean` in `months/YYYY-MM.json` (bestehende Spalten-Erzeugungslogik, `COLS`-Schleife unveraendert lassen). **Bewusst in Kauf genommen:** `wind_gust_max_min`/`_mean` sind semantisch bedeutungslos (siehe Hinweis oben) und werden vom Frontend nie gelesen - nur `wind_gust_max_max` ist der gesuchte Tageshoechstwert. Kein Sonderfall im Code noetig, Doku-Kommentar am Dateikopf ergaenzen, der das genau so erklaert (damit niemand spaeter versehentlich `wind_gust_max_min`/`_mean` fuer echte Werte haelt).
2. **`export_history.py`**:
   - Neue Konstante `WIND_GUST_MAX_MEASUREMENTS = SENSOR_MEASUREMENTS["wind_gust_max"]` (nutzt denselben `WIND_START`, da gleiche Station).
   - In `main()`: `wind_gust_max_months_full = query_months(client, WIND_GUST_MAX_MEASUREMENTS, WIND_START)` (bestehende Funktion, liefert bereits `{jahr: {min:[12], max:[12], avg:[12]}}` - unveraendert lassen, KEINE neue Flux-Query-Funktion noetig).
   - Daraus NUR die `max`-Reihe extrahieren: `wind_gust_max_monthly = {y: d["max"] for y, d in wind_gust_max_months_full.items()}` (flaches Dict `{jahr: [12 floats|null]}`, analog zur Struktur, die `at_monthly`/`wind_monthly` NICHT 1:1 ist - bewusst einfacher, da nur ein Wert pro Monat sinnvoll ist, siehe Hinweis oben).
   - Payload um Top-Level-Feld `"wind_gust_max_monthly": wind_gust_max_monthly` erweitern (neben dem bestehenden `"wind_monthly"` aus WETTER-0017, NICHT ersetzen).
   - KEINE DOY-Tagesreihe (`years.wind_gust_max`) ergaenzen - nicht Teil dieses Scopes, Monats-Aufloesung reicht fuer den geplanten Vergleich (analog Taschensee Luft-min/max im Vergleich-Tab, nicht die taegliche DOY-Wasserlinie).
   - Logging-Zeile analog `wind_monthly` fuer `wind_gust_max_monthly` ergaenzen.
   - Docstring-Kopf um den neuen Sensor/die Monats-Struktur ergaenzen (inkl. kurzer Erklaerung "nur Max sinnvoll, Min/Mittel bewusst nicht exportiert").
3. Keine Aenderung an bestehenden Sensor-Logiken (sw40/swgr/at/ah/bld/blt/bln/wind_speed/wind_gust/wind_dir bleiben unberuehrt), an `query_years`/`query_months`/`_flux`/`_flux_monthly` (unveraendert wiederverwendet), an `load_reference`, `ClimacSFTP` oder SFTP-Pfaden.

## Pflicht: Verifikation (angepasst - kein Browser, keine lokale Ausfuehrung moeglich)
`python -m py_compile pi-scripts/export_daily.py pi-scripts/export_history.py`. Mehr ist von `E:\_DEV\Wetter-App` aus NICHT moeglich (kein InfluxDB-Zugriff). Keine Playwright-/Browser-Verifikation noetig.

## Abschluss
Im Ziel-Repo committen und pushen (Commit-Message beginnt mit "WETTER-0018:"). Dann im ACB-Repo:
`BR run finish WETTER-0018 --status COMPLETED --actor claude-code --commit --base-head <ACB-Repo-HEAD-SHA zu Beginn deines Laufs, NICHT der Ziel-Repo-SHA> --summary "<Ziel-Repo-HEAD-SHA, welche Spalten/Felder in welcher Datei ergaenzt, py_compile-Ergebnis, Hinweis dass echte Datenverifikation auf pi5-01 durch den Steuerchat erfolgt>"`, `git push`.
**Hinweis zu `--base-head`:** bei WETTER-0017 hat der automatische Fallback (aus `task.yaml: git.expected_head`, das bei uns den Ziel-Repo-SHA traegt) bei `run finish` einen Fail-Closed-Stopp ausgeloest, weil dieses Feld intern (BRIDGE-0095) als ACB-Repo-interner Ahnen-Check verwendet wird, nicht als Ziel-Repo-Referenz. Bitte DESHALB von Anfang an `--base-head` explizit mit dem ACB-Repo-HEAD-SHA setzen, den du beim `run start` in Schritt 1 notierst (NICHT den Ziel-Repo-SHA aus Schritt 2) - erspart den Nacharbeits-Schritt aus WETTER-0017.
Ausgabe NUR: Footer + max. 5 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, welche Dateien/Felder ergaenzt, py_compile-Ergebnis, Hinweis Pi-Verifikation steht aus.
- [x] `export_daily.py`: `wind_gust_max` im `SENSORS`-Tupel, erzeugt `wind_gust_max_max` (und ungenutzte `_min`/`_mean`) in `months/YYYY-MM.json`
- [x] `export_history.py`: `wind_gust_max_monthly` (flaches `{jahr: [12 floats|null]}`, nur Max) als neues Top-Level-Feld in `history.json`
- [x] Bestehende Felder/Sensoren (inkl. `wind`/`wind_monthly` aus WETTER-0017) unveraendert
- [x] Scope eingehalten (nur `export_daily.py`/`export_history.py`), `py_compile` fehlerfrei
