from __future__ import annotations

# retrieval query rewrite 공개 허브.
# 실제 무거운 구현은 book_adjustments/query_terms로 분리하고,
# 바깥에서는 기존 import 경로를 계속 유지한다.

from .followups import has_follow_up_reference
from .models import SessionContext
from .text_utils import collapse_spaces as _collapse_spaces, token_count as _token_count
from .intents import has_explicit_topic_signal
from .book_adjustments import query_book_adjustments
from .query_terms import normalize_query


def needs_rewrite(query: str, context: SessionContext) -> bool:
    normalized = _collapse_spaces(query)
    if not normalized:
        return False
    if not any(
        [
            context.current_topic,
            context.user_goal,
            context.open_entities,
            context.ocp_version,
            context.unresolved_question,
        ]
    ):
        return False

    if has_follow_up_reference(normalized):
        return True
    if has_explicit_topic_signal(normalized):
        return False
    return _token_count(normalized) <= 3


def rewrite_query(query: str, context: SessionContext | None = None) -> str:
    normalized = query
    context = context or SessionContext()
    if not needs_rewrite(normalized, context):
        return normalized

    hints: list[str] = []
    if context.ocp_version:
        hints.append(f"OCP {context.ocp_version}")
    if context.current_topic:
        hints.append(f"주제 {context.current_topic}")
    if context.open_entities:
        hints.append(f"엔터티 {', '.join(context.open_entities)}")
    if context.unresolved_question:
        hints.append(f"미해결 질문 {context.unresolved_question}")
    elif context.user_goal:
        hints.append(f"사용자 목표 {context.user_goal}")
    hints.append(normalized)
    return " | ".join(hints)


__all__ = [
    "has_explicit_topic_signal",
    "needs_rewrite",
    "normalize_query",
    "query_book_adjustments",
    "rewrite_query",
]
