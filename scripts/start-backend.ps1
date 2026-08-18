$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$VenvPython = Join-Path $Backend ".venv\Scripts\python.exe"
$VenvPip = Join-Path $Backend ".venv\Scripts\pip.exe"
$Requirements = Join-Path $Backend "requirements.txt"
$Marker = Join-Path $Backend ".venv\.deps-installed"

Set-Location $Backend

if (-not (Test-Path $VenvPython)) {
    Write-Host "[setup] Creating virtual environment..."
    python -m venv .venv
}

if (-not (Test-Path $Marker)) {
    Write-Host "[setup] Installing Python dependencies (first run may take a few minutes)..."
    & $VenvPip install -r $Requirements
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[error] pip install failed. See output above." -ForegroundColor Red
        exit 1
    }
    New-Item -ItemType File -Path $Marker -Force | Out-Null
}

Write-Host "[backend] Starting API at http://127.0.0.1:8000 ..."
& $VenvPython run.py
