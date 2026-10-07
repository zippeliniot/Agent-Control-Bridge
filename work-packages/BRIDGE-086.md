# BRIDGE-0086 - rag-setup.ps1: vorhandene Ollama-Instanz erkennen, Modell nicht doppelt laden

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0086 |
| project_id | agent-control-bridge |
| Typ / Klasse | BUGFIX |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | BRIDGE-0085 (ARCHIVED) |

> Anlass (April, 07.10.): auf HAM11 hat `rag-setup.ps1` `winget install` ausgefuehrt, obwohl
> Ollama schon installiert war - nur weil die HTTP-Erreichbarkeitspruefung im Moment der
> Pruefung fehlschlug (Dienst lief gerade nicht). `winget` hat daraus zwar keine echte
> Doppelinstallation gemacht (Reinstall derselben Version, kein zweiter Eintrag), aber das war
> Zufall, nicht Absicht des Skripts. April: "ergaenze fuer die installation von rag auch die
> suche nach einer vorhandenen ollama instanz und sorge dafuer das das model nicht doppelt
> installiert wird."

### Teil A - Installiert vs. erreichbar unterscheiden

**Scope:** `scripts/rag-setup.ps1`.

1. Neue, von der HTTP-Erreichbarkeit unabhaengige Erkennung `$ollamaInstalled`: `winget list
   --id Ollama.Ollama` (Treffer in der Ausgabe) ODER eines der bekannten
   Installationsverzeichnisse vorhanden (`%LOCALAPPDATA%\Programs\Ollama`,
   `%ProgramFiles%\Ollama`, `%ProgramFiles(x86)%\Ollama` - dieselbe Liste wie in
   `rag-ollama-inventory.ps1`, BRIDGE-0085).
2. Aktionsliste/Bestaetigungsfrage je nach Kombination:
   - erreichbar: keine Ollama-Aktion (unveraendert).
   - nicht erreichbar, aber installiert: Aktion wird zu "Ollama-Dienst starten (bereits
     installiert, antwortet aber nicht)" statt `winget install` - startet den gefundenen
     `ollama app.exe`/`ollama.exe`-Prozess aus dem erkannten Installationsverzeichnis, dann bis
     zu 10 Sekunden in 2-Sekunden-Schritten erneut `GET /api/tags` versuchen. Bleibt es dabei
     nicht erreichbar: Fehlermeldung, Abbruch (fail-closed) - **kein** automatischer Fallback
     auf `winget install` bei bereits erkannter Installation.
   - nicht erreichbar und nicht installiert: Aktion bleibt `winget install` (unveraendertes
     Verhalten von BRIDGE-0084/0085).
3. Statusuebersicht am Anfang um eine Zeile ergaenzen: "Ollama installiert: ja/nein"
   (unabhaengig von "erreichbar").
- [ ] `$ollamaInstalled` korrekt erkannt (Test mit vorhandenem/fehlendem winget-Treffer)
- [ ] Bereits installiert + nicht erreichbar -> Dienst-Start-Versuch, kein `winget install`
- [ ] Weder installiert noch erreichbar -> weiterhin `winget install` (unveraendert)

### Teil B - Modell-Pull nur nach frischer Pruefung (kein doppelter Download)

**Scope:** `scripts/rag-setup.ps1`.

1. Die Pruefung auf `$embedModelPresent` (BRIDGE-0084) beruht auf der Modell-Liste aus der
   **ersten** Erreichbarkeitspruefung - die kann veraltet sein, wenn Ollama zwischen Erkennung
   und Installationsschritt erst gestartet wurde (Teil A). Vor dem eigentlichen `ollama pull
   $EmbedModel`-Aufruf: erneut `ollama list` (CLI, nicht HTTP - laeuft nach einem frischen
   Dienststart zuverlaessiger) ausfuehren und auf `$EmbedModel` pruefen. Ist das Modell jetzt
   doch vorhanden (weil es schon lag, nur zum Pruefzeitpunkt nicht sichtbar war): Pull
   **uebersprungen**, Meldung "Modell bereits vorhanden - kein erneuter Download", kein
   `ollama pull`-Aufruf.
2. Gleiches Prinzip fuer den Index-Klon ist nicht nötig (Dateisystem-Pruefung `Test-Path` ist
   nicht von einem Dienststart abhaengig, bleibt unveraendert).
- [ ] Frische `ollama list`-Pruefung direkt vor dem Pull-Schritt
- [ ] Modell bereits vorhanden -> kein `ollama pull`-Aufruf, nur Meldung

## Abschluss
1. Volle Suite EINMAL (keine neuen Python-Tests - reines PowerShell-Skript), letzte 3 Zeilen zeigen.
2. `git status` sauber.
- [ ] Volle Suite gruen

**Hinweis (wie bei BRIDGE-0084/0085):** kein `pwsh` in dieser Sitzung - Review statt Ausfuehrungstest.
Bitte auf HAM11 oder DES11 einmal pruefen, idealerweise mit Ollama-Dienst bewusst beendet vor dem Lauf.
