from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import Settings
from play_book_studio.retrieval.models import RetrievalHit, RetrievalResult, SessionContext
from play_book_studio.answering.answerer import (
    _normalize_answer_markup_blocks,
    _ensure_korean_product_terms,
    _strip_intro_offtopic_noise,
    _strip_structured_key_extra_guidance,
    Part3Answerer,
    finalize_citations,
    normalize_answer_text,
    reshape_ops_answer_text,
    select_fallback_citations,
    _strip_weak_additional_guidance,
    summarize_session_context,
)
from play_book_studio.answering.models import Citation
from play_book_studio.answering.llm import LLMClient
from play_book_studio.answering.prompt import build_messages


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


class _MultiCitationRetriever:
    def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
        hits = [
            RetrievalHit(
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
            ),
            RetrievalHit(
                chunk_id="chunk-2",
                book_slug="overview",
                chapter="overview",
                section="플랫폼 개요",
                anchor="platform-overview",
                source_url="https://example.com/overview",
                viewer_path="/docs/overview.html#platform-overview",
                text="OpenShift Container Platform은 쿠버네티스 기반 플랫폼입니다.",
                source="hybrid",
                raw_score=0.94,
                fused_score=0.94,
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


class _PodLifecycleRetriever:
    def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
        hits = [
            RetrievalHit(
                chunk_id="chunk-1",
                book_slug="nodes",
                chapter="nodes",
                section="2.1.1. Pod 이해",
                anchor="pod-understanding",
                source_url="https://example.com/nodes",
                viewer_path="/docs/nodes.html#pod-understanding",
                text="Pod에는 라이프사이클이 정의되어 있으며 노드에서 실행되도록 할당된 다음 컨테이너가 종료되거나 기타 이유로 제거될 때까지 실행됩니다.",
                source="hybrid",
                raw_score=1.0,
                fused_score=1.0,
            ),
            RetrievalHit(
                chunk_id="chunk-2",
                book_slug="nodes",
                chapter="nodes",
                section="2.1.2. Pod 구성의 예",
                anchor="pod-example",
                source_url="https://example.com/nodes",
                viewer_path="/docs/nodes.html#pod-example",
                text="이 Pod 정의에는 Pod가 생성되고 해당 라이프사이클이 시작된 후 자동으로 채워지는 특성은 포함되지 않습니다.",
                source="hybrid",
                raw_score=0.95,
                fused_score=0.95,
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


class _PodPendingRetriever:
    def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
        hits = [
            RetrievalHit(
                chunk_id="chunk-1",
                book_slug="nodes",
                chapter="nodes",
                section="8.1.3. 이벤트 목록",
                anchor="nodes-containers-events-list_nodes-containers-events",
                source_url="https://example.com/nodes",
                viewer_path="/docs/nodes.html#nodes-containers-events-list_nodes-containers-events",
                text="`FailedScheduling` 이벤트는 Pod 예약 실패 원인을 보여 주며 다양한 이유로 발생할 수 있습니다.",
                source="hybrid",
                raw_score=1.0,
                fused_score=1.0,
            ),
            RetrievalHit(
                chunk_id="chunk-2",
                book_slug="nodes",
                chapter="nodes",
                section="4.4.4.2. 일치하는 라벨이 없는 노드 유사성",
                anchor="admin-guide-sched-affinity-examples2_nodes-scheduler-node-affinity",
                source_url="https://example.com/nodes",
                viewer_path="/docs/nodes.html#admin-guide-sched-affinity-examples2_nodes-scheduler-node-affinity",
                text="Pod는 node affinity 조건이 맞지 않으면 예약할 수 없으며, `oc describe pod` 출력의 Events로 이를 확인할 수 있습니다.",
                source="hybrid",
                raw_score=0.95,
                fused_score=0.95,
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


class _SinglePodLifecycleRetriever:
    def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
        hits = [
            RetrievalHit(
                chunk_id="chunk-1",
                book_slug="nodes",
                chapter="nodes",
                section="2.1.1. Pod 이해",
                anchor="pod-understanding",
                source_url="https://example.com/nodes",
                viewer_path="/docs/nodes.html#pod-understanding",
                text="Pod에는 라이프사이클이 정의되어 있으며 노드에서 실행되도록 할당된 다음 컨테이너가 종료되거나 제거될 때까지 실행됩니다.",
                source="hybrid",
                raw_score=1.0,
                fused_score=1.0,
            )
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


class _SinglePodPendingRetriever:
    def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
        hits = [
            RetrievalHit(
                chunk_id="chunk-1",
                book_slug="nodes",
                chapter="nodes",
                section="8.1.3. 이벤트 목록",
                anchor="nodes-containers-events-list_nodes-containers-events",
                source_url="https://example.com/nodes",
                viewer_path="/docs/nodes.html#nodes-containers-events-list_nodes-containers-events",
                text="`FailedScheduling` 이벤트는 Pod 예약 실패 원인을 보여 주며 다양한 이유로 발생할 수 있습니다.",
                source="hybrid",
                raw_score=1.0,
                fused_score=1.0,
            )
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


class _NarrativeNoCitationLLMClient:
    def generate(self, messages, trace_callback=None):  # noqa: ANN001
        self.messages = messages
        if trace_callback is not None:
            trace_callback(
                {
                    "step": "llm_generate",
                    "label": "LLM 응답 생성 완료",
                    "status": "done",
                    "duration_ms": 1.9,
                }
            )
        return "답변: OpenShift는 컨트롤 플레인과 작업자 노드로 구성된 플랫폼입니다."


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


class _EtcdBackupRetriever:
    def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
        hit = RetrievalHit(
            chunk_id="etcd-backup",
            book_slug="postinstallation_configuration",
            chapter="설치 후 구성",
            section="4.12.5. etcd 데이터 백업",
            anchor="etcd-backup",
            source_url="https://example.com/postinstall",
            viewer_path="/docs/postinstall.html#etcd-backup",
            text="cluster-backup.sh 스크립트는 etcdctl snapshot save 명령 관련 래퍼입니다.",
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


class _EtcdBackupOverclaimLLMClient:
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
            "답변: OCP 클러스터에서 etcd 데이터를 백업하려면 먼저 환경 변수인 "
            "`HTTPS_PROXY` 와 `NO_PROXY` 를 설정한 뒤 스크립트를 실행해야 합니다 [1].\n\n"
            "```bash\n"
            "export HTTPS_PROXY=https://proxy.example.com:8080\n"
            "export NO_PROXY=example.com\n"
            "/usr/local/bin/cluster-backup.sh /home/core/assets/backup\n"
            "```"
        )


class _CertificateMonitorRetriever:
    def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
        hit = RetrievalHit(
            chunk_id="cert-monitor",
            book_slug="cli_tools",
            chapter="CLI",
            section="2.7.1.25. oc adm ocp-certificates monitor-certificates",
            anchor="monitor-certificates",
            source_url="https://example.com/cli",
            viewer_path="/docs/cli.html#monitor-certificates",
            text="플랫폼 인증서 감시 사용 예. oc adm ocp-certificates monitor-certificates",
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


class _CertificateOverclaimLLMClient:
    def generate(self, messages, trace_callback=None):  # noqa: ANN001
        self.messages = messages
        if trace_callback is not None:
            trace_callback(
                {
                    "step": "llm_generate",
                    "label": "LLM 응답 생성 완료",
                    "status": "done",
                    "duration_ms": 1.6,
                }
            )
        return (
            "답변: OCP API 서버 인증서 만료 임박 여부를 확인하려면 "
            "`oc adm ocp-certificates monitor-certificates` 명령을 실행하여 "
            "플랫폼 인증서의 상태를 실시간으로 감시합니다 [1]. "
            "이 명령은 인증서 만료 기간을 모니터링하고 만료 임박 시 경고를 제공합니다."
        )


class _DeploymentScaleRetriever:
    def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
        hits = [
            RetrievalHit(
                chunk_id="cli-scale",
                book_slug="cli_tools",
                chapter="2장. OpenShift CLI(oc)",
                section="2.6.1.124. oc scale",
                anchor="oc-scale",
                source_url="https://example.com/cli",
                viewer_path="/docs/ocp/4.20/ko/cli_tools/index.html#oc-scale",
                text="oc scale --current-replicas=2 --replicas=3 deployment/mysql",
                source="hybrid",
                raw_score=1.0,
                fused_score=1.0,
            ),
            RetrievalHit(
                chunk_id="rollover",
                book_slug="building_applications",
                chapter="7장. 배포",
                section="7.1.4.2.1. 롤오버",
                anchor="rollover",
                source_url="https://example.com/building",
                viewer_path="/docs/ocp/4.20/ko/building_applications/index.html#rollover",
                text="기존 복제본 세트를 축소하고 새 복제본 세트를 확장합니다.",
                source="hybrid",
                raw_score=0.8,
                fused_score=0.8,
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
        from play_book_studio.answering.context import assemble_context

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
        from play_book_studio.answering.context import assemble_context

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

    def test_build_messages_expands_learn_mode_explanations(self) -> None:
        messages = build_messages(
            query="CrashLoopBackOff가 반복될 때 확인 순서를 설명해줘",
            mode="learn",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("필요한 흐름과 이유와 확인 포인트를 충분히 설명하라", messages[0]["content"])
        self.assertIn("단계마다 왜 필요한지와 무엇을 확인해야 하는지 1~2문장씩 덧붙일 것", messages[1]["content"])
        self.assertIn("단계마다 왜 필요한지와 무엇을 확인해야 하는지 1~2문장씩 덧붙일 것", messages[1]["content"])
        self.assertIn("[CODE], [/CODE], [TABLE], [/TABLE] 같은 내부 태그를 답변에 그대로 노출하지 말고", messages[0]["content"])
        self.assertIn("[CODE], [/CODE], [TABLE], [/TABLE] 같은 내부 태그를 답변에 그대로 쓰지 말 것", messages[1]["content"])
        self.assertIn("OOM은 가능한 원인 중 하나", messages[1]["content"])

    def test_build_messages_adds_pod_pending_shape_hint(self) -> None:
        messages = build_messages(
            query="Pod Pending일 때 어디부터 확인해야 해?",
            mode="learn",
            context_bundle=type("Bundle", (), {"prompt_context": "[1] ...", "citations": []})(),
            session_summary="",
        )

        self.assertIn("이벤트로 FailedScheduling 이유 확인", messages[1]["content"])
        self.assertIn("첫 단계는 Pod Events 확인", messages[1]["content"])

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
        self.assertIn("OCP 질문을 입력해 주세요.", result.answer)
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
        self.assertIn("OCP 질문에 답하는 챗봇", result.answer)
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

    def test_answerer_shapes_etcd_backup_answer_without_proxy_overclaim(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_EtcdBackupRetriever(),
            llm_client=_EtcdBackupOverclaimLLMClient(),
        )

        result = answerer.answer("etcd 백업은 실제로 어떤 절차로 해?", mode="ops")

        self.assertIn("oc debug --as-root node/<node_name>", result.answer)
        self.assertIn("chroot /host", result.answer)
        self.assertIn("cluster-backup.sh", result.answer)
        self.assertNotIn("HTTPS_PROXY", result.answer)
        self.assertNotIn("NO_PROXY", result.answer)

    def test_answerer_shapes_certificate_monitor_answer_without_overclaim(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_CertificateMonitorRetriever(),
            llm_client=_CertificateOverclaimLLMClient(),
        )

        result = answerer.answer("ocp api 서버 인증서 만료 임박했는지 어떻게 확인해?", mode="ops")

        self.assertIn("oc adm ocp-certificates monitor-certificates", result.answer)
        self.assertNotIn("실시간으로 감시", result.answer)
        self.assertNotIn("경고를 제공", result.answer)

    def test_answerer_returns_deterministic_deployment_scale_command_when_grounded(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_DeploymentScaleRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer(
            "5개에서 10개로 변경도돼?",
            mode="ops",
            context=SessionContext(
                mode="ops",
                user_goal="실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
                current_topic="Deployment 스케일링",
                ocp_version="4.20",
            ),
        )

        self.assertIn("oc scale --current-replicas=5 --replicas=10", result.answer)
        self.assertIn("deployment/<deployment-name>", result.answer)
        self.assertEqual("rag", result.response_kind)
        self.assertEqual("cli_tools", result.citations[0].book_slug)

    def test_answerer_asks_for_target_when_corrective_command_request_lacks_numbers(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_DeploymentScaleRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer(
            "그럼 명령어라도 알려줘",
            mode="ops",
            context=SessionContext(
                mode="ops",
                user_goal="실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
                current_topic="Deployment 스케일링",
                ocp_version="4.20",
            ),
        )

        self.assertEqual("clarification", result.response_kind)
        self.assertIn("몇 개로 바꾸려는지", result.answer)

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

    def test_normalize_answer_markup_blocks_converts_internal_code_tags(self) -> None:
        normalized = _normalize_answer_markup_blocks(
            "답변: 확인 순서는 다음과 같습니다.\n[CODE]\noc describe pod/<pod>\n[/CODE]"
        )

        self.assertNotIn("[CODE]", normalized)
        self.assertIn("```bash", normalized)
        self.assertIn("oc describe pod/<pod>", normalized)

    def test_normalize_answer_markup_blocks_converts_internal_table_tags(self) -> None:
        normalized = _normalize_answer_markup_blocks(
            "답변: 표는 아래와 같습니다.\n[TABLE]\n이름 | 상태\npod-a | Pending\n[/TABLE]"
        )

        self.assertNotIn("[TABLE]", normalized)
        self.assertIn("```text", normalized)
        self.assertIn("이름 | 상태", normalized)

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

    def test_strip_structured_key_extra_guidance_removes_speculative_tail(self) -> None:
        stripped = _strip_structured_key_extra_guidance(
            "답변: 값은 `starfall-88` 입니다 [1].\n\n추가 가이드: 예: orion status check 등으로 확인하세요.",
            query="orion.unique/flag 값이 뭐야?",
            mode="ops",
        )

        self.assertEqual("답변: 값은 `starfall-88` 입니다 [1].", stripped)

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

    def test_finalize_citations_strips_invalid_reference_markers(self) -> None:
        citations = [
            Citation(
                index=1,
                chunk_id="chunk-1",
                book_slug="nodes",
                section="8.1.3. 이벤트 목록",
                anchor="events",
                source_url="https://example.com/nodes",
                viewer_path="/docs/nodes.html#events",
                excerpt="이벤트",
            )
        ]

        answer_text, final_citations, cited_indices = finalize_citations(
            "답변: 먼저 [1][2]를 보고, 다음 단계도 [2] 대신 [1]을 기준으로 판단합니다.",
            citations,
        )

        self.assertEqual(
            "답변: 먼저 [1]를 보고, 다음 단계도 대신 [1]을 기준으로 판단합니다.",
            answer_text,
        )
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
            "답변: 클러스터 전체 노드의 CPU와 메모리 사용량은 아래 명령으로 확인합니다 [1].\n\n```bash\noc adm top nodes\n```",
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

    def test_select_fallback_citations_deduplicates_and_limits(self) -> None:
        citations = [
            Citation(
                index=1,
                chunk_id="chunk-1",
                book_slug="support",
                section="A",
                anchor="same",
                source_url="https://example.com/support",
                viewer_path="/docs/support.html#same",
                excerpt="first",
            ),
            Citation(
                index=2,
                chunk_id="chunk-2",
                book_slug="support",
                section="A",
                anchor="same",
                source_url="https://example.com/support",
                viewer_path="/docs/support.html#same",
                excerpt="second",
            ),
            Citation(
                index=3,
                chunk_id="chunk-3",
                book_slug="nodes",
                section="B",
                anchor="other",
                source_url="https://example.com/nodes",
                viewer_path="/docs/nodes.html#other",
                excerpt="third",
            ),
        ]

        selected = select_fallback_citations(citations, limit=2)

        self.assertEqual(2, len(selected))
        self.assertEqual([1, 2], [citation.index for citation in selected])
        self.assertEqual(
            ["/docs/support.html#same", "/docs/nodes.html#other"],
            [citation.viewer_path for citation in selected],
        )

    def test_answerer_preserves_source_tags_when_learn_answer_has_no_inline_citations(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_MultiCitationRetriever(),
            llm_client=_NarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("OpenShift 아키텍처를 설명해줘", mode="learn")

        self.assertGreaterEqual(len(result.citations), 1)
        self.assertEqual("/docs/architecture.html#overview", result.citations[0].viewer_path)
        self.assertNotIn("inline citations auto-repaired", result.warnings)

    def test_answerer_shapes_pod_lifecycle_learn_response_from_grounded_citations(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_PodLifecycleRetriever(),
            llm_client=_NarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("Pod lifecycle 개념을 초보자 기준으로 설명해줘", mode="learn")

        self.assertIn("Pod 라이프사이클은 Pod가 생성되고 노드에 배치된 뒤", result.answer)
        self.assertIn("생성/배치", result.answer)
        self.assertIn("종료/교체", result.answer)
        self.assertIn("[1]", result.answer)
        self.assertNotIn("같이 보면 좋은 문서", result.answer)
        self.assertEqual(
            ["2.1.1. Pod 이해", "2.1.2. Pod 구성의 예"],
            [citation.section for citation in result.citations],
        )

    def test_answerer_shapes_pod_lifecycle_without_leaking_missing_second_citation(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_SinglePodLifecycleRetriever(),
            llm_client=_NarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("Pod lifecycle 개념을 초보자 기준으로 설명해줘", mode="learn")

        self.assertIn("[1]", result.answer)
        self.assertNotIn("[2]", result.answer)
        self.assertEqual([1], result.cited_indices)
        self.assertEqual(1, len(result.citations))

    def test_answerer_shapes_pod_pending_learn_response_from_grounded_citations(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_PodPendingRetriever(),
            llm_client=_NarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("Pod Pending일 때 어디부터 확인해야 해?", mode="learn")

        self.assertIn("Pod가 `Pending`이면 가장 먼저", result.answer)
        self.assertIn("oc describe pod <pod-name> -n <pod-namespace>", result.answer)
        self.assertIn("FailedScheduling", result.answer)
        self.assertIn("[1]", result.answer)
        self.assertIn("[2]", result.answer)
        self.assertEqual(
            ["8.1.3. 이벤트 목록", "4.4.4.2. 일치하는 라벨이 없는 노드 유사성"],
            [citation.section for citation in result.citations],
        )

    def test_answerer_shapes_pod_pending_without_leaking_missing_second_citation(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = Part3Answerer(
            settings=settings,
            retriever=_SinglePodPendingRetriever(),
            llm_client=_NarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("Pod Pending일 때 어디부터 확인해야 해?", mode="learn")

        self.assertIn("[1]", result.answer)
        self.assertNotIn("[2]", result.answer)
        self.assertEqual([1], result.cited_indices)
        self.assertEqual(1, len(result.citations))

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
