# KONZEPT: Externe Pruefrunden in den ACB-Auftragsfluss integrieren (V3)

**Status: ENTWURF - ZUR ENTSCHEIDUNG.** Kein Auftrag, keine Schema-Aenderung, keine
Repo-Schreibaktion. Fassung V3 nach Korrektur durch die Pruefrunde vom 08.10.2026 zu V2
(externer Pruefbericht, vom Steuerchat gegen frischen Klon HEAD `b70ed66` nachgeprueft -
alle unten verwendeten Befunde des Berichts sind bestaetigt, nicht nur uebernommen).

## 0. Registry-Abgleich (Pflichtschritt vor jedem Issue-Vorschlag)

`store.issues_dir = <root>/open-issues` (`src/bridge/store.py:154`), CLI: `bridge issue
open/close/list` (`src/bridge/cli.py:254-269`, Implementierung `:1221-1252`). Geprueft: Verzeichnis
`open-issues/` existiert im Repo (Stand HEAD `b70ed66`) **nicht** - es wurden bisher ueberhaupt
keine `OpenIssue`-Eintraege angelegt, seit BRIDGE-0075 den Mechanismus freigegeben hat. Kein
Duplikatsrisiko, da keine bestehenden Eintraege zu pruefen sind. Das ist selbst ein Befund: der
seit 02.10.2026 freigegebene Mechanismus wurde bislang nicht ein einziges Mal benutzt.

## 1. Mechanismus (unveraendert zu V1/V2, Begruendung gestrafft)

`OpenIssue` (BRIDGE-0075, `schemas/open-issue.schema.yaml`) wird fuer jeden eigenstaendigen,
offenen Pruefrunden-Befund genutzt statt nur im Chat gehalten. Felder real bestaetigt:
`issue_id`/`project_id`/`status [OPEN|CLOSED]`/`summary`/`origin_task_id`/`created_at` (Pflicht),
`closed_at`/`closed_by`/`note` (optional, `null` solange offen). Anlegen: `bridge issue open
--project-id <id> --summary "..." --origin-task-id <id> --actor <name>`. Schliessen: `bridge issue
close <issue_id> --project-id <id> --actor <name> --note "..."`. Datei:
`open-issues/<project_id>/<issue_id>.yaml`.

## 2. Verfahrensregeln (neu in V3 - in V2 nur behauptet, nicht ausformuliert)

V2 Abschnitt 2 Punkt 5 verwies auf "Abschnitt 4 Punkt 3" fuer den Verzicht auf einen Suite-Lauf -
dieser Abschnitt enthielt tatsaechlich nur die Issue-Tabelle, keine Verfahrensregeln (Befund der
Pruefrunde, am Dokument nachvollzogen). Hiermit nachgeholt, als eigener Abschnitt:

1. **Registry abgleichen** (Abschnitt 0) - vor jedem neuen Issue-Vorschlag `bridge issue list
   --project-id <id> --include-closed` pruefen, kein Duplikat anlegen.
2. **Befund mit Quelle pruefen** - jede Zustandsbehauptung ueber das Repo braucht Datei+Zeile oder
   Commit-SHA aus einem frischen Klon, keine Uebernahme aus einer Uebergabedatei oder einem
   aelteren Chatverlauf ungeprueft.
3. **Issue erfassen** - `bridge issue open`, `summary` kurz und konkret, `origin_task_id` der
   Auftrag, aus dem der Befund stammt (nicht zwingend der Auftrag, der ihn beheben wird).
4. **Kein Suite-Lauf allein fuer eine Issue-Anlage** - das Anlegen eines `OpenIssue`-Eintrags ist
   eine reine Store-Aktion, keine Code-Aenderung; ein Testlauf traegt dazu nichts bei.
5. **Auf GitHub sichern** - `bridge issue open/close` committen **nicht automatisch** (kein
   `--commit`-Flag vorhanden, geprueft in `src/bridge/cli.py:254-269`; die Whitelist in
   `gitops.expected_git_files()` kennt zudem noch keinen `kind` fuer `open-issues/`, geprueft in
   `src/bridge/gitops.py:84-126`). Bis diese Luecke geschlossen ist (siehe Issue 3 unten), legt der
   Steuerchat die Issue-Befehle vor, **Claude Code fuehrt sie aus und committet/pusht manuell**
   (`git add open-issues/<project_id>/ && git commit && git push`) - sonst bleibt der Befund nur
   lokal und ist beim naechsten Steuerchat/Rechnerwechsel nicht sichtbar.
6. **Folgeauftrag verknuepfen** - ein Work-Package, das ein Issue bearbeitet, nennt die
   `issue_id` explizit im Anlass-Abschnitt; das Issue bleibt bis zum Abschluss `OPEN`.
7. **Ergebnis pruefen** - wie jede andere Behauptung ueber den Repo-Zustand: frischer Klon, Befund
   gegen echten Code/Doku-Stand verifizieren, nicht gegen den Footer des Laufs.
8. **Issue mit konkretem Nachweis schliessen** - `note` beim Schliessen benennt, welches
   Akzeptanzkriterium wie geprueft wurde (Datei+Zeile oder Kommando-Ausgabe), nicht nur eine SHA.
9. **Abschluss auf GitHub verifizieren** - nach dem Schliessen erneut frischer Klon, `bridge issue
   list --include-closed` zeigt `CLOSED` mit Nachweis-`note`.

## 3. Aenderungen aus der Pruefrunde vom 08.10., eingearbeitet

1. **Testzahl-Issue entfaellt.** Commit `46b2a81` (BRIDGE-0087 Teil B) entfernte
   `test_claim_exact_path_only` bewusst (toter `kind="claim"`-Zweig, BRIDGE-0079-Entscheidung).
   `work-packages/BRIDGE-088.md` erklaert die Differenz 576 -> 575 bereits ausdruecklich. Kein
   eigenstaendiger offener Punkt - **aus der Issue-Liste gestrichen** (war Issue 2 in V2).
2. **`superseded_by`-Speicherfrage ist in V2 bereits spezifiziert, nicht offen.**
   `docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` §3a sagt ausdruecklich:
   "`superseded_by` existiert nur in einer daraus berechneten, nicht gespeicherten Ansicht." Die
   Formulierung "Speicherungsfrage nicht entschieden" in der urspruenglichen Issue-1-Fassung war
   falsch - **korrigiert** (siehe Issue 1 unten: nur noch drei echte Luecken, nicht vier).
3. **`base_head`-Befund praezisiert statt zugespitzt.** Siehe Abschnitt 4 unten - Auftragsbasis
   (Kopf zum Konzeptionszeitpunkt), tatsaechlicher Git-Parent der Auftragsanlage und Vergleichsbasis
   fuer `changed_files` sind drei verschiedene Dinge, die das Konzept bisher nicht benennt.
4. **Git-Autorisierung als Nachweisluecke, nicht Mechanismusfehler.** Beide Task-Dateien
   (`tasks/BRIDGE-0088/task.yaml`, `tasks/BRIDGE-0089/task.yaml`) und die zugehoerigen
   Work-Packages tragen `GIT_COMMIT`/`GIT_PUSH` explizit im Berechtigungsprofil. Offen ist allein
   der gesonderte Nachweis der konkreten menschlichen Freigabe (`CLAUDE.md`: Bestaetigung im
   Claude-Code-Fenster **ist** die Freigabe) - ein fehlender gesonderter Nachweis belegt keine
   unautorisierte Aktion.
5. **Dauerhafte Sicherung fehlte im Ablauf** - siehe Abschnitt 2 Punkt 5 oben, jetzt Teil des
   Verfahrens statt nur erwaehnt.
6. **Einbindung in Folgeauftraege war nicht geregelt** - siehe Abschnitt 2 Punkte 3/6/8/9 oben.

## 4. Neuer, belegter Befund: `base_head`/`expected_head` bei BRIDGE-0089 - drei zu trennende Dinge

Realer Git-Parent des Commits "BRIDGE-0089: task create" (`b0496d13...`):

```
git log -1 --format="%H %P" b0496d138abac6f9dfc6a8847ce08fbef6e0e47e
b0496d138abac6f9dfc6a8847ce08fbef6e0e47e c01c5b4137996b5e7a9baa3f3878ea3884aa5d97
```

Tatsaechlicher Elternkommit der Auftragsanlage ist `c01c5b4...` (BRIDGE-0088 archive).
`tasks/BRIDGE-0089/task.yaml: git.expected_head` und daraus abgeleitet
`results/BRIDGE-0089/RUN-01/result.yaml: base_head` tragen beide `815ec26...` (BRIDGE-0088
run_finish, zeitlich **vor** dessen copied/archive-Aktionen).

`work-packages/BRIDGE-089.md`, Abschnitt "Anlass", nennt `815ec26` jedoch ausdruecklich als den
Kopf **zum Konzeptionszeitpunkt** des Auftrags (vor den copied/archive-Schritten) - das ist also
keine stillschweigende Falschangabe, sondern ein Beleg dafuer, dass drei unterschiedliche
Zeitpunkte bisher denselben Feldnamen teilen:

- **Auftragsbasis** - der Stand, auf dem die fachliche Korrektur inhaltlich aufsetzt (hier: `815ec26`).
- **tatsaechlicher Git-Parent der Auftragsanlage** - der reale HEAD beim `task create`-Commit (hier: `c01c5b4`).
- **Vergleichsbasis fuer `changed_files`** - das, wogegen `run finish --base-head` tatsaechlich
  diffed (aktuell identisch mit `expected_head`, s. `src/bridge/cli.py:467-472` und `:1093-1099` -
  reiner Fallback-Wert, keine Pruefung gegen den Live-HEAD, in keinem der beiden Code-Pfade).

Keine stillschweigende Korrektur der historischen Dateien - das waere seinerseits eine
unautorisierte Aenderung an einem abgeschlossenen Auftrag. Der Befund wird stattdessen als Issue
erfasst (Abschnitt 5, Issue 3 unten).

## 5. Vorgeschlagene Issues (Entwuerfe, nicht angelegt) - drei statt vier (Testzahl-Issue entfaellt)

| # | Kategorie | summary | origin_task_id |
|---|---|---|---|
| 1 | Dokumentation | V2 der Steering-Continuity-Nachtragsentscheidung inhaltlich unvollstaendig: RAG-unabhaengiger Anlass (§2) fehlt, §6 formuliert pauschale Aufhebung von BRIDGE-0073 statt Ergaenzung/teilweise Revision, kein expliziter Satz zum Erhalt der bisherigen Prosa-Entscheidungen | BRIDGE-0089 |
| 2 | Integritaet (Nachweisluecke, nicht Mechanismusfehler) | Konkrete Autorisierung von GIT_COMMIT/GIT_PUSH fuer BRIDGE-0088/0089 nicht gesondert nachgewiesen - nur Schema-Default `push_mode: direct` belegt die Policy, kein auftragsspezifischer Freigabenachweis dokumentiert | BRIDGE-0089 |
| 3 | Integritaet | `expected_head`/`base_head` vermischen bisher drei getrennte Zeitpunkte (Auftragsbasis, realer Git-Parent der Auftragsanlage, Vergleichsbasis fuer `changed_files`) - keine harte Durchsetzung gegen Live-HEAD in `cli.py:467-472`/`:1093-1099`; zusaetzlich fehlt `open-issues/` ein `kind` in `gitops.expected_git_files()` und ein `--commit`-Flag auf `bridge issue open/close`, ohne das Registry-Eintraege nur lokal bleiben | BRIDGE-0089 |

Keines dieser drei Issues wird hier angelegt - das waere eine Store-Schreibaktion (`bridge issue
open`), die dieser Steuerchat nicht ohne Freigabe ausfuehrt. Freigabe liegt vor (April, 08.10.2026,
diese Sitzung) - Ausfuehrung durch Claude Code, siehe beiliegende kopierfertige Befehle.

## 6. Nicht Teil dieses Konzepts

Keine Aussage zu BRIDGE-0073 Option B selbst. Keine Aenderung an `CLAUDE.md`. Keine feste Zahl von
Folgeauftraegen - Issue 1 waere ein inhaltlicher Nachbesserungsauftrag an
`ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md`, Issues 2+3 koennten in einem gemeinsamen
Integritaets-Auftrag behandelt werden (beide betreffen Governance/Nachweisbarkeit rund um
BRIDGE-0088/0089 und die `open-issues/`-Infrastruktur selbst).

## 7. Entscheidung

April hat am 08.10.2026 im Steuerchat zugestimmt: (a) Verfahren (Abschnitt 1+2) wird uebernommen,
(b) die drei Issues aus Abschnitt 5 werden real per `bridge issue open` angelegt, (c) Abschnitt 2
dieses Dokuments wird in `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` Abschnitt 4 uebernommen (eigener
Auftrag, siehe Work-Package BRIDGE-0090).
