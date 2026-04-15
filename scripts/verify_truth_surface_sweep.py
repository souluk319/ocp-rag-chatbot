from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

from play_book_studio.app.source_books import internal_customer_pack_viewer_html
from play_book_studio.config.settings import load_settings

BASE_URL = "http://127.0.0.1:8765"


def fetch_text(path: str) -> str:
    request = urllib.request.Request(f"{BASE_URL}{path}", headers={"User-Agent": "codex-truth-sweep"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    tsx = (root / "presentation-ui" / "src" / "pages" / "WorkspacePage.tsx").read_text(encoding="utf-8")
    css = (root / "presentation-ui" / "src" / "pages" / "WorkspacePage.css").read_text(encoding="utf-8")
    source_books = (root / "src" / "play_book_studio" / "app" / "source_books.py").read_text(encoding="utf-8")

    sessions_payload = json.loads(fetch_text("/api/sessions"))
    settings = load_settings(root)
    draft_id = "synthetic-customer-pack-sweep"
    viewer_path = f"/playbooks/customer-packs/{draft_id}/index.html"
    store_dir = settings.customer_pack_drafts_dir
    books_dir = settings.customer_pack_books_dir
    source_file = root / "tmp_customer_pack_surface_sweep.md"

    draft_payload = {
        "draft_id": draft_id,
        "status": "normalized",
        "created_at": "2026-04-15T00:00:00Z",
        "updated_at": "2026-04-15T00:10:00Z",
        "request": {"source_type": "md", "uri": str(source_file), "title": "Synthetic Customer Pack Sweep", "language_hint": "ko"},
        "plan": {
            "book_slug": "synthetic_customer_pack_sweep",
            "title": "Synthetic Customer Pack Sweep",
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
        "source_fingerprint": "sweep123",
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
        "normalized_section_count": 1,
        "normalize_error": "",
        "capture_error": "",
    }
    canonical_payload = {
        "book_slug": "synthetic_customer_pack_sweep",
        "title": "Synthetic Customer Pack Sweep",
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
                "text": "compact truth surface",
                "blocks": [{"kind": "paragraph", "text": "compact truth surface"}],
            }
        ],
    }

    store_dir.mkdir(parents=True, exist_ok=True)
    books_dir.mkdir(parents=True, exist_ok=True)
    source_file.write_text("# Synthetic Customer Pack Sweep\n", encoding="utf-8")
    draft_file = store_dir / f"{draft_id}.json"
    book_file = books_dir / f"{draft_id}.json"
    draft_file.write_text(json.dumps(draft_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    book_file.write_text(json.dumps(canonical_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        viewer_html = internal_customer_pack_viewer_html(root, viewer_path) or ""
    finally:
        for target in (draft_file, book_file, source_file):
            if target.exists():
                target.unlink()

    viewer_truth_title_count = len(re.findall(r'<div class="viewer-truth-title">', viewer_html))
    viewer_meta_pill_count = len(re.findall(r'<span class="meta-pill">', viewer_html))

    report = {
        "status": "ok",
        "assistant_truth_compact_source": "badgeClassName=\"assistant-truth-chip\"" in tsx and "showMeta={false}" in tsx,
        "session_truth_compact_source": "badgeClassName=\"session-truth-chip\"" in tsx and tsx.count("showMeta={false}") >= 2,
        "related_link_summary_first_source": "const meta = link.summary ? [link.summary] : [];" in tsx,
        "citation_truth_still_card_based": "function CitationTag" in tsx and "citation-tag-title" in css,
        "customer_viewer_compact_copy_source": "customer source-first private runtime 문서다. 아래 evidence 로 현재 상태만 확인하면 된다." in source_books,
        "customer_viewer_live_truth_block": "viewer-truth-badge" in viewer_html and "viewer-truth-title" in viewer_html,
        "customer_viewer_live_single_truth_title": viewer_truth_title_count == 1,
        "customer_viewer_live_meta_pills_trimmed": viewer_meta_pill_count <= 4,
        "sessions_api_live_ok": isinstance(sessions_payload, dict) and "sessions" in sessions_payload,
    }
    if not all(report.values()):
        report["status"] = "failed"
        report["viewer_truth_title_count"] = viewer_truth_title_count
        report["viewer_meta_pill_count"] = viewer_meta_pill_count
        raise SystemExit(json.dumps(report, ensure_ascii=False))

    report["viewer_truth_title_count"] = viewer_truth_title_count
    report["viewer_meta_pill_count"] = viewer_meta_pill_count
    out = root / "reports" / "build_logs" / "truth_surface_sweep_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
