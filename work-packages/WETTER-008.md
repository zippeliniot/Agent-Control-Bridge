# WETTER-0008 - Bugfix: js/tanken.js fehlt dauerhaft in deploy_web.py WEB_FILES

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0008 |
| project_id | wetter-app |
| Typ / Klasse | BUGFIX |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0007 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.
> **HINWEIS:** Kein SSH-Zugriff auf pi5-01 in dieser Session - NICHT versuchen.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0008 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss 0e962dbcf7751f6d07bd6c5a7d29e16e511770c0 sein. Abweichung -> STOPP.
3. Scope NUR: `pi-scripts/deploy_web.py`.

## Befund (Steuerchat, live auf pi5-01 bestaetigt)
WETTER-0005 hat `js/tanken.js` eingefuehrt, `pi-scripts/deploy_web.py` war dabei bewusst NICHT im Scope (Datei war zu dem Zeitpunkt gar nicht Teil des noetigen Deploys, da Teil C/Button noch fehlte). Die feste `WEB_FILES`-Liste in `deploy_web.py` wurde seither nie aktualisiert. Nach dem WETTER-0007-Deploy fehlte `js/tanken.js` auf dem Live-Server (404), waehrend `index.html`/`js/main.js` das Modul bereits per `import * as tanken from './tanken.js'` referenzierten - das haette den kompletten Modul-Import brechen koennen. Als Sofortmassnahme wurde `js/tanken.js` manuell per `deploy_web.py --only js/tanken.js` nachgeschoben (Live-Seite jetzt wieder OK, HTTP 200 bestaetigt) - dieser WP behebt nur die dauerhafte Ursache.

## Fix (eine Zeile, eine Datei)
In `pi-scripts/deploy_web.py`, `WEB_FILES`-Liste: `"js/tanken.js"` ergaenzen (Position egal, z. B. nach `"js/regen.js"`). Sonst nichts aendern.

## Pflicht: Verifikation (kein Browser noetig, reiner Dry-Run reicht)
`python3 -m py_compile pi-scripts/deploy_web.py` (Syntax). Zusaetzlich: `python3 pi-scripts/deploy_web.py --dry-run` lokal ausfuehren (funktioniert auch auf Windows, da nur Dateien aufgelistet werden) und pruefen, dass `js/tanken.js` jetzt in der Ausgabe auftaucht (12 statt 11 Dateien).

## Abschluss
`BR run finish WETTER-0008 --status COMPLETED --actor claude-code --commit --summary "<HEAD-SHA, Dry-Run-Befund: 12 Dateien inkl. tanken.js>"`, `git push`.
Ausgabe NUR: Footer + max. 3 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Dry-Run-Befund.
- [ ] js/tanken.js in WEB_FILES ergaenzt, committet+gepusht
- [ ] Dry-Run zeigt 12 Dateien inkl. js/tanken.js
- [ ] Scope eingehalten (nur pi-scripts/deploy_web.py)
