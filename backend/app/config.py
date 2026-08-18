from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_model_name: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
    llm_device: str = "auto"
    llm_load_in_4bit: bool = True
    llm_max_new_tokens: int = 1024
    llm_temperature: float = 0.3

    embedding_model_name: str = "BAAI/bge-small-zh-v1.5"
    embedding_device: str = "auto"

    vlm_model_name: str = "Qwen/Qwen2.5-VL-3B-Instruct"
    vlm_device: str = "auto"
    vlm_max_new_tokens: int = 512

    pdf_enabled: bool = True
    pdf_vlm_enabled: bool = True
    pdf_cache_dir: str = "./data/pdf_cache"

    chroma_persist_dir: str = "./chroma"
    chroma_collection: str = "visiontext_rag"

    knowledge_dir: str = "./knowledge"

    top_k: int = 4
    chunk_size: int = 600
    chunk_overlap: int = 80

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def knowledge_path(self) -> Path:
        path = Path(self.knowledge_dir)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path

    @property
    def chroma_path(self) -> Path:
        path = Path(self.chroma_persist_dir)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def resolve_model_path(self, model_name: str) -> str:
        path = Path(model_name)
        if path.is_absolute() and path.exists():
            return str(path)
        if model_name.startswith("./") or model_name.startswith(".\\"):
            local_path = PROJECT_ROOT / model_name[2:]
            if local_path.exists():
                return str(local_path)
        if (PROJECT_ROOT / model_name).exists():
            return str(PROJECT_ROOT / model_name)
        return model_name

    @property
    def llm_model_path(self) -> str:
        return self.resolve_model_path(self.llm_model_name)

    @property
    def embedding_model_path(self) -> str:
        return self.resolve_model_path(self.embedding_model_name)

    @property
    def vlm_model_path(self) -> str:
        return self.resolve_model_path(self.vlm_model_name)

    @property
    def pdf_cache_path(self) -> Path:
        path = Path(self.pdf_cache_dir)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
