from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    id: str
    source: str
    title: str
    chunk_index: int
    content: str
    score: float
    content_type: str = "text"
    file_type: str = "markdown"
    page_number: int | None = None
    modality_label: str = "文本"


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=10)


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]


class IngestResponse(BaseModel):
    files_processed: int
    chunks_indexed: int
    md_files: int = 0
    pdf_files: int = 0
    text_chunks: int = 0
    table_chunks: int = 0
    image_chunks: int = 0
    markdown_chunks: int = 0
    message: str


class HealthResponse(BaseModel):
    status: str
    llm_model: str
    embedding_model: str
    vlm_model: str
    knowledge_files: int
    pdf_files: int = 0
    md_files: int = 0
    indexed_chunks: int
    cuda_available: bool = False
    gpu_name: str | None = None
    llm_device: str = "cpu"
    embedding_device: str = "cpu"
    vlm_device: str = "cpu"
    llm_load_in_4bit: bool = False
    pdf_enabled: bool = True
    pdf_vlm_enabled: bool = True


class KnowledgeFileInfo(BaseModel):
    filename: str
    path: str
    size_bytes: int
    file_type: str
