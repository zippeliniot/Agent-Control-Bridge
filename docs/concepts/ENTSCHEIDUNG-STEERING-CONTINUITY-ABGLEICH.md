# ENTSCHEIDUNG: "Steering Continuity"-Datenmodell vs. realer ACB-Mechanismus (BRIDGE-0073)

Stand 2026-10-02. Reine Konzeptpruefung, kein Schema, kein Code. Pruefmassstab fuer die
Generizitaet (§4) ist die Dorfschaft-Anforderungsform; Dorfschaft-Fachwerte (Kapitel-, Phasen-,
Statusnamen, K1-K6, Agentenrollen) werden hier **nicht** nach ACB uebernommen.
Das Quelldokument `04_DATENMODELL_STRUKTUR_GATES.md` liegt nicht im Repo; verglichen wird gegen
die im Auftrag `work-packages/BRIDGE-073.md` wiedergegebene Objektliste.

## 1. Objekttabelle (Option A = formalisieren, B = unveraendert, C = verwerfen)

| Vorgeschlagenes Objekt | Gegenstueck im Repo (Beleg) | Deckung | Option |
|---|---|---|---|
| Program | `schemas/project.schema.yaml`, `projects/<id>/project.yaml` | teilweise (kein `phase`) | A (S) — nur Phasenfeld, siehe §4a |
| WorkPackage | `schemas/task.schema.yaml`, `work-packages/BRIDGE-xxx.md`, `tasks/<id>.yaml` | vollstaendig | B |
| SteeringSession | `docs/ACB-STEUERCHAT-STANDARDSTART.md`, `scripts/steuerchat-vorlage.py`, `project.yaml: controller/review_roles` | teilweise (Prompt + Rollenfelder, kein Sitzungsobjekt) | A (S) — erst mit dem spaeteren MULTI-AGENT-Auftrag, siehe §5 |
| Checkpoint | CLAUDE.md "Checkpoint & Resume" (Haken + Commit), `schemas/heartbeat.schema.yaml`, `run beat` | vollstaendig | B |
| Decision | `docs/concepts/ENTSCHEIDUNG-*.md` (4 Dateien), Zustaende `REVIEW_REQUIRED`/`APPROVAL_REQUIRED` | teilweise (Prosa, kein Schema) | B — Entscheidungen sind bewusst menschlicher Text |
| OpenIssue | `docs/handover/ACB-UEBERGABE-v13.md` §2/§5/§6, `result.schema.yaml: findings`, `stop_conditions` | teilweise (laufuebergreifend nur Prosa) | A (S) — einziger Punkt mit echtem Kontinuitaetsnutzen |
| Dependency | `schemas/task.schema.yaml:216 depends_on` | teilweise (Auftrag→Auftrag, untypisiert) | B |
| Collision | `docs/concepts/ENTSCHEIDUNG-RESSOURCENREGEL.md`, `schemas/error-codes.yaml` (`RESOURCE_CONFLICT`, `CLAIM_CONFLICT`) | teilweise (nur technische Ressourcenkollision) | C als fachliche Konfliktklasse — gehoert in den Adapter, nicht in ACB |
| Baseline | Git selbst, `task: git.expected_head`, `result: base_head/head/task_hash/diff_hash` | teilweise (repoweit, nicht je Artefakt) | B — Git ist der Baseline-Mechanismus |
| HandoverState | `docs/handover/ACB-UEBERGABE-v<N>.md`, `scripts/handover-check.ps1|.sh`, `project.yaml: handover_policy` | vollstaendig | B |
| ChangeRequest | keines | keines | C — Auftraege sind unveraenderlich (CLAUDE.md: "es gibt bewusst kein `task edit`"); Aenderung = naechste freie `BRIDGE-00NN` |

## 2. Sondervermerk: Objekte ohne Gegenstueck

- **Dependency — Annahme des Auftrags korrigiert.** Die Bestandspruefung findet ein
  Gegenstueck: `depends_on` ist ein Pflichtfeld-Kandidat im Task-Schema und in
  `tasks/BRIDGE-0073.yaml` real belegt. Dependency ist also **nicht** gegenstuecklos; nur die
  Typisierung (Art der Abhaengigkeit) fehlt. Kein erkennbarer Bedarf an mehr.
- **Collision:** technisches Gegenstueck vorhanden (G4-Ressourcenregel), fachliches nicht.
  Fuer fachliche Konfliktklassen gibt es im ACB-Repo **keinen** Anwendungsfall — Vorratsdefinition.
- **Baseline:** Gegenstueck vorhanden (Git + Hashes). Ein eigenes ACB-Objekt ist Vorratsdefinition;
  Bedarf entsteht erst, wenn ACB Artefakt-Revisionen fachlich versionieren soll — heute nicht der Fall.
- **ChangeRequest:** gegenstuecklos **und** bewusst so. Kein Bedarf: die Unveraenderlichkeit von
  Auftraegen ist eine getragene Sicherheitsentscheidung, kein Defizit. Reine Vorratsdefinition.

## 3. ID-Namensraum

Die Planungs-IDs `ACB-ST-0xx` aus dem Uebergabepaket werden **nicht** als eigener Nummernkreis
uebernommen. ACB kennt getrennte Nummernraeume je Projekt ueber `task_prefix`
(`schemas/project.schema.yaml`); ein dritter, paralleler Planungs-Nummernkreis ohne Store-Eintrag
waere eine zweite Wahrheit neben `tasks/`. Jeder tatsaechliche Folgeauftrag laeuft als naechste
freie `BRIDGE-00NN`. `ACB-ST-0xx` darf hoechstens als Lesehilfe im Quelltext des Uebergabepakets
stehenbleiben, nie in `tasks/`, `work-packages/` oder einem Footer.

## 4. Generizitaets-Pruefung (Pruefmassstab Dorfschaft, kein Adapter-Entwurf)

| Punkt | Bewertung | Fundstelle / Begruendung |
|---|---|---|
| a) `Program.Phase` offene Phasenfolge | TRAEGT NICHT | `schemas/project.schema.yaml:13 additionalProperties: false` — kein `phase`-Feld und kein Erweiterungspunkt; ein Adapter kann nichts hinzufuegen. Fail-closed wirkt hier als Sperre, nicht als Schutz. |
| b) `WorkPackage.Kapitelstatus` variable Teilstatus | TRAEGT NICHT | `task.schema.yaml:82 acceptance_criteria` traegt beliebig viele frei benannte Eintraege, aber der Status je Eintrag ist binaer (`[ ]`/`[x]` im WP, `met: boolean` in `result.schema.yaml:105`). Eine adapterdefinierte mehrwertige Statustaxonomie ist nicht abbildbar. |
| c) Gatebericht als UND-Verknuepfung benannter Bedingungen | TRAEGT | `acceptance_criteria` (frei, unbegrenzt) + `acceptance_results[].criterion/met/note` bilden genau eine beliebig lange UND-Kette frei benannter Bedingungen; Benutzerfreigabe ist als Zustand `APPROVAL_REQUIRED` (`schemas/state-model.yaml`) vorhanden. |
| d) `Baseline` je Einzelartefakt einfrierbar | TRAEGT NICHT | `result.schema.yaml` kennt genau ein `repository`/`head`; `docs/handover/ACB-UEBERGABE-v13.md` §3 nennt das ausdruecklich als strukturellen Befund. Revisionen je Artefakt mit gueltiger Vorgaengerversion sind nicht abbildbar. |
| e) `Collision.Profilklasse` adapterdefinierte Konflikttaxonomie | TRAEGT NICHT | `task.schema.yaml:244 stop_conditions` ist ein geschlossenes Enum, per SSOT-Test gegen `schemas/error-codes.yaml` erzwungen (BRIDGE-0047). Kein Platz fuer adapterdefinierte Klassen. |
| f) `SteeringSession` mehrfach gleichzeitig + freie Pruefrolle | TRAEGT NICHT | Zwei Punkte: (1) kein Sitzungsobjekt, und die G4-Ressourcenregel (`ENTSCHEIDUNG-RESSOURCENREGEL.md`) verbietet zwei aktive Claims auf demselben (`repository`,`branch`) — gleichzeitige Bearbeitung desselben Programms kollidiert per Regel. (2) Die Auftragsannahme eines freien `Rolle`-Feldes trifft nicht zu: `project.schema.yaml:106 review_roles` ist ein geschlossenes Objekt (`lead`/`support`) mit geschlossenem Werte-Enum `[anthropic, openai, human, null]` — eine freie Rollenbezeichnung ist dort nicht eintragbar. |

Fuenf von sechs Punkten TRAEGT NICHT, und zwar immer aus demselben Grund: ACB ist durchgaengig
fail-closed mit geschlossenen Enums und `additionalProperties: false`. Das ist gewollt und bleibt;
Generizitaet fuer Fremdprojekte waere nur ueber **ausdrueckliche, benannte Erweiterungspunkte**
erreichbar, nicht ueber Aufweichung der Schemas. Diese Datei entscheidet das nicht.

## 5. Geltende Grenzen (nur vermerkt, hier nicht bewertet)

- **G5 unberuehrt.** Keine Aussage zu einem Dorfschaft-Adapter-Inhalt. G5 bleibt laut
  `docs/handover/ACB-UEBERGABE-v13.md` §2 nicht erreicht.
- **Codex-Rollenbeschraenkung** in der Dorfschaft-Fachkonzeptphase (Analyse-/Review-Instrument,
  keine Fachfreigabe) gilt bereits als inhaltliche Grenze — hier nur festgehalten, nicht bewertet.
- **Multi-Agent:** der fachliche Bedarf an paralleler Mehrfachbearbeitung mit zentraler
  Kompatibilitaetspruefung ist fuer Dorfschaft **fachlich gesetzt** (durch April bestaetigt).
  Die davon getrennte **Ausfuehrungsfreigabe** fuer MULTI-AGENT-Betrieb in ACB (Schreibkonflikte,
  Writer-Lock/Ressourcenregel analog BRIDGE-0063, Freigabekette) ist **weiterhin offen** und
  gehoert in einen eigenen, spaeteren ACB-Auftrag. In BRIDGE-0073 bleibt MULTI-AGENT: **NEIN**.
