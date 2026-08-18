$ErrorActionPreference = "Stop"
$Root = "g:\development\AIprojects\VisionText-RAG\models"
$Mirror = "https://hf-mirror.com"

function Download-File {
    param(
        [string]$Url,
        [string]$Dest
    )
    $dir = Split-Path $Dest -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    if ((Test-Path $Dest) -and ((Get-Item $Dest).Length -gt 0)) {
        Write-Host "[SKIP] $(Split-Path $Dest -Leaf) already exists"
        return
    }
    Write-Host "[DOWN] $(Split-Path $Dest -Leaf) ..."
    curl.exe -L --retry 5 --retry-delay 3 -C - -o $Dest $Url
    if ($LASTEXITCODE -ne 0) {
        throw "Download failed: $Url"
    }
}

# --- Embedding: bge-small-zh-v1.5 (~96 MB) ---
$BgeBase = "$Mirror/BAAI/bge-small-zh-v1.5/resolve/main"
$BgeDir = "$Root/bge-small-zh-v1.5"
$BgeFiles = @(
    "config.json",
    "config_sentence_transformers.json",
    "modules.json",
    "sentence_bert_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.txt",
    "special_tokens_map.json",
    "model.safetensors"
)
foreach ($f in $BgeFiles) {
    Download-File "$BgeBase/$f" "$BgeDir/$f"
}
Download-File "$BgeBase/1_Pooling/config.json" "$BgeDir/1_Pooling/config.json"

Write-Host "[DONE] bge-small-zh-v1.5 complete"

# --- LLM: DeepSeek-R1-Distill-Qwen-7B (~15 GB) ---
$LlmBase = "$Mirror/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B/resolve/main"
$LlmDir = "$Root/DeepSeek-R1-Distill-Qwen-7B"
$LlmSmall = @(
    "config.json",
    "generation_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "model.safetensors.index.json"
)
foreach ($f in $LlmSmall) {
    Download-File "$LlmBase/$f" "$LlmDir/$f"
}

$LlmBig = @(
    "model-00001-of-000002.safetensors",
    "model-00002-of-000002.safetensors"
)
foreach ($f in $LlmBig) {
    Download-File "$LlmBase/$f" "$LlmDir/$f"
}

Write-Host "[DONE] All models downloaded to $Root"
