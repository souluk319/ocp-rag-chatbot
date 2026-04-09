# chat / chat-stream 처리 흐름을 server.py 밖으로 분리한다.
from __future__ import annotations

import uuid
from http import HTTPStatus
from pathlib import Path
from typing import Any

from play_book_studio.retrieval.models import SessionContext
from play_book_studio.app.sessions import RUNTIME_CHAT_MODE, Turn


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
        handler._send_json({"error": "질문을 입력해 주세요."}, HTTPStatus.BAD_REQUEST)
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
    session.history.append(
        Turn(
            query=query,
            mode=mode,
            answer=result.answer,
            rewritten_query=result.rewritten_query,
            response_kind=result.response_kind,
            warnings=list(result.warnings),
            stages=build_turn_stages(result),
            diagnosis=build_turn_diagnosis(result),
        )
    )
    session.history = session.history[-20:]
    store.update(session)
    append_chat_turn_log(
        root_dir,
        answerer=active_answerer,
        session=session,
        query=query,
        result=result,
        context_before=context_before,
        context_after=session.context,
    )
    write_recent_chat_session_snapshot(root_dir, session=session)
    handler._send_json(
        build_chat_payload(
            root_dir=root_dir,
            answerer=active_answerer,
            session=session,
            result=result,
        )
    )


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
        handler._send_json({"error": "질문을 입력해 주세요."}, HTTPStatus.BAD_REQUEST)
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
    session.history.append(
        Turn(
            query=query,
            mode=mode,
            answer=result.answer,
            rewritten_query=result.rewritten_query,
            response_kind=result.response_kind,
            warnings=list(result.warnings),
            stages=build_turn_stages(result),
            diagnosis=build_turn_diagnosis(result),
        )
    )
    session.history = session.history[-20:]
    store.update(session)
    append_chat_turn_log(
        root_dir,
        answerer=active_answerer,
        session=session,
        query=query,
        result=result,
        context_before=context_before,
        context_after=session.context,
    )
    write_recent_chat_session_snapshot(root_dir, session=session)
    handler._stream_event(
        {
            "type": "result",
            "payload": build_chat_payload(
                root_dir=root_dir,
                answerer=active_answerer,
                session=session,
                result=result,
            ),
        }
    )
