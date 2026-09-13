# BRIDGE-030 — Web-UI: Maschinen-Spalte überall, sortierbare Übersicht, Projekt-Dropdown

| Feld | Wert |
|------|------|
| bridge_task_id | BRIDGE-0030 |
| project_id | codex-control-bridge |
| task_class | FEATURE |
| depends_on | (keine) |
| permission | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| executor | claude-code |
| review_roles | lead: anthropic, support: openai (aus Projektprofil übernommen) |
| Modell/Denkstufe | Claude Code, Denkstufe MEDIUM — reine Web-UI-/Darstellungs-Erweiterung, ein kleiner, sauber abgegrenzter Backend-Zusatz (roher Zeitstempel für Sortierung), kein Eingriff in Schema oder Zustandsmodell. |

> **Verbindlich für diesen und jeden CCB-Auftrag:**
> - Jede Zustandsänderung läuft über die Bridge-CLI, kein direktes Bearbeiten
>   von Store-Dateien.
> - `GIT_PUSH` steht im Profil — nach `run finish` **muss** gepusht werden,
>   idealerweise über `--commit` (BRIDGE-025), und **sofort**, nicht gesammelt.

## Kontext

Fachlicher Wunsch aus dem Steuerchat (nicht Teil der ursprünglichen
Orchestrator-Roadmap, daher vor das Review-Unternummern-Schema
eingeschoben — das rückt auf `BRIDGE-0031`). Drei Teile, unabhängig
voneinander umsetzbar, aber in einem Auftrag gebündelt, da alle drei
`src/bridge/webui.py` betreffen und typischerweise gemeinsam getestet
werden.

**Vor der Spezifikation gegen den echten Code geprüft**
(`src/bridge/webui.py` + `src/bridge/cli.py`, Verifikationspflicht Nr. 3):

1. **Maschinen-Spalte in Board + „Offene Aufträge außerhalb des Boards“**
   fehlt aktuell. In „Alle Projekte – Gesamtübersicht“ ist sie **bereits**
   vorhanden (`r.machine`, gespeist aus `_overview_task_info()`). Die
   Datenermittlung (Heartbeat des letzten Laufs > letzter Audit-Eintrag >
   `"?"`) existiert schon als wiederverwendbare Logik
   (`_overview_audit_scan()` einmalig + `_overview_task_info()` pro
   Auftrag) — **keine neue Datenquelle nötig**, nur Durchreichen zu
   `_board_rows()` und in die „other“-Liste von `board_payload()`.
2. `_board_rows()` gibt aktuell ein 7er-Tupel zurück
   (`task_id, projekt, fuehrung, richtung, wait, note, prio`), das u. a.
   in `_board_text()` (CLI-Textausgabe `bridge board`) **positionell**
   entpackt wird
   (`for i, (task_id, projekt, fuehrung, richtung, wait, note, prio) in
   enumerate(rows, ...)`). Wird `machine` ins Tupel aufgenommen, **muss**
   `_board_text()` entsprechend angepasst werden, sonst bricht die
   CLI-Ausgabe (`ValueError: too many values to unpack`). Design-
   Entscheidung: `machine` wird im Tupel ergänzt, aber in der
   **Terminal**-Ausgabe (`_board_text()`) bewusst **nicht** als eigene
   Spalte gedruckt (Terminal-Board bleibt kompakt, Maschine gibt es dort
   schon separat über `bridge overview`) — nur korrekt entpacken, nicht
   crashen.
3. `board_payload()`s „other“-Liste (Aufträge außerhalb des Boards) wird
   manuell als Dict gebaut, ganz ohne Maschinen-Feld — dieselbe
   Ermittlungslogik wie oben muss dort zusätzlich eingebaut werden.
4. **Sortierbare Spaltenüberschriften**: aktuell nirgends vorhanden
   (kein `onclick`/Sortierlogik auf `<th>`). Du hast das auf „Alle
   Projekte“ bezogen (`ov-table`) — nur diese Tabelle wird sortierbar,
   Board/Other bleiben wie bisher serverseitig sortiert (Priorität/
   Zustand), ohne Klick-Sortierung.
5. **Wichtiger Fund, der die Umsetzung beeinflusst:** Die Spalte
   „Aktiv vor“ liefert im JSON (`overview_payload()`) nur einen bereits
   **formatierten Text** (`last_act_str`, z. B. „vor 5 Min“/„vor 2 Std“).
   Der rohe, sortierbare Zeitstempel (`sort_ts` in `_overview_rows()`)
   wird serverseitig als reine Sortier-Hilfsspalte verwendet und **vor
   der Rückgabe verworfen** (`return [r[:8] for r in rows_raw]`). Eine
   Sortierung dieser Spalte rein auf Basis des Anzeigetexts wäre
   **inhaltlich falsch** (alphabetisch statt chronologisch — „vor 2 Std“
   käme vor „vor 5 Min“). `overview_payload()` muss deshalb ein
   zusätzliches, rohes Feld liefern (z. B. `last_activity_ts`: Unix-
   Epoch-Sekunden oder `null`), das für die Sortierung verwendet wird,
   der bestehende Anzeigetext (`last_activity`) bleibt unverändert für
   die Darstellung.
6. **Filter-Dropdown**: `rowMatches()`/`filterRows()` (JS) arbeiten
   durchgängig mit **Teilstring**-Vergleich (`indexOf(...) < 0`), nicht
   exaktem Abgleich — ein `<select>` liefert einen exakten Wert, der
   trivial ein Teilstring seiner selbst ist, bricht also nichts.
   `updateStatusList()` liefert bereits das Muster für „Werte aus den
   aktuell geladenen Zeilen ableiten, nicht aus einer festen Liste“ —
   genau dieses Muster für Projekt übernehmen (`updateProjektList()`
   analog), **nicht** die 7 `project_id`-Werte aus den `project.yaml`-
   Dateien hart hinterlegen (sonst zwei Quellen der Wahrheit, die
   auseinanderlaufen können).
7. **Bewusst NICHT verändert:** Status bleibt Freitext-Input +
   `<datalist>` (kein `<select>`) — das erlaubt aktuell nützliches
   Teilstring-Filtern wie `WAITING`, das alle `WAITING_FOR_*`-Zustände
   gleichzeitig zeigt. Ein starres `<select>` würde genau diese
   Funktionalität kaputt machen. Auftrag (Auftrags-ID) bleibt ebenfalls
   Freitext ohne Dropdown/Datalist — zu viele, wachsende Werte, kein
   klarer Nutzen.

## Von Claude Code umzusetzen

1. Auftrag anlegen und starten:
   ```
   bridge task create tasks/incoming/BRIDGE-0030.yaml
   bridge run start BRIDGE-0030 --actor claude-code
   ```

2. **Maschine in `_board_rows()` + `board_payload()`-„other“**
   (`src/bridge/cli.py` + `src/bridge/webui.py`):
   - `_board_rows()`-Tupel um `machine` ergänzen (Ermittlung wie in
     `_overview_task_info()`, `_overview_audit_scan()` **einmal** pro
     Aufruf, nicht pro Zeile — bestehendes Effizienz-Muster einhalten).
   - `_BOARD_FIELDS` in `webui.py` entsprechend erweitern.
   - `board_payload()`s „other“-Liste um dasselbe `machine`-Feld
     ergänzen (gleiche Ermittlungslogik, gleicher Audit-Scan
     wiederverwenden statt zweimal zu scannen).
   - `_board_text()` (`cli.py`) an das neue Tupel anpassen (korrektes
     Entpacken), **keine** neue Terminal-Spalte drucken (siehe Kontext
     Punkt 2).
   - Web-UI: `<th>Maschine</th>` in beiden oberen Tabellen (`#board`,
     `#other`) ergänzen, JS-Renderfunktionen (`renderTables()`) um die
     Zelle erweitern.

3. **`last_activity_ts` in `overview_payload()`** (`src/bridge/cli.py`
   `_overview_rows()` + `webui.py` `overview_payload()`): rohen
   Zeitstempel (Unix-Epoch, `null` falls kein `last_act`) zusätzlich zum
   bestehenden `last_activity`-Anzeigetext ausliefern — bestehendes
   Rückgabeformat sonst unverändert (rückwärtskompatibel).

4. **Sortierbare Spaltenüberschriften in `#ov-table`** (Web-UI,
   `src/bridge/webui.py`, nur JS/Frontend):
   - Jede Spalte außer `#` bekommt einen klickbaren `<th>` mit
     Sortierindikator (`▲`/`▼`) bei aktivem Sort.
   - Klick auf einen Spaltenkopf: 1. Klick → aufsteigend, 2. Klick auf
     dieselbe Spalte → absteigend, 3. Klick → zurück zur
     Standard-Sortierung (serverseitig: aktiv/inaktiv-Gruppe +
     Priorität + Zeit, wie bisher).
   - Sortierschlüssel pro Spalte: `Prio` → Rang (`HIGH`/`MEDIUM`/`LOW`
     clientseitig gemappt, analog zu `_PRIORITY_RANK` in `cli.py`),
     `Aktiv vor` → das neue `last_activity_ts`-Feld (Punkt 3, **nicht**
     der Anzeigetext), alle anderen Spalten (`Projekt`, `Auftrag`,
     `Status`, `Maschine`, `Führung/Prüfung`) → alphabetisch auf dem
     jeweiligen Textfeld.
   - Solange ein expliziter Spalten-Sort aktiv ist: die „— inaktiv /
     unterbrochen —“-Trennzeile (`ov-sep`) **ausblenden** — sie gehört
     zur Standard-Gruppierung und ergibt bei beliebiger Spaltensortierung
     keinen Sinn mehr. Bei Rückkehr zur Standard-Sortierung (3. Klick)
     wieder einblenden.
   - Bestehende Filter (`filterState`) bleiben unabhängig vom Spalten-
     Sort weiterhin wirksam (Filtern vor Sortieren anwenden).

5. **Projekt-Filter als `<select>`** (Web-UI):
   - `#f-projekt` von `<input>` zu `<select>` ändern, erste Option
     `<option value="">(alle)</option>` als expliziter „kein Filter“-
     Wert (wichtig für den bestehenden „Filter zurücksetzen“-Button,
     der `.value = ""` setzt).
   - Neue Funktion `updateProjektList()` analog `updateStatusList()`:
     Projekt-Werte aus `lastData.board`, `lastData.other`,
     `lastOverviewData` ableiten (`seen`-Muster übernehmen), alphabetisch
     sortiert als `<option>`-Elemente befüllen — **keine** feste Liste
     aus den `project.yaml`-Dateien hinterlegen.
   - Event-Listener: `<select>` löst zuverlässig sowohl `input`- als
     auch `change`-Events aus — bestehenden Listener wiederverwenden
     (`input`), **zusätzlich** `change` abonnieren (Absicherung, falls
     ein Browser bei `<select>` kein `input`-Event feuert).

6. Tests (`tests/test_cli.py`, `tests/test_webui.py`, neue Fälle):
   - `_board_rows()` liefert `machine` korrekt (Heartbeat > Audit >
     `"?"`, gleiche Fälle wie die bestehenden Overview-Tests).
   - `_board_text()` crasht nicht, druckt weiterhin keine
     Maschinen-Spalte (bewusste Design-Entscheidung, expliziter Test).
   - `board_payload()`-„other“ enthält `machine` pro Zeile.
   - Web-UI-HTML enthält `<th>Maschine</th>` in `#board` und `#other`.
   - `overview_payload()` liefert `last_activity_ts` als Zahl oder
     `null`, bestehendes `last_activity` unverändert.
   - HTML enthält `<select id="f-projekt">` (kein `<input>` mehr) mit
     leerer „(alle)“-Option.
   - Bestehende Tests (alle Module) weiterhin grün.
   - **Hinweis:** clientseitige Sortier-/Klick-Logik in reinem
     JS/HTML lässt sich mit den bestehenden Testmustern aus
     `WebUiFrontendTests` (String-Prüfung auf HTML/JS-Quelltext, siehe
     z. B. `test_filter_state_kept_in_js_variable`) abdecken — kein
     Headless-Browser im Projekt vorhanden, das ist konsistent mit dem
     bisherigen Testansatz für Frontend-Code in diesem Modul.

7. `docs/CCB-STEUERCHAT-REFERENZ.md` Teil 4 (Web-UI-Referenz) um die
   drei Änderungen ergänzen (Maschine in Board/Other, sortierbare
   Gesamtübersicht, Projekt-Dropdown).

8. Pflicht-Footer + Abschluss, `--commit` nutzen, **sofort pushen**:
   ```
   bridge run finish BRIDGE-0030 --status COMPLETED --actor claude-code \
     --commit \
     --summary "Maschinen-Spalte jetzt auch in Board und 'Offene Auftraege ausserhalb des Boards' (bestehende Ermittlungslogik aus der Gesamtuebersicht wiederverwendet, _board_text() Terminal-Ausgabe bewusst ohne neue Spalte). overview_payload() liefert zusaetzlich rohen Zeitstempel 'last_activity_ts' fuer korrekte chronologische Sortierung. Spaltenkoepfe der Gesamtuebersicht-Tabelle klickbar sortierbar (3-Stufen: auf/ab/Standard), Trennzeile aktiv/inaktiv nur bei Standard-Sortierung sichtbar. Projekt-Filter von Freitext zu <select> mit dynamisch aus geladenen Daten abgeleiteten Werten (kein hartkodierter Projekt-Katalog). Status- und Auftrag-Filter bewusst unveraendert (Teilstring-Suche bleibt nuetzlich bzw. Wertemenge zu gross)."
   git push
   ```
   `Auftrag: BRIDGE-0030 / Lauf: RUN-01 / Status: COMPLETED`

## Akzeptanzkriterien

- [ ] `_board_rows()` liefert `machine` pro Zeile (gleiche Ermittlungslogik
      wie Gesamtübersicht, kein doppelter Audit-Scan).
- [ ] `_board_text()` (CLI, `bridge board`) crasht nicht, druckt weiterhin
      keine Maschinen-Spalte.
- [ ] Web-UI „Board – wartet auf Weitergabe/Kopie“ und „Offene Aufträge
      außerhalb des Boards“ zeigen je eine Maschinen-Spalte.
- [ ] `overview_payload()` liefert zusätzliches `last_activity_ts`-Feld
      (Zahl/`null`), bestehendes `last_activity` unverändert.
- [ ] Spaltenköpfe der Tabelle „Alle Projekte – Gesamtübersicht“ (außer
      `#`) klickbar, 3-Stufen-Sortierung (auf/ab/Standard).
- [ ] „Aktiv vor“ sortiert chronologisch über `last_activity_ts`, nicht
      alphabetisch über den Anzeigetext.
- [ ] Inaktiv/aktiv-Trennzeile nur bei Standard-Sortierung sichtbar, bei
      explizitem Spalten-Sort ausgeblendet.
- [ ] Bestehende Filter bleiben bei aktivem Spalten-Sort wirksam.
- [ ] `#f-projekt` ist ein `<select>` mit „(alle)“-Option, Werte dynamisch
      aus geladenen Daten abgeleitet, kein hartkodierter Projekt-Katalog.
- [ ] Status- und Auftrag-Filter unverändert (weiterhin Freitext/
      Teilstring).
- [ ] `CCB-STEUERCHAT-REFERENZ.md` Teil 4 aktualisiert.
- [ ] Bestehende Tests weiterhin grün, neue Tests grün, frischer Klon
      verifiziert.
- [ ] Jeder Commit sofort gepusht, nicht gesammelt.
