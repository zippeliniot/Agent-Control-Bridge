# Uebergabe: Steuerchat Wetter-App (Stand 2026-09-26, nach WETTER-0013)

Fuer einen neuen Chat/eine neue Steuerchat-Session, die WETTER-Folgeauftraege
durchfuehren soll. Analog zu docs/handover/ACB-UEBERGABE-v12.md, aber fuer
das Profil projects/wetter-app/project.yaml. Der Wetter-Steuerchat
prueft/zuschneidet NUR Auftraege mit project_id wetter-app (Praefix WETTER),
ruehrt ACB-eigenen Quellcode nicht an und nutzt dieselbe Store-/Gate-
Maschinerie wie der ACB-Steuerchat.

## System-Umgebung (wichtig fuer einen neuen Chat, der die Ablaeufe versteht)

**Fuenf Beteiligte, drei physische Rechner:**

1. **Steuerchat (dieser Chat, browser-basiertes Claude, claude.ai)** - hat
   selbst KEINEN Push-Zugriff auf irgendein Repo. Rolle: Auftraege (WPs)
   pruefen/zuschneiden, als Markdown+YAML-Dateien formulieren, Diffs nach
   Abschluss unabhaengig gegenpruefen (eigener Sandbox-Klon, node --check /
   py_compile), Review-Verdikt geben, Archivierungs-/Deploy-Befehle als
   Text-Anweisungen ("WO: ...") an April durchreichen. Schreibt NIE selbst
   Code, gibt nur Copy-Paste-Bloecke.
2. **April** - fuehrt alle "WO:"-Anweisungen des Steuerchats tatsaechlich
   aus, an zwei verschiedenen Orten:
   a) **PowerShell (Windows, ACB-Repo-Klon)** - `E:\_DEV\Agent-Control-Bridge\projects\wetter-app`.
      Hier laufen: `git pull/add/commit/push` fuer WP-Dateien, sowie die
      ACB-CLI (`BR` = `.venv\Scripts\python.exe src\bridge\cli.py --root . --schema-dir .\schemas`)
      fuer `task copied`/`task archive` nach jedem Review.
   b) **PowerShell (Windows) mit Claude Code darin** - eigenes Fenster,
      arbeitet im SELBEN ACB-Repo-Klon (`E:\_DEV\Agent-Control-Bridge\projects\wetter-app`)
      als Executor: liest die WP-Datei, wechselt intern zum Zielrepo-Klon
      `E:\_DEV\Wetter-App`, aendert dort Code, committet/pusht, fuehrt
      `BR task create`/`run start`/`run finish` aus. WICHTIG: NIE den
      `/acb-auftrag`-Slash-Befehl oder das Wort "Auftrag" in der ersten
      Anweisung an Claude Code verwenden (der Skill ist nur fuer BRIDGE-IDs
      geschrieben, reagiert bei "Auftrag"/WETTER-IDs fehlerhaft - siehe
      Vorfall unten). Immer woertlich: "Lies work-packages/WETTER-0XX.md
      und befolge es wortgenau, Schritt fuer Schritt."
   c) Physischer Rechner wechselt je nach Wochentag (HAM11/HAM01 vs.
      DES11/DES01, siehe docs/architecture/machines.md) - JEDE Maschine hat
      ihre EIGENEN Klone, nichts wird automatisch synchronisiert ausser
      ueber GitHub push/pull. Nach einem Maschinenwechsel: auf der neuen
      Maschine beide Klone (ACB-Repo + Zielrepo) frisch pullen/klonen und
      HEAD gegenpruefen, bevor weitergearbeitet wird.
3. **pi5-01** (192.168.200.42, Debian, CLIMAC-Intelligenzschicht-Pi,
   SSH-Zugang `mp01@PI5-01`) - hat einen EIGENEN, separaten Klon des
   Zielrepos unter `/opt/climac/web/wetter-app` (WorkingDirectory aller
   systemd-Units). Muss nach jedem WP manuell per `git pull` aktualisiert
   werden (kein Auto-Pull). Dort laufen:
   - `pi-scripts/climac_sftp.py` - gemeinsame SFTP-Hilfsklasse, Zugangsdaten
     NIE hardcodiert, sondern aus SQLite `/opt/climac/data/climac.db`,
     Tabelle `credentials`, per `get_credential(cred_id)` (z. B.
     `sftp_ionos_wetter`, `tankerkoenig_api`).
   - `pi-scripts/deploy_web.py` - deployt das FRONTEND (`index.html`, `CNAME`,
     alle `js/*.js` aus der festen `WEB_FILES`-Liste) per SFTP zu IONOS.
     **Muss nach JEDEM WP, das Frontend-Dateien aendert, manuell ausgefuehrt
     werden** (`python3 deploy_web.py`, vorher `--dry-run` zur Kontrolle) -
     das ist KEIN automatischer Schritt. Achtung: neue `js/*.js`-Dateien
     muessen manuell in `WEB_FILES` ergaenzt werden, sonst 404 auf der
     Live-Seite (siehe WETTER-0008).
   - `pi-scripts/export_live.py`, `export_daily.py`, `export_history.py` -
     Sensordaten (Taschensee/Ostsee), automatisiert per systemd-Timer.
   - `pi-scripts/export_tanken_stations.py` (taeglich 00:10) und
     `export_tanken_prices.py` (alle 15 Min) - Tankstellenpreise
     (Tankerkoenig-API), seit WETTER-0005/0007/0011, ebenfalls automatisiert.
   - systemd-Units in `pi-scripts/systemd/`, Installation/Reinstallation via
     `sudo bash pi-scripts/systemd/install.sh` (idempotent, ergaenzt nur neue
     Units, ruehrt bestehende nicht an).
4. **IONOS-Webserver** (`home20261535.1and1-data.host`, SFTP-Pfad
   `/Gronenberg/Wetter_1`) - die eigentliche Live-Seite
   `wetter.gronenberg.info`. WICHTIG (fruehere Fehlannahme des Steuerchats
   korrigiert): das ist **NICHT GitHub Pages**. GitHub hat keinerlei
   direkten Zugriff auf diesen Webserver. Der einzige Weg, wie Code dort
   ankommt, ist der manuelle SFTP-Push via `deploy_web.py` von pi5-01 aus.
   Ein gepushter GitHub-main-Commit ist NICHT automatisch live, bis dieser
   Schritt gemacht wurde (mehrfach in dieser Session erlebt, u. a. WETTER-0002
   war laenger live veraltet, bis das aufgefallen ist).
5. **Sensor-Pi ha01** (192.168.200.99, HAOS) - separat, liefert Rohdaten an
   pi5-01, hat mit dem wetter-app-Deploy selbst nichts zu tun.

**Repos:**
- ACB-Koordination (Task/Result/Audit/WP): github.com/zippeliniot/Agent-Control-Bridge, Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (Windows) - NUR fuer Task/Result/Audit/WP-Dateien.
- Zielrepo (echter Code): github.com/zippeliniot/wetter-app, Branch main. Klone: `E:\_DEV\Wetter-App` (Windows, Claude Code arbeitet hier), `/opt/climac/web/wetter-app` (pi5-01, fuer Export-Skripte + Deploy).
- Profil: `projects/wetter-app/project.yaml` (Executor Claude Code, Controller human, task_prefix WETTER, allow_push true, allow_merge false, protected_branches [main]).

## Bekannte Struktur-Luecken / wiederkehrende Fallstricke
1. `.claude/commands/acb-auftrag.md` ist NUR fuer BRIDGE-IDs geschrieben. Fuer WETTER-Auftraege NIE den Slash-Befehl oder das Wort "Auftrag"/"acb-auftrag" verwenden - sonst reagiert Claude Code teils gar nicht (Datei nicht gefunden) oder driftet in einen falschen Kontext ab (siehe Vorfall: Claude Code arbeitete faelschlich am unabhaengigen "Dorfschaft"-Projekt/DORF-031 im selben ACB-Repo, weil der Auftrags-Skill anders getriggert wurde). IMMER woertlich auf die WP-Datei verweisen. **Vor jedem neuen WP `/clear` in Claude Code ausfuehren**, um Kontext-Vermischung zwischen Auftraegen zu vermeiden.
2. `result.yaml` kennt nur EIN Repository (das ACB-Repo). Der Zielrepo-Commit-SHA steht nur im freien `summary`-Text. Beim Pruefen IMMER zusaetzlich das Zielrepo frisch fetchen/pullen und den im summary genannten SHA per Diff verifizieren - nie nur dem Text vertrauen.
3. Keine automatisierten Tests im Zielrepo (reine statische JS/HTML/Python-Seite). Pruefverfahren: `node --check`/`python3 -m py_compile` auf geaenderte Dateien + vollstaendiger Diff-Review durch den Steuerchat + (wenn moeglich) echte Browser-Verifikation durch Claude Code selbst.
4. **CLI-Befehle `task copied`/`task archive` committen NICHT automatisch.** Nach jedem der beiden IMMER `git status` pruefen, dann `git add -A; git commit; git push` - sonst bleibt der neue Status nur lokal und geht bei einem Maschinenwechsel/Neustart verloren (mehrfach passiert, u. a. WETTER-0003, WETTER-0004, WETTER-0009).
5. Claude-in-Chrome-Erweiterung war ueber viele Auftraege hinweg (WETTER-0001 bis 0007) nicht zuverlaessig verbunden - echte Browser-Verifikation oft nicht moeglich, Ersatzverfahren (Node-Skript gegen echte APIs, reines Code-Review) wurden genutzt. Ab ca. WETTER-0007/0010 hat der Executor selbststaendig einen **Playwright/headless-Chromium-Fallback** gefunden, der zuverlaessig funktioniert, wenn die Erweiterung nicht verbunden ist - seitdem sind echte Browser-Verifikationen wieder moeglich, auch ohne die Erweiterung.
6. `deploy_web.py` hat eine FESTE `WEB_FILES`-Liste. Jede neue JS-Datei MUSS dort manuell ergaenzt werden, sonst 404 auf der Live-Seite nach dem naechsten Deploy trotz erfolgreichem GitHub-Push (siehe WETTER-0008, live production incident, per Sofort-Fix `--only` behoben und dauerhaft gepatcht).
7. Maschinenwechsel (z. B. HAM11 -> DES01): JEDE Maschine hat eigene, unabhaengige Klone. Nach Wechsel immer `git pull`/frisch klonen auf BEIDEN relevanten Klonen (ACB-Repo + Zielrepo) und HEAD gegenpruefen, bevor weitergearbeitet wird. `scripts/handover-check.ps1` im ACB-Repo prueft Working-Tree-Sauberkeit + Pflichtdokumente vor einer Uebergabe.
8. Ab und zu laeuft eine PowerShell-Sitzung faelschlich im falschen Verzeichnis (z. B. `E:\_dev\wetter-app` statt `E:\_DEV\Wetter-App`/`E:\_DEV\Agent-Control-Bridge\projects\wetter-app`) - bei "Datei nicht gefunden"-Meldungen immer zuerst `pwd`/`ls` pruefen lassen.

## Chronologie aller WETTER-Auftraege (alle Status: ARCHIVED, alle live deployt)
- **WETTER-0001** (vor dieser Session begonnen): Regen-Nowcast Basis - Niederschlagswahrscheinlichkeit + engerer Abtastring.
- **WETTER-0002**: Regenwahrscheinlichkeit sichtbar gemacht (veralteter Footnote-Text korrigiert, neue immer-sichtbare Wahrscheinlichkeits-Kachel) + Ostsee-Kopfzeile-Coldstart-Bug behoben.
- **WETTER-0003**: Aktuelle Werte (Temperatur+Niederschlag, Wind) in den jeweiligen Kartenkoepfen ergaenzt (`temp-current`/`wind-current`), analog Taschensee/Ostsee.
- **WETTER-0004**: Layout-Fix fuer WETTER-0003 (Flex-Wrapper, die neuen Werte waren faelschlich zentriert statt rechtsbuendig).
- **WETTER-0005**: Tankstellenpreise-Grundgeruest (Tankerkoenig-API) - Pi-seitige Export-Skripte (kein API-Key im Frontend, Architektur-Entscheid mit April abgestimmt), Frontend-Liste, Button bewusst noch NICHT aktiviert (Teil C zurueckgestellt bis Live-Verifikation).
- **WETTER-0006**: Bugfix - Tankerkoenig liefert `false` statt `null` bei nicht gefuehrten Sorten, verursachte Rendering-Crash (Live-Daten-Fund).
- **WETTER-0007**: Preisverlauf-Chart (3 Tage, Historie-Sammlung) + Zahnrad-Auswahl (Stationen/Sorten, pro Geraet via localStorage) + Auto-Refresh alle 5 Min.
- **WETTER-0008**: Bugfix - `deploy_web.py` `WEB_FILES` fehlte `js/tanken.js` dauerhaft (Live-404-Vorfall, per Sofort-Fix + WP behoben).
- **WETTER-0009**: Tanken-Button im Haupt-Header final aktiviert (nach Live-Verifikation von 0005-0008).
- **WETTER-0010**: Zahnrad-Auswahl filtert jetzt auch die Stationsliste selbst (vorher nur den Chart).
- **WETTER-0011**: Bugfix - fehlende Preise (Station in einem 15-Min-Zyklus nicht in der API-Antwort) wurden faelschlich mit `null` ueberschrieben statt letzten bekannten Wert zu behalten (Live-Daten-Fund, ~50% Ausfallrate bei 2 von 5 Stationen) + Chart-Y-Achse auf 3 Dezimalstellen + optische Auffrischung (Flaechenfuellung, punktdichte-abhaengige Marker).
- **WETTER-0012**: Tanken-Zahnrad-Panel responsiv gemacht - eigenes Overlay mit 3 echten Breakpoints (Mobil: Bottom-Sheet, Tablet: zentriertes Modal, Desktop: Dropdown mit max-width+Scroll), vorheriges Panel lief auf schmalen iPhones ueber den Bildschirmrand hinaus.
- **WETTER-0013**: Schmale-Screens-Layout - Header-Ueberlappung (Tanken-Button vs. 1-Tag/3-Tage-Umschalter) durch `flex-wrap` behoben + kleinerer Umschalter unter 420px + alle 4 Kartenkoepfe (Temperatur/Wind/Taschensee/Ostsee) brechen jetzt sauber linksbuendig um statt mittig zu springen.

## Aktueller Funktionsumfang (live auf wetter.gronenberg.info)
- Hauptansicht: Temperatur & Niederschlag, Wind, Taschensee, Ostsee - je mit aktuellen Werten im Kartenkopf, responsiv bei schmalen Screens.
- Regen-Nowcast (2h, Wahrscheinlichkeit immer sichtbar).
- Tankstellenpreise Umkreis Gronenberg (5 Stationen, 5 km Radius) - Liste mit Sortierung E5/E10/Diesel, Preisverlauf-Chart (3 Tage), Zahnrad-Auswahl (Stationen/Sorten, filtert Liste UND Chart, responsives Overlay), Auto-Refresh, Tankerkoenig-Attribution.
- Blitzsensor-Karte (Gronenberg), unveraendert seit vor dieser Session.

## Offene Punkte (noch kein WP zugeschnitten)
1. **Responsives Mehrspalten-Layout fuer Tablet/Desktop**: `#main-view` steht aktuell fest auf `.page { max-width: 760px; }`, eine Spalte, egal wie breit der Bildschirm ist. Vorschlag (mit April besprochen, aber noch nicht als WP umgesetzt): `#main-view { display:grid; grid-template-columns: repeat(auto-fit, minmax(340px,1fr)); }` + `.page` auf groesseren Screens verbreitern. Chart.js-Charts sind bereits `responsive:true, maintainAspectRatio:false` - sollten sich automatisch anpassen.
2. **"Manchmal regnet es bereits, App zeigt es nicht"** (April-Meldung vom 2026-09-23) - nie abschliessend geklaert, vermutlich Modell-/Aktualitaetsgrenze der ICON-D2/AROME-Vorhersage (kein Live-Abgleich mit Ist-Zustand vorhanden), kein bestaetigter Code-Fehler. Muesste live bei einem echten Regenereignis nachgeprueft werden.
3. Tankerkoenig-Stationsausfaelle (WETTER-0011-Fix ist ein Carry-Forward-Workaround, keine Ursachenklaerung) - falls die Warn-Logs in `export_tanken_prices.py` haeufig fuer dieselben Stationen auftauchen, lohnt sich eine naehere Untersuchung, ob das ein dauerhaftes Tankerkoenig-seitiges Problem bei genau diesen Stationen ist.
