# ENTSCHEIDUNG: Ressourcenregel (BRIDGE-0063, Gate G4)

Status: umgesetzt in `src/bridge/claim.py`.

## Regel

Es gibt genau eine Regel: **nie zwei aktive Claims auf demselben Schluessel.**

- Schluessel = (`repository` des Auftrags, Ausgabe von `git remote get-url origin`
  im Repo-Root, `branch` des Auftrags).
- Aktiv = Claim existiert und seine Lease ist nicht abgelaufen.
- `claim` prueft alle Claims unter `results/*/claim.json` (ausser dem eigenen
  Auftrag) unter dem Writer-Lock. Gleicher Schluessel -> Ablehnung mit
  `ClaimError`, Fehlercode `RESOURCE_CONFLICT` (Zustand BLOCKED, kein neuer Zustand).
- Abgelaufene Claims blockieren nicht (Uebernahme wie bisher).
- Kein Remote ermittelbar: Remote-Teil = `<none>`; gleiches Repository + gleicher
  Branch kollidieren dann trotzdem (konservativ, nie weniger streng).

## Abgrenzung

`CLAIM_CONFLICT` = derselbe Auftrag ist fremd geclaimt.
`RESOURCE_CONFLICT` = anderer Auftrag belegt dieselbe Ressource.
Der Code steht in `schemas/error-codes.yaml` und im Enum `stop_conditions`
(SSOT-Test aus BRIDGE-0047 erzwingt Gleichheit).
