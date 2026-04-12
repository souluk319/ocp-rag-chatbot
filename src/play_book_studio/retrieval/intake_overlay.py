# 업로드 문서를 retrieval overlay 인덱스로 바꾸는 보조 로직이다.
# canonical book JSON을 읽어서 BM25 overlay와 draft 선택 필터를 준비한다.
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from play_book_studio.intake.service import evaluate_canonical_book_quality

from .bm25 import BM25Index
from .models import RetrievalHit, SessionContext


def draft_id_from_intake_hit(hit: RetrievalHit) -> str:
    chunk_id = str(hit.chunk_id or "").strip()
    if ":" in chunk_id:
        return chunk_id.split(":", 1)[0].strip()
    viewer_path = str(hit.viewer_path or "").strip()
    match = re.match(r"^/playbooks/customer-packs/([^/]+)/", viewer_path)
    if match:
        return match.group(1).strip()
    return ""


def filter_customer_pack_hits_by_selection(
    hits: list[RetrievalHit],
    *,
    context: SessionContext | None = None,
) -> list[RetrievalHit]:
    context = context or SessionContext()
    if not context.restrict_uploaded_sources:
        return hits
    selected = {
        str(draft_id).strip()
        for draft_id in context.selected_draft_ids
        if str(draft_id).strip()
    }
    if not selected:
        return []
    return [hit for hit in hits if draft_id_from_intake_hit(hit) in selected]


def customer_pack_books_fingerprint(books_dir: Path) -> tuple[tuple[str, int], ...]:
    if not books_dir.exists():
        return ()
    return tuple(
        sorted(
            (path.name, path.stat().st_mtime_ns)
            for path in books_dir.glob("*.json")
            if path.is_file()
        )
    )


def customer_pack_row_from_section(
    payload: dict[str, object],
    section: dict[str, object],
    *,
    draft_id: str,
) -> dict[str, str]:
    anchor = str(section.get("anchor") or "").strip()
    viewer_path = str(section.get("viewer_path") or "").strip()
    if not viewer_path:
        viewer_path = f"/playbooks/customer-packs/{draft_id}/index.html"
        if anchor:
            viewer_path = f"{viewer_path}#{anchor}"
    section_path = [
        str(item).strip()
        for item in (section.get("section_path") or [])
        if str(item).strip()
    ]
    title = str(payload.get("title") or payload.get("book_slug") or draft_id).strip()
    return {
        "chunk_id": f"{draft_id}:{str(section.get('section_key') or anchor or section.get('ordinal') or 'section').strip()}",
        "book_slug": str(payload.get("book_slug") or draft_id).strip(),
        "chapter": section_path[0] if section_path else title,
        "section": str(section.get("heading") or section.get("section_path_label") or title).strip(),
        "section_path": section_path,
        "anchor": anchor,
        "source_url": str(section.get("source_url") or payload.get("source_uri") or "").strip(),
        "viewer_path": viewer_path,
        "text": str(section.get("text") or "").strip(),
        "source_id": f"customer_pack:{draft_id}",
        "source_lane": "customer_pack",
        "source_type": str(payload.get("playbook_family") or payload.get("source_type") or "customer_pack").strip(),
        "source_collection": "uploaded",
        "review_status": str(payload.get("quality_status") or "ready").strip() or "ready",
        "trust_score": 1.0,
        "semantic_role": str(section.get("semantic_role") or "unknown").strip(),
        "block_kinds": list(section.get("block_kinds") or []),
    }


@lru_cache(maxsize=4)
def load_customer_pack_overlay_index(
    books_dir_str: str,
    fingerprint: tuple[tuple[str, int], ...],
) -> BM25Index | None:
    del fingerprint
    books_dir = Path(books_dir_str)
    rows: list[dict[str, str]] = []
    for path in sorted(books_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if str(evaluate_canonical_book_quality(payload).get("quality_status") or "review") != "ready":
            continue
        sections = [
            dict(section)
            for section in (payload.get("sections") or [])
            if isinstance(section, dict)
        ]
        draft_id = path.stem
        for section in sections:
            row = customer_pack_row_from_section(payload, section, draft_id=draft_id)
            if row["text"]:
                rows.append(row)
    if not rows:
        return None
    return BM25Index.from_rows(rows)

