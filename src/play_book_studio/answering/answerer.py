"""grounded answer 전체를 오케스트레이션한다.

이 모듈이 채팅 제품의 런타임 spine이다:
retrieve -> assemble context -> prompt -> LLM -> answer shaping -> citations
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from play_book_studio.config.settings import Settings
from play_book_studio.retrieval import Part2Retriever, SessionContext
from play_book_studio.retrieval.query import (
    has_follow_up_entity_ambiguity,
    has_follow_up_reference,
)

from .answer_text import (
    align_answer_to_grounded_commands,
    build_deployment_scaling_answer,
    citation_marker,
    ensure_korean_product_terms,
    has_grounded_deployment_scale_citation,
    normalize_answer_markup_blocks,
    normalize_answer_text,
    reshape_ops_answer_text,
    shape_certificate_monitor_answer,
    shape_etcd_backup_answer,
    shape_pod_lifecycle_explainer,
    shape_pod_pending_troubleshooting,
    strip_intro_offtopic_noise,
    strip_structured_key_extra_guidance,
    strip_weak_additional_guidance,
    summarize_session_context,
    trim_productization_noise,
)
from .citations import (
    CITATION_RE,
    finalize_citations,
    inject_single_citation,
    maybe_autorepair_inline_citations,
    select_fallback_citations,
    summarize_selected_citations,
)
from .context import assemble_context
from .llm import LLMClient
from .models import AnswerResult
from .prompt import build_messages
from .router import route_non_rag


_normalize_answer_markup_blocks = normalize_answer_markup_blocks
_ensure_korean_product_terms = ensure_korean_product_terms
_align_answer_to_grounded_commands = align_answer_to_grounded_commands
_shape_etcd_backup_answer = shape_etcd_backup_answer
_shape_certificate_monitor_answer = shape_certificate_monitor_answer
_strip_weak_additional_guidance = strip_weak_additional_guidance
_strip_intro_offtopic_noise = strip_intro_offtopic_noise
_strip_structured_key_extra_guidance = strip_structured_key_extra_guidance
_trim_productization_noise = trim_productization_noise
_citation_marker = citation_marker
_shape_pod_lifecycle_explainer = shape_pod_lifecycle_explainer
_shape_pod_pending_troubleshooting = shape_pod_pending_troubleshooting
_has_grounded_deployment_scale_citation = has_grounded_deployment_scale_citation
_build_deployment_scaling_answer = build_deployment_scaling_answer
_inject_single_citation = inject_single_citation
_summarize_selected_citations = summarize_selected_citations
_CITATION_RE = CITATION_RE


class Part3Answerer:
    """CLI, UI, eval 파이프라인이 공통으로 쓰는 최상위 answer 서비스."""

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
        return self.settings.answer_log_path

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
            return AnswerResult(
                query=query,
                mode=mode,
                answer=routed_response.answer.strip(),
                rewritten_query=query,
                response_kind=routed_response.route,
                citations=[],
                cited_indices=[],
                warnings=[],
                retrieval_trace={"route": routed_response.route, "warnings": []},
                pipeline_trace={"events": pipeline_events, "timings_ms": pipeline_timings_ms},
            )

        if is_follow_up and has_follow_up_entity_ambiguity(query, context):
            leading_entities = [entity for entity in context.open_entities if str(entity).strip()][:2]
            if len(leading_entities) == 2:
                scope_hint = f"{leading_entities[0]} 쪽인지, {leading_entities[1]} 쪽인지"
            else:
                scope_hint = "어느 항목을 가리키는지"
            answer_text = (
                "답변: 지금은 열린 주제가 둘 이상이라 어느 설정을 말씀하시는지 먼저 정해야 합니다. "
                f"{scope_hint} 먼저 확인해 주시겠어요?"
            )
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
            return AnswerResult(
                query=query,
                mode=mode,
                answer=answer_text,
                rewritten_query=query,
                response_kind="clarification",
                citations=[],
                cited_indices=[],
                warnings=[],
                retrieval_trace={"route": "follow_up_clarification", "warnings": []},
                pipeline_trace={"events": pipeline_events, "timings_ms": pipeline_timings_ms},
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
                    "selected_hits": _summarize_selected_citations(
                        context_bundle.citations,
                        retrieval.hits,
                    ),
                },
            }
        )
        warnings: list[str] = []
        if not context_bundle.citations:
            warnings.append("no context citations assembled")

        deployment_scaling_answer = _build_deployment_scaling_answer(
            query=query,
            context=context,
            citations=context_bundle.citations,
        )
        if deployment_scaling_answer is not None:
            answer_text = deployment_scaling_answer
            final_citations = select_fallback_citations(context_bundle.citations, limit=1)
            answer_text, final_citations, cited_indices = finalize_citations(
                answer_text,
                final_citations,
            )
            if not cited_indices and final_citations:
                answer_text = _inject_single_citation(answer_text, citation_index=1)
                answer_text, final_citations, cited_indices = finalize_citations(
                    answer_text,
                    final_citations,
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
            return AnswerResult(
                query=query,
                mode=mode,
                answer=answer_text,
                rewritten_query=retrieval.rewritten_query,
                response_kind="clarification" if "숫자가 현재 질문에 없습니다" in answer_text else "rag",
                citations=final_citations,
                cited_indices=cited_indices,
                warnings=warnings + list(retrieval.trace.get("warnings", [])),
                retrieval_trace=retrieval.trace,
                pipeline_trace={
                    "events": pipeline_events,
                    "timings_ms": {
                        **retrieval.trace.get("timings_ms", {}),
                        **pipeline_timings_ms,
                    },
                    "selection": {
                        "selected_hits": _summarize_selected_citations(
                            context_bundle.citations,
                            retrieval.hits,
                        )
                    },
                },
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
        answer_text = reshape_ops_answer_text(
            normalize_answer_text(
                _normalize_answer_markup_blocks(
                    self.llm_client.generate(messages, trace_callback=emit)
                )
            ),
            mode=mode,
        )
        answer_text = _ensure_korean_product_terms(answer_text, query=query)
        answer_text = _align_answer_to_grounded_commands(
            answer_text,
            query=query,
            citations=context_bundle.citations,
        )
        answer_text = _shape_etcd_backup_answer(
            answer_text,
            query=query,
            citations=context_bundle.citations,
        )
        answer_text = _shape_certificate_monitor_answer(
            answer_text,
            query=query,
            citations=context_bundle.citations,
        )
        answer_text = _shape_pod_lifecycle_explainer(
            answer_text,
            query=query,
            mode=mode,
            citations=context_bundle.citations,
        )
        answer_text = _shape_pod_pending_troubleshooting(
            answer_text,
            query=query,
            mode=mode,
            citations=context_bundle.citations,
        )
        answer_text = _strip_weak_additional_guidance(
            answer_text,
            mode=mode,
            citations=context_bundle.citations,
        )
        answer_text = _strip_structured_key_extra_guidance(
            answer_text,
            query=query,
            mode=mode,
        )
        answer_text = _trim_productization_noise(answer_text)
        answer_text = _strip_intro_offtopic_noise(answer_text, query=query)
        if context_bundle.citations and not _CITATION_RE.search(answer_text):
            answer_text = _inject_single_citation(answer_text, citation_index=1)
        pipeline_timings_ms["llm_generate_total"] = round(
            (time.perf_counter() - llm_started_at) * 1000,
            1,
        )
        llm_runtime_meta = (
            self.llm_client.runtime_metadata()
            if hasattr(self.llm_client, "runtime_metadata")
            else {
                "preferred_provider": "unknown",
                "fallback_enabled": False,
                "last_provider": None,
                "last_fallback_used": False,
                "last_attempted_providers": [],
            }
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
        auto_repaired_citations = False
        if not cited_indices:
            answer_text, auto_repaired_citations = maybe_autorepair_inline_citations(
                answer_text,
                context_bundle.citations,
            )
            if auto_repaired_citations:
                answer_text, final_citations, cited_indices = finalize_citations(
                    answer_text,
                    context_bundle.citations,
                )
            elif context_bundle.citations:
                final_citations = select_fallback_citations(context_bundle.citations)
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
            warnings.append("answer has no inline citations")

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

        result = AnswerResult(
            query=query,
            mode=mode,
            answer=answer_text,
            rewritten_query=retrieval.rewritten_query,
            response_kind="rag",
            citations=final_citations,
            cited_indices=cited_indices,
            warnings=warnings + list(retrieval.trace.get("warnings", [])),
            retrieval_trace=retrieval.trace,
            pipeline_trace={
                "events": pipeline_events,
                "timings_ms": {
                    **retrieval.trace.get("timings_ms", {}),
                    **pipeline_timings_ms,
                },
                "selection": {
                    "selected_hits": _summarize_selected_citations(
                        context_bundle.citations,
                        retrieval.hits,
                    )
                },
                "llm": llm_runtime_meta,
            },
        )
        return result
