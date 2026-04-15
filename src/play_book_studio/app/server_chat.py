# chat / chat-stream 처리 흐름을 server.py 밖으로 분리한다.
from __future__ import annotations

import uuid
from http import HTTPStatus
from pathlib import Path
from typing import Any
from datetime import datetime

from play_book_studio.retrieval.models import SessionContext
from play_book_studio.app.sessions import RUNTIME_CHAT_MODE, Turn


def _summarize_citation_truth(response_payload: dict[str, Any]) -> dict[str, str]:
    citations = response_payload.get("citations")
    if not isinstance(citations, list) or not citations:
        return {}
    payloads = [item for item in citations if isinstance(item, dict)]
    if not payloads:
        return {}
    boundary_truths = {str(item.get("boundary_truth") or "").strip() for item in payloads if str(item.get("boundary_truth") or "").strip()}
    has_private = "private_customer_pack_runtime" in boundary_truths
    has_official = any(
        truth in {"official_validated_runtime", "official_candidate_runtime"}
        for truth in boundary_truths
    )
    if has_private and has_official:
        official_label = next(
            (
                str(item.get("runtime_truth_label") or "").strip()
                for item in payloads
                if str(item.get("boundary_truth") or "").strip() in {"official_validated_runtime", "official_candidate_runtime"}
                and str(item.get("runtime_truth_label") or "").strip()
            ),
            "Official Runtime",
        )
        private_label = next(
            (
                str(item.get("runtime_truth_label") or "").strip()
                for item in payloads
                if str(item.get("boundary_truth") or "").strip() == "private_customer_pack_runtime"
                and str(item.get("runtime_truth_label") or "").strip()
            ),
            "Private Runtime",
        )
        return {
            "source_lane": "mixed_runtime_bridge",
            "boundary_truth": "mixed_runtime_bridge",
            "runtime_truth_label": f"{official_label} + {private_label}",
            "boundary_badge": "Mixed Runtime",
            "publication_state": "mixed",
            "approval_state": "mixed",
        }
    primary = payloads[0]
    return {
        "source_lane": str(primary.get("source_lane") or ""),
        "boundary_truth": str(primary.get("boundary_truth") or ""),
        "runtime_truth_label": str(primary.get("runtime_truth_label") or ""),
        "boundary_badge": str(primary.get("boundary_badge") or ""),
        "publication_state": str(primary.get("publication_state") or ""),
        "approval_state": str(primary.get("approval_state") or ""),
    }


def _apply_primary_citation_truth(turn: Turn, response_payload: dict[str, Any]) -> None:
    summary = _summarize_citation_truth(response_payload)
    if not summary:
        return
    turn.primary_source_lane = str(summary.get("source_lane") or "")
    turn.primary_boundary_truth = str(summary.get("boundary_truth") or "")
    turn.primary_runtime_truth_label = str(summary.get("runtime_truth_label") or "")
    turn.primary_boundary_badge = str(summary.get("boundary_badge") or "")
    turn.primary_publication_state = str(summary.get("publication_state") or "")
    turn.primary_approval_state = str(summary.get("approval_state") or "")


def handle_chat(
    handler: Any,
    payload: dict[str, Any],
    *,
    current_answerer: Any,
    store: Any,
    root_dir: Path,
    build_chat_payload: Any,
    context_with_request_overrides: Any,
    derive_next_context: Any,
    append_chat_turn_log: Any,
    append_unanswered_question_log: Any,
    write_recent_chat_session_snapshot: Any,
    build_turn_stages: Any,
    build_turn_diagnosis: Any,
    suggest_follow_up_questions: Any | None = None,
) -> None:
    active_answerer = current_answerer()
    session_id = str(payload.get("session_id") or uuid.uuid4().hex)
    session = store.get(session_id)
    mode = RUNTIME_CHAT_MODE
    regenerate = bool(payload.get("regenerate", False))
    query = str(payload.get("query") or "").strip()
    request_context = context_with_request_overrides(
        session.context,
        payload=payload,
        mode=mode,
        default_ocp_version=active_answerer.settings.ocp_version,
    )
    context_before = SessionContext.from_dict(request_context.to_dict())
    if regenerate and not query:
        query = session.last_query

    if not query:
        handler._send_json({"error": "Query is required."}, HTTPStatus.BAD_REQUEST)
        return

    try:
        result = active_answerer.answer(
            query,
            mode=mode,
            context=request_context,
            top_k=8,
            candidate_k=20,
            max_context_chunks=6,
        )
        active_answerer.append_log(result)
    except Exception as exc:  # noqa: BLE001
        handler._send_json(
            {"error": f"답변 생성 중 오류가 발생했습니다: {exc}"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return

    session.mode = RUNTIME_CHAT_MODE
    session.context = derive_next_context(
        request_context,
        query=query,
        mode=mode,
        result=result,
        default_ocp_version=active_answerer.settings.ocp_version,
    )
    now = datetime.now().isoformat(timespec="seconds")
    parent_turn_id = session.history[-1].turn_id if session.history else ""
    turn = Turn(
        turn_id=uuid.uuid4().hex,
        parent_turn_id=parent_turn_id,
        created_at=now,
        query=query,
        mode=mode,
        answer=result.answer,
        rewritten_query=result.rewritten_query,
        response_kind=result.response_kind,
        warnings=list(result.warnings),
        stages=build_turn_stages(result),
        diagnosis=build_turn_diagnosis(result),
    )
    session.history.append(
        turn
    )
    session.history = session.history[-20:]
    session.revision += 1
    session.updated_at = now
    store.update(session)
    response_payload = build_chat_payload(
        root_dir=root_dir,
        answerer=active_answerer,
        session=session,
        result=result,
    )
    _apply_primary_citation_truth(turn, response_payload)
    store.update(session)
    append_chat_turn_log(
        root_dir,
        answerer=active_answerer,
        session=session,
        query=query,
        result=result,
        context_before=context_before,
        context_after=session.context,
        suggested_queries=response_payload.get("suggested_queries"),
        related_links=response_payload.get("related_links"),
        related_sections=response_payload.get("related_sections"),
    )
    if result.response_kind == "no_answer":
        append_unanswered_question_log(
            root_dir,
            session=session,
            query=query,
            result=result,
        )
    handler._send_json(response_payload)


def handle_chat_stream(
    handler: Any,
    payload: dict[str, Any],
    *,
    current_answerer: Any,
    store: Any,
    root_dir: Path,
    build_chat_payload: Any,
    context_with_request_overrides: Any,
    derive_next_context: Any,
    append_chat_turn_log: Any,
    append_unanswered_question_log: Any,
    write_recent_chat_session_snapshot: Any,
    build_turn_stages: Any,
    build_turn_diagnosis: Any,
) -> None:
    active_answerer = current_answerer()
    session_id = str(payload.get("session_id") or uuid.uuid4().hex)
    session = store.get(session_id)
    mode = RUNTIME_CHAT_MODE
    regenerate = bool(payload.get("regenerate", False))
    query = str(payload.get("query") or "").strip()
    request_context = context_with_request_overrides(
        session.context,
        payload=payload,
        mode=mode,
        default_ocp_version=active_answerer.settings.ocp_version,
    )
    context_before = SessionContext.from_dict(request_context.to_dict())
    if regenerate and not query:
        query = session.last_query

    if not query:
        handler._send_json({"error": "Query is required."}, HTTPStatus.BAD_REQUEST)
        return

    handler._start_ndjson_stream()
    handler._stream_event(
        {
            "type": "trace",
            "step": "request_received",
            "label": "질문 접수 완료",
            "status": "done",
            "detail": query[:180],
        }
    )

    def emit_trace(event: dict[str, Any]) -> None:
        handler._stream_event(event)

    try:
        result = active_answerer.answer(
            query,
            mode=mode,
            context=request_context,
            top_k=8,
            candidate_k=20,
            max_context_chunks=6,
            trace_callback=emit_trace,
        )
        active_answerer.append_log(result)
    except Exception as exc:  # noqa: BLE001
        handler._stream_event({"type": "error", "error": f"답변 생성 중 오류가 발생했습니다: {exc}"})
        return

    session.mode = RUNTIME_CHAT_MODE
    session.context = derive_next_context(
        request_context,
        query=query,
        mode=mode,
        result=result,
        default_ocp_version=active_answerer.settings.ocp_version,
    )
    now = datetime.now().isoformat(timespec="seconds")
    parent_turn_id = session.history[-1].turn_id if session.history else ""
    turn = Turn(
        turn_id=uuid.uuid4().hex,
        parent_turn_id=parent_turn_id,
        created_at=now,
        query=query,
        mode=mode,
        answer=result.answer,
        rewritten_query=result.rewritten_query,
        response_kind=result.response_kind,
        warnings=list(result.warnings),
        stages=build_turn_stages(result),
        diagnosis=build_turn_diagnosis(result),
    )
    session.history.append(
        turn
    )
    session.history = session.history[-20:]
    session.revision += 1
    session.updated_at = now
    store.update(session)
    response_payload = build_chat_payload(
        root_dir=root_dir,
        answerer=active_answerer,
        session=session,
        result=result,
    )
    _apply_primary_citation_truth(turn, response_payload)
    store.update(session)
    append_chat_turn_log(
        root_dir,
        answerer=active_answerer,
        session=session,
        query=query,
        result=result,
        context_before=context_before,
        context_after=session.context,
        suggested_queries=response_payload.get("suggested_queries"),
        related_links=response_payload.get("related_links"),
        related_sections=response_payload.get("related_sections"),
    )
    if result.response_kind == "no_answer":
        append_unanswered_question_log(
            root_dir,
            session=session,
            query=query,
            result=result,
        )
    handler._stream_event(
        {
            "type": "result",
            "payload": response_payload,
        }
    )
