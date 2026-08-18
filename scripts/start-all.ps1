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
Write-Info "  VisionText-RAG 一键启动"
Write-Info "========================================"

if (-not (Test-Path (Join-Path $Root ".env"))) {
    Copy-Item (Join-Path $Root ".env.example") (Join-Path $Root ".env")
    Write-Warn "已根据 .env.example 创建 .env"
}

$llmIndex = Join-Path $Root "models\DeepSeek-R1-Distill-Qwen-7B\model.safetensors.index.json"
$embeddingModel = Join-Path $Root "models\bge-small-zh-v1.5\model.safetensors"

if (-not (Test-Path $llmIndex) -or -not (Test-Path $embeddingModel)) {
    Write-Warn "未检测到本地模型，请先运行: .\scripts\download-models.ps1"
}

Write-Info ""
Write-Info "正在启动服务（各开一个独立窗口）..."
Write-Info "  后端 API : http://127.0.0.1:8000"
Write-Info "  前端 WebUI: http://127.0.0.1:5173"
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

Write-Info "启动命令已发送。请在新窗口中查看运行日志。"
Write-Info "关闭对应窗口即可停止服务。"
