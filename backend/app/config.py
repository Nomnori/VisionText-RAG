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


@lru_cache
def get_settings() -> Settings:
    return Settings()
