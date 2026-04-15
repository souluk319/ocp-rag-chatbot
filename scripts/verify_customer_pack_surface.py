from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.answering.models import Citation
from play_book_studio.config.settings import load_settings
from play_book_studio.app.presenters import _customer_pack_meta_for_viewer_path, _serialize_citation
from play_book_studio.app.source_books import internal_customer_pack_viewer_html, load_customer_pack_book


def main() -> int:
    root_dir = Path(__file__).resolve().parents[1]
    settings = load_settings(root_dir)
    draft_id = "synthetic-customer-pack"
    book_slug = "synthetic_customer_pack"
    viewer_path = f"/playbooks/customer-packs/{draft_id}/index.html"
    store_dir = settings.customer_pack_drafts_dir
    books_dir = settings.customer_pack_books_dir
    source_file = root_dir / "tmp_customer_pack_surface.md"
    report_path = root_dir / "reports" / "build_logs" / "customer_pack_surface_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    draft_payload = {
        "draft_id": draft_id,
        "status": "normalized",
        "created_at": "2026-04-14T00:00:00Z",
        "updated_at": "2026-04-14T00:10:00Z",
        "request": {
            "source_type": "md",
            "uri": str(source_file),
            "title": "Synthetic Customer Pack",
            "language_hint": "ko",
        },
        "plan": {
            "book_slug": book_slug,
            "title": "Synthetic Customer Pack",
            "source_type": "md",
            "source_uri": str(source_file),
            "source_collection": "uploaded",
            "pack_id": "custom-uploaded-surface",
            "pack_label": "Synthetic Customer Pack",
            "inferred_product": "custom",
            "inferred_version": "n/a",
            "acquisition_uri": str(source_file),
            "capture_strategy": "uploaded_file_copy",
            "canonical_model": "canonical_book_v1",
            "source_view_strategy": "source_view_first",
            "retrieval_derivation": "chunks_from_canonical_sections",
        },
        "uploaded_file_name": source_file.name,
        "uploaded_file_path": str(source_file),
        "uploaded_byte_size": 128,
        "capture_artifact_path": str(source_file),
        "capture_content_type": "text/markdown",
        "capture_byte_size": 128,
        "source_lane": "customer_source_first_pack",
        "source_fingerprint": "abc123synthetic",
        "parser_route": "md_customer_pack_normalize_v1",
        "parser_backend": "customer_pack_normalize_service",
        "parser_version": "v1",
        "ocr_used": False,
        "extraction_confidence": 0.93,
        "tenant_id": "default-tenant",
        "workspace_id": "default-workspace",
        "approval_state": "unreviewed",
        "publication_state": "draft",
        "canonical_book_path": str(books_dir / f"{draft_id}.json"),
        "normalized_section_count": 2,
        "normalize_error": "",
        "capture_error": "",
    }
    canonical_payload = {
        "book_slug": book_slug,
        "title": "Synthetic Customer Pack",
        "source_type": "md",
        "source_uri": str(source_file),
        "source_collection": "uploaded",
        "pack_id": "custom-uploaded-surface",
        "pack_label": "Synthetic Customer Pack",
        "inferred_product": "custom",
        "inferred_version": "n/a",
        "playable_asset_count": 1,
        "derived_asset_count": 0,
        "derived_assets": [],
        "sections": [
            {
                "heading": "Overview",
                "section_path": ["Overview"],
                "section_path_label": "Overview",
                "anchor": "overview",
                "viewer_path": viewer_path,
                "text": "customer pack runtime evidence surface",
                "blocks": [{"kind": "paragraph", "text": "customer pack runtime evidence surface"}],
            },
            {
                "heading": "Procedure",
                "section_path": ["Procedure"],
                "section_path_label": "Procedure",
                "anchor": "procedure",
                "viewer_path": f"{viewer_path}#procedure",
                "text": "follow the steps",
                "blocks": [{"kind": "paragraph", "text": "follow the steps"}],
            },
        ],
    }

    store_dir.mkdir(parents=True, exist_ok=True)
    books_dir.mkdir(parents=True, exist_ok=True)
    source_file.write_text("# Synthetic Customer Pack\n", encoding="utf-8")
    draft_file = store_dir / f"{draft_id}.json"
    book_file = books_dir / f"{draft_id}.json"
    draft_file.write_text(json.dumps(draft_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    book_file.write_text(json.dumps(canonical_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    try:
        loaded_book = load_customer_pack_book(root_dir, draft_id)
        viewer_html = internal_customer_pack_viewer_html(root_dir, viewer_path) or ""
        meta_payload = _customer_pack_meta_for_viewer_path(root_dir, viewer_path) or {}
        citation_payload = _serialize_citation(
            root_dir,
            Citation(
                index=1,
                chunk_id="synthetic-1",
                book_slug=book_slug,
                section="Overview",
                anchor="overview",
                source_url=str(source_file),
                viewer_path=viewer_path,
                excerpt="customer pack runtime evidence surface",
            ),
        )
        report = {
            "status": "ok",
            "loaded_book_has_evidence": bool((loaded_book or {}).get("customer_pack_evidence")),
            "loaded_book_runtime_truth_label": str((loaded_book or {}).get("runtime_truth_label") or ""),
            "viewer_has_runtime_truth": "Customer Source-First Pack" in viewer_html,
            "viewer_has_boundary_badge": "Private Pack Runtime" in viewer_html,
            "viewer_has_parser_backend": "customer_pack_normalize_service" in viewer_html,
            "source_meta_source_lane": str(meta_payload.get("source_lane") or ""),
            "source_meta_publication_state": str(meta_payload.get("publication_state") or ""),
            "citation_boundary_truth": str(citation_payload.get("boundary_truth") or ""),
            "citation_runtime_truth_label": str(citation_payload.get("runtime_truth_label") or ""),
            "citation_publication_state": str(citation_payload.get("publication_state") or ""),
        }
    finally:
        for target in (draft_file, book_file, source_file):
            if target.exists():
                target.unlink()

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
