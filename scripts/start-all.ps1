$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$BackendScript = Join-Path $Root "scripts\start-backend.ps1"
$FrontendScript = Join-Path $Root "scripts\start-frontend.ps1"

function Write-Info([string]$Message) {
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Warn([string]$Message) {
    Write-Host $Message -ForegroundColor Yellow
}

Write-Info "========================================"
Write-Info "  VisionText-RAG"
Write-Info "========================================"

if (-not (Test-Path (Join-Path $Root ".env"))) {
    Copy-Item (Join-Path $Root ".env.example") (Join-Path $Root ".env")
    Write-Warn "Created .env from .env.example"
}

$llmIndex = Join-Path $Root "models\DeepSeek-R1-Distill-Qwen-7B\model.safetensors.index.json"
$embeddingModel = Join-Path $Root "models\bge-small-zh-v1.5\model.safetensors"

if (-not (Test-Path $llmIndex) -or -not (Test-Path $embeddingModel)) {
    Write-Warn "Local models not found. Run: .\scripts\download-models.ps1"
}

Write-Info ""
Write-Info "Starting backend and frontend in separate windows..."
Write-Info "  Backend API : http://127.0.0.1:8000"
Write-Info "  Frontend UI : http://127.0.0.1:5173"
Write-Info ""

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $BackendScript
)

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $FrontendScript
)

Write-Info "Done. Check the new windows for logs."
Write-Info "Close those windows to stop the services."
