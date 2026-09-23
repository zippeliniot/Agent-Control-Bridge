# Uebergabe: Steuerchat Wetter-App (Stand 2026-09-23)

Analog zu docs/handover/ACB-UEBERGABE-v12.md, aber fuer das Profil
projects/wetter-app/project.yaml. Der Wetter-Steuerchat prueft/zuschneidet
NUR Auftraege mit project_id wetter-app (Praefix WETTER), ruehrt ACB-eigenen
Quellcode nicht an und nutzt dieselbe Store-/Gate-Maschinerie wie der
ACB-Steuerchat.

## Repos
- ACB-Koordination (Task/Result/Audit/WP): github.com/zippeliniot/Agent-Control-Bridge, Klon E:\_DEV\Agent-Control-Bridge\projects\wetter-app
- Zielrepo (echter Code): github.com/zippeliniot/wetter-app, Klon E:\_DEV\Wetter-App, Branch main, live unter wetter.gronenberg.info (GitHub Pages, deployt direkt aus main)
- Profil: projects/wetter-app/project.yaml (Executor Claude Code, Controller human, task_prefix WETTER, allow_push true, allow_merge false, protected_branches [main])

## Bekannte Struktur-Luecken (nicht meine Aufgabe, sondern fuer April/ACB-Steuerchat)
1. `.claude/commands/acb-auftrag.md` ist NUR fuer BRIDGE-IDs geschrieben (Beispiel BRIDGE-0047 fest im Skill). Fuer WETTER-Auftraege NIE den Slash-Befehl oder das Wort "Auftrag"/"acb-auftrag" in der ersten Anweisung an Claude Code nutzen - stattdessen woertlich auf die WP-Datei verweisen (siehe WETTER-0001/WETTER-0002 als Beispiele).
2. `result.yaml` kennt nur EIN Repository (repository/head). Der Zielrepo-Commit-SHA steht deshalb nur im freien `summary`-Text, nicht in einem eigenen Schema-Feld. Beim Pruefen also IMMER zusaetzlich zum ACB-Repo auch das Zielrepo frisch klonen und den im summary genannten SHA verifizieren.
3. Keine automatisierten Tests im Zielrepo (reine statische JS/HTML-Seite). Pruefung bislang: node --check auf geaenderte JS-Dateien + Diff-Review + (wenn moeglich) echter Blick auf die Live-Seite, da sie direkt aus main deployt.
4. NEU seit WETTER-0002: Die Claude-in-Chrome-Erweiterung war in der Executor-Session (HAM11) wiederholt (WETTER-0001 UND WETTER-0002) nicht verbunden - echte Browser-Pruefung der Live-Seite war beide Male nicht moeglich. Ersatzverfahren bisher: Node-Skript gegen die echte Open-Meteo-API (WETTER-0002 Teil A) bzw. reines Code-Review (WETTER-0002 Teil B). Funktioniert als Notbehelf, ist aber kein vollwertiger Browser-Test - falls das oefter vorkommt, gehoert die Ursache selbst untersucht (eigener kleiner Auftrag).

## Letzter Auftrag: WETTER-0002 (Bugfix-Buendel: Regenwahrscheinlichkeit-Anzeige + Ostsee-Kopfzeile)
- Teil A: Veralteten Footnote-Text ("keine Regenwahrscheinlichkeit %") korrigiert + neue, immer sichtbare Stat-Kachel `regen-prob-main` (Maximum von `precipitation_probability` ueber die 2h-Timeline), auch bei "Kein Regen". Bestehende bedingte Wahrscheinlichkeits-Texte in heroFeel/regen-peak-sub unveraendert.
- Teil B: `updateSeaHeader()` fehlte im Erstlade-Pfad von `loadAll()` (kein Cache vorhanden) - Kopfzeile "Ostsee · Scharbeutz" blieb bis zu 10 Min leer. Aufruf direkt nach `initCharts()` ergaenzt (marineCache ist zu dem Zeitpunkt bereits gesetzt, Reihenfolge im Review bestaetigt).
- Zielrepo-Commit 4831a8e5bcfaf599a577261395fa6240da0b1691, verifiziert (Diff nur index.html + js/main.js + js/regen.js, 12 Zeilen, node --check OK, marineCache-Reihenfolge per Code-Review bestaetigt).
- ACB-Repo-HEAD nach Abschluss: af99ca424aa4b73350ec4e91fec5377293663256
- Status: ARCHIVED. Kopiert->Review->Archiviert erledigt. Live-Browser-Pruefung NICHT moeglich (siehe Struktur-Luecke 4), Ersatzverfahren wie oben.

## Naechster moeglicher Auftrag
Noch keiner zugeschnitten. Offene Punkte aus dem Review:
1. Chrome-Erweiterung fuer Browser-Pruefung wiederholt nicht verbunden (siehe Struktur-Luecke 4) - Ursache klaeren, falls das Muster anhaelt.
2. "Manchmal regnet es bereits, App zeigt es nicht" (April-Meldung vom 2026-09-23) - noch nicht abschliessend geklaert, vermutlich Modell-/Aktualitaetsgrenze der ICON-D2/AROME-Vorhersage, kein bestaetigter Code-Fehler. Muesste live bei tatsaechlichem Regenereignis nachgeprueft werden, bevor daraus ein Auftrag wird.
