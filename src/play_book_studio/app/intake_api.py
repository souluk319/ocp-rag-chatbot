"""doc-to-book draft lifecycle API 보조 로직."""

from __future__ import annotations

import base64
import re
import uuid
from pathlib import Path
from typing import Any

from play_book_studio.intake import DocSourceRequest, DocToBookDraftStore, DocToBookPlanner
from play_book_studio.intake.capture.service import DocToBookCaptureService
from play_book_studio.intake.normalization.service import DocToBookNormalizeService
from play_book_studio.config.settings import load_settings


def build_doc_to_book_plan(payload: dict[str, Any]) -> dict[str, Any]:
    request = doc_to_book_request_from_payload(payload)
    return DocToBookPlanner().plan(request).to_dict()


def doc_to_book_request_from_payload(payload: dict[str, Any]) -> DocSourceRequest:
    source_type = str(payload.get("source_type") or "").strip().lower()
    uri = str(payload.get("uri") or "").strip()
    title = str(payload.get("title") or "").strip()
    language_hint = str(payload.get("language_hint") or "ko").strip() or "ko"

    if source_type not in {"web", "pdf"}:
        raise ValueError("source_type은 web 또는 pdf여야 합니다.")
    if not uri:
        raise ValueError("uri가 필요합니다.")

    return DocSourceRequest(
        source_type=source_type,
        uri=uri,
        title=title,
        language_hint=language_hint,
    )


def create_doc_to_book_draft(root_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    request = doc_to_book_request_from_payload(payload)
    record = DocToBookDraftStore(root_dir).create(request)
    return record.to_dict()


def upload_doc_to_book_draft(root_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    request = doc_to_book_request_from_payload(payload)
    file_name = str(payload.get("file_name") or "").strip()
    content_base64 = str(payload.get("content_base64") or "").strip()
    if not file_name:
        raise ValueError("업로드할 file_name이 필요합니다.")
    if not content_base64:
        raise ValueError("업로드할 content_base64가 필요합니다.")

    try:
        content = base64.b64decode(content_base64.encode("utf-8"), validate=True)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"업로드 파일 디코딩에 실패했습니다: {exc}") from exc
    if not content:
        raise ValueError("빈 파일은 업로드할 수 없습니다.")

    settings = load_settings(root_dir)
    upload_dir = settings.doc_to_book_capture_dir / "_uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    source_suffix = Path(file_name).suffix or (".pdf" if request.source_type == "pdf" else ".html")
    safe_stem = re.sub(r"[^A-Za-z0-9가-힣._-]+", "-", Path(file_name).stem).strip("-") or "upload"
    target = upload_dir / f"{uuid.uuid4().hex[:10]}-{safe_stem}{source_suffix}"
    target.write_bytes(content)

    uploaded_request = DocSourceRequest(
        source_type=request.source_type,
        uri=str(target),
        title=request.title or Path(file_name).stem,
        language_hint=request.language_hint,
    )
    store = DocToBookDraftStore(root_dir)
    record = store.create(uploaded_request)
    record.uploaded_file_name = file_name
    record.uploaded_file_path = str(target)
    record.uploaded_byte_size = len(content)
    store.save(record)
    return record.to_dict()


def load_doc_to_book_draft(root_dir: Path, draft_id: str) -> dict[str, Any] | None:
    record = DocToBookDraftStore(root_dir).get(draft_id)
    if record is None:
        return None
    return record.to_dict()


def capture_doc_to_book_draft(root_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    draft_id = str(payload.get("draft_id") or "").strip()
    request = None if draft_id else doc_to_book_request_from_payload(payload)
    record = DocToBookCaptureService(root_dir).capture(draft_id=draft_id, request=request)
    return record.to_dict()


def normalize_doc_to_book_draft(root_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    draft_id = str(payload.get("draft_id") or "").strip()
    if not draft_id:
        raise ValueError("normalize할 draft_id가 필요합니다.")
    record = DocToBookNormalizeService(root_dir).normalize(draft_id=draft_id)
    return record.to_dict()


def load_doc_to_book_capture(
    root_dir: Path,
    draft_id: str,
) -> tuple[bytes, str] | None:
    record = DocToBookDraftStore(root_dir).get(draft_id)
    if record is None or not record.capture_artifact_path.strip():
        return None
    artifact_path = Path(record.capture_artifact_path)
    if not artifact_path.exists():
        return None
    return artifact_path.read_bytes(), record.capture_content_type or "application/octet-stream"


__all__ = [
    "build_doc_to_book_plan",
    "capture_doc_to_book_draft",
    "create_doc_to_book_draft",
    "doc_to_book_request_from_payload",
    "load_doc_to_book_capture",
    "load_doc_to_book_draft",
    "normalize_doc_to_book_draft",
    "upload_doc_to_book_draft",
]
