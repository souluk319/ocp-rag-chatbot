from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.app.data_control_room import build_data_control_room_payload
from play_book_studio.config.settings import load_settings
from play_book_studio.intake import CustomerPackDraftStore, DocSourceRequest


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    settings = load_settings(root)
    store = CustomerPackDraftStore(root)

    request = DocSourceRequest(
        source_type="txt",
        uri="synthetic-customer-pack.txt",
        title="Synthetic Customer Pack",
        language_hint="ko",
    )
    record = store.create(request)
    record.source_lane = "customer_source_first_pack"
    record.parser_backend = "customer_pack_normalize_service"
    record.approval_state = "unreviewed"
    record.publication_state = "draft"

    canonical_path = settings.customer_pack_books_dir / f"{record.draft_id}.json"
    record.canonical_book_path = str(canonical_path)
    store.save(record)

    canonical_payload = {
        "draft_id": record.draft_id,
        "book_slug": record.draft_id,
        "title": "Synthetic Customer Pack",
        "source_type": "txt",
        "target_viewer_path": f"/playbooks/customer-packs/{record.draft_id}/index.html",
        "viewer_path": f"/playbooks/customer-packs/{record.draft_id}/index.html",
        "sections": [
            {
                "heading": "Overview",
                "section_path_label": "Overview",
                "viewer_path": f"/playbooks/customer-packs/{record.draft_id}/index.html#overview",
                "blocks": [{"kind": "paragraph", "text": "synthetic section"}],
            }
        ],
        "source_metadata": {
            "source_collection": "customer_pack",
            "updated_at": "2026-04-14T00:00:00+09:00",
        },
    }
    canonical_path.write_text(json.dumps(canonical_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    try:
        payload = build_data_control_room_payload(root)
        bucket = payload.get("customer_pack_runtime_books") or {}
        books = bucket.get("books") or []
        target = next((book for book in books if str(book.get("book_slug") or "") == record.draft_id), {})
        report = {
            "status": "ok",
            "customer_pack_bucket_count": len(books),
            "summary_customer_pack_runtime_book_count": payload.get("summary", {}).get("customer_pack_runtime_book_count"),
            "target_found": bool(target),
            "target_boundary_truth": str(target.get("boundary_truth") or ""),
            "target_runtime_truth_label": str(target.get("runtime_truth_label") or ""),
            "target_boundary_badge": str(target.get("boundary_badge") or ""),
            "target_source_lane": str(target.get("source_lane") or ""),
            "target_publication_state": str(target.get("publication_state") or ""),
            "target_parser_backend": str(target.get("parser_backend") or ""),
        }
        if not (
            report["target_found"]
            and report["target_boundary_truth"] == "private_customer_pack_runtime"
            and report["target_runtime_truth_label"] == "Customer Source-First Pack"
            and report["target_boundary_badge"] == "Private Pack Runtime"
            and report["target_source_lane"] == "customer_source_first_pack"
            and report["target_publication_state"] == "draft"
        ):
            report["status"] = "failed"
            raise SystemExit(json.dumps(report, ensure_ascii=False))
    finally:
        canonical_path.unlink(missing_ok=True)
        store.delete(record.draft_id)

    report_path = root / "reports" / "build_logs" / "customer_pack_library_surface_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
