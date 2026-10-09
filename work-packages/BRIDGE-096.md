# BRIDGE-0096: Governance-Pfad fuer Drei-Schichten-Architektur entscheiden

| Feld | Wert |
|---|---|
| Rechte | WORKTREE_WRITE, GIT_COMMIT, GIT_PUSH |
| Scope | `docs/concepts/DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md` |

## Anlass

BRIDGE-0094 Abschnitt 5 liess offen, ob die Drei-Schichten-Architektur ein eigenes Gate
braucht, bevor weitere Auftraege (Spike, Schemata) draufgesetzt werden.

## Entscheidung

Kein neues Gate. G0-G5 (`ACB-UMSETZUNGSKONZEPT-V2.md` §5) sind Reifegrade der
ACB-Infrastruktur selbst (Push-Sperre, CAS/Claim, Parallelitaet, Dorfschaft-Zugriff), kein
Feature-Gate-Modell. Bereits gelebte Praxis (BRIDGE-0088/89/90/93/94, alle
`task_class: ARCHITECTURE` ohne Gate-Bezug) bestaetigt das. Jede weitere Spezifikation
bleibt im normalen `task create`/`run start`/`run finish`-Flow; ein bestehendes Gate gilt
nur zusaetzlich, wenn eine spaetere Implementierung eine der dort bereits geregelten
Infrastruktur-Faehigkeiten beruehrt (z. B. Parallelbetrieb mehrerer Indexer-Laeufe -> G4).

## Akzeptanzkriterien

- [x] Bestehende Gate-Definition (G0-G5) gegen die Frage geprueft, nicht neu erfunden
- [x] Gelebte Praxis (BRIDGE-0088/89/90/93/94) als Beleg herangezogen
- [x] Entscheidung in `DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md` Abschnitt 5 festgehalten
- [x] Klargestellt, wann ein bestehendes Gate trotzdem zusaetzlich greift
