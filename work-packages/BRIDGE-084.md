# BRIDGE-0084 - RAG-Setup-Skript (Mensch-bestaetigter Install-Klick)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0084 |
| project_id | agent-control-bridge |
| Typ / Klasse | FEATURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | BRIDGE-0083 (ARCHIVED) |

> April (07.10.): "Punkt 3/4 als 'erkennen + Skript bereit, aber Mensch bestaetigt den
> Install-Klick' statt komplett unbeaufsichtigter Installation." BRIDGE-0083 liefert die
> Erkennung (`rag_prereqs.check`). Dieser Auftrag liefert das Skript, das die fehlenden
> Komponenten installiert - aber **nur nach einer expliziten Bestaetigung durch den Menschen**,
> niemals automatisch (gleicher Grundsatz wie CLAUDE.md zur Python-venv: "fail-closed: anhalten
> und melden, nicht selbst installieren" - hier auf den Install-Schritt selbst uebertragen, der
> erst nach Bestaetigung laeuft, nicht auf die Erkennung davor).

**Nur Windows-/PowerShell-Skript (`.ps1`).** Anders als `handover-check.ps1`/`.sh` (beide
Shells, weil das Gate auch unter Git Bash laufen muss) ist dieser Installationsschritt reine
Windows-Maschinenpflege (Ollama-Installer, `ollama.exe`, `git clone` unter `E:\_DEV\...`) - kein
Bash-Gegenstueck notwendig.

**Bekannte Testgrenze dieser Sitzung:** `pwsh` ist in dieser Linux-Cloud-Umgebung nicht
installiert - das Skript kann hier nicht tatsaechlich ausgefuehrt werden (wie bereits
`handover-check.ps1`, das ebenfalls nur durch Lesen/Review geprueft wird, nicht durch einen
Testlauf). Syntax und Logik werden durch sorgfaeltiges Review sichergestellt; der erste echte
Lauf braucht eine Pruefung auf HAM11/DES11 selbst - **ausdruecklich als offener Punkt vermerkt**,
keine stille Annahme von "funktioniert".

### Teil A - `scripts/rag-setup.ps1`

**Scope:** `scripts/rag-setup.ps1`.

1. Erkennung (liest dieselben drei Signale wie `rag_prereqs.check`, eigenstaendig in
   PowerShell nachgebildet - kein Python-Interpreter-Zwang fuer ein reines Mensch-Werkzeug):
   - Ollama erreichbar: `Invoke-RestMethod http://localhost:11434/api/tags` (Timeout, try/catch).
   - Modell `nomic-embed-text` vorhanden: `ollama list` parsen.
   - Index-Klon vorhanden: `Test-Path "$PSScriptRoot\..\..\rag-index\.git"` (Geschwister von
     `dev`/`board`/`claude`/`codex`, siehe `docs/architecture/machines.md`, BRIDGE-0083).
2. Statusuebersicht ausgeben (OK/FEHLT je Komponente). Ist alles OK: Meldung, Exit 0, keine
   weitere Aktion.
3. Fehlt etwas: **vor jeder Aktion** exakt auflisten, was installiert wuerde (z. B. "Ollama
   fuer Windows installieren", "ollama pull nomic-embed-text", "git clone .../acb-rag-index
   nach rag-index"). Danach `Read-Host` mit einer expliziten Ja/Nein-Frage - Standardverhalten
   bei leerer/anderer Eingabe ist **Abbruch** (fail-closed), nicht Fortfahren.
4. Nur bei bestaetigter Eingabe ("ja"/"j"): die fehlenden Schritte ausfuehren (Ollama-Installer
   herunterladen+starten oder `winget install -e --id Ollama.Ollama`, `ollama pull
   nomic-embed-text`, `git clone` + `git lfs pull` fuer `rag-index`). Nach jedem Schritt eigene
   Erfolgsmeldung; ein fehlschlagender Schritt bricht ab (fail-closed), fuehrt nicht die
   naechsten Schritte unbeaufsichtigt weiter aus.
5. Kein `--yes`/`--force`-Parameter zum Ueberspringen der Abfrage - die Bestaetigung ist
   zwingend, nicht optional (sonst waere es wieder unbeaufsichtigte Installation).
- [ ] Skript geschrieben, Review auf Syntax/Logik (kein Ausfuehrungstest moeglich, siehe oben)
- [ ] Bestaetigungsabfrage zwingend, Default = Abbruch, kein Bypass-Parameter

### Teil B - Dokumentation aktualisieren

**Scope:** `docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md`.

1. Abschnitt "Was ACB automatisch tut vs. was manuell bleibt" aktualisieren: "Fehlende
   Voraussetzung beheben" wechselt von "nein (reserviert fuer BRIDGE-0084)" auf "ja, per
   `scripts/rag-setup.ps1`, nur nach Bestaetigung".
2. Nutzungsabschnitt ergaenzen: `pwsh scripts\rag-setup.ps1` auf HAM11/DES11 ausfuehren, Ablauf
   (Erkennung -> Liste -> Bestaetigungsfrage -> Installation) kurz beschreiben.
- [ ] Doku aktualisiert, keine veraltete "reserviert"-Aussage mehr stehen

## Abschluss
1. Volle Suite EINMAL (Python-Tests unveraendert, da reines PowerShell-Skript - keine
   neuen Python-Tests in diesem Auftrag), letzte 3 Zeilen zeigen.
2. `git status` sauber.
- [ ] Volle Suite gruen

**Offene Bestaetigung an April:** bitte `scripts/rag-setup.ps1` einmal real auf HAM11 oder DES11
ausfuehren (zunaechst ruhig mit "nein" bei der Bestaetigungsfrage antworten, nur um die
Erkennung zu pruefen) und Rueckmeldung geben, ob Erkennung/Ausgabe wie erwartet funktionieren -
das kann aus dieser Sitzung heraus nicht verifiziert werden.
