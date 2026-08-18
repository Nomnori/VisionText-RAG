from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    id: str
    source: str
    title: str
    chunk_index: int
    content: str
    score: float


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=10)


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]


class IngestResponse(BaseModel):
    files_processed: int
    chunks_indexed: int
    message: str


class HealthResponse(BaseModel):
    status: str
    llm_model: str
    embedding_model: str
    knowledge_files: int
    indexed_chunks: int
    cuda_available: bool = False
    gpu_name: str | None = None
    llm_device: str = "cpu"
    embedding_device: str = "cpu"
    llm_load_in_4bit: bool = False


class KnowledgeFileInfo(BaseModel):
    filename: str
    path: str
    size_bytes: int
