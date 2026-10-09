# BRIDGE-0091 - rag-setup.ps1: Git-LFS-Praevenz-Pruefung ergaenzen

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0091 |
| project_id | agent-control-bridge |
| Typ / Klasse | BUGFIX |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - lokal begrenzte Skript-Aenderung, aber mit einer echten Entwurfsentscheidung (PATH-Refresh in laufender Session, Re-Pull-Logik fuer bereits bestehenden Klon) - kein reines Nach-Schema-Ausfuellen. |
| Modellwechsel zum Vorgaenger | NEIN (Vorgaenger BRIDGE-0090: Claude Sonnet 5 / MEDIUM, ARCHITECTURE) |
| depends_on | keine |
| Gate | keines (reine Skript-/Doku-Aenderung, kein Bridge-Kernverhalten) |
| stop_conditions | CONCEPT_CONFLICT |
| Multi-Agent | NEIN |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0091` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: Claude Sonnet 5 / DENKSTUFE: MEDIUM`. Abweichung von der Tabelle = STOPP.

## Anlass

Beim ersten Lauf von `scripts/rag-setup.ps1` auf DES11 (08.10.2026, Maschinenwechsel HAM11->DES11):
Ollama und das Embedding-Modell wurden korrekt installiert, der `rag-index`-Klon wurde angelegt,
aber `git lfs pull` schlug fehl ("`git: 'lfs' is not a git command`") - Git LFS war auf DES11 noch
nicht installiert. Das Skript meldet diesen Fall nur als `[ FAIL ]` *nach* dem Klon, statt ihn
vorab zu erkennen (gleiches Muster wie die bereits vorhandene Ollama-"installiert vs. erreichbar"-
Unterscheidung aus BRIDGE-0086, hier fehlt das Pendant fuer Git LFS). Zusaetzlich zeigte sich beim
manuellen Nachinstallieren: `winget install -e --id GitHub.GitLFS` traegt den neuen Pfad nur in die
Registry ein, ein `git lfs`-Aufruf **in derselben PowerShell-Session** bleibt bis zum PATH-Reload
(neues Fenster oder manueller Reload aus der Registry) erfolglos - das Skript muesste das selbst
abfangen, nicht den Menschen zwingen, das Terminal neu zu starten.

## Auftrag

**Ziel:** `scripts/rag-setup.ps1` so erweitern, dass ein fehlendes Git LFS vor dem `git clone`
erkannt, bei Bestaetigung installiert und **innerhalb desselben Laufs** nutzbar gemacht wird -
ohne dass der Mensch das Terminal neu starten muss. Kein neues Feature, keine Schema-Aenderung,
kein Bridge-Kernverhalten betroffen.

### Teil A - Erkennung ergaenzen (Abschnitt "Erkennung")

Neues Signal `$gitLfsInstalled`, nach demselben Muster wie `$ollamaInstalled`: `git lfs version`
in einem `try`/`catch` ausfuehren (Exit-Code/Exception pruefen, kein `winget list`-Parsing noetig,
da `git lfs version` direkt und zuverlaessig scheitert, wenn das Subcommand fehlt). Ausgabe:
`Ok "Git LFS installiert"` bzw. `Missing "Git LFS nicht installiert"`, gleiche Zeilenform wie die
bestehenden vier Signale.

### Teil B - Geplante-Aktionen-Liste und Bestaetigung erweitern

In der Liste "Folgende Schritte wuerden ausgefuehrt": wenn `-not $gitLfsInstalled`, zusaetzlichen
Punkt einfuegen (" Git LFS installieren (winget install -e --id GitHub.GitLFS) + git lfs install").
Reihenfolge: vor dem Index-Klon-Punkt, da Voraussetzung dafuer. Die bestehende
Ja/Nein-Bestaetigung deckt das mit ab (kein zusaetzlicher Bypass-Parameter, Grundsatz aus CLAUDE.md
bleibt: Installation nur nach Bestaetigung).

### Teil C - Installation: PATH-Refresh + `git lfs install` nach Neuinstallation

Vor dem bestehenden `if (-not $indexCloneExists)`-Block, neuer Block:
```powershell
if (-not $gitLfsInstalled) {
    Write-Host "Installiere Git LFS (noch nicht installiert) ..."
    winget install -e --id GitHub.GitLFS
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ FAIL ] Git-LFS-Installation fehlgeschlagen - Abbruch."
        exit 1
    }
    # PATH in dieser laufenden Session nachladen, kein Terminal-Neustart noetig
    # (winget traegt den neuen Pfad nur in die Registry ein, nicht ins
    # Environment des bereits laufenden Prozesses - DES11-Erfahrung 08.10.2026).
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
    try {
        git lfs version | Out-Null
        $gitLfsInstalled = $true
    } catch {
        Write-Host "[ FAIL ] Git LFS installiert, aber im laufenden Prozess weiterhin " `
                  "nicht aufrufbar - bitte Terminal neu oeffnen und Skript erneut starten."
        exit 1
    }
    git lfs install
    Write-Host "[ OK ] Git LFS installiert und aktiviert."
}
```
Exakte Variablennamen/Stil an die bestehende Datei anpassen (Funktionen `Ok`/`Missing`/`Info`
wiederverwenden), nicht wortgleich uebernehmen, wenn der bestehende Stil abweicht.

### Teil D - Bestehenden Klon ohne vollstaendige LFS-Dateien mitbehandeln

Aktuell gilt `$indexCloneExists = Test-Path (Join-Path $IndexPath ".git")` als "fertig" - ein
Klon, der wegen fehlendem Git LFS nur Platzhalterzeiger enthaelt (wie jetzt auf DES11 real
vorgefallen), wird bei einem erneuten Lauf faelschlich als vollstaendig erkannt und nicht
nachgebessert. Ergaenzen: wenn `$indexCloneExists` true ist, trotzdem `git lfs pull` im
`IndexPath` ausfuehren (idempotent, guenstig, kein erneuter Clone), nicht nur beim Erstanlegen -
bei Fehlschlag `[ FAIL ]` mit Hinweis, aber Skript nicht abbrechen (bestehendes Verhalten fuer
"Index-Klon vorhanden" bleibt sonst unveraendert, nur der LFS-Pull wird nachgeholt).

## Nicht Teil dieses Auftrags

- Keine Aenderung an `rag-ollama-inventory.ps1` oder der Ollama-Erkennungslogik.
- Keine Aenderung an `src/bridge/rag_prereqs.py` (Bridge-Kerncode, pruefte die drei urspruenglichen
  Signale - Git LFS ist eine Voraussetzung fuer den Klon-Inhalt, keine eigene von
  `rag_prereqs.check()` gepruefte Groesse; falls das gewuenscht ist, eigener, spaeterer Auftrag).
- Kein automatischer Bypass der Bestaetigungs-Abfrage.

## Akzeptanzkriterien

- [ ] Teil A: `$gitLfsInstalled`-Erkennung ergaenzt, OK/FEHLT-Zeile wie die vier bestehenden Signale.
- [ ] Teil B: fehlendes Git LFS erscheint in der "geplante Schritte"-Liste vor dem Index-Klon-Punkt.
- [ ] Teil C: Installation inkl. PATH-Refresh in derselben Session, `git lfs install` danach
      ausgefuehrt, klare Fail-Meldung falls PATH-Refresh selbst nicht reicht.
- [ ] Teil D: `git lfs pull` wird auch bei bereits vorhandenem Klon (re-)versucht, nicht nur beim
      Erstanlegen; Fehlschlag dort haelt das Skript nicht an.
- [ ] `docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md` Abschnitt 4 um einen Satz ergaenzt: Git
      LFS wird seit BRIDGE-0091 vom Skript selbst erkannt/installiert, nicht mehr nur als manuelle
      Voraussetzung in Abschnitt 3 beschrieben (Abschnitt 3 bleibt als Fallback-Beschreibung stehen).
- [ ] Volle Suite einmal am Ende, nur letzte 3 Zeilen (reines PowerShell-Skript, keine
      Python-Testabdeckung dafuer vorhanden - Suite dient nur dem Nachweis, dass der restliche
      Bridge-Code unberuehrt ist).
- [ ] `git status` sauber, gepusht, Footer.
