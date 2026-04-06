from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal


SourceType = Literal["web", "pdf"]


@dataclass(slots=True)
class DocSourceRequest:
    source_type: SourceType
    uri: str
    title: str = ""
    language_hint: str = "ko"


@dataclass(slots=True)
class CanonicalBookDraft:
    book_slug: str
    title: str
    source_type: SourceType
    source_uri: str
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
            "language_hint": self.language_hint,
            "source_view_strategy": self.source_view_strategy,
            "retrieval_derivation": self.retrieval_derivation,
            "sections": [section.to_dict() for section in self.sections],
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class DocToBookDraftRecord:
    draft_id: str
    status: str
    created_at: str
    updated_at: str
    request: DocSourceRequest
    plan: CanonicalBookDraft
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
            "request": asdict(self.request),
            "plan": self.plan.to_dict(),
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
            "acquisition_uri": self.plan.acquisition_uri,
            "capture_strategy": self.plan.capture_strategy,
            "canonical_model": self.plan.canonical_model,
            "capture_artifact_path": self.capture_artifact_path,
            "capture_content_type": self.capture_content_type,
            "capture_byte_size": self.capture_byte_size,
            "capture_error": self.capture_error,
            "canonical_book_path": self.canonical_book_path,
            "normalized_section_count": self.normalized_section_count,
            "normalize_error": self.normalize_error,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "DocToBookDraftRecord":
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
            capture_artifact_path=str(payload.get("capture_artifact_path") or "").strip(),
            capture_content_type=str(payload.get("capture_content_type") or "").strip(),
            capture_byte_size=int(payload.get("capture_byte_size") or 0),
            capture_error=str(payload.get("capture_error") or "").strip(),
            canonical_book_path=str(payload.get("canonical_book_path") or "").strip(),
            normalized_section_count=int(payload.get("normalized_section_count") or 0),
            normalize_error=str(payload.get("normalize_error") or "").strip(),
        )
