from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.ingestion.collector import raw_html_path
from play_book_studio.ingestion.graph_sidecar import (
    GRAPH_SIDECAR_COMPACT_SCHEMA_VERSION,
    build_graph_sidecar_compact_payload,
    build_graph_sidecar_compact_payload_from_artifacts,
    build_graph_sidecar_payload,
    refresh_active_runtime_graph_artifacts,
)
from play_book_studio.ingestion.models import ChunkRecord, SourceManifestEntry
from play_book_studio.ingestion.pipeline import run_ingestion_pipeline
from play_book_studio.config.settings import Settings


class IngestionGraphSidecarTests(unittest.TestCase):
    def test_build_graph_sidecar_payload_carries_derived_metadata_and_relation_groups(self) -> None:
        chunk_rows = [
            {
                "chunk_id": "chunk-a",
                "book_slug": "backup_restore_control_plane",
                "chapter": "backup",
                "section": "컨트롤 플레인 백업",
                "anchor": "backup",
                "viewer_path": "/docs/ocp/4.20/ko/backup_restore_control_plane/index.html#backup",
                "source_url": "https://example.com/backup",
                "source_collection": "core",
                "source_type": "topic_playbook",
                "source_lane": "applied_playbook",
                "k8s_objects": ["Pod", "MachineConfigPool"],
                "operator_names": ["Machine Config Operator"],
                "error_strings": ["NotReady"],
                "verification_hints": ["oc get mcp"],
            },
            {
                "chunk_id": "chunk-b",
                "book_slug": "backup_restore_control_plane",
                "chapter": "backup",
                "section": "복구 검증",
                "anchor": "verify",
                "viewer_path": "/docs/ocp/4.20/ko/backup_restore_control_plane/index.html#verify",
                "source_url": "https://example.com/backup",
                "source_collection": "core",
                "source_type": "topic_playbook",
                "source_lane": "applied_playbook",
                "k8s_objects": ["Pod"],
                "operator_names": ["Machine Config Operator"],
                "error_strings": ["NotReady"],
                "verification_hints": ["oc get mcp"],
            },
        ]
        playbook_documents = [
            {
                "book_slug": "backup_restore_control_plane",
                "title": "컨트롤 플레인 백업/복구 플레이북",
                "source_uri": "https://example.com/backup",
                "anchor_map": {
                    "backup": "/docs/ocp/4.20/ko/backup_restore_control_plane/index.html#backup"
                },
                "source_metadata": {
                    "source_type": "topic_playbook",
                    "source_lane": "applied_playbook",
                    "source_collection": "core",
                    "derived_from_book_slug": "backup_and_restore",
                    "topic_key": "backup_restore_control_plane",
                },
            }
        ]

        payload = build_graph_sidecar_payload(
            chunk_rows=chunk_rows,
            playbook_documents=playbook_documents,
        )

        self.assertEqual("graph_sidecar_v1", payload["schema_version"])
        self.assertEqual("", payload["app_id"])
        self.assertEqual("", payload["pack_id"])
        self.assertEqual({"app_id": "", "pack_id": ""}, payload["pack_scope"])
        self.assertEqual(1, payload["summary"]["book_count"])
        self.assertEqual(2, payload["summary"]["chunk_count"])
        self.assertEqual(1, payload["summary"]["relation_group_counts"]["shared_k8s_objects"])
        self.assertEqual(1, payload["summary"]["relation_group_counts"]["shared_operator_names"])
        self.assertEqual(1, payload["summary"]["relation_group_counts"]["shared_error_strings"])
        self.assertEqual(1, payload["summary"]["relation_group_counts"]["shared_verification_hints"])
        self.assertEqual({"topic_playbook": 1}, payload["summary"]["source_type_counts"])

        book = payload["books"][0]
        self.assertEqual("backup_and_restore", book["derived_from_book_slug"])
        self.assertEqual("backup_restore_control_plane", book["topic_key"])

        first_chunk = payload["chunks"][0]
        self.assertEqual("topic_playbook", first_chunk["source_type"])
        self.assertEqual("applied_playbook", first_chunk["source_lane"])
        self.assertEqual("core", first_chunk["source_collection"])
        self.assertEqual("backup_and_restore", first_chunk["derived_from_book_slug"])
        self.assertEqual("backup_restore_control_plane", first_chunk["topic_key"])
        self.assertEqual(
            ["chunk-b"],
            first_chunk["relation_groups"]["shared_k8s_objects"][0]["related_chunk_ids"],
        )
        self.assertEqual(
            ["chunk-b"],
            first_chunk["relation_groups"]["shared_operator_names"][0]["related_chunk_ids"],
        )

    def test_run_ingestion_pipeline_writes_graph_sidecar_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root, chunk_size=1000, chunk_overlap=0)
            entry = SourceManifestEntry(
                book_slug="machine_configuration",
                title="머신 구성",
                source_url="https://example.com/machine_configuration",
                viewer_path="/docs/ocp/4.20/ko/machine_configuration/index.html",
                content_status="approved_ko",
                source_fingerprint="fp-machine-configuration",
                source_id="ocp-4.20-ko-machine_configuration",
                source_lane="official_ko",
                source_type="official_doc",
                source_collection="core",
                original_title="Machine configuration",
                review_status="approved",
                trust_score=1.0,
                verifiability="anchor_backed",
            )
            html = """
            <html><body><main id="main-content"><article>
            <h1>머신 구성</h1>
            <h2 id="recover">장애 복구</h2>
            <p>Machine Config Operator 가 NotReady 증상을 진단합니다.</p>
            </article></main></body></html>
            """
            raw_html_path(settings, entry.book_slug).write_text(html, encoding="utf-8")

            fake_chunks = [
                ChunkRecord(
                    chunk_id="machine_configuration:1",
                    book_slug="machine_configuration",
                    book_title="머신 구성",
                    chapter="머신 구성",
                    section="장애 복구",
                    anchor="recover",
                    source_url="https://example.com/machine_configuration",
                    viewer_path="/docs/ocp/4.20/ko/machine_configuration/index.html#recover",
                    text="Machine Config Operator 가 NotReady 증상을 진단합니다.",
                    token_count=10,
                    ordinal=1,
                    section_id="machine_configuration:recover",
                    section_path=("머신 구성", "장애 복구"),
                    chunk_type="procedure",
                    source_id="ocp-4.20-ko-machine_configuration",
                    source_lane="official_ko",
                    source_type="official_doc",
                    source_collection="core",
                    k8s_objects=("Pod",),
                    operator_names=("Machine Config Operator",),
                    error_strings=("NotReady",),
                    verification_hints=("oc get mcp",),
                ),
                ChunkRecord(
                    chunk_id="machine_configuration:2",
                    book_slug="machine_configuration",
                    book_title="머신 구성",
                    chapter="머신 구성",
                    section="장애 복구",
                    anchor="recover",
                    source_url="https://example.com/machine_configuration",
                    viewer_path="/docs/ocp/4.20/ko/machine_configuration/index.html#recover",
                    text="Pod 상태와 Machine Config Operator 로그를 함께 확인합니다.",
                    token_count=10,
                    ordinal=2,
                    section_id="machine_configuration:recover",
                    section_path=("머신 구성", "장애 복구"),
                    chunk_type="reference",
                    source_id="ocp-4.20-ko-machine_configuration",
                    source_lane="official_ko",
                    source_type="official_doc",
                    source_collection="core",
                    k8s_objects=("Pod",),
                    operator_names=("Machine Config Operator",),
                    error_strings=("NotReady",),
                    verification_hints=("oc get mcp",),
                ),
            ]

            with (
                patch(
                    "play_book_studio.ingestion.pipeline.load_runtime_manifest_entries",
                    return_value=[entry],
                ),
                patch(
                    "play_book_studio.ingestion.pipeline.collect_entry",
                    side_effect=lambda item, provided_settings, force=False: raw_html_path(
                        provided_settings,
                        item.book_slug,
                    ),
                ),
                patch(
                    "play_book_studio.ingestion.pipeline.chunk_sections",
                    return_value=fake_chunks,
                ),
            ):
                log = run_ingestion_pipeline(
                    settings,
                    collect_subset="all",
                    process_subset="all",
                    skip_embeddings=True,
                    skip_qdrant=True,
                )

            self.assertEqual(2, log.chunk_count)
            self.assertTrue(settings.graph_sidecar_path.exists())

            payload = json.loads(settings.graph_sidecar_path.read_text(encoding="utf-8"))
            self.assertEqual("graph_sidecar_v1", payload["schema_version"])
            self.assertEqual(settings.app_id, payload["app_id"])
            self.assertEqual(settings.active_pack_id, payload["pack_id"])
            self.assertEqual(
                {"app_id": settings.app_id, "pack_id": settings.active_pack_id},
                payload["pack_scope"],
            )
            self.assertEqual(1, payload["summary"]["book_count"])
            self.assertEqual(2, payload["summary"]["chunk_count"])
            self.assertEqual({"official_doc": 1}, payload["summary"]["source_type_counts"])
            self.assertEqual("official_doc", payload["chunks"][0]["source_type"])
            self.assertEqual("official_ko", payload["chunks"][0]["source_lane"])
            self.assertEqual("core", payload["chunks"][0]["source_collection"])
            self.assertEqual(
                ["machine_configuration:2"],
                payload["chunks"][0]["relation_groups"]["shared_k8s_objects"][0]["related_chunk_ids"],
            )
            self.assertEqual(
                ["machine_configuration:2"],
                payload["chunks"][0]["relation_groups"]["shared_operator_names"][0]["related_chunk_ids"],
            )
            self.assertEqual(
                ["machine_configuration:2"],
                payload["chunks"][0]["relation_groups"]["shared_error_strings"][0]["related_chunk_ids"],
            )
            self.assertEqual(
                ["machine_configuration:2"],
                payload["chunks"][0]["relation_groups"]["shared_verification_hints"][0]["related_chunk_ids"],
            )
            compact_payload = json.loads(settings.graph_sidecar_compact_path.read_text(encoding="utf-8"))
            self.assertEqual(GRAPH_SIDECAR_COMPACT_SCHEMA_VERSION, compact_payload["schema_version"])
            self.assertEqual(1, compact_payload["book_count"])
            self.assertEqual(payload["relation_count"], compact_payload["relation_count"])
            self.assertNotIn("chunks", compact_payload)

    def test_build_graph_sidecar_compact_payload_keeps_books_and_relations_only(self) -> None:
        payload = build_graph_sidecar_payload(
            chunk_rows=[
                {
                    "chunk_id": "chunk-a",
                    "book_slug": "backup_restore_control_plane",
                    "chapter": "backup",
                    "section": "컨트롤 플레인 백업",
                    "anchor": "backup",
                    "viewer_path": "/docs/backup#backup",
                    "source_url": "https://example.com/backup",
                    "source_collection": "core",
                    "source_type": "topic_playbook",
                    "source_lane": "applied_playbook",
                    "operator_names": ["Machine Config Operator"],
                },
                {
                    "chunk_id": "chunk-b",
                    "book_slug": "backup_and_restore",
                    "chapter": "backup",
                    "section": "백업 개요",
                    "anchor": "overview",
                    "viewer_path": "/docs/backup#overview",
                    "source_url": "https://example.com/manual",
                    "source_collection": "core",
                    "source_type": "manual_synthesis",
                    "source_lane": "applied_playbook",
                    "operator_names": ["Machine Config Operator"],
                },
            ],
            playbook_documents=[
                {
                    "book_slug": "backup_restore_control_plane",
                    "title": "컨트롤 플레인 백업/복구 플레이북",
                    "source_uri": "https://example.com/backup",
                    "source_metadata": {
                        "source_type": "topic_playbook",
                        "source_lane": "applied_playbook",
                        "source_collection": "core",
                        "derived_from_book_slug": "backup_and_restore",
                        "topic_key": "backup_restore_control_plane",
                    },
                }
            ],
            graph_backend="neo4j",
            app_id="play-book-studio",
            pack_id="openshift-4-20-core",
        )

        compact_payload = build_graph_sidecar_compact_payload(payload)

        self.assertEqual(GRAPH_SIDECAR_COMPACT_SCHEMA_VERSION, compact_payload["schema_version"])
        self.assertEqual(payload["app_id"], compact_payload["app_id"])
        self.assertEqual(payload["pack_id"], compact_payload["pack_id"])
        self.assertEqual(payload["book_count"], compact_payload["book_count"])
        self.assertEqual(payload["relation_count"], compact_payload["relation_count"])
        self.assertIn("books", compact_payload)
        self.assertIn("relations", compact_payload)
        self.assertNotIn("chunks", compact_payload)

    def test_build_graph_sidecar_compact_payload_from_artifacts_reconstructs_relations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            chunks_path = root / "chunks.jsonl"
            playbook_documents_path = root / "playbook_documents.jsonl"
            playbook_documents_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "book_slug": "backup_restore_control_plane",
                                "title": "컨트롤 플레인 백업/복구 플레이북",
                                "source_uri": "https://example.com/backup",
                                "anchor_map": {
                                    "backup": "/docs/backup_restore_control_plane/index.html#backup"
                                },
                                "source_metadata": {
                                    "source_type": "topic_playbook",
                                    "source_lane": "applied_playbook",
                                    "source_collection": "core",
                                    "derived_from_book_slug": "backup_and_restore",
                                    "topic_key": "backup_restore_control_plane",
                                },
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "book_slug": "backup_and_restore",
                                "title": "백업과 복구",
                                "source_uri": "https://example.com/manual",
                                "anchor_map": {
                                    "overview": "/docs/backup_and_restore/index.html#overview"
                                },
                                "source_metadata": {
                                    "source_type": "manual_synthesis",
                                    "source_lane": "applied_playbook",
                                    "source_collection": "core",
                                },
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            chunks_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "chunk_id": "chunk-a",
                                "book_slug": "backup_restore_control_plane",
                                "book_title": "컨트롤 플레인 백업/복구 플레이북",
                                "viewer_path": "/docs/backup_restore_control_plane/index.html#backup",
                                "source_url": "https://example.com/backup",
                                "operator_names": ["Machine Config Operator"],
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "chunk_id": "chunk-b",
                                "book_slug": "backup_and_restore",
                                "book_title": "백업과 복구",
                                "viewer_path": "/docs/backup_and_restore/index.html#overview",
                                "source_url": "https://example.com/manual",
                                "operator_names": ["Machine Config Operator"],
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            compact_payload = build_graph_sidecar_compact_payload_from_artifacts(
                chunks_path=chunks_path,
                playbook_documents_path=playbook_documents_path,
                graph_backend="local",
                app_id="play-book-studio",
                pack_id="openshift-4-20-core",
            )

        self.assertEqual(GRAPH_SIDECAR_COMPACT_SCHEMA_VERSION, compact_payload["schema_version"])
        self.assertEqual("play-book-studio", compact_payload["app_id"])
        self.assertEqual("openshift-4-20-core", compact_payload["pack_id"])
        self.assertEqual(2, compact_payload["book_count"])
        self.assertEqual(1, compact_payload["relation_count"])
        self.assertEqual({"manual_synthesis": 1, "topic_playbook": 1}, compact_payload["summary"]["source_type_counts"])
        self.assertEqual(1, compact_payload["summary"]["relation_group_counts"]["shared_operator_names"])
        relation = compact_payload["relations"][0]
        self.assertEqual("backup_and_restore", relation["source_book_slug"])
        self.assertEqual("backup_restore_control_plane", relation["target_book_slug"])
        self.assertEqual(
            ["derived_from_book", "shared_operator_names"],
            relation["relation_types"],
        )
        self.assertEqual(2, relation["weight"])
        self.assertNotIn("chunks", compact_payload)

    def test_write_graph_sidecar_exports_to_neo4j_when_backend_is_neo4j(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(
                root_dir=Path(tmpdir),
                graph_backend="neo4j",
                graph_uri="bolt://graph.local:7687",
                graph_username="neo4j",
                graph_password="secret",
            )
            driver = MagicMock()
            session = MagicMock()
            driver.session.return_value.__enter__.return_value = session
            with patch("play_book_studio.ingestion.graph_sidecar.GraphDatabase") as graph_database:
                graph_database.driver.return_value = driver
                payload = build_graph_sidecar_payload(
                    chunk_rows=[
                        {
                            "chunk_id": "chunk-a",
                            "book_slug": "backup_restore_control_plane",
                            "chapter": "backup",
                            "section": "컨트롤 플레인 백업",
                            "anchor": "backup",
                            "viewer_path": "/docs/backup#backup",
                            "source_url": "https://example.com/backup",
                            "source_collection": "core",
                            "source_type": "topic_playbook",
                            "source_lane": "applied_playbook",
                            "operator_names": ["Machine Config Operator"],
                        },
                        {
                            "chunk_id": "chunk-b",
                            "book_slug": "backup_and_restore",
                            "chapter": "backup",
                            "section": "백업 개요",
                            "anchor": "overview",
                            "viewer_path": "/docs/backup#overview",
                            "source_url": "https://example.com/manual",
                            "source_collection": "core",
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                            "operator_names": ["Machine Config Operator"],
                        },
                    ],
                    playbook_documents=[
                        {
                            "book_slug": "backup_restore_control_plane",
                            "title": "컨트롤 플레인 백업/복구 플레이북",
                            "source_uri": "https://example.com/backup",
                            "source_metadata": {
                                "source_type": "topic_playbook",
                                "source_lane": "applied_playbook",
                                "source_collection": "core",
                                "derived_from_book_slug": "backup_and_restore",
                                "topic_key": "backup_restore_control_plane",
                            },
                        }
                    ],
                    graph_backend="neo4j",
                )
                settings.graph_sidecar_path.parent.mkdir(parents=True, exist_ok=True)
                settings.graph_sidecar_path.write_text(
                    json.dumps(payload, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                from play_book_studio.ingestion.graph_sidecar import write_graph_sidecar

                write_graph_sidecar(
                    settings,
                    chunks=[],
                    playbook_documents=[],
                )

            graph_database.driver.assert_called_once_with(
                "bolt://graph.local:7687",
                auth=("neo4j", "secret"),
            )
            compact_payload = json.loads(settings.graph_sidecar_compact_path.read_text(encoding="utf-8"))
            self.assertEqual(GRAPH_SIDECAR_COMPACT_SCHEMA_VERSION, compact_payload["schema_version"])
            self.assertGreaterEqual(session.run.call_count, 3)
            delete_call = session.run.call_args_list[2]
            self.assertEqual("play-book-studio", delete_call.kwargs["app_id"])
            self.assertEqual("openshift-4-20-core", delete_call.kwargs["pack_id"])

    def test_refresh_active_runtime_graph_artifacts_full_refresh_writes_full_and_compact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
            settings.chunks_path.parent.mkdir(parents=True, exist_ok=True)
            settings.playbook_documents_path.write_text(
                json.dumps(
                    {
                        "book_slug": "monitoring",
                        "title": "모니터링 운영 플레이북",
                        "source_uri": "https://example.com/monitoring",
                        "anchor_map": {
                            "overview": "/docs/ocp/4.20/ko/monitoring/index.html#overview"
                        },
                        "source_metadata": {
                            "source_id": "manual_synthesis:monitoring",
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                            "source_collection": "core",
                        },
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            settings.chunks_path.write_text(
                json.dumps(
                    {
                        "chunk_id": "monitoring:overview",
                        "book_slug": "monitoring",
                        "book_title": "모니터링 운영 플레이북",
                        "chapter": "모니터링",
                        "section": "개요",
                        "anchor": "overview",
                        "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html#overview",
                        "source_url": "https://example.com/monitoring",
                        "text": "Cluster Monitoring Operator overview",
                        "token_count": 8,
                        "ordinal": 1,
                        "section_id": "monitoring:overview",
                        "section_path": ["모니터링", "개요"],
                        "chunk_type": "concept",
                        "source_id": "manual_synthesis:monitoring",
                        "source_lane": "applied_playbook",
                        "source_type": "manual_synthesis",
                        "source_collection": "core",
                        "product": "openshift",
                        "version": "4.20",
                        "locale": "ko",
                        "translation_status": "approved_ko",
                        "review_status": "approved",
                        "trust_score": 0.98,
                        "semantic_role": "concept",
                        "cli_commands": [],
                        "error_strings": [],
                        "k8s_objects": [],
                        "operator_names": ["Cluster Monitoring Operator"],
                        "verification_hints": [],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            refresh = refresh_active_runtime_graph_artifacts(
                settings,
                refresh_full_sidecar=True,
            )

            self.assertEqual("ok", refresh["status"])
            self.assertEqual("ok", refresh["full_sidecar"]["status"])
            self.assertTrue(settings.graph_sidecar_path.exists())
            self.assertTrue(settings.graph_sidecar_compact_path.exists())
            compact_payload = json.loads(settings.graph_sidecar_compact_path.read_text(encoding="utf-8"))
            self.assertEqual(GRAPH_SIDECAR_COMPACT_SCHEMA_VERSION, compact_payload["schema_version"])

    def test_refresh_active_runtime_graph_artifacts_allows_compact_degrade_for_incremental_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            with patch(
                "play_book_studio.ingestion.graph_sidecar.write_graph_sidecar_compact_from_artifacts",
                side_effect=RuntimeError("compact boom"),
            ):
                refresh = refresh_active_runtime_graph_artifacts(
                    settings,
                    refresh_full_sidecar=False,
                    allow_compact_degrade=True,
                )

            self.assertEqual("degraded", refresh["status"])
            self.assertEqual(
                "playbook_documents_runtime_fallback",
                refresh["compact_sidecar"]["degrade_mode"],
            )

    def test_active_runtime_writer_paths_are_sealed_by_graph_refresh_contract(self) -> None:
        ingestion_dir = ROOT / "src" / "play_book_studio" / "ingestion"
        candidate_files = [
            path
            for path in ingestion_dir.glob("*.py")
            if path.name != "graph_sidecar.py"
        ]
        writer_markers = (
            "_write_jsonl(",
            "_write_jsonl_rows(",
            "write_playbook_documents(",
            "_upsert_playbook_payload_for_slug(",
            "_write_playbook_payloads(",
        )
        discovered = {
            path.name
            for path in candidate_files
            if (
                any(marker in path.read_text(encoding="utf-8") for marker in writer_markers)
                and (
                    "settings.chunks_path" in path.read_text(encoding="utf-8")
                    or "settings.playbook_documents_path" in path.read_text(encoding="utf-8")
                )
            )
        }
        expected = {
            "curated_gold.py",
            "pipeline.py",
            "runtime_catalog_library.py",
            "topic_playbooks.py",
            "translation_gold_promotion.py",
        }

        self.assertEqual(expected, discovered)
        for filename in expected:
            source = (ingestion_dir / filename).read_text(encoding="utf-8")
            self.assertIn("refresh_active_runtime_graph_artifacts(", source, filename)
        self.assertNotIn(
            "write_graph_sidecar(",
            (ingestion_dir / "pipeline.py").read_text(encoding="utf-8"),
        )
        self.assertNotIn(
            "write_graph_sidecar(",
            (ingestion_dir / "runtime_catalog_library.py").read_text(encoding="utf-8"),
        )
        self.assertNotIn(
            "write_graph_sidecar_compact_from_artifacts(",
            (ingestion_dir / "translation_gold_promotion.py").read_text(encoding="utf-8"),
        )
        self.assertNotIn(
            "write_graph_sidecar_compact_from_artifacts(",
            (ingestion_dir / "curated_gold.py").read_text(encoding="utf-8"),
        )
        self.assertNotIn(
            "write_graph_sidecar_compact_from_artifacts(",
            (ingestion_dir / "topic_playbooks.py").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
