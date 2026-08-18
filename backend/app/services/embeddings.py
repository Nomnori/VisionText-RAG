from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.services.device import resolve_device


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    settings = get_settings()
    device = resolve_device(settings.embedding_device)
    return SentenceTransformer(settings.embedding_model_path, device=device)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()
