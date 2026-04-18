"""HTTP 서버가 공통으로 쓰는 presentation helper.

런타임/내부 객체를 UI가 소비할 payload로 바꾸고, runtime fingerprint 및
health snapshot 생성도 담당한다.
"""

import html
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from play_book_studio.intake import CustomerPackDraftStore
from play_book_studio.intake.service import evaluate_canonical_book_quality
from play_book_studio.config.packs import default_core_pack, resolve_ocp_core_pack
from play_book_studio.config.settings import Settings, load_settings
from play_book_studio.config.validation import read_jsonl
from play_book_studio.ingestion.graph_sidecar import graph_sidecar_compact_artifact_status
from play_book_studio.runtime_catalog_registry import official_runtime_book_entry
from play_book_studio.answering.answerer import ChatAnswerer
from play_book_studio.answering.models import Citation
from play_book_studio.app.viewers import _parse_viewer_path
from .viewer_blocks import _clean_source_view_text


HEADING_NUMBER_PREFIX_RE = re.compile(
    r"^\s*(?:chapter\s+\d+\.?\s*|\d+\s*장\.?\s*|(?:\d+|[A-Za-z])(?:\.\d+)*\.?\s+)",
    re.IGNORECASE,
)


def _display_source_heading(text: str) -> str:
    raw = " ".join(str(text or "").split()).strip()
    if not raw:
        return ""
    cleaned = HEADING_NUMBER_PREFIX_RE.sub("", raw).strip()
    return cleaned or raw


def _display_section_path(items: list[Any]) -> list[str]:
    normalized: list[str] = []
    for item in items:
        display = _display_source_heading(str(item))
        if display:
            normalized.append(display)
    return normalized


def _display_section_label(
    *,
    section_path: list[str],
    section_path_label: str,
    heading: str,
) -> str:
    raw_label = str(section_path_label or "").strip()
    if raw_label:
        normalized_parts = [
            display
            for display in (_display_source_heading(part) for part in raw_label.split(">"))
            if display
        ]
        if normalized_parts:
            return " > ".join(normalized_parts)
    if section_path:
        return " > ".join(section_path)
    return _display_source_heading(heading)




def _citation_href(citation: Citation) -> str:
    viewer_path = (citation.viewer_path or "").strip()
    if viewer_path:
        return viewer_path
    if citation.anchor:
        return f"{citation.source_url}#{citation.anchor}"
    return citation.source_url


def _humanize_book_slug(book_slug: str) -> str:
    return " ".join(part for part in str(book_slug or "").replace("_", " ").split())


def _core_pack_payload(*, version: str | None = None, language: str | None = None) -> dict[str, str]:
    pack = (
        resolve_ocp_core_pack(version=version, language=language or default_core_pack().language)
        if version is not None or language is not None
        else default_core_pack()
    )
    return pack.payload()

def _llm_runtime_signature(settings: Settings) -> tuple[Any, ...]:
    return (
        settings.ocp_version,
        settings.docs_language,
        settings.llm_endpoint,
        settings.llm_model,
        settings.llm_api_key,
        settings.llm_temperature,
        settings.llm_max_tokens,
        settings.embedding_base_url,
        settings.embedding_model,
        settings.embedding_device,
        settings.embedding_api_key,
        settings.embedding_batch_size,
        settings.embedding_timeout_seconds,
        settings.reranker_enabled,
        settings.reranker_model,
        settings.reranker_top_n,
        settings.reranker_batch_size,
        settings.reranker_device,
        settings.qdrant_url,
        settings.qdrant_collection,
        settings.qdrant_vector_size,
        settings.qdrant_distance,
        settings.request_timeout_seconds,
        str(settings.artifacts_dir),
        str(settings.source_manifest_path),
        str(settings.normalized_docs_path),
        str(settings.chunks_path),
        str(settings.bm25_corpus_path),
        str(settings.customer_pack_books_dir),
        settings.request_timeout_seconds,
    )


def _runtime_fingerprint(settings: Settings) -> str:
    raw = "|".join(str(item) for item in _llm_runtime_signature(settings))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def _refresh_answerer_llm_settings(
    answerer: ChatAnswerer,
    *,
    root_dir: Path,
    current_signature: tuple[Any, ...] | None,
) -> tuple[ChatAnswerer, tuple[Any, ...]]:
    # runtime signature가 바뀌면 answerer 전체를 다시 만들어 LLM, embedding,
    # retriever, pack 상태가 서로 어긋나지 않게 한다.
    settings = load_settings(root_dir)
    signature = _llm_runtime_signature(settings)
    if signature == current_signature:
        return answerer, signature
    factory = getattr(answerer.__class__, "from_settings", None)
    if callable(factory):
        return factory(settings), signature
    answerer.settings = settings
    if hasattr(answerer, "llm_client") and hasattr(answerer.llm_client.__class__, "__call__"):
        answerer.llm_client = answerer.llm_client.__class__(settings)
    return answerer, signature


def _build_health_payload(answerer: ChatAnswerer) -> dict[str, Any]:
    settings = answerer.settings
    pack = settings.active_pack
    embedding_mode = "remote" if settings.embedding_base_url else "local"
    compact_graph_artifact = graph_sidecar_compact_artifact_status(settings)
    llm_runtime = (
        answerer.llm_client.runtime_metadata()
        if hasattr(answerer.llm_client, "runtime_metadata")
        else {}
    )
    return {
        "ok": True,
        "runtime": {
            "app_id": settings.app_id,
            "app_label": settings.app_label,
            "config_fingerprint": _runtime_fingerprint(settings),
            "runtime_refresh_strategy": "rebuild_answerer_on_signature_change",
            "ocp_version": settings.ocp_version,
            "docs_language": settings.docs_language,
            "active_pack_id": pack.pack_id,
            "active_pack_label": pack.pack_label,
            "active_pack_product": pack.product_label,
            "viewer_path_prefix": pack.viewer_path_prefix,
            "llm_endpoint": settings.llm_endpoint,
            "llm_model": settings.llm_model,
            "llm_provider_hint": llm_runtime.get("preferred_provider", "unknown"),
            "llm_fallback_enabled": bool(llm_runtime.get("fallback_enabled", False)),
            "llm_last_provider": llm_runtime.get("last_provider"),
            "llm_last_fallback_used": bool(llm_runtime.get("last_fallback_used", False)),
            "llm_attempted_providers": list(llm_runtime.get("last_attempted_providers", [])),
            "embedding_mode": embedding_mode,
            "embedding_base_url": settings.embedding_base_url,
            "embedding_model": settings.embedding_model,
            "embedding_device": settings.embedding_device,
            "reranker_enabled": bool(settings.reranker_enabled),
            "reranker_model": settings.reranker_model,
            "reranker_top_n": settings.reranker_top_n,
            "reranker_batch_size": settings.reranker_batch_size,
            "reranker_device": settings.reranker_device,
            "qdrant_url": settings.qdrant_url,
            "qdrant_collection": settings.qdrant_collection,
            "graph_backend": settings.graph_backend,
            "graph_runtime_mode": settings.graph_runtime_mode,
            "graph_compact_artifact": compact_graph_artifact,
            "artifacts_dir": str(settings.artifacts_dir),
            "source_manifest_path": str(settings.source_manifest_path),
            "normalized_docs_path": str(settings.normalized_docs_path),
            "bm25_corpus_path": str(settings.bm25_corpus_path),
            "customer_pack_books_dir": str(settings.customer_pack_books_dir),
        },
    }


@lru_cache(maxsize=4)
def _load_manifest_entries(
    manifest_path: str,
    mtime_ns: int,
) -> dict[str, dict[str, Any]]:
    del mtime_ns
    payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    entries = payload.get("entries") or []
    return {
        str(entry.get("book_slug", "")).strip(): dict(entry)
        for entry in entries
        if str(entry.get("book_slug", "")).strip()
    }


def _manifest_entry_for_book(root_dir: Path, book_slug: str) -> dict[str, Any]:
    settings = load_settings(root_dir)
    manifest_path = settings.source_manifest_path
    manifest_entry: dict[str, Any] = {}
    if manifest_path.exists():
        manifest_entry = _load_manifest_entries(
            str(manifest_path),
            manifest_path.stat().st_mtime_ns,
        ).get(book_slug, {})
    if manifest_entry:
        return manifest_entry
    return official_runtime_book_entry(root_dir, book_slug)


class _CitationPresentationContext:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.settings = load_settings(root_dir)
        self.core_pack_payload = _core_pack_payload(
            version=self.settings.ocp_version,
            language=self.settings.docs_language,
        )
        self._manifest_entries: dict[str, dict[str, Any]] = {}
        self._normalized_rows: dict[str, tuple[dict[str, Any] | None, bool]] = {}
        self._customer_pack_meta: dict[str, dict[str, Any] | None] = {}

    def manifest_entry(self, book_slug: str) -> dict[str, Any]:
        normalized_slug = str(book_slug or "").strip()
        if normalized_slug not in self._manifest_entries:
            manifest_path = self.settings.source_manifest_path
            manifest_entry: dict[str, Any] = {}
            if manifest_path.exists():
                manifest_entry = _load_manifest_entries(
                    str(manifest_path),
                    manifest_path.stat().st_mtime_ns,
                ).get(normalized_slug, {})
            if not manifest_entry:
                manifest_entry = official_runtime_book_entry(self.root_dir, normalized_slug)
            self._manifest_entries[normalized_slug] = manifest_entry
        return self._manifest_entries[normalized_slug]

    def normalized_row(self, viewer_path: str) -> tuple[dict[str, Any] | None, bool]:
        normalized_viewer_path = str(viewer_path or "").strip()
        if normalized_viewer_path not in self._normalized_rows:
            self._normalized_rows[normalized_viewer_path] = _resolve_normalized_row_for_viewer_path(
                self.root_dir,
                normalized_viewer_path,
                settings=self.settings,
            )
        return self._normalized_rows[normalized_viewer_path]

    def customer_pack_meta(self, viewer_path: str) -> dict[str, Any] | None:
        normalized_viewer_path = str(viewer_path or "").strip()
        if normalized_viewer_path not in self._customer_pack_meta:
            self._customer_pack_meta[normalized_viewer_path] = _customer_pack_meta_for_viewer_path(
                self.root_dir,
                normalized_viewer_path,
                settings=self.settings,
            )
        return self._customer_pack_meta[normalized_viewer_path]


def _build_citation_presentation_context(root_dir: Path) -> _CitationPresentationContext:
    return _CitationPresentationContext(root_dir)


@lru_cache(maxsize=1)
def _load_normalized_sections(
    normalized_docs_path: str,
    mtime_ns: int,
) -> dict[str, list[dict[str, Any]]]:
    del mtime_ns
    sections = read_jsonl(Path(normalized_docs_path))
    sections_by_book: dict[str, list[dict[str, Any]]] = {}
    for row in sections:
        book_slug = str(row.get("book_slug") or "").strip()
        if book_slug:
            if book_slug not in sections_by_book:
                sections_by_book[book_slug] = []
            sections_by_book[book_slug].append(row)
    return sections_by_book


def _parse_customer_pack_viewer_path(viewer_path: str) -> tuple[str, str] | None:
    value = (viewer_path or "").strip()
    if "#" in value:
        path_part, anchor = value.split("#", 1)
    else:
        path_part, anchor = value, ""
    prefix = "/playbooks/customer-packs/"
    if not path_part.startswith(prefix):
        return None
    remainder = path_part[len(prefix) :]
    parts = [part for part in remainder.split("/") if part]
    if len(parts) == 2 and parts[1] == "index.html":
        return parts[0], anchor
    if len(parts) == 4 and parts[1] == "assets" and parts[3] == "index.html":
        return f"{parts[0]}::{parts[2]}", anchor
    return None


def _customer_pack_book_for_viewer_path(
    root_dir: Path,
    viewer_path: str,
    *,
    settings: Settings | None = None,
) -> dict[str, Any] | None:
    parsed = _parse_customer_pack_viewer_path(viewer_path)
    if parsed is None:
        return None
    draft_id, target_anchor = parsed
    resolved_draft_id = draft_id
    asset_slug = ""
    if "::" in draft_id:
        resolved_draft_id, asset_slug = draft_id.split("::", 1)
    record = CustomerPackDraftStore(root_dir).get(resolved_draft_id)
    if record is None or not record.canonical_book_path.strip():
        return None
    active_settings = settings or load_settings(root_dir)
    payload_path = (
        active_settings.customer_pack_books_dir / f"{asset_slug}.json"
        if asset_slug
        else Path(record.canonical_book_path)
    )
    if not payload_path.exists():
        return None
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    payload["draft_id"] = record.draft_id
    payload["target_viewer_path"] = (
        f"/playbooks/customer-packs/{record.draft_id}/assets/{asset_slug}/index.html"
        if asset_slug
        else f"/playbooks/customer-packs/{record.draft_id}/index.html"
    )
    payload["target_anchor"] = target_anchor
    payload["source_origin_url"] = f"/api/customer-packs/captured?draft_id={record.draft_id}"
    payload.setdefault("source_collection", record.plan.source_collection)
    payload.setdefault("pack_id", record.plan.pack_id)
    payload.setdefault("pack_label", record.plan.pack_label)
    payload.setdefault("inferred_product", record.plan.inferred_product)
    payload.setdefault("inferred_version", record.plan.inferred_version)
    payload.setdefault("source_lane", record.source_lane)
    payload.setdefault("approval_state", record.approval_state)
    payload.setdefault("publication_state", record.publication_state)
    payload.setdefault("parser_backend", record.parser_backend)
    payload.setdefault("parser_route", record.parser_route)
    payload.setdefault("parser_version", record.parser_version)
    payload.setdefault("ocr_used", record.ocr_used)
    payload.setdefault("extraction_confidence", record.extraction_confidence)
    payload.setdefault("degraded_pdf", record.degraded_pdf)
    payload.setdefault("degraded_reason", record.degraded_reason)
    payload.setdefault("fallback_used", record.fallback_used)
    payload.setdefault("fallback_backend", record.fallback_backend)
    payload.setdefault("fallback_status", record.fallback_status)
    payload.setdefault("fallback_reason", record.fallback_reason)
    payload.setdefault("boundary_truth", "private_customer_pack_runtime")
    payload.setdefault("runtime_truth_label", "Customer Source-First Pack")
    payload.setdefault("boundary_badge", "Private Pack Runtime")
    payload.update(evaluate_canonical_book_quality(payload))
    return payload


def _customer_pack_meta_for_viewer_path(
    root_dir: Path,
    viewer_path: str,
    *,
    settings: Settings | None = None,
) -> dict[str, Any] | None:
    payload = _customer_pack_book_for_viewer_path(root_dir, viewer_path, settings=settings)
    if payload is None:
        return None
    sections = [dict(section) for section in (payload.get("sections") or []) if isinstance(section, dict)]
    if not sections:
        return None
    target_anchor = str(payload.get("target_anchor") or "").strip()
    target = sections[0]
    matched_exact = not target_anchor
    for section in sections:
        if str(section.get("anchor") or "").strip() == target_anchor:
            target = section
            matched_exact = True
            break
    section_path = _display_section_path(list(target.get("section_path") or []))
    section = _display_source_heading(str(target.get("heading") or ""))
    return {
        "book_slug": str(payload.get("book_slug") or ""),
        "book_title": str(payload.get("title") or payload.get("book_slug") or ""),
        "anchor": str(target.get("anchor") or target_anchor),
        "section": section,
        "section_path": section_path,
        "section_path_label": _display_section_label(
            section_path=section_path,
            section_path_label=str(target.get("section_path_label") or "").strip(),
            heading=section,
        ),
        "source_url": str(payload.get("source_origin_url") or target.get("source_url") or payload.get("source_uri") or ""),
        "viewer_path": viewer_path,
        "source_collection": str(payload.get("source_collection") or "uploaded"),
        "pack_id": str(payload.get("pack_id") or ""),
        "pack_label": str(payload.get("pack_label") or ""),
        "source_lane": str(payload.get("source_lane") or "customer_source_first_pack"),
        "approval_state": str(payload.get("approval_state") or "unreviewed"),
        "publication_state": str(payload.get("publication_state") or "draft"),
        "parser_backend": str(payload.get("parser_backend") or ""),
        "fallback_used": bool(payload.get("fallback_used") or False),
        "boundary_truth": str(payload.get("boundary_truth") or "private_customer_pack_runtime"),
        "runtime_truth_label": str(payload.get("runtime_truth_label") or "Customer Source-First Pack"),
        "boundary_badge": str(payload.get("boundary_badge") or "Private Pack Runtime"),
        "inferred_product": str(payload.get("inferred_product") or "unknown"),
        "inferred_version": str(payload.get("inferred_version") or "unknown"),
        "quality_status": str(payload.get("quality_status") or "ready"),
        "quality_summary": str(payload.get("quality_summary") or ""),
        "section_match_exact": matched_exact,
    }


def _default_customer_pack_summary(payload: dict[str, Any]) -> str:
    source_type = str(payload.get("source_type") or "").strip().lower()
    source_label = {
        "pdf": "PDF를",
        "md": "text 문서를",
        "asciidoc": "text 문서를",
        "txt": "text 문서를",
    }.get(source_type, "웹 문서를")
    return (
        f"업로드 {source_label} canonical section으로 정리한 내부 review view입니다. "
        "이후 retrieval chunk는 이 section을 부모로 파생됩니다."
    )


def _official_runtime_truth_payload(
    *,
    settings: Settings,
    manifest_entry: dict[str, Any],
) -> dict[str, str]:
    pack_label = str(manifest_entry.get("pack_label") or settings.active_pack.pack_label or "").strip()
    runtime_truth_label = f"{pack_label} Runtime" if pack_label else "Validated Pack Runtime"
    return {
        "source_lane": str(manifest_entry.get("source_lane") or "approved_wiki_runtime"),
        "boundary_truth": "official_validated_runtime",
        "runtime_truth_label": runtime_truth_label,
        "boundary_badge": "Validated Runtime",
    }


def _normalized_row_for_viewer_path(root_dir: Path, viewer_path: str) -> dict[str, Any] | None:
    row, _matched_exact = _resolve_normalized_row_for_viewer_path(root_dir, viewer_path)
    return row


def _resolve_normalized_row_for_viewer_path(
    root_dir: Path,
    viewer_path: str,
    *,
    settings: Settings | None = None,
) -> tuple[dict[str, Any] | None, bool]:
    parsed = _parse_viewer_path(viewer_path)
    if parsed is None:
        return None, False
    book_slug, anchor = parsed
    active_settings = settings or load_settings(root_dir)
    for normalized_docs_path in active_settings.normalized_docs_candidates:
        if not normalized_docs_path.exists():
            continue
        sections_by_book = _load_normalized_sections(
            str(normalized_docs_path),
            normalized_docs_path.stat().st_mtime_ns,
        )
        sections = sections_by_book.get(book_slug, [])
        if not sections:
            continue
        if not anchor:
            return sections[0], True

        for row in sections:
            if str(row.get("anchor") or "").strip() == anchor:
                return row, True
        return sections[0], False
    return None, False


def _serialize_citation(
    root_dir: Path,
    citation: Citation,
    *,
    presentation_context: _CitationPresentationContext | None = None,
) -> dict[str, Any]:
    context = presentation_context or _build_citation_presentation_context(root_dir)
    settings = context.settings
    href = _citation_href(citation)
    row, matched_exact = context.normalized_row(href)
    customer_pack_meta = context.customer_pack_meta(href)
    manifest_entry = context.manifest_entry(citation.book_slug)

    if row is None and customer_pack_meta is not None:
        book_title = str(customer_pack_meta.get("book_title") or "") or _humanize_book_slug(citation.book_slug)
        section_path = [
            _display_source_heading(str(item))
            for item in (customer_pack_meta.get("section_path") or [])
            if _display_source_heading(str(item))
        ]
        section_label = (
            _display_section_label(
                section_path=section_path,
                section_path_label=str(customer_pack_meta.get("section_path_label") or "").strip(),
                heading=str(customer_pack_meta.get("section") or citation.section or citation.anchor),
            )
            or _display_source_heading(str(customer_pack_meta.get("section") or citation.section or citation.anchor))
        )
        return {
            **citation.to_dict(),
            "section": _display_source_heading(
                str(customer_pack_meta.get("section") or citation.section or citation.anchor)
            ),
            "href": href,
            "book_title": book_title,
            "section_path": section_path,
            "section_path_label": section_label,
            "source_label": f"{book_title} · {section_label}" if section_label else book_title,
            "source_collection": str(customer_pack_meta.get("source_collection") or "uploaded"),
            "pack_id": str(customer_pack_meta.get("pack_id") or ""),
            "pack_label": str(customer_pack_meta.get("pack_label") or ""),
            "source_lane": str(customer_pack_meta.get("source_lane") or "customer_source_first_pack"),
            "approval_state": str(customer_pack_meta.get("approval_state") or "unreviewed"),
            "publication_state": str(customer_pack_meta.get("publication_state") or "draft"),
            "parser_backend": str(customer_pack_meta.get("parser_backend") or ""),
            "fallback_used": bool(customer_pack_meta.get("fallback_used") or False),
            "quality_status": str(customer_pack_meta.get("quality_status") or "ready"),
            "boundary_truth": str(customer_pack_meta.get("boundary_truth") or "private_customer_pack_runtime"),
            "runtime_truth_label": str(customer_pack_meta.get("runtime_truth_label") or "Customer Source-First Pack"),
            "boundary_badge": str(customer_pack_meta.get("boundary_badge") or "Private Pack Runtime"),
            "inferred_product": str(customer_pack_meta.get("inferred_product") or "unknown"),
            "inferred_version": str(customer_pack_meta.get("inferred_version") or "unknown"),
            "section_match_exact": bool(customer_pack_meta.get("section_match_exact", True)),
        }

    book_title = (
        str((row or {}).get("book_title") or "")
        or str(manifest_entry.get("title") or "")
        or _humanize_book_slug(citation.book_slug)
    )
    section_path = [
        item
        for item in _display_section_path(list((row or {}).get("section_path") or []))
        if str(item).strip()
    ]
    section = _display_source_heading(str((row or {}).get("heading") or citation.section or citation.anchor))
    section_label = _display_section_label(
        section_path=section_path,
        section_path_label="",
        heading=section,
    )
    return {
        **citation.to_dict(),
        "section": section,
        "href": href,
        "book_title": book_title,
        "section_path": section_path,
        "section_path_label": section_label,
        "source_label": f"{book_title} · {section_label}" if section_label else book_title,
        **context.core_pack_payload,
        **_official_runtime_truth_payload(settings=settings, manifest_entry=manifest_entry),
        "section_match_exact": matched_exact,
    }
