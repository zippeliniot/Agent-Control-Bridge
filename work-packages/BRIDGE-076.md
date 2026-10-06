# BRIDGE-0076 - Entscheidung MULTI-AGENT-Ausfuehrungsfreigabe (Schreibkonfliktvermeidung)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0076 |
| project_id | agent-control-bridge |
| Typ / Klasse | T1 / ARCHITECTURE |
| Teile (alte Nummern) | keine (neuer Auftrag, kein Buendel) |
| Rechte | WORKTREE_WRITE, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Opus 5 / HIGH** - Sicherheitsfall (Schreibkonfliktvermeidung bei echter Parallelausfuehrung), daher HIGH statt MEDIUM (ACB-UMSETZUNGSKONZEPT-V2.md §4). |
| Modellwechsel zum Vorgaenger | JA (BRIDGE-0075 war Claude Sonnet 5 / MEDIUM, T2-Implementierung) |
| depends_on | BRIDGE-0075 (ARCHIVED) |
| Gate | keines (reine Entscheidung, kein G2/G3/G4-Scope beruehrt) |
| stop_conditions | CONCEPT_CONFLICT |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0076` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

## Auftrag

**Hintergrund:** `docs/concepts/ENTSCHEIDUNG-RESSOURCENREGEL.md` (BRIDGE-0063) legt genau eine Regel fest: nie zwei aktive Claims auf demselben Schluessel `(repository, remote, branch)`. Das verhindert strukturell echte Parallelausfuehrung mehrerer Sitzungen am selben Repository/Branch - auch wenn sie an unterschiedlichen Artefakten arbeiten. In BRIDGE-0073 Punkt 4f hat April den **fachlichen** Bedarf an paralleler Mehrfachbearbeitung fuer Dorfschaft-Fachkonzepte (mehrere `SteeringSession` gleichzeitig auf demselben Program/WorkPackage, plus eine Integrationsrolle zur zentralen Kompatibilitaetspruefung) bereits bestaetigt. Das ist eine fachliche Festlegung fuer Dorfschaft, **keine** Ausfuehrungsfreigabe fuer MULTI-AGENT-Betrieb in ACB. Diese getrennte, bislang offene Ausfuehrungsfreigabe ist Gegenstand dieses Auftrags.

**Ziel:** Eine Entscheidungsdatei, die festlegt, OB und WIE ACB echte Parallelausfuehrung (mehrere gleichzeitig aktive Claims auf feingranularerer Ressourcenebene als heute) sicher zulassen kann, ohne die bestehende Ressourcenregel (BRIDGE-0063) aufzuweichen oder Schreibkonflikte zu riskieren. Keine Implementierung, kein neues Schema, keine Aenderung an `claim.py`.

**Scope:** Neu: `docs/concepts/ENTSCHEIDUNG-MULTI-AGENT-AUSFUEHRUNG.md` (max. 80 Zeilen). Sonst nichts. Kein Code, kein `schemas/`-Eintrag, keine Aenderung an `src/bridge/claim.py` oder bestehenden Entscheidungs-/Regeldateien.

1. Ist-Stand/Risiko in 3-5 Saetzen benennen: heutiger Schluessel `(repository, remote, branch)` ist repo-/branchweit, nicht artefaktweise. Zwei Sitzungen am selben Dorfschaft-Branch, die unterschiedliche Einzelkonzepte bearbeiten, wuerden sich heute gegenseitig als `RESOURCE_CONFLICT` blockieren (sicher, aber nicht parallelfaehig) - oder, falls die Granularitaet einfach auf Dateiebene verfeinert wird, drohen neue Risiken (gleichzeitiges Schreiben in gemeinsam genutzte Dateien wie `work-packages/`, `audit/audit.jsonl`, dieselbe `docs/handover/ACB-UEBERGABE-v<N>.md`), die die bestehende Ressourcenregel bislang strukturell ausschliesst.
2. Mindestens zwei Granularitaets-/Sicherheitsoptionen fuer einen feineren Ressourcen-Schluessel ausarbeiten (nach demselben Muster wie `ENTSCHEIDUNG-RESSOURCENREGEL.md`/`ENTSCHEIDUNG-OPENISSUE-FORMALISIERUNG.md`: T-Shirt-Groesse, Vor-/Nachteile, Risiken), z. B.:
   - **Artefaktebene:** Schluessel erweitert um einen vierten, adapterdefinierten Bestandteil (z. B. betroffener Pfad/Artefakt-Identifier), sodass zwei Claims auf demselben Repo/Branch aber unterschiedlichem Artefakt gleichzeitig aktiv sein duerfen.
   - **Geteilte Dateien bleiben repo-/branchweit gesperrt:** eine explizite, generische Ausnahmeliste (oder ein zweiter, grober Schluessel) fuer Dateien, die trotz Artefakt-Granularitaet weiterhin repo-/branchweit exklusiv bleiben muessen (Audit-Log, Handover-Datei, `work-packages/`-Verzeichnis als Ganzes) - WELCHE Dateien das konkret sind, ist Teil der Entscheidung.
   - **Unveraendert (B - keine Parallelausfuehrung):** Ressourcenregel bleibt wie sie ist; Parallelitaet wird stattdessen ausserhalb von ACB geloest (z. B. mehrere unabhaengige Worktrees/Branches je Sitzung, erst beim Cross-Check zusammengefuehrt) - kein ACB-Codeeingriff noetig.
3. Fuer jede Option explizit pruefen: bleibt das Fail-Closed-Prinzip erhalten (ein Konflikt fuehrt weiterhin zu einem harten Fehler, nie zu stillem Verlust einer Schreiboperation)? Bleibt die Loesung generisch (kein Dorfschaft-Fachwert im Schluessel oder in `claim.py` selbst, Dorfschaft nur als Pruefmassstab wie in BRIDGE-0073 Punkt 3)?
4. Empfehlung mit Begruendung; Status ENTWURF, Freigabe durch April ausstehend.
5. Ausdruecklich NICHT Teil dieses Auftrags: Implementierung der empfohlenen Option, Dorfschaft-Adapter-Inhalt, G5-Bewertung, Aenderung an `claim.py`/`ENTSCHEIDUNG-RESSOURCENREGEL.md`.

**Tests:** Keine.

- [x] Ist-Stand/Risiko in 3-5 Saetzen benannt
- [x] Mindestens zwei Granularitaets-/Sicherheitsoptionen mit T-Shirt-Groesse, Vor-/Nachteilen, Risiken
- [x] Fail-Closed- und Generizitaets-Check je Option
- [x] Empfehlung mit Begruendung, Status ENTWURF
- [x] Kein Code/Schema geaendert, keine Dorfschaft-Fachwerte uebernommen
