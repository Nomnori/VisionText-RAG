from app.config import get_settings
from app.models.schemas import ChatResponse, IngestResponse, SourceCitation
from app.services.ingestion import load_markdown_files
from app.services.llm import get_llm_service
from app.services.vectorstore import count_indexed_chunks, index_chunks, query_similar

SYSTEM_PROMPT = """你是一个基于知识库回答问题的助手。
请严格依据提供的参考资料作答；如果资料不足以回答，请明确说明不知道，不要编造。
回答末尾请列出引用编号，例如：[1][2]。"""


def _build_context(sources: list[dict]) -> str:
    blocks: list[str] = []
    for index, source in enumerate(sources, start=1):
        blocks.append(
            f"[{index}] 来源: {source['source']} | 标题: {source['title']}\n{source['content']}"
        )
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
    chunks = load_markdown_files()
    indexed = index_chunks(chunks)
    files = len({chunk.source for chunk in chunks})

    if indexed == 0:
        message = "知识库目录为空，请将 .md 文件放入 knowledge/ 后重新索引。"
    else:
        message = f"已成功索引 {files} 个 Markdown 文件，共 {indexed} 个文本块。"

    return IngestResponse(files_processed=files, chunks_indexed=indexed, message=message)


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
        )
        for hit in hits
    ]

    return ChatResponse(answer=answer, sources=sources)
