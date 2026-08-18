$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$BackendScript = Join-Path $Root "scripts\start-backend.ps1"
$FrontendScript = Join-Path $Root "scripts\start-frontend.ps1"
$HealthUrl = "http://127.0.0.1:8000/api/health"

function Write-Info([string]$Message) {
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Warn([string]$Message) {
    Write-Host $Message -ForegroundColor Yellow
}

function Wait-ForBackend {
    param([int]$TimeoutSeconds = 120)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 3
            if ($response.StatusCode -eq 200) {
                return $true
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    return $false
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
Write-Info "Starting backend..."
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $BackendScript
)

Write-Info "Waiting for backend to become ready..."
if (-not (Wait-ForBackend)) {
    Write-Warn "Backend did not respond within 120s."
    Write-Warn "Check the backend window for errors, then start frontend manually."
    exit 1
}

Write-Info "Backend is ready: $HealthUrl"
Write-Info "Starting frontend..."
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $FrontendScript
)

Write-Info ""
Write-Info "  Backend API : http://127.0.0.1:8000"
Write-Info "  Frontend UI : http://127.0.0.1:5173"
Write-Info ""
Write-Info "Done. To stop all services, run: .\stop.bat"
