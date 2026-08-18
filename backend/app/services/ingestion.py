import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from app.config import get_settings


@dataclass
class DocumentChunk:
    chunk_id: str
    source: str
    title: str
    chunk_index: int
    content: str


def _extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return fallback


def _normalize_whitespace(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_markdown(content: str, source: str, title: str) -> list[DocumentChunk]:
    settings = get_settings()
    chunk_size = settings.chunk_size
    chunk_overlap = settings.chunk_overlap

    content = _normalize_whitespace(content)
    if not content:
        return []

    chunks: list[DocumentChunk] = []
    start = 0
    chunk_index = 0

    while start < len(content):
        end = min(start + chunk_size, len(content))
        if end < len(content):
            split_at = content.rfind("\n\n", start, end)
            if split_at > start + chunk_size // 2:
                end = split_at

        piece = content[start:end].strip()
        if piece:
            chunk_id = hashlib.md5(f"{source}:{chunk_index}:{piece[:64]}".encode()).hexdigest()
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    source=source,
                    title=title,
                    chunk_index=chunk_index,
                    content=piece,
                )
            )
            chunk_index += 1

        if end >= len(content):
            break
        start = max(end - chunk_overlap, start + 1)

    return chunks


def load_markdown_files(knowledge_dir: Path | None = None) -> list[DocumentChunk]:
    settings = get_settings()
    root = knowledge_dir or settings.knowledge_path
    root.mkdir(parents=True, exist_ok=True)

    all_chunks: list[DocumentChunk] = []
    for md_path in sorted(root.rglob("*.md")):
        if md_path.name.startswith("."):
            continue
        content = md_path.read_text(encoding="utf-8")
        rel_source = str(md_path.relative_to(root)).replace("\\", "/")
        title = _extract_title(content, md_path.stem)
        all_chunks.extend(_split_markdown(content, rel_source, title))

    return all_chunks


def list_knowledge_files(knowledge_dir: Path | None = None) -> list[Path]:
    settings = get_settings()
    root = knowledge_dir or settings.knowledge_path
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.md") if not path.name.startswith("."))
