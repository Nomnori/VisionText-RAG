# 知识库目录

将 **Markdown（`.md`）** 或 **PDF（`.pdf`）** 文件放在此目录或其子目录中。

## 支持格式

| 格式 | 处理方式 |
|------|----------|
| `.md` | 直接分块 → Embedding → ChromaDB |
| `.pdf` | Docling 解析 → 文本/表格/图片分流 → VLM 描述图片 → Embedding → ChromaDB |

## PDF 处理流程

```
PDF
 ├─ 文本   → Embedding
 ├─ 表格   → 结构化 Markdown → Embedding
 └─ 图片   → Qwen2.5-VL 描述 → Embedding
                ↓
            ChromaDB → RAG → 本地 LLM
```

## 使用步骤

1. 将 `.md` / `.pdf` 文件复制到 `knowledge/` 目录
2. 启动后端与前端
3. 在 WebUI 左侧点击 **重建索引**
4. 在聊天框中提问，引用来源会标注类型（文本/表格/图片描述）和页码

## 建议

- PDF 首次索引较慢（需 Docling 解析 + VLM 图片描述）
- 图片较多的 PDF 建议确保 VLM 模型已下载并启用 `PDF_VLM_ENABLED=true`
- Markdown 文件仍支持子目录组织
