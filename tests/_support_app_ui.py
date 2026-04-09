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

from play_book_studio.answering.models import AnswerResult, Citation
from play_book_studio.app.chat_debug import (
    append_chat_turn_log as _append_chat_turn_log,
    build_session_debug_payload as _build_session_debug_payload,
    build_turn_diagnosis as _build_turn_diagnosis,
    write_recent_chat_session_snapshot as _write_recent_chat_session_snapshot,
)
from play_book_studio.app.intake_api import (
    build_doc_to_book_plan as _build_doc_to_book_plan,
    capture_doc_to_book_draft as _capture_doc_to_book_draft,
    create_doc_to_book_draft as _create_doc_to_book_draft,
    load_doc_to_book_capture as _load_doc_to_book_capture,
    load_doc_to_book_draft as _load_doc_to_book_draft,
    normalize_doc_to_book_draft as _normalize_doc_to_book_draft,
    upload_doc_to_book_draft as _upload_doc_to_book_draft,
)
from play_book_studio.app.presenters import (
    _build_health_payload,
    _citation_href,
    _clean_source_view_text,
    _doc_to_book_meta_for_viewer_path,
    _refresh_answerer_llm_settings,
    _serialize_citation,
)
from play_book_studio.app.server import _build_handler
from play_book_studio.app.session_flow import (
    context_with_request_overrides as _context_with_request_overrides,
    derive_next_context as _derive_next_context,
    suggest_follow_up_questions as _suggest_follow_up_questions,
)
from play_book_studio.app.sessions import ChatSession, SessionStore, Turn
from play_book_studio.app.source_books import (
    internal_doc_to_book_viewer_html as _internal_doc_to_book_viewer_html,
    internal_viewer_html as _internal_viewer_html,
    list_doc_to_book_drafts as _list_doc_to_book_drafts,
    load_doc_to_book_book as _load_doc_to_book_book,
)
from play_book_studio.app.viewers import _viewer_path_to_local_html
from play_book_studio.retrieval.models import SessionContext


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
