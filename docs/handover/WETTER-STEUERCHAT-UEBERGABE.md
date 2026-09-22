# Uebergabe: Steuerchat Wetter-App (Stand 2026-09-22)

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
1. `.claude/commands/acb-auftrag.md` ist NUR fuer BRIDGE-IDs geschrieben (Beispiel BRIDGE-0047 fest im Skill). Fuer WETTER-Auftraege NIE den Slash-Befehl oder das Wort "Auftrag"/"acb-auftrag" in der ersten Anweisung an Claude Code nutzen - stattdessen woertlich auf die WP-Datei verweisen (siehe WETTER-0001 als Beispiel fuer den zweiten, erfolgreichen Versuch).
2. `result.yaml` kennt nur EIN Repository (repository/head). Der Zielrepo-Commit-SHA steht deshalb nur im freien `summary`-Text, nicht in einem eigenen Schema-Feld. Beim Pruefen also IMMER zusaetzlich zum ACB-Repo auch das Zielrepo frisch klonen und den im summary genannten SHA verifizieren.
3. Keine automatisierten Tests im Zielrepo (reine statische JS/HTML-Seite). Pruefung bislang: node --check auf geaenderte JS-Dateien + Diff-Review + (wenn moeglich) echter Blick auf die Live-Seite, da sie direkt aus main deployt.

## Letzter Auftrag: WETTER-0001 (Regen-Nowcast genauer)
- Teil A: precipitation_probability ergaenzt, RING_KM um 2-km-Ring erweitert. Zielrepo-Commit f3452963a5a119d7809edf8a68b56f7e950d3f9d, verifiziert (Diff nur js/api.js + js/regen.js, node --check OK, precipitation_probability ist echter Open-Meteo-Parameter).
- Teil B (DWD-Radar): nicht umgesetzt, RADOLAN ist binaer ohne bekannte CORS-Freigabe - nachvollziehbar recherchiert, kein Blocker.
- ACB-Repo-HEAD nach Abschluss: e0653a6d3ef9dcbacc350d8d6cc349a88aa6c486
- Offen bei Uebergabe: April muss noch die Live-Seite kurz pruefen und in der Web-UI Kopiert->Review, dann Archivieren klicken.

## Naechster moeglicher Auftrag
Noch keiner zugeschnitten. Ideen aus WETTER-0001-Zusammenfassung: keine offenen technischen Vorschlaege, da Teil B ergebnislos war.