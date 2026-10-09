# BRIDGE-0094: Drei-Schichten-Architektur fuer Steering Continuity spezifizieren

| Feld | Wert |
|---|---|
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| Scope | `docs/concepts/DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md` |

## Anlass

`ENTSCHEIDUNG-DREI-SCHICHTEN-STEERING-CONTINUITY.md` §5 empfahl die Reihenfolge BRIDGE-0090
-> V2 §6 -> Mehrprojekt-RAG -> diese Spezifikation. April hat die Reihenfolge 09.10.2026
bestaetigt; alle drei Vorbedingungen sind erfuellt (BRIDGE-0090 COMPLETED, V2 §6 entschieden,
BRIDGE-0093 COMPLETED).

## Ergebnis

Drei Schichten benannt (Decision-Log, Symbol-/Datei-Graph, Vektor-RAG-Archiv), Routing-
Kriterium und Context-Assembler mit Rueckfluss skizziert, Symbol-/Datei-Graph gegen den
real genannten Dorfschaft-Stack (PHP/MariaDB/JS/PowerShell) spezifiziert - Tree-sitter als
Kandidat, nicht festgelegt. Details: `docs/concepts/DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md`.

## Akzeptanzkriterien

- [x] Alle drei Vorbedingungen (BRIDGE-0090, V2 §6, Mehrprojekt-RAG) vor Beginn verifiziert
- [x] Drei Schichten gegen bestehende Dokumente abgegrenzt (was ist neu, was nur umbenannt)
- [x] Symbol-/Datei-Graph gegen echten Dorfschaft-Stack spezifiziert, nicht werkzeugneutral
  offengelassen
- [x] Offene Folgefragen (Governance, Schema, Spike) explizit als nicht hier entschieden markiert
