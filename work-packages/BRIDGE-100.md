# BRIDGE-0100: Stammdaten-Block im Web UI zu den anderen Eingabebereichen verschoben

| Feld | Wert |
|---|---|
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| Scope | `src/bridge/webui.py` |

## Anlass

April (Steuerchat, 09.10.2026): der neue Block "Projekt-Einstellungen &
Stammdaten" (BRIDGE-0099) stand ganz unten nach allen Tabellen, getrennt von
den uebrigen Eingabebereichen (Akteur, Filter) oben auf der Seite.

## Ergebnis

Reine Platzierungsaenderung, keine neue Logik: der Block steht jetzt direkt
unter dem Filter-Bereich (`#filters`), vor dem Aktions-Log und den Tabellen -
zusammen mit den anderen Eingabebereichen am Seitenanfang.

## Akzeptanzkriterien

- [x] Block erscheint nur noch einmal, direkt nach `#filters`
- [x] Keine funktionale Aenderung (IDs/Handler unveraendert)
- [x] Volle Suite gruen
