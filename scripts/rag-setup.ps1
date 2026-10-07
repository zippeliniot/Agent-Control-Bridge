#!/usr/bin/env pwsh
#
# rag-setup.ps1 - RAG-Infrastruktur-Setup der Agent Control Bridge (BRIDGE-0084/0085).
# Erkennt fehlende Voraussetzungen (Ollama, Embedding-Modell, Index-Klon) und
# installiert sie NUR nach ausdruecklicher Bestaetigung - niemals automatisch.
# BRIDGE-0085: setzt OLLAMA_MODELS vor einer Ollama-Neuinstallation auf E:,
# damit Modelle nicht auf C: landen (zu wenig Platz) - nur wenn noch nicht gesetzt.
# Siehe docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md.
#
# Grundsatz (CLAUDE.md, auf RAG uebertragen): Erkennung ist automatisch, die
# Installation selbst ist fail-closed - ohne bestaetigte Eingabe passiert nichts.
#
# Nutzung:
#   pwsh scripts\rag-setup.ps1

$ErrorActionPreference = "Stop"

$OllamaUrl        = "http://localhost:11434"
$EmbedModel       = "nomic-embed-text"
$IndexRepo        = "https://github.com/zippeliniot/acb-rag-index.git"
$DefaultOllamaModelsPath = "E:\_DEV\ollama-models"

# rag-index ist Geschwister von dev/board/claude/codex (BRIDGE-0083, siehe
# docs/architecture/machines.md) - eine Ebene ueber dem Repo-Wurzelverzeichnis
# dieses Skripts (scripts\ liegt direkt im Checkout, also zwei Ebenen hoch).
$RepoRoot  = Split-Path -Parent $PSScriptRoot
$IndexPath = Join-Path (Split-Path -Parent $RepoRoot) "rag-index"

function Ok($m)   { Write-Host "[ OK ]   $m" }
function Missing($m) { Write-Host "[ FEHLT ] $m" }
function Info($m) { Write-Host "         $m" }

Write-Host "=== Agent Control Bridge - RAG-Setup ==="
Write-Host "Index-Pfad: $IndexPath"
Write-Host ""

# --- Erkennung (liest dieselben drei Signale wie rag_prereqs.check) ---------

$ollamaReachable = $false
$models = @()
try {
    $resp = Invoke-RestMethod -Uri "$OllamaUrl/api/tags" -TimeoutSec 3
    $ollamaReachable = $true
    if ($resp.models) { $models = $resp.models | ForEach-Object { $_.name } }
} catch {
    $ollamaReachable = $false
}

$embedModelPresent = $false
if ($ollamaReachable) {
    $embedModelPresent = @($models | Where-Object {
        $_ -eq $EmbedModel -or $_.StartsWith("$EmbedModel`:")
    }).Count -gt 0
}

$indexCloneExists = Test-Path (Join-Path $IndexPath ".git")

if ($ollamaReachable) { Ok "Ollama erreichbar ($OllamaUrl)" }
else { Missing "Ollama nicht erreichbar ($OllamaUrl)" }

if ($embedModelPresent) { Ok "Embedding-Modell '$EmbedModel' vorhanden" }
else { Missing "Embedding-Modell '$EmbedModel' nicht vorhanden" }

if ($indexCloneExists) { Ok "Index-Klon vorhanden ($IndexPath)" }
else { Missing "Index-Klon nicht vorhanden ($IndexPath)" }

# BRIDGE-0085: nur anzeigen, nicht hier schon setzen - Ollama-Modelle landen
# sonst auf C: statt E: (zu wenig Platz, HAM11-Erfahrung 07.10.2026).
$currentOllamaModels = [Environment]::GetEnvironmentVariable("OLLAMA_MODELS", "User")
if ($currentOllamaModels) { Ok "OLLAMA_MODELS gesetzt auf $currentOllamaModels" }
else { Missing "OLLAMA_MODELS nicht gesetzt (Standard: `$env:USERPROFILE\.ollama\models auf C:)" }

Write-Host ""

if ($ollamaReachable -and $embedModelPresent -and $indexCloneExists) {
    Write-Host "Alle Voraussetzungen vorhanden - nichts zu tun."
    exit 0
}

# --- Liste der geplanten Aktionen (vor jeder Aktion anzeigen) ---------------

Write-Host "Folgende Schritte wuerden ausgefuehrt:"
if (-not $ollamaReachable) {
    Info "1. Ollama fuer Windows installieren (winget install -e --id Ollama.Ollama)"
}
if (-not $embedModelPresent) {
    Info "2. ollama pull $EmbedModel"
}
if (-not $indexCloneExists) {
    Info "3. git clone $IndexRepo -> $IndexPath, danach git lfs pull"
}
Write-Host ""

# --- Zwingende Bestaetigung (kein Bypass-Parameter, Default = Abbruch) -----

$answer = Read-Host "Fortfahren und die fehlenden Komponenten installieren? (ja/nein)"
if ($answer -notin @("ja", "j", "yes", "y")) {
    Write-Host "Abgebrochen - keine Aenderung vorgenommen."
    exit 1
}

# --- Installation (nur nach Bestaetigung, jeder Schritt einzeln geprueft) --

if (-not $ollamaReachable) {
    # BRIDGE-0085: OLLAMA_MODELS VOR der Installation auf E: vorbelegen, damit
    # Ollama von Anfang an dort statt auf C: ablegt - nur wenn noch nichts
    # gesetzt ist (ein bestehender bewusster Wert wird nie ueberschrieben).
    if (-not $currentOllamaModels) {
        Write-Host "Setze OLLAMA_MODELS auf $DefaultOllamaModelsPath (vorher nicht gesetzt) ..."
        [Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $DefaultOllamaModelsPath, "User")
        Write-Host "[ OK ] OLLAMA_MODELS gesetzt. Gilt fuer neue Shells/Prozesse - dieser " `
                  "Ollama-Dienst muss nach der Installation damit (neu) gestartet werden."
    } else {
        Write-Host "OLLAMA_MODELS bereits gesetzt auf $currentOllamaModels - unveraendert."
    }
    Write-Host "Installiere Ollama ..."
    winget install -e --id Ollama.Ollama
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ FAIL ] Ollama-Installation fehlgeschlagen - Abbruch."
        exit 1
    }
    Write-Host "[ OK ] Ollama installiert. Bitte Terminal ggf. neu starten, bevor der " `
              "naechste Schritt (Modell-Pull) laeuft."
}

if (-not $embedModelPresent) {
    Write-Host "Lade Embedding-Modell '$EmbedModel' ..."
    ollama pull $EmbedModel
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ FAIL ] 'ollama pull $EmbedModel' fehlgeschlagen - Abbruch."
        exit 1
    }
    Write-Host "[ OK ] Modell '$EmbedModel' geladen."
}

if (-not $indexCloneExists) {
    Write-Host "Klone Index-Repository ..."
    git clone $IndexRepo $IndexPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ FAIL ] git clone fehlgeschlagen - Abbruch."
        exit 1
    }
    Push-Location $IndexPath
    git lfs pull
    $lfsExit = $LASTEXITCODE
    Pop-Location
    if ($lfsExit -ne 0) {
        Write-Host "[ FAIL ] 'git lfs pull' fehlgeschlagen - Klon liegt vor, " `
                  "aber ggf. ohne grosse Dateien."
        exit 1
    }
    Write-Host "[ OK ] Index-Klon angelegt unter $IndexPath."
}

Write-Host ""
Write-Host "Setup abgeschlossen."
exit 0
