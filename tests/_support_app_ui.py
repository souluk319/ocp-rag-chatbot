from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.retrieval.models import SessionContext
from play_book_studio.answering.models import AnswerResult, Citation
from play_book_studio.app.presenters import _clean_source_view_text
from play_book_studio.app.session_flow import (
    context_with_request_overrides as _context_with_request_overrides,
    derive_next_context as _derive_next_context,
    suggest_follow_up_questions as _suggest_follow_up_questions,
)
from play_book_studio.app.server import (
    ChatSession,
    Turn,
    _build_health_payload,
    _build_turn_diagnosis,
    _build_doc_to_book_plan,
    _build_session_debug_payload,
    _capture_doc_to_book_draft,
    _canonical_source_book,
    _create_doc_to_book_draft,
    _citation_href,
    _doc_to_book_meta_for_viewer_path,
    _internal_doc_to_book_viewer_html,
    _internal_viewer_html,
    _list_doc_to_book_drafts,
    _load_doc_to_book_book,
    _load_doc_to_book_capture,
    _load_doc_to_book_draft,
    _normalize_doc_to_book_draft,
    _append_chat_turn_log,
    _write_recent_chat_session_snapshot,
    _refresh_answerer_llm_settings,
    _serialize_citation,
    _upload_doc_to_book_draft,
    _viewer_path_to_local_html,
)


def _citation(
    index: int,
    *,
    anchor: str = "overview",
    section: str = "OpenShift 아키텍처 개요",
    book_slug: str = "architecture",
) -> Citation:
    return Citation(
        index=index,
        chunk_id=f"chunk-{index}",
        book_slug=book_slug,
        section=section,
        anchor=anchor,
        source_url="https://example.com/architecture/index",
        viewer_path="/docs/ocp/4.20/ko/architecture/index.html#overview",
        excerpt="OpenShift 아키텍처 개요",
    )



__all__ = [name for name in globals() if not name.startswith('__')]
