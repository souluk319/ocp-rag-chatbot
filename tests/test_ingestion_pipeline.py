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

from play_book_studio.config.settings import Settings
from play_book_studio.ingestion import chunking
from play_book_studio.ingestion.collector import raw_html_path
from play_book_studio.ingestion.models import SourceManifestEntry
from play_book_studio.ingestion.pipeline import run_ingestion_pipeline


class _FakeTokenizer:
    def __init__(self) -> None:
        self.model_max_length = 32

    def __call__(self, text: str, **_: object) -> dict[str, list[int]]:
        return {"input_ids": [ord(char) for char in text]}


class _FakeSentenceModel:
    def __init__(self) -> None:
        self.tokenizer = _FakeTokenizer()


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class IngestionPipelineTests(unittest.TestCase):
    def test_run_ingestion_pipeline_writes_foundry_outputs_to_canonical_paths(self) -> None:
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
                legal_notice_url="https://example.com/legal",
                license_or_terms="OpenShift documentation is licensed under the Apache License 2.0.",
                review_status="approved",
                trust_score=1.0,
                verifiability="anchor_backed",
                updated_at="2026-04-10T00:00:00Z",
            )
            html = """
            <html>
              <body>
                <main id="main-content">
                  <article>
                    <h1>머신 구성</h1>
                    <h2 id="recover">장애 복구</h2>
                    <p>Machine Config Operator 가 NotReady Pod 와 ImagePullBackOff 증상을 진단합니다.</p>
                    <p>검증: oc get pods -n openshift-machine-config-operator</p>
                    <pre><code>oc get pods -n openshift-machine-config-operator</code></pre>
                    <p>Deployment 와 MachineConfigPool 상태를 점검합니다.</p>
                  </article>
                </main>
              </body>
            </html>
            """
            raw_html_path(settings, entry.book_slug).write_text(html, encoding="utf-8")

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
                patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()),
            ):
                log = run_ingestion_pipeline(
                    settings,
                    collect_subset="all",
                    process_subset="all",
                    skip_embeddings=True,
                    skip_qdrant=True,
                )

            self.assertEqual(1, log.normalized_count)
            self.assertEqual(1, log.chunk_count)
            self.assertTrue(settings.normalized_docs_path.exists())
            self.assertTrue(settings.chunks_path.exists())
            self.assertTrue(settings.bm25_corpus_path.exists())
            self.assertTrue(settings.playbook_documents_path.exists())
            self.assertTrue(settings.graph_sidecar_path.exists())
            self.assertTrue((settings.playbook_books_dir / "machine_configuration.json").exists())

            normalized_row = _read_jsonl(settings.normalized_docs_path)[0]
            self.assertEqual("ocp-4.20-ko-machine_configuration", normalized_row["source_id"])
            self.assertEqual("official_ko", normalized_row["source_lane"])
            self.assertEqual("Machine configuration", normalized_row["original_title"])
            self.assertEqual(["NotReady", "ImagePullBackOff"], normalized_row["error_strings"])
            self.assertEqual(
                ["Pod", "Deployment", "MachineConfigPool"],
                normalized_row["k8s_objects"],
            )
            self.assertEqual(
                [
                    "검증: oc get pods -n openshift-machine-config-operator",
                    "oc get pods -n openshift-machine-config-operator",
                ],
                normalized_row["verification_hints"],
            )
            self.assertEqual("parsed:ocp-4.20-ko-machine_configuration", normalized_row["parsed_artifact_id"])
            self.assertEqual("public", normalized_row["tenant_id"])
            self.assertEqual(["public"], normalized_row["access_groups"])

            chunk_row = _read_jsonl(settings.chunks_path)[0]
            self.assertEqual(["oc get pods -n openshift-machine-config-operator"], chunk_row["cli_commands"])
            self.assertEqual(["Machine Config Operator"], chunk_row["operator_names"])
            self.assertEqual("https://example.com/legal", chunk_row["legal_notice_url"])
            self.assertEqual("approved", chunk_row["review_status"])
            self.assertEqual("parsed:ocp-4.20-ko-machine_configuration", chunk_row["parsed_artifact_id"])
            self.assertEqual("public", chunk_row["classification"])

            bm25_row = _read_jsonl(settings.bm25_corpus_path)[0]
            self.assertEqual("official_doc", bm25_row["source_type"])
            self.assertEqual("core", bm25_row["source_collection"])
            self.assertEqual(["NotReady", "ImagePullBackOff"], bm25_row["error_strings"])
            self.assertEqual(["Machine Config Operator"], bm25_row["operator_names"])

            playbook_row = _read_jsonl(settings.playbook_documents_path)[0]
            self.assertEqual("https://example.com/legal", playbook_row["legal_notice_url"])
            self.assertEqual("approved", playbook_row["review_status"])
            self.assertEqual(
                "ocp-4.20-ko-machine_configuration",
                playbook_row["source_metadata"]["source_id"],
            )
            self.assertEqual("official_ko", playbook_row["source_metadata"]["source_lane"])
            self.assertEqual(
                "https://example.com/legal",
                playbook_row["source_metadata"]["legal_notice_url"],
            )
            self.assertEqual(
                "OpenShift documentation is licensed under the Apache License 2.0.",
                playbook_row["source_metadata"]["license_or_terms"],
            )
            self.assertEqual(
                "2026-04-10T00:00:00Z",
                playbook_row["source_metadata"]["updated_at"],
            )
            self.assertEqual(
                "parsed:ocp-4.20-ko-machine_configuration",
                playbook_row["source_metadata"]["parsed_artifact_id"],
            )
            self.assertEqual("public", playbook_row["source_metadata"]["tenant_id"])
            self.assertEqual(
                "/docs/ocp/4.20/ko/machine_configuration/index.html#recover",
                playbook_row["anchor_map"]["recover"],
            )
            graph_payload = json.loads(settings.graph_sidecar_path.read_text(encoding="utf-8"))
            self.assertEqual("graph_sidecar_v1", graph_payload["schema"])
            self.assertEqual("graph_sidecar_v1", graph_payload["schema_version"])
            self.assertEqual(settings.app_id, graph_payload["app_id"])
            self.assertEqual(settings.active_pack_id, graph_payload["pack_id"])
            self.assertEqual(
                {"app_id": settings.app_id, "pack_id": settings.active_pack_id},
                graph_payload["pack_scope"],
            )
            self.assertEqual(1, graph_payload["book_count"])
            self.assertEqual(1, graph_payload["summary"]["book_count"])
            self.assertEqual(1, graph_payload["summary"]["chunk_count"])
            self.assertEqual(0, graph_payload["relation_count"])
            self.assertEqual(
                "machine_configuration",
                graph_payload["books"][0]["book_slug"],
            )

    def test_run_ingestion_pipeline_downgrades_fallback_book_to_needs_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root, chunk_size=1000, chunk_overlap=0)
            entry = SourceManifestEntry(
                book_slug="backup_and_restore",
                title="Backup and restore",
                source_url="https://example.com/backup_and_restore",
                viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html",
                content_status="unknown",
                review_status="unreviewed",
                source_fingerprint="fp-backup-and-restore",
                source_type="official_doc",
                source_lane="",
            )
            html = """
            <html>
              <body>
                <main id="main-content">
                  <article>
                    <p>This content is not available in the selected language.</p>
                    <h1>Backup and restore</h1>
                    <h2 id="overview">Overview</h2>
                    <p>Use OADP to back up applications and restore namespaces.</p>
                  </article>
                </main>
              </body>
            </html>
            """
            raw_html_path(settings, entry.book_slug).write_text(html, encoding="utf-8")

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
                patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()),
            ):
                log = run_ingestion_pipeline(
                    settings,
                    collect_subset="all",
                    process_subset="all",
                    skip_embeddings=True,
                    skip_qdrant=True,
                )

            self.assertEqual("en_only", log.per_book_stats[0]["content_status"])
            self.assertEqual("official_en_fallback", log.per_book_stats[0]["source_lane"])
            self.assertEqual("needs_review", log.per_book_stats[0]["review_status"])

            normalized_row = _read_jsonl(settings.normalized_docs_path)[0]
            self.assertEqual("official_en_fallback", normalized_row["source_lane"])
            self.assertEqual("needs_review", normalized_row["review_status"])

    def test_run_ingestion_pipeline_assigns_applied_playbook_lane_for_community_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root, chunk_size=1000, chunk_overlap=0)
            entry = SourceManifestEntry(
                book_slug="community_restore_runbook",
                title="커뮤니티 복구 런북",
                source_url="https://example.com/community_restore_runbook",
                viewer_path="/docs/community/restore.html",
                content_status="unknown",
                review_status="unreviewed",
                source_fingerprint="fp-community-restore",
                source_type="community_issue",
                source_lane="",
            )
            html = """
            <html>
              <body>
                <main id="main-content">
                  <article>
                    <h1>커뮤니티 복구 런북</h1>
                    <h2 id="verify">검증</h2>
                    <p>Pod 재기동 이후 Route 상태를 확인합니다.</p>
                    <pre><code>oc get pods -A</code></pre>
                  </article>
                </main>
              </body>
            </html>
            """
            raw_html_path(settings, entry.book_slug).write_text(html, encoding="utf-8")

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
                patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()),
            ):
                log = run_ingestion_pipeline(
                    settings,
                    collect_subset="all",
                    process_subset="all",
                    skip_embeddings=True,
                    skip_qdrant=True,
                )

            self.assertEqual("approved_ko", log.per_book_stats[0]["content_status"])
            self.assertEqual("applied_playbook", log.per_book_stats[0]["source_lane"])
            self.assertEqual("approved", log.per_book_stats[0]["review_status"])

            normalized_row = _read_jsonl(settings.normalized_docs_path)[0]
            self.assertEqual("applied_playbook", normalized_row["source_lane"])
            self.assertEqual("approved", normalized_row["review_status"])

    def test_run_ingestion_pipeline_prunes_stale_canonical_playbook_book_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root, chunk_size=1000, chunk_overlap=0)
            machine_entry = SourceManifestEntry(
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
                legal_notice_url="https://example.com/legal",
                review_status="approved",
                trust_score=1.0,
                verifiability="anchor_backed",
            )
            backup_entry = SourceManifestEntry(
                book_slug="backup_and_restore",
                title="백업 및 복구",
                source_url="https://example.com/backup_and_restore",
                viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html",
                content_status="approved_ko",
                source_fingerprint="fp-backup-and-restore",
                source_id="ocp-4.20-ko-backup_and_restore",
                source_lane="official_ko",
                source_type="official_doc",
                source_collection="core",
                original_title="Backup and restore",
                legal_notice_url="https://example.com/legal",
                review_status="approved",
                trust_score=1.0,
                verifiability="anchor_backed",
            )
            html_map = {
                "machine_configuration": """
                <html><body><main id="main-content"><article>
                <h1>머신 구성</h1><h2 id="recover">장애 복구</h2><p>머신 설정을 점검합니다.</p>
                </article></main></body></html>
                """,
                "backup_and_restore": """
                <html><body><main id="main-content"><article>
                <h1>백업 및 복구</h1><h2 id="overview">개요</h2><p>백업 절차를 점검합니다.</p>
                </article></main></body></html>
                """,
            }
            for slug, html in html_map.items():
                raw_html_path(settings, slug).write_text(html, encoding="utf-8")

            with (
                patch(
                    "play_book_studio.ingestion.pipeline.load_runtime_manifest_entries",
                    return_value=[machine_entry, backup_entry],
                ),
                patch(
                    "play_book_studio.ingestion.pipeline.collect_entry",
                    side_effect=lambda item, provided_settings, force=False: raw_html_path(
                        provided_settings,
                        item.book_slug,
                    ),
                ),
                patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()),
            ):
                run_ingestion_pipeline(
                    settings,
                    collect_subset="all",
                    process_subset="all",
                    skip_embeddings=True,
                    skip_qdrant=True,
                )

            self.assertTrue((settings.playbook_books_dir / "machine_configuration.json").exists())
            self.assertTrue((settings.playbook_books_dir / "backup_and_restore.json").exists())
            self.assertTrue((settings.playbook_books_dir / "machine_configuration.json").exists())
            self.assertTrue((settings.playbook_books_dir / "backup_and_restore.json").exists())

            with (
                patch(
                    "play_book_studio.ingestion.pipeline.load_runtime_manifest_entries",
                    return_value=[machine_entry],
                ),
                patch(
                    "play_book_studio.ingestion.pipeline.collect_entry",
                    side_effect=lambda item, provided_settings, force=False: raw_html_path(
                        provided_settings,
                        item.book_slug,
                    ),
                ),
                patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()),
            ):
                run_ingestion_pipeline(
                    settings,
                    collect_subset="all",
                    process_subset="all",
                    skip_embeddings=True,
                    skip_qdrant=True,
                )

            self.assertTrue((settings.playbook_books_dir / "machine_configuration.json").exists())
            self.assertFalse((settings.playbook_books_dir / "backup_and_restore.json").exists())
            self.assertTrue((settings.playbook_books_dir / "machine_configuration.json").exists())
            self.assertFalse((settings.playbook_books_dir / "backup_and_restore.json").exists())
            playbook_rows = _read_jsonl(settings.playbook_documents_path)
            self.assertEqual(["machine_configuration"], [row["book_slug"] for row in playbook_rows])

    def test_run_ingestion_pipeline_builds_graph_sidecar_relations_for_shared_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root, chunk_size=1000, chunk_overlap=0)
            entries = [
                SourceManifestEntry(
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
                    review_status="approved",
                    trust_score=1.0,
                    verifiability="anchor_backed",
                ),
                SourceManifestEntry(
                    book_slug="nodes",
                    title="노드",
                    source_url="https://example.com/nodes",
                    viewer_path="/docs/ocp/4.20/ko/nodes/index.html",
                    content_status="approved_ko",
                    source_fingerprint="fp-nodes",
                    source_id="ocp-4.20-ko-nodes",
                    source_lane="official_ko",
                    source_type="official_doc",
                    source_collection="core",
                    review_status="approved",
                    trust_score=1.0,
                    verifiability="anchor_backed",
                ),
            ]
            html_map = {
                "machine_configuration": """
                <html><body><main id="main-content"><article>
                <h1>머신 구성</h1>
                <h2 id="recover">장애 복구</h2>
                <p>Machine Config Operator Pod 상태를 점검합니다.</p>
                <pre><code>oc get pods -n openshift-machine-config-operator</code></pre>
                </article></main></body></html>
                """,
                "nodes": """
                <html><body><main id="main-content"><article>
                <h1>노드</h1>
                <h2 id="ops">노드 점검</h2>
                <p>Machine Config Operator Pod 로그를 검토합니다.</p>
                <pre><code>oc logs -n openshift-machine-config-operator deploy/machine-config-operator</code></pre>
                </article></main></body></html>
                """,
            }
            for slug, html in html_map.items():
                raw_html_path(settings, slug).write_text(html, encoding="utf-8")

            with (
                patch(
                    "play_book_studio.ingestion.pipeline.load_runtime_manifest_entries",
                    return_value=entries,
                ),
                patch(
                    "play_book_studio.ingestion.pipeline.collect_entry",
                    side_effect=lambda item, provided_settings, force=False: raw_html_path(
                        provided_settings,
                        item.book_slug,
                    ),
                ),
                patch.object(chunking, "load_sentence_model", return_value=_FakeSentenceModel()),
            ):
                log = run_ingestion_pipeline(
                    settings,
                    collect_subset="all",
                    process_subset="all",
                    skip_embeddings=True,
                    skip_qdrant=True,
                )

            graph_payload = json.loads(settings.graph_sidecar_path.read_text(encoding="utf-8"))
            self.assertEqual(2, log.graph_book_count)
            self.assertGreaterEqual(log.graph_relation_count, 1)
            self.assertEqual(2, graph_payload["book_count"])
            self.assertGreaterEqual(graph_payload["relation_count"], 1)
            relation_types = {
                relation_type
                for relation in graph_payload["relations"]
                for relation_type in relation["relation_types"]
            }
            self.assertIn("shared_operator_names", relation_types)
            self.assertIn("shared_k8s_objects", relation_types)


if __name__ == "__main__":
    unittest.main()
