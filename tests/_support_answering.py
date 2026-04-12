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
from play_book_studio.answering.answer_text_commands import shape_actionable_ops_answer
from play_book_studio.answering.answer_text_formatting import (
    ensure_korean_product_terms,
    normalize_answer_markup_blocks,
    normalize_answer_text,
    restore_readable_paragraphs,
    reshape_ops_answer_text,
    strip_intro_offtopic_noise,
    strip_structured_key_extra_guidance,
    strip_weak_additional_guidance,
    summarize_session_context,
)
from play_book_studio.answering.answerer import ChatAnswerer
from play_book_studio.answering.citations import finalize_citations, select_fallback_citations
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
        hits = [
            RetrievalHit(
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
            ),
            RetrievalHit(
                chunk_id="etcd-dedicated",
                book_slug="etcd",
                chapter="etcd",
                section="4.3.2. etcd 백업 및 복원",
                anchor="etcd-backup-restore",
                source_url="https://example.com/etcd",
                viewer_path="/docs/etcd.html#etcd-backup-restore",
                text="etcd 전용 절차 문서는 백업과 복원 흐름을 함께 설명합니다.",
                source="hybrid",
                raw_score=0.82,
                fused_score=0.82,
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

__all__ = [
    "Settings",
    "RetrievalHit",
    "RetrievalResult",
    "SessionContext",
    "shape_actionable_ops_answer",
    "normalize_answer_markup_blocks",
    "ensure_korean_product_terms",
    "strip_intro_offtopic_noise",
    "strip_structured_key_extra_guidance",
    "ChatAnswerer",
    "finalize_citations",
    "normalize_answer_text",
    "reshape_ops_answer_text",
    "select_fallback_citations",
    "strip_weak_additional_guidance",
    "summarize_session_context",
    "Citation",
    "LLMClient",
    "build_messages",
    "_FakeRetriever",
    "_DuplicateCitationRetriever",
    "_MultiCitationRetriever",
    "_PodLifecycleRetriever",
    "_PodPendingRetriever",
    "_SinglePodLifecycleRetriever",
    "_SinglePodPendingRetriever",
    "_DuplicateCitationLLMClient",
    "_FakeLLMClient",
    "_NoCitationLLMClient",
    "_BareCommandLLMClient",
    "_NarrativeNoCitationLLMClient",
    "_WrongDrainCommandLLMClient",
    "_EtcdBackupRetriever",
    "_EtcdBackupOverclaimLLMClient",
    "_CertificateMonitorRetriever",
    "_CertificateOverclaimLLMClient",
    "_DeploymentScaleRetriever",
    "_ExplodingRetriever",
    "_FakeResponse",
]
