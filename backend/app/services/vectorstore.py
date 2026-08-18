from functools import lru_cache

import chromadb
from chromadb.api.models.Collection import Collection

from app.config import get_settings
from app.services.embeddings import embed_texts
from app.services.ingestion import DocumentChunk


@lru_cache
def get_chroma_client() -> chromadb.PersistentClient:
    settings = get_settings()
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(settings.chroma_path))


def get_collection() -> Collection:
    settings = get_settings()
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=settings.chroma_collection,
        metadata={"hnsw:space": "cosine"},
    )


def count_indexed_chunks() -> int:
    collection = get_collection()
    return collection.count()


def clear_collection() -> None:
    settings = get_settings()
    client = get_chroma_client()
    try:
        client.delete_collection(settings.chroma_collection)
    except ValueError:
        pass

def index_chunks(chunks: list[DocumentChunk]) -> int:
    if not chunks:
        clear_collection()
        return 0

    collection = get_collection()
    clear_collection()
    collection = get_collection()

    batch_size = 32
    indexed = 0

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        embeddings = embed_texts([chunk.content for chunk in batch])
        collection.add(
            ids=[chunk.chunk_id for chunk in batch],
            documents=[chunk.content for chunk in batch],
            embeddings=embeddings,
            metadatas=[
                {
                    "source": chunk.source,
                    "title": chunk.title,
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in batch
            ],
        )
        indexed += len(batch)

    return indexed


def query_similar(query: str, top_k: int) -> list[dict]:
    collection = get_collection()
    if collection.count() == 0:
        return []

    query_embedding = embed_texts([query])[0]
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    hits: list[dict] = []
    ids = result.get("ids", [[]])[0]
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    for idx, doc_id in enumerate(ids):
        metadata = metadatas[idx] or {}
        distance = distances[idx] if idx < len(distances) else 1.0
        score = max(0.0, 1.0 - distance)
        hits.append(
            {
                "id": doc_id,
                "source": metadata.get("source", "unknown"),
                "title": metadata.get("title", metadata.get("source", "unknown")),
                "chunk_index": int(metadata.get("chunk_index", 0)),
                "content": documents[idx] or "",
                "score": round(score, 4),
            }
        )

    return hits
