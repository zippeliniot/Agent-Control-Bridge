# ACB - Uebergabe v18 (Stand 2026-10-08, Maschinenwechsel HAM11 -> DES11)

**Repo-HEAD bei Erstellung:** `c04654418e06a4f0200213015770cfcb5fe63553` (`c046544`) | **Tests:**
575/575 - unabhaengig frisch nachgelaufen im Steuerchat (nicht nur aus `result.yaml` uebernommen).

**Fuer den neuen Steuerchat:** `docs/ACB-STEUERCHAT-STANDARDSTART.md`,
`docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md`, `docs/concepts/ENTSCHEIDUNG-PUSH-MODELL.md`, diese
Datei. v17 nicht loeschen (Historie) - v17 war bei Erstellung bereits unvollstaendig/veraltet, siehe
§1 unten.

**Anlass dieser Version:** April schliesst HAM11 fuer ein paar Tage und wechselt auf DES11. Diese
Datei ist die Uebergabe-Grundlage dafuer (`CLAUDE.md`: "Vor jedem Wechsel muss alles auf GitHub
liegen"). Sie dokumentiert gleichzeitig BRIDGE-0090 und eine Korrektur zu v17.

## 1. Was sich seit v17 geaendert hat - und eine Korrektur an v17 selbst

**Befund zu v17:** Die Datei wurde ausserhalb des Scopes von BRIDGE-0090 durch Claude Code
miterstellt und committet (nicht in `allowed_changed_files`/`allowed_paths` der Staging-YAML, vom
Steuerchat per frischem Klon nach `run finish` entdeckt). Inhaltlich war sie bei Erstellung
korrekt, war aber bereits beim Commit stehender Stand - sie erwaehnt BRIDGE-0090 nicht und fuehrt
den `base_head`-Befund noch als unbehandelt, obwohl er inzwischen als Issue erfasst ist. **Diese
v18 ersetzt v17 als aktuellen Stand**, v17 bleibt als Historie liegen.

**BRIDGE-0090 (Steering-Continuity-V2 praezisiert + OpenIssue-Verfahren):** `COMPLETED`, HEAD-Kette
`535b8e0`..`b395f70`..`c046544`, Footer-Angabe durch Steuerchat per frischem Klon unabhaengig
verifiziert (HEAD, Testzahl, Teil-A/B-Inhalte, Issue-Status - alle bestaetigt).

- **Teil A** (`docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md`): drei Ergaenzungen
  umgesetzt - §2 um RAG-unabhaengigen Anlass erweitert (Prosa-Verlinkung zwischen
  `ENTSCHEIDUNG-*.md` skaliert auch ohne RAG nicht mehr), §6 von "pauschale Aufhebung" auf
  "teilweise Revision der Formalisierungsebene, Prosa-Ebene bleibt unberuehrt" praezisiert, §4 um
  expliziten Prosa-Erhalt-Satz ergaenzt. **Status weiterhin "ENTWURF - ENTSCHEIDUNG AUSSTEHEND" -
  keine Entscheidung getroffen, nur die Vorlage praezisiert.**
- **Teil B** (`docs/ACB-STEUERCHAT-ARBEITSWEISE.md` Abschnitt 4): neunstufiger `issue`-Ablauf
  ergaenzt (Registry abgleichen -> ... -> Abschluss auf GitHub verifizieren), inkl. Hinweis auf
  fehlendes `--commit`-Flag bei `bridge issue open/close`.
- **OpenIssue-Mechanismus erstmals real genutzt** (seit BRIDGE-0075 ungenutzt, siehe v16/v17):
  drei Eintraege unter `open-issues/agent-control-bridge/` angelegt, manuell committet/gepusht
  (kein `--commit`-Flag vorhanden).
  - `agent-control-bridge-ISSUE-0001` - **CLOSED** (BRIDGE-0090 Teil A, s. o.).
  - `agent-control-bridge-ISSUE-0002` - **OPEN**: konkrete Autorisierung von
    `GIT_COMMIT`/`GIT_PUSH` fuer BRIDGE-0088/0089 ueber den Projekt-Default (`push_mode: direct`)
    hinaus nicht gesondert nachgewiesen (Nachweisluecke, kein belegter Mechanismusfehler).
  - `agent-control-bridge-ISSUE-0003` - **OPEN**: `expected_head`/`base_head` vermischen drei
    Zeitpunkte (Auftragsbasis, realer Git-Parent der Auftragsanlage, Vergleichsbasis fuer
    `changed_files`), keine Durchsetzung gegen Live-HEAD in `cli.py` (nur Fallback-Wert); zusaetzlich
    fehlt `open-issues/` ein `kind` in `gitops.expected_git_files()` und `bridge issue open/close`
    ein `--commit`-Flag.

**`KONZEPT-PRUEFRUNDEN-INTEGRATION.md` entschieden (war v17 §6 Punkt 5, jetzt erledigt):** April hat
am 08.10. im Steuerchat zugestimmt - Verfahren uebernommen (jetzt in `ACB-STEUERCHAT-ARBEITSWEISE.md`
Abschnitt 4), drei Issues real angelegt (s. o., ein viertes Issue - Testzahl-Klaerung - entfiel, da
durch BRIDGE-0087 bereits erklaert). Das Konzeptdokument selbst (`KONZEPT-PRUEFRUNDEN-INTEGRATION_V3.md`)
liegt **nicht im Repo** - nur das daraus abgeleitete Verfahren in `ACB-STEUERCHAT-ARBEITSWEISE.md`.

**Neuer Entscheidungsvorschlag, noch nicht spezifiziert (April, 08.10., per Bild+Text im
Steuerchat):** Drei-Schichten-Modell fuer Steering Continuity (Decision-Log / Symbol-Datei-Graph /
Vektor-RAG-Archiv), adressiert explizit das Dorfschaft-Projekt (1000+ geplante Steuerchats).
Verhaeltnis zu bestehenden Dokumenten vom Steuerchat geprueft (`RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md`
deckt Archiv-Vorrang-Policy bereits ab; neu sind Symbol-/Datei-Graph und Flag-Routing nach Schicht).
**Haengt an der §6-Entscheidung unten** - nicht davon unabhaengig spezifizierbar. Dokument liegt
**nicht im Repo**, nur als Datei beim Steuerchat/April.

## 2. G-Status
Unveraendert zu v16/v17 (G0-G5, G6 weiterhin nicht konzipiert).

## 3. Strukturelle Befunde (kumulativ, unveraendert aus v17 §3)
(siehe v17 §3 - durch BRIDGE-0090 keine neuen strukturellen Befunde, nur die oben genannten
Issues als strukturierte Nachfolge der dort bereits dokumentierten Funde.)

## 4. Arbeitsweise
Unveraendert zu v16/v17 §4, zusaetzlich: **Scope-Abweichungen (Datei ausserhalb
`allowed_changed_files`/`allowed_paths` committet) zaehlen als eigener Verifikationspunkt** - beim
naechsten `run finish`-Review `result.yaml: changed_files` gegen die Staging-YAML abgleichen, nicht
nur gegen das Work-Package (Lehre aus v17/BRIDGE-0090, s. §1).

## 5. Nicht von selbst anfangen bei (geklaert, nicht erneut hinterfragen)
(unveraendert aus v16/v17 §5, zusaetzlich:)
- `KONZEPT-PRUEFRUNDEN-INTEGRATION`-Verfahren ist entschieden und uebernommen (s. §1) - nicht
  erneut zur Diskussion stellen, nur noch anwenden.
- BRIDGE-0073 Option B ist weiterhin **nicht** aufgehoben, auch nach BRIDGE-0090 nicht - die
  praezisierte V2-Vorlage ist noch nicht angenommen (siehe §6 Punkt 1 unten). Nicht so behandeln,
  als sei die Formalisierung bereits beschlossen.

## 6. Offene Punkte - in dieser Reihenfolge

1. **§6-Entscheidung zu `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` (Decision-Log-
   Formalisierung) - April im Steuerchat am 08.10. zweimal gefragt, noch keine Antwort.** Naechster
   Schritt laut vereinbarter Reihenfolge (BRIDGE-0090 -> diese Entscheidung -> Drei-Schichten-
   Spezifikation) - **vor jedem neuen BRIDGE-Auftrag zu klaeren**, nicht uebergehen.
2. **Drei-Schichten-Modell spezifizieren** (s. §1) - haengt an Punkt 1, noch nicht begonnen.
3. **Issue-0002** (GIT_COMMIT/GIT_PUSH-Autorisierungsnachweis BRIDGE-0088/0089) - offen, noch
   keinem Auftrag zugeordnet.
4. **Issue-0003** (`expected_head`/`base_head`-Dreiteilung + `--commit`-Flag fuer `bridge issue` +
   `open_issue`-`kind` in `gitops.expected_git_files()`) - offen, Code-Aenderung, noch keinem
   Auftrag zugeordnet.
5. (unveraendert aus v16/v17 §6 Punkt 6: Quellen-Manifest, Mehrprojekt-Parallelitaet,
   RAG-Status-Seite, generische Steuerchat-Vorlage/Dorfschaft-Einbindung/Draft-Modus.)

## 7. Referenz
v16 §7 (Checkpoint-Register-Datei bei April, dort Abschnitte 6-8) unveraendert gueltig.

## 8. Maschinenwechsel HAM11 -> DES11 (Anlass dieser Version)

- `handover-check.sh`/`.ps1` muss auf HAM11 vor dem Wechsel PASS liefern (siehe separate
  Kopiervorlage im Steuerchat) - prueft Branch, sauberer Working Tree, keine untracked Dateien,
  keine Stashes, lokal nicht ahead von `origin/main`, Pflichtdokumente versioniert.
- Dieser Steuerchat sieht nur den GitHub-Stand (frischer Klon), nicht HAM11s lokale Arbeitskopien
  (`board`, `dev`, `claude`, `projects\<id>`, `codex`, `rag-index`) - die Pruefung muss auf HAM11
  selbst laufen.
- Nach PASS: DES11 uebernimmt per `git pull` in seinen eigenen Klonen (gleiche Topologie seit
  19./20.09., siehe `docs/architecture/machines.md`).
