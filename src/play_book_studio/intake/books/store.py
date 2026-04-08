from __future__ import annotations

# doc-to-book draft 레코드를 저장하고 읽는 draft store 구현.

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from play_book_studio.config.settings import load_settings

from ..models import DocSourceRequest, DocToBookDraftRecord
from ..planner import DocToBookPlanner


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class DocToBookDraftStore:
    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)
        self.settings = load_settings(self.root_dir)

    @property
    def drafts_dir(self) -> Path:
        return self.settings.doc_to_book_drafts_dir

    def create(self, request: DocSourceRequest) -> DocToBookDraftRecord:
        timestamp = _utc_now()
        draft_id = f"dtb-{uuid.uuid4().hex[:12]}"
        record = DocToBookDraftRecord(
            draft_id=draft_id,
            status="planned",
            created_at=timestamp,
            updated_at=timestamp,
            request=request,
            plan=DocToBookPlanner().plan(request),
        )
        self._write(record)
        return record

    def get(self, draft_id: str) -> DocToBookDraftRecord | None:
        path = self._draft_path(draft_id)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        return self._hydrate_legacy_pack_meta(DocToBookDraftRecord.from_dict(payload))

    def list(self) -> list[DocToBookDraftRecord]:
        records: list[DocToBookDraftRecord] = []
        for path in sorted(self.drafts_dir.glob("*.json"), reverse=True):
            payload = json.loads(path.read_text(encoding="utf-8"))
            records.append(self._hydrate_legacy_pack_meta(DocToBookDraftRecord.from_dict(payload)))
        records.sort(key=lambda record: (record.created_at, record.draft_id), reverse=True)
        return records

    def save(self, record: DocToBookDraftRecord) -> DocToBookDraftRecord:
        self._write(record)
        return record

    def _write(self, record: DocToBookDraftRecord) -> None:
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        self._draft_path(record.draft_id).write_text(
            json.dumps(record.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _draft_path(self, draft_id: str) -> Path:
        return self.drafts_dir / f"{draft_id}.json"

    def _hydrate_legacy_pack_meta(self, record: DocToBookDraftRecord) -> DocToBookDraftRecord:
        fallback = DocToBookPlanner().plan(record.request)
        if not record.plan.source_collection.strip():
            record.plan.source_collection = fallback.source_collection
        if (
            not record.plan.pack_id.strip()
            or record.plan.pack_id.strip() in {"custom-uploaded", "uploaded"}
        ):
            record.plan.pack_id = fallback.pack_id
        if (
            not record.plan.pack_label.strip()
            or record.plan.pack_label.strip() == "User Custom Pack"
        ):
            record.plan.pack_label = fallback.pack_label
        if not record.plan.inferred_product.strip() or record.plan.inferred_product.strip() == "unknown":
            record.plan.inferred_product = fallback.inferred_product
        if not record.plan.inferred_version.strip() or record.plan.inferred_version.strip() == "unknown":
            record.plan.inferred_version = fallback.inferred_version
        return record


__all__ = ["DocToBookDraftStore"]
