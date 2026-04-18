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


class TestRetrievalRuntime(unittest.TestCase):
    def test_reranker_rebalances_cluster_node_usage_back_to_support_family(self) -> None:
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
            context=None,
        )

        self.assertTrue(trace["applied"])
        self.assertEqual("support", hits[0].book_slug)

    def test_reranker_rebalances_generic_intro_back_to_intro_overview(self) -> None:
        hybrid_hits = [
            RetrievalHit(
                chunk_id="overview-intro",
                book_slug="overview",
                chapter="개요",
                section="OpenShift Container Platform 소개",
                anchor="ocp-overview",
                source_url="https://example.com/overview",
                viewer_path="/docs/overview.html#ocp-overview",
                text="OpenShift Container Platform 기능에 대한 개요를 설명합니다.",
                source="hybrid",
                raw_score=0.92,
                fused_score=0.92,
                component_scores={"pre_rerank_fused_score": 0.92},
            ),
            RetrievalHit(
                chunk_id="architecture-intro",
                book_slug="architecture",
                chapter="아키텍처",
                section="2.1.3. OpenShift Container Platform 개요",
                anchor="architecture-overview",
                source_url="https://example.com/architecture",
                viewer_path="/docs/architecture.html#architecture-overview",
                text="OpenShift Container Platform 개요를 설명합니다.",
                source="hybrid",
                raw_score=0.89,
                fused_score=0.89,
                component_scores={"pre_rerank_fused_score": 0.89},
            ),
            RetrievalHit(
                chunk_id="architecture-deep",
                book_slug="architecture",
                chapter="아키텍처",
                section="2.1.3.1. 사용자 정의 운영 체제",
                anchor="custom-os",
                source_url="https://example.com/architecture",
                viewer_path="/docs/architecture.html#custom-os",
                text="CRI-O와 Kubelet을 설명합니다.",
                source="hybrid",
                raw_score=0.81,
                fused_score=0.81,
                component_scores={"pre_rerank_fused_score": 0.81},
            ),
        ]
        reranked_hits = [
            RetrievalHit(
                chunk_id="architecture-deep",
                book_slug="architecture",
                chapter="아키텍처",
                section="2.1.3.1. 사용자 정의 운영 체제",
                anchor="custom-os",
                source_url="https://example.com/architecture",
                viewer_path="/docs/architecture.html#custom-os",
                text="CRI-O와 Kubelet을 설명합니다.",
                source="hybrid_reranked",
                raw_score=4.9,
                fused_score=4.9,
                component_scores={"pre_rerank_fused_score": 0.81, "reranker_score": 4.9},
            ),
            RetrievalHit(
                chunk_id="overview-intro",
                book_slug="overview",
                chapter="개요",
                section="OpenShift Container Platform 소개",
                anchor="ocp-overview",
                source_url="https://example.com/overview",
                viewer_path="/docs/overview.html#ocp-overview",
                text="OpenShift Container Platform 기능에 대한 개요를 설명합니다.",
                source="hybrid_reranked",
                raw_score=2.2,
                fused_score=2.2,
                component_scores={"pre_rerank_fused_score": 0.92, "reranker_score": 2.2},
            ),
        ]

        hits, trace = maybe_rerank_hits(
            _FakeRetrieverWithReranker(reranked_hits),
            query="오픈시프트가 뭐야",
            hybrid_hits=hybrid_hits,
            top_k=2,
            trace_callback=None,
            timings_ms={},
            context=None,
        )

        self.assertTrue(trace["applied"])
        self.assertEqual("overview", hits[0].book_slug)
        self.assertEqual("ocp-overview", hits[0].anchor)
        self.assertEqual("OpenShift Container Platform 소개", hits[0].section)
        self.assertTrue(hits[0].viewer_path.endswith("#ocp-overview"))
        self.assertEqual("overview-intro", hits[0].chunk_id)
        self.assertIn("generic_intro_intent", trace["rebalance_reasons"])

    def test_reranker_rebalances_etcd_backup_hits_toward_backup_procedure(self) -> None:
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
            context=None,
        )

        self.assertTrue(trace["applied"])
        self.assertEqual("postinstallation_configuration", hits[0].book_slug)

    def test_reranker_rescues_uploaded_customer_pack_for_explicit_customer_doc_query(self) -> None:
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
            context=None,
        )

        self.assertTrue(trace["applied"])
        self.assertEqual("customer-backup-runbook", hits[0].book_slug)
        self.assertEqual("uploaded", hits[0].source_collection)

    def test_reranker_rescues_uploaded_customer_pack_for_selected_draft_snippet_query(self) -> None:
        hybrid_hits = [
            RetrievalHit(
                chunk_id="uploaded-configmap-secret",
                book_slug="customer-config-guide",
                chapter="Customer Config Guide",
                section="ConfigMap Secret",
                anchor="snippet",
                source_url="/tmp/customer.pdf",
                viewer_path="/playbooks/customer-packs/draft-a/index.html#snippet",
                text="ConfigMap Secret values must be synchronized before rollout.",
                source="hybrid",
                raw_score=0.87,
                fused_score=0.87,
                source_collection="uploaded",
            ),
            RetrievalHit(
                chunk_id="core-configmap-secret",
                book_slug="authentication_and_authorization",
                chapter="auth",
                section="ConfigMap and Secret defaults",
                anchor="configmap-secret",
                source_url="https://example.com/core",
                viewer_path="/docs/core.html#configmap-secret",
                text="ConfigMap Secret handling in OpenShift",
                source="hybrid",
                raw_score=0.92,
                fused_score=0.92,
            ),
        ]
        reranked_hits = [
            RetrievalHit(
                chunk_id="core-configmap-secret",
                book_slug="authentication_and_authorization",
                chapter="auth",
                section="ConfigMap and Secret defaults",
                anchor="configmap-secret",
                source_url="https://example.com/core",
                viewer_path="/docs/core.html#configmap-secret",
                text="ConfigMap Secret handling in OpenShift",
                source="hybrid_reranked",
                raw_score=4.8,
                fused_score=4.8,
                component_scores={"pre_rerank_fused_score": 0.92, "reranker_score": 4.8},
            ),
        ]

        hits, trace = maybe_rerank_hits(
            _FakeRetrieverWithReranker(reranked_hits),
            query="ConfigMap Secret",
            hybrid_hits=hybrid_hits,
            top_k=2,
            trace_callback=None,
            timings_ms={},
            context=SessionContext(
                selected_draft_ids=["draft-a"],
                restrict_uploaded_sources=True,
            ),
        )

        self.assertTrue(trace["applied"])
        self.assertEqual("customer-config-guide", hits[0].book_slug)
        self.assertEqual("uploaded", hits[0].source_collection)
        self.assertIn("uploaded_customer_pack_priority", trace["rebalance_reasons"])

    def test_reranker_keeps_etcd_backup_companion_when_rerank_returns_only_postinstall_hits(self) -> None:
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
            context=None,
        )

        self.assertTrue(trace["applied"])
        self.assertEqual("postinstallation_configuration", hits[0].book_slug)
        self.assertIn(hits[1].book_slug, {"etcd", "backup_and_restore"})

    def test_reranker_replaces_restore_companion_with_backup_companion_for_etcd_backup_query(self) -> None:
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
            context=None,
        )

        self.assertTrue(trace["applied"])
        self.assertEqual("postinstallation_configuration", hits[0].book_slug)
        self.assertEqual("etcd", hits[1].book_slug)
        self.assertIn("데이터 백업", hits[1].section)

    def test_reranker_rebalances_certificate_monitor_query_back_to_cli_or_security(self) -> None:
        hybrid_hits = [
            RetrievalHit(
                chunk_id="cert-command",
                book_slug="cli_tools",
                chapter="cli",
                section="2.7.1.25. oc adm ocp-certificates monitor-certificates",
                anchor="oc-adm-ocp-certificates-monitor-certificates",
                source_url="https://example.com/cli",
                viewer_path="/docs/cli.html#oc-adm-ocp-certificates-monitor-certificates",
                text="플랫폼 인증서 감시 [CODE] oc adm ocp-certificates monitor-certificates [/CODE]",
                source="hybrid",
                raw_score=0.88,
                fused_score=0.88,
            ),
            RetrievalHit(
                chunk_id="cert-expiry",
                book_slug="security_and_compliance",
                chapter="security",
                section="4.1.4. 만료",
                anchor="expiration",
                source_url="https://example.com/security",
                viewer_path="/docs/security.html#expiration",
                text="API 서버 인증서 만료 여부를 확인합니다.",
                source="hybrid",
                raw_score=0.84,
                fused_score=0.84,
            ),
            RetrievalHit(
                chunk_id="support-install",
                book_slug="support",
                chapter="support",
                section="7.1.10. 컨트롤 플레인 노드 kubelet 및 API 서버 문제 조사",
                anchor="investigating-kubelet-api-installation-issues_troubleshooting-installations",
                source_url="https://example.com/support",
                viewer_path="/docs/support.html#investigating-kubelet-api-installation-issues_troubleshooting-installations",
                text="API 서버 문제 조사 지원 문서입니다.",
                source="hybrid",
                raw_score=0.93,
                fused_score=0.93,
            ),
        ]
        reranked_hits = [
            RetrievalHit(
                chunk_id="support-install",
                book_slug="support",
                chapter="support",
                section="7.1.10. 컨트롤 플레인 노드 kubelet 및 API 서버 문제 조사",
                anchor="investigating-kubelet-api-installation-issues_troubleshooting-installations",
                source_url="https://example.com/support",
                viewer_path="/docs/support.html#investigating-kubelet-api-installation-issues_troubleshooting-installations",
                text="API 서버 문제 조사 지원 문서입니다.",
                source="hybrid_reranked",
                raw_score=9.0,
                fused_score=9.0,
                component_scores={"pre_rerank_fused_score": 0.93, "reranker_score": 9.0},
            ),
            RetrievalHit(
                chunk_id="cert-expiry",
                book_slug="security_and_compliance",
                chapter="security",
                section="4.1.4. 만료",
                anchor="expiration",
                source_url="https://example.com/security",
                viewer_path="/docs/security.html#expiration",
                text="API 서버 인증서 만료 여부를 확인합니다.",
                source="hybrid_reranked",
                raw_score=8.0,
                fused_score=8.0,
                component_scores={"pre_rerank_fused_score": 0.84, "reranker_score": 8.0},
            ),
            RetrievalHit(
                chunk_id="cert-command",
                book_slug="cli_tools",
                chapter="cli",
                section="2.7.1.25. oc adm ocp-certificates monitor-certificates",
                anchor="oc-adm-ocp-certificates-monitor-certificates",
                source_url="https://example.com/cli",
                viewer_path="/docs/cli.html#oc-adm-ocp-certificates-monitor-certificates",
                text="플랫폼 인증서 감시 [CODE] oc adm ocp-certificates monitor-certificates [/CODE]",
                source="hybrid_reranked",
                raw_score=7.0,
                fused_score=7.0,
                component_scores={"pre_rerank_fused_score": 0.88, "reranker_score": 7.0},
            ),
        ]

        hits, trace = maybe_rerank_hits(
            _FakeRetrieverWithReranker(reranked_hits),
            query="API 서버 인증서 만료 여부는 어떻게 확인해?",
            hybrid_hits=hybrid_hits,
            top_k=3,
            trace_callback=None,
            timings_ms={},
            context=None,
        )

        self.assertTrue(trace["applied"])
        self.assertIn("certificate_monitor_intent", trace["rebalance_reasons"])
        self.assertIn(hits[0].book_slug, {"cli_tools", "security_and_compliance"})

    def test_retriever_applies_reranker_to_hybrid_candidates(self) -> None:
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
            SeededBm25(
                [
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
            ),
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
            SeededBm25(
                [
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
            ),
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
            SeededBm25(
                [
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
            ),
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
            SeededBm25(
                [
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
            ),
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
            SeededBm25(
                [
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
                        source_collection="core",
                        review_status="approved",
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
                        source_collection="core",
                        review_status="approved",
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
                        source_collection="core",
                        review_status="approved",
                    ),
                ]
            ),
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
        self.assertEqual("about-mco", result.hits[0].anchor)
        self.assertEqual("About the Machine Config Operator", result.hits[0].section)
        self.assertTrue(result.hits[0].viewer_path.endswith("#about-mco"))

    def test_retriever_rebalances_operations_query_toward_operation_playbook(self) -> None:
        class StubReranker:
            def __init__(self) -> None:
                self.model_name = "stub-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int):
                del query, top_k
                promoted = list(hits)
                promoted.sort(
                    key=lambda hit: (
                        0 if hit.source_type == "official_doc" else 1,
                        hit.book_slug,
                    )
                )
                for index, hit in enumerate(promoted, start=1):
                    hit.component_scores["pre_rerank_fused_score"] = float(hit.fused_score)
                    hit.component_scores["reranker_score"] = float(10 - index)
                    hit.fused_score = float(10 - index)
                    hit.raw_score = float(10 - index)
                return promoted

        retriever = ChatRetriever(
            Settings(ROOT),
            SeededBm25(
                [
                    RetrievalHit(
                        chunk_id="official-backup-hit",
                        book_slug="backup_and_restore",
                        chapter="백업",
                        section="컨트롤 플레인 백업",
                        anchor="control-plane-backup",
                        source_url="https://example.com/backup-and-restore",
                        viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html#control-plane-backup",
                        text="컨트롤 플레인 백업 절차를 설명합니다.",
                        source="bm25",
                        raw_score=1.0,
                        fused_score=1.0,
                        source_collection="core",
                        review_status="approved",
                        source_type="official_doc",
                    ),
                    RetrievalHit(
                        chunk_id="ops-backup-hit",
                        book_slug="backup_restore_operations",
                        chapter="운영",
                        section="컨트롤 플레인 백업 운영 절차",
                        anchor="backup-ops",
                        source_url="https://example.com/backup-ops",
                        viewer_path="/docs/ocp/4.20/ko/backup_restore_operations/index.html#backup-ops",
                        text="백업 실행과 검증 명령을 바로 수행하는 운영 플레이북입니다.",
                        source="bm25",
                        raw_score=0.95,
                        fused_score=0.95,
                        source_collection="core",
                        review_status="approved",
                        source_type="operation_playbook",
                    ),
                ]
            ),
            vector_retriever=None,
            reranker=StubReranker(),
        )

        result = retriever.retrieve(
            "컨트롤 플레인 백업 절차와 검증 명령 알려줘",
            top_k=2,
            candidate_k=2,
            use_vector=False,
        )

        self.assertEqual("official_doc", result.trace["hybrid"][0]["source_type"])
        self.assertEqual("operation_playbook", result.hits[0].source_type)
        self.assertEqual("operation_playbook", result.trace["reranked"][0]["source_type"])
        self.assertIn("derived_family_intent", result.trace["reranker"]["rebalance_reasons"])

    def test_retriever_rebalances_troubleshooting_query_toward_troubleshooting_playbook(self) -> None:
        class StubReranker:
            def __init__(self) -> None:
                self.model_name = "stub-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int):
                del query, top_k
                promoted = list(hits)
                promoted.sort(
                    key=lambda hit: (
                        0 if hit.source_type == "official_doc" else 1,
                        hit.book_slug,
                    )
                )
                for index, hit in enumerate(promoted, start=1):
                    hit.component_scores["pre_rerank_fused_score"] = float(hit.fused_score)
                    hit.component_scores["reranker_score"] = float(10 - index)
                    hit.fused_score = float(10 - index)
                    hit.raw_score = float(10 - index)
                return promoted

        retriever = ChatRetriever(
            Settings(ROOT),
            SeededBm25(
                [
                    RetrievalHit(
                        chunk_id="support-hit",
                        book_slug="support",
                        chapter="지원",
                        section="프로젝트 삭제 문제 조사",
                        anchor="project-delete-troubleshoot",
                        source_url="https://example.com/support",
                        viewer_path="/docs/ocp/4.20/ko/support/index.html#project-delete-troubleshoot",
                        text="프로젝트 삭제가 멈췄을 때 확인 순서를 설명합니다.",
                        source="bm25",
                        raw_score=1.0,
                        fused_score=1.0,
                        source_collection="core",
                        review_status="approved",
                        source_type="official_doc",
                    ),
                    RetrievalHit(
                        chunk_id="derived-troubleshoot-hit",
                        book_slug="project_namespace_troubleshooting_playbook",
                        chapter="트러블슈팅",
                        section="프로젝트 Terminating 트러블슈팅 플레이북",
                        anchor="terminating-project",
                        source_url="https://example.com/project-troubleshooting",
                        viewer_path="/docs/ocp/4.20/ko/project_namespace_troubleshooting_playbook/index.html#terminating-project",
                        text="Terminating 상태에서 안 지워질 때 점검 순서를 바로 안내합니다.",
                        source="bm25",
                        raw_score=0.96,
                        fused_score=0.96,
                        source_collection="core",
                        review_status="approved",
                        source_type="troubleshooting_playbook",
                    ),
                ]
            ),
            vector_retriever=None,
            reranker=StubReranker(),
        )

        result = retriever.retrieve(
            "프로젝트가 Terminating에서 안 지워질 때 어디부터 점검해야 해?",
            top_k=2,
            candidate_k=2,
            use_vector=False,
        )

        self.assertEqual("official_doc", result.trace["hybrid"][0]["source_type"])
        self.assertEqual("troubleshooting_playbook", result.hits[0].source_type)
        self.assertEqual("troubleshooting_playbook", result.trace["reranked"][0]["source_type"])
        self.assertIn("derived_family_intent", result.trace["reranker"]["rebalance_reasons"])

    def test_retriever_rebalances_policy_query_toward_policy_overlay_book(self) -> None:
        class StubReranker:
            def __init__(self) -> None:
                self.model_name = "stub-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int):
                del query, top_k
                promoted = list(hits)
                promoted.sort(
                    key=lambda hit: (
                        0 if hit.source_type == "official_doc" else 1,
                        hit.book_slug,
                    )
                )
                for index, hit in enumerate(promoted, start=1):
                    hit.component_scores["pre_rerank_fused_score"] = float(hit.fused_score)
                    hit.component_scores["reranker_score"] = float(10 - index)
                    hit.fused_score = float(10 - index)
                    hit.raw_score = float(10 - index)
                return promoted

        retriever = ChatRetriever(
            Settings(ROOT),
            SeededBm25(
                [
                    RetrievalHit(
                        chunk_id="official-disconnected-hit",
                        book_slug="disconnected_environments",
                        chapter="분리망",
                        section="분리망 설치 요구 사항",
                        anchor="disconnected-prerequisites",
                        source_url="https://example.com/disconnected",
                        viewer_path="/docs/ocp/4.20/ko/disconnected_environments/index.html#disconnected-prerequisites",
                        text="분리망 환경에서 필요한 요구 사항을 설명합니다.",
                        source="bm25",
                        raw_score=1.0,
                        fused_score=1.0,
                        source_collection="core",
                        review_status="approved",
                        source_type="official_doc",
                    ),
                    RetrievalHit(
                        chunk_id="policy-overlay-hit",
                        book_slug="disconnected_policy_overlay_book",
                        chapter="정책",
                        section="분리망 지원 제한과 사전 조건 정책",
                        anchor="policy-prerequisites",
                        source_url="https://example.com/disconnected-policy",
                        viewer_path="/docs/ocp/4.20/ko/disconnected_policy_overlay_book/index.html#policy-prerequisites",
                        text="지원 제한, 사전 조건, 금지되는 구성을 정책 오버레이로 다시 묶었습니다.",
                        source="bm25",
                        raw_score=0.97,
                        fused_score=0.97,
                        source_collection="core",
                        review_status="approved",
                        source_type="policy_overlay_book",
                    ),
                ]
            ),
            vector_retriever=None,
            reranker=StubReranker(),
        )

        result = retriever.retrieve(
            "분리망 환경에서 지원 제한과 사전 조건 정책부터 알려줘",
            top_k=2,
            candidate_k=2,
            use_vector=False,
        )

        self.assertEqual("official_doc", result.trace["hybrid"][0]["source_type"])
        self.assertEqual("policy_overlay_book", result.hits[0].source_type)
        self.assertEqual("policy_overlay_book", result.trace["reranked"][0]["source_type"])
        self.assertIn("derived_family_intent", result.trace["reranker"]["rebalance_reasons"])


if __name__ == "__main__":
    unittest.main()
