from __future__ import annotations

import json
import re
from pathlib import Path

from ocp_rag_part1.settings import Settings
from ocp_rag_part2 import Part2Retriever, SessionContext

from .confidence import calculate_confidence
from .context import assemble_context
from .llm import LLMClient
from .models import AnswerResult
from .prompt import build_messages


CITATION_RE = re.compile(r"\[(\d+)\]")
ANSWER_HEADER_RE = re.compile(
    r"^\s*(?:[#>*\-\s`]*)(?:답변|answer)\s*[:：]?\s*",
    re.IGNORECASE,
)
GUIDE_HEADER_RE = re.compile(
    r"(?:^|\n)\s*(?:[#>*\-\s`]*)(?:추가\s*가이드|additional guidance)\s*[:：]?\s*",
    re.IGNORECASE,
)
GREETING_PREFIXES = (
    "안녕하세요",
    "물론입니다",
    "좋습니다",
    "네,",
)


def normalize_answer_text(answer_text: str) -> str:
    normalized = (answer_text or "").strip()
    if not normalized:
        return "답변:"

    lines = [line.strip() for line in normalized.splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and any(lines[0].startswith(prefix) for prefix in GREETING_PREFIXES):
        lines.pop(0)

    normalized = "\n".join(lines).strip()
    normalized = ANSWER_HEADER_RE.sub("", normalized, count=1)
    for prefix in GREETING_PREFIXES:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :].lstrip(" ,:\n")
            break
    normalized = GUIDE_HEADER_RE.sub("\n\n추가 가이드: ", normalized)
    normalized = normalized.strip()

    if not normalized:
        return "답변:"
    if normalized.startswith("답변:"):
        return normalized
    return f"답변: {normalized}"


def summarize_session_context(context: SessionContext | None) -> str:
    if context is None:
        return ""

    parts: list[str] = []
    if context.current_topic:
        parts.append(f"- 현재 주제: {context.current_topic}")
    if context.open_entities:
        parts.append(f"- 열린 엔터티: {', '.join(context.open_entities)}")
    if context.unresolved_question:
        parts.append(f"- 미해결 질문: {context.unresolved_question}")
    elif context.user_goal:
        parts.append(f"- 사용자 목표: {context.user_goal}")
    if context.ocp_version:
        parts.append(f"- OCP 버전: {context.ocp_version}")
    if context.mode:
        parts.append(f"- 세션 모드: {context.mode}")
    return "\n".join(parts)


def resolved_query_for_prompt(query: str, rewritten_query: str) -> str:
    candidate = (rewritten_query or "").strip()
    if not candidate or candidate == (query or "").strip():
        return ""
    if " | " in candidate:
        return ""
    return candidate


class Part3Answerer:
    def __init__(
        self,
        settings: Settings,
        retriever: Part2Retriever,
        llm_client: LLMClient,
    ) -> None:
        self.settings = settings
        self.retriever = retriever
        self.llm_client = llm_client

    @classmethod
    def from_settings(cls, settings: Settings) -> "Part3Answerer":
        return cls(
            settings=settings,
            retriever=Part2Retriever.from_settings(settings, enable_vector=True),
            llm_client=LLMClient(settings),
        )

    def default_log_path(self) -> Path:
        return self.settings.part3_answer_log_path

    def append_log(self, result: AnswerResult, log_path: Path | None = None) -> Path:
        target = log_path or self.default_log_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
        return target

    def answer(
        self,
        query: str,
        *,
        mode: str = "ops",
        context: SessionContext | None = None,
        top_k: int = 5,
        candidate_k: int = 20,
        max_context_chunks: int = 6,
    ) -> AnswerResult:
        retrieval = self.retriever.retrieve(
            query,
            context=context,
            top_k=top_k,
            candidate_k=candidate_k,
        )
        context_bundle = assemble_context(
            retrieval.hits,
            max_chunks=max_context_chunks,
        )
        warnings: list[str] = []
        if not context_bundle.citations:
            warnings.append("no context citations assembled")

        messages = build_messages(
            query=query,
            mode=mode,
            context_bundle=context_bundle,
            session_summary=summarize_session_context(context),
            resolved_query=resolved_query_for_prompt(query, retrieval.rewritten_query),
        )
        answer_text = normalize_answer_text(self.llm_client.generate(messages))
        cited_indices = sorted(
            {
                int(match.group(1))
                for match in CITATION_RE.finditer(answer_text)
                if 1 <= int(match.group(1)) <= len(context_bundle.citations)
            }
        )
        if not cited_indices:
            warnings.append("answer has no inline citations")

        confidence = calculate_confidence(
            query=query,
            hits=retrieval.hits,
            citations=context_bundle.citations,
            warnings=warnings + list(retrieval.trace.get("warnings", [])),
        )
        result = AnswerResult(
            query=query,
            mode=mode,
            answer=answer_text,
            rewritten_query=retrieval.rewritten_query,
            citations=context_bundle.citations,
            cited_indices=cited_indices,
            warnings=warnings + list(retrieval.trace.get("warnings", [])),
            retrieval_trace=retrieval.trace,
            confidence=confidence,
        )
        return result
