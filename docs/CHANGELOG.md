# 变更日志

本文件记录 VisionText-RAG 项目的所有重要变更。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

> 每次修改请先在本文件 `[Unreleased]` 段落追加摘要，再提交 Git。详见 [README.md](./README.md)。

## [Unreleased]

（暂无）

---

## [0.1.1] - 2026-08-19

### Fixed

- **本地模型路径解析**：从 `backend/` 目录启动时，`./models/` 被错误解析为 `backend/models/`，导致重建索引报 `Path not found`；现统一相对项目根目录解析
- **后端无法连接 (ECONNREFUSED)**：venv 依赖未安装完整（缺少 fastapi 等），后端窗口启动即退出；启动脚本增加首次依赖安装与失败提示
- **PowerShell 编码错误**：`start-all.ps1` 含中文时在 Windows PowerShell 5.1 下乱码导致脚本解析失败；改为英文输出

### Changed

- **启动脚本改进**：`start-backend.ps1` 首次运行自动 `pip install`，用 `.deps-installed` 标记避免重复安装
- **一键启动顺序**：`start-all.ps1` 等待 `/api/health` 就绪后再启动前端，避免前端代理报 ECONNREFUSED

---

## [0.1.0] - 2026-08-19

### Added

- **MVP 全栈 RAG 应用**
  - 后端：FastAPI + ChromaDB + DeepSeek-R1-Distill-Qwen-7B 本地推理
  - 前端：Vue 3 WebUI 聊天界面
  - Markdown 知识库导入、分块、向量索引与检索
  - 问答返回答案 + 引用来源（文件名、标题、片段、相关度）
- **项目基础设施**
  - 私人 GitHub 仓库初始化
  - `docs/GIT_COMMIT_CONVENTION.md` 提交规范
  - `docs/ARCHITECTURE.md` 架构说明
  - `knowledge/` 知识库目录、`models/` 本地模型目录（权重不进 Git）
- **脚本与工具**
  - `scripts/start-backend.ps1` / `scripts/start-frontend.ps1` 分服务启动
  - `start.bat` / `start.ps1` / `scripts/start-all.ps1` 一键启动
  - `scripts/download-models.ps1` 通过 hf-mirror.com 国内镜像下载模型

### Fixed

- **Pydantic schema 缺失**：`.gitignore` 中 `models/` 规则误忽略 `backend/app/models/`，导致 `schemas.py` 未提交
- **CHANGELOG 结构损坏**：MVP 提交后 CHANGELOG 标题层级错乱，已恢复

### Changed

- **`.gitignore` 优化**：改为 `/models/*` 忽略模型权重，保留 `models/README.md`
- **`.env.example`**：默认指向本地模型路径 `./models/...`

---

## 提交对照表

便于从 Git 历史回溯到本文件条目：

| Commit | 类型 | 摘要 |
|--------|------|------|
| `f507b08` | docs | 初始化私人仓库、docs 目录与提交规范 |
| `0d429cd` | feat | MVP：FastAPI + ChromaDB + LLM + Vue WebUI |
| `e0af2fa` | fix | 补提交缺失的 Pydantic schema |
| `463e248` | docs | 恢复 CHANGELOG 结构 |
| `993710b` | chore | 模型国内镜像下载脚本 + 本地路径配置 |
| `3f3ef21` | chore | 一键启动脚本 + 模型权重排除 Git |
| `24d44dd` | fix | start-all.ps1 PowerShell 编码修复 |
| `44b5ede` | fix | 后端启动与本地模型路径修复 |

---

## [0.0.1] - 2026-08-19（初始）

### Added

- 初始化私人 Git 仓库与 `docs/` 文档结构
- 添加 Git 提交规范说明
- 添加 `.gitignore`（Python、密钥、大文件、模型权重等）
