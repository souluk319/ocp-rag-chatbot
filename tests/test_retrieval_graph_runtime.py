from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import Settings, load_settings
from play_book_studio.retrieval.models import RetrievalHit
from play_book_studio.retrieval.retriever import ChatRetriever


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class _StubBm25:
    def __init__(self, hits: list[RetrievalHit]) -> None:
        self._hits = hits

    def search(self, query: str, top_k: int) -> list[RetrievalHit]:
        del query, top_k
        return list(self._hits)


class RetrievalGraphRuntimeTests(unittest.TestCase):
    def test_load_settings_keeps_graph_enabled_default_on_without_env_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = load_settings(Path(tmpdir))

        self.assertTrue(settings.graph_enabled)
        self.assertEqual("auto", settings.graph_runtime_mode)

    def test_retrieve_attaches_local_graph_sidecar_provenance_and_relations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                root_dir=Path(tmpdir),
                graph_sidecar_path_override="artifacts/retrieval/custom_graph_sidecar.json",
            )
            _write_json(
                settings.graph_sidecar_path,
                {
                    "books": [
                        {
                            "book_slug": "backup_restore_control_plane",
                            "title": "컨트롤 플레인 백업/복구 플레이북",
                            "source_type": "topic_playbook",
                            "source_lane": "applied_playbook",
                            "source_collection": "core",
                            "derived_from_book_slug": "backup_and_restore",
                            "topic_key": "backup_restore_control_plane",
                        }
                    ]
                },
            )
            hit = RetrievalHit(
                chunk_id="backup-hit",
                book_slug="backup_restore_control_plane",
                chapter="backup",
                section="컨트롤 플레인 백업 절차",
                anchor="control-plane-backup",
                source_url="https://example.com/backup",
                viewer_path="/docs/ocp/4.20/ko/backup_restore_control_plane/index.html#control-plane-backup",
                text="cluster-backup.sh /home/core/assets/backup",
                source="bm25",
                raw_score=1.0,
                fused_score=1.0,
                source_collection="core",
                semantic_role="procedure",
                block_kinds=("code",),
            )
            retriever = ChatRetriever(settings, _StubBm25([hit]), vector_retriever=None)

            result = retriever.retrieve(
                "컨트롤 플레인 백업 절차",
                top_k=1,
                candidate_k=1,
                use_vector=False,
            )

            self.assertTrue(result.trace["graph"]["graph_enabled"])
            self.assertIn("graph", result.trace)
            self.assertEqual("local_sidecar", result.trace["graph"]["adapter_mode"])
            self.assertEqual(str(settings.graph_sidecar_path), result.trace["graph"]["sidecar_path"])
            self.assertEqual(1, result.trace["graph"]["summary"]["provenance_count"])
            graph_hit = result.trace["graph"]["hits"][0]
            self.assertEqual("backup_restore_control_plane", graph_hit["book_slug"])
            self.assertEqual(
                "backup_and_restore",
                graph_hit["provenance"]["derived_from_book_slug"],
            )
            self.assertIn(
                "derived_from_book",
                [relation["type"] for relation in graph_hit["relations"]],
            )
            self.assertEqual(1.0, result.hits[0].component_scores["graph_provenance_count"])
            self.assertGreaterEqual(
                result.hits[0].component_scores["graph_relation_count"],
                1.0,
            )

    def test_retrieve_falls_back_to_local_sidecar_when_remote_graph_endpoint_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                root_dir=Path(tmpdir),
                graph_runtime_mode="remote",
                graph_endpoint="http://graph.example.test",
                graph_sidecar_path_override="artifacts/retrieval/custom_graph_sidecar.json",
            )
            _write_json(
                settings.graph_sidecar_path,
                {
                    "books": [
                        {
                            "book_slug": "etcd_backup_restore",
                            "title": "etcd 백업/복구 플레이북",
                            "source_type": "topic_playbook",
                            "source_lane": "applied_playbook",
                            "source_collection": "core",
                            "derived_from_book_slug": "etcd",
                            "topic_key": "etcd_backup_restore",
                        }
                    ]
                },
            )
            hit = RetrievalHit(
                chunk_id="etcd-hit",
                book_slug="etcd_backup_restore",
                chapter="etcd",
                section="etcd 백업 절차",
                anchor="etcd-backup",
                source_url="https://example.com/etcd",
                viewer_path="/docs/ocp/4.20/ko/etcd_backup_restore/index.html#etcd-backup",
                text="cluster-backup.sh /home/core/assets/backup",
                source="bm25",
                raw_score=1.0,
                fused_score=1.0,
                source_collection="core",
                semantic_role="procedure",
                block_kinds=("code",),
            )
            retriever = ChatRetriever(settings, _StubBm25([hit]), vector_retriever=None)

            with patch(
                "play_book_studio.retrieval.graph_runtime.requests.post",
                side_effect=RuntimeError("graph endpoint down"),
            ):
                result = retriever.retrieve(
                    "etcd 백업 절차",
                    top_k=1,
                    candidate_k=1,
                    use_vector=False,
                )

            self.assertTrue(result.trace["graph"]["graph_enabled"])
            self.assertEqual("local_sidecar", result.trace["graph"]["adapter_mode"])
            self.assertTrue(
                str(result.trace["graph"]["fallback_reason"]).startswith("remote_endpoint_failed:")
            )
            self.assertEqual(
                "etcd",
                result.trace["graph"]["hits"][0]["provenance"]["derived_from_book_slug"],
            )

    def test_retrieve_uses_graph_relations_to_promote_related_playbook(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                root_dir=Path(tmpdir),
                graph_sidecar_path_override="artifacts/retrieval/custom_graph_sidecar.json",
                graph_boost_top_n=2,
            )
            _write_json(
                settings.graph_sidecar_path,
                {
                    "schema": "graph_sidecar_v1",
                    "book_count": 3,
                    "relation_count": 1,
                    "books": [
                        {
                            "book_slug": "backup_and_restore",
                            "title": "백업 및 복구",
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                            "source_collection": "core",
                        },
                        {
                            "book_slug": "backup_restore_control_plane",
                            "title": "컨트롤 플레인 백업/복구 플레이북",
                            "source_type": "topic_playbook",
                            "source_lane": "applied_playbook",
                            "source_collection": "core",
                            "derived_from_book_slug": "backup_and_restore",
                            "topic_key": "backup_restore_control_plane",
                        },
                        {
                            "book_slug": "overview",
                            "title": "개요",
                            "source_type": "official_doc",
                            "source_lane": "official_ko",
                            "source_collection": "core",
                        },
                    ],
                    "relations": [
                        {
                            "source_book_slug": "backup_and_restore",
                            "target_book_slug": "backup_restore_control_plane",
                            "relation_types": ["derived_from_book", "shared_k8s_object"],
                            "signal_values": ["backup_and_restore", "pod"],
                            "weight": 2,
                        }
                    ],
                },
            )
            hits = [
                RetrievalHit(
                    chunk_id="manual-hit",
                    book_slug="backup_and_restore",
                    chapter="backup",
                    section="백업 개요",
                    anchor="backup-overview",
                    source_url="https://example.com/backup",
                    viewer_path="/docs/backup.html#backup-overview",
                    text="백업 및 복구 개요",
                    source="bm25",
                    raw_score=1.0,
                    fused_score=1.0,
                    source_collection="core",
                ),
                RetrievalHit(
                    chunk_id="overview-hit",
                    book_slug="overview",
                    chapter="overview",
                    section="개요",
                    anchor="overview",
                    source_url="https://example.com/overview",
                    viewer_path="/docs/overview.html#overview",
                    text="개요 설명",
                    source="bm25",
                    raw_score=0.95,
                    fused_score=0.95,
                    source_collection="core",
                ),
                RetrievalHit(
                    chunk_id="topic-hit",
                    book_slug="backup_restore_control_plane",
                    chapter="backup",
                    section="컨트롤 플레인 백업 절차",
                    anchor="control-plane-backup",
                    source_url="https://example.com/topic",
                    viewer_path="/docs/topic.html#control-plane-backup",
                    text="cluster-backup.sh /home/core/assets/backup",
                    source="vector",
                    raw_score=0.94,
                    fused_score=0.94,
                    source_collection="core",
                    semantic_role="procedure",
                    block_kinds=("code",),
                ),
            ]
            retriever = ChatRetriever(settings, _StubBm25(hits), vector_retriever=None)

            result = retriever.retrieve(
                "컨트롤 플레인 백업 절차",
                top_k=3,
                candidate_k=3,
                use_vector=False,
            )

            ranked_books = [hit.book_slug for hit in result.hits]
            self.assertIn("backup_restore_control_plane", ranked_books[:2])
            self.assertLess(
                ranked_books.index("backup_restore_control_plane"),
                ranked_books.index("overview"),
            )
            topic_hit = next(hit for hit in result.hits if hit.book_slug == "backup_restore_control_plane")
            self.assertGreater(
                topic_hit.component_scores["graph_boost"],
                0.0,
            )
            self.assertIn("derived_from_book", topic_hit.graph_relations)
            self.assertEqual("local_sidecar", result.trace["graph"]["adapter_mode"])

    def test_retrieve_uses_local_graph_runtime_even_without_sidecar_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir), graph_enabled=False)
            hit = RetrievalHit(
                chunk_id="overview-hit",
                book_slug="overview",
                chapter="overview",
                section="개요",
                anchor="overview",
                source_url="https://example.com/overview",
                viewer_path="/docs/overview.html#overview",
                text="개요 설명",
                source="bm25",
                raw_score=1.0,
                fused_score=1.0,
            )
            retriever = ChatRetriever(settings, _StubBm25([hit]), vector_retriever=None)

            result = retriever.retrieve(
                "개요 설명",
                top_k=1,
                candidate_k=1,
                use_vector=False,
            )

            self.assertFalse(result.trace["graph"]["enabled"])
            self.assertFalse(result.trace["graph"]["graph_enabled"])
            self.assertEqual("disabled", result.trace["graph"]["adapter_mode"])
            self.assertEqual(0, result.trace["graph"]["summary"]["hit_count"])


if __name__ == "__main__":
    unittest.main()
