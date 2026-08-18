from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    IngestResponse,
    KnowledgeFileInfo,
)
from app.services.device import get_runtime_devices
from app.services.ingestion import list_knowledge_files
from app.services.rag import chat_with_citations, ingest_knowledge_base
from app.services.vectorstore import count_indexed_chunks

router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    files = list_knowledge_files()
    runtime = get_runtime_devices()
    return HealthResponse(
        status="ok",
        llm_model=settings.llm_model_name,
        embedding_model=settings.embedding_model_name,
        knowledge_files=len(files),
        indexed_chunks=count_indexed_chunks(),
        cuda_available=runtime["cuda_available"],
        gpu_name=runtime.get("device_name"),
        llm_device=runtime["llm_device"],
        embedding_device=runtime["embedding_device"],
        llm_load_in_4bit=runtime["llm_load_in_4bit"],
    )


@router.get("/knowledge", response_model=list[KnowledgeFileInfo])
def knowledge_files() -> list[KnowledgeFileInfo]:
    settings = get_settings()
    files = list_knowledge_files()
    return [
        KnowledgeFileInfo(
            filename=path.name,
            path=str(path.relative_to(settings.knowledge_path)).replace("\\", "/"),
            size_bytes=path.stat().st_size,
        )
        for path in files
    ]


@router.post("/ingest", response_model=IngestResponse)
def ingest() -> IngestResponse:
    try:
        return ingest_knowledge_base()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    try:
        return chat_with_citations(question, payload.top_k)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
