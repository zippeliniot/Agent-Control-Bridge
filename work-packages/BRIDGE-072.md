# BRIDGE-0072 - Alte Steuerchat-Dokumente bereinigen, Vorlagen-Skript auf Startprompt v2 umstellen

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0072 |
| project_id | agent-control-bridge |
| Typ / Klasse | DOCS |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - gezielte Textedits plus kleines Skript samt Test. |
| Modellwechsel zum Vorgaenger | NEIN |
| depends_on | BRIDGE-0071 (ARCHIVED) |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0072` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung = STOPP.

## Auftrag
**Ziel:** Seit b6d595e gibt es den generischen Startprompt `docs/ACB-STEUERCHAT-START-GENERISCH-v2.md` (einziges Feld `{{PROJEKT_ID}}`, alles andere liest der Chat aus dem Profil). Die alte Vorlage `docs/ACB-STEUERCHAT-VORLAGE.md` und das Skript `scripts/steuerchat-vorlage.py` (fuellt sie mit 6 Platzhaltern) sind damit ueberholt und enthalten veraltete Angaben. Bereinigen, ohne Historie zu veraendern.
**Scope (nur diese Pfade, sonst nichts):**
- entfernen (`git rm`): `docs/ACB-STEUERCHAT-VORLAGE.md`
- aendern: `scripts/steuerchat-vorlage.py`, `tests/test_steuerchat_vorlage.py`, `docs/ACB-STEUERCHAT-STANDARDSTART.md`, `docs/ACB-PROJEKT-INTEGRATION.md`, `docs/ACB-DOKUMENTENUEBERSICHT-v1.md`, `docs/ACB-NEUES-PROJEKT-ANLEITUNG-v1.md`, `docs/ACB-INTEGRATION-GENERISCH-v1.md`, `docs/ACB-STEUERCHAT-START-GENERISCH-v2.md`, `work-packages/BRIDGE-072.md`
- NICHT anfassen: `docs/handover/*`, alle anderen Dateien in `work-packages/`, `results/`, `tasks/`, `.claude/`, `src/`, `schemas/`. Historische Verweise auf die entfernte Vorlage bleiben als Historie stehen.
Dokumente in deutschem Klartext mit Umlauten (wie die Zieldateien), Edits einzeln per Einzelersetzung, nie Volltext neu schreiben.

### Teil A - Skript und Test auf Startprompt v2 umstellen, alte Vorlage entfernen
`scripts/steuerchat-vorlage.py` neu schreiben (ein Modul, `build(project_id, repo_root=...)` und `main()` beibehalten):
1. `--project-id` Pflichtargument. Profil `projects/<id>/project.yaml` lesen. Fehlt es: `ValueError` mit Text, der die vorhandenen Verzeichnisnamen unter `projects/` auflistet (Tippfehler-Hilfe).
2. Fail-closed pruefen: `project_id` im Profil muss dem Argument entsprechen; `task_prefix`, `github_repo`, `repository` muessen gesetzt sein; `github_repo` als `<org>/<repo>`. `executor` darf fehlen (lesende Projekte). Sonst `ValueError`, kein Raten.
3. `docs/ACB-STEUERCHAT-START-GENERISCH-v2.md` lesen, Zeilenenden `\r\n` zu `\n` normalisieren (Windows-Checkout), den Teil NACH der ersten Zeile `---` nehmen (Kopfbereich vor der Linie ist Meta-Text und nicht Teil der Ausgabe; fehlt die Linie: `ValueError`), `{{PROJEKT_ID}}` durch die ID ersetzen. Bleibt danach irgendwo `{{` stehen: `ValueError`.
4. Ausgabe auf stdout, kein Datei-Write, Fehler auf stderr mit Exit-Code 1. Der bisherige Executor-Hinweis-Mechanismus (`EXECUTOR_HINWEIS_*`) entfaellt ersatzlos; der Startprompt v2 enthaelt die Executor-Regeln selbst.
5. Modul-Docstring auf den neuen Zweck anpassen (Aufruf: `.venv/Scripts/python.exe scripts/steuerchat-vorlage.py --project-id <id>`).
`tests/test_steuerchat_vorlage.py` neu, stdlib unittest, temp-Repo-Root mit Kopie des echten v2-Startprompts und Fake-`project.yaml`: (a) fuellt die ID ein, kein `{{` im Ergebnis; (b) Ergebnis enthaelt nicht den Kopfbereich vor der `---`-Linie; (c) funktioniert mit `\r\n`-Zeilenenden der Vorlage; (d) unbekannte project-id -> Fehler, der eine vorhandene ID nennt; (e) fehlendes Pflichtfeld -> Fehler; (f) `project_id` im Profil weicht vom Argument ab -> Fehler; (g) Profil ohne `executor` ist zulaessig.
Danach `git rm docs/ACB-STEUERCHAT-VORLAGE.md`.
**Tests:** `python -m unittest tests.test_steuerchat_vorlage`.
- [x] Skript fuellt `{{PROJEKT_ID}}` in den v2-Startprompt, validiert die ID gegen die Profile
- [x] Tests (a)-(g) gruen
- [x] `docs/ACB-STEUERCHAT-VORLAGE.md` entfernt

### Teil B - STANDARDSTART als ACB-Kern-Startprompt korrigieren
In `docs/ACB-STEUERCHAT-STANDARDSTART.md` genau zwei Aenderungen:
1. Direkt unter der Titelzeile diese Zeile einfuegen (woertlich, Backticks sind Teil des Textes):
```
> **Geltungsbereich:** Startprompt des ACB-Kern-Steuerchats (Projekt `agent-control-bridge`). Für Fremdprojekte gilt `docs/ACB-STEUERCHAT-START-GENERISCH-v2.md`.
```
2. In Abschnitt 2 die nummerierte Pflichtliste (13 Punkte, beginnend mit `CCB-UEBERGABE-v<N>.md`) ersetzen durch die aktuell gueltige Pflichtliste: (1) `docs/handover/ACB-UEBERGABE-v<N>.md` mit hoechster Versionsnummer (`ls docs/handover/ | sort -V`), (2) `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md`, (3) `docs/concepts/ENTSCHEIDUNG-PUSH-MODELL.md`, (4) `.claude/commands/acb-auftrag.md`, (5) `docs/ACB-STEUERCHAT-ARBEITSWEISE.md`, (6) `docs/architecture/machines.md` (Maschinen-/Pfad-Register), (7) `CLAUDE.md`. Darunter neuer Absatz "Bei Bedarf (nicht Pflicht):" mit den bisherigen uebrigen Eintraegen (`docs/ACB-STEUERCHAT-REFERENZ.md`, `CODEX.md`, `CONTROL.md`, `docs/architecture/ARCHITECTURE.md`, `docs/security/SECURITY-MODEL.md`, `docs/PROJEKTKONZEPT.md`, `docs/ACB-PROJEKT-INTEGRATION.md`, `docs/ACB-ORCHESTRATOR-KONZEPT.md`, alle `projects/<id>/project.yaml`). Nichts sonst in der Datei aendern.
- [x] Geltungsbereich-Hinweis eingefuegt
- [x] Pflichtliste aktualisiert, `CCB-`-Name korrigiert, uebrige Eintraege unter "Bei Bedarf"

### Teil C - PROJEKT-INTEGRATION: Verweis auf die generische Anleitung
In `docs/ACB-PROJEKT-INTEGRATION.md` direkt unter der Titelzeile diese Zeile einfuegen (woertlich), sonst nichts aendern:
```
> Detailreferenz zu Profilfeldern und Durchsetzung. Den Ablauf (Einrichtung, Auftragsablauf, Vorlagen) beschreibt `docs/ACB-INTEGRATION-GENERISCH-v1.md`, die Übersicht `docs/ACB-DOKUMENTENUEBERSICHT-v1.md`.
```
- [x] Verweis eingefuegt

### Teil D - generische Dokumente konsistent machen
1. `docs/ACB-STEUERCHAT-START-GENERISCH-v2.md`: im Kopfbereich (vor der `---`-Linie) die Zeile `Verwendung: ...Einziges Feld: {{PROJEKT_ID}}.` um diesen Satz ergaenzen (woertlich); der Text ab der Linie bleibt unveraendert:
   ```
   Empfohlen: `scripts\steuerchat-vorlage.py --project-id <id>` gibt den Text ab der Linie fertig aus und prüft die ID gegen die Profile.
   ```
2. `docs/ACB-DOKUMENTENUEBERSICHT-v1.md`: (a) in der Tabelle in Zeile `ACB-STEUERCHAT-START-GENERISCH-v2.md`, Spalte "Wann / durch wen", den Satz, der mit "Einziges Feld:" beginnt, ersetzen durch `Fertig befüllt per scripts\steuerchat-vorlage.py --project-id <id> (prüft die ID gegen die Profile, kein manuelles Ersetzen).` (Backticks um den Skriptaufruf wie im umgebenden Text setzen); (b) den Absatz `**Nicht verwenden für neue Projekte:** ...` (bis Absatzende) ersetzen durch den Absatz `**Ältere Dokumente und ihr Geltungsbereich:**` mit vier Punkten: `ACB-STEUERCHAT-STANDARDSTART.md` = nur ACB-Kern-Steuerchat; `ACB-PROJEKT-INTEGRATION.md` = Detailreferenz zu Profilfeldern, Ablauf steht in der Integrationsdatei; `ACB-STEUERCHAT-VORLAGE.md` = entfernt (BRIDGE-0072); `scripts/steuerchat-vorlage.py` = füllt jetzt den Startprompt v2.
3. `docs/ACB-NEUES-PROJEKT-ANLEITUNG-v1.md`: Schritt 7, Spalte "Was": statt manuellem Einfügen mit Ersetzen von `{{PROJEKT_ID}}` den Ablauf: im ACB-Klon des Projekts den Befehl `.venv\Scripts\python.exe scripts\steuerchat-vorlage.py --project-id <id>` ausführen (der Steuerchat liefert ihn mit konkretem Wert), die komplette Ausgabe als Custom Instructions des neuen claude.ai-Projekts einfügen. Spalte "WO" auf `PowerShell, dann claude.ai` aendern.
4. `docs/ACB-INTEGRATION-GENERISCH-v1.md`: in Tabelle Abschnitt 2, Zeile 6, den Verweis auf den Startprompt um den Satz ergaenzen: Fertig befüllt per `scripts\steuerchat-vorlage.py --project-id <id>`.
- [x] Vier Dokumente konsistent angepasst

## Abschluss
1. Kontrolle: `git grep -n "ACB-STEUERCHAT-VORLAGE"` darf ausserhalb von `docs/handover/`, `work-packages/`, `results/`, `tasks/` und `docs/ACB-DOKUMENTENUEBERSICHT-v1.md` (dort nur als "entfernt") nichts liefern. Sonst STOPP mit Fundstellen.
2. Volle Suite EINMAL, nur die letzten 3 Zeilen zeigen.
3. `git status` sauber, dann Abschluss wie im Slash-Befehl.
- [ ] Kontrolle ohne verwaiste Verweise
- [ ] Volle Suite gruen
