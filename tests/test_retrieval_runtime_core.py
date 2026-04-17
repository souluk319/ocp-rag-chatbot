from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_retrieval import BM25Index, ChatRetriever, RetrievalHit, SeededBm25, SessionContext, Settings, _FakeRetrieverWithReranker, fuse_ranked_hits
from play_book_studio.retrieval.trace import build_retrieval_trace
from play_book_studio.retrieval.retriever_rerank import maybe_rerank_hits


class TestRetrievalRuntimeCore(unittest.TestCase):
    def test_retriever_raises_when_vector_path_is_requested_but_unconfigured(self) -> None:
        settings = Settings(root_dir=ROOT)
        retriever = ChatRetriever(settings, BM25Index.from_rows([]), vector_retriever=None)

        with self.assertRaisesRegex(RuntimeError, "vector retriever is not configured"):
            retriever.retrieve("OpenShift 아키텍처 설명", top_k=3, candidate_k=3)

    def test_fusion_boosts_backup_book_for_backup_doc_locator_query(self) -> None:
        etcd_hit = RetrievalHit(
            chunk_id="etcd-hit",
            book_slug="etcd",
            chapter="etcd",
            section="etcd 재해 복구",
            anchor="etcd-dr",
            source_url="https://example.com/etcd",
            viewer_path="/docs/etcd.html#dr",
            text="etcd 백업에서 클러스터를 복구하는 절차",
            source="bm25",
            raw_score=0.80,
            fused_score=0.80,
        )
        backup_hit = RetrievalHit(
            chunk_id="backup-hit",
            book_slug="backup_and_restore",
            chapter="backup",
            section="백업 및 복구 문서 개요",
            anchor="backup-overview",
            source_url="https://example.com/backup",
            viewer_path="/docs/backup.html#overview",
            text="백업과 복구 관련 문서와 절차를 모은 가이드",
            source="vector",
            raw_score=0.74,
            fused_score=0.74,
        )

        hits = fuse_ranked_hits(
            "백업 복구 문서는 어디서 봐? 문서 guide documentation backup restore",
            {
                "bm25": [etcd_hit, backup_hit],
                "vector": [backup_hit, etcd_hit],
            },
            top_k=2,
        )

        self.assertEqual("backup_and_restore", hits[0].book_slug)

    def test_retrieve_expands_candidate_pool_for_compare_query(self) -> None:
        settings = Settings(root_dir=ROOT)
        bm25 = SeededBm25(record_calls=True)
        retriever = ChatRetriever(settings, bm25, vector_retriever=None)

        result = retriever.retrieve(
            "오픈시프트와 쿠버네티스 차이를 세 줄로 설명해줘",
            use_vector=False,
        )

        self.assertEqual(3, len(bm25.calls))
        self.assertTrue(all(top_k == 40 for _, top_k in bm25.calls))
        self.assertEqual(
            [
                "오픈시프트와 쿠버네티스 차이를 세 줄로 설명해줘",
                "오픈시프트 개요",
                "쿠버네티스 개요",
            ],
            result.trace["decomposed_queries"],
        )
        self.assertEqual(40, result.trace["effective_candidate_k"])

    def test_fusion_prefers_authz_books_over_api_books_for_project_rbac_assignment(self) -> None:
        auth_hit = RetrievalHit(
            chunk_id="auth-hit",
            book_slug="authentication_and_authorization",
            chapter="rbac",
            section="9.1.1. 기본 클러스터 역할",
            anchor="default-roles",
            source_url="https://example.com/auth",
            viewer_path="/docs/auth.html#default-roles",
            text="RBAC에서는 로컬 바인딩으로 프로젝트에 admin 역할을 연결할 수 있습니다.",
            source="vector",
            raw_score=0.61,
            fused_score=0.61,
        )
        tutorial_hit = RetrievalHit(
            chunk_id="tutorial-hit",
            book_slug="tutorials",
            chapter="tutorials",
            section="3.3. 보기 권한 부여",
            anchor="grant-view",
            source_url="https://example.com/tutorials",
            viewer_path="/docs/tutorials.html#grant-view",
            text="oc adm policy add-role-to-user view -z default -n user-getting-started",
            source="bm25",
            raw_score=0.60,
            fused_score=0.60,
        )
        api_hit = RetrievalHit(
            chunk_id="api-hit",
            book_slug="role_apis",
            chapter="apis",
            section="RoleBinding API 끝점",
            anchor="rolebinding-api",
            source_url="https://example.com/apis",
            viewer_path="/docs/apis.html#rolebinding-api",
            text="RoleBinding API 끝점과 POST /namespaces/{namespace}/rolebindings 설명",
            source="bm25",
            raw_score=0.66,
            fused_score=0.66,
        )

        hits = fuse_ranked_hits(
            "프로젝트 namespace admin 권한 부여 RBAC 설정 방법 rolebinding add-role-to-user",
            {
                "bm25": [api_hit, tutorial_hit, auth_hit],
                "vector": [auth_hit, tutorial_hit],
            },
            top_k=3,
        )

        self.assertEqual("authentication_and_authorization", hits[0].book_slug)
        self.assertNotEqual("role_apis", hits[0].book_slug)

    def test_fusion_keeps_compare_docs_for_openshift_kubernetes_difference_query(self) -> None:
        security_hit = RetrievalHit(
            chunk_id="security-compare",
            book_slug="security_and_compliance",
            chapter="security",
            section="2.1.2. OpenShift Container Platform의 정의",
            anchor="platform-definition",
            source_url="https://example.com/security",
            viewer_path="/docs/security.html#platform-definition",
            text="쿠버네티스 플랫폼마다 보안이 다를 수 있습니다. OpenShift Container Platform은 쿠버네티스 보안을 잠그고 운영 기능을 제공합니다.",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        compare_hit = RetrievalHit(
            chunk_id="overview-compare",
            book_slug="overview",
            chapter="overview",
            section="7.1. 유사점 및 차이점",
            anchor="similarities-and-differences",
            source_url="https://example.com/overview",
            viewer_path="/docs/overview.html#similarities-and-differences",
            text="유사점 및 차이점 비교 표입니다.",
            source="vector",
            raw_score=0.82,
            fused_score=0.82,
        )

        hits = fuse_ranked_hits(
            "오픈시프트와 쿠버네티스 차이를 세 줄로 설명해줘 OpenShift Kubernetes comparison difference",
            {"bm25": [security_hit], "vector": [compare_hit, security_hit]},
            top_k=2,
        )

        self.assertIn(hits[0].book_slug, {"security_and_compliance", "overview"})

    def test_fusion_prefers_cluster_backup_wrapper_for_etcd_procedure(self) -> None:
        generic_hit = RetrievalHit(
            chunk_id="etcd-generic",
            book_slug="postinstallation_configuration",
            chapter="etcd",
            section="4.12.5. etcd 데이터 백업",
            anchor="backing-up-etcd-data",
            source_url="https://example.com/postinstall",
            viewer_path="/docs/postinstall.html#backing-up-etcd-data",
            text="found latest kube-apiserver ... etcdctl version: 3.4.14 ... snapshot stream downloading",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        procedure_hit = RetrievalHit(
            chunk_id="etcd-procedure",
            book_slug="postinstallation_configuration",
            chapter="etcd",
            section="4.12.5. etcd 데이터 백업",
            anchor="backing-up-etcd-data",
            source_url="https://example.com/postinstall",
            viewer_path="/docs/postinstall.html#backing-up-etcd-data",
            text="cluster-backup.sh 스크립트를 실행합니다. [CODE] /usr/local/bin/cluster-backup.sh /home/core/assets/backup [/CODE]",
            source="vector",
            raw_score=0.98,
            fused_score=0.98,
        )

        hits = fuse_ranked_hits(
            "etcd 백업은 실제로 어떤 절차로 해?",
            {"bm25": [generic_hit], "vector": [procedure_hit]},
            top_k=2,
        )

        self.assertEqual("etcd-procedure", hits[0].chunk_id)

    def test_build_retrieval_trace_exposes_ablation_stage_signals(self) -> None:
        bm25_hits = [
            RetrievalHit(
                chunk_id="bm25-top",
                book_slug="backup_and_restore",
                chapter="backup",
                section="etcd 백업과 복구",
                anchor="backup",
                source_url="https://example.com/backup",
                viewer_path="/docs/backup.html#backup",
                text="etcd 백업 절차",
                source="bm25",
                raw_score=0.91,
                fused_score=0.91,
                component_scores={"bm25_score": 0.91, "bm25_rank": 1.0},
            ),
            RetrievalHit(
                chunk_id="bm25-secondary",
                book_slug="etcd",
                chapter="etcd",
                section="etcd 재해 복구",
                anchor="etcd-dr",
                source_url="https://example.com/etcd",
                viewer_path="/docs/etcd.html#etcd-dr",
                text="etcd 재해 복구",
                source="bm25",
                raw_score=0.84,
                fused_score=0.84,
                component_scores={"bm25_score": 0.84, "bm25_rank": 2.0},
            ),
        ]
        vector_hits = [
            RetrievalHit(
                chunk_id="vector-top",
                book_slug="backup_and_restore",
                chapter="backup",
                section="etcd 백업과 복구",
                anchor="backup",
                source_url="https://example.com/backup",
                viewer_path="/docs/backup.html#backup",
                text="etcd 백업 절차",
                source="vector",
                raw_score=0.89,
                fused_score=0.89,
                component_scores={"vector_score": 0.89, "vector_rank": 1.0},
            ),
            RetrievalHit(
                chunk_id="vector-secondary",
                book_slug="etcd",
                chapter="etcd",
                section="etcd 재해 복구",
                anchor="etcd-dr",
                source_url="https://example.com/etcd",
                viewer_path="/docs/etcd.html#etcd-dr",
                text="etcd 재해 복구",
                source="vector",
                raw_score=0.8,
                fused_score=0.8,
                component_scores={"vector_score": 0.8, "vector_rank": 2.0},
            ),
        ]
        hybrid_hits = [
            RetrievalHit(
                chunk_id="hybrid-top",
                book_slug="backup_and_restore",
                chapter="backup",
                section="etcd 백업과 복구",
                anchor="backup",
                source_url="https://example.com/backup",
                viewer_path="/docs/backup.html#backup",
                text="etcd 백업 절차",
                source="hybrid",
                raw_score=0.95,
                fused_score=0.95,
                component_scores={
                    "bm25_score": 0.91,
                    "bm25_rank": 1.0,
                    "vector_score": 0.89,
                    "vector_rank": 1.0,
                },
            ),
            RetrievalHit(
                chunk_id="hybrid-secondary",
                book_slug="etcd",
                chapter="etcd",
                section="etcd 재해 복구",
                anchor="etcd-dr",
                source_url="https://example.com/etcd",
                viewer_path="/docs/etcd.html#etcd-dr",
                text="etcd 재해 복구",
                source="hybrid",
                raw_score=0.82,
                fused_score=0.82,
                component_scores={
                    "bm25_score": 0.84,
                    "bm25_rank": 2.0,
                    "vector_score": 0.8,
                    "vector_rank": 2.0,
                },
            ),
        ]
        reranked_hits = [
            RetrievalHit(
                chunk_id="reranked-top",
                book_slug="support",
                chapter="support",
                section="백업과 복구 참고",
                anchor="support",
                source_url="https://example.com/support",
                viewer_path="/docs/support.html#support",
                text="운영 지원 문서",
                source="hybrid_reranked",
                raw_score=1.5,
                fused_score=1.5,
                component_scores={
                    "bm25_score": 0.91,
                    "vector_score": 0.89,
                    "pre_rerank_fused_score": 0.95,
                    "reranker_score": 1.5,
                },
            ),
            RetrievalHit(
                chunk_id="reranked-second",
                book_slug="backup_and_restore",
                chapter="backup",
                section="etcd 백업과 복구",
                anchor="backup",
                source_url="https://example.com/backup",
                viewer_path="/docs/backup.html#backup",
                text="etcd 백업 절차",
                source="hybrid_reranked",
                raw_score=1.2,
                fused_score=1.2,
                component_scores={
                    "pre_rerank_fused_score": 0.91,
                    "reranker_score": 1.2,
                },
            ),
        ]

        trace = build_retrieval_trace(
            warnings=[],
            bm25_hits=bm25_hits,
            vector_hits=vector_hits,
            hybrid_hits=hybrid_hits,
            graph_trace={},
            reranked_hits=reranked_hits,
            reranker_trace={
                "enabled": True,
                "applied": True,
                "model": "fake-reranker",
                "top_n": 8,
                "top1_changed": True,
                "top1_before": "backup_and_restore",
                "top1_after": "support",
                "rebalance_reasons": ["support rescue"],
            },
            decomposed_queries=["etcd 백업은 어떻게 해?"],
            effective_candidate_k=20,
            fusion_output_k=2,
            timings_ms={
                "bm25_search": 1.0,
                "vector_search": 2.0,
                "fusion": 3.0,
                "rerank": 4.0,
                "total": 10.0,
            },
            candidate_k=20,
            top_k=2,
        )

        self.assertIn("ablation", trace)
        ablation = trace["ablation"]
        self.assertEqual("backup_and_restore", ablation["bm25_top_book_slugs"][0])
        self.assertEqual("backup_and_restore", ablation["vector_top_book_slugs"][0])
        self.assertEqual("backup_and_restore", ablation["hybrid_top_book_slugs"][0])
        self.assertEqual("support", ablation["reranked_top_book_slugs"][0])
        self.assertEqual("both", ablation["hybrid_top_support"])
        self.assertEqual("both", ablation["reranked_top_support"])
        self.assertTrue(ablation["rerank_top1_changed"])
        self.assertEqual("backup_and_restore", ablation["rerank_top1_from"])
        self.assertEqual("support", ablation["rerank_top1_to"])
        self.assertEqual(["support rescue"], ablation["rerank_reasons"])

    def test_fusion_prefers_monitor_certificates_command_for_certificate_expiry_query(self) -> None:
        concept_hit = RetrievalHit(
            chunk_id="cert-concept",
            book_slug="security_and_compliance",
            chapter="security",
            section="4.3.2. 만료",
            anchor="expiry",
            source_url="https://example.com/security",
            viewer_path="/docs/security.html#expiry",
            text="서비스 CA 인증서는 26개월 동안 유효하며 순환됩니다.",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        command_hit = RetrievalHit(
            chunk_id="cert-command",
            book_slug="cli_tools",
            chapter="cli",
            section="2.7.1.25. oc adm ocp-certificates monitor-certificates",
            anchor="oc-adm-ocp-certificates-monitor-certificates",
            source_url="https://example.com/cli",
            viewer_path="/docs/cli.html#oc-adm-ocp-certificates-monitor-certificates",
            text="플랫폼 인증서 감시 [CODE] oc adm ocp-certificates monitor-certificates [/CODE]",
            source="vector",
            raw_score=0.97,
            fused_score=0.97,
        )

        hits = fuse_ranked_hits(
            "ocp api 서버 인증서 만료 임박했는지 어떻게 확인해?",
            {"bm25": [concept_hit], "vector": [command_hit]},
            top_k=2,
        )

        self.assertEqual("cert-command", hits[0].chunk_id)

    def test_fusion_prefers_pod_issue_section_over_installation_etcd_for_pending_question(self) -> None:
        installation_hit = RetrievalHit(
            chunk_id="support-install-etcd",
            book_slug="support",
            chapter="support",
            section="7.1.9. etcd 설치 문제 조사",
            anchor="investigating-etcd-installation-issues",
            source_url="https://example.com/support",
            viewer_path="/docs/support.html#investigating-etcd-installation-issues",
            text="지원 7장. 문제 해결 > 7.1. 설치 문제 해결 > 7.1.9. etcd 설치 문제 조사 Pod의 이벤트를 검토합니다. oc describe pod/<pod_name> -n <namespace>",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        pod_issue_hit = RetrievalHit(
            chunk_id="support-pod-issues",
            book_slug="support",
            chapter="support",
            section="7.7.1. Pod 오류 상태 이해",
            anchor="understanding-pod-error-states",
            source_url="https://example.com/support",
            viewer_path="/docs/support.html#understanding-pod-error-states",
            text="지원 7장. 문제 해결 > 7.7. Pod 문제 조사 > 7.7.1. Pod 오류 상태 이해 FailedScheduling Pending node affinity taint toleration",
            source="vector",
            raw_score=0.97,
            fused_score=0.97,
        )

        hits = fuse_ranked_hits(
            "Pod가 Pending 상태로 오래 멈춰 있을 때 어디부터 확인해야 해? Pending FailedScheduling pod issues error states node affinity taint toleration",
            {"bm25": [installation_hit], "vector": [pod_issue_hit]},
            top_k=2,
        )

        self.assertEqual("support-pod-issues", hits[0].chunk_id)

    def test_retriever_short_circuits_unsupported_external_query(self) -> None:
        settings = Settings(ROOT)
        retriever = ChatRetriever(settings, BM25Index.from_rows([]), vector_retriever=None)

        result = retriever.retrieve("Harbor 설치 방법 알려줘", use_bm25=False, use_vector=False)

        self.assertEqual([], result.hits)
        self.assertTrue(
            any("outside OCP corpus" in warning for warning in result.trace["warnings"])
        )


if __name__ == "__main__":
    unittest.main()
