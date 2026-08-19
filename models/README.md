# 本地模型目录

此目录用于存放从 HuggingFace / hf-mirror 下载的模型权重，**不会也不应提交到 Git**。

## 目录结构

```
models/
├── DeepSeek-R1-Distill-Qwen-7B/   # LLM 问答（约 15 GB）
├── bge-small-zh-v1.5/             # Embedding（约 96 MB）
└── Qwen2.5-VL-3B-Instruct/        # PDF 图片描述 VLM（约 6 GB，可选）
```

## 下载模型

```powershell
# 全部模型（LLM + Embedding + VLM）
.\scripts\download-models.ps1

# 仅下载 VLM
.\scripts\download-vlm.ps1
```

## 配置

下载完成后，`.env` 中应指向本地路径：

```env
LLM_MODEL_NAME=./models/DeepSeek-R1-Distill-Qwen-7B
EMBEDDING_MODEL_NAME=./models/bge-small-zh-v1.5
VLM_MODEL_NAME=./models/Qwen2.5-VL-3B-Instruct
```
