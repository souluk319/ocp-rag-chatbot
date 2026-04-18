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

from play_book_studio.app.intake_api import ingest_customer_pack
from play_book_studio.config.settings import load_settings
from play_book_studio.intake import CustomerPackDraftStore, DocSourceRequest
from play_book_studio.intake.private_corpus import (
    customer_pack_private_bm25_path,
    customer_pack_private_chunks_path,
    customer_pack_private_manifest_path,
    customer_pack_private_vector_path,
    materialize_customer_pack_private_corpus,
)


def _customer_pack_record(root: Path):
    store = CustomerPackDraftStore(root)
    record = store.create(
        DocSourceRequest(
            source_type="md",
            uri=str(root / "runbook.md"),
            title="Private Runbook",
        )
    )
    record.tenant_id = "tenant-a"
    record.workspace_id = "workspace-a"
    record.access_groups = ("workspace-a", "tenant-a")
    record.approval_state = "approved"
    record.publication_state = "draft"
    return record


class PrivateCorpusMaterializationTests(unittest.TestCase):
    def test_materialize_private_corpus_writes_empty_artifacts_when_chunking_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            record = _customer_pack_record(root)
            settings = load_settings(root)
            chunk_path = customer_pack_private_chunks_path(settings, record.draft_id)
            bm25_path = customer_pack_private_bm25_path(settings, record.draft_id)
            vector_path = customer_pack_private_vector_path(settings, record.draft_id)
            chunk_path.parent.mkdir(parents=True, exist_ok=True)
            chunk_path.write_text('{"stale": true}\n', encoding="utf-8")
            bm25_path.write_text('{"stale": true}\n', encoding="utf-8")
            vector_path.write_text('{"stale": true}\n', encoding="utf-8")

            with patch(
                "play_book_studio.intake.private_corpus.chunk_sections",
                side_effect=ValueError("chunk-tokenizer-offline"),
            ):
                manifest = materialize_customer_pack_private_corpus(
                    root,
                    record=record,
                    canonical_payload={
                        "book_slug": "private-runbook",
                        "title": "Private Runbook",
                        "sections": [
                            {
                                "section_key": "configmap-secret",
                                "heading": "ConfigMap Secret",
                                "section_level": 2,
                                "section_path": ["Private Runbook", "ConfigMap Secret"],
                                "anchor": "configmap-secret",
                                "viewer_path": f"/playbooks/customer-packs/{record.draft_id}/index.html#configmap-secret",
                                "source_url": "/api/customer-packs/captured",
                                "text": "ConfigMap Secret values must be synchronized before rollout.",
                            }
                        ],
                    },
                    derived_payloads=[],
                )

            self.assertEqual("failed", manifest["materialization_status"])
            self.assertIn("chunk-tokenizer-offline", manifest["materialization_error"])
            self.assertEqual(0, manifest["chunk_count"])
            self.assertFalse(manifest["bm25_ready"])
            self.assertEqual("skipped", manifest["vector_status"])
            self.assertEqual("private_customer_pack_runtime", manifest["boundary_truth"])
            self.assertEqual("tenant-a", manifest["tenant_id"])
            self.assertTrue(chunk_path.exists())
            self.assertTrue(bm25_path.exists())
            self.assertEqual("", chunk_path.read_text(encoding="utf-8"))
            self.assertEqual("", bm25_path.read_text(encoding="utf-8"))
            self.assertFalse(vector_path.exists())

            manifest_path = customer_pack_private_manifest_path(settings, record.draft_id)
            stored_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual("failed", stored_manifest["materialization_status"])

    def test_ingest_customer_pack_keeps_normalized_status_when_private_chunking_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_md = root / "runbook.md"
            source_md.write_text(
                "# Private Runbook\n\n## ConfigMap Secret\n\nConfigMap Secret values must be synchronized before rollout.\n",
                encoding="utf-8",
            )

            with patch(
                "play_book_studio.intake.private_corpus.chunk_sections",
                side_effect=ValueError("chunk-tokenizer-offline"),
            ):
                normalized = ingest_customer_pack(
                    root,
                    {
                        "source_type": "md",
                        "uri": str(source_md),
                        "title": "Private Runbook",
                        "tenant_id": "tenant-a",
                        "workspace_id": "workspace-a",
                        "approval_state": "approved",
                        "publication_state": "draft",
                    },
                )

            self.assertEqual("normalized", normalized["status"])
            self.assertEqual("", normalized["normalize_error"])
            self.assertEqual("failed", normalized["private_corpus_status"])
            self.assertTrue(Path(str(normalized["canonical_book_path"])).exists())
            self.assertIn("book", normalized)
            self.assertIn("private_corpus", normalized)
            private_corpus = normalized["private_corpus"]
            self.assertEqual(0, private_corpus["chunk_count"])
            self.assertFalse(private_corpus["bm25_ready"])
            self.assertEqual("skipped", private_corpus["vector_status"])

            settings = load_settings(root)
            manifest_path = customer_pack_private_manifest_path(settings, str(normalized["draft_id"]))
            self.assertTrue(manifest_path.exists())
            stored_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual("failed", stored_manifest["materialization_status"])


if __name__ == "__main__":
    unittest.main()
