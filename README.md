# VisionText-RAG

基于 Markdown 知识库的本地 RAG 问答 MVP，使用 **DeepSeek-R1-Distill-Qwen-7B** + **ChromaDB** + **FastAPI** + **Vue 3 WebUI**，回答附带引用来源。

## 架构

```
VisionText-RAG/
├── backend/          # FastAPI + RAG 服务
├── frontend/         # Vue 3 WebUI
├── knowledge/        # Markdown 知识库（放入 .md 文件）
├── models/           # 本地模型权重（不提交 Git，见 models/README.md）
├── chroma/           # ChromaDB 持久化（自动生成，不提交 Git）
└── docs/             # 项目文档
```

## 功能

- 本地 LLM 推理（DeepSeek-R1-Distill-Qwen-7B，支持 4bit 量化）
- ChromaDB 向量检索
- Markdown 知识库导入与分块索引
- 问答回答 + **引用来源**（文件名、标题、相关度、原文片段）
- Vue WebUI 聊天界面

## 环境要求

- Python 3.10+
- Node.js 18+
- 推荐 NVIDIA GPU（8GB+ 显存，4bit 量化）；CPU 可运行但较慢
- 模型需先下载到 `models/`（约 15 GB，**不会上传到 Git**）

## 快速开始

### 1. 下载模型（首次）

```powershell
.\scripts\download-models.ps1
```

### 2. 配置环境变量

```powershell
copy .env.example .env
```

按需修改 `.env` 中的模型路径、设备、端口等。

### 3. 一键启动

双击 `start.bat`，或在项目根目录运行：

```powershell
.\start.ps1
```

将自动打开两个窗口：后端 API（8000）+ 前端 WebUI（5173）。

也可分别启动：

```powershell
.\scripts\start-backend.ps1   # 终端 1
.\scripts\start-frontend.ps1  # 终端 2
```

### 4. 导入知识库

1. 将 `.md` 文件放入 `knowledge/` 目录
2. 在 WebUI 左侧点击 **重建索引**
3. 开始提问

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查与索引状态 |
| GET | `/api/knowledge` | 列出知识库 Markdown 文件 |
| POST | `/api/ingest` | 重建向量索引 |
| POST | `/api/chat` | 问答（返回答案 + 引用来源） |

## 文档

- [文档索引与摘要说明](./docs/README.md)
- [变更日志（每次修改摘要）](./docs/CHANGELOG.md)
- [Git 提交规范](./docs/GIT_COMMIT_CONVENTION.md)
- [架构说明](./docs/ARCHITECTURE.md)

## 开发约定

每次修改请：

1. 更新 [`docs/CHANGELOG.md`](./docs/CHANGELOG.md)
2. 按 Conventional Commits 规范提交并推送

## 仓库信息

- **远程**: https://github.com/Nomnori/VisionText-RAG （Private）
- **维护者**: Nomnori
