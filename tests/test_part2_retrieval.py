from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.settings import Settings
from ocp_rag_part2.bm25 import BM25Index
from ocp_rag_part2.models import RetrievalHit, SessionContext
from ocp_rag_part2.query import (
    detect_unsupported_product,
    has_scc_troubleshooting_intent,
    normalize_query,
    query_book_adjustments,
    rewrite_query,
)
from ocp_rag_part2.retriever import Part2Retriever, fuse_ranked_hits
from ocp_rag_part2.retriever import filter_hits_by_language_policy


class RetrievalTests(unittest.TestCase):
    def test_bm25_prefers_matching_korean_chunk(self) -> None:
        rows = [
            {
                "chunk_id": "chunk-etcd",
                "book_slug": "backup_and_restore",
                "chapter": "백업",
                "section": "etcd 백업",
                "anchor": "etcd-backup",
                "source_url": "https://example.com/backup",
                "viewer_path": "/docs/backup.html#etcd-backup",
                "text": "OpenShift etcd 백업과 복구 절차를 설명합니다.",
            },
            {
                "chunk_id": "chunk-route",
                "book_slug": "ingress_and_load_balancing",
                "chapter": "네트워크",
                "section": "Route",
                "anchor": "route",
                "source_url": "https://example.com/route",
                "viewer_path": "/docs/route.html#route",
                "text": "Route와 Ingress 차이를 설명합니다.",
            },
        ]
        index = BM25Index.from_rows(rows)

        hits = index.search("etcd 백업 방법", top_k=2)

        self.assertEqual("chunk-etcd", hits[0].chunk_id)

    def test_rewrite_query_uses_session_context_for_follow_up(self) -> None:
        context = SessionContext(
            current_topic="etcd 백업",
            ocp_version="4.20",
            unresolved_question="백업 이후 복구 절차",
        )

        rewritten = rewrite_query("그거 복구는?", context)

        self.assertIn("etcd 백업", rewritten)
        self.assertIn("4.20", rewritten)
        self.assertIn("그거 복구는?", rewritten)

    def test_rewrite_query_does_not_fire_for_first_turn_with_version_only_context(self) -> None:
        context = SessionContext(mode="ops", ocp_version="4.20")

        rewritten = rewrite_query("오픈시프트가 뭐야?", context)

        self.assertEqual("오픈시프트가 뭐야?", rewritten)

    def test_rewrite_query_resolves_entity_use_case_follow_up(self) -> None:
        context = SessionContext(
            current_topic="OpenShift 아키텍처 개요",
            open_entities=["OpenShift Container Platform"],
            ocp_version="4.20",
        )

        rewritten = rewrite_query("그걸 어따써?", context)

        self.assertIn("OpenShift", rewritten)
        self.assertIn("사용 사례", rewritten)
        self.assertIn("overview", rewritten)

    def test_rewrite_query_handles_colloquial_use_case_follow_up_typo(self) -> None:
        context = SessionContext(
            current_topic="OpenShift 아키텍처 개요",
            open_entities=["OpenShift Container Platform"],
            ocp_version="4.20",
        )

        rewritten = rewrite_query("그걸 어떠써?", context)

        self.assertIn("OpenShift", rewritten)
        self.assertIn("용도", rewritten)
        self.assertIn("사용 사례", rewritten)

    def test_normalize_query_expands_high_value_aliases(self) -> None:
        normalized = normalize_query("로그는 어디서 봐?")

        self.assertIn("로깅", normalized)
        self.assertIn("logging", normalized)

    def test_normalize_query_expands_security_and_architecture_aliases(self) -> None:
        normalized = normalize_query("보안 아키텍처 기본 문서")

        self.assertIn("security", normalized)
        self.assertIn("architecture", normalized)
        self.assertIn("overview", normalized)

    def test_normalize_query_expands_architecture_explainer_prompt(self) -> None:
        normalized = normalize_query("오픈시프트 아키텍처를 설명해줘")

        self.assertIn("OpenShift", normalized)
        self.assertIn("architecture", normalized)
        self.assertIn("overview", normalized)

    def test_normalize_query_expands_etcd_backup_intent(self) -> None:
        normalized = normalize_query("etcd 백업은 어떻게 해?")

        self.assertIn("backup", normalized)
        self.assertIn("snapshot", normalized)
        self.assertNotIn("restore", normalized)

    def test_normalize_query_keeps_etcd_explainer_separate_from_backup_restore(self) -> None:
        normalized = normalize_query("etcd가 왜 중요한지 설명해줘")

        self.assertIn("quorum", normalized)
        self.assertIn("cluster", normalized)
        self.assertNotIn("backup", normalized)
        self.assertNotIn("restore", normalized)

    def test_query_book_adjustments_boost_backup_docs_for_doc_locator(self) -> None:
        boosts, penalties = query_book_adjustments("백업 복구 문서는 어디서 봐?")

        self.assertGreater(boosts["backup_and_restore"], 1.0)
        self.assertGreater(boosts["etcd"], 1.0)
        self.assertNotIn("backup_and_restore", penalties)

    def test_query_book_adjustments_prefer_etcd_for_backup_only_how_to(self) -> None:
        boosts, penalties = query_book_adjustments("etcd 백업은 어떻게 해?")

        self.assertGreater(boosts["etcd"], 1.3)
        self.assertLess(penalties["backup_and_restore"], 1.0)

    def test_scc_operational_query_expands_verification_and_grant_terms(self) -> None:
        normalized = normalize_query(
            "특정 Pod가 Permission denied 에러를 내는데 SCC 확인하고 anyuid 권한 주는 방법은?"
        )

        self.assertIn("openshift.io/scc", normalized)
        self.assertIn("jsonpath", normalized)
        self.assertIn("oc adm policy add-scc-to-user", normalized)
        self.assertIn("system:openshift:scc:anyuid", normalized)
        self.assertTrue(has_scc_troubleshooting_intent(normalized))

    def test_query_book_adjustments_boost_auth_and_nodes_for_scc_ops(self) -> None:
        boosts, penalties = query_book_adjustments(
            "특정 Pod가 Permission denied 에러를 내는데 SCC 확인하고 anyuid 권한 주는 방법은?"
        )

        self.assertGreater(boosts["authentication_and_authorization"], 1.4)
        self.assertGreater(boosts["nodes"], 1.1)
        self.assertGreater(boosts["cli_tools"], 1.1)
        self.assertLess(penalties["storage"], 1.0)

    def test_detect_unsupported_product_flags_external_install_query(self) -> None:
        self.assertEqual("harbor", detect_unsupported_product("Harbor 설치 방법 알려줘"))
        self.assertIsNone(detect_unsupported_product("OpenShift에서 Harbor 연동 방법 알려줘"))

    def test_fusion_penalizes_english_only_hit_for_korean_query(self) -> None:
        english_hit = RetrievalHit(
            chunk_id="en-hit",
            book_slug="monitoring",
            chapter="Monitoring",
            section="Monitoring",
            anchor="monitoring",
            source_url="https://example.com/en",
            viewer_path="/docs/en.html#monitoring",
            text="Monitoring stack configuration and alerts",
            source="bm25",
            raw_score=10.0,
            fused_score=10.0,
        )
        korean_hit = RetrievalHit(
            chunk_id="ko-hit",
            book_slug="monitoring",
            chapter="모니터링",
            section="모니터링",
            anchor="monitoring-ko",
            source_url="https://example.com/ko",
            viewer_path="/docs/ko.html#monitoring",
            text="모니터링 스택 구성과 경고 설정 방법",
            source="vector",
            raw_score=9.0,
            fused_score=9.0,
        )

        hits = fuse_ranked_hits(
            "모니터링 설정",
            {
                "bm25": [english_hit, korean_hit],
                "vector": [korean_hit, english_hit],
            },
            top_k=2,
        )

        self.assertEqual("ko-hit", hits[0].chunk_id)

    def test_fusion_boosts_books_supported_by_bm25_and_vector(self) -> None:
        vector_only_hit = RetrievalHit(
            chunk_id="nodes-hit",
            book_slug="nodes",
            chapter="nodes",
            section="기본 인증 보안 생성",
            anchor="nodes-security",
            source_url="https://example.com/nodes",
            viewer_path="/docs/nodes.html#nodes-security",
            text="기본 인증 보안 생성 절차",
            source="vector",
            raw_score=0.52,
            fused_score=0.52,
        )
        security_vector_hit = RetrievalHit(
            chunk_id="security-vector-hit",
            book_slug="security_and_compliance",
            chapter="security",
            section="기본 통신 인증서 교체",
            anchor="default-cert",
            source_url="https://example.com/security-cert",
            viewer_path="/docs/security.html#default-cert",
            text="보안과 인증서 기본 구성을 설명합니다.",
            source="vector",
            raw_score=0.51,
            fused_score=0.51,
        )
        security_bm25_hit = RetrievalHit(
            chunk_id="security-bm25-hit",
            book_slug="security_and_compliance",
            chapter="security",
            section="클러스터 이벤트 감시",
            anchor="cluster-events",
            source_url="https://example.com/security-events",
            viewer_path="/docs/security.html#cluster-events",
            text="보안 관련 기본 문서와 운영 중점 항목",
            source="bm25",
            raw_score=13.0,
            fused_score=13.0,
        )

        hits = fuse_ranked_hits(
            "보안 관련 기본 문서는 뭐가 중요해?",
            {
                "bm25": [security_bm25_hit],
                "vector": [vector_only_hit, security_vector_hit],
            },
            top_k=3,
        )

        self.assertEqual("security_and_compliance", hits[0].book_slug)

    def test_fusion_prefers_architecture_for_generic_openshift_intro_query(self) -> None:
        architecture_hit = RetrievalHit(
            chunk_id="architecture-hit",
            book_slug="architecture",
            chapter="architecture",
            section="OpenShift Container Platform 아키텍처 개요",
            anchor="architecture-overview",
            source_url="https://example.com/architecture",
            viewer_path="/docs/architecture.html#overview",
            text="OpenShift Container Platform 아키텍처 개요와 기본 개념",
            source="vector",
            raw_score=0.70,
            fused_score=0.70,
        )
        networking_hit = RetrievalHit(
            chunk_id="networking-hit",
            book_slug="networking_overview",
            chapter="networking",
            section="OpenShift Container Platform 기본 네트워크 개념",
            anchor="networking-overview",
            source_url="https://example.com/networking",
            viewer_path="/docs/networking.html#overview",
            text="OpenShift Container Platform 기본 네트워크 개념과 일반 작업 이해",
            source="bm25",
            raw_score=0.72,
            fused_score=0.72,
        )

        hits = fuse_ranked_hits(
            "오픈시프트 OpenShift 소개 overview architecture 기본 개념",
            {
                "bm25": [networking_hit, architecture_hit],
                "vector": [architecture_hit, networking_hit],
            },
            top_k=2,
        )

        self.assertEqual("architecture", hits[0].book_slug)

    def test_fusion_prefers_scc_command_sections_for_scc_ops_query(self) -> None:
        general_scc_hit = RetrievalHit(
            chunk_id="auth-general",
            book_slug="authentication_and_authorization",
            chapter="auth",
            section="기본 보안 컨텍스트 제약 조건",
            anchor="default-sccs",
            source_url="https://example.com/auth-general",
            viewer_path="/docs/auth-general.html#default-sccs",
            text="anyuid 는 restricted SCC 의 모든 기능을 제공하지만 사용자는 모든 UID 및 GID 로 실행할 수 있습니다.",
            source="bm25",
            raw_score=0.73,
            fused_score=0.73,
        )
        scc_check_hit = RetrievalHit(
            chunk_id="auth-check",
            book_slug="authentication_and_authorization",
            chapter="auth",
            section="특정 SCC가 필요하도록 워크로드 구성",
            anchor="required-scc",
            source_url="https://example.com/auth-check",
            viewer_path="/docs/auth-check.html#required-scc",
            text="openshift.io/scc 주석 값을 확인하려면 oc get pod <pod_name> -o jsonpath='{.metadata.annotations.openshift\\.io\\/scc}{\"\\n\"}' 를 실행합니다.",
            source="vector",
            raw_score=0.69,
            fused_score=0.69,
        )
        scc_grant_hit = RetrievalHit(
            chunk_id="cli-grant",
            book_slug="cli_tools",
            chapter="cli",
            section="oc adm policy add-scc-to-user",
            anchor="oc-adm-policy-add-scc-to-user",
            source_url="https://example.com/cli-grant",
            viewer_path="/docs/cli-grant.html#grant",
            text="[CODE] oc adm policy add-scc-to-user anyuid -z <service_account_name> -n <project_name> [/CODE]",
            source="vector",
            raw_score=0.66,
            fused_score=0.66,
        )

        hits = fuse_ranked_hits(
            "특정 Pod가 Permission denied 에러를 내는데 SCC 확인하고 anyuid 권한 주는 방법은?",
            {
                "bm25": [general_scc_hit, scc_check_hit],
                "vector": [scc_check_hit, scc_grant_hit],
            },
            top_k=4,
        )

        self.assertEqual("auth-check", hits[0].chunk_id)
        self.assertIn("cli-grant", {hit.chunk_id for hit in hits[:4]})

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

    def test_retriever_short_circuits_unsupported_external_query(self) -> None:
        settings = Settings(ROOT)
        retriever = Part2Retriever(settings, BM25Index.from_rows([]), vector_retriever=None)

        result = retriever.retrieve("Harbor 설치 방법 알려줘", use_bm25=False, use_vector=False)

        self.assertEqual([], result.hits)
        self.assertTrue(
            any("outside OCP corpus" in warning for warning in result.trace["warnings"])
        )

    def test_filter_hits_by_language_policy_warns_or_excludes_books(self) -> None:
        hits = [
            RetrievalHit(
                chunk_id="backup-hit",
                book_slug="backup_and_restore",
                chapter="backup",
                section="Backup and restore",
                anchor="backup",
                source_url="https://example.com/backup",
                viewer_path="/docs/backup/index.html#backup",
                text="Backup and restore cluster state",
                source="hybrid",
                raw_score=0.8,
                fused_score=0.8,
            ),
            RetrievalHit(
                chunk_id="low-hit",
                book_slug="custom_low_value_book",
                chapter="low",
                section="Low value book",
                anchor="low",
                source_url="https://example.com/low",
                viewer_path="/docs/low/index.html#low",
                text="English only appendix",
                source="hybrid",
                raw_score=0.7,
                fused_score=0.7,
            ),
            RetrievalHit(
                chunk_id="ko-hit",
                book_slug="architecture",
                chapter="architecture",
                section="아키텍처 개요",
                anchor="overview",
                source_url="https://example.com/architecture",
                viewer_path="/docs/architecture/index.html#overview",
                text="OpenShift 아키텍처 개요",
                source="hybrid",
                raw_score=0.6,
                fused_score=0.6,
            ),
        ]
        warnings: list[str] = []

        filtered = filter_hits_by_language_policy(
            hits,
            {
                "backup_and_restore": {
                    "retrieval_policy": "allow_with_warning",
                    "recommended_action": "translate_priority",
                },
                "custom_low_value_book": {
                    "retrieval_policy": "exclude_default",
                    "recommended_action": "exclude_default",
                },
            },
            warnings,
            top_k=3,
        )

        self.assertEqual(["backup_and_restore", "architecture"], [hit.book_slug for hit in filtered])
        self.assertTrue(any("backup_and_restore" in warning for warning in warnings))
        self.assertTrue(any("custom_low_value_book" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main()
