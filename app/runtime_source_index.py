from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip().lower()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _guess_product(document_path: str) -> str:
    lowered = _normalize_path(document_path)
    if lowered.startswith("rosa/"):
        return "rosa"
    if lowered.startswith("osd/"):
        return "osd"
    if lowered.startswith("microshift/"):
        return "microshift"
    if lowered.startswith("okd/"):
        return "okd"
    return "ocp"


def _section_anchor(document: dict[str, Any], section_title: str) -> str:
    normalized_section = section_title.strip().lower()
    if not normalized_section:
        return ""

    for section in document.get("sections", []) or []:
        title = str(section.get("section_title", "")).strip().lower()
        if title == normalized_section:
            return str(section.get("section_anchor", "")).strip()
    return ""


@dataclass(frozen=True)
class SourceCatalog:
    index_id: str
    manifest_path: Path
    documents: tuple[dict[str, Any], ...]
    by_html_path: dict[str, dict[str, Any]]
    by_viewer_url: dict[str, dict[str, Any]]
    by_document_path: dict[str, dict[str, Any]]

    @classmethod
    def from_active_index(cls) -> "SourceCatalog":
        repo_root = _repo_root()
        pointer_path = repo_root / "indexes" / "current.txt"
        index_id = pointer_path.read_text(encoding="utf-8").strip()
        if not index_id or index_id == "uninitialized":
            raise FileNotFoundError("Active runtime index is not initialized.")

        index_manifest_path = repo_root / "indexes" / index_id / "manifests" / "index-manifest.json"
        if not index_manifest_path.exists():
            raise FileNotFoundError(f"Active index manifest is missing: {index_manifest_path}")

        index_manifest = _load_json(index_manifest_path)
        index_documents = list(index_manifest.get("documents", []))
        staged_manifest_value = str(index_manifest.get("staged_manifest_path", "")).strip()
        staged_manifest_path = repo_root / staged_manifest_value if staged_manifest_value else index_manifest_path
        if staged_manifest_path.exists():
            manifest_payload = _load_json(staged_manifest_path)
            staged_documents = list(manifest_payload.get("documents", []))
        else:
            manifest_payload = index_manifest
            staged_documents = []

        if staged_documents:
            index_by_html: dict[str, dict[str, Any]] = {}
            index_by_viewer: dict[str, dict[str, Any]] = {}
            for document in index_documents:
                html_path = str(document.get("html_path", "")).strip()
                viewer_url = str(document.get("viewer_url", "")).strip()
                if html_path:
                    index_by_html[_normalize_path(html_path)] = document
                if viewer_url:
                    index_by_viewer[_normalize_path(viewer_url)] = document

            merged_documents: list[dict[str, Any]] = []
            matched_keys: set[str] = set()
            for document in staged_documents:
                html_path = str(document.get("html_path", "")).strip()
                viewer_url = str(document.get("viewer_url", "")).strip()
                match = index_by_html.get(_normalize_path(html_path)) or index_by_viewer.get(_normalize_path(viewer_url))
                merged = dict(match or {})
                merged.update(document)
                merged_documents.append(merged)
                if html_path:
                    matched_keys.add(_normalize_path(html_path))
            for document in index_documents:
                html_path = str(document.get("html_path", "")).strip()
                if html_path and _normalize_path(html_path) in matched_keys:
                    continue
                merged_documents.append(dict(document))
            documents = tuple(merged_documents)
        else:
            documents = tuple(index_documents)

        by_html_path: dict[str, dict[str, Any]] = {}
        by_viewer_url: dict[str, dict[str, Any]] = {}
        by_document_path: dict[str, dict[str, Any]] = {}
        for document in documents:
            html_path = str(document.get("html_path", "")).strip()
            viewer_url = str(document.get("viewer_url", "")).strip()
            document_path = str(document.get("document_path", "")).strip()
            if html_path:
                by_html_path[_normalize_path(html_path)] = document
            if viewer_url:
                by_viewer_url[_normalize_path(viewer_url)] = document
            if document_path:
                by_document_path[_normalize_path(document_path)] = document

        return cls(
            index_id=index_id,
            manifest_path=staged_manifest_path if staged_manifest_path.exists() else index_manifest_path,
            documents=documents,
            by_html_path=by_html_path,
            by_viewer_url=by_viewer_url,
            by_document_path=by_document_path,
        )

    def resolve_document(self, source_path: str) -> dict[str, Any]:
        normalized = _normalize_path(source_path)
        return self.by_html_path.get(normalized) or self.by_viewer_url.get(normalized) or {}

    def resolve_viewer_document(self, viewer_url: str) -> dict[str, Any]:
        return self.by_viewer_url.get(_normalize_path(viewer_url), {})

    def normalize_search_result(self, source: dict[str, Any], *, rank: int) -> dict[str, Any]:
        source_path = str(source.get("sourcePath", "")).strip()
        document = self.resolve_document(source_path)
        heading_hierarchy = [str(item).strip() for item in (source.get("headingHierarchy") or []) if str(item).strip()]
        section_title = heading_hierarchy[-1] if heading_hierarchy else ""
        section_anchor = _section_anchor(document, section_title)

        viewer_url = str(document.get("viewer_url", "")).strip() or source_path
        if section_anchor and "#" not in viewer_url:
            viewer_url = f"{viewer_url}#{section_anchor}"

        document_path = str(document.get("document_path", "")).strip()
        if not document_path and source_path:
            html_name = Path(source_path).name
            document_path = html_name.rsplit(".", 1)[0] + ".adoc"

        source_dir = str(document.get("top_level_dir", "")).strip()
        if not source_dir and document_path:
            source_dir = _normalize_path(document_path).split("/")[0]

        category = str(document.get("category", "")).strip()
        version = str(document.get("version", "")).strip()
        trust_level = str(document.get("trust_level", "")).strip() or "official"
        title = str(document.get("title", "")).strip()

        return {
            "rank": rank,
            "score": float(source.get("score", 0.0)),
            "source_dir": source_dir,
            "document_path": document_path,
            "viewer_url": viewer_url,
            "html_path": str(document.get("html_path", "")).strip(),
            "source_url": str(document.get("source_url", "")).strip(),
            "section_title": section_title,
            "section_anchor": section_anchor,
            "heading_hierarchy": heading_hierarchy,
            "title": title,
            "product": str(document.get("product", "")).strip() or _guess_product(document_path),
            "version": version,
            "category": category,
            "trust_level": trust_level,
            "top_level_dir": source_dir,
        }


@lru_cache(maxsize=1)
def load_active_source_catalog() -> SourceCatalog:
    return SourceCatalog.from_active_index()


def reset_active_source_catalog() -> None:
    load_active_source_catalog.cache_clear()
