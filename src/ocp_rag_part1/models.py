from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class SourceManifestEntry:
    book_slug: str
    title: str
    source_url: str
    viewer_path: str
    high_value: bool

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
    section_key: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
    viewer_doc_count: int = 0
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
