from __future__ import annotations

# captured source를 canonical study asset으로 바꾸는 normalize service 구현.

import json
from datetime import datetime, timezone
from pathlib import Path

from play_book_studio.config.settings import load_settings

from ..books.store import CustomerPackDraftStore
from ..models import CustomerPackDraftRecord
from ..service import build_customer_pack_playable_books
from .builders import build_canonical_book
from .pdf import (
    extract_pdf_markdown_with_docling,
    extract_pdf_markdown_with_docling_ocr,
    extract_pdf_outline,
    extract_pdf_pages,
)
from .pdf_rows import (
    _build_pdf_rows_from_docling_markdown,
    _prepare_pdf_page_text,
    _segment_pdf_page,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class CustomerPackNormalizeService:
    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)
        self.settings = load_settings(self.root_dir)
        self.store = CustomerPackDraftStore(self.root_dir)

    def normalize(self, *, draft_id: str) -> CustomerPackDraftRecord:
        record = self.store.get(draft_id.strip())
        if record is None:
            raise ValueError("업로드 플레이북 초안을 찾을 수 없습니다.")
        if not record.capture_artifact_path.strip():
            raise ValueError("먼저 capture를 실행해서 source artifact를 확보해야 합니다.")

        try:
            canonical_book = build_canonical_book(
                record,
                extract_pdf_markdown_with_docling_fn=extract_pdf_markdown_with_docling,
                extract_pdf_markdown_with_docling_ocr_fn=extract_pdf_markdown_with_docling_ocr,
                extract_pdf_outline_fn=extract_pdf_outline,
                extract_pdf_pages_fn=extract_pdf_pages,
            )
            canonical_payload, derived_payloads = build_customer_pack_playable_books(
                canonical_book.to_dict(),
                draft_id=record.draft_id,
            )
            book_path = self.settings.customer_pack_books_dir / f"{record.draft_id}.json"
            for stale_path in self.settings.customer_pack_books_dir.glob(f"{record.draft_id}--*.json"):
                stale_path.unlink(missing_ok=True)
            book_path.write_text(
                json.dumps(canonical_payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            for derived_payload in derived_payloads:
                asset_slug = str(derived_payload.get("asset_slug") or "").strip()
                if not asset_slug:
                    continue
                (self.settings.customer_pack_books_dir / f"{asset_slug}.json").write_text(
                    json.dumps(derived_payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            record.status = "normalized"
            record.canonical_book_path = str(book_path)
            record.normalized_section_count = len(canonical_book.sections)
            record.normalize_error = ""
        except Exception as exc:  # noqa: BLE001
            record.status = "normalize_failed"
            record.normalize_error = str(exc)
            record.updated_at = _utc_now()
            self.store.save(record)
            raise

        record.updated_at = _utc_now()
        self.store.save(record)
        return record

