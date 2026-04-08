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

from play_book_studio.intake import DocToBookDraftStore
from play_book_studio.intake.service import evaluate_canonical_book_quality
from play_book_studio.config.packs import default_core_pack, resolve_ocp_core_pack
from play_book_studio.config.settings import Settings, load_settings
from play_book_studio.config.validation import read_jsonl
from play_book_studio.answering.answerer import Part3Answerer
from play_book_studio.answering.models import Citation
from play_book_studio.app.viewers import _parse_viewer_path

SOURCE_VIEW_LEADING_NOISE_RE = re.compile(
    r"^\s*Red Hat OpenShift Documentation Team(?:\s+법적 공지)?(?:\s+초록)?\s*",
)
SOURCE_VIEW_TOC_RE = re.compile(r"^\s*목차\s*(?:\n\n|\n)?")




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
        str(settings.doc_to_book_books_dir),
        settings.request_timeout_seconds,
    )


def _runtime_fingerprint(settings: Settings) -> str:
    raw = "|".join(str(item) for item in _llm_runtime_signature(settings))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def _refresh_answerer_llm_settings(
    answerer: Part3Answerer,
    *,
    root_dir: Path,
    current_signature: tuple[Any, ...] | None,
) -> tuple[Part3Answerer, tuple[Any, ...]]:
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


def _build_health_payload(answerer: Part3Answerer) -> dict[str, Any]:
    settings = answerer.settings
    pack = settings.active_pack
    embedding_mode = "remote" if settings.embedding_base_url else "local"
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
            "llm_fallback_enabled": bool(llm_runtime.get("fallback_enabled", True)),
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
            "artifacts_dir": str(settings.artifacts_dir),
            "source_manifest_path": str(settings.source_manifest_path),
            "normalized_docs_path": str(settings.normalized_docs_path),
            "bm25_corpus_path": str(settings.bm25_corpus_path),
            "doc_to_book_books_dir": str(settings.doc_to_book_books_dir),
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
    if not manifest_path.exists():
        return {}
    return _load_manifest_entries(
        str(manifest_path),
        manifest_path.stat().st_mtime_ns,
    ).get(book_slug, {})


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


def _parse_doc_to_book_viewer_path(viewer_path: str) -> tuple[str, str] | None:
    value = (viewer_path or "").strip()
    if "#" in value:
        path_part, anchor = value.split("#", 1)
    else:
        path_part, anchor = value, ""
    prefix = "/docs/intake/"
    if not path_part.startswith(prefix):
        return None
    remainder = path_part[len(prefix) :]
    parts = [part for part in remainder.split("/") if part]
    if len(parts) != 2 or parts[1] != "index.html":
        return None
    return parts[0], anchor


def _doc_to_book_book_for_viewer_path(root_dir: Path, viewer_path: str) -> dict[str, Any] | None:
    parsed = _parse_doc_to_book_viewer_path(viewer_path)
    if parsed is None:
        return None
    draft_id, target_anchor = parsed
    record = DocToBookDraftStore(root_dir).get(draft_id)
    if record is None or not record.canonical_book_path.strip():
        return None
    canonical_path = Path(record.canonical_book_path)
    if not canonical_path.exists():
        return None
    payload = json.loads(canonical_path.read_text(encoding="utf-8"))
    payload["draft_id"] = record.draft_id
    payload["target_viewer_path"] = f"/docs/intake/{record.draft_id}/index.html"
    payload["target_anchor"] = target_anchor
    payload["source_origin_url"] = f"/api/doc-to-book/captured?draft_id={record.draft_id}"
    payload.setdefault("source_collection", record.plan.source_collection)
    payload.setdefault("pack_id", record.plan.pack_id)
    payload.setdefault("pack_label", record.plan.pack_label)
    payload.setdefault("inferred_product", record.plan.inferred_product)
    payload.setdefault("inferred_version", record.plan.inferred_version)
    payload.update(evaluate_canonical_book_quality(payload))
    return payload


def _doc_to_book_meta_for_viewer_path(root_dir: Path, viewer_path: str) -> dict[str, Any] | None:
    payload = _doc_to_book_book_for_viewer_path(root_dir, viewer_path)
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
    section_path = [str(item) for item in (target.get("section_path") or []) if str(item).strip()]
    return {
        "book_slug": str(payload.get("book_slug") or ""),
        "book_title": str(payload.get("title") or payload.get("book_slug") or ""),
        "anchor": str(target.get("anchor") or target_anchor),
        "section": str(target.get("heading") or ""),
        "section_path": section_path,
        "section_path_label": (
            str(target.get("section_path_label") or "").strip()
            or (" > ".join(section_path) if section_path else str(target.get("heading") or ""))
        ),
        "source_url": str(payload.get("source_origin_url") or target.get("source_url") or payload.get("source_uri") or ""),
        "viewer_path": viewer_path,
        "source_collection": str(payload.get("source_collection") or "uploaded"),
        "pack_id": str(payload.get("pack_id") or ""),
        "pack_label": str(payload.get("pack_label") or ""),
        "inferred_product": str(payload.get("inferred_product") or "unknown"),
        "inferred_version": str(payload.get("inferred_version") or "unknown"),
        "quality_status": str(payload.get("quality_status") or "ready"),
        "quality_score": int(payload.get("quality_score") or 0),
        "quality_summary": str(payload.get("quality_summary") or ""),
        "quality_flags": list(payload.get("quality_flags") or []),
        "section_match_exact": matched_exact,
    }


def _default_doc_to_book_summary(payload: dict[str, Any]) -> str:
    source_type = str(payload.get("source_type") or "").strip().lower()
    if source_type == "pdf":
        return (
            "capture된 PDF를 canonical section으로 정리한 내부 study view입니다. "
            "이후 retrieval chunk는 이 section들을 부모로 파생됩니다."
        )
    return (
        "capture된 웹 문서를 canonical section으로 정리한 내부 study view입니다. "
        "이후 retrieval chunk는 이 section들을 부모로 파생됩니다."
    )


def _clean_source_view_text(text: str) -> str:
    cleaned = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    cleaned = SOURCE_VIEW_LEADING_NOISE_RE.sub("", cleaned, count=1).lstrip()
    cleaned = SOURCE_VIEW_TOC_RE.sub("", cleaned, count=1).lstrip()
    return cleaned


def _normalized_row_for_viewer_path(root_dir: Path, viewer_path: str) -> dict[str, Any] | None:
    row, _matched_exact = _resolve_normalized_row_for_viewer_path(root_dir, viewer_path)
    return row


def _resolve_normalized_row_for_viewer_path(
    root_dir: Path,
    viewer_path: str,
) -> tuple[dict[str, Any] | None, bool]:
    parsed = _parse_viewer_path(viewer_path)
    if parsed is None:
        return None, False
    book_slug, anchor = parsed
    settings = load_settings(root_dir)
    normalized_docs_path = settings.normalized_docs_path
    if not normalized_docs_path.exists():
        return None, False
    sections_by_book = _load_normalized_sections(
        str(normalized_docs_path),
        normalized_docs_path.stat().st_mtime_ns,
    )
    sections = sections_by_book.get(book_slug, [])
    if not sections:
        return None, False
    if not anchor:
        return sections[0], True

    for row in sections:
        if str(row.get("anchor") or "").strip() == anchor:
            return row, True
    return sections[0], False


def _serialize_citation(root_dir: Path, citation: Citation) -> dict[str, Any]:
    settings = load_settings(root_dir)
    href = _citation_href(citation)
    row, matched_exact = _resolve_normalized_row_for_viewer_path(root_dir, href)
    doc_to_book_meta = _doc_to_book_meta_for_viewer_path(root_dir, href)
    manifest_entry = _manifest_entry_for_book(root_dir, citation.book_slug)

    if row is None and doc_to_book_meta is not None:
        book_title = str(doc_to_book_meta.get("book_title") or "") or _humanize_book_slug(citation.book_slug)
        section_path = [
            str(item)
            for item in (doc_to_book_meta.get("section_path") or [])
            if str(item).strip()
        ]
        section_label = (
            str(doc_to_book_meta.get("section_path_label") or "").strip()
            or citation.section
            or citation.anchor
        )
        return {
            **citation.to_dict(),
            "href": href,
            "book_title": book_title,
            "section_path": section_path,
            "section_path_label": section_label,
            "source_label": f"{book_title} · {section_label}" if section_label else book_title,
            "source_collection": str(doc_to_book_meta.get("source_collection") or "uploaded"),
            "pack_id": str(doc_to_book_meta.get("pack_id") or ""),
            "pack_label": str(doc_to_book_meta.get("pack_label") or ""),
            "inferred_product": str(doc_to_book_meta.get("inferred_product") or "unknown"),
            "inferred_version": str(doc_to_book_meta.get("inferred_version") or "unknown"),
            "section_match_exact": bool(doc_to_book_meta.get("section_match_exact", True)),
        }

    book_title = (
        str((row or {}).get("book_title") or "")
        or str(manifest_entry.get("title") or "")
        or _humanize_book_slug(citation.book_slug)
    )
    section_path = [
        str(item)
        for item in ((row or {}).get("section_path") or [])
        if str(item).strip()
    ]
    section_label = " > ".join(section_path) if section_path else citation.section or citation.anchor
    return {
        **citation.to_dict(),
        "href": href,
        "book_title": book_title,
        "section_path": section_path,
        "section_path_label": section_label,
        "source_label": f"{book_title} · {section_label}" if section_label else book_title,
        **_core_pack_payload(version=settings.ocp_version, language=settings.docs_language),
        "section_match_exact": matched_exact,
    }
