# WETTER-0003 - Kopfzeilen-Konsistenz: aktuelle Werte in Temperatur/Wind analog Taschensee/Ostsee

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0003 |
| project_id | wetter-app |
| Typ / Klasse | FEATURE (additiv, kein Architektur-Entscheid) |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0002 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> ZWEI Repositories, nicht verwechseln:
> (1) ACB-Repo, lokal `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` - NUR fuer Task/Result/Audit/diese WP-Datei.
> (2) Ziel-Repo `zippeliniot/wetter-app`, lokal `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0003 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` muss sauber sein, HEAD muss 4831a8e5bcfaf599a577261395fa6240da0b1691 sein (Stand nach WETTER-0002). Abweichung -> STOPP (CONCEPT_CONFLICT).
3. Scope NUR im Ziel-Repo: `index.html`, `js/main.js`. Keine anderen Dateien. Im ACB-Repo NUR diese WP-Datei (Haken) + Store-Dateien aus Schritt 1/5.

## Ausgangslage (Steuerchat-Befund, per Code-Review bestaetigt)
`js/api.js` (`fetchCityData`/`fetchAllCitiesData`) fragt fuer jede Stadt bereits einen `current`-Block ab (`temperature_2m, relative_humidity_2m, apparent_temperature, weather_code, wind_speed_10m, wind_direction_10m, precipitation, uv_index`) - diese Daten liegen also in `cachedData[i].current.*` vor, werden aber bisher NIRGENDS angezeigt. Nur die Kopfzeilen der Karten "Taschensee" (`#sw-current`) und "Ostsee" (`#sea-current`) zeigen rechts oben aktuelle Werte; "Temperatur & Niederschlag" und "Wind · Gronenberg" zeigen dort nur eine statische Legende. April wuenscht die gleiche Optik/Konsistenz fuer diese beiden Karten. Vorhandene Hilfsfunktion `getWindCityIdx()` (js/main.js, liefert bei `currentLocation==='all'` Index 1/Gronenberg, sonst den gewaehlten Stadt-Index) und `getWindDir(deg)` (js/utils.js, Grad -> Himmelsrichtungskuerzel) koennen direkt wiederverwendet werden.

## Teil A - Kopfzeile "Temperatur & Niederschlag" (index.html Zeile ~239-254, js/main.js)
1. In `index.html` im `.chart-head` von `#temp-card` einen neuen Span rechts neben/ueber der Legende ergaenzen, z. B. `<span id="temp-current" style="font-size:1.05rem;font-weight:700;opacity:0.9;"></span>` (gleiche Optik wie `#sw-current`/`#sea-current`).
2. In `js/main.js` eine Funktion `updateTempHeader()` ergaenzen: nutzt `getWindCityIdx()` fuer die Referenzstadt (gleiche Logik wie beim Wind-Kartentitel), liest `cachedData[idx].current.temperature_2m` und `cachedData[idx].current.precipitation`, formatiert mit Staedte-Kuerzel aus `ABBR` (config.js), z. B. `GR 12.4° · 0.0 mm`. Bei fehlenden Daten leeres Ergebnis (kein Fehlertext).
3. Aufruf von `updateTempHeader()` an ALLEN Stellen ergaenzen, an denen `applyLocationFilter()` bereits aufgerufen wird (Standortwechsel) UND in BEIDEN Zweigen von `loadAll()` (`if (!shellBuilt)` UND `else`) - nicht denselben Fehler wie bei WETTER-0002 Teil B wiederholen (Kopf blieb dort im Kaltstart-Pfad leer, weil der Aufruf nur an einer Stelle stand).

## Teil B - Kopfzeile "Wind · Gronenberg" (index.html Zeile ~256-267, js/main.js)
1. In `index.html` im `.chart-head` von `#wind-card` einen neuen Span rechts neben der Schwellen-Legende ergaenzen, z. B. `<span id="wind-current" style="font-size:1.05rem;font-weight:700;opacity:0.9;"></span>`.
2. In `js/main.js` eine Funktion `updateWindHeader()` ergaenzen: IMMER Gronenberg (CITIES[1] bzw. index 1, unabhaengig vom Standortfilter - der Kartentitel ist fest "Wind · Gronenberg"), liest `cachedData[1].current.wind_speed_10m` und `cachedData[1].current.wind_direction_10m`, formatiert mit `getWindDir()` aus `js/utils.js`, z. B. `7 km/h NW`.
3. Aufruf von `updateWindHeader()` an denselben Stellen wie `updateTempHeader()` ergaenzen (beide Zweige von `loadAll()`).

## Teil C - Ostsee-Kopfzeile: NUR verifizieren, nicht anfassen
`#sea-current` wurde bereits in WETTER-0002 gefixt (Aufruf von `updateSeaHeader()` im Kaltstart-Pfad ergaenzt). Kein Code-Aendern hier, NUR pruefen: `localStorage.clear()` im Browser, Seite neu laden, `#sea-current` zeigt sofort einen Wert. Falls doch ein Fehler auffaellt: NICHT selbst reparieren (Scope-Verletzung), sondern im Abschluss-Bericht explizit benennen.

## Manuelle Pruefung (fuer Teil A + B)
`python -m http.server` im Ziel-Repo, Seite oeffnen, Browser-Konsole ohne Fehler. Pruefen:
- `#temp-current` zeigt sofort einen Wert beim Erstladen (auch mit geleertem `localStorage`).
- `#wind-current` zeigt sofort einen Wert beim Erstladen (auch mit geleertem `localStorage`).
- Standort in den Einstellungen wechseln (z. B. Hamburg): `#temp-current` aktualisiert sich auf die neue Stadt, `#wind-current` bleibt "Gronenberg"-Werte (Kartentitel aendert sich nicht).
Kein Screenshot noetig, nur Befund in der Zusammenfassung.

## Abschluss
`BR run finish WETTER-0003 --status COMPLETED --actor claude-code --commit --summary "<inkl. HEAD-SHA von E:\_DEV\Wetter-App nach Teil A+B, Befund Teil C>"`, `git push` (ACB-Repo).
Ausgabe NUR: Footer (Auftrag/Lauf/Status) + max. 5 Zeilen: ACB-HEAD, Ziel-Repo-HEAD (SHA), Teil-A-Befund, Teil-B-Befund, Teil-C-Befund.
- [x] Teil A umgesetzt (temp-current, Erstladen + Standortwechsel funktionieren), im Ziel-Repo committet und gepusht
- [x] Teil B umgesetzt (wind-current, Erstladen funktioniert, immer Gronenberg), im Ziel-Repo committet und gepusht
- [ ] Teil C verifiziert (Ostsee-Kopf funktioniert weiterhin nach Cache-Leerung) - kein Codeaendern falls OK - NICHT geprueft, kein Browser-Tool verfuegbar (Claude-in-Chrome-Extension in dieser Session nicht verbunden)
- [ ] Manuelle Pruefung ohne Konsolenfehler bestanden - NICHT durchfuehrbar, kein Browser-Tool verfuegbar; nur statische Pruefung (node --check, Code-Review) gemacht
- [x] Scope eingehalten (nur index.html, js/main.js im Ziel-Repo)
