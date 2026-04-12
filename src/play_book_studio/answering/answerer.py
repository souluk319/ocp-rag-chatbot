"""grounded answer 전체를 오케스트레이션한다.

이 모듈이 채팅 제품의 런타임 spine이다:
retrieve -> assemble context -> prompt -> LLM -> answer shaping -> citations
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from play_book_studio.config.settings import Settings
from play_book_studio.retrieval import ChatRetriever, SessionContext
from play_book_studio.retrieval.query import (
    has_follow_up_entity_ambiguity,
    has_follow_up_reference,
)

from .answer_text_commands import (
    build_deployment_scaling_answer,
    build_grounded_command_guide_answer,
)
from .answer_text_formatting import summarize_session_context
from .citations import (
    finalize_citations,
    summarize_selected_citations,
)
from .context import assemble_context
from .llm import LLMClient
from .models import AnswerResult
from .pipeline_helpers import (
    build_answer_result,
    build_follow_up_clarification_answer,
    finalize_deployment_scaling_answer,
    generate_grounded_answer_text,
)
from .prompt import build_messages
from .router import route_non_rag

class ChatAnswerer:
    """CLI, UI, eval 파이프라인이 공통으로 쓰는 최상위 answer 서비스."""

    def __init__(
        self,
        settings: Settings,
        retriever: ChatRetriever,
        llm_client: LLMClient,
    ) -> None:
        self.settings = settings
        self.retriever = retriever
        self.llm_client = llm_client

    @classmethod
    def from_settings(cls, settings: Settings) -> "ChatAnswerer":
        return cls(
            settings=settings,
            retriever=ChatRetriever.from_settings(settings, enable_vector=True),
            llm_client=LLMClient(settings),
        )

    def default_log_path(self) -> Path:
        return self.settings.answer_log_path

    def append_log(self, result: AnswerResult, log_path: Path | None = None) -> Path:
        target = log_path or self.default_log_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
        return target

    def _build_grounding_blocked_result(
        self,
        *,
        query: str,
        mode: str,
        rewritten_query: str,
        answer: str,
        warnings: list[str],
        retrieval_trace: dict,
        pipeline_events: list[dict],
        pipeline_timings_ms: dict[str, float],
        selected_hits: list[dict] | None = None,
        llm_runtime_meta: dict | None = None,
    ) -> AnswerResult:
        return build_answer_result(
            query=query,
            mode=mode,
            answer=answer,
            rewritten_query=rewritten_query,
            response_kind="no_answer",
            citations=[],
            cited_indices=[],
            warnings=warnings,
            retrieval_trace=retrieval_trace,
            pipeline_events=pipeline_events,
            pipeline_timings_ms=pipeline_timings_ms,
            selected_hits=selected_hits,
            llm_runtime_meta=llm_runtime_meta,
        )

    def answer(
        self,
        query: str,
        *,
        mode: str = "chat",
        context: SessionContext | None = None,
        top_k: int = 5,
        candidate_k: int = 20,
        max_context_chunks: int = 6,
        trace_callback=None,
    ) -> AnswerResult:
        # 모든 사용자 답변에 trace/timing을 남겨 두어, 품질 문제 발생 시
        # 어디서 파이프라인이 흔들렸는지 추측이 아니라 기록으로 좁힐 수 있게 한다.
        answer_started_at = time.perf_counter()
        pipeline_timings_ms: dict[str, float] = {}
        pipeline_events: list[dict] = []

        def emit(event: dict) -> None:
            payload = dict(event)
            payload.setdefault("type", "trace")
            payload.setdefault(
                "timestamp_ms",
                round((time.perf_counter() - answer_started_at) * 1000, 1),
            )
            pipeline_events.append(payload)
            if trace_callback is not None:
                trace_callback(payload)

        route_started_at = time.perf_counter()
        emit(
            {
                "step": "route_query",
                "label": "질문 라우팅 중",
                "status": "running",
                "detail": query[:180],
            }
        )
        is_follow_up = has_follow_up_reference(query)
        routed_response = None
        if not is_follow_up:
            routed_response = route_non_rag(
                query,
                corpus_label=self.settings.active_pack.product_label,
                corpus_version=self.settings.active_pack.version,
            )
        pipeline_timings_ms["route_query"] = round(
            (time.perf_counter() - route_started_at) * 1000,
            1,
        )
        if routed_response is not None:
            emit(
                {
                    "step": "route_query",
                    "label": "질문 라우팅 완료",
                    "status": "done",
                    "detail": f"non-rag route={routed_response.route}",
                    "duration_ms": pipeline_timings_ms["route_query"],
                }
            )
            pipeline_timings_ms["total"] = round(
                (time.perf_counter() - answer_started_at) * 1000,
                1,
            )
            emit(
                {
                    "step": "pipeline_complete",
                    "label": "답변 생성 완료",
                    "status": "done",
                    "detail": f"총 {pipeline_timings_ms['total']}ms",
                    "duration_ms": pipeline_timings_ms["total"],
                }
            )
            return build_answer_result(
                query=query,
                mode=mode,
                answer=routed_response.answer.strip(),
                rewritten_query=query,
                response_kind=routed_response.route,
                citations=[],
                cited_indices=[],
                warnings=[],
                retrieval_trace={"route": routed_response.route, "warnings": []},
                pipeline_events=pipeline_events,
                pipeline_timings_ms=pipeline_timings_ms,
            )

        if is_follow_up and has_follow_up_entity_ambiguity(query, context):
            answer_text = build_follow_up_clarification_answer(context)
            pipeline_timings_ms["total"] = round(
                (time.perf_counter() - answer_started_at) * 1000,
                1,
            )
            emit(
                {
                    "step": "route_query",
                    "label": "질문 라우팅 완료",
                    "status": "done",
                    "detail": "follow-up clarification",
                    "duration_ms": pipeline_timings_ms["route_query"],
                }
            )
            emit(
                {
                    "step": "pipeline_complete",
                    "label": "답변 생성 완료",
                    "status": "done",
                    "detail": f"총 {pipeline_timings_ms['total']}ms",
                    "duration_ms": pipeline_timings_ms["total"],
                }
            )
            return build_answer_result(
                query=query,
                mode=mode,
                answer=answer_text,
                rewritten_query=query,
                response_kind="clarification",
                citations=[],
                cited_indices=[],
                warnings=[],
                retrieval_trace={"route": "follow_up_clarification", "warnings": []},
                pipeline_events=pipeline_events,
                pipeline_timings_ms=pipeline_timings_ms,
            )

        emit(
            {
                "step": "route_query",
                "label": "질문 라우팅 완료",
                "status": "done",
                "detail": "rag",
                "duration_ms": pipeline_timings_ms["route_query"],
            }
        )
        emit(
            {
                "step": "retrieval",
                "label": "근거 검색 시작",
                "status": "running",
                "detail": query[:180],
            }
        )
        retrieval_started_at = time.perf_counter()
        retrieval = self.retriever.retrieve(
            query,
            context=context,
            top_k=top_k,
            candidate_k=candidate_k,
            trace_callback=emit,
        )
        pipeline_timings_ms["retrieval_total"] = round(
            (time.perf_counter() - retrieval_started_at) * 1000,
            1,
        )
        emit(
            {
                "step": "retrieval",
                "label": "근거 검색 완료",
                "status": "done",
                "detail": f"상위 근거 {len(retrieval.hits)}개",
                "duration_ms": pipeline_timings_ms["retrieval_total"],
            }
        )

        context_started_at = time.perf_counter()
        emit(
            {
                "step": "context_assembly",
                "label": "citation 컨텍스트 조립 중",
                "status": "running",
            }
        )
        context_bundle = assemble_context(
            retrieval.hits,
            query=query,
            max_chunks=max_context_chunks,
        )
        pipeline_timings_ms["context_assembly"] = round(
            (time.perf_counter() - context_started_at) * 1000,
            1,
        )
        emit(
            {
                "step": "context_assembly",
                "label": "citation 컨텍스트 조립 완료",
                "status": "done",
                "detail": f"citation {len(context_bundle.citations)}개",
                "duration_ms": pipeline_timings_ms["context_assembly"],
                "meta": {
                    "selected": len(context_bundle.citations),
                    "selected_hits": summarize_selected_citations(
                        context_bundle.citations,
                        retrieval.hits,
                    ),
                },
            }
        )
        warnings: list[str] = []
        if not context_bundle.citations:
            warnings.append("no context citations assembled")
            emit(
                {
                    "step": "grounding_guard",
                    "label": "근거 검증 차단",
                    "status": "error",
                    "detail": "선택된 citation이 없습니다",
                }
            )
            pipeline_timings_ms["total"] = round(
                (time.perf_counter() - answer_started_at) * 1000,
                1,
            )
            emit(
                {
                    "step": "pipeline_complete",
                    "label": "답변 생성 중단",
                    "status": "done",
                    "detail": f"총 {pipeline_timings_ms['total']}ms",
                    "duration_ms": pipeline_timings_ms["total"],
                }
            )
            return self._build_grounding_blocked_result(
                query=query,
                mode=mode,
                rewritten_query=retrieval.rewritten_query,
                answer=(
                    "답변: 현재 선택된 근거가 없어 답변을 생성하지 않습니다. "
                    "질문 범위를 더 구체화하거나 코퍼스 상태를 점검해야 합니다."
                ),
                warnings=warnings,
                retrieval_trace=retrieval.trace,
                pipeline_events=pipeline_events,
                pipeline_timings_ms=pipeline_timings_ms,
            )
        selected_hits = summarize_selected_citations(
            context_bundle.citations,
            retrieval.hits,
        )

        deployment_scaling_answer = build_deployment_scaling_answer(
            query=query,
            context=context,
            citations=context_bundle.citations,
        )
        if deployment_scaling_answer is not None:
            answer_text = deployment_scaling_answer
            answer_text, final_citations, cited_indices = finalize_deployment_scaling_answer(
                answer_text,
                context_bundle.citations,
            )
            pipeline_timings_ms["total"] = round(
                (time.perf_counter() - answer_started_at) * 1000,
                1,
            )
            emit(
                {
                    "step": "deterministic_answer",
                    "label": "전용 명령 답변 생성 완료",
                    "status": "done",
                    "detail": "deployment scaling",
                }
            )
            emit(
                {
                    "step": "pipeline_complete",
                    "label": "답변 생성 완료",
                    "status": "done",
                    "detail": f"총 {pipeline_timings_ms['total']}ms",
                    "duration_ms": pipeline_timings_ms["total"],
                }
            )
            return build_answer_result(
                query=query,
                mode=mode,
                answer=answer_text,
                rewritten_query=retrieval.rewritten_query,
                response_kind="clarification" if "숫자가 현재 질문에 없습니다" in answer_text else "rag",
                citations=final_citations,
                cited_indices=cited_indices,
                warnings=warnings,
                retrieval_trace=retrieval.trace,
                pipeline_events=pipeline_events,
                pipeline_timings_ms=pipeline_timings_ms,
                selected_hits=selected_hits,
            )

        grounded_command_answer = build_grounded_command_guide_answer(
            query=query,
            citations=context_bundle.citations,
        )
        if grounded_command_answer is not None:
            answer_text, final_citations, cited_indices = finalize_deployment_scaling_answer(
                grounded_command_answer,
                context_bundle.citations,
            )
            pipeline_timings_ms["total"] = round(
                (time.perf_counter() - answer_started_at) * 1000,
                1,
            )
            emit(
                {
                    "step": "deterministic_answer",
                    "label": "명령 우선 답변 생성 완료",
                    "status": "done",
                    "detail": "grounded command guide",
                }
            )
            emit(
                {
                    "step": "pipeline_complete",
                    "label": "답변 생성 완료",
                    "status": "done",
                    "detail": f"총 {pipeline_timings_ms['total']}ms",
                    "duration_ms": pipeline_timings_ms["total"],
                }
            )
            return build_answer_result(
                query=query,
                mode=mode,
                answer=answer_text,
                rewritten_query=retrieval.rewritten_query,
                response_kind="rag",
                citations=final_citations,
                cited_indices=cited_indices,
                warnings=warnings,
                retrieval_trace=retrieval.trace,
                pipeline_events=pipeline_events,
                pipeline_timings_ms=pipeline_timings_ms,
                selected_hits=selected_hits,
            )

        prompt_started_at = time.perf_counter()
        emit(
            {
                "step": "prompt_build",
                "label": "프롬프트 조립 중",
                "status": "running",
            }
        )
        messages = build_messages(
            query=query,
            mode=mode,
            context_bundle=context_bundle,
            session_summary=summarize_session_context(context),
        )
        pipeline_timings_ms["prompt_build"] = round(
            (time.perf_counter() - prompt_started_at) * 1000,
            1,
        )
        emit(
            {
                "step": "prompt_build",
                "label": "프롬프트 조립 완료",
                "status": "done",
                "detail": f"messages {len(messages)}개",
                "duration_ms": pipeline_timings_ms["prompt_build"],
            }
        )

        llm_started_at = time.perf_counter()
        answer_text, llm_runtime_meta = generate_grounded_answer_text(
            self.llm_client,
            messages,
            query=query,
            mode=mode,
            citations=context_bundle.citations,
            trace_callback=emit,
        )
        pipeline_timings_ms["llm_generate_total"] = round(
            (time.perf_counter() - llm_started_at) * 1000,
            1,
        )
        emit(
            {
                "step": "llm_runtime",
                "label": "LLM 런타임 확인",
                "status": "done",
                "detail": (
                    f"provider={llm_runtime_meta.get('last_provider') or llm_runtime_meta.get('preferred_provider')} "
                    f"fallback={str(bool(llm_runtime_meta.get('last_fallback_used', False))).lower()}"
                ),
                "meta": llm_runtime_meta,
            }
        )

        finalize_started_at = time.perf_counter()
        emit(
            {
                "step": "citation_finalize",
                "label": "citation 정리 중",
                "status": "running",
            }
        )
        answer_text, final_citations, cited_indices = finalize_citations(
            answer_text,
            context_bundle.citations,
        )
        if not cited_indices:
            warnings.append("answer has no inline citations")
        pipeline_timings_ms["citation_finalize"] = round(
            (time.perf_counter() - finalize_started_at) * 1000,
            1,
        )
        emit(
            {
                "step": "citation_finalize",
                "label": "citation 정리 완료",
                "status": "done",
                "detail": f"최종 citation {len(final_citations)}개",
                "duration_ms": pipeline_timings_ms["citation_finalize"],
            }
        )
        if not cited_indices:
            emit(
                {
                    "step": "grounding_guard",
                    "label": "근거 검증 차단",
                    "status": "error",
                    "detail": "생성 답변에 inline citation이 없습니다",
                }
            )
            pipeline_timings_ms["total"] = round(
                (time.perf_counter() - answer_started_at) * 1000,
                1,
            )
            emit(
                {
                    "step": "pipeline_complete",
                    "label": "답변 생성 중단",
                    "status": "done",
                    "detail": f"총 {pipeline_timings_ms['total']}ms",
                    "duration_ms": pipeline_timings_ms["total"],
                }
            )
            return self._build_grounding_blocked_result(
                query=query,
                mode=mode,
                rewritten_query=retrieval.rewritten_query,
                answer=(
                    "답변: 생성된 답변에 근거 번호가 없어 결과를 폐기했습니다. "
                    "질문을 더 구체화하거나 코퍼스와 검색 상태를 점검해야 합니다."
                ),
                warnings=warnings,
                retrieval_trace=retrieval.trace,
                pipeline_events=pipeline_events,
                pipeline_timings_ms=pipeline_timings_ms,
                selected_hits=selected_hits,
                llm_runtime_meta=llm_runtime_meta,
            )

        pipeline_timings_ms["total"] = round(
            (time.perf_counter() - answer_started_at) * 1000,
            1,
        )
        emit(
            {
                "step": "pipeline_complete",
                "label": "답변 생성 완료",
                "status": "done",
                "detail": f"총 {pipeline_timings_ms['total']}ms",
                "duration_ms": pipeline_timings_ms["total"],
            }
        )

        result = build_answer_result(
            query=query,
            mode=mode,
            answer=answer_text,
            rewritten_query=retrieval.rewritten_query,
            response_kind="rag",
            citations=final_citations,
            cited_indices=cited_indices,
            warnings=warnings,
            retrieval_trace=retrieval.trace,
            pipeline_events=pipeline_events,
            pipeline_timings_ms=pipeline_timings_ms,
            selected_hits=selected_hits,
            llm_runtime_meta=llm_runtime_meta,
        )
        return result
