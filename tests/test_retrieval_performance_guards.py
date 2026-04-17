from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from _support_retrieval import ROOT, RetrievalHit, Settings
from play_book_studio.ingestion.embedding import EmbeddingClient
from play_book_studio.retrieval.retriever_rerank import maybe_rerank_hits
from play_book_studio.retrieval.vector import VectorRetriever


class EmbeddingClientPerformanceTests(unittest.TestCase):
    def test_embed_texts_caches_single_query_embeddings(self) -> None:
        settings = Settings(ROOT)
        settings.embedding_base_url = "http://embedding.example"
        client = EmbeddingClient(settings)

        with patch.object(client, "_request_embeddings", return_value=[[0.1, 0.2, 0.3]]) as request_embeddings:
            first = client.embed_texts(["etcd 백업 절차 알려줘"])
            second = client.embed_texts(["etcd 백업 절차 알려줘"])

        self.assertEqual([[0.1, 0.2, 0.3]], first)
        self.assertEqual(first, second)
        self.assertEqual(1, request_embeddings.call_count)


class VectorRetrieverPerformanceTests(unittest.TestCase):
    def test_search_with_trace_uses_configured_request_timeout(self) -> None:
        settings = Settings(ROOT)
        settings.embedding_base_url = "http://embedding.example"
        settings.qdrant_url = "http://qdrant.example"
        settings.qdrant_collection = "test-collection"
        settings.request_timeout_seconds = 7
        retriever = VectorRetriever(settings)

        class _Response:
            ok = True
            status_code = 200

            @staticmethod
            def json() -> dict[str, object]:
                return {"result": []}

        with (
            patch.object(retriever.embedding_client, "embed_texts", return_value=[[0.1, 0.2, 0.3]]),
            patch("play_book_studio.retrieval.vector.requests.post", return_value=_Response()) as mocked_post,
        ):
            retriever.search_with_trace("etcd 백업 절차 알려줘", top_k=5)

        self.assertEqual(7.0, mocked_post.call_args.kwargs["timeout"])


class RerankerPerformanceTests(unittest.TestCase):
    def test_reranker_skips_model_for_simple_etcd_backup_query_and_rebalances_from_hybrid_hits(self) -> None:
        hybrid_hits = [
            RetrievalHit(
                chunk_id="postinstall-hit",
                book_slug="postinstallation_configuration",
                chapter="etcd",
                section="4.12.5. etcd 데이터 백업",
                anchor="backing-up-etcd-data",
                source_url="https://example.com/postinstall",
                viewer_path="/docs/postinstall.html#backing-up-etcd-data",
                text="백업 전에 클러스터 상태를 확인합니다.",
                source="hybrid",
                raw_score=0.95,
                fused_score=0.95,
            ),
            RetrievalHit(
                chunk_id="etcd-hit",
                book_slug="etcd",
                chapter="etcd",
                section="etcd 재해 복구",
                anchor="etcd-dr",
                source_url="https://example.com/etcd",
                viewer_path="/docs/etcd.html#etcd-dr",
                text="etcd 복구 개요와 주의 사항입니다.",
                source="hybrid",
                raw_score=0.91,
                fused_score=0.91,
            ),
            RetrievalHit(
                chunk_id="backup-hit",
                book_slug="backup_and_restore",
                chapter="backup",
                section="자동화된 etcd 백업",
                anchor="automated-etcd-backup",
                source_url="https://example.com/backup",
                viewer_path="/docs/backup.html#automated-etcd-backup",
                text="cluster-backup.sh 스크립트로 etcd 백업을 수행합니다.",
                source="hybrid",
                raw_score=0.88,
                fused_score=0.88,
            ),
        ]

        class _CountingReranker:
            def __init__(self) -> None:
                self.calls = 0
                self.model_name = "counting-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int) -> list[RetrievalHit]:
                del query, hits, top_k
                self.calls += 1
                raise AssertionError("heuristic-first query should not invoke the reranker model")

        reranker = _CountingReranker()
        retriever = SimpleNamespace(
            reranker=reranker,
            settings=SimpleNamespace(root_dir=ROOT),
        )

        hits, trace = maybe_rerank_hits(
            retriever,
            query="etcd 백업 절차 알려줘",
            hybrid_hits=hybrid_hits,
            top_k=3,
            trace_callback=None,
            timings_ms={},
            context=None,
        )

        self.assertEqual(0, reranker.calls)
        self.assertTrue(trace["applied"])
        self.assertFalse(trace["model_applied"])
        self.assertEqual("heuristic_only", trace["mode"])
        self.assertEqual("heuristic_first_intent", trace["decision_reason"])
        self.assertIn("etcd_backup_restore_intent", trace["rebalance_reasons"])
        self.assertEqual("backup_and_restore", hits[0].book_slug)

    def test_reranker_skips_model_for_confident_explanation_query(self) -> None:
        hybrid_hits = [
            RetrievalHit(
                chunk_id="architecture-hit",
                book_slug="architecture",
                chapter="architecture",
                section="OpenShift 아키텍처 개요",
                anchor="overview",
                source_url="https://example.com/architecture",
                viewer_path="/docs/architecture.html#overview",
                text="OpenShift는 컨트롤 플레인과 작업자 노드로 구성됩니다.",
                source="hybrid",
                raw_score=0.98,
                fused_score=0.98,
                component_scores={"bm25_score": 0.91, "vector_score": 0.94},
            ),
            RetrievalHit(
                chunk_id="overview-hit",
                book_slug="overview",
                chapter="overview",
                section="플랫폼 개요",
                anchor="platform-overview",
                source_url="https://example.com/overview",
                viewer_path="/docs/overview.html#platform-overview",
                text="플랫폼 기본 개요입니다.",
                source="hybrid",
                raw_score=0.74,
                fused_score=0.74,
                component_scores={"bm25_score": 0.62},
            ),
        ]

        class _CountingReranker:
            def __init__(self) -> None:
                self.calls = 0
                self.model_name = "counting-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int) -> list[RetrievalHit]:
                del query, hits, top_k
                self.calls += 1
                raise AssertionError("confident explanation query should skip model rerank")

        reranker = _CountingReranker()
        retriever = SimpleNamespace(
            reranker=reranker,
            settings=SimpleNamespace(root_dir=ROOT),
        )

        hits, trace = maybe_rerank_hits(
            retriever,
            query="OpenShift 아키텍처를 설명해줘",
            hybrid_hits=hybrid_hits,
            top_k=2,
            trace_callback=None,
            timings_ms={},
            context=None,
        )

        self.assertEqual(0, reranker.calls)
        self.assertFalse(trace["model_applied"])
        self.assertEqual("heuristic_only", trace["mode"])
        self.assertEqual("confident_explanation_hybrid_top_hit", trace["decision_reason"])
        self.assertEqual("architecture", hits[0].book_slug)

    def test_reranker_caps_candidate_budget_for_compare_queries(self) -> None:
        hybrid_hits = [
            RetrievalHit(
                chunk_id=f"compare-{index}",
                book_slug=book_slug,
                chapter=book_slug,
                section=f"{book_slug} section",
                anchor=f"anchor-{index}",
                source_url=f"https://example.com/{book_slug}",
                viewer_path=f"/docs/{book_slug}.html#anchor-{index}",
                text=f"{book_slug} 관련 설명입니다.",
                source="hybrid",
                raw_score=score,
                fused_score=score,
                component_scores={"bm25_score": score - 0.05, "vector_score": score - 0.03},
            )
            for index, (book_slug, score) in enumerate(
                [
                    ("networking", 0.96),
                    ("ingress_and_load_balancing", 0.95),
                    ("architecture", 0.82),
                    ("overview", 0.80),
                    ("operators", 0.78),
                    ("nodes", 0.76),
                ],
                start=1,
            )
        ]

        class _BudgetCapturingReranker:
            def __init__(self) -> None:
                self.calls: list[dict[str, int | None]] = []
                self.model_name = "capturing-reranker"
                self.top_n = 10

            def rerank(
                self,
                query: str,
                hits: list[RetrievalHit],
                *,
                top_k: int,
                top_n_override: int | None = None,
            ) -> list[RetrievalHit]:
                del query, hits
                self.calls.append({"top_k": top_k, "top_n_override": top_n_override})
                return hybrid_hits

        reranker = _BudgetCapturingReranker()
        retriever = SimpleNamespace(
            reranker=reranker,
            settings=SimpleNamespace(root_dir=ROOT),
        )

        hits, trace = maybe_rerank_hits(
            retriever,
            query="Route와 Ingress 차이를 설명해줘",
            hybrid_hits=hybrid_hits,
            top_k=3,
            trace_callback=None,
            timings_ms={},
            context=None,
        )

        self.assertEqual(1, len(reranker.calls))
        self.assertEqual(6, reranker.calls[0]["top_n_override"])
        self.assertTrue(trace["model_applied"])
        self.assertEqual("model", trace["mode"])
        self.assertEqual(6, trace["candidate_budget"])
        self.assertEqual(3, len(hits))


if __name__ == "__main__":
    unittest.main()
