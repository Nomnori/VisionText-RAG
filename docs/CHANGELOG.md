# 变更日志

本文件记录 VisionText-RAG 项目的所有重要变更。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

## [Unreleased]

## [0.1.0] - 2026-08-19

### Added

- MVP 后端：FastAPI + ChromaDB + DeepSeek-R1-Distill-Qwen-7B 本地 RAG
- Markdown 知识库导入、分块索引与向量检索
- 问答 API 返回答案及引用来源（文件名、标题、片段、相关度）
- Vue 3 WebUI：聊天界面、索引重建、引用来源展示
- 启动脚本 `scripts/start-backend.ps1` 与 `scripts/start-frontend.ps1`
- 架构文档 `docs/ARCHITECTURE.md`
- `knowledge/` 目录用于存放 Markdown 知识库

### Fixed

- 修复 `.gitignore` 误忽略 `backend/app/models/` 导致 schema 未提交

### Added (initial)

- 初始化私人 Git 仓库与项目文档结构
- 添加 `docs/GIT_COMMIT_CONVENTION.md` 提交规范说明
- 添加 `.gitignore` 忽略常见 Python、密钥与大文件目录
