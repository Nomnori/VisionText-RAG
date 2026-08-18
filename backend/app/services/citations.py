MODALITY_LABELS = {
    "text": "文本",
    "markdown": "Markdown",
    "table": "表格",
    "image": "图片描述",
}


def modality_label(content_type: str) -> str:
    return MODALITY_LABELS.get(content_type, content_type)
