import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from app.config import get_settings

CONTENT_TYPES = ("text", "markdown", "table", "image")


@dataclass
class DocumentChunk:
    chunk_id: str
    source: str
    title: str
    chunk_index: int
    content: str
    content_type: str = "text"
    page_number: int | None = None
    file_type: str = "markdown"


@dataclass
class KnowledgeFile:
    path: Path
    file_type: str


@dataclass
class IngestStats:
    md_files: int = 0
    pdf_files: int = 0
    text_chunks: int = 0
    table_chunks: int = 0
    image_chunks: int = 0
    markdown_chunks: int = 0

    @property
    def total_files(self) -> int:
        return self.md_files + self.pdf_files

    @property
    def total_chunks(self) -> int:
        return self.text_chunks + self.table_chunks + self.image_chunks + self.markdown_chunks


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


def _make_chunk_id(source: str, chunk_index: int, content: str, content_type: str) -> str:
    raw = f"{source}:{content_type}:{chunk_index}:{content[:64]}"
    return hashlib.md5(raw.encode()).hexdigest()


def _split_text(
    content: str,
    source: str,
    title: str,
    *,
    content_type: str = "text",
    page_number: int | None = None,
    file_type: str = "markdown",
    start_index: int = 0,
) -> list[DocumentChunk]:
    settings = get_settings()
    chunk_size = settings.chunk_size
    chunk_overlap = settings.chunk_overlap

    content = _normalize_whitespace(content)
    if not content:
        return []

    chunks: list[DocumentChunk] = []
    start = 0
    chunk_index = start_index

    while start < len(content):
        end = min(start + chunk_size, len(content))
        if end < len(content):
            split_at = content.rfind("\n\n", start, end)
            if split_at > start + chunk_size // 2:
                end = split_at

        piece = content[start:end].strip()
        if piece:
            chunks.append(
                DocumentChunk(
                    chunk_id=_make_chunk_id(source, chunk_index, piece, content_type),
                    source=source,
                    title=title,
                    chunk_index=chunk_index,
                    content=piece,
                    content_type=content_type,
                    page_number=page_number,
                    file_type=file_type,
                )
            )
            chunk_index += 1

        if end >= len(content):
            break
        start = max(end - chunk_overlap, start + 1)

    return chunks


def _chunk_whole_segment(
    source: str,
    title: str,
    content: str,
    content_type: str,
    page_number: int | None,
    file_type: str,
    start_index: int,
) -> tuple[list[DocumentChunk], int]:
    if content_type in ("table", "image"):
        content = _normalize_whitespace(content)
        if not content:
            return [], start_index
        chunk = DocumentChunk(
            chunk_id=_make_chunk_id(source, start_index, content, content_type),
            source=source,
            title=title,
            chunk_index=start_index,
            content=content,
            content_type=content_type,
            page_number=page_number,
            file_type=file_type,
        )
        return [chunk], start_index + 1

    chunks = _split_text(
        content,
        source,
        title,
        content_type=content_type,
        page_number=page_number,
        file_type=file_type,
        start_index=start_index,
    )
    return chunks, start_index + len(chunks)


def load_markdown_files(knowledge_dir: Path | None = None) -> tuple[list[DocumentChunk], int]:
    settings = get_settings()
    root = knowledge_dir or settings.knowledge_path
    root.mkdir(parents=True, exist_ok=True)

    all_chunks: list[DocumentChunk] = []
    file_count = 0

    for md_path in sorted(root.rglob("*.md")):
        if md_path.name.startswith("."):
            continue
        file_count += 1
        content = md_path.read_text(encoding="utf-8")
        rel_source = str(md_path.relative_to(root)).replace("\\", "/")
        title = _extract_title(content, md_path.stem)
        all_chunks.extend(
            _split_text(
                content,
                rel_source,
                title,
                content_type="markdown",
                file_type="markdown",
            )
        )

    return all_chunks, file_count


def load_pdf_files(knowledge_dir: Path | None = None) -> tuple[list[DocumentChunk], int]:
    from app.services.pdf_parser import parse_pdf_file

    settings = get_settings()
    if not settings.pdf_enabled:
        return [], 0

    root = knowledge_dir or settings.knowledge_path
    if not root.exists():
        return [], 0

    all_chunks: list[DocumentChunk] = []
    file_count = 0
    chunk_index = 0

    for pdf_path in sorted(root.rglob("*.pdf")):
        if pdf_path.name.startswith("."):
            continue
        file_count += 1
        rel_source = str(pdf_path.relative_to(root)).replace("\\", "/")
        title = pdf_path.stem
        segments = parse_pdf_file(pdf_path, rel_source, title)

        for segment in segments:
            chunks, chunk_index = _chunk_whole_segment(
                source=segment.source,
                title=segment.title,
                content=segment.content,
                content_type=segment.content_type,
                page_number=segment.page_number,
                file_type="pdf",
                start_index=chunk_index,
            )
            all_chunks.extend(chunks)

    return all_chunks, file_count


def load_all_documents(knowledge_dir: Path | None = None) -> tuple[list[DocumentChunk], IngestStats]:
    md_chunks, md_files = load_markdown_files(knowledge_dir)
    pdf_chunks, pdf_files = load_pdf_files(knowledge_dir)
    chunks = md_chunks + pdf_chunks

    stats = IngestStats(md_files=md_files, pdf_files=pdf_files)
    for chunk in chunks:
        if chunk.content_type == "markdown":
            stats.markdown_chunks += 1
        elif chunk.content_type == "table":
            stats.table_chunks += 1
        elif chunk.content_type == "image":
            stats.image_chunks += 1
        else:
            stats.text_chunks += 1

    return chunks, stats


def list_knowledge_files(knowledge_dir: Path | None = None) -> list[KnowledgeFile]:
    settings = get_settings()
    root = knowledge_dir or settings.knowledge_path
    if not root.exists():
        return []

    files: list[KnowledgeFile] = []
    patterns = ["*.md"]
    if settings.pdf_enabled:
        patterns.append("*.pdf")

    for pattern in patterns:
        for path in sorted(root.rglob(pattern)):
            if path.name.startswith("."):
                continue
            file_type = "pdf" if path.suffix.lower() == ".pdf" else "markdown"
            files.append(KnowledgeFile(path=path, file_type=file_type))

    return sorted(files, key=lambda item: str(item.path))
