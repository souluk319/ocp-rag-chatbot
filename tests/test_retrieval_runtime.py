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

from _support_retrieval import BM25Index, ChatRetriever, RetrievalHit, SessionContext, Settings, fuse_ranked_hits
from play_book_studio.retrieval.retriever_rerank import maybe_rerank_hits

class TestRetrievalRuntime(unittest.TestCase):
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
        class StubBm25:
            def __init__(self) -> None:
                self.calls: list[tuple[str, int]] = []

            def search(self, query: str, top_k: int):
                self.calls.append((query, top_k))
                return []

        settings = Settings(root_dir=ROOT)
        bm25 = StubBm25()
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

    def test_reranker_rebalances_cluster_node_usage_back_to_support_family(self) -> None:
        class _FakeReranker:
            def __init__(self, hits: list[RetrievalHit]) -> None:
                self.hits = hits
                self.model_name = "fake-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int) -> list[RetrievalHit]:
                return list(self.hits)

        class _FakeRetrieverWithReranker:
            def __init__(self, hits: list[RetrievalHit]) -> None:
                self.reranker = _FakeReranker(hits)

        hybrid_hits = [
            RetrievalHit(
                chunk_id="support-hit",
                book_slug="support",
                chapter="support",
                section="7.2.1. 노드 상태, 리소스 사용량 및 구성 확인",
                anchor="checking-node-resource-usage",
                source_url="https://example.com/support",
                viewer_path="/docs/support.html#checking-node-resource-usage",
                text="oc adm top nodes",
                source="hybrid",
                raw_score=0.90,
                fused_score=0.90,
            ),
            RetrievalHit(
                chunk_id="nodes-hit",
                book_slug="nodes",
                chapter="nodes",
                section="6.1.3. 노드의 메모리 및 CPU 사용량 통계 보기",
                anchor="node-resource-usage",
                source_url="https://example.com/nodes",
                viewer_path="/docs/nodes.html#node-resource-usage",
                text="oc adm top nodes",
                source="hybrid",
                raw_score=0.70,
                fused_score=0.70,
            ),
        ]
        reranked_hits = [
            RetrievalHit(
                chunk_id="nodes-hit",
                book_slug="nodes",
                chapter="nodes",
                section="6.1.3. 노드의 메모리 및 CPU 사용량 통계 보기",
                anchor="node-resource-usage",
                source_url="https://example.com/nodes",
                viewer_path="/docs/nodes.html#node-resource-usage",
                text="oc adm top nodes",
                source="hybrid_reranked",
                raw_score=6.7,
                fused_score=6.7,
                component_scores={"pre_rerank_fused_score": 0.70, "reranker_score": 6.7},
            ),
            RetrievalHit(
                chunk_id="support-hit",
                book_slug="support",
                chapter="support",
                section="7.2.1. 노드 상태, 리소스 사용량 및 구성 확인",
                anchor="checking-node-resource-usage",
                source_url="https://example.com/support",
                viewer_path="/docs/support.html#checking-node-resource-usage",
                text="oc adm top nodes",
                source="hybrid_reranked",
                raw_score=3.0,
                fused_score=3.0,
                component_scores={"pre_rerank_fused_score": 0.90, "reranker_score": 3.0},
            ),
        ]

        hits, trace = maybe_rerank_hits(
            _FakeRetrieverWithReranker(reranked_hits),
            query="지금 클러스터 전체 노드 CPU랑 메모리 사용량 한 번에 보려면 어떤 명령 써?",
            hybrid_hits=hybrid_hits,
            top_k=2,
            trace_callback=None,
            timings_ms={},
        )

        self.assertTrue(trace["applied"])
        self.assertEqual("support", hits[0].book_slug)

    def test_reranker_rebalances_etcd_backup_hits_toward_backup_procedure(self) -> None:
        class _FakeReranker:
            def __init__(self, hits: list[RetrievalHit]) -> None:
                self.hits = hits
                self.model_name = "fake-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int) -> list[RetrievalHit]:
                return list(self.hits)

        class _FakeRetrieverWithReranker:
            def __init__(self, hits: list[RetrievalHit]) -> None:
                self.reranker = _FakeReranker(hits)

        hybrid_hits = [
            RetrievalHit(
                chunk_id="etcd-restore",
                book_slug="etcd",
                chapter="etcd",
                section="4.3.2.4. etcd 백업에서 수동으로 클러스터 복원",
                anchor="restore",
                source_url="https://example.com/etcd",
                viewer_path="/docs/etcd.html#restore",
                text="cluster-restore.sh",
                source="hybrid",
                raw_score=0.90,
                fused_score=0.90,
            ),
            RetrievalHit(
                chunk_id="postinstall-backup",
                book_slug="postinstallation_configuration",
                chapter="postinstall",
                section="4.12.5. etcd 데이터 백업",
                anchor="backup",
                source_url="https://example.com/postinstall",
                viewer_path="/docs/postinstall.html#backup",
                text="oc debug --as-root node\nchroot /host\n/usr/local/bin/cluster-backup.sh /home/core/assets/backup",
                source="hybrid",
                raw_score=0.82,
                fused_score=0.82,
            ),
        ]
        reranked_hits = [
            RetrievalHit(
                chunk_id="etcd-restore",
                book_slug="etcd",
                chapter="etcd",
                section="4.3.2.4. etcd 백업에서 수동으로 클러스터 복원",
                anchor="restore",
                source_url="https://example.com/etcd",
                viewer_path="/docs/etcd.html#restore",
                text="cluster-restore.sh",
                source="hybrid_reranked",
                raw_score=4.5,
                fused_score=4.5,
                component_scores={"pre_rerank_fused_score": 0.90, "reranker_score": 4.5},
            ),
            RetrievalHit(
                chunk_id="postinstall-backup",
                book_slug="postinstallation_configuration",
                chapter="postinstall",
                section="4.12.5. etcd 데이터 백업",
                anchor="backup",
                source_url="https://example.com/postinstall",
                viewer_path="/docs/postinstall.html#backup",
                text="oc debug --as-root node\nchroot /host\n/usr/local/bin/cluster-backup.sh /home/core/assets/backup",
                source="hybrid_reranked",
                raw_score=2.2,
                fused_score=2.2,
                component_scores={"pre_rerank_fused_score": 0.82, "reranker_score": 2.2},
            ),
        ]

        hits, trace = maybe_rerank_hits(
            _FakeRetrieverWithReranker(reranked_hits),
            query="etcd 백업은 실제로 어떤 절차로 해? 표준적인 방법만 짧게 알려줘",
            hybrid_hits=hybrid_hits,
            top_k=2,
            trace_callback=None,
            timings_ms={},
        )

        self.assertTrue(trace["applied"])
        self.assertEqual("postinstallation_configuration", hits[0].book_slug)

    def test_reranker_rescues_uploaded_customer_pack_for_explicit_customer_doc_query(self) -> None:
        class _FakeReranker:
            def __init__(self, hits: list[RetrievalHit]) -> None:
                self.hits = hits
                self.model_name = "fake-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int) -> list[RetrievalHit]:
                return list(self.hits)

        class _FakeRetrieverWithReranker:
            def __init__(self, hits: list[RetrievalHit]) -> None:
                self.reranker = _FakeReranker(hits)

        hybrid_hits = [
            RetrievalHit(
                chunk_id="uploaded-backup",
                book_slug="customer-backup-runbook",
                chapter="Customer Backup Runbook",
                section="OpenShift Backup Restore Runbook",
                anchor="uploaded-backup",
                source_url="/tmp/customer.pdf",
                viewer_path="/playbooks/customer-packs/dtb-demo/index.html#uploaded-backup",
                text="/usr/local/bin/cluster-backup.sh /home/core/assets/backup",
                source="hybrid",
                raw_score=0.87,
                fused_score=0.87,
                source_collection="uploaded",
            ),
            RetrievalHit(
                chunk_id="core-backup",
                book_slug="postinstallation_configuration",
                chapter="postinstall",
                section="4.12.5. etcd 데이터 백업",
                anchor="backup",
                source_url="https://example.com/postinstall",
                viewer_path="/docs/postinstall.html#backup",
                text="oc debug --as-root node\nchroot /host\n/usr/local/bin/cluster-backup.sh /home/core/assets/backup",
                source="hybrid",
                raw_score=0.92,
                fused_score=0.92,
            ),
        ]
        reranked_hits = [
            RetrievalHit(
                chunk_id="core-backup",
                book_slug="postinstallation_configuration",
                chapter="postinstall",
                section="4.12.5. etcd 데이터 백업",
                anchor="backup",
                source_url="https://example.com/postinstall",
                viewer_path="/docs/postinstall.html#backup",
                text="oc debug --as-root node\nchroot /host\n/usr/local/bin/cluster-backup.sh /home/core/assets/backup",
                source="hybrid_reranked",
                raw_score=4.8,
                fused_score=4.8,
                component_scores={"pre_rerank_fused_score": 0.92, "reranker_score": 4.8},
            ),
        ]

        hits, trace = maybe_rerank_hits(
            _FakeRetrieverWithReranker(reranked_hits),
            query="업로드 문서 기준으로 backup 절차를 알려줘",
            hybrid_hits=hybrid_hits,
            top_k=2,
            trace_callback=None,
            timings_ms={},
        )

        self.assertTrue(trace["applied"])
        self.assertEqual("customer-backup-runbook", hits[0].book_slug)
        self.assertEqual("uploaded", hits[0].source_collection)

    def test_reranker_keeps_etcd_backup_companion_when_rerank_returns_only_postinstall_hits(self) -> None:
        class _FakeReranker:
            def __init__(self, hits: list[RetrievalHit]) -> None:
                self.hits = hits
                self.model_name = "fake-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int) -> list[RetrievalHit]:
                return list(self.hits)

        class _FakeRetrieverWithReranker:
            def __init__(self, hits: list[RetrievalHit]) -> None:
                self.reranker = _FakeReranker(hits)

        hybrid_hits = [
            RetrievalHit(
                chunk_id="postinstall-backup",
                book_slug="postinstallation_configuration",
                chapter="postinstall",
                section="4.12.5. etcd 데이터 백업",
                anchor="backup",
                source_url="https://example.com/postinstall",
                viewer_path="/docs/postinstall.html#backup",
                text="oc debug --as-root node\nchroot /host\n/usr/local/bin/cluster-backup.sh /home/core/assets/backup",
                source="hybrid",
                raw_score=0.92,
                fused_score=0.92,
            ),
            RetrievalHit(
                chunk_id="etcd-backup",
                book_slug="etcd",
                chapter="etcd",
                section="4.1.1. etcd 데이터 백업",
                anchor="etcd-backup",
                source_url="https://example.com/etcd",
                viewer_path="/docs/etcd.html#etcd-backup",
                text="etcd 백업 절차와 보존 위치를 설명합니다.",
                source="hybrid",
                raw_score=0.81,
                fused_score=0.81,
            ),
            RetrievalHit(
                chunk_id="backup-doc-backup",
                book_slug="backup_and_restore",
                chapter="backup",
                section="6.1.1. Backing up etcd data",
                anchor="backup-and-restore-etcd",
                source_url="https://example.com/backup",
                viewer_path="/docs/backup.html#backup-and-restore-etcd",
                text="etcd 전용 백업/복원 문서입니다.",
                source="hybrid",
                raw_score=0.78,
                fused_score=0.78,
            ),
        ]
        reranked_hits = [
            RetrievalHit(
                chunk_id="postinstall-backup",
                book_slug="postinstallation_configuration",
                chapter="postinstall",
                section="4.12.5. etcd 데이터 백업",
                anchor="backup",
                source_url="https://example.com/postinstall",
                viewer_path="/docs/postinstall.html#backup",
                text="oc debug --as-root node\nchroot /host\n/usr/local/bin/cluster-backup.sh /home/core/assets/backup",
                source="hybrid_reranked",
                raw_score=4.3,
                fused_score=4.3,
                component_scores={"pre_rerank_fused_score": 0.92, "reranker_score": 4.3},
            ),
            RetrievalHit(
                chunk_id="postinstall-restore",
                book_slug="postinstallation_configuration",
                chapter="postinstall",
                section="4.12.7. 두 개 이상의 노드의 이전 클러스터 상태로 복원",
                anchor="restore",
                source_url="https://example.com/postinstall",
                viewer_path="/docs/postinstall.html#restore",
                text="cluster-restore.sh",
                source="hybrid_reranked",
                raw_score=4.1,
                fused_score=4.1,
                component_scores={"pre_rerank_fused_score": 0.88, "reranker_score": 4.1},
            ),
        ]

        hits, trace = maybe_rerank_hits(
            _FakeRetrieverWithReranker(reranked_hits),
            query="etcd 백업은 어떻게 해?",
            hybrid_hits=hybrid_hits,
            top_k=2,
            trace_callback=None,
            timings_ms={},
        )

        self.assertTrue(trace["applied"])
        self.assertEqual("postinstallation_configuration", hits[0].book_slug)
        self.assertIn(hits[1].book_slug, {"etcd", "backup_and_restore"})

    def test_reranker_replaces_restore_companion_with_backup_companion_for_etcd_backup_query(self) -> None:
        class _FakeReranker:
            def __init__(self, hits: list[RetrievalHit]) -> None:
                self.hits = hits
                self.model_name = "fake-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int) -> list[RetrievalHit]:
                return list(self.hits)

        class _FakeRetrieverWithReranker:
            def __init__(self, hits: list[RetrievalHit]) -> None:
                self.reranker = _FakeReranker(hits)

        hybrid_hits = [
            RetrievalHit(
                chunk_id="postinstall-backup",
                book_slug="postinstallation_configuration",
                chapter="postinstall",
                section="4.12.5. etcd 데이터 백업",
                anchor="backup",
                source_url="https://example.com/postinstall",
                viewer_path="/docs/postinstall.html#backup",
                text="cluster-backup.sh",
                source="hybrid",
                raw_score=0.92,
                fused_score=0.92,
            ),
            RetrievalHit(
                chunk_id="etcd-backup",
                book_slug="etcd",
                chapter="etcd",
                section="4.1.1. etcd 데이터 백업",
                anchor="etcd-backup",
                source_url="https://example.com/etcd",
                viewer_path="/docs/etcd.html#etcd-backup",
                text="cluster-backup.sh",
                source="hybrid",
                raw_score=0.81,
                fused_score=0.81,
            ),
            RetrievalHit(
                chunk_id="etcd-restore",
                book_slug="etcd",
                chapter="etcd",
                section="4.3.2.3. 두 개 이상의 노드의 이전 클러스터 상태로 복원",
                anchor="etcd-restore",
                source_url="https://example.com/etcd",
                viewer_path="/docs/etcd.html#etcd-restore",
                text="cluster-restore.sh",
                source="hybrid",
                raw_score=0.74,
                fused_score=0.74,
            ),
        ]
        reranked_hits = [
            RetrievalHit(
                chunk_id="postinstall-backup",
                book_slug="postinstallation_configuration",
                chapter="postinstall",
                section="4.12.5. etcd 데이터 백업",
                anchor="backup",
                source_url="https://example.com/postinstall",
                viewer_path="/docs/postinstall.html#backup",
                text="cluster-backup.sh",
                source="hybrid_reranked",
                raw_score=4.3,
                fused_score=4.3,
                component_scores={"pre_rerank_fused_score": 0.92, "reranker_score": 4.3},
            ),
            RetrievalHit(
                chunk_id="etcd-restore",
                book_slug="etcd",
                chapter="etcd",
                section="4.3.2.3. 두 개 이상의 노드의 이전 클러스터 상태로 복원",
                anchor="etcd-restore",
                source_url="https://example.com/etcd",
                viewer_path="/docs/etcd.html#etcd-restore",
                text="cluster-restore.sh",
                source="hybrid_reranked",
                raw_score=5.7,
                fused_score=5.7,
                component_scores={"pre_rerank_fused_score": 0.74, "reranker_score": 5.7},
            ),
        ]

        hits, trace = maybe_rerank_hits(
            _FakeRetrieverWithReranker(reranked_hits),
            query="etcd 백업은 어떻게 해?",
            hybrid_hits=hybrid_hits,
            top_k=2,
            trace_callback=None,
            timings_ms={},
        )

        self.assertTrue(trace["applied"])
        self.assertEqual("postinstallation_configuration", hits[0].book_slug)
        self.assertEqual("etcd", hits[1].book_slug)
        self.assertIn("데이터 백업", hits[1].section)

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

    def test_retriever_applies_reranker_to_hybrid_candidates(self) -> None:
        class StubBm25:
            def search(self, query: str, top_k: int):
                del query, top_k
                return [
                    RetrievalHit(
                        chunk_id="overview-hit",
                        book_slug="overview",
                        chapter="개요",
                        section="플랫폼 개요",
                        anchor="overview",
                        source_url="https://example.com/overview",
                        viewer_path="/docs/ocp/4.20/ko/overview/index.html#overview",
                        text="플랫폼 전체 개요 설명",
                        source="bm25",
                        raw_score=1.0,
                    ),
                    RetrievalHit(
                        chunk_id="nodes-hit",
                        book_slug="nodes",
                        chapter="노드",
                        section="Pod 이해",
                        anchor="pod-understanding",
                        source_url="https://example.com/nodes",
                        viewer_path="/docs/ocp/4.20/ko/nodes/index.html#pod-understanding",
                        text="Pod lifecycle과 phase를 설명합니다.",
                        source="bm25",
                        raw_score=0.9,
                    ),
                ]

        class StubReranker:
            def __init__(self) -> None:
                self.model_name = "stub-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int):
                del query, top_k
                reordered = list(hits)
                reordered.reverse()
                for index, hit in enumerate(reordered, start=1):
                    hit.component_scores["pre_rerank_fused_score"] = float(hit.fused_score)
                    hit.component_scores["reranker_score"] = float(10 - index)
                    hit.fused_score = float(10 - index)
                    hit.raw_score = float(10 - index)
                return reordered

        settings = Settings(ROOT)
        retriever = ChatRetriever(
            settings,
            StubBm25(),
            vector_retriever=None,
            reranker=StubReranker(),
        )

        result = retriever.retrieve(
            "Pod lifecycle 개념 설명",
            top_k=2,
            candidate_k=2,
            use_vector=False,
        )

        self.assertNotEqual(
            result.trace["hybrid"][0]["book_slug"],
            result.hits[0].book_slug,
        )
        self.assertTrue(result.trace["reranker"]["applied"])
        self.assertEqual("stub-reranker", result.trace["reranker"]["model"])
        self.assertEqual(result.hits[0].book_slug, result.trace["reranked"][0]["book_slug"])
        self.assertIn("reranked", result.trace["metrics"])

    def test_retriever_raises_when_configured_reranker_fails(self) -> None:
        class StubBm25:
            def search(self, query: str, top_k: int):
                del query, top_k
                return [
                    RetrievalHit(
                        chunk_id="overview-hit",
                        book_slug="overview",
                        chapter="개요",
                        section="플랫폼 개요",
                        anchor="overview",
                        source_url="https://example.com/overview",
                        viewer_path="/docs/ocp/4.20/ko/overview/index.html#overview",
                        text="플랫폼 전체 개요 설명",
                        source="bm25",
                        raw_score=1.0,
                    )
                ]

        class FailingReranker:
            def __init__(self) -> None:
                self.model_name = "failing-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int):
                del query, hits, top_k
                raise RuntimeError("reranker backend down")

        settings = Settings(ROOT)
        retriever = ChatRetriever(
            settings,
            StubBm25(),
            vector_retriever=None,
            reranker=FailingReranker(),
        )

        with self.assertRaisesRegex(RuntimeError, "reranker failed: reranker backend down"):
            retriever.retrieve(
                "Pod lifecycle 개념 설명",
                top_k=2,
                candidate_k=2,
                use_vector=False,
            )

    def test_retriever_rebalances_registry_follow_up_when_reranker_promotes_installation_overview(self) -> None:
        class StubBm25:
            def search(self, query: str, top_k: int):
                del query, top_k
                return [
                    RetrievalHit(
                        chunk_id="images-hit",
                        book_slug="images",
                        chapter="이미지",
                        section="이미지 레지스트리 저장소 미러링 설정",
                        anchor="image-mirror",
                        source_url="https://example.com/images",
                        viewer_path="/docs/ocp/4.20/ko/images/index.html#image-mirror",
                        text="이미지 레지스트리 저장소 미러링 설정 절차입니다.",
                        source="bm25",
                        raw_score=1.0,
                        fused_score=1.0,
                    ),
                    RetrievalHit(
                        chunk_id="registry-hit",
                        book_slug="registry",
                        chapter="레지스트리",
                        section="이미지 레지스트리 스토리지 구성",
                        anchor="registry-storage",
                        source_url="https://example.com/registry",
                        viewer_path="/docs/ocp/4.20/ko/registry/index.html#registry-storage",
                        text="이미지 레지스트리의 스토리지를 구성합니다.",
                        source="bm25",
                        raw_score=0.9,
                        fused_score=0.9,
                    ),
                    RetrievalHit(
                        chunk_id="installation-hit",
                        book_slug="installation_overview",
                        chapter="설치 개요",
                        section="클러스터 이미지 레지스트리 기능",
                        anchor="cluster-image-registry",
                        source_url="https://example.com/install",
                        viewer_path="/docs/ocp/4.20/ko/installation_overview/index.html#cluster-image-registry",
                        text="설치 개요에서 클러스터 이미지 레지스트리 기능을 설명합니다.",
                        source="bm25",
                        raw_score=0.8,
                        fused_score=0.8,
                    ),
                ]

        class StubReranker:
            def __init__(self) -> None:
                self.model_name = "stub-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int):
                del query, top_k
                promoted = list(hits)
                promoted.sort(
                    key=lambda hit: (
                        0 if hit.book_slug == "installation_overview" else 1,
                        hit.book_slug,
                    )
                )
                for index, hit in enumerate(promoted, start=1):
                    hit.component_scores["pre_rerank_fused_score"] = float(hit.fused_score)
                    hit.component_scores["reranker_score"] = float(10 - index)
                    hit.fused_score = float(10 - index)
                    hit.raw_score = float(10 - index)
                return promoted

        settings = Settings(ROOT)
        retriever = ChatRetriever(
            settings,
            StubBm25(),
            vector_retriever=None,
            reranker=StubReranker(),
        )

        result = retriever.retrieve(
            "아까 말한 이미지 저장소는?",
            context=SessionContext(
                mode="ops",
                current_topic="내부 이미지 레지스트리 구성",
                open_entities=["registry", "image registry"],
                ocp_version="4.20",
            ),
            top_k=3,
            candidate_k=3,
            use_vector=False,
        )

        self.assertEqual("images", result.trace["hybrid"][0]["book_slug"])
        self.assertEqual("images", result.hits[0].book_slug)
        self.assertEqual("images", result.trace["reranked"][0]["book_slug"])

    def test_retriever_rebalances_registry_storage_ops_query_when_reranker_promotes_install_book(self) -> None:
        class StubBm25:
            def search(self, query: str, top_k: int):
                del query, top_k
                return [
                    RetrievalHit(
                        chunk_id="registry-hit",
                        book_slug="registry",
                        chapter="레지스트리",
                        section="이미지 레지스트리 스토리지 구성",
                        anchor="registry-storage",
                        source_url="https://example.com/registry",
                        viewer_path="/docs/ocp/4.20/ko/registry/index.html#registry-storage",
                        text="이미지 레지스트리의 스토리지를 구성합니다.",
                        source="bm25",
                        raw_score=1.0,
                        fused_score=1.0,
                    ),
                    RetrievalHit(
                        chunk_id="images-hit",
                        book_slug="images",
                        chapter="이미지",
                        section="이미지 레지스트리 저장소 미러링 설정",
                        anchor="image-mirror",
                        source_url="https://example.com/images",
                        viewer_path="/docs/ocp/4.20/ko/images/index.html#image-mirror",
                        text="이미지 레지스트리 저장소 미러링 설정 절차입니다.",
                        source="bm25",
                        raw_score=0.9,
                        fused_score=0.9,
                    ),
                    RetrievalHit(
                        chunk_id="install-hit",
                        book_slug="installing_on_any_platform",
                        chapter="설치",
                        section="베어 메탈 및 기타 수동 설치에 대한 레지스트리 저장소 구성",
                        anchor="registry-storage-install",
                        source_url="https://example.com/install",
                        viewer_path="/docs/ocp/4.20/ko/installing_on_any_platform/index.html#registry-storage-install",
                        text="수동 설치 환경에서 이미지 레지스트리 저장소를 구성하는 절차입니다.",
                        source="bm25",
                        raw_score=0.8,
                        fused_score=0.8,
                    ),
                ]

        class StubReranker:
            def __init__(self) -> None:
                self.model_name = "stub-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int):
                del query, top_k
                promoted = list(hits)
                promoted.sort(
                    key=lambda hit: (
                        0 if hit.book_slug == "installing_on_any_platform" else 1,
                        hit.book_slug,
                    )
                )
                for index, hit in enumerate(promoted, start=1):
                    hit.component_scores["pre_rerank_fused_score"] = float(hit.fused_score)
                    hit.component_scores["reranker_score"] = float(10 - index)
                    hit.fused_score = float(10 - index)
                    hit.raw_score = float(10 - index)
                return promoted

        settings = Settings(ROOT)
        retriever = ChatRetriever(
            settings,
            StubBm25(),
            vector_retriever=None,
            reranker=StubReranker(),
        )

        result = retriever.retrieve(
            "이미지 레지스트리 저장소를 구성하려면?",
            top_k=3,
            candidate_k=3,
            use_vector=False,
        )

        self.assertEqual("registry", result.trace["hybrid"][0]["book_slug"])
        self.assertIn(result.hits[0].book_slug, {"registry", "images"})
        self.assertNotEqual("installing_on_any_platform", result.hits[0].book_slug)
        self.assertEqual(result.hits[0].book_slug, result.trace["reranked"][0]["book_slug"])

    def test_retriever_rebalances_mco_concept_when_reranker_promotes_update_glossary(self) -> None:
        class StubBm25:
            def search(self, query: str, top_k: int):
                del query, top_k
                return [
                    RetrievalHit(
                        chunk_id="overview-hit",
                        book_slug="overview",
                        chapter="개요",
                        section="OpenShift Container Platform의 일반 용어집",
                        anchor="overview-glossary",
                        source_url="https://example.com/overview",
                        viewer_path="/docs/ocp/4.20/ko/overview/index.html#overview-glossary",
                        text="일반 용어집에서 Machine Config Operator를 간단히 언급합니다.",
                        source="bm25",
                        raw_score=1.0,
                        fused_score=1.0,
                    ),
                    RetrievalHit(
                        chunk_id="machine-config-hit",
                        book_slug="machine_configuration",
                        chapter="머신 구성",
                        section="About the Machine Config Operator",
                        anchor="about-mco",
                        source_url="https://example.com/machine-configuration",
                        viewer_path="/docs/ocp/4.20/ko/machine_configuration/index.html#about-mco",
                        text="Machine Config Operator의 역할과 구성 요소를 설명합니다.",
                        source="bm25",
                        raw_score=0.95,
                        fused_score=0.95,
                    ),
                    RetrievalHit(
                        chunk_id="updating-glossary-hit",
                        book_slug="updating_clusters",
                        chapter="업데이트",
                        section="1.1.5. 일반 용어",
                        anchor="update-glossary",
                        source_url="https://example.com/updating",
                        viewer_path="/docs/ocp/4.20/ko/updating_clusters/index.html#update-glossary",
                        text="업데이트 일반 용어에서 Machine Config Operator를 간단히 정의합니다.",
                        source="bm25",
                        raw_score=0.9,
                        fused_score=0.9,
                    ),
                ]

        class StubReranker:
            def __init__(self) -> None:
                self.model_name = "stub-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int):
                del query, top_k
                promoted = list(hits)
                promoted.sort(
                    key=lambda hit: (
                        0 if hit.book_slug == "updating_clusters" else 1,
                        hit.book_slug,
                    )
                )
                for index, hit in enumerate(promoted, start=1):
                    hit.component_scores["pre_rerank_fused_score"] = float(hit.fused_score)
                    hit.component_scores["reranker_score"] = float(10 - index)
                    hit.fused_score = float(10 - index)
                    hit.raw_score = float(10 - index)
                return promoted

        settings = Settings(ROOT)
        retriever = ChatRetriever(
            settings,
            StubBm25(),
            vector_retriever=None,
            reranker=StubReranker(),
        )

        result = retriever.retrieve(
            "Machine Config Operator는 뭐야?",
            context=SessionContext(),
            top_k=3,
            candidate_k=3,
            use_vector=False,
        )

        self.assertEqual("machine_configuration", result.trace["hybrid"][0]["book_slug"])
        self.assertEqual("machine_configuration", result.hits[0].book_slug)
        self.assertEqual("machine_configuration", result.trace["reranked"][0]["book_slug"])


class TestRetrievalGraphRuntime(unittest.TestCase):
    def _write_playbook_documents(self, settings: Settings, *rows: dict) -> None:
        settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
        settings.playbook_documents_path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )

    def _write_graph_sidecar(self, settings: Settings, books: list[dict]) -> None:
        settings.graph_sidecar_path.parent.mkdir(parents=True, exist_ok=True)
        settings.graph_sidecar_path.write_text(
            json.dumps({"books": books}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _make_hit(
        self,
        *,
        chunk_id: str,
        book_slug: str,
        source_collection: str = "core",
        source_lane: str = "official_ko",
        source_type: str = "official_doc",
    ) -> RetrievalHit:
        return RetrievalHit(
            chunk_id=chunk_id,
            book_slug=book_slug,
            chapter="chapter",
            section=f"{book_slug} section",
            anchor=f"{chunk_id}-anchor",
            source_url=f"https://example.com/{book_slug}",
            viewer_path=f"/docs/{book_slug}.html#{chunk_id}-anchor",
            text=f"{book_slug} text",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
            source_collection=source_collection,
            source_lane=source_lane,
            source_type=source_type,
            section_path=("운영", book_slug),
            block_kinds=("paragraph",),
            semantic_role="procedure",
        )

    def _retriever(self, settings: Settings, hits: list[RetrievalHit]) -> ChatRetriever:
        class StubBm25:
            def __init__(self, seeded_hits: list[RetrievalHit]) -> None:
                self.seeded_hits = seeded_hits

            def search(self, query: str, top_k: int):
                del query
                return list(self.seeded_hits[:top_k])

        return ChatRetriever(settings, StubBm25(hits), vector_retriever=None)

    def test_retrieve_attaches_graph_trace_with_local_sidecar_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            self._write_playbook_documents(
                settings,
                {
                    "book_slug": "backup_and_restore",
                    "title": "Backup",
                    "translation_status": "approved_ko",
                    "review_status": "approved",
                    "source_metadata": {"source_type": "official_doc", "source_lane": "official_ko"},
                },
            )
            retriever = self._retriever(
                settings,
                [self._make_hit(chunk_id="hit-a", book_slug="backup_and_restore")],
            )

            result = retriever.retrieve("백업 절차", top_k=1, candidate_k=1, use_vector=False)

            self.assertTrue(result.trace["graph"]["graph_enabled"])
            self.assertEqual("local_sidecar", result.trace["graph"]["adapter_mode"])
            self.assertEqual(1, result.trace["graph"]["summary"]["hit_count"])
            self.assertEqual(1, result.trace["graph"]["summary"]["provenance_count"])

    def test_retrieve_graph_trace_reads_metadata_from_graph_sidecar_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            self._write_graph_sidecar(
                settings,
                [
                    {
                        "book_slug": "backup_restore_control_plane",
                        "title": "컨트롤 플레인 백업/복구 플레이북",
                        "source_type": "topic_playbook",
                        "source_lane": "applied_playbook",
                        "source_collection": "customer_pack",
                        "derived_from_book_slug": "backup_and_restore",
                        "topic_key": "backup_restore_control_plane",
                    }
                ],
            )
            retriever = self._retriever(
                settings,
                [
                    self._make_hit(
                        chunk_id="topic-hit",
                        book_slug="backup_restore_control_plane",
                        source_collection="customer_pack",
                    )
                ],
            )

            result = retriever.retrieve("컨트롤 플레인 백업", top_k=1, candidate_k=1, use_vector=False)
            provenance = result.trace["graph"]["hits"][0]["provenance"]

            self.assertEqual("topic_playbook", provenance["source_type"])
            self.assertEqual("applied_playbook", provenance["source_lane"])
            self.assertEqual("backup_and_restore", provenance["derived_from_book_slug"])
            self.assertEqual("backup_restore_control_plane", provenance["topic_key"])

    def test_retrieve_graph_trace_falls_back_to_playbook_documents_when_sidecar_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            self._write_playbook_documents(
                settings,
                {
                    "book_slug": "monitoring_stack_operations",
                    "title": "모니터링 스택 운영 플레이북",
                    "translation_status": "approved_ko",
                    "review_status": "approved",
                    "source_metadata": {
                        "source_type": "operation_playbook",
                        "source_lane": "applied_playbook",
                        "source_collection": "customer_pack",
                        "derived_from_book_slug": "monitoring",
                        "topic_key": "monitoring_stack_operations",
                    },
                },
            )
            retriever = self._retriever(
                settings,
                [
                    self._make_hit(
                        chunk_id="monitoring-hit",
                        book_slug="monitoring_stack_operations",
                        source_collection="customer_pack",
                    )
                ],
            )

            result = retriever.retrieve("모니터링 운영", top_k=1, candidate_k=1, use_vector=False)
            provenance = result.trace["graph"]["hits"][0]["provenance"]

            self.assertEqual("operation_playbook", provenance["source_type"])
            self.assertEqual("monitoring", provenance["derived_from_book_slug"])

    def test_retrieve_graph_trace_records_same_book_relations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            retriever = self._retriever(
                settings,
                [
                    self._make_hit(chunk_id="same-a", book_slug="backup_and_restore"),
                    self._make_hit(chunk_id="same-b", book_slug="backup_and_restore"),
                ],
            )

            result = retriever.retrieve("백업 문서", top_k=2, candidate_k=2, use_vector=False)
            relations = result.trace["graph"]["hits"][0]["relations"]

            self.assertTrue(any(item["type"] == "same_book" for item in relations))
            self.assertEqual(2, result.trace["graph"]["summary"]["relation_count"])

    def test_retrieve_graph_trace_records_shared_collection_relations_for_adjacent_books(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            retriever = self._retriever(
                settings,
                [
                    self._make_hit(chunk_id="shared-a", book_slug="backup_and_restore", source_collection="customer_pack"),
                    self._make_hit(chunk_id="shared-b", book_slug="monitoring", source_collection="customer_pack"),
                ],
            )

            result = retriever.retrieve("고객 팩 운영", top_k=2, candidate_k=2, use_vector=False)
            relations = result.trace["graph"]["hits"][0]["relations"]

            self.assertTrue(any(item["type"] == "shared_collection" for item in relations))
            self.assertEqual("customer_pack", relations[0]["source_collection"])

    def test_retrieve_graph_trace_records_derived_from_relations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            self._write_graph_sidecar(
                settings,
                [
                    {
                        "book_slug": "etcd_backup_restore",
                        "title": "etcd 백업/복구 플레이북",
                        "source_type": "topic_playbook",
                        "source_lane": "applied_playbook",
                        "source_collection": "customer_pack",
                        "derived_from_book_slug": "etcd",
                        "topic_key": "etcd_backup_restore",
                    }
                ],
            )
            retriever = self._retriever(
                settings,
                [self._make_hit(chunk_id="etcd-topic", book_slug="etcd_backup_restore", source_collection="customer_pack")],
            )

            result = retriever.retrieve("etcd 백업 복구", top_k=1, candidate_k=1, use_vector=False)
            relations = result.trace["graph"]["hits"][0]["relations"]

            self.assertTrue(any(item["type"] == "derived_from_book" for item in relations))
            self.assertEqual(1.0, result.hits[0].component_scores["graph_has_derivation"])

    def test_retrieve_graph_component_scores_preserve_fusion_scores(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            retriever = self._retriever(
                settings,
                [self._make_hit(chunk_id="score-hit", book_slug="backup_and_restore")],
            )

            result = retriever.retrieve("백업", top_k=1, candidate_k=1, use_vector=False)
            scores = result.hits[0].component_scores

            self.assertIn("bm25_score", scores)
            self.assertIn("bm25_rank", scores)
            self.assertIn("graph_relation_count", scores)
            self.assertIn("graph_provenance_count", scores)

    def test_retrieve_graph_component_scores_are_serialized_in_result_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            retriever = self._retriever(
                settings,
                [self._make_hit(chunk_id="serialize-hit", book_slug="backup_and_restore")],
            )

            payload = retriever.retrieve("백업", top_k=1, candidate_k=1, use_vector=False).to_dict()
            scores = payload["hits"][0]["component_scores"]

            self.assertIn("graph_relation_count", scores)
            self.assertIn("graph_provenance_count", scores)

    def test_retrieve_graph_trace_callback_emits_running_and_done_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            retriever = self._retriever(
                settings,
                [self._make_hit(chunk_id="trace-hit", book_slug="backup_and_restore")],
            )
            events: list[dict] = []

            retriever.retrieve(
                "백업",
                top_k=1,
                candidate_k=1,
                use_vector=False,
                trace_callback=events.append,
            )

            graph_events = [event for event in events if event.get("step") == "graph_expand"]
            self.assertEqual(["running", "done"], [event["status"] for event in graph_events])
            self.assertEqual("local_sidecar", graph_events[1]["meta"]["adapter_mode"])

    def test_retrieve_graph_trace_summary_counts_all_local_relations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            retriever = self._retriever(
                settings,
                [
                    self._make_hit(chunk_id="graph-a", book_slug="backup_and_restore", source_collection="customer_pack"),
                    self._make_hit(chunk_id="graph-b", book_slug="backup_and_restore", source_collection="customer_pack"),
                    self._make_hit(chunk_id="graph-c", book_slug="monitoring", source_collection="customer_pack"),
                ],
            )

            result = retriever.retrieve("운영", top_k=3, candidate_k=3, use_vector=False)

            self.assertEqual(3, result.trace["graph"]["summary"]["hit_count"])
            self.assertEqual(6, result.trace["graph"]["summary"]["relation_count"])
            self.assertEqual(3, result.trace["graph"]["summary"]["provenance_count"])

    def test_retrieve_graph_trace_keeps_provenance_source_collection_and_section_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            retriever = self._retriever(
                settings,
                [
                    self._make_hit(
                        chunk_id="prov-hit",
                        book_slug="customer_pack_ops",
                        source_collection="customer_pack",
                        source_lane="applied_playbook",
                        source_type="operation_playbook",
                    )
                ],
            )

            result = retriever.retrieve("운영 절차", top_k=1, candidate_k=1, use_vector=False)
            provenance = result.trace["graph"]["hits"][0]["provenance"]

            self.assertEqual("customer_pack", provenance["source_collection"])
            self.assertEqual(["운영", "customer_pack_ops"], provenance["section_path"])
