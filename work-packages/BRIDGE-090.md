# BRIDGE-0090 - Dokumentkorrektur: Steering-Continuity-V2 (Issue 1) + OpenIssue-Verfahren in ARBEITSWEISE.md

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0090 |
| project_id | agent-control-bridge |
| Typ / Klasse | ARCHITECTURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - inhaltliche Korrektur an bestehenden Konzept-/Prozessdokumenten, kein Code, kein Widerspruchs-/Sicherheitsfall. |
| Modellwechsel zum Vorgaenger | NEIN (Vorgaenger BRIDGE-0089: Claude Sonnet 5 / MEDIUM, ARCHITECTURE) |
| depends_on | BRIDGE-0089 (ARCHIVED) |
| Gate | keines (reine Dokumentkorrektur) |
| stop_conditions | CONCEPT_CONFLICT |
| Multi-Agent | NEIN |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0090` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: Claude Sonnet 5 / DENKSTUFE: MEDIUM`. Abweichung von der Tabelle = STOPP.

## Anlass

Externe Pruefrunde vom 08.10.2026 zu `docs/concepts/KONZEPT-PRUEFRUNDEN-INTEGRATION_V2.md` hat
drei Luecken in `docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` bestaetigt und das
Verfahren fuer `OpenIssue`-Pruefrunden-Befunde praezisiert (V3 des Konzepts). April hat am
08.10.2026 im Steuerchat zugestimmt: Verfahren uebernehmen, drei Issues anlegen (vor diesem
Auftrag, separates Deliverable `issue-open-befehle.md`), Reihenfolge BRIDGE-0090 ->
Decision-Log-Formalisierungsentscheidung (ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md §6) ->
Drei-Schichten-Architektur-Spezifikation.

Issue 1 (angelegt per beiliegendem `issue-open-befehle.md` vor diesem Auftrag, `issue_id` =
`agent-control-bridge-ISSUE-0001`, sofern keine andere Nummer zwischenzeitlich vergeben wurde -
per `bridge issue list --project-id agent-control-bridge` gegenpruefen) wird durch Teil A
geschlossen.

## Auftrag

**Ziel:** Zwei bestehende Dateien praezisieren, keine neue Datei, keine Implementierung, keine
Schema-Aenderung, keine neue fachliche Entscheidung (V2 bleibt ENTWURF, BRIDGE-0073 Option B
bleibt unveraendert gueltig).

### Teil A - `docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` praezisieren

Drei konkrete Ergaenzungen (Issue 1):

1. **RAG-unabhaengiger Anlass fehlt in §2.** §2 begruendet den Nachtrag ausschliesslich mit der
   RAG-Retrieval-Pipeline (BRIDGE-0088). Ergaenzen: ein zweiter, von RAG unabhaengiger Anlass -
   die reine Prosa-Verlinkung zwischen `ENTSCHEIDUNG-*.md`-Dateien skaliert auch ohne RAG-Suche
   nicht mehr, sobald mehr als eine Handvoll Entscheidungsdokumente existieren und ein Steuerchat
   beim Sitzungsstart alle lesen muss (vgl. `docs/ACB-STEUERCHAT-STANDARDSTART.md` Abschnitt 2 -
   die Liste der "bei Bedarf"-Dokumente waechst bereits).
2. **§6 formuliert pauschale Aufhebung statt Ergaenzung/teilweise Revision.** Aktueller Wortlaut:
   "Soll BRIDGE-0073s Decision-Verdikt (Option B) aufgehoben und durch die Formalisierung aus
   Abschnitt 3 ersetzt werden". Praezisieren: die Formalisierung aus §3 ergaenzt das
   Objektmodell um strukturierte Felder (append-only Ereignisse, `supersedes`,
   `affects`/`implemented_by`/`verified_by`), sie hebt nicht auf, dass Entscheidungen weiterhin als
   menschlicher Prosa-Text in `ENTSCHEIDUNG-*.md`-Dateien formuliert werden (BRIDGE-0073s
   eigentliche Begruendung "Entscheidungen sind bewusst menschlicher Text", §1 dieses Dokuments,
   bleibt davon unberuehrt). Formulierung in §6 entsprechend anpassen: teilweise Revision
   (Formalisierungsebene), keine Aufhebung (Prosa-Ebene).
3. **Expliziter Prosa-Erhalt-Satz fehlt.** In §4 ("Was das NICHT ist") einen Satz ergaenzen: die
   Formalisierung ersetzt nicht die bestehenden `ENTSCHEIDUNG-*.md`-Prosadokumente durch
   strukturierte Datensaetze - sie ergaenzt sie um maschinenlesbare Referenzfelder fuer RAG-
   gestuetzte Suche, der menschlich lesbare Entscheidungstext bleibt die primaere Quelle.

Nach Abschluss: `bridge issue close <issue-1-id> --project-id agent-control-bridge --actor
claude-code --note "<Datei>:<Abschnitt> - <was ergaenzt wurde>, Commit <SHA>"` (konkrete
Dateizeile/Abschnitt im Note-Text nennen, nicht nur die SHA).

### Teil B - `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` Abschnitt 4 ergaenzen

Abschnitt 4 ("ACB-Nutzung — Kurzreferenz") traegt bereits einen Hinweis auf `issue open/close/list`
(BRIDGE-0075), aber keinen verpflichtenden Ablauf. Ergaenzen (neuer Unterpunkt, Text wortgleich
uebernehmen, nicht neu formulieren):

> `issue`-Ablauf (ab BRIDGE-0090 verbindlich): Registry abgleichen (`issue list --include-closed`,
> kein Duplikat anlegen) -> Befund mit Quelle pruefen (Datei+Zeile oder Commit-SHA aus frischem
> Klon) -> Issue erfassen (`issue open`, `origin_task_id` = Auftrag, aus dem der Befund stammt) ->
> auf GitHub sichern (kein `--commit`-Flag auf `issue open/close`, manuell `git add
> open-issues/<project_id>/ && git commit && git push`, sonst nur lokal sichtbar) ->
> Folgeauftrag verknuepfen (WP nennt `issue_id` im Anlass-Abschnitt, Issue bleibt bis Abschluss
> OPEN) -> Ergebnis pruefen (frischer Klon, echter Code-/Doku-Stand) -> Issue mit konkretem
> Nachweis schliessen (`note` nennt Akzeptanzkriterium + Datei+Zeile/Kommando-Ausgabe, nicht nur
> SHA) -> Abschluss auf GitHub verifizieren (`issue list --include-closed` nach frischem Klon
> zeigt CLOSED mit Nachweis-`note`).

## Nicht Teil dieses Auftrags

- Issues 2+3 (Integritaet: `GIT_COMMIT`/`GIT_PUSH`-Nachweis, `expected_head`/`base_head`-Trennung,
  `--commit`-Flag fuer `bridge issue`, `open_issue`-`kind` in `gitops.expected_git_files()`) -
  eigener, spaeterer Auftrag (Code-Aenderung, nicht reine Doku).
- Keine Entscheidung zu `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` §6 selbst (Decision-Log-
  Formalisierung) - das ist der naechste Schritt NACH diesem Auftrag, nicht Teil davon.
- Keine Aenderung an `CLAUDE.md`, `BRIDGE-0073`-Originaldokument (V1) oder dem Decision-Schema
  selbst.

## Akzeptanzkriterien

- [x] Teil A: drei Ergaenzungen in `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` umgesetzt (§2,
      §6, §4 wie oben beschrieben), Datei bleibt Status "ENTWURF - ENTSCHEIDUNG AUSSTEHEND".
- [x] Teil A: Issue 1 per `bridge issue close` mit konkretem Datei/Abschnitt-Nachweis geschlossen.
- [x] Teil B: `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` Abschnitt 4 um den neunstufigen Ablauf ergaenzt,
      inkl. Hinweis auf fehlendes `--commit`-Flag.
- [ ] Volle Suite einmal am Ende, nur letzte 3 Zeilen (reine Doku-Aenderung, keine neue
      Testabdeckung erwartet - Suite dient nur dem Nachweis, dass nichts kaputt ist).
- [ ] `git status` sauber, gepusht, Footer.
