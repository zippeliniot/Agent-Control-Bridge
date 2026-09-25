# WETTER-0006 - Bugfix: Tankerkoenig liefert `false` statt `null` bei fehlender Kraftstoffsorte

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0006 |
| project_id | wetter-app |
| Typ / Klasse | BUGFIX |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0005 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.
> **HINWEIS:** Kein SSH-Zugriff auf pi5-01 in dieser Session - NICHT versuchen. Aktivierung/Test mit echten Daten macht der Steuerchat anschliessend manuell.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0006 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss 9e31fe7a2b4383a450f6f72c970f4af2c3f0f13c sein. Abweichung -> STOPP.
3. Scope NUR: `pi-scripts/export_tanken_stations.py`, `pi-scripts/export_tanken_prices.py`, `js/tanken.js`.

## Befund (Steuerchat, per echten Live-Daten auf pi5-01 bestaetigt)
Live-Aufruf von `data/tanken.json` (echte Tankerkoenig-Antwort) zeigt fuer Stationen ohne E10 z. B. `"e10":false` (Boolean, nicht `null`). Tankerkoenig liefert bei nicht gefuehrten Sorten offenbar `false` statt `null`. `js/tanken.js` `fmtPrice(v)` prueft nur `v == null` - `false == null` ist in JS `false`, also faellt `false` NICHT in den "—"-Zweig, sondern `false.toFixed(3)` wird aufgerufen -> `TypeError: v.toFixed is not a function`. Das reisst `render()` (innerhalb `.map()`) komplett ab, sobald irgendeine Station eine Sorte nicht fuehrt - bei den echten Daten (5 Stationen) betrifft das bereits 2 von 5.

## Fix (zwei Ebenen - beide umsetzen)
1. **Root Cause, Python (beide Export-Skripte):** Preisfelder beim Schreiben normalisieren - `False`/nicht-numerische Werte zu `None` mappen, bevor sie in die JSON-Payload geschrieben werden. Kleine Hilfsfunktion, z. B.:
```python
   def _num_or_none(v):
       return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
```
   (Python: `bool` ist eine Unterklasse von `int`, daher der explizite `isinstance(v, bool)`-Ausschluss.) Anwenden auf `diesel`/`e5`/`e10` in `_station_full()` (stations-Skript) und in der entsprechenden Preis-Zusammenstellung im prices-Skript.
2. **Verteidigung, Frontend (`js/tanken.js`):** `fmtPrice(v)` UND die Sortier-Vergleichsfunktion in `render()` robust gegen jeden Nicht-Zahl-Wert machen (`typeof v !== 'number'` statt nur `v == null`), damit ein kuenftiger API-Eigenheit-Fall (egal welcher Typ) nie wieder das ganze Rendering zum Absturz bringt.
3. Keine weiteren Aenderungen - insbesondere Schema/Feldnamen/Sortierlogik sonst unangetastet.

## Pflicht: echte Browser-Verifikation MIT den echten Randfall-Daten
`python -m http.server` im Ziel-Repo. Lokale Testdatei `data/tanken.json` diesmal NICHT mit Fantasiedaten, sondern mit einer Station, die `"e10": false` (oder `"e10": null`) hat, um genau diesen Fall abzudecken - NICHT committen. Pruefe per Chrome-Tool: `window.showTanken()`, Liste rendert vollstaendig inkl. der Station mit fehlender Sorte (zeigt "—" statt Absturz), Sortierung funktioniert weiter, Browser-Konsole ohne Fehler.

## Abschluss
`BR run finish WETTER-0006 --status COMPLETED --actor claude-code --commit --summary "<HEAD-SHA, Fix-Befund, Browser-Verifikations-Befund>"`, `git push`.
Ausgabe NUR: Footer + max. 4 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Fix-Befund, Browser-Verifikation.
- [ ] Python-Normalisierung in beiden Export-Skripten umgesetzt
- [ ] Frontend-Haertung in js/tanken.js umgesetzt (fmtPrice + Sortierung)
- [ ] Browser-Verifikation MIT false/null-Randfall bestanden (nicht nur Idealfall)
- [ ] Scope eingehalten (nur die 3 genannten Dateien)
