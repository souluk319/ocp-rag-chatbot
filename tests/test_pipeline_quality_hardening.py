from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
SRC = ROOT / "src"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from _support_app_ui import _customer_pack_meta_for_viewer_path, _ingest_customer_pack
from play_book_studio.app.customer_pack_read_boundary import sanitize_customer_pack_draft_payload
from play_book_studio.config.settings import load_settings
from play_book_studio.intake.private_corpus import customer_pack_private_manifest_path
from scripts.build_pipeline_quality_outlier_report import build_reports


class PipelineQualityHardeningTests(unittest.TestCase):
    def test_private_corpus_build_failure_does_not_fail_normalize(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_md = root / "runbook.md"
            source_md.write_text(
                "# 운영 런북\n\n## ConfigMap Secret\n\nConfigMap Secret values must be synchronized before rollout.\n",
                encoding="utf-8",
            )
            with patch(
                "play_book_studio.intake.private_corpus.build_customer_pack_private_corpus_rows",
                side_effect=ValueError("simulated_private_corpus_build_failure"),
            ):
                normalized = _ingest_customer_pack(
                    root,
                    {
                        "source_type": "md",
                        "uri": str(source_md),
                        "title": "운영 런북",
                        "tenant_id": "tenant-a",
                        "workspace_id": "workspace-a",
                        "approval_state": "approved",
                        "publication_state": "draft",
                    },
                )
            manifest_path = customer_pack_private_manifest_path(
                load_settings(root),
                str(normalized["draft_id"]),
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual("normalized", normalized["status"])
            self.assertEqual("", normalized["normalize_error"])
            self.assertEqual("failed", normalized["private_corpus_status"])
            self.assertTrue(Path(str(normalized["canonical_book_path"])).exists())
            self.assertTrue(manifest_path.exists())
            self.assertEqual("failed", manifest["materialization_status"])
            self.assertEqual("simulated_private_corpus_build_failure", manifest["materialization_error"])
            self.assertFalse(manifest["bm25_ready"])
            self.assertEqual("materialization_failed", manifest["vector_status"])

    def test_customer_pack_meta_hides_internal_only_evidence_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "customer_packs" / "drafts"
            book_dir = root / "artifacts" / "customer_packs" / "books"
            draft_dir.mkdir(parents=True)
            book_dir.mkdir(parents=True)

            (draft_dir / "dtb-review.json").write_text(
                json.dumps(
                    {
                        "draft_id": "dtb-review",
                        "status": "normalized",
                        "created_at": "2026-04-06T00:00:00Z",
                        "updated_at": "2026-04-06T00:00:00Z",
                        "request": {
                            "source_type": "pdf",
                            "uri": "/tmp/demo.pdf",
                            "title": "데모 PDF",
                            "language_hint": "ko",
                        },
                        "plan": {
                            "book_slug": "demo-pdf",
                            "title": "데모 PDF",
                            "source_type": "pdf",
                            "source_uri": "/tmp/demo.pdf",
                            "source_collection": "uploaded",
                            "pack_id": "openshift-4-16-custom",
                            "pack_label": "OpenShift 4.16 Custom Pack",
                            "inferred_product": "openshift",
                            "inferred_version": "4.16",
                            "acquisition_uri": "/tmp/demo.pdf",
                            "capture_strategy": "pdf_text_extract_v1",
                            "acquisition_step": "capture",
                            "normalization_step": "normalize",
                            "derivation_step": "derive",
                            "notes": [],
                            "canonical_model": "canonical_book_v1",
                            "source_view_strategy": "source_view_first",
                            "retrieval_derivation": "chunks_from_canonical_sections",
                        },
                        "capture_artifact_path": "/tmp/demo.pdf",
                        "capture_content_type": "application/pdf",
                        "capture_byte_size": 12,
                        "parser_backend": "customer_pack_normalize_service",
                        "degraded_pdf": True,
                        "degraded_reason": "too_many_heading_only_sections",
                        "fallback_used": False,
                        "fallback_backend": "surya",
                        "fallback_status": "backend_unavailable",
                        "fallback_reason": "surya_adapter_unavailable",
                        "capture_error": "",
                        "canonical_book_path": str(book_dir / "dtb-review.json"),
                        "normalized_section_count": 3,
                        "normalize_error": "",
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )
            (book_dir / "dtb-review.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "canonical_book_v1",
                        "book_slug": "demo-pdf",
                        "title": "데모 PDF",
                        "source_type": "pdf",
                        "source_uri": "/tmp/demo.pdf",
                        "language_hint": "ko",
                        "source_view_strategy": "normalized_sections_v1",
                        "retrieval_derivation": "chunks_from_canonical_sections",
                        "sections": [
                            {
                                "ordinal": 1,
                                "section_key": "demo-pdf:short-a",
                                "heading": "온프레미스",
                                "section_level": 1,
                                "section_path": ["Page 1", "온프레미스"],
                                "section_path_label": "Page 1 > 온프레미스",
                                "anchor": "short-a",
                                "viewer_path": "/playbooks/customer-packs/dtb-review/index.html#short-a",
                                "source_url": "/tmp/demo.pdf",
                                "text": "온프레미스",
                                "block_kinds": ["paragraph"],
                                "quality_status": "review",
                                "quality_summary": "정규화 품질 검토가 필요합니다.",
                            },
                        ],
                        "quality_status": "review",
                        "quality_score": 41,
                        "quality_summary": "정규화 품질 검토가 필요합니다.",
                        "quality_flags": ["too_many_heading_only_sections"],
                        "notes": [],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            meta = _customer_pack_meta_for_viewer_path(root, "/playbooks/customer-packs/dtb-review/index.html#short-a")

        self.assertIsNotNone(meta)
        assert meta is not None
        self.assertEqual("review", meta["quality_status"])
        self.assertIn("정규화 품질 검토", meta["quality_summary"])
        self.assertEqual("customer_pack_normalize_service", meta["parser_backend"])
        self.assertFalse(meta["fallback_used"])
        self.assertNotIn("quality_score", meta)
        self.assertNotIn("quality_flags", meta)
        self.assertNotIn("degraded_pdf", meta)
        self.assertNotIn("degraded_reason", meta)
        self.assertNotIn("fallback_backend", meta)
        self.assertNotIn("fallback_status", meta)
        self.assertNotIn("fallback_reason", meta)

    def test_sanitize_customer_pack_draft_payload_drops_forensic_quality_fields(self) -> None:
        sanitized = sanitize_customer_pack_draft_payload(
            {
                "draft_id": "dtb-review",
                "capture_artifact_path": "/tmp/demo.pdf",
                "parser_backend": "customer_pack_normalize_service",
                "quality_status": "review",
                "quality_score": 41,
                "quality_flags": ["too_many_heading_only_sections"],
                "degraded_pdf": True,
                "degraded_reason": "too_many_heading_only_sections",
                "fallback_used": False,
                "fallback_backend": "surya",
                "fallback_status": "backend_unavailable",
                "fallback_reason": "surya_adapter_unavailable",
            }
        )

        self.assertIn("parser_backend", sanitized)
        self.assertIn("quality_status", sanitized)
        self.assertIn("fallback_used", sanitized)
        self.assertNotIn("quality_score", sanitized)
        self.assertNotIn("quality_flags", sanitized)
        self.assertNotIn("degraded_pdf", sanitized)
        self.assertNotIn("degraded_reason", sanitized)
        self.assertNotIn("fallback_backend", sanitized)
        self.assertNotIn("fallback_status", sanitized)
        self.assertNotIn("fallback_reason", sanitized)

    def test_build_pipeline_quality_outlier_report_identifies_active_outliers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "outliers.json"
            checklist_path = Path(tmpdir) / "checklist.json"
            report, checklist = build_reports(
                output_path=output_path,
                checklist_output_path=checklist_path,
            )
            self.assertTrue(output_path.exists())
            self.assertTrue(checklist_path.exists())
            self.assertEqual(29, report["runtime_book_count"])
            self.assertEqual(8, report["thresholds"]["low_section_threshold"])
            outlier_map = {
                str(item["book_slug"]): dict(item)
                for item in report["outliers"]
            }
            self.assertNotIn("logging", outlier_map)
            self.assertNotIn("monitoring", outlier_map)
            self.assertEqual("section split problem", outlier_map["observability_overview"]["classification"])
            self.assertEqual([], checklist["blocker"])
            self.assertLessEqual(len(checklist["warning"]), 5)


if __name__ == "__main__":
    unittest.main()
