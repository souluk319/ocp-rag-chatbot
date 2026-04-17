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
        source_collection: str = "customer_pack",
        source_lane: str = "applied_playbook",
        source_type: str = "operation_playbook",
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
        return ChatRetriever(settings, SeededBm25(hits), vector_retriever=None)

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


if __name__ == "__main__":
    unittest.main()
