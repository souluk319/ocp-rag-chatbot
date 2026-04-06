from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ocp_rag_part1.models import SourceManifestEntry
from ocp_rag_part1.normalize import extract_sections
from ocp_rag_part1.settings import load_settings

from ..books.store import DocToBookDraftStore
from ..models import DocToBookDraftRecord
from ..service import DocToBookPlanner


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class DocToBookNormalizeService:
    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)
        self.settings = load_settings(self.root_dir)
        self.store = DocToBookDraftStore(self.root_dir)

    def normalize(self, *, draft_id: str) -> DocToBookDraftRecord:
        record = self.store.get(draft_id.strip())
        if record is None:
            raise ValueError("doc-to-book draft를 찾을 수 없습니다.")
        if not record.capture_artifact_path.strip():
            raise ValueError("먼저 capture를 실행해서 source artifact를 확보해야 합니다.")

        try:
            canonical_book = self._build_canonical_book(record)
            book_path = self.settings.doc_to_book_books_dir / f"{record.draft_id}.json"
            book_path.write_text(
                json.dumps(canonical_book.to_dict(), ensure_ascii=False, indent=2) + "\n",
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

    def _build_canonical_book(self, record: DocToBookDraftRecord):
        if record.request.source_type != "web":
            raise ValueError("지금 normalize는 web source에 대해서만 지원합니다. PDF는 text extraction 단계가 더 필요합니다.")

        capture_path = Path(record.capture_artifact_path)
        if not capture_path.exists():
            raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")

        html = capture_path.read_text(encoding="utf-8")
        manifest_entry = SourceManifestEntry(
            book_slug=record.plan.book_slug,
            title=record.plan.title,
            source_url=record.request.uri,
            viewer_path=f"/docs/intake/{record.draft_id}/index.html",
            high_value=False,
            viewer_strategy="internal_text",
            body_language_guess=record.request.language_hint,
            approval_status="derived",
        )
        sections = extract_sections(html, manifest_entry)
        if not sections:
            raise ValueError("capture한 문서에서 canonical section을 만들지 못했습니다.")
        rows = [section.to_dict() for section in sections]
        return DocToBookPlanner().build_canonical_book(rows, request=record.request)
