#!/usr/bin/env pwsh
#
# rag-ollama-inventory.ps1 - Ollama-Installations- und Modell-Inventar (BRIDGE-0085).
# Anlass: nach einer ungeplanten Ollama-Installation auf HAM11 (07.10.2026) ohne
# OLLAMA_MODELS -> Modelle landeten auf C: (zu wenig Platz) statt E:, vermutlich
# zusaetzlich zu einer bereits vorhandenen Installation (Doppelinstallation).
#
# Dieses Skript ist reine Erkennung/Auflistung - es loescht standardmaessig
# NICHTS. Nur im optionalen Aufraeum-Abschnitt am Ende, und auch dort erst nach
# einer expliziten Ja/Nein-Bestaetigung je Fund (Default bei falscher/leerer
# Eingabe: nicht loeschen). Der OLLAMA_MODELS-Zielpfad selbst wird nie geloescht.
#
# Siehe docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md.
#
# Nutzung:
#   pwsh scripts\rag-ollama-inventory.ps1

$ErrorActionPreference = "Continue"

function Section($m) { Write-Host ""; Write-Host "=== $m ===" }
function Ok($m)       { Write-Host "[ OK ]      $m" }
function Found($m)    { Write-Host "[ GEFUNDEN ] $m" }
function NotFound($m) { Write-Host "[ -- ]      $m" }
function Warn($m)     { Write-Host "[ ACHTUNG ] $m" }

Section "Agent Control Bridge - Ollama-Installations-/Modell-Inventar"

# --- 1) Installationen (winget + bekannte Installationspfade) --------------

Section "1. Installationen"

try {
    $wingetOut = winget list --id Ollama.Ollama 2>$null
    if ($wingetOut -match "Ollama") {
        Found "winget-Eintrag vorhanden:"
        $wingetOut | ForEach-Object { Write-Host "            $_" }
    } else {
        NotFound "Kein winget-Eintrag fuer Ollama.Ollama gefunden."
    }
} catch {
    Warn "winget nicht verfuegbar oder Abfrage fehlgeschlagen: $_"
}

$knownInstallPaths = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Ollama"),
    (Join-Path ${env:ProgramFiles} "Ollama"),
    (Join-Path ${env:ProgramFiles(x86)} "Ollama")
) | Where-Object { $_ }

foreach ($p in $knownInstallPaths) {
    if (Test-Path $p) { Found "Installationsverzeichnis: $p" }
    else { NotFound "Kein Installationsverzeichnis unter: $p" }
}

# --- 2) Modellablagen (Standardpfad + OLLAMA_MODELS, falls gesetzt) --------

Section "2. Modellablagen"

function Describe-ModelDir($label, $path) {
    if (-not $path) { return $null }
    if (-not (Test-Path $path)) {
        NotFound "$label $path - existiert nicht"
        return $null
    }
    $blobsPath = Join-Path $path "blobs"
    $blobCount = 0
    $sizeBytes = 0
    if (Test-Path $blobsPath) {
        $items = Get-ChildItem -Path $blobsPath -File -ErrorAction SilentlyContinue
        $blobCount = @($items).Count
        $sizeBytes = ($items | Measure-Object -Property Length -Sum).Sum
    }
    $sizeGb = [math]::Round($sizeBytes / 1GB, 2)
    Found "$label $path - $blobCount Blob(s), $sizeGb GB"
    return @{ Path = $path; BlobCount = $blobCount; SizeGb = $sizeGb }
}

$defaultModelsPath = Join-Path $env:USERPROFILE ".ollama\models"
$envModelsPath = [Environment]::GetEnvironmentVariable("OLLAMA_MODELS", "User")

$defaultInfo = Describe-ModelDir "Standardpfad (C:):" $defaultModelsPath
if ($envModelsPath) {
    $envInfo = Describe-ModelDir "OLLAMA_MODELS-Pfad:" $envModelsPath
} else {
    NotFound "OLLAMA_MODELS ist nicht gesetzt."
    $envInfo = $null
}

if ($defaultInfo -and $envInfo -and $defaultInfo.BlobCount -gt 0 -and $envInfo.BlobCount -gt 0) {
    Warn "Zwei Modellablagen mit Inhalt gefunden - vermutlich die Doppelinstallation, " `
         "die aufgeraeumt werden sollte (siehe Abschnitt 4 unten)."
}

# --- 3) Vom laufenden Dienst tatsaechlich genutzte Modelle ------------------

Section "3. Vom Ollama-Dienst gemeldete Modelle (ollama list)"

try {
    ollama list
} catch {
    Warn "'ollama list' fehlgeschlagen - Dienst laeuft vermutlich nicht: $_"
}

# --- 4) Optionales, bestaetigtes Aufraeumen ---------------------------------

Section "4. Aufraeumen (optional, nur nach Bestaetigung)"

if (-not $defaultInfo -or $defaultInfo.BlobCount -eq 0) {
    Write-Host "Nichts zum Aufraeumen unter dem Standardpfad (C:) gefunden."
    exit 0
}

if ($envModelsPath -and (Resolve-Path $defaultModelsPath -ErrorAction SilentlyContinue).Path `
        -eq (Resolve-Path $envModelsPath -ErrorAction SilentlyContinue).Path) {
    Write-Host "Standardpfad entspricht dem OLLAMA_MODELS-Zielpfad - wird nie geloescht."
    exit 0
}

Write-Host "Gefunden: $($defaultInfo.Path) ($($defaultInfo.SizeGb) GB, $($defaultInfo.BlobCount) Blobs)"
Write-Host "Dieser Pfad ist NICHT der aktuelle OLLAMA_MODELS-Zielpfad und kann geloescht werden,"
Write-Host "sobald sichergestellt ist, dass alle benoetigten Modelle am neuen Ort vorhanden sind"
Write-Host "(ggf. vorher pruefen: 'ollama list' nach einem Dienst-Neustart mit OLLAMA_MODELS)."
$answer = Read-Host "Diesen alten Modellordner jetzt loeschen? (ja/nein)"
if ($answer -notin @("ja", "j", "yes", "y")) {
    Write-Host "Abgebrochen - keine Aenderung vorgenommen."
    exit 0
}

try {
    Remove-Item -Path $defaultInfo.Path -Recurse -Force
    Write-Host "[ OK ] Geloescht: $($defaultInfo.Path)"
} catch {
    Write-Host "[ FAIL ] Loeschen fehlgeschlagen: $_"
    exit 1
}

exit 0
