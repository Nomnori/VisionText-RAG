$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Pip = Join-Path $Backend ".venv\Scripts\pip.exe"
$Python = Join-Path $Backend ".venv\Scripts\python.exe"

Write-Host "[gpu] Uninstalling CPU-only PyTorch..."
cmd /c "`"$Pip`" uninstall -y torch torchvision torchaudio >nul 2>&1"

Write-Host "[gpu] Installing PyTorch cu128 (required for RTX 5070 / sm_120)..."
Write-Host "[gpu] This may take several minutes..."
& $Pip install --pre torch torchvision torchaudio `
    --index-url https://download.pytorch.org/whl/nightly/cu128 `
    --no-cache-dir

if ($LASTEXITCODE -ne 0) {
    Write-Host "[error] PyTorch GPU install failed." -ForegroundColor Red
    exit 1
}

Write-Host "[gpu] Installing bitsandbytes for 4bit quantization..."
& $Pip install bitsandbytes

Write-Host "[gpu] Verifying GPU..."
& $Python -c "import torch; print('cuda_available:', torch.cuda.is_available()); print('version:', torch.__version__); print('cuda_version:', torch.version.cuda); print('gpu:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'); print('capability:', torch.cuda.get_device_capability(0) if torch.cuda.is_available() else 'N/A')"

Write-Host "[gpu] Done. Restart the backend to use GPU."
