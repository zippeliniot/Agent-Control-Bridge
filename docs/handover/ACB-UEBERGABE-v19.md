# ACB - Uebergabe v19 (Stand 2026-10-09)

**Repo-HEAD bei Erstellung:** `454050b9b7501cdcdef5393b1fa55ec2f3f257ee` (`454050b`) | **Tests:**
577/577 - unabhaengig frisch nachgelaufen im Steuerchat (575 Bestand + 2 neue Tests aus
BRIDGE-0092).

**Fuer den neuen Steuerchat:** `docs/ACB-STEUERCHAT-STANDARDSTART.md`, diese Datei. v18 nicht
loeschen (Historie).

**Anlass dieser Version:** Fortsetzung derselben Steuerchat-Sitzung wie v18 (kein
Maschinenwechsel) - diese Version dokumentiert, was seit v18 passiert ist, weil v18 bereits
veraltet war, als die Sitzung weiterlief (Lehre aus Abschnitt 2 unten).

## 1. Ein Prozessfehler dieser Sitzung - und die Korrektur

**Befund:** Zu Sitzungsbeginn wurde `docs/concepts/KONZEPT-PRUEFRUNDEN-INTEGRATION_V2.md`
(ein hochgeladenes Dokument, Stand-Vermerk HEAD `b70ed66`) ungeprueft umgesetzt - vier Issues
angelegt, obwohl der Repo-Stand durch BRIDGE-0090 bereits weitergelaufen war. Drei der vier
Issues waren bereits vorhanden (`ISSUE-0001` CLOSED, `-0002`/`-0003` OPEN). Der Fehler wurde
vor dem Push bemerkt, der Commit zurueckgesetzt, nur der eine echte neue Befund angelegt.

**Korrektur, verbindlich:** `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` Abschnitt 5 Punkt 7 (neu) -
Konzept-/Entscheidungsdokumente sind Momentaufnahmen, nie Live-Zustand. Vor jeder Umsetzung
eines Vorschlags daraus: erneut `git log`/`fetch` gegen den echten `HEAD` **und** `bridge
issue list --include-closed` pruefen, unabhaengig davon, was das Dokument selbst ueber seinen
eigenen Pruefstand behauptet.

**Nachtrag selbst betroffen:** Die drei zum Sitzungsende hochgeladenen Dokumente
(`KONZEPT-PRUEFRUNDEN-INTEGRATION_V3.md`, `ENTSCHEIDUNG-DREI-SCHICHTEN-STEERING-CONTINUITY.md`,
`issue-open-befehle.md`) waren seit 08.10. nie ins Repo uebernommen worden - v18 hatte das
bereits als Luecke benannt ("liegt nicht im Repo"), aber `handover-check.ps1/.sh` prueft nur
Repo-Sauberkeit, nicht ob Chat-Anhaenge uebernommen wurden. Die ersten zwei sind jetzt im
Repo (`docs/concepts/`), das dritte (reine Copy-Paste-Befehle) ist durch BRIDGE-0092 obsolet.

## 2. Was seit v18 fertig ist

- **ISSUE-0004** (Testzahl 576 vs. 575): angelegt und sofort wieder **CLOSED** - war durch
  BRIDGE-0087 bereits erklaert (`test_claim_exact_path_only` entfernt), v18 §1 hatte das
  schon vermerkt, bei Anlage uebersehen.
- **ISSUE-0002** (GIT_COMMIT/GIT_PUSH-Autorisierungsnachweis): **CLOSED**. Nachweis lag
  bereits vor - `permissions`-Default ist `[READ_ONLY]` (`task.schema.yaml:128`),
  `tasks/BRIDGE-0088|0089/task.yaml` setzen GIT_COMMIT/GIT_PUSH **explizit**, nicht per
  Default, dokumentiert in den jeweiligen Work-Packages und `audit.jsonl` (`TASK_CREATED`).
- **BRIDGE-0092** (Teilbefund aus ISSUE-0003): `--commit`-Flag fuer `bridge issue
  open/close` ergaenzt (`gitops.expected_git_files()` kennt jetzt `kind=issue_open/
  issue_close`, Praefix-Match auf `open-issues/<project_id>/`). 577/577 gruen (2 neue Tests).
  **ISSUE-0003 bleibt OPEN** - der zweite Teilbefund (drei vermischte Zeitpunkte bei
  `expected_head`/`base_head`, keine Live-HEAD-Durchsetzung in `cli.py:472`/`:1099`) ist
  bewusst **nicht** mitgezogen - riskanterer Eingriff in zentrale Git-Logik, eigener Auftrag.
- **ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md §6 entschieden** (neuer §7): April hat der
  Formalisierungsebene aus §3 **teilweise** zugestimmt (append-only Ereignisse, `supersedes`,
  `affects`/`implemented_by`/`verified_by`) - BRIDGE-0073s Prosa-Begruendung bleibt unberuehrt,
  Folgefragen aus §5 (`decision.schema.yaml`, `task.schema.yaml`-Erweiterung) bleiben eigene,
  noch nicht entschiedene Auftraege. Kein Code/Schema geaendert.
- **BRIDGE-0093**: Mehrprojekt-RAG spezifiziert (`docs/concepts/MEHRPROJEKT-RAG-
  SPEZIFIKATION.md`) - ein Repo/Klon (`rag-index`, unveraendert), Unterordner pro
  `project_id` darin. Kein Code-/Schema-Bedarf jetzt (`rag_index_clone_path()`/
  `rag_index_sync()` bereits projekt-unabhaengig korrekt, kein Indexer-Code existiert).
  Loest die Vorbedingung aus `ENTSCHEIDUNG-DREI-SCHICHTEN-STEERING-CONTINUITY.md` §3.
- **BRIDGE-0094**: Drei-Schichten-Architektur spezifiziert (`docs/concepts/DREI-SCHICHTEN-
  ARCHITEKTUR-SPEZIFIKATION.md`) - Decision-Log/Symbol-Datei-Graph/Vektor-RAG-Archiv benannt,
  Flag-Routing-Reihenfolge + Context-Assembler mit Rueckfluss skizziert, Symbol-/Datei-Graph
  gegen echten Dorfschaft-Stack (PHP 8.x/MariaDB/natives JS/PowerShell) spezifiziert -
  Tree-sitter als Kandidat, Spike vor Festlegung. Governance/Schema bleiben eigene Auftraege.

## 3. G-Status

Unveraendert zu v16/v17/v18 (G0-G5, G6 weiterhin nicht konzipiert).

## 4. Offene Punkte - in dieser Reihenfolge

1. **ISSUE-0003, zweiter Teilbefund** (`expected_head`/`base_head` vermischen drei
   Zeitpunkte, keine Live-HEAD-Durchsetzung) - offen, Code-Aenderung in `cli.py`, bewusst
   nicht mit BRIDGE-0092 mitgezogen, noch keinem Auftrag zugeordnet.
2. **Technischer Spike** (BRIDGE-0094 Abschnitt 5): Tree-sitter-Grammatik-Abdeckung fuer
   PHP/JavaScript/PowerShell real pruefen, bevor der Symbol-Graph-Indexer beauftragt wird -
   Voraussetzung fuer jeden konkreten Umsetzungsauftrag der Drei-Schichten-Architektur.
3. **Context-Assembler-Schema** (BRIDGE-0094 Abschnitt 3) und **Decision-Log-Schema**
   (`decision.schema.yaml`, ENTSCHEIDUNG-V2 §5) - beide nur als Sketch/Nennung vorbereitet,
   nicht entworfen.
4. **Governance-Pfad fuer die Drei-Schichten-Architektur** (eigenes Gate/Auftragsfolge,
   BRIDGE-0094 Abschnitt 5) - noch nicht begonnen.
5. (unveraendert aus v16/v17/v18 §6 Punkt 5: RAG-Status-Seite im Web-UI, Quellen-Manifest
   `rag/sources.yaml` real anlegen, generische Steuerchat-Vorlage/Dorfschaft-Einbindung/
   Draft-Modus.)

## 5. Referenz

Primaerdokumente unveraendert (`CLAUDE.md`, `docs/architecture/ARCHITECTURE.md`,
`docs/security/SECURITY-MODEL.md`, `docs/PROJEKTKONZEPT.md`). Neu seit v18:
`docs/concepts/MEHRPROJEKT-RAG-SPEZIFIKATION.md`,
`docs/concepts/DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md`,
`docs/concepts/KONZEPT-PRUEFRUNDEN-INTEGRATION_V3.md`,
`docs/concepts/ENTSCHEIDUNG-DREI-SCHICHTEN-STEERING-CONTINUITY.md`,
`docs/ACB-STEUERCHAT-ARBEITSWEISE.md` Abschnitt 5 Punkt 7.
