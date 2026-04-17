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


if __name__ == "__main__":
    unittest.main()
