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
    normalize_query,
    query_book_adjustments,
    rewrite_query,
)
from ocp_rag_part2.retriever import Part2Retriever, fuse_ranked_hits


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
        self.assertIn("restore", normalized)

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


if __name__ == "__main__":
    unittest.main()
