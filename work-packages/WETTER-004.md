# WETTER-0004 - Layout-Fix: temp-current/wind-current in Flex-Wrapper analog Taschensee/Ostsee

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0004 |
| project_id | wetter-app |
| Typ / Klasse | BUGFIX |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0003 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0004 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss 3c08ac7db4de100b1d84d6355ccadc5d4289e6b0 sein (Stand nach WETTER-0003). Abweichung -> STOPP.
3. Scope NUR: `index.html` im Ziel-Repo. Keine JS-Datei. Im ACB-Repo NUR diese WP-Datei + Store-Dateien.

## Befund (Steuerchat, per Live-Screenshot bestaetigt)
`.chart-head` hat CSS `display:flex; justify-content:space-between` (index.html, CSS-Regel `.chart-head`, ca. Zeile 42). Bei `#sw-current` (Taschensee) und `#sea-current` (Ostsee) gibt es GENAU zwei Kind-Elemente in `.chart-head`: den `.card-title` und einen Wrapper-Div (bei Taschensee: `<div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">` der den aktuellen Wert UND die Legende buendelt). Bei `#temp-current`/`#wind-current` (WETTER-0003) wurden diese Spans stattdessen als DRITTES, eigenstaendiges Geschwister-Element zwischen Titel und Legende eingefuegt - `justify-content:space-between` verteilt bei 3 Kindern das mittlere Element in die Bildschirmmitte statt rechtsbuendig neben die Legende zu setzen. Sichtbar im Live-Screenshot: "GR 14.3° · 0 mm" und "12 km/h NW" erscheinen gross und zentriert statt klein und rechtsbuendig wie bei Taschensee/Ostsee.

## Fix (NUR index.html, zwei Stellen)
1. Bei `#temp-card`: `#temp-current` aus der direkten Kindposition von `.chart-head` herausnehmen und zusammen mit dem bestehenden `.chart-legend`-Div in einen neuen Wrapper packen, exakt nach dem Taschensee-Muster:
```html
   <div class="chart-head">
     <span class="card-title" onclick="window.openFS('temp')">Temperatur &amp; Niederschlag ↗</span>
     <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
       <span id="temp-current" style="font-size:1.05rem;font-weight:700;opacity:0.9;"></span>
       <div class="chart-legend">
         ... (bestehender Inhalt unveraendert) ...
       </div>
     </div>
   </div>
```
2. Bei `#wind-card`: identisches Muster fuer `#wind-current` + `.wind-thr`.
3. KEINE Aenderung an `js/main.js` noetig (die Update-Logik selbst ist korrekt, nur das HTML-Nesting war falsch) - falls doch ein JS-Bug auffaellt: STOPP, nicht selbst erweitern, im Bericht benennen.

## Pflicht: echte Browser-Verifikation (kein Ersatzverfahren mehr - 3. Mal in Folge fehlte das)
Chrome-Erweiterung sollte jetzt verbunden sein. `python -m http.server` im Ziel-Repo, Seite im Browser oeffnen (per Chrome-Tool, nicht nur Code-Review):
1. Screenshot/Visuelle Pruefung: `temp-current` UND `wind-current` erscheinen jetzt rechtsbuendig, klein, direkt ueber ihrer jeweiligen Legende - NICHT mehr zentriert/gross.
2. Vergleich mit Taschensee/Ostsee-Kopf: optisch gleiches Muster (Wert oben, Legende darunter, beides rechtsbuendig).
3. Browser-Konsole ohne Fehler.
Falls die Erweiterung wieder nicht verbunden ist: das explizit und deutlich im Abschluss-Bericht vermerken (nicht stillschweigend auf Code-Review ausweichen).

## Abschluss
`BR run finish WETTER-0004 --status COMPLETED --actor claude-code --commit --summary "<HEAD-SHA, Befund Browser-Verifikation: durchgefuehrt ja/nein>"`, `git push`.
Ausgabe NUR: Footer + max. 3 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Browser-Verifikations-Befund (durchgefuehrt oder nicht, mit Grund).
- [x] Fix umgesetzt (beide Kopfzeilen in Wrapper), nur index.html geaendert, committet und gepusht
- [ ] Echte Browser-Verifikation durchgefuehrt (nicht nur Code-Review) - Ergebnis dokumentiert - NICHT durchgefuehrt: Chrome-Erweiterung in dieser Session nicht verbunden (ToolSearch ohne Treffer fuer Browser-Tools), kein Ersatzverfahren angewendet wie von WP gefordert
- [x] Scope eingehalten (nur index.html)
