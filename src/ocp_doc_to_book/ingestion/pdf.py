from __future__ import annotations


def resolve_pdf_capture(uri: str) -> tuple[str, str]:
    normalized = (uri or "").strip()
    return normalized, "pdf_text_extract_v1"
