$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Mirror = "https://hf-mirror.com"
$VlmDir = Join-Path $Root "models\Qwen2.5-VL-3B-Instruct"
$VlmBase = "$Mirror/Qwen/Qwen2.5-VL-3B-Instruct/resolve/main"

$ExpectedSizes = @{
    "model-00001-of-00002.safetensors" = 3900000000
    "model-00002-of-00002.safetensors" = 3400000000
}

function Test-FileComplete {
    param([string]$Dest)
    $name = Split-Path $Dest -Leaf
    if (-not (Test-Path $Dest)) { return $false }
    $size = (Get-Item $Dest).Length
    if ($ExpectedSizes.ContainsKey($name)) {
        return $size -ge $ExpectedSizes[$name]
    }
    return $size -gt 0
}

function Download-File {
    param(
        [string]$Url,
        [string]$Dest,
        [int]$MaxRetries = 10
    )
    $dir = Split-Path $Dest -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }

    $name = Split-Path $Dest -Leaf
    if (Test-FileComplete $Dest) {
        $mb = [math]::Round((Get-Item $Dest).Length / 1MB, 1)
        Write-Host "[SKIP] $name (${mb} MB)"
        return
    }

    if ((Test-Path $Dest) -and -not (Test-FileComplete $Dest)) {
        Write-Host "[RESUME] $name (partial file, continuing...)"
    }

    for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
        Write-Host "[DOWN] $name (attempt $attempt/$MaxRetries) ..."
        curl.exe -L --retry 5 --retry-delay 8 -C - --connect-timeout 30 --max-time 7200 -o $Dest $Url
        if (Test-FileComplete $Dest) {
            $mb = [math]::Round((Get-Item $Dest).Length / 1MB, 1)
            Write-Host "[OK] $name (${mb} MB)"
            return
        }
        Write-Host "[WARN] $name incomplete, retry in 10s..."
        Start-Sleep -Seconds 10
    }
    throw "Download failed after $MaxRetries attempts: $name"
}

Write-Host "[vlm] Downloading Qwen2.5-VL-3B-Instruct from hf-mirror.com (~7.5 GB)"

$small = @(
    "config.json", "generation_config.json", "chat_template.json",
    "preprocessor_config.json", "tokenizer.json", "tokenizer_config.json",
    "merges.txt", "vocab.json", "model.safetensors.index.json"
)
foreach ($f in $small) { Download-File "$VlmBase/$f" "$VlmDir\$f" -MaxRetries 5 }

foreach ($f in @("model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors")) {
    Download-File "$VlmBase/$f" "$VlmDir\$f" -MaxRetries 15
}

Write-Host "[vlm] Done. Set VLM_MODEL_NAME=./models/Qwen2.5-VL-3B-Instruct in .env"
