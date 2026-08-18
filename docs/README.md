# 项目文档索引

本目录存放 VisionText-RAG 的项目文档。**每次有意义的代码或配置修改，都应在 [`CHANGELOG.md`](./CHANGELOG.md) 追加摘要**，然后再 Git 提交推送。

## 文档列表

| 文件 | 用途 |
|------|------|
| [CHANGELOG.md](./CHANGELOG.md) | **变更摘要主文件** — 记录每次版本/改动的做了什么、为什么 |
| [GIT_COMMIT_CONVENTION.md](./GIT_COMMIT_CONVENTION.md) | Git 提交类型与 Commit Message 规范 |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 系统架构与模块说明 |

## 变更摘要写在哪里？

**不是**每个修改单独建一个文件，而是统一追加到 **`CHANGELOG.md`**：

```markdown
## [Unreleased]

### Added
- 新增了 xxx 功能，原因是 xxx

### Fixed
- 修复了 xxx 问题，原因是 xxx
```

发布或阶段性收尾时，将 `[Unreleased]` 下的内容归入版本号段落（如 `[0.1.2] - 2026-08-19`）。

## 推荐工作流

1. 完成代码修改
2. 在 `docs/CHANGELOG.md` 的 `[Unreleased]` 下写摘要（中文，说明做了什么）
3. 按 [GIT_COMMIT_CONVENTION.md](./GIT_COMMIT_CONVENTION.md) 提交
4. `git push origin main`

## 与 Git Commit 的关系

| 位置 | 内容 |
|------|------|
| `docs/CHANGELOG.md` | 给用户/团队看的**变更摘要**（中文，可稍详细） |
| Git Commit Message | 给版本历史看的**简短标题**（Conventional Commits 格式） |

两者应描述同一次改动，但 CHANGELOG 可以更详细。
