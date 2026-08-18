$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Frontend = Join-Path $Root "frontend"

Set-Location $Frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "[setup] Installing frontend dependencies..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[error] npm install failed." -ForegroundColor Red
        exit 1
    }
}

Write-Host "[frontend] Starting WebUI at http://127.0.0.1:5173 ..."
npm run dev
