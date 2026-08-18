# Git 提交规范

本项目采用 [Conventional Commits](https://www.conventionalcommits.org/) 规范，每次提交必须包含**类型**、**摘要**，必要时附带**正文**说明。

## 提交格式

```
<type>(<scope>): <summary>

[optional body]

[optional footer]
```

### 示例

```
feat(rag): add multimodal document ingestion pipeline

docs: update CHANGELOG for v0.1.0 setup

fix(retrieval): handle empty embedding results gracefully
```

## 提交类型 (type)

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 仅文档变更 |
| `style` | 代码格式（不影响逻辑，如空格、分号） |
| `refactor` | 重构（非新功能、非修复） |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `build` | 构建系统或外部依赖变更 |
| `ci` | CI/CD 配置变更 |
| `chore` | 其他杂项（不影响源码与测试） |
| `revert` | 回滚某次提交 |

## 摘要 (summary) 要求

- 使用**中文或英文**均可，团队内保持一致即可
- 简明扼要，说明**做了什么**以及**为什么**（如适用）
- 不超过 72 个字符
- 不以句号结尾
- 使用祈使语气（如「添加」「修复」「更新」）

## 可选范围 (scope)

scope 表示影响模块，例如：

- `rag` — RAG 核心逻辑
- `ocr` — 文字/图像识别
- `embedding` — 向量嵌入
- `retrieval` — 检索模块
- `api` — 接口层
- `ui` — 前端界面
- `docs` — 文档

## 变更摘要记录

每次有意义的修改，除 Git Commit 外，还应在 [`CHANGELOG.md`](./CHANGELOG.md) 的 **`[Unreleased]`** 段落追加条目。

摘要写在哪里？→ **只有一个文件**：`docs/CHANGELOG.md`（不是每个修改单独建文件）。  
文档索引见 [`docs/README.md`](./README.md)。

## 工作流程

1. 完成代码或文档修改
2. 在 `docs/CHANGELOG.md` 追加变更摘要
3. 按规范撰写 Commit Message 并提交
4. 推送到远程私人仓库

```bash
git add .
git commit -m "feat(rag): 添加 PDF 文档解析入口"
git push origin main
```

## 本机 Git 身份

提交时使用全局配置（无需在仓库内重复设置）：

- **用户名**: Nomnori
- **邮箱**: 2220771440@qq.com
