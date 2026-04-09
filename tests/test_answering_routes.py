from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_answering import (
    ChatAnswerer,
    RetrievalHit,
    RetrievalResult,
    SessionContext,
    Settings,
    _CertificateMonitorRetriever,
    _CertificateOverclaimLLMClient,
    _DeploymentScaleRetriever,
    _EtcdBackupOverclaimLLMClient,
    _EtcdBackupRetriever,
    _ExplodingRetriever,
    _FakeLLMClient,
    _FakeRetriever,
    _WrongDrainCommandLLMClient,
)

class TestAnsweringRoutes(unittest.TestCase):
    def test_answerer_returns_citations_and_used_indices(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
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
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_ExplodingRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("하이", mode="ops")

        self.assertEqual("smalltalk", result.response_kind)
        self.assertEqual([], result.citations)
        self.assertEqual([], result.cited_indices)
        self.assertFalse(result.warnings)
        self.assertIn("OCP PlayBook 챗봇", result.answer)
        self.assertIn("편하게 질문", result.answer)
        self.assertTrue(
            any(event.get("step") == "route_query" for event in result.pipeline_trace["events"])
        )
        self.assertEqual("smalltalk", result.retrieval_trace["route"])

    def test_answerer_routes_short_nontechnical_smalltalk_without_retrieval(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_ExplodingRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("어드레감수광", mode="ops")

        self.assertEqual("smalltalk", result.response_kind)
        self.assertIn("OCP PlayBook 챗봇", result.answer)
        self.assertIn("가볍게 말을 붙여도 괜찮습니다", result.answer)
        self.assertEqual([], result.citations)

    def test_answerer_routes_meta_question_without_retrieval(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_ExplodingRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("넌 누구야?", mode="ops")

        self.assertEqual("meta", result.response_kind)
        self.assertIn("OCP PlayBook 챗봇", result.answer)
        self.assertIn("실행 가이드", result.answer)
        self.assertEqual([], result.citations)
        self.assertFalse(result.warnings)

    def test_answerer_routes_generic_ocp_intro_without_retrieval(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_ExplodingRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("OCP가 뭐야?", mode="learn")

        self.assertEqual("guide", result.response_kind)
        self.assertIn("오픈시프트", result.answer)
        self.assertIn("쿠버네티스", result.answer)
        self.assertIn("엔터프라이즈 컨테이너 플랫폼", result.answer)
        self.assertEqual([], result.citations)

    def test_answerer_routes_ocp_learning_advice_without_retrieval(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_ExplodingRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("오픈시프트를 잘하려면 어떻게 해야 돼?", mode="learn")

        self.assertEqual("guide", result.response_kind)
        self.assertIn("리눅스 기본기", result.answer)
        self.assertIn("쿠버네티스", result.answer)
        self.assertIn("oc CLI", result.answer)
        self.assertEqual([], result.citations)

    def test_answerer_routes_ambiguous_log_question_to_clarification(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
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
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_DrainRetriever(),
            llm_client=_WrongDrainCommandLLMClient(),
        )

        result = answerer.answer("특정 작업자 노드를 drain 해야 해. 예시 명령이 뭐야?", mode="ops")

        self.assertIn("oc adm drain", result.answer)
        self.assertNotIn("kubectl drain", result.answer)

    def test_answerer_shapes_etcd_backup_answer_without_proxy_overclaim(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_EtcdBackupRetriever(),
            llm_client=_EtcdBackupOverclaimLLMClient(),
        )

        result = answerer.answer("etcd 백업은 실제로 어떤 절차로 해?", mode="ops")

        self.assertIn("oc debug --as-root node/<node_name>", result.answer)
        self.assertIn("chroot /host", result.answer)
        self.assertIn("/usr/local/bin/cluster-backup.sh /home/core/assets/backup", result.answer)
        self.assertNotIn("HTTPS_PROXY", result.answer)
        self.assertNotIn("NO_PROXY", result.answer)

    def test_answerer_shapes_certificate_monitor_answer_without_overclaim(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_CertificateMonitorRetriever(),
            llm_client=_CertificateOverclaimLLMClient(),
        )

        result = answerer.answer("ocp api 서버 인증서 만료 임박했는지 어떻게 확인해?", mode="ops")

        self.assertIn(
            "`oc adm ocp-certificates monitor-certificates` 명령으로 모니터링해 확인합니다",
            result.answer,
        )
        self.assertNotIn("실시간으로 감시", result.answer)
        self.assertNotIn("경고를 제공", result.answer)

    def test_answerer_returns_deterministic_deployment_scale_command_when_grounded(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
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
        answerer = ChatAnswerer(
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
        answerer = ChatAnswerer(
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
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_ExplodingRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("Argo CD 설치 절차를 단계별로 알려줘", mode="ops")

        self.assertEqual("no_answer", result.response_kind)
        self.assertIn("설치", result.answer)
        self.assertEqual([], result.citations)
