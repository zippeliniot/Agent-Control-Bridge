# WETTER-0010 - Zahnrad-Auswahl filtert auch die Stationsliste (nicht nur den Chart)

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0010 |
| project_id | wetter-app |
| Typ / Klasse | FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0009 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0010 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss 453717af38019a30dac8e1a9e82cf66e063bd524 sein. Abweichung -> STOPP.
3. Scope NUR: `js/tanken.js`.

## Befund (Steuerchat)
Die Zahnrad-Auswahl (Stationen/Sorten, `prefs`) wirkt bisher NUR auf `getFSConfig()` (Preisverlauf-Chart). `render()` (die normale Stationsliste im Tanken-Screen) ignoriert `prefs` komplett - zeigt immer alle Stationen mit allen drei Preisen. April moechte, dass abgewaehlte Stationen/Sorten auch aus der Liste verschwinden.

## Fix (NUR js/tanken.js)
1. In `render()`: vor dem Sortieren die Stationsliste auf `isStationChecked(st.id)` filtern (Funktion existiert bereits). Ergibt die Filterung eine leere Liste, obwohl `stations` nicht leer ist: eigener Hinweistext "Keine Stationen ausgewaehlt (siehe ⚙)" statt des bestehenden "Keine Stationen gefunden" (das bleibt fuer den Fall reserviert, dass `data/tanken.json` wirklich leer ist).
2. Je Station: nur die Preis-Zeilen (E5/E10/Diesel) anzeigen, deren Sorte in `prefs.fuels` enthalten ist (statt immer alle drei). Ist `prefs.fuels` leer: ebenfalls eigener Hinweistext "Keine Kraftstoffsorte ausgewaehlt (siehe ⚙)" statt der Liste.
3. Sortier-Umschalter (`#tanken-sort-toggle`, drei feste Buttons E5/E10/Diesel in index.html, NICHT aendern): per JS (z. B. in `render()` oder einer kleinen `renderSortToggle()`-Funktion) die Buttons fuer nicht ausgewaehlte Sorten ausblenden (`style.display = 'none'`), fuer ausgewaehlte wieder einblenden. Ist `sortKey` aktuell eine abgewaehlte Sorte (z. B. Nutzer deaktiviert die Sorte, nach der gerade sortiert wird): automatisch auf die erste noch ausgewaehlte Sorte umschalten (Reihenfolge E5 -> E10 -> Diesel), `sortKey` + aktive Button-Klasse entsprechend aktualisieren. Sind gar keine Sorten ausgewaehlt: Umschalter komplett ausblenden (die Liste zeigt ohnehin den Hinweistext aus Punkt 2).
4. `prefsChanged()` muss nach dem Speichern der Auswahl `render()` (inkl. Sortier-Umschalter-Update) erneut aufrufen, damit die Liste sofort reagiert, ohne dass die Ansicht neu geladen werden muss.
5. Default-Zustand beim allerersten Aufruf (kein gespeicherter `localStorage`-Eintrag, `DEFAULT_FUELS = ['e10','diesel']`): `sortKey` sollte dann ebenfalls direkt auf 'e10' initialisiert werden statt des bisherigen festen 'e5' (das waere sonst eine Sorte, die per Default gar nicht angezeigt wird - unstimmiger Startzustand). Nur den initialen Default anpassen, keine sonstige Logik.

## Pflicht: echte Browser-Verifikation
`python -m http.server` im Ziel-Repo, lokale Test-`data/tanken.json` mit 3+ Stationen (nicht committen). Pruefe per Chrome-Tool:
1. Zahnrad oeffnen, eine Station abwaehlen -> verschwindet sofort aus der Liste (kein Neuladen noetig).
2. E5 abwaehlen (Standard-Zustand) -> keine E5-Preiszeile in den Karten, E5-Sortier-Button nicht sichtbar.
3. Alle Sorten abwaehlen -> Hinweistext statt Liste, Sortier-Umschalter verschwindet.
4. Alle Stationen abwaehlen -> Hinweistext statt Liste.
5. Sortierung nach E10, dann E10 im Zahnrad abwaehlen -> Sortierung springt automatisch auf Diesel (naechste verfuegbare Sorte), kein JS-Fehler.
6. Browser-Konsole durchgehend ohne Fehler.

## Abschluss
`BR run finish WETTER-0010 --status COMPLETED --actor claude-code --commit --summary "<HEAD-SHA, Browser-Verifikations-Befund>"`, `git push`.
Ausgabe NUR: Footer + max. 3 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Browser-Verifikation.
- [ ] Stationsliste filtert nach ausgewaehlten Stationen
- [ ] Preiszeilen filtern nach ausgewaehlten Sorten, Sortier-Umschalter blendet nicht ausgewaehlte Sorten aus
- [ ] Automatischer Sortier-Wechsel bei Abwahl der aktiven Sortier-Sorte funktioniert
- [ ] Leerzustaende (keine Stationen/keine Sorten ausgewaehlt) sauber abgefangen
- [ ] Browser-Verifikation bestanden (alle 6 Punkte)
- [ ] Scope eingehalten (nur js/tanken.js)
