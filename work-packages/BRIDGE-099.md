# BRIDGE-0099: RAG-Stammdaten je Projekt im Web UI

| Feld | Wert |
|---|---|
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| Scope | `src/bridge/webui.py`, `tests/test_webui.py` |

## Anlass

April-Fund (Steuerchat, 09.10.2026): die RAG-Einrichtungs-Funktionen
existieren bereits im Repo (`scripts/rag-setup.ps1`,
`scripts/rag-ollama-inventory.ps1`,
`docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md`, Erkennungslogik
`rag_prereqs.check()` seit BRIDGE-0083/0084/0085/0086) - waren aber im Web UI
an keiner Stelle sichtbar. Die bestehende Projekt-Einstellungsseite
(BRIDGE-0081) zeigt nur den `rag_enabled`-Schalter, keinen Einrichtungsstatus
und keine Verweise auf Skripte/Doku.

## Entscheidung zum Umfang (bewusste Abgrenzung, mit April abgestimmt)

April hat auf Rueckfrage **"RAG-Einrichtung je Projekt"** als ersten Schritt
bestaetigt (nicht die breitere, noch unklare Forderung nach "Beschreibungen
und Skripte als Dokumentation zu Installation und System-Check" fuer *alle*
neuen Funktionen generell). Deshalb hier **nur**:

- Anzeige des bestehenden Pruefergebnisses (`rag_prereqs.check`) je Projekt
- Verweis auf die bestehenden Skript-/Doku-Pfade (Text, kein Link-Handling)

**Explizit nicht Teil dieses Auftrags:** kein Skriptstart aus dem Web UI
(bliebe Mensch-bestaetigter Klick, BRIDGE-0084-Grundsatz), keine allgemeine
Dokumentations-/Systemcheck-Seite fuer andere Funktionen (Decision-Log,
Drei-Schichten-Architektur, Tree-sitter) - das waeren eigene, hier nicht
entschiedene Folgeauftraege, falls April das so will.

## Ergebnis

Neuer Endpunkt `GET /api/project/<id>/rag-status`: liefert `rag_enabled`,
`rag_index_repo`, die Pruefergebnisse von `rag_prereqs.check()` (nur wenn
`rag_enabled`, sonst `null` - kein unnoetiger Ollama-Call), sowie die
statischen Pfade zu Setup-/Inventar-Skript und Doku. Web UI: neuer Button
"RAG-Einrichtung pruefen" im bestehenden Projekt-Einstellungen-Block (jetzt
"Projekt-Einstellungen & Stammdaten"), zeigt das Ergebnis lesbar als Text.

## Akzeptanzkriterien

- [x] Neuer Endpunkt liefert bei `rag_enabled: false` `prereqs: null`, ruft
  `rag_prereqs.check()` nicht auf (kein unnoetiger Netzwerkzugriff)
- [x] Bei `rag_enabled: true` werden die echten Pruefergebnisse zurueckgegeben
- [x] Fehlendes Projektprofil -> 404, wie beim bestehenden `/api/project/<id>`
- [x] Skript-/Doku-Pfade im Payload (Text, keine Ausfuehrung)
- [x] Web-UI-Button zeigt das Ergebnis lesbar an
- [x] 3 neue Tests gruen, volle Suite gruen (594/594)
- [x] Scope-Abgrenzung (kein Skriptstart, keine generelle Doku-Seite)
  explizit begruendet
