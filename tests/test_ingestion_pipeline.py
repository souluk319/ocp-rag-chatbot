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
    def test_run_ingestion_pipeline_writes_foundry_outputs_and_legacy_mirrors(self) -> None:
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
                review_status="approved",
                trust_score=1.0,
                verifiability="anchor_backed",
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
            self.assertTrue((settings.playbook_books_dir / "machine_configuration.json").exists())
            self.assertTrue(settings.legacy_normalized_docs_path.exists())
            self.assertTrue(settings.legacy_chunks_path.exists())
            self.assertTrue(settings.legacy_bm25_corpus_path.exists())
            self.assertTrue(settings.legacy_playbook_documents_path.exists())
            self.assertTrue((settings.legacy_playbook_books_dir / "machine_configuration.json").exists())

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

            chunk_row = _read_jsonl(settings.chunks_path)[0]
            self.assertEqual(["oc get pods -n openshift-machine-config-operator"], chunk_row["cli_commands"])
            self.assertEqual(["Machine Config Operator"], chunk_row["operator_names"])
            self.assertEqual("https://example.com/legal", chunk_row["legal_notice_url"])
            self.assertEqual("approved", chunk_row["review_status"])

            bm25_row = _read_jsonl(settings.bm25_corpus_path)[0]
            self.assertEqual("official_doc", bm25_row["source_type"])
            self.assertEqual("core", bm25_row["source_collection"])
            self.assertEqual(["NotReady", "ImagePullBackOff"], bm25_row["error_strings"])
            self.assertEqual(["Machine Config Operator"], bm25_row["operator_names"])

            playbook_row = _read_jsonl(settings.playbook_documents_path)[0]
            self.assertEqual("https://example.com/legal", playbook_row["legal_notice_url"])
            self.assertEqual("approved", playbook_row["review_status"])
            self.assertEqual("official_ko", playbook_row["source_metadata"]["source_lane"])
            self.assertEqual(
                "/docs/ocp/4.20/ko/machine_configuration/index.html#recover",
                playbook_row["anchor_map"]["recover"],
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


if __name__ == "__main__":
    unittest.main()
