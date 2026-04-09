# ingestion 단계에서 쓰는 manifest/source entry 데이터 모델 모음.
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

SOURCE_STATE_PUBLISHED_NATIVE = "published_native"
SOURCE_STATE_FALLBACK_TO_EN = "fallback_to_en"
SOURCE_STATE_EN_ONLY = "en_only"
SOURCE_STATE_MISSING = "missing"
SOURCE_STATE_BLOCKED = "blocked"

KNOWN_SOURCE_STATES = (
    SOURCE_STATE_PUBLISHED_NATIVE,
    SOURCE_STATE_FALLBACK_TO_EN,
    SOURCE_STATE_EN_ONLY,
    SOURCE_STATE_MISSING,
    SOURCE_STATE_BLOCKED,
)

CONTENT_STATUS_APPROVED_KO = "approved_ko"
CONTENT_STATUS_TRANSLATED_KO_DRAFT = "translated_ko_draft"
CONTENT_STATUS_MIXED = "mixed"
CONTENT_STATUS_EN_ONLY = "en_only"
CONTENT_STATUS_BLOCKED = "blocked"
CONTENT_STATUS_UNKNOWN = "unknown"

KNOWN_CONTENT_STATUSES = (
    CONTENT_STATUS_APPROVED_KO,
    CONTENT_STATUS_TRANSLATED_KO_DRAFT,
    CONTENT_STATUS_MIXED,
    CONTENT_STATUS_EN_ONLY,
    CONTENT_STATUS_BLOCKED,
    CONTENT_STATUS_UNKNOWN,
)

CITATION_ELIGIBLE_STATUSES = (CONTENT_STATUS_APPROVED_KO,)


@dataclass(slots=True)
class SourceManifestEntry:
    product_slug: str = "openshift_container_platform"
    ocp_version: str = "4.20"
    docs_language: str = "ko"
    source_kind: str = "html-single"
    book_slug: str = ""
    title: str = ""
    index_url: str = ""
    source_url: str = ""
    resolved_source_url: str = ""
    resolved_language: str = "ko"
    source_state: str = SOURCE_STATE_PUBLISHED_NATIVE
    source_state_reason: str = ""
    catalog_source_label: str = ""
    viewer_path: str = ""
    high_value: bool = False
    vendor_title: str = ""
    content_status: str = CONTENT_STATUS_UNKNOWN
    citation_eligible: bool = False
    citation_block_reason: str = ""
    viewer_strategy: str = "raw_html"
    body_language_guess: str = "unknown"
    hangul_section_ratio: float = 0.0
    hangul_chunk_ratio: float = 0.0
    fallback_detected: bool = False
    source_fingerprint: str = ""
    approval_status: str = "unreviewed"
    approval_notes: str = ""
    translation_source_language: str = ""
    translation_target_language: str = "ko"
    translation_source_url: str = ""
    translation_source_fingerprint: str = ""
    translation_stage: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class NormalizedSection:
    book_slug: str
    book_title: str
    heading: str
    section_level: int
    section_path: list[str]
    anchor: str
    source_url: str
    viewer_path: str
    text: str
    section_id: str = ""
    semantic_role: str = "unknown"
    block_kinds: tuple[str, ...] = field(default_factory=tuple)
    source_language: str = "ko"
    display_language: str = "ko"
    translation_status: str = "approved_ko"
    translation_stage: str = "approved_ko"
    translation_source_language: str = ""
    translation_source_url: str = ""
    translation_source_fingerprint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "book_slug": self.book_slug,
            "book_title": self.book_title,
            "heading": self.heading,
            "section_level": self.section_level,
            "section_path": list(self.section_path),
            "anchor": self.anchor,
            "source_url": self.source_url,
            "viewer_path": self.viewer_path,
            "text": self.text,
            "section_id": self.section_id,
            "semantic_role": self.semantic_role,
            "block_kinds": list(self.block_kinds),
            "source_language": self.source_language,
            "display_language": self.display_language,
            "translation_status": self.translation_status,
            "translation_stage": self.translation_stage,
            "translation_source_language": self.translation_source_language,
            "translation_source_url": self.translation_source_url,
            "translation_source_fingerprint": self.translation_source_fingerprint,
        }


@dataclass(slots=True)
class ChunkRecord:
    chunk_id: str
    book_slug: str
    book_title: str
    chapter: str
    section: str
    anchor: str
    source_url: str
    viewer_path: str
    text: str
    token_count: int
    ordinal: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PipelineLog:
    stage: str = "init"
    manifest_count: int = 0
    collected_count: int = 0
    normalized_count: int = 0
    chunk_count: int = 0
    embedded_count: int = 0
    qdrant_upserted_count: int = 0
    collected_sources: list[str] = field(default_factory=list)
    processed_sources: list[str] = field(default_factory=list)
    per_book_stats: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)

    def add_error(self, stage: str, source: str, message: str) -> None:
        self.errors.append({"stage": stage, "source": source, "message": message})

    def upsert_book_stat(self, book_slug: str, **fields: Any) -> None:
        for item in self.per_book_stats:
            if item.get("book_slug") == book_slug:
                item.update(fields)
                return
        record = {"book_slug": book_slug}
        record.update(fields)
        self.per_book_stats.append(record)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
