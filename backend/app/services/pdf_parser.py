import logging
from dataclasses import dataclass
from pathlib import Path

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class PdfSegment:
    source: str
    title: str
    content: str
    content_type: str
    page_number: int | None = None


def _page_number_from_item(item) -> int | None:
    if hasattr(item, "prov") and item.prov:
        first = item.prov[0]
        page_no = getattr(first, "page_no", None)
        if page_no is not None:
            return int(page_no)
    return None


def _extract_table_content(item, doc) -> str:
    for method_name in ("export_to_markdown", "to_markdown"):
        method = getattr(item, method_name, None)
        if callable(method):
            try:
                return method(doc=doc)
            except TypeError:
                return method()
    if hasattr(item, "text") and item.text:
        return str(item.text)
    return ""


def _save_picture(item, doc, image_dir: Path, source: str, index: int):
    image_dir.mkdir(parents=True, exist_ok=True)
    image_path = image_dir / f"{Path(source).stem}_img_{index}.png"

    if hasattr(item, "get_image"):
        image = item.get_image(doc)
        if image is not None:
            image.save(image_path)
            return image_path

    return None


def parse_pdf_file(pdf_path: Path, rel_source: str, title: str) -> list[PdfSegment]:
    settings = get_settings()

    try:
        from docling.document_converter import DocumentConverter
    except ImportError as exc:
        raise RuntimeError("未安装 docling，请运行: pip install docling") from exc

    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))
    doc = result.document

    segments: list[PdfSegment] = []
    image_dir = settings.pdf_cache_path / Path(rel_source).stem
    image_index = 0

    try:
        from docling_core.types.doc import PictureItem, TableItem, TextItem
    except ImportError:
        TextItem = TableItem = PictureItem = tuple()

    vlm = None
    if settings.pdf_vlm_enabled:
        from app.services.vlm import get_vlm_service

        vlm = get_vlm_service()

    for item, _level in doc.iterate_items():
        page_number = _page_number_from_item(item)

        if TableItem and isinstance(item, TableItem):
            table_text = _extract_table_content(item, doc)
            if table_text.strip():
                segments.append(
                    PdfSegment(
                        source=rel_source,
                        title=f"{title} · 表格",
                        content=f"[表格]\n{table_text.strip()}",
                        content_type="table",
                        page_number=page_number,
                    )
                )
            continue

        if PictureItem and isinstance(item, PictureItem):
            if not settings.pdf_vlm_enabled or vlm is None:
                continue
            image_path = _save_picture(item, doc, image_dir, rel_source, image_index)
            image_index += 1
            if image_path is None or not image_path.exists():
                continue
            try:
                description = vlm.describe_image(str(image_path))
            except Exception as exc:  # noqa: BLE001
                logger.warning("VLM failed for %s: %s", image_path, exc)
                continue
            if description.strip():
                page_label = f"第 {page_number} 页" if page_number else "未知页"
                segments.append(
                    PdfSegment(
                        source=rel_source,
                        title=f"{title} · 图片 ({page_label})",
                        content=f"[图片描述]\n{description.strip()}",
                        content_type="image",
                        page_number=page_number,
                    )
                )
            continue

        if TextItem and isinstance(item, TextItem):
            text = getattr(item, "text", "") or ""
            if text.strip():
                segments.append(
                    PdfSegment(
                        source=rel_source,
                        title=title,
                        content=text.strip(),
                        content_type="text",
                        page_number=page_number,
                    )
                )

    if not segments:
        markdown = doc.export_to_markdown()
        if markdown.strip():
            segments.append(
                PdfSegment(
                    source=rel_source,
                    title=title,
                    content=markdown.strip(),
                    content_type="text",
                    page_number=1,
                )
            )

    if vlm is not None:
        from app.services.vlm import unload_vlm_service

        unload_vlm_service()

    return segments
