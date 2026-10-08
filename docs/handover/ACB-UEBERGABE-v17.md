# ACB - Uebergabe v17 (Stand 2026-10-08)

**Repo-HEAD bei Erstellung:** `b70ed66d989b7ed59e04815fb2daa36bf080a576` (`b70ed66`) | **Tests:**
575/575 gruen laut `results/BRIDGE-0089/RUN-01/result.yaml` - **nicht** in dieser Sitzung
unabhaengig frisch nachgelaufen (kein `pwsh`/volle venv in dieser Cloud-Sandbox verfuegbar fuer
einen reinen Dokumentationsabgleich; Regel aus `KONZEPT-PRUEFRUNDEN-INTEGRATION.md` §4 Punkt 5:
kein Suite-Lauf allein fuer eine Nachpruefung). **Der naechste Steuerchat muss die Suite laut
Standardstart §4 trotzdem frisch selbst laufen lassen, bevor er sich auf diese Zahl verlaesst.**

**Fuer den neuen Steuerchat:** `docs/ACB-STEUERCHAT-STANDARDSTART.md`,
`docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md`, `docs/concepts/ENTSCHEIDUNG-PUSH-MODELL.md`, diese
Datei. v16 nicht loeschen (Historie).

**Hinweis zu dieser Version:** v16 endete bei BRIDGE-0086 (RAG-Infrastruktur-Grundgeruest). v17
dokumentiert BRIDGE-0087 bis BRIDGE-0089 sowie eine noch **nicht entschiedene** Konzeptvorlage
(Pruefrunden-Integration via `OpenIssue`) und einen real belegten Integritaetsbefund, der bisher
in **keinem** Auftrag korrigiert wurde.

## 1. Was sich seit v16 geaendert hat

**BRIDGE-0087 (toter Whitelist-Eintrag `kind="claim"`):** umgesetzt, `ARCHIVED`. Loest den in v16
§6 Punkt 3 genannten offenen Punkt auf.

**BRIDGE-0088 (RAG-Retrieval-/Injection-Pipeline-Spezifikation + Entscheidungsvorlage V2):**
`ARCHIVED`. Zwei neue Dateien: `docs/concepts/RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md` (loest v16
§6 Punkt 4 - spezifiziert, **nicht implementiert**: `structured_coverage`, `migration_status`,
`archive_fallback_policy`, `context_sources_used`, Quellenprioritaet, Revisionsbindung,
Pflichtkontext, Blocker-Verhalten, Herkunftsnachweis; legt die Grundlage fuer v16 §6 Punkt 5,
`rag/sources.yaml`, aber als Policy-Text, kein Code) und
`docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` (Vorschlag zur **teilweisen**
Praezisierung von BRIDGE-0073s Decision-Verdikt - **keine Entscheidung**, Status weiterhin
"ENTWURF - ENTSCHEIDUNG AUSSTEHEND"). Erste Ausfuehrung dieses Auftrags enthielt noch die
unkorrigierte Entwurfsfassung (siehe BRIDGE-0089).

**BRIDGE-0089 (Nachbesserung BRIDGE-0088):** `ARCHIVED`. Korrigiert an den zwei o.g. Dateien:
`structured_coverage`/`migration_status`/`context_sources_used` von "Soll-Zustand" auf "Ist-
Zustand, kein fester Zielwert" umformuliert; Herkunftsnachweis verschaerft (Datei+Revision+
Fundstelle Pflicht, reiner Steuerchat-Verweis nicht ausreichend); V2 §3a/3b/3c praezisiert (vier
Ereignisse Annahme/Ablehnung/Widerruf/Abloesung statt zwei, teilweise Abloesung mit
Geltungsbereich, `origin_task_id` explizit optional, `affects`/`implemented_by`/`verified_by`
ausdruecklich nicht auf Code beschraenkt). V1 unangetastet, keine Entscheidung getroffen.

**Weiterhin offen in V2 (durch BRIDGE-0089 NICHT behoben, da nicht im Scope):**
- §2 nennt ausschliesslich einen RAG-bezogenen Anlass, keinen RAG-unabhaengigen (Steuerkontinuitaet
  allgemein).
- §6 formuliert eine **pauschale Aufhebung** von BRIDGE-0073s Option B ("aufgehoben und ersetzt"),
  nicht die inzwischen praezisere Formulierung "Ergaenzung/teilweise Revision: Prosa bleibt,
  Metadaten/Gueltigkeitsereignisse werden formalisiert".
- Kein expliziter Satz, dass menschliche Prosa (Entscheidung + Begruendung) erhalten bleibt - nur
  implizit aus §1/§3 ableitbar.
- `superseded_by` ist bewusst nur als **nicht gespeicherte, abgeleitete Ansicht** spezifiziert
  (§3a) - eine gespeicherte, rekonstruierbare Projektion waere enger/anders und ist nicht
  entschieden.

**Realer, belegter Integritaetsbefund zu BRIDGE-0089 (neu, durch keinen Auftrag korrigiert):**
`tasks/BRIDGE-0089/task.yaml: git.expected_head` und daraus `results/BRIDGE-0089/RUN-01/
result.yaml: base_head` tragen beide `815ec26c55a9bd8c67f08f8bf2335362dd844ea6`. Der tatsaechliche
Git-Parent des Commits "BRIDGE-0089: task create" (`b0496d138abac6f9dfc6a8847ce08fbef6e0e47e`) ist
aber nachweislich `c01c5b4137996b5e7a9baa3f3878ea3884aa5d97` (`git log -1 --format="%H %P"
b0496d138abac6f9dfc6a8847ce08fbef6e0e47e`). Die historische Provenienz-Angabe ist damit falsch,
nicht nur veraltet. **Nicht stillschweigend korrigiert** (waere Aenderung an einem abgeschlossenen
Auftrag) - als Befund hier dokumentiert, Behandlung siehe §6 Punkt 2 unten.

**Zusaetzlich real geprueft (bisher nicht dokumentiert gewesen):** `push_mode` ist ein
Projekt-Feld (`schemas/project.schema.yaml:141-148`, Default `direct`), **nicht** ein Task-Feld.
`docs/concepts/ENTSCHEIDUNG-PUSH-MODELL.md` (BRIDGE-0043/0047, FREIGEGEBEN, "G2: IN KRAFT
2026-09-20"): Projekte ohne gesetztes `push_mode`-Feld bleiben explizit auf `direct` - kein
stiller Wechsel. `projects/agent-control-bridge/project.yaml` setzt dieses Feld nicht -> `direct`
ist fuer BRIDGE-0088/0089 der ausdruecklich geregelte, nicht nur zufaellig funktionierende Modus.
**Was damit weiterhin NICHT belegt ist:** eine ueber den Projekt-Default hinausgehende,
auftragsspezifische Freigabe fuer `GIT_COMMIT`/`GIT_PUSH` bei genau diesen beiden Auftraegen -
bleibt offen (siehe §6 Punkt 3).

**`expected_head` ist im echten CLI kein harter Vorab-Abgleich gegen den Live-HEAD**
(`src/bridge/cli.py:472,1099`) - nur ein Fallback-Wert fuer `base_head`, falls `--base-head` beim
Aufruf fehlt. Ein veralteter/falscher Wert in der Staging-Datei fuehrt **nicht** automatisch zu
`HEAD_MISMATCH`. Die eigentliche Absicherung laeuft (falls ueberhaupt) ueber den
`/acb-auftrag`-Ablauf selbst (git pull + manueller Vergleich), nicht ueber dieses Feld.

**Konzeptvorlage `KONZEPT-PRUEFRUNDEN-INTEGRATION.md` (ENTWURF, nicht entschieden, nicht im
Repo):** schlaegt vor, wiederkehrende externe Pruefrunden-Befunde (wie die beiden obigen) ab jetzt
als `OpenIssue`-Eintraege (BRIDGE-0075, `schemas/open-issue.schema.yaml`) zu fuehren statt nur im
Chatverlauf. Realer Befund dabei: `open-issues/`-Verzeichnis existiert im Repo **nicht** - der
Mechanismus wurde seit seiner Freigabe (02.10.2026) noch kein einziges Mal benutzt. Vier konkrete
Issue-Entwuerfe liegen vor (V2-Inhalt gesammelt, Testzahl-Klaerung, Git-Autorisierung-Nachweis,
`expected_head`/`base_head`-Befund) - keiner davon real angelegt.

## 2. G-Status
Unveraendert zu v16 (G0-G5, G6 weiterhin nicht konzipiert).

## 3. Strukturelle Befunde (kumulativ, durch v17 ergaenzt)
- (unveraendert aus v16 §3.)
- **Neu:** `push_mode` ist Projekt-, nicht Task-Feld; Projekte ohne das Feld bleiben laut
  `ENTSCHEIDUNG-PUSH-MODELL.md` explizit auf `direct` - vor jeder Aussage zu Push-Rechten dieses
  Dokument pruefen, nicht aus der Ausfuehrung selbst auf Zulaessigkeit schliessen.
- **Neu:** `git.expected_head` in `task.yaml` ist nur ein `base_head`-Fallback, kein
  durchgesetzter Gate-Check - bei jeder Aussage zu "HEAD_MISMATCH waere aufgefallen" diesen
  Unterschied explizit machen, nicht annehmen.
- **Neu:** `open-issues/` ist bisher ungenutzte Infrastruktur (Schema+CLI vollstaendig vorhanden
  seit BRIDGE-0075, aber null Instanzen im Repo) - vor jeder Aussage "es gibt/gibt keine offenen
  Punkte zu X" den Store real pruefen (`bridge issue list`), nicht aus Chat-Erinnerung behaupten.

## 4. Arbeitsweise
Unveraendert zu v16 §4, zusaetzlich: **jede Einstufung eines Pruefrundenbefunds
(ERLEDIGT/OFFEN/NICHT NACHGEWIESEN) braucht eine Fundstelle (Datei+Zeile oder Commit-SHA) - keine
Einschaetzung ohne Beleg** (aus der Pruefrunde zu BRIDGE-0089 gelernt, die vier vorherige
"ERLEDIGT"-Einstufungen korrigieren musste).

## 5. Nicht von selbst anfangen bei (geklaert, nicht erneut hinterfragen)
(unveraendert aus v16 §5, zusaetzlich:)
- BRIDGE-0073 Option B ist **nicht aufgehoben** - V2 ist weiterhin nur Vorschlag, nicht
  Entscheidung. Nicht so behandeln, als sei die Formalisierung bereits beschlossen.
- `push_mode: direct` fuer dieses Projekt ist der real geregelte Default (siehe §1) - nicht erneut
  als ungeklaerte Frage aufwerfen, ohne `ENTSCHEIDUNG-PUSH-MODELL.md` zu zitieren.

## 6. Offene Punkte - in dieser Reihenfolge

1. **V2 inhaltlich weiter praezisieren** (vier Punkte aus §1 oben: RAG-unabhaengiger Anlass,
   §6-Formulierung, expliziter Prosa-Erhalt-Satz, Speicherungsfrage `superseded_by`) - noch nicht
   als Auftrag spezifiziert.
2. **`base_head`-Provenienz-Fehler in BRIDGE-0089** real beheben oder als bewusst stehenbleibender
   historischer Fehler dokumentieren (keine stillschweigende Korrektur) - Entscheidung steht aus.
3. **Konkrete Auftragsautorisierung fuer `GIT_COMMIT`/`GIT_PUSH`** bei BRIDGE-0088/0089 ueber den
   Projekt-Default hinaus nachweisen oder als Nachweisluecke dokumentieren.
4. **`expected_head` als harten Pruefpunkt vor `run start` durchsetzen** (oder bewusst als
   Fallback-only-Feld belassen) - bisher nur beschrieben, nicht entschieden.
5. **`KONZEPT-PRUEFRUNDEN-INTEGRATION.md` entscheiden:** Verfahren uebernehmen, vier Issue-
   Entwuerfe real per `bridge issue open` anlegen, Abschnitt in
   `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` uebernehmen - oder verwerfen.
6. (unveraendert aus v16 §6, Punkte 5-8: Quellen-Manifest, Mehrprojekt-Parallelitaet, RAG-Status-
   Seite, generische Steuerchat-Vorlage/`OpenIssue`-Referenz/Dorfschaft-Einbindung/Draft-Modus.)

## 7. Referenz
v16 §7 (Checkpoint-Register-Datei bei April, Abschnitte 6-8 weiterhin offen) unveraendert gueltig.
