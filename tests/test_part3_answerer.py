from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.settings import Settings
from ocp_rag_part2.models import (
    CitationGroupMemory,
    CitationMemory,
    ProcedureMemory,
    RetrievalHit,
    RetrievalResult,
    SessionContext,
    TurnMemory,
)
from ocp_rag_part3.answerer import (
    _build_procedure_follow_up_answer,
    _augment_query_with_procedure_focus,
    _ensure_korean_product_terms,
    _strip_intro_offtopic_noise,
    Part3Answerer,
    finalize_citations,
    normalize_answer_text,
    reshape_ops_answer_text,
    _strip_weak_additional_guidance,
    summarize_session_context,
)
from ocp_rag_part3.models import Citation
from ocp_rag_part3.llm import LLMClient
from ocp_rag_part3.prompt import build_messages


class _FakeRetriever:
    def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
        if trace_callback is not None:
            trace_callback(
                {
                    "step": "bm25_search",
                    "label": "키워드 검색 완료",
                    "status": "done",
                    "duration_ms": 1.1,
                }
            )
        hit = RetrievalHit(
            chunk_id="chunk-1",
            book_slug="architecture",
            chapter="architecture",
            section="OpenShift 아키텍처 개요",
            anchor="overview",
            source_url="https://example.com/architecture",
            viewer_path="/docs/architecture.html#overview",
            text="OpenShift 아키텍처는 컨트롤 플레인과 작업자 노드로 구성됩니다.",
            source="hybrid",
            raw_score=1.0,
            fused_score=1.0,
        )
        return RetrievalResult(
            query=query,
            normalized_query=query,
            rewritten_query=query,
            top_k=top_k,
            candidate_k=candidate_k,
            context=(context or SessionContext()).to_dict(),
            hits=[hit],
            trace={"warnings": [], "timings_ms": {"bm25_search": 1.1}},
        )


class _DuplicateCitationRetriever:
    def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
        hits = [
            RetrievalHit(
                chunk_id="chunk-1",
                book_slug="support",
                chapter="support",
                section="7.2.1. 노드 상태, 리소스 사용량 및 구성 확인",
                anchor="checking-node-resource-usage",
                source_url="https://example.com/support",
                viewer_path="/docs/ocp/4.20/ko/support/index.html#checking-node-resource-usage",
                text="클러스터 내 각 노드에 대한 CPU 및 메모리 사용량을 요약합니다. oc adm top nodes",
                source="hybrid",
                raw_score=1.0,
                fused_score=1.0,
            ),
            RetrievalHit(
                chunk_id="chunk-2",
                book_slug="support",
                chapter="support",
                section="7.2.1. 노드 상태, 리소스 사용량 및 구성 확인",
                anchor="checking-node-resource-usage",
                source_url="https://example.com/support",
                viewer_path="/docs/ocp/4.20/ko/support/index.html#checking-node-resource-usage",
                text="특정 노드의 CPU 및 메모리 사용량은 oc adm top node my-node 로 확인합니다.",
                source="hybrid",
                raw_score=0.99,
                fused_score=0.99,
            ),
        ]
        return RetrievalResult(
            query=query,
            normalized_query=query,
            rewritten_query=query,
            top_k=top_k,
            candidate_k=candidate_k,
            context=(context or SessionContext()).to_dict(),
            hits=hits,
            trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
        )


class _DuplicateCitationLLMClient:
    def generate(self, messages, trace_callback=None):  # noqa: ANN001
        self.messages = messages
        if trace_callback is not None:
            trace_callback(
                {
                    "step": "llm_generate",
                    "label": "LLM 응답 생성 완료",
                    "status": "done",
                    "duration_ms": 2.2,
                }
            )
        return "답변: `oc adm top nodes` 명령으로 한눈에 확인하세요 [1][2]."


class _FakeLLMClient:
    def generate(self, messages, trace_callback=None):  # noqa: ANN001
        self.messages = messages
        if trace_callback is not None:
            trace_callback(
                {
                    "step": "llm_generate",
                    "label": "LLM 응답 생성 완료",
                    "status": "done",
                    "duration_ms": 2.4,
                }
        )
        return "### 답변\nOpenShift는 컨트롤 플레인과 작업자 노드로 구성됩니다. [1]"


class _NoCitationLLMClient:
    def generate(self, messages, trace_callback=None):  # noqa: ANN001
        self.messages = messages
        if trace_callback is not None:
            trace_callback(
                {
                    "step": "llm_generate",
                    "label": "LLM 응답 생성 완료",
                    "status": "done",
                    "duration_ms": 2.1,
                }
            )
        return (
            "답변: 특정 네임스페이스에만 admin 권한을 주려면 다음 명령을 사용하세요.\n\n"
            "```bash\n"
            "oc adm policy add-role-to-user admin alice -n joe\n"
            "```"
        )


class _BareCommandLLMClient:
    def generate(self, messages, trace_callback=None):  # noqa: ANN001
        self.messages = messages
        if trace_callback is not None:
            trace_callback(
                {
                    "step": "llm_generate",
                    "label": "LLM 응답 생성 완료",
                    "status": "done",
                    "duration_ms": 1.4,
                }
        )
        return "답변: $ oc adm policy add-role-to-user admin <사용자명> -n <namespace> [1]"


class _WrongDrainCommandLLMClient:
    def generate(self, messages, trace_callback=None):  # noqa: ANN001
        self.messages = messages
        if trace_callback is not None:
            trace_callback(
                {
                    "step": "llm_generate",
                    "label": "LLM 응답 생성 완료",
                    "status": "done",
                    "duration_ms": 1.8,
                }
            )
        return (
            "답변: 아래 명령으로 노드를 비울 수 있습니다.\n\n"
            "```bash\nkubectl drain <노드명> --ignore-daemonsets --delete-emptydir-data\n```"
        )


class _ClarifyingLLMClient:
    def generate(self, messages, trace_callback=None):  # noqa: ANN001
        self.messages = messages
        if trace_callback is not None:
            trace_callback(
                {
                    "step": "llm_generate",
                    "label": "LLM 응답 생성 완료",
                    "status": "done",
                    "duration_ms": 1.7,
                }
            )
        return (
            "답변: 질문의 실행 대상이 불명확합니다. "
            "어떤 사용자 또는 namespace를 말씀하시는 건가요?"
        )


class _ReplayLLMClient:
    def generate(self, messages, trace_callback=None):  # noqa: ANN001
        self.messages = messages
        if trace_callback is not None:
            trace_callback(
                {
                    "step": "llm_generate",
                    "label": "LLM 응답 생성 완료",
                    "status": "done",
                    "duration_ms": 1.4,
                }
            )
        return "답변: 같은 문서를 기준으로 다시 정리하면 OpenShift 아키텍처 개요입니다 [1]."


class _ExplodingRetriever:
    def retrieve(self, *args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("retriever should not be called for non-rag routes")


class _FakeResponse:
    def __init__(self, payload, status_code=200, text=None):
        self.payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload, ensure_ascii=False) if text is None else text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")

    def json(self):
        return self.payload


class Part3AnswererTests(unittest.TestCase):
    def test_build_messages_includes_grounding_context(self) -> None:
        from ocp_rag_part3.context import assemble_context

        hit = RetrievalHit(
            chunk_id="chunk-1",
            book_slug="architecture",
            chapter="architecture",
            section="개요",
            anchor="overview",
            source_url="https://example.com/architecture",
            viewer_path="/docs/architecture.html#overview",
            text="OpenShift 아키텍처 개요",
            source="hybrid",
            raw_score=1.0,
            fused_score=1.0,
        )
        bundle = assemble_context([hit])
        messages = build_messages(
            query="아키텍처 설명",
            mode="learn",
            context_bundle=bundle,
            session_summary="- 현재 주제: OpenShift 아키텍처",
        )

        self.assertEqual("system", messages[0]["role"])
        self.assertIn("[1] book=architecture", messages[1]["content"])
        self.assertIn("질문: 아키텍처 설명", messages[1]["content"])
        self.assertIn("세션 맥락:", messages[1]["content"])

    def test_build_messages_hardens_follow_up_constraints(self) -> None:
        from ocp_rag_part3.context import assemble_context

        hit = RetrievalHit(
            chunk_id="chunk-1",
            book_slug="etcd",
            chapter="etcd",
            section="복원",
            anchor="restore",
            source_url="https://example.com/etcd",
            viewer_path="/docs/etcd.html#restore",
            text="etcd 복원 절차",
            source="hybrid",
            raw_score=1.0,
            fused_score=1.0,
        )
        bundle = assemble_context([hit])
        messages = build_messages(
            query="그거 어떻게 해?",
            mode="ops",
            context_bundle=bundle,
            session_summary="- 현재 주제: etcd 복원",
        )

        self.assertIn("이전 대화 맥락은 해석 힌트일 뿐", messages[0]["content"])
        self.assertIn("follow-up이라도 현재 검색 근거가 약하면 단정하지 말고 확인 질문을 할 것", messages[1]["content"])
        self.assertIn("이전 맥락 때문에 현재 근거와 맞지 않는 대상을 끌어오지 말 것", messages[1]["content"])

    def test_build_messages_adds_procedure_follow_up_rule_for_step_reference(self) -> None:
        from ocp_rag_part3.context import assemble_context

        hit = RetrievalHit(
            chunk_id="chunk-1",
            book_slug="authentication_and_authorization",
            chapter="rbac",
            section="RoleBinding",
            anchor="adding-roles",
            source_url="https://example.com/rbac",
            viewer_path="/docs/rbac.html#adding-roles",
            text="RoleBinding procedure",
            source="hybrid",
            raw_score=1.0,
            fused_score=1.0,
        )
        bundle = assemble_context([hit])
        messages = build_messages(
            query="2번만 더 자세히",
            mode="ops",
            context_bundle=bundle,
            session_summary=(
                "- active procedure: namespace admin role\n"
                "- procedure step command map: "
                "1. Create binding => oc adm policy add-role-to-user admin alice -n joe | "
                "2. Verify binding => oc describe rolebinding -n joe"
            ),
        )

        self.assertIn("Procedure follow-up rule:", messages[1]["content"])
        self.assertIn("preserve the mapped command for that step", messages[1]["content"])

    def test_build_messages_forces_brief_clarification_in_ambiguous_cases(self) -> None:
        messages = build_messages(
            query="로그는 어디서 봐?",
            mode="ops",
            context_bundle=type("Bundle", (), {"prompt_context": "", "citations": []})(),
            session_summary="",
        )

        self.assertIn("지금은 <불명확한 점>이 불명확합니다. <짧은 확인 질문>?", messages[0]["content"])
        self.assertIn("질문이 애매한 경우 '근거가 없습니다'로만 끝내지 말 것", messages[1]["content"])

    def test_build_messages_enforces_ops_command_answer_shape(self) -> None:
        messages = build_messages(
            query="특정 namespace에만 admin 권한 주려면 어떤 명령 써?",
            mode="ops",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("bare command만 던지지 말고", messages[0]["content"])
        self.assertIn("한 줄 설명 -> 코드 블록 -> 짧은 범위/예시", messages[1]["content"])

    def test_build_messages_adds_step_by_step_rule_for_ops_queries(self) -> None:
        messages = build_messages(
            query="특정 namespace만 admin 권한 주는 방법 단계별로 알려줘",
            mode="ops",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("번호 목록 `1. 2. 3.`", messages[0]["content"])
        self.assertIn("단계별 출력 규칙:", messages[1]["content"])

    def test_build_messages_adds_compare_shape_hint(self) -> None:
        messages = build_messages(
            query="오픈시프트와 쿠버네티스 차이를 세 줄로 설명해줘",
            mode="learn",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("공통 기반 1문장 -> 핵심 차이 2~3개", messages[1]["content"])

    def test_build_messages_adds_intro_shape_hint(self) -> None:
        messages = build_messages(
            query="오픈시프트가 뭐야?",
            mode="learn",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("정의 1문장 -> 핵심 역할/구성 2~3개", messages[1]["content"])

    def test_build_messages_adds_project_finalizer_shape_hint(self) -> None:
        messages = build_messages(
            query="프로젝트가 Terminating 상태에서 finalizers 정리는 어떻게 해?",
            mode="ops",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("상태/남은 리소스 확인 명령", messages[1]["content"])

    def test_build_messages_adds_operator_concept_shape_hint(self) -> None:
        messages = build_messages(
            query="Operator가 왜 필요한지 예시까지 설명해줘",
            mode="learn",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("정의 1문장", messages[1]["content"])
        self.assertIn("예시를 짧게", messages[1]["content"])

    def test_answerer_returns_citations_and_used_indices(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_FakeRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("OpenShift 아키텍처를 설명해줘", mode="learn")

        self.assertEqual([1], result.cited_indices)
        self.assertEqual("architecture", result.citations[0].book_slug)
        self.assertFalse(result.warnings)
        self.assertTrue(result.answer.startswith("답변:"))
        self.assertIn("events", result.pipeline_trace)
        self.assertIn("timings_ms", result.pipeline_trace)
        self.assertTrue(
            any(event.get("step") == "context_assembly" for event in result.pipeline_trace["events"])
        )
        self.assertIn("total", result.pipeline_trace["timings_ms"])

    def test_answerer_routes_greeting_without_retrieval(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_ExplodingRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("하이", mode="ops")

        self.assertEqual("smalltalk", result.response_kind)
        self.assertEqual([], result.citations)
        self.assertEqual([], result.cited_indices)
        self.assertFalse(result.warnings)
        self.assertIn("안녕하세요", result.answer)
        self.assertIn("OCP 운영 절차", result.answer)
        self.assertTrue(
            any(event.get("step") == "route_query" for event in result.pipeline_trace["events"])
        )
        self.assertEqual("smalltalk", result.retrieval_trace["route"])

    def test_answerer_routes_meta_question_without_retrieval(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_ExplodingRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("넌 누구야?", mode="ops")

        self.assertEqual("meta", result.response_kind)
        self.assertIn("RAG 챗봇", result.answer)
        self.assertEqual([], result.citations)
        self.assertFalse(result.warnings)

    def test_answerer_routes_ambiguous_log_question_to_clarification(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_ExplodingRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("로그는 어디서 봐?", mode="ops")

        self.assertEqual("clarification", result.response_kind)
        self.assertIn("어떤 로그", result.answer)
        self.assertEqual([], result.citations)

    def test_answerer_uses_first_turn_rbac_fast_lane_for_complete_runbook_question(self) -> None:
        class _RbacRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hit = RetrievalHit(
                    chunk_id="chunk-rbac",
                    book_slug="authentication_and_authorization",
                    chapter="rbac",
                    section="9.6. 사용자 역할 추가",
                    anchor="adding-roles",
                    source_url="https://example.com/rbac",
                    viewer_path="/docs/rbac.html#adding-roles",
                    text=(
                        "사용자 역할 추가 절차입니다. "
                        "oc adm policy add-role-to-user admin alice -n joe "
                        "그리고 oc describe rolebinding -n joe 로 확인합니다."
                    ),
                    source="hybrid",
                    raw_score=1.0,
                    fused_score=1.0,
                )
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=[hit],
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_RbacRetriever(),
            llm_client=_ClarifyingLLMClient(),
        )

        result = answerer.answer(
            "alice 사용자에게 joe namespace admin 역할을 부여하고 확인하는 절차를 단계별로 알려줘",
            mode="ops",
        )

        self.assertEqual("rag", result.response_kind)
        self.assertIn("1. 사용자 `alice`에게 `joe` namespace의 `admin` 역할을 부여합니다.", result.answer)
        self.assertIn("oc adm policy add-role-to-user admin alice -n joe", result.answer)
        self.assertIn("oc describe rolebinding -n joe", result.answer)
        self.assertNotIn("불명확합니다", result.answer)
        self.assertTrue(
            any(event.get("step") == "rbac_fast_lane" for event in result.pipeline_trace["events"])
        )

    def test_answerer_replays_citation_group_for_explicit_same_document_recap(self) -> None:
        context = SessionContext(
            mode="learn",
            current_topic="OpenShift",
            active_citation_group=CitationGroupMemory(
                query="아키텍처 설명",
                topic="OpenShift",
                citations=[
                    CitationMemory(
                        chunk_id="chunk-1",
                        book_slug="architecture",
                        section="개요",
                        anchor="overview",
                        source_url="https://example.com/architecture",
                        viewer_path="/docs/architecture.html#overview",
                        excerpt="OpenShift 아키텍처 개요",
                    )
                ],
            ),
        )
        answerer = Part3Answerer(
            settings=Settings(root_dir=ROOT),
            retriever=_ExplodingRetriever(),
            llm_client=_ReplayLLMClient(),
        )

        result = answerer.answer(
            "그 문서 기준으로 다시 정리해줘",
            mode="learn",
            context=context,
        )

        self.assertEqual("rag", result.response_kind)
        self.assertEqual("replayed", result.citations[0].origin)
        self.assertTrue(
            any(event.get("step") == "citation_replay" for event in result.pipeline_trace["events"])
        )
        self.assertEqual("hit", result.retrieval_trace["citation_replay"]["status"])

    def test_answerer_reruns_retrieval_for_risky_citation_follow_up(self) -> None:
        class _TrackingRetriever:
            def __init__(self) -> None:
                self.called = False
                self.last_query = ""

            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                self.called = True
                self.last_query = query
                return _FakeRetriever().retrieve(
                    query,
                    context,
                    top_k,
                    candidate_k,
                    trace_callback=trace_callback,
                )

        retriever = _TrackingRetriever()
        context = SessionContext(
            mode="learn",
            current_topic="OpenShift",
            active_citation_group=CitationGroupMemory(
                query="아키텍처 설명",
                topic="OpenShift",
                citations=[
                    CitationMemory(
                        chunk_id="chunk-1",
                        book_slug="architecture",
                        section="개요",
                        anchor="overview",
                        source_url="https://example.com/architecture",
                        viewer_path="/docs/architecture.html#overview",
                        excerpt="OpenShift 아키텍처 개요",
                    )
                ],
            ),
        )
        answerer = Part3Answerer(
            settings=Settings(root_dir=ROOT),
            retriever=retriever,
            llm_client=_ReplayLLMClient(),
        )

        result = answerer.answer(
            "그 문서 기준으로 OpenShift 아키텍처가 왜 그런지 설명해줘",
            mode="learn",
            context=context,
        )

        self.assertTrue(retriever.called)
        self.assertEqual("retrieved", result.citations[0].origin)
        self.assertTrue(
            any(
                event.get("step") == "citation_replay"
                and event.get("detail") == "requires_fresh_retrieval"
                for event in result.pipeline_trace["events"]
            )
        )

    def test_answerer_replays_prior_branch_when_query_returns_to_named_topic(self) -> None:
        context = SessionContext(
            mode="ops",
            current_topic="Certificates",
            active_citation_group=CitationGroupMemory(
                query="인증서 만료 확인",
                topic="Certificates",
                citations=[
                    CitationMemory(
                        chunk_id="chunk-cert",
                        book_slug="security",
                        section="인증서 만료 확인",
                        anchor="cert-monitor",
                        source_url="https://example.com/security",
                        viewer_path="/docs/security.html#cert-monitor",
                        excerpt="인증서 만료를 확인합니다.",
                    )
                ],
            ),
            citation_groups=[
                CitationGroupMemory(
                    query="RBAC rolebinding 설명",
                    topic="RBAC",
                    citations=[
                        CitationMemory(
                            chunk_id="chunk-rbac",
                            book_slug="authentication_and_authorization",
                            section="RoleBinding",
                            anchor="adding-roles",
                            source_url="https://example.com/rbac",
                            viewer_path="/docs/rbac.html#adding-roles",
                            excerpt="RoleBinding으로 권한을 부여합니다.",
                        )
                    ],
                ),
                CitationGroupMemory(
                    query="인증서 만료 확인",
                    topic="Certificates",
                    citations=[
                        CitationMemory(
                            chunk_id="chunk-cert",
                            book_slug="security",
                            section="인증서 만료 확인",
                            anchor="cert-monitor",
                            source_url="https://example.com/security",
                            viewer_path="/docs/security.html#cert-monitor",
                            excerpt="인증서 만료를 확인합니다.",
                        )
                    ],
                ),
            ],
        )
        answerer = Part3Answerer(
            settings=Settings(root_dir=ROOT),
            retriever=_ExplodingRetriever(),
            llm_client=_ReplayLLMClient(),
        )

        result = answerer.answer(
            "그때 RBAC 문서 기준으로 다시 정리해줘",
            mode="ops",
            context=context,
        )

        self.assertEqual("replayed", result.citations[0].origin)
        self.assertEqual("authentication_and_authorization", result.citations[0].book_slug)
        self.assertTrue(
            any(
                event.get("step") == "citation_replay"
                and event.get("status") == "done"
                for event in result.pipeline_trace["events"]
            )
        )

    def test_answerer_uses_prior_branch_focus_for_risky_return_query(self) -> None:
        class _TrackingRetriever:
            def __init__(self) -> None:
                self.called = False
                self.last_query = ""

            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                self.called = True
                self.last_query = query
                return _FakeRetriever().retrieve(
                    query,
                    context,
                    top_k,
                    candidate_k,
                    trace_callback=trace_callback,
                )

        retriever = _TrackingRetriever()
        context = SessionContext(
            mode="ops",
            current_topic="Certificates",
            active_citation_group=CitationGroupMemory(
                query="인증서 만료 확인",
                topic="Certificates",
                citations=[
                    CitationMemory(
                        chunk_id="chunk-cert",
                        book_slug="security",
                        section="인증서 만료 확인",
                        anchor="cert-monitor",
                        source_url="https://example.com/security",
                        viewer_path="/docs/security.html#cert-monitor",
                        excerpt="인증서 만료를 확인합니다.",
                    )
                ],
            ),
            citation_groups=[
                CitationGroupMemory(
                    query="RBAC rolebinding 설명",
                    topic="RBAC",
                    citations=[
                        CitationMemory(
                            chunk_id="chunk-rbac",
                            book_slug="authentication_and_authorization",
                            section="RoleBinding",
                            anchor="adding-roles",
                            source_url="https://example.com/rbac",
                            viewer_path="/docs/rbac.html#adding-roles",
                            excerpt="RoleBinding으로 권한을 부여합니다.",
                        )
                    ],
                ),
                CitationGroupMemory(
                    query="인증서 만료 확인",
                    topic="Certificates",
                    citations=[
                        CitationMemory(
                            chunk_id="chunk-cert",
                            book_slug="security",
                            section="인증서 만료 확인",
                            anchor="cert-monitor",
                            source_url="https://example.com/security",
                            viewer_path="/docs/security.html#cert-monitor",
                            excerpt="인증서 만료를 확인합니다.",
                        )
                    ],
                ),
            ],
        )
        answerer = Part3Answerer(
            settings=Settings(root_dir=ROOT),
            retriever=retriever,
            llm_client=_ReplayLLMClient(),
        )

        result = answerer.answer(
            "그때 RBAC 문서 기준으로 왜 그런지 설명해줘",
            mode="ops",
            context=context,
        )

        self.assertTrue(retriever.called)
        self.assertIn("Focused prior topic: RBAC", retriever.last_query)
        self.assertEqual("retrieved", result.citations[0].origin)
        self.assertTrue(
            any(event.get("step") == "citation_branch" for event in result.pipeline_trace["events"])
        )

    def test_answerer_aligns_drain_command_to_grounded_oc_command(self) -> None:
        class _DrainRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hit = RetrievalHit(
                    chunk_id="chunk-drain",
                    book_slug="nodes",
                    chapter="nodes",
                    section="6.2.1. 노드에서 Pod를 비우는 방법 이해",
                    anchor="drain",
                    source_url="https://example.com/nodes",
                    viewer_path="/docs/nodes.html#drain",
                    text="oc adm drain <노드명> --ignore-daemonsets --delete-emptydir-data",
                    source="hybrid",
                    raw_score=1.0,
                    fused_score=1.0,
                )
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=[hit],
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_DrainRetriever(),
            llm_client=_WrongDrainCommandLLMClient(),
        )

        result = answerer.answer("특정 작업자 노드를 drain 해야 해. 예시 명령이 뭐야?", mode="ops")

        self.assertIn("oc adm drain", result.answer)
        self.assertNotIn("kubectl drain", result.answer)

    def test_answerer_routes_out_of_corpus_version_question_without_retrieval(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_ExplodingRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("OpenShift 4.21에서 새로 추가된 기능만 정리해줘", mode="learn")

        self.assertEqual("no_answer", result.response_kind)
        self.assertIn("4.20 기준", result.answer)
        self.assertEqual([], result.citations)

    def test_answerer_routes_external_product_install_question_without_retrieval(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_ExplodingRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("Argo CD 설치 절차를 단계별로 알려줘", mode="ops")

        self.assertEqual("no_answer", result.response_kind)
        self.assertIn("설치", result.answer)
        self.assertEqual([], result.citations)

    def test_normalize_answer_text_enforces_single_answer_prefix(self) -> None:
        normalized = normalize_answer_text("### 답변\n안녕하세요\nOpenShift 설명입니다. [1]")

        self.assertEqual("답변: OpenShift 설명입니다. [1]", normalized)

    def test_reshape_ops_answer_text_wraps_bare_command(self) -> None:
        reshaped = reshape_ops_answer_text(
            "답변: $ oc adm policy add-role-to-user admin <사용자명> -n <namespace> [1]",
            mode="ops",
        )

        self.assertTrue(reshaped.startswith("답변: 아래 명령을 사용하세요 [1]."))
        self.assertIn("```bash", reshaped)
        self.assertIn("oc adm policy add-role-to-user admin <사용자명> -n <namespace>", reshaped)

    def test_strip_weak_additional_guidance_removes_empty_disclaimer_tail(self) -> None:
        stripped = _strip_weak_additional_guidance(
            "답변: 표준 절차는 다음과 같습니다 [1].\n\n추가 가이드: 현재 제공된 근거에 명시되어 있지 않습니다.",
            mode="ops",
            citations=[Citation(
                index=1,
                chunk_id="chunk-1",
                book_slug="postinstallation_configuration",
                section="4.12.5. etcd 데이터 백업",
                anchor="backup",
                source_url="https://example.com",
                viewer_path="/docs/example.html#backup",
                excerpt="cluster-backup.sh",
            )],
        )

        self.assertEqual("답변: 표준 절차는 다음과 같습니다 [1].", stripped)

    def test_ensure_korean_product_terms_keeps_both_names_for_compare_answer(self) -> None:
        updated = _ensure_korean_product_terms(
            "답변: 오픈시프트는 쿠버네티스 기반 플랫폼입니다.",
            query="오픈시프트랑 쿠버네티스 차이를 설명해줘 OpenShift",
        )

        self.assertIn("오픈시프트(OpenShift)", updated)

    def test_strip_intro_offtopic_noise_removes_etcd_backup_sentence(self) -> None:
        updated = _strip_intro_offtopic_noise(
            "답변: 오픈시프트는 플랫폼입니다. 클러스터 업데이트 전에는 반드시 etcd 백업을 수행해야 합니다.",
            query="오픈시프트가 뭐야?",
        )

        self.assertNotIn("etcd 백업", updated)

    def test_summarize_session_context_flattens_follow_up_hints(self) -> None:
        summary = summarize_session_context(
            SessionContext(
                mode="ops",
                current_topic="etcd 백업",
                open_entities=["etcd"],
                unresolved_question="복원 절차",
                ocp_version="4.20",
            )
        )

        self.assertIn("현재 주제: etcd 백업", summary)
        self.assertIn("열린 엔터티: etcd", summary)
        self.assertIn("미해결 질문: 복원 절차", summary)

    def test_summarize_session_context_includes_memory_ledgers(self) -> None:
        summary = summarize_session_context(
            SessionContext(
                mode="ops",
                current_topic="RBAC",
                topic_journal=["OpenShift", "RBAC"],
                reference_hints=["authentication_and_authorization · 9.6. 사용자 역할 추가"],
                recent_turns=[
                    TurnMemory(
                        query="특정 namespace만 admin 권한 주는 방법 단계별로 알려줘",
                        topic="RBAC",
                        answer_focus="namespace 단위 admin 권한은 RoleBinding으로 부여한다",
                        references=["authentication_and_authorization · 9.6. 사용자 역할 추가"],
                    )
                ],
                recent_steps=["명령을 통해 역할 바인딩 추가", "적용 결과 확인"],
                recent_commands=["oc adm policy add-role-to-user admin alice -n joe"],
                procedure_memory=ProcedureMemory(
                    goal="namespace admin 권한 부여",
                    steps=["명령을 통해 역할 바인딩 추가", "적용 결과 확인"],
                    active_step_index=1,
                    step_commands=[
                        "oc adm policy add-role-to-user admin alice -n joe",
                        "oc describe rolebinding -n joe",
                    ],
                    references=["authentication_and_authorization · 9.6. 사용자 역할 추가"],
                ),
                ocp_version="4.20",
            )
        )

        self.assertIn("최근 주제 흐름", summary)
        self.assertIn("최근 근거 메모", summary)
        self.assertIn("최근 대화 캡슐", summary)
        self.assertIn("최근 단계 메모", summary)
        self.assertIn("최근 명령 메모", summary)
        self.assertIn("진행 중 절차", summary)
        self.assertIn("절차 근거 메모", summary)

        self.assertIn("procedure step command map", summary)
        self.assertIn("oc describe rolebinding -n joe", summary)

    def test_augment_query_with_procedure_focus_prefers_requested_step(self) -> None:
        query = _augment_query_with_procedure_focus(
            "2번만 더 자세히",
            SessionContext(
                mode="ops",
                procedure_memory=ProcedureMemory(
                    goal="namespace admin role",
                    steps=["Create binding", "Verify binding"],
                    active_step_index=0,
                    step_commands=[
                        "oc adm policy add-role-to-user admin alice -n joe",
                        "oc describe rolebinding -n joe",
                    ],
                ),
            ),
        )

        self.assertIn("Focused procedure step: 2. Verify binding", query)
        self.assertIn("Expected step command: oc describe rolebinding -n joe", query)
        self.assertNotIn("Focused procedure step: 1. Create binding", query)

    def test_build_procedure_follow_up_answer_uses_requested_step_command(self) -> None:
        answer = _build_procedure_follow_up_answer(
            "2번만 더 자세히",
            SessionContext(
                mode="ops",
                procedure_memory=ProcedureMemory(
                    goal="namespace admin role",
                    steps=["Create binding", "Verify binding"],
                    active_step_index=0,
                    step_commands=[
                        "oc adm policy add-role-to-user admin alice -n joe",
                        "oc describe rolebinding -n joe",
                    ],
                ),
            ),
            [
                Citation(
                    index=1,
                    chunk_id="chunk-1",
                    book_slug="authentication_and_authorization",
                    section="RoleBinding",
                    anchor="adding-roles",
                    source_url="https://example.com/rbac",
                    viewer_path="/docs/rbac.html#adding-roles",
                    excerpt="RoleBinding verification",
                )
            ],
        )

        self.assertIsNotNone(answer)
        assert answer is not None
        self.assertIn("2번 단계는 Verify binding입니다.", answer)
        self.assertIn("oc describe rolebinding -n joe", answer)
        self.assertNotIn("oc adm policy add-role-to-user admin alice -n joe", answer)

    def test_finalize_citations_collapses_duplicate_targets(self) -> None:
        citations = [
            Citation(
                index=1,
                chunk_id="chunk-1",
                book_slug="support",
                section="7.2.1. 노드 상태, 리소스 사용량 및 구성 확인",
                anchor="checking-node-resource-usage",
                source_url="https://example.com/support",
                viewer_path="/docs/ocp/4.20/ko/support/index.html#checking-node-resource-usage",
                excerpt="oc adm top nodes",
            ),
            Citation(
                index=2,
                chunk_id="chunk-2",
                book_slug="support",
                section="7.2.1. 노드 상태, 리소스 사용량 및 구성 확인",
                anchor="checking-node-resource-usage",
                source_url="https://example.com/support",
                viewer_path="/docs/ocp/4.20/ko/support/index.html#checking-node-resource-usage",
                excerpt="oc adm top node my-node",
            ),
        ]

        answer_text, final_citations, cited_indices = finalize_citations(
            "답변: `oc adm top nodes` 명령을 사용하세요 [1][2].",
            citations,
        )

        self.assertEqual("답변: `oc adm top nodes` 명령을 사용하세요 [1].", answer_text)
        self.assertEqual([1], cited_indices)
        self.assertEqual(1, len(final_citations))

    def test_answerer_deduplicates_same_section_citations(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_DuplicateCitationRetriever(),
            llm_client=_DuplicateCitationLLMClient(),
        )

        result = answerer.answer(
            "지금 클러스터 내 전체 노드들의 CPU랑 메모리 사용량을 한눈에 확인하고 싶은데, 어떤 CLI 명령어를 써야 해?",
            mode="ops",
        )

        self.assertEqual(
            "답변: `oc adm top nodes` 명령으로 한눈에 확인하세요 [1].",
            result.answer,
        )
        self.assertEqual([1], result.cited_indices)
        self.assertEqual(1, len(result.citations))
        self.assertEqual(
            "/docs/ocp/4.20/ko/support/index.html#checking-node-resource-usage",
            result.citations[0].viewer_path,
        )

    def test_answerer_autorepairs_single_missing_inline_citation(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_FakeRetriever(),
            llm_client=_NoCitationLLMClient(),
        )

        result = answerer.answer(
            "특정 namespace에만 admin 권한 주려면 어떤 명령 써?",
            mode="ops",
        )

        self.assertIn("[1]", result.answer)
        self.assertEqual([1], result.cited_indices)
        self.assertEqual(1, len(result.citations))
        self.assertNotIn("inline citations auto-repaired", result.warnings)

    def test_answerer_reshapes_bare_ops_command_response(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_FakeRetriever(),
            llm_client=_BareCommandLLMClient(),
        )

        result = answerer.answer(
            "특정 namespace에만 admin 권한 주려면 어떤 명령 써?",
            mode="ops",
        )

        self.assertTrue(result.answer.startswith("답변: 아래 명령을 사용하세요 [1]."))
        self.assertIn("```bash", result.answer)
        self.assertIn("oc adm policy add-role-to-user admin <사용자명> -n <namespace>", result.answer)

    def test_llm_client_parses_chat_completions_response(self) -> None:
        settings = Settings(root_dir=ROOT)
        settings.llm_endpoint = "http://llm.local/v1"
        settings.llm_model = "demo-model"

        client = LLMClient(settings)

        import requests
        from unittest.mock import patch

        with patch.object(
            requests,
            "post",
            return_value=_FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": "답변: 테스트입니다. [1]",
                            }
                        }
                    ]
                }
            ),
        ) as mocked_post:
            content = client.generate([{"role": "user", "content": "질문"}])

        self.assertEqual("답변: 테스트입니다. [1]", content)
        self.assertEqual(
            "http://llm.local/v1/chat/completions",
            mocked_post.call_args.args[0],
        )
        self.assertEqual({}, mocked_post.call_args.kwargs["headers"])
        self.assertFalse(mocked_post.call_args.kwargs["json"]["reasoning"])
        self.assertFalse(
            mocked_post.call_args.kwargs["json"]["chat_template_kwargs"]["enable_thinking"]
        )

    def test_llm_client_retries_without_reasoning_controls(self) -> None:
        settings = Settings(root_dir=ROOT)
        settings.llm_endpoint = "http://llm.local:8080/v1"
        settings.llm_model = "demo-model"

        client = LLMClient(settings)

        import requests
        from unittest.mock import patch

        responses = [
            _FakeResponse(
                {"error": {"message": "json: cannot unmarshal bool into Go struct field ChatCompletionRequest.reasoning of type openai.Reasoning"}},
                status_code=400,
                text="json: cannot unmarshal bool into Go struct field ChatCompletionRequest.reasoning of type openai.Reasoning",
            ),
            _FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": "답변: 테스트입니다. [1]",
                            }
                        }
                    ]
                }
            ),
        ]

        with patch.object(requests, "post", side_effect=responses) as mocked_post:
            content = client.generate([{"role": "user", "content": "질문"}])

        self.assertEqual("답변: 테스트입니다. [1]", content)
        self.assertIn("reasoning", mocked_post.call_args_list[0].kwargs["json"])
        self.assertNotIn("reasoning", mocked_post.call_args_list[1].kwargs["json"])
        self.assertNotIn("chat_template_kwargs", mocked_post.call_args_list[1].kwargs["json"])

    def test_llm_client_falls_back_to_ollama_native_when_openai_content_is_empty(self) -> None:
        settings = Settings(root_dir=ROOT)
        settings.llm_endpoint = "http://llm.local:8080/v1"
        settings.llm_model = "demo-model"

        client = LLMClient(settings)

        import requests
        from unittest.mock import patch

        responses = [
            _FakeResponse(
                {
                    "id": "chatcmpl-1",
                    "object": "chat.completion",
                    "model": "qwen3.5:9b",
                    "system_fingerprint": "fp_ollama",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "", "reasoning": "Thinking"},
                            "finish_reason": "length",
                        }
                    ],
                }
            ),
            _FakeResponse(
                {
                    "model": "qwen3.5:9b",
                    "message": {"role": "assistant", "content": "ok"},
                    "done": True,
                }
            ),
        ]

        with patch.object(requests, "post", side_effect=responses) as mocked_post:
            content = client.generate([{"role": "user", "content": "질문"}])

        self.assertEqual("ok", content)
        self.assertEqual(
            "http://llm.local:8080/api/chat",
            mocked_post.call_args_list[1].args[0],
        )
        self.assertFalse(mocked_post.call_args_list[1].kwargs["json"]["stream"])
        self.assertFalse(mocked_post.call_args_list[1].kwargs["json"]["think"])

    def test_llm_client_prefers_ollama_native_for_tagged_model_names(self) -> None:
        settings = Settings(root_dir=ROOT)
        settings.llm_endpoint = "http://llm.local:8080/v1"
        settings.llm_model = "qwen3.5:9b"

        client = LLMClient(settings)

        import requests
        from unittest.mock import patch

        with patch.object(
            requests,
            "post",
            return_value=_FakeResponse(
                {
                    "model": "qwen3.5:9b",
                    "message": {"role": "assistant", "content": "ok"},
                    "done": True,
                }
            ),
        ) as mocked_post:
            content = client.generate([{"role": "user", "content": "질문"}])

        self.assertEqual("ok", content)
        self.assertEqual("http://llm.local:8080/api/chat", mocked_post.call_args.args[0])
        self.assertFalse(mocked_post.call_args.kwargs["json"]["stream"])
        self.assertFalse(mocked_post.call_args.kwargs["json"]["think"])

    def test_llm_client_sends_bearer_authorization_when_api_key_is_set(self) -> None:
        settings = Settings(root_dir=ROOT)
        settings.llm_endpoint = "http://llm.local/v1"
        settings.llm_model = "demo-model"
        settings.llm_api_key = "llm-secret"

        client = LLMClient(settings)

        import requests
        from unittest.mock import patch

        with patch.object(
            requests,
            "post",
            return_value=_FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": "답변: 테스트입니다. [1]",
                            }
                        }
                    ]
                }
            ),
        ) as mocked_post:
            content = client.generate([{"role": "user", "content": "질문"}])

        self.assertEqual("답변: 테스트입니다. [1]", content)
        self.assertEqual(
            {"Authorization": "Bearer llm-secret"},
            mocked_post.call_args.kwargs["headers"],
        )


if __name__ == "__main__":
    unittest.main()
