# WETTER-0009 - Tanken-Button im Haupt-Header (finale Aktivierung)

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0009 |
| project_id | wetter-app |
| Typ / Klasse | FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0008 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0009 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss 956f187416ebc2ef05feb0f70eeeec100a900f5c sein. Abweichung -> STOPP.
3. Scope NUR: `index.html`.

## Hintergrund
Der Header-Button war seit WETTER-0005 bewusst zurueckgestellt (Teil C), bis echte Daten live liefen. Backend (Timer), Frontend (Liste + Preisverlauf-Chart), false/null-Fix und der Deploy-Datei-Fix sind inzwischen alle abgeschlossen und live verifiziert (WETTER-0005 bis 0008). Jetzt der letzte Schritt: sichtbar machen.

## Fix (NUR index.html)
In `.header-left` (enthaelt aktuell nur `#btn-regen`, ca. Zeile 138-139): direkt danach einen neuen Button ergaenzen, gleiche CSS-Klasse `nav-btn` wie `#btn-regen` (ohne `dry`-Modifier, da kein "Status"-Badge noetig), z. B.:
```html
<button class="nav-btn" id="btn-tanken" onclick="window.showTanken()" title="Tankstellenpreise Umkreis Gronenberg" aria-label="Tankstellenpreise öffnen">Tanken</button>
```
Keine weiteren Aenderungen - `window.showTanken` existiert bereits (WETTER-0005/js/main.js), wird hier nur erstmals verlinkt.

## Pflicht: echte Browser-Verifikation
`python -m http.server` im Ziel-Repo. Pruefe per Chrome-Tool:
1. Button "Tanken" erscheint im Header rechts neben "Kein Regen"/Regen-Status-Button.
2. Klick oeffnet die Tanken-Ansicht (Stationsliste + Preisverlauf-Card).
3. "Zurueck" fuehrt korrekt zur Hauptansicht zurueck.
4. Browser-Konsole ohne Fehler.

## Abschluss
`BR run finish WETTER-0009 --status COMPLETED --actor claude-code --commit --summary "<HEAD-SHA, Browser-Verifikations-Befund>"`, `git push`.
Ausgabe NUR: Footer + max. 3 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Browser-Verifikation.
- [x] Button ergaenzt, im Ziel-Repo committet und gepusht (453717a)
- [x] Browser-Verifikation bestanden (Button sichtbar, Ansicht oeffnet/schliesst korrekt)
- [x] Scope eingehalten (nur index.html)
