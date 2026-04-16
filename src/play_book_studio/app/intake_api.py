"""customer-pack draft lifecycle API 보조 로직."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any

from play_book_studio.app.source_books import load_customer_pack_book
from play_book_studio.intake import (
    DocSourceRequest,
    CustomerPackDraftStore,
    CustomerPackPlanner,
    build_customer_pack_support_matrix as _build_customer_pack_support_matrix_model,
)
from play_book_studio.intake.capture.service import CustomerPackCaptureService
from play_book_studio.intake.normalization.service import CustomerPackNormalizeService
from play_book_studio.config.settings import load_settings

SUPPORTED_CUSTOMER_PACK_SOURCE_TYPES = {
    "web",
    "pdf",
    "md",
    "asciidoc",
    "txt",
    "docx",
    "pptx",
    "xlsx",
    "image",
}


def _select_support_entry(matrix: dict[str, Any], source_type: str) -> dict[str, Any]:
    source_type = str(source_type or "").strip().lower()
    entries = [entry for entry in matrix.get("entries") or [] if isinstance(entry, dict)]
    candidates = [entry for entry in entries if str(entry.get("source_type") or "").strip().lower() == source_type]
    for status in ("supported", "staged"):
        for entry in candidates:
            if str(entry.get("support_status") or "").strip().lower() == status:
                return entry
    return candidates[0] if candidates else {}


def build_customer_pack_plan(payload: dict[str, Any]) -> dict[str, Any]:
    request = customer_pack_request_from_payload(payload)
    plan = CustomerPackPlanner().plan(request).to_dict()
    support_matrix = build_customer_pack_support_matrix()
    selected_support = _select_support_entry(support_matrix, request.source_type)
    support_review_rule = str(selected_support.get("review_rule") or "")
    ocr_metadata = dict(selected_support.get("ocr") or {})
    ocr_review_rule = str(ocr_metadata.get("review_rule") or "").strip()
    if ocr_review_rule and ocr_review_rule not in support_review_rule:
        if support_review_rule:
            support_review_rule = f"{support_review_rule} {ocr_review_rule}"
        else:
            support_review_rule = ocr_review_rule
    plan["support_status"] = str(selected_support.get("support_status") or "rejected")
    plan["support_route"] = selected_support
    plan["support_review_rule"] = support_review_rule
    plan["ocr_metadata"] = ocr_metadata
    plan["support_matrix"] = support_matrix
    return plan


def build_customer_pack_support_matrix() -> dict[str, Any]:
    return _build_customer_pack_support_matrix_model().to_dict()


def customer_pack_request_from_payload(payload: dict[str, Any]) -> DocSourceRequest:
    source_type = str(payload.get("source_type") or "").strip().lower()
    uri = str(payload.get("uri") or "").strip()
    title = str(payload.get("title") or "").strip()
    language_hint = str(payload.get("language_hint") or "ko").strip() or "ko"

    if source_type not in SUPPORTED_CUSTOMER_PACK_SOURCE_TYPES:
        raise ValueError(
            "source_type은 web, pdf, md, asciidoc, txt, docx, pptx, xlsx, image 중 하나여야 합니다."
        )
    if not uri:
        raise ValueError("uri가 필요합니다.")

    return DocSourceRequest(
        source_type=source_type,
        uri=uri,
        title=title,
        language_hint=language_hint,
    )


def create_customer_pack_draft(root_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    request = customer_pack_request_from_payload(payload)
    record = CustomerPackDraftStore(root_dir).create(request)
    return record.to_dict()


def upload_customer_pack_draft(root_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    request = customer_pack_request_from_payload(payload)
    file_name = str(payload.get("file_name") or "").strip()
    file_bytes = payload.get("file_bytes")
    if not file_name:
        raise ValueError("업로드할 file_name이 필요합니다.")
    if not isinstance(file_bytes, (bytes, bytearray)):
        raise ValueError("업로드할 file_bytes가 필요합니다.")

    content = bytes(file_bytes)
    if not content:
        raise ValueError("빈 파일은 업로드할 수 없습니다.")

    settings = load_settings(root_dir)
    upload_dir = settings.customer_pack_capture_dir / "_uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    default_suffix = {
        "pdf": ".pdf",
        "md": ".md",
        "asciidoc": ".adoc",
        "txt": ".txt",
        "docx": ".docx",
        "pptx": ".pptx",
        "xlsx": ".xlsx",
        "image": ".png",
    }.get(request.source_type, ".html")
    source_suffix = Path(file_name).suffix or default_suffix
    safe_stem = re.sub(r"[^A-Za-z0-9가-힣._-]+", "-", Path(file_name).stem).strip("-") or "upload"
    target = upload_dir / f"{uuid.uuid4().hex[:10]}-{safe_stem}{source_suffix}"
    target.write_bytes(content)

    uploaded_request = DocSourceRequest(
        source_type=request.source_type,
        uri=str(target),
        title=request.title or Path(file_name).stem,
        language_hint=request.language_hint,
    )
    store = CustomerPackDraftStore(root_dir)
    record = store.create(uploaded_request)
    record.uploaded_file_name = file_name
    record.uploaded_file_path = str(target)
    record.uploaded_byte_size = len(content)
    store.save(record)
    return record.to_dict()


def load_customer_pack_draft(root_dir: Path, draft_id: str) -> dict[str, Any] | None:
    record = CustomerPackDraftStore(root_dir).get(draft_id)
    if record is None:
        return None
    payload = record.to_dict()
    canonical_payload = load_customer_pack_book(root_dir, record.draft_id)
    if canonical_payload is not None:
        payload["playable_asset_count"] = canonical_payload.get("playable_asset_count", 1)
        payload["derived_asset_count"] = canonical_payload.get("derived_asset_count", 0)
        payload["derived_assets"] = canonical_payload.get("derived_assets", [])
    return payload


def delete_customer_pack_draft(root_dir: Path, draft_id: str) -> bool:
    store = CustomerPackDraftStore(root_dir)
    record = store.get(draft_id)
    if record is None:
        return False
    settings = load_settings(root_dir)
    # Clean up canonical book and derived playbook JSONs
    books_dir = settings.customer_pack_books_dir
    if books_dir.is_dir():
        for path in books_dir.glob(f"{draft_id}*.json"):
            path.unlink(missing_ok=True)
    # Clean up capture artifacts
    capture_dir = settings.customer_pack_capture_dir / draft_id
    if capture_dir.is_dir():
        import shutil
        shutil.rmtree(capture_dir, ignore_errors=True)
    return store.delete(draft_id)


def capture_customer_pack_draft(root_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    draft_id = str(payload.get("draft_id") or "").strip()
    request = None if draft_id else customer_pack_request_from_payload(payload)
    record = CustomerPackCaptureService(root_dir).capture(draft_id=draft_id, request=request)
    return record.to_dict()


def normalize_customer_pack_draft(root_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    draft_id = str(payload.get("draft_id") or "").strip()
    if not draft_id:
        raise ValueError("normalize할 draft_id가 필요합니다.")
    record = CustomerPackNormalizeService(root_dir).normalize(draft_id=draft_id)
    result = record.to_dict()
    canonical_payload = load_customer_pack_book(root_dir, record.draft_id)
    if canonical_payload is not None:
        result["playable_asset_count"] = canonical_payload.get("playable_asset_count", 1)
        result["derived_asset_count"] = canonical_payload.get("derived_asset_count", 0)
        result["derived_assets"] = canonical_payload.get("derived_assets", [])
    return result


def ingest_customer_pack(root_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    draft_id = str(payload.get("draft_id") or "").strip()
    if draft_id:
        captured = capture_customer_pack_draft(root_dir, {"draft_id": draft_id})
    elif isinstance(payload.get("file_bytes"), (bytes, bytearray)):
        uploaded = upload_customer_pack_draft(root_dir, payload)
        captured = capture_customer_pack_draft(root_dir, {"draft_id": str(uploaded["draft_id"])})
    else:
        captured = capture_customer_pack_draft(root_dir, payload)

    normalized = normalize_customer_pack_draft(
        root_dir,
        {"draft_id": str(captured["draft_id"])},
    )
    canonical_payload = load_customer_pack_book(root_dir, str(captured["draft_id"]))
    if canonical_payload is not None:
        normalized["book"] = canonical_payload
    return normalized


def load_customer_pack_capture(
    root_dir: Path,
    draft_id: str,
) -> tuple[bytes, str] | None:
    record = CustomerPackDraftStore(root_dir).get(draft_id)
    if record is None or not record.capture_artifact_path.strip():
        return None
    artifact_path = Path(record.capture_artifact_path)
    if not artifact_path.exists():
        return None
    return artifact_path.read_bytes(), record.capture_content_type or "application/octet-stream"


__all__ = [
    "build_customer_pack_plan",
    "build_customer_pack_support_matrix",
    "capture_customer_pack_draft",
    "create_customer_pack_draft",
    "customer_pack_request_from_payload",
    "ingest_customer_pack",
    "load_customer_pack_capture",
    "load_customer_pack_draft",
    "normalize_customer_pack_draft",
    "upload_customer_pack_draft",
]
