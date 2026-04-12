from __future__ import annotations

# intake가 주고받는 canonical book / draft 데이터 모델 모음.

from dataclasses import asdict, dataclass, field
from typing import Literal


SourceType = Literal["web", "pdf", "md", "asciidoc", "txt", "docx", "pptx", "xlsx", "image"]
SupportStatus = Literal["supported", "staged", "rejected"]


@dataclass(slots=True)
class DocSourceRequest:
    source_type: SourceType
    uri: str
    title: str = ""
    language_hint: str = "ko"


@dataclass(slots=True)
class IntakeOcrMetadata:
    enabled: bool
    required: bool
    runtime: str
    fallback_order: tuple[str, ...] = field(default_factory=tuple)
    quality_gate: str = ""
    review_rule: str = ""
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "required": self.required,
            "runtime": self.runtime,
            "fallback_order": list(self.fallback_order),
            "quality_gate": self.quality_gate,
            "review_rule": self.review_rule,
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class IntakeFormatSupportEntry:
    format_id: str
    route_label: str
    source_type: str
    support_status: SupportStatus
    capture_strategy: str
    normalization_strategy: str
    review_rule: str
    ocr: IntakeOcrMetadata = field(default_factory=lambda: IntakeOcrMetadata(False, False, "n/a"))
    accepted_extensions: tuple[str, ...] = field(default_factory=tuple)
    accepted_mime_types: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "format_id": self.format_id,
            "route_label": self.route_label,
            "source_type": self.source_type,
            "support_status": self.support_status,
            "capture_strategy": self.capture_strategy,
            "normalization_strategy": self.normalization_strategy,
            "review_rule": self.review_rule,
            "ocr": self.ocr.to_dict(),
            "accepted_extensions": list(self.accepted_extensions),
            "accepted_mime_types": list(self.accepted_mime_types),
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class IntakeSupportMatrix:
    matrix_version: str
    entries: tuple[IntakeFormatSupportEntry, ...]
    status_legend: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        entries = [entry.to_dict() for entry in self.entries]
        source_type_summary: dict[str, dict[str, object]] = {}
        for entry in self.entries:
            summary = source_type_summary.setdefault(
                entry.source_type,
                {
                    "source_type": entry.source_type,
                    "support_status": entry.support_status,
                    "route_ids": [],
                    "route_labels": [],
                    "supported_route_ids": [],
                    "staged_route_ids": [],
                    "review_rules": [],
                    "ocr_enabled": False,
                    "ocr_required": False,
                    "has_rejected_route": False,
                },
            )
            summary["route_ids"].append(entry.format_id)
            summary["route_labels"].append(entry.route_label)
            if entry.support_status == "supported":
                summary["supported_route_ids"].append(entry.format_id)
            elif entry.support_status == "staged":
                summary["staged_route_ids"].append(entry.format_id)
            else:
                summary["has_rejected_route"] = True
            summary["ocr_enabled"] = bool(summary["ocr_enabled"]) or entry.ocr.enabled
            summary["ocr_required"] = bool(summary["ocr_required"]) or entry.ocr.required
            if entry.review_rule not in summary["review_rules"]:
                summary["review_rules"].append(entry.review_rule)

        for summary in source_type_summary.values():
            if summary["supported_route_ids"]:
                summary["support_status"] = "supported"
                summary["recommended_route_id"] = summary["supported_route_ids"][0]
            elif summary["staged_route_ids"]:
                summary["support_status"] = "staged"
                summary["recommended_route_id"] = summary["staged_route_ids"][0]
            else:
                summary["support_status"] = "rejected"
                summary["recommended_route_id"] = summary["route_ids"][0] if summary["route_ids"] else ""
            summary["route_count"] = len(summary["route_ids"])

        return {
            "matrix_version": self.matrix_version,
            "status_legend": dict(self.status_legend),
            "entries": entries,
            "source_type_summary": list(source_type_summary.values()),
        }


@dataclass(slots=True)
class CanonicalBookDraft:
    book_slug: str
    title: str
    source_type: SourceType
    source_uri: str
    source_collection: str
    pack_id: str
    pack_label: str
    inferred_product: str
    inferred_version: str
    acquisition_uri: str
    capture_strategy: str
    acquisition_step: str
    normalization_step: str
    derivation_step: str
    notes: tuple[str, ...] = field(default_factory=tuple)
    canonical_model: str = "canonical_book_v1"
    source_view_strategy: str = "source_view_first"
    retrieval_derivation: str = "chunks_from_canonical_sections"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class CanonicalSection:
    ordinal: int
    section_key: str
    heading: str
    section_level: int
    section_path: tuple[str, ...]
    section_path_label: str
    anchor: str
    viewer_path: str
    source_url: str
    text: str
    block_kinds: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "ordinal": self.ordinal,
            "section_key": self.section_key,
            "heading": self.heading,
            "section_level": self.section_level,
            "section_path": list(self.section_path),
            "section_path_label": self.section_path_label,
            "anchor": self.anchor,
            "viewer_path": self.viewer_path,
            "source_url": self.source_url,
            "text": self.text,
            "block_kinds": list(self.block_kinds),
        }


@dataclass(slots=True)
class CanonicalBook:
    canonical_model: str
    book_slug: str
    title: str
    source_type: SourceType
    source_uri: str
    source_collection: str
    pack_id: str
    pack_label: str
    inferred_product: str
    inferred_version: str
    language_hint: str
    source_view_strategy: str
    retrieval_derivation: str
    sections: tuple[CanonicalSection, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "canonical_model": self.canonical_model,
            "book_slug": self.book_slug,
            "title": self.title,
            "source_type": self.source_type,
            "source_uri": self.source_uri,
            "source_collection": self.source_collection,
            "pack_id": self.pack_id,
            "pack_label": self.pack_label,
            "inferred_product": self.inferred_product,
            "inferred_version": self.inferred_version,
            "language_hint": self.language_hint,
            "source_view_strategy": self.source_view_strategy,
            "retrieval_derivation": self.retrieval_derivation,
            "sections": [section.to_dict() for section in self.sections],
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class CustomerPackDraftRecord:
    draft_id: str
    status: str
    created_at: str
    updated_at: str
    request: DocSourceRequest
    plan: CanonicalBookDraft
    uploaded_file_name: str = ""
    uploaded_file_path: str = ""
    uploaded_byte_size: int = 0
    capture_artifact_path: str = ""
    capture_content_type: str = ""
    capture_byte_size: int = 0
    capture_error: str = ""
    canonical_book_path: str = ""
    normalized_section_count: int = 0
    normalize_error: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "draft_id": self.draft_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source_type": self.request.source_type,
            "title": self.plan.title,
            "book_slug": self.plan.book_slug,
            "source_uri": self.request.uri,
            "source_collection": self.plan.source_collection,
            "pack_id": self.plan.pack_id,
            "pack_label": self.plan.pack_label,
            "inferred_product": self.plan.inferred_product,
            "inferred_version": self.plan.inferred_version,
            "acquisition_uri": self.plan.acquisition_uri,
            "capture_strategy": self.plan.capture_strategy,
            "canonical_model": self.plan.canonical_model,
            "request": asdict(self.request),
            "plan": self.plan.to_dict(),
            "uploaded_file_name": self.uploaded_file_name,
            "uploaded_file_path": self.uploaded_file_path,
            "uploaded_byte_size": self.uploaded_byte_size,
            "capture_artifact_path": self.capture_artifact_path,
            "capture_content_type": self.capture_content_type,
            "capture_byte_size": self.capture_byte_size,
            "capture_error": self.capture_error,
            "canonical_book_path": self.canonical_book_path,
            "normalized_section_count": self.normalized_section_count,
            "normalize_error": self.normalize_error,
        }

    def to_summary(self) -> dict[str, object]:
        return {
            "draft_id": self.draft_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source_type": self.request.source_type,
            "title": self.plan.title,
            "book_slug": self.plan.book_slug,
            "source_uri": self.request.uri,
            "source_collection": self.plan.source_collection,
            "pack_id": self.plan.pack_id,
            "pack_label": self.plan.pack_label,
            "inferred_product": self.plan.inferred_product,
            "inferred_version": self.plan.inferred_version,
            "acquisition_uri": self.plan.acquisition_uri,
            "capture_strategy": self.plan.capture_strategy,
            "canonical_model": self.plan.canonical_model,
            "uploaded_file_name": self.uploaded_file_name,
            "uploaded_file_path": self.uploaded_file_path,
            "uploaded_byte_size": self.uploaded_byte_size,
            "capture_artifact_path": self.capture_artifact_path,
            "capture_content_type": self.capture_content_type,
            "capture_byte_size": self.capture_byte_size,
            "capture_error": self.capture_error,
            "canonical_book_path": self.canonical_book_path,
            "normalized_section_count": self.normalized_section_count,
            "normalize_error": self.normalize_error,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "CustomerPackDraftRecord":
        request_payload = dict(payload.get("request") or {})
        plan_payload = dict(payload.get("plan") or {})
        return cls(
            draft_id=str(payload.get("draft_id") or "").strip(),
            status=str(payload.get("status") or "planned").strip() or "planned",
            created_at=str(payload.get("created_at") or "").strip(),
            updated_at=str(payload.get("updated_at") or "").strip(),
            request=DocSourceRequest(
                source_type=str(request_payload.get("source_type") or "web").strip(),  # type: ignore[arg-type]
                uri=str(request_payload.get("uri") or "").strip(),
                title=str(request_payload.get("title") or "").strip(),
                language_hint=str(request_payload.get("language_hint") or "ko").strip() or "ko",
            ),
            plan=CanonicalBookDraft(
                book_slug=str(plan_payload.get("book_slug") or "").strip(),
                title=str(plan_payload.get("title") or "").strip(),
                source_type=str(plan_payload.get("source_type") or request_payload.get("source_type") or "web").strip(),  # type: ignore[arg-type]
                source_uri=str(plan_payload.get("source_uri") or request_payload.get("uri") or "").strip(),
                source_collection=str(plan_payload.get("source_collection") or "uploaded").strip() or "uploaded",
                pack_id=str(plan_payload.get("pack_id") or "custom-uploaded").strip() or "custom-uploaded",
                pack_label=str(plan_payload.get("pack_label") or "User Custom Pack").strip() or "User Custom Pack",
                inferred_product=str(plan_payload.get("inferred_product") or "unknown").strip() or "unknown",
                inferred_version=str(plan_payload.get("inferred_version") or "unknown").strip() or "unknown",
                acquisition_uri=str(plan_payload.get("acquisition_uri") or "").strip(),
                capture_strategy=str(plan_payload.get("capture_strategy") or "").strip(),
                acquisition_step=str(plan_payload.get("acquisition_step") or "").strip(),
                normalization_step=str(plan_payload.get("normalization_step") or "").strip(),
                derivation_step=str(plan_payload.get("derivation_step") or "").strip(),
                notes=tuple(str(item) for item in (plan_payload.get("notes") or [])),
                canonical_model=str(plan_payload.get("canonical_model") or "canonical_book_v1").strip(),
                source_view_strategy=str(plan_payload.get("source_view_strategy") or "source_view_first").strip(),
                retrieval_derivation=str(plan_payload.get("retrieval_derivation") or "chunks_from_canonical_sections").strip(),
            ),
            uploaded_file_name=str(payload.get("uploaded_file_name") or "").strip(),
            uploaded_file_path=str(payload.get("uploaded_file_path") or "").strip(),
            uploaded_byte_size=int(payload.get("uploaded_byte_size") or 0),
            capture_artifact_path=str(payload.get("capture_artifact_path") or "").strip(),
            capture_content_type=str(payload.get("capture_content_type") or "").strip(),
            capture_byte_size=int(payload.get("capture_byte_size") or 0),
            capture_error=str(payload.get("capture_error") or "").strip(),
            canonical_book_path=str(payload.get("canonical_book_path") or "").strip(),
            normalized_section_count=int(payload.get("normalized_section_count") or 0),
            normalize_error=str(payload.get("normalize_error") or "").strip(),
        )
