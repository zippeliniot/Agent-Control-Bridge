# WETTER-0011 - Bugfix: fehlende Preise nicht mit null ueberschreiben + Chart-Y-Achse/Optik

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0011 |
| project_id | wetter-app |
| Typ / Klasse | BUGFIX |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0010 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.
> **HINWEIS:** Kein SSH-Zugriff auf pi5-01 in dieser Session - NICHT versuchen. Aktivierung/Verifikation mit echten Daten macht der Steuerchat anschliessend manuell.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0011 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss 1fc89b21526746982fff7c1874cef90b91f02180 sein. Abweichung -> STOPP.
3. Scope NUR: `pi-scripts/export_tanken_prices.py`, `js/tanken.js`.

## Befund (Steuerchat, per Live-Daten auf pi5-01 bestaetigt)
Live-Historie (`data/tanken_history.json`, 69 Punkte) zeigt: zwei von fuenf Stationen (Ulf Koberstein, Shell Scharbeutz Pönitzer Chaussee 1) haben bei 32 bzw. 36 von 69 Punkten `null` bei ALLEN drei Sorten gleichzeitig - obwohl beide Stationen laut aktueller Liste (Screenshot) valide Preise fuehren. Ursache in `export_tanken_prices.py` `main()`: `p = prices_by_id.get(st["id"], {})` - liefert Tankerkoenigs `prices.php` fuer eine Station in einem 15-Min-Zyklus KEINE Daten zurueck (leeres Dict, Station fehlt komplett in der API-Antwort), wird das kommentarlos als `null`/`isOpen=false` in `tanken.json` UND `tanken_history.json` geschrieben - der vorherige, echte Preis geht verloren, bis der naechste Zyklus wieder Daten liefert. Das fuehrt zum sichtbaren Chart-Loch UND zum Flackern der Live-Liste. Zusaetzlich: Chart-Y-Achse formatiert nur auf 2 Nachkommastellen (`toFixed(2)`), bei der engen Preisspanne (wenige Cent) erzeugt das doppelte/verwirrende Achsenbeschriftungen (z. B. zweimal "2.40 €" untereinander).

## Teil A - Fehlende Preise nicht ueberschreiben (NUR pi-scripts/export_tanken_prices.py)
1. In `main()`: VOR dem Aufbau von `full_stations`, den aktuell live stehenden `data/tanken.json`-Stand per `sftp.download_file(REMOTE_NAME, <temp-lokal-pfad>)` herunterladen (gleiches Muster wie in `_append_history()` fuer die History-Datei) und daraus `old_prices: dict[str, dict]` bauen (Station-ID -> {diesel, e5, e10, isOpen}). Schlaegt Download fehl oder Datei existiert noch nicht (erster Lauf ueberhaupt): `old_prices = {}`, dann bleibt das Verhalten wie bisher (kein Rueckfall moeglich).
2. Fuer jede Station: `p = prices_by_id.get(st["id"])` (OHNE Default `{}` - `None` muss unterscheidbar sein von "Station vorhanden aber Sorte fehlt"). Ist `p is None` (Station komplett nicht in der API-Antwort dieses Zyklus): Preise UND `isOpen` aus `old_prices.get(st["id"], {})` uebernehmen (Fallback), UND `log.warning(...)` mit Stations-ID + Namen, damit das sichtbar bleibt, falls es zum Dauerzustand wird. Ist `p` vorhanden, aber eine einzelne Sorte fehlt/ist `false` (Station bietet diese Sorte generell nicht - siehe WETTER-0006): unveraendert `null` lassen, NICHT aus `old_prices` nachziehen (das ist ein legitimer, dauerhafter Zustand, kein API-Ausfall).
3. Bestehende Logik (Chunking, `_num_or_none`, History-Anhaengen) sonst unveraendert lassen.

## Teil B - Chart-Y-Achse + Optik (NUR js/tanken.js, in getFSConfig())
1. Y-Achsen-`ticks.callback`: von `toFixed(2)` auf `toFixed(3)` aendern (Kraftstoffpreise haben immer 3 Nachkommastellen, behebt die doppelten Achsenbeschriftungen direkt).
2. Optische Auffrischung (deine Vorgabe "interessanter gestalten"), moderate Aenderungen:
   - Jede Linie erhaelt eine dezente Flaechenfuellung in der eigenen Linienfarbe mit niedriger Deckkraft (`backgroundColor` statt `'transparent'`, z. B. gleiche Farbe wie `borderColor` mit ca. 12% Deckkraft, `fill: 'origin'` oder `fill: true`), statt reiner Linien.
   - Punktmarker (`pointRadius`) abhaengig vom gewaehlten Zeitraum: bei 3 Tagen (viele Punkte, sonst ueberladen) `pointRadius: 0` (nur `pointHoverRadius` behalten), bei 1 Tag `pointRadius: 2` wie bisher.
   - Sonst keine strukturellen Aenderungen (Legende, Tooltip, x-Achse unveraendert).

## Pflicht: echte Browser-Verifikation
`python -m http.server` im Ziel-Repo. Lokale Test-`data/tanken_history.json` mit eng beieinanderliegenden Preisen (z. B. 2.395/2.399/2.401) anlegen, NICHT committen. Pruefe per Chrome-Tool:
1. Y-Achse zeigt jetzt 3 Nachkommastellen, keine doppelten/verwirrenden Labels mehr.
2. Linien haben sichtbare, aber dezente Flaechenfuellung.
3. Wechsel 1 Tag/3 Tage: Punktmarker bei 3 Tagen ausgeblendet, bei 1 Tag sichtbar.
4. Browser-Konsole ohne Fehler.
Fuer Teil A (Server-Logik) ist ein lokaler Python-Test ohne echten API-Call nicht sinnvoll moeglich - `python3 -m py_compile pi-scripts/export_tanken_prices.py` reicht als Syntaxpruefung; die echte Verifikation (faellt der Fallback wirklich greift) macht der Steuerchat anschliessend live auf pi5-01.

## Abschluss
`BR run finish WETTER-0011 --status COMPLETED --actor claude-code --commit --summary "<HEAD-SHA, Teil-A/B-Befund, Browser-Verifikations-Befund>"`, `git push`.
Ausgabe NUR: Footer + max. 4 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Teil-A/B-Befund, Browser-Verifikation.
- [x] Teil A: Fallback auf letzten bekannten Preis bei fehlender Station in prices.php-Antwort, Warn-Log, legitime Sorten-Luecken (false/None bei vorhandener Station) bleiben unangetastet
- [x] Teil B: Y-Achse 3 Nachkommastellen, dezente Flaechenfuellung, punktabhaengige Marker-Groesse
- [x] Browser-Verifikation bestanden
- [x] Scope eingehalten (nur die 2 genannten Dateien)
