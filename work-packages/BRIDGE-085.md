# BRIDGE-0085 - OLLAMA_MODELS auf E: + Installations-/Modell-Inventar-Skript

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0085 |
| project_id | agent-control-bridge |
| Typ / Klasse | FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | BRIDGE-0084 (ARCHIVED) |

> Anlass (April, 07.10.): `rag-setup.ps1` hat Ollama auf HAM11 installiert, ohne `OLLAMA_MODELS`
> zu setzen - Modelle landen damit auf `C:` (zu wenig Platz) statt `E:`. Zudem existiert jetzt
> vermutlich eine Doppelinstallation (vorheriges Ollama + die durch das Skript ausgeloeste).
> April: "es muss die doppelte installation wieder geloescht werden. schreibe pwsh script um
> das system zu durchsuchen und die installation und modell listen." - zunaechst **nur**
> Erkennung/Auflistung, die eigentliche Loeschung bleibt ein von April bestaetigter, manueller
> Schritt (gleicher Fail-closed-Grundsatz wie bei der Installation selbst, BRIDGE-0084).

### Teil A - `rag-setup.ps1`: `OLLAMA_MODELS` vor Installation auf `E:` setzen

**Scope:** `scripts/rag-setup.ps1`, `docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md`.

1. Vor dem Ollama-Installationsschritt (nach Bestaetigung, vor `winget install`): pruefen, ob
   die Benutzer-Umgebungsvariable `OLLAMA_MODELS` bereits gesetzt ist
   (`[Environment]::GetEnvironmentVariable("OLLAMA_MODELS", "User")`). Ist sie leer/nicht
   gesetzt, auf `E:\_DEV\ollama-models` setzen (`SetEnvironmentVariable(..., "User")`) **bevor**
   `winget install` laeuft, und das sichtbar melden ("OLLAMA_MODELS gesetzt auf ..."). Ist sie
   bereits (auf einen anderen Pfad) gesetzt, nicht ueberschreiben, nur anzeigen - kein stilles
   Ueberschreiben einer bewussten Vorentscheidung.
2. Erkennungsabschnitt (Status-Uebersicht) um eine Zeile ergaenzen, die den aktuellen Wert von
   `OLLAMA_MODELS` anzeigt (oder "nicht gesetzt (Standard: C:\Users\<Nutzer>\.ollama\models)").
3. `docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md`: Abschnitt 1 (Ollama-Dienst) um den
   Hinweis auf `OLLAMA_MODELS` erweitern - warum (Modelle sind gross, `E:` statt `C:`), wie
   (Env-Var, Neustart des Diensts nötig), und dass `rag-setup.ps1` das seit diesem Auftrag
   automatisch vorbelegt, wenn noch nichts gesetzt ist.
- [x] `OLLAMA_MODELS` wird nur gesetzt, wenn noch leer; bestehender Wert bleibt unberuehrt
- [x] Status-Uebersicht zeigt aktuellen `OLLAMA_MODELS`-Wert an
- [x] Doku aktualisiert

### Teil B - `scripts/rag-ollama-inventory.ps1`: Installations- und Modell-Inventar

**Scope:** neues Skript `scripts/rag-ollama-inventory.ps1`,
`docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md`.

1. Reine Erkennung/Auflistung (kein automatisches Loeschen als Standardverhalten):
   - Ollama-Installationen finden: `winget list --id Ollama.Ollama` (Paketverwaltung-Eintrag),
     bekannte Installationspfade pruefen (`$env:LOCALAPPDATA\Programs\Ollama`,
     `$env:ProgramFiles\Ollama`), jeweils Pfad + Vorhandensein ausgeben.
   - Modellablagen finden: Standardpfad (`$env:USERPROFILE\.ollama\models`) UND den Pfad aus
     `OLLAMA_MODELS` (falls gesetzt) jeweils pruefen - Vorhandensein, Groesse
     (`Get-ChildItem -Recurse | Measure-Object -Property Length -Sum`), Anzahl Dateien in
     `models\blobs`.
   - `ollama list` ausfuehren und die aktuell dem laufenden Dienst bekannten Modelle anzeigen
     (das sagt, welche Ablage der Dienst tatsaechlich benutzt).
   - Deutliche Warnung ausgeben, wenn **beide** Modellablagen (Standard und `OLLAMA_MODELS`)
     tatsaechlich Daten enthalten ("ACHTUNG: zwei Modellablagen mit Inhalt - vermutlich die
     Doppelinstallation, die geraeumt werden sollte").
2. Optionaler, explizit bestaetigter Aufraeum-Abschnitt (gleiches Muster wie `rag-setup.ps1`,
   KEIN automatisches Loeschen): nach der Auflistung fragen, ob die **alte** Modellablage
   (Standardpfad unter `C:`, niemals der `OLLAMA_MODELS`-Zielpfad) geloescht werden soll -
   eigene Ja/Nein-Abfrage je Fund, Default bei falscher/leerer Eingabe ist "nicht loeschen".
   Nur bei "ja" `Remove-Item -Recurse -Force` auf genau diesen einen Pfad.
3. `docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md`: neuen Abschnitt "Inventar/Aufraeumen"
   mit Nutzungshinweis (`pwsh scripts\rag-ollama-inventory.ps1`).
- [ ] Skript geschrieben, Review auf Syntax/Logik (kein Ausfuehrungstest moeglich, `pwsh` in
      dieser Sitzung nicht verfuegbar - wie bereits bei BRIDGE-0084 vermerkt)
- [ ] Aufraeum-Abschnitt loescht nur nach expliziter Bestaetigung, nie den `OLLAMA_MODELS`-Zielpfad
- [ ] Doku-Abschnitt ergaenzt

## Abschluss
1. Volle Suite EINMAL (keine neuen Python-Tests - reine PowerShell-Skripte), letzte 3 Zeilen zeigen.
2. `git status` sauber.
- [ ] Volle Suite gruen

**Offene Bestaetigung an April:** bitte `rag-ollama-inventory.ps1` zuerst nur lesend laufen
lassen (die Abfrage am Ende mit "nein" beantworten), die Ausgabe pruefen, und erst danach -
wenn die Zuordnung (welcher Pfad ist die alte Doppelinstallation) eindeutig ist - den
Aufraeum-Schritt bestaetigen. Diese Sitzung kann weder die Ausgabe noch die Loeschung selbst
verifizieren (kein `pwsh`, kein Zugriff auf HAM11).
