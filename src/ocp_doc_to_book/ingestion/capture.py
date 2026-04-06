from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from ocp_rag_part1.collector import fetch_html_text
from ocp_rag_part1.settings import load_settings

from ..books.store import DocToBookDraftStore
from ..models import DocSourceRequest, DocToBookDraftRecord


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class DocToBookCaptureService:
    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)
        self.settings = load_settings(self.root_dir)
        self.store = DocToBookDraftStore(self.root_dir)

    def capture(
        self,
        *,
        draft_id: str = "",
        request: DocSourceRequest | None = None,
    ) -> DocToBookDraftRecord:
        record = self._load_or_create(draft_id=draft_id, request=request)
        try:
            if record.request.source_type == "web":
                artifact_path, content_type, byte_size = self._capture_web(record)
            else:
                artifact_path, content_type, byte_size = self._capture_pdf(record)
            record.status = "captured"
            record.capture_artifact_path = str(artifact_path)
            record.capture_content_type = content_type
            record.capture_byte_size = byte_size
            record.capture_error = ""
        except Exception as exc:  # noqa: BLE001
            record.status = "capture_failed"
            record.capture_error = str(exc)
            record.updated_at = _utc_now()
            self.store.save(record)
            raise

        record.updated_at = _utc_now()
        self.store.save(record)
        return record

    def _load_or_create(
        self,
        *,
        draft_id: str,
        request: DocSourceRequest | None,
    ) -> DocToBookDraftRecord:
        if draft_id.strip():
            existing = self.store.get(draft_id.strip())
            if existing is None:
                raise ValueError("doc-to-book draft를 찾을 수 없습니다.")
            return existing
        if request is None:
            raise ValueError("capture할 draft_id 또는 request가 필요합니다.")
        return self.store.create(request)

    def _capture_web(self, record: DocToBookDraftRecord) -> tuple[Path, str, int]:
        html = fetch_html_text(record.plan.acquisition_uri, self.settings)
        target_dir = self.settings.doc_to_book_capture_dir / record.draft_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "source.html"
        target.write_text(html, encoding="utf-8")
        return target, "text/html; charset=utf-8", len(html.encode("utf-8"))

    def _capture_pdf(self, record: DocToBookDraftRecord) -> tuple[Path, str, int]:
        source = Path(record.plan.acquisition_uri).expanduser()
        if not source.exists():
            raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {source}")
        suffix = source.suffix or ".pdf"
        target_dir = self.settings.doc_to_book_capture_dir / record.draft_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"source{suffix}"
        shutil.copy2(source, target)
        return target, "application/pdf", target.stat().st_size
