from app.config import get_settings
from app.models.schemas import ChatResponse, IngestResponse, SourceCitation
from app.services.ingestion import load_all_documents
from app.services.llm import get_llm_service
from app.services.vectorstore import count_indexed_chunks, index_chunks, query_similar

SYSTEM_PROMPT = """你是一个基于知识库回答问题的助手。
知识库包含 Markdown 文档，以及 PDF 中提取的文本、表格和图片描述。
请严格依据提供的参考资料作答；如果资料不足以回答，请明确说明不知道，不要编造。
回答末尾请列出引用编号，例如：[1][2]。"""


def _format_source_line(index: int, source: dict) -> str:
    parts = [f"[{index}] 来源: {source['source']}"]
    parts.append(f"类型: {source.get('modality_label', '文本')}")
    if source.get("page_number"):
        parts.append(f"页码: {source['page_number']}")
    parts.append(f"标题: {source['title']}")
    return " | ".join(parts)


def _build_context(sources: list[dict]) -> str:
    blocks: list[str] = []
    for index, source in enumerate(sources, start=1):
        header = _format_source_line(index, source)
        blocks.append(f"{header}\n{source['content']}")
    return "\n\n".join(blocks)


def _build_prompt(question: str, sources: list[dict]) -> str:
    if not sources:
        return (
            f"{SYSTEM_PROMPT}\n\n"
            "当前知识库中没有检索到相关资料。\n"
            f"用户问题：{question}\n"
            "请礼貌地说明无法从知识库中找到答案。"
        )

    context = _build_context(sources)
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"参考资料：\n{context}\n\n"
        f"用户问题：{question}\n"
        "请给出简洁、准确的中文回答，并在正文中使用 [1]、[2] 等标注引用。"
    )


def ingest_knowledge_base() -> IngestResponse:
    chunks, stats = load_all_documents()
    indexed = index_chunks(chunks)

    if indexed == 0:
        message = "知识库目录为空，请将 .md 或 .pdf 文件放入 knowledge/ 后重新索引。"
    else:
        parts = [f"共索引 {stats.total_files} 个文件、{indexed} 个块"]
        if stats.md_files:
            parts.append(f"Markdown {stats.md_files} 个")
        if stats.pdf_files:
            parts.append(f"PDF {stats.pdf_files} 个")
        detail = []
        if stats.markdown_chunks:
            detail.append(f"MD {stats.markdown_chunks}")
        if stats.text_chunks:
            detail.append(f"文本 {stats.text_chunks}")
        if stats.table_chunks:
            detail.append(f"表格 {stats.table_chunks}")
        if stats.image_chunks:
            detail.append(f"图片 {stats.image_chunks}")
        if detail:
            parts.append(f"({' / '.join(detail)})")
        message = f"已成功索引：{'，'.join(parts)}。"

    return IngestResponse(
        files_processed=stats.total_files,
        chunks_indexed=indexed,
        md_files=stats.md_files,
        pdf_files=stats.pdf_files,
        text_chunks=stats.text_chunks,
        table_chunks=stats.table_chunks,
        image_chunks=stats.image_chunks,
        markdown_chunks=stats.markdown_chunks,
        message=message,
    )


def chat_with_citations(question: str, top_k: int | None = None) -> ChatResponse:
    settings = get_settings()
    k = top_k or settings.top_k

    if count_indexed_chunks() == 0:
        ingest_knowledge_base()

    hits = query_similar(question, k)
    prompt = _build_prompt(question, hits)
    answer = get_llm_service().generate(prompt)

    sources = [
        SourceCitation(
            id=hit["id"],
            source=hit["source"],
            title=hit["title"],
            chunk_index=hit["chunk_index"],
            content=hit["content"],
            score=hit["score"],
            content_type=hit.get("content_type", "text"),
            file_type=hit.get("file_type", "markdown"),
            page_number=hit.get("page_number"),
            modality_label=hit.get("modality_label", "文本"),
        )
        for hit in hits
    ]

    return ChatResponse(answer=answer, sources=sources)
