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

from play_book_studio.canonical.models import PlaybookDocumentArtifact, PlaybookSectionArtifact
from play_book_studio.config.settings import Settings
from play_book_studio.ingestion.manifest import write_manifest
from play_book_studio.ingestion.models import ChunkRecord, NormalizedSection, SourceManifestEntry
from play_book_studio.ingestion.translation_draft_generation import generate_translation_drafts


class TranslationDraftGenerationTests(unittest.TestCase):
    def test_generate_translation_drafts_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            entry = SourceManifestEntry(
                book_slug="backup_and_restore",
                title="Backup and restore",
                source_url="https://example.com/backup_and_restore",
                viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html",
                content_status="translated_ko_draft",
            )
            write_manifest(settings.translation_draft_manifest_path, [entry])
            (settings.raw_html_dir / "backup_and_restore.html").parent.mkdir(parents=True, exist_ok=True)
            (settings.raw_html_dir / "backup_and_restore.html").write_text("<html></html>", encoding="utf-8")

            fake_section = NormalizedSection(
                book_slug="backup_and_restore",
                book_title="백업 및 복원",
                heading="개요",
                section_level=1,
                section_path=["백업 및 복원"],
                anchor="overview",
                source_url="https://example.com/backup_and_restore",
                viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                text="백업 및 복원 초안입니다.",
                translation_status="translated_ko_draft",
                translation_stage="translated_ko_draft",
                translation_source_language="en",
                translation_source_url="https://example.com/en/backup_and_restore",
            )
            fake_chunk = ChunkRecord(
                chunk_id="chunk-1",
                book_slug="backup_and_restore",
                book_title="백업 및 복원",
                chapter="백업 및 복원",
                section="개요",
                anchor="overview",
                source_url="https://example.com/backup_and_restore",
                viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                text="백업 및 복원 초안입니다.",
                token_count=8,
                ordinal=0,
                translation_status="translated_ko_draft",
                translation_stage="translated_ko_draft",
                translation_source_language="en",
                translation_source_url="https://example.com/en/backup_and_restore",
            )
            fake_playbook = PlaybookDocumentArtifact(
                book_slug="backup_and_restore",
                title="백업 및 복원",
                source_uri="https://example.com/backup_and_restore",
                source_language="en",
                language_hint="ko",
                translation_status="translated_ko_draft",
                translation_stage="translated_ko_draft",
                translation_source_uri="https://example.com/en/backup_and_restore",
                translation_source_language="en",
                translation_source_fingerprint="fp",
                pack_id="openshift-4-20-core",
                inferred_version="4.20",
                legal_notice_url="",
                review_status="needs_review",
                sections=(
                    PlaybookSectionArtifact(
                        section_id="s1",
                        ordinal=0,
                        heading="개요",
                        level=1,
                        path=("백업 및 복원",),
                        anchor="overview",
                        viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                        semantic_role="overview",
                        blocks=(),
                    ),
                ),
                quality_status="review_required",
                quality_flags=("translated_ko_draft",),
                source_metadata={"source_lane": "official_en_fallback"},
                anchor_map={"overview": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview"},
            )
            enriched_entry = SourceManifestEntry(
                **{
                    **entry.to_dict(),
                    "legal_notice_url": "https://example.com/legal",
                    "license_or_terms": "Apache-2.0",
                    "updated_at": "2026-04-10T12:00:00Z",
                }
            )

            with (
                patch("play_book_studio.ingestion.translation_draft_generation.collect_entry"),
                patch(
                    "play_book_studio.ingestion.translation_draft_generation.entry_with_collected_metadata",
                    return_value=enriched_entry,
                ),
                patch("play_book_studio.ingestion.translation_draft_generation.extract_document_ast", return_value=object()) as extract_mock,
                patch("play_book_studio.ingestion.translation_draft_generation.project_normalized_sections", return_value=[fake_section]),
                patch("play_book_studio.ingestion.translation_draft_generation.chunk_sections", return_value=[fake_chunk]),
                patch("play_book_studio.ingestion.translation_draft_generation.project_playbook_document", return_value=fake_playbook),
            ):
                report = generate_translation_drafts(settings)

            self.assertEqual(1, report["summary"]["generated_count"])
            self.assertEqual(1, report["summary"]["section_count"])
            self.assertEqual(1, report["summary"]["chunk_count"])
            self.assertIn("draft_manualbook_audit", report)
            self.assertEqual(0, report["summary"]["draft_manualbook_failing_book_count"])
            self.assertEqual("https://example.com/legal", extract_mock.call_args.args[1].legal_notice_url)
            self.assertEqual("Apache-2.0", extract_mock.call_args.args[1].license_or_terms)
            self.assertEqual("2026-04-10T12:00:00Z", extract_mock.call_args.args[1].updated_at)

            normalized_path = Path(report["output_targets"]["normalized_docs_path"])
            chunks_path = Path(report["output_targets"]["chunks_path"])
            playbook_documents_path = Path(report["output_targets"]["playbook_documents_path"])
            playbook_book_path = Path(report["output_targets"]["playbook_books_dir"]) / "backup_and_restore.json"

            self.assertTrue(normalized_path.exists())
            self.assertTrue(chunks_path.exists())
            self.assertTrue(playbook_documents_path.exists())
            self.assertTrue(playbook_book_path.exists())

            normalized_row = json.loads(normalized_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual("translated_ko_draft", normalized_row["translation_status"])

    def test_generate_translation_drafts_reuses_existing_outputs_without_regeneration(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            entry = SourceManifestEntry(
                book_slug="backup_and_restore",
                title="Backup and restore",
                source_url="https://example.com/backup_and_restore",
                viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html",
                content_status="translated_ko_draft",
            )
            write_manifest(settings.translation_draft_manifest_path, [entry])
            (settings.raw_html_dir / "backup_and_restore.html").parent.mkdir(parents=True, exist_ok=True)
            (settings.raw_html_dir / "backup_and_restore.html").write_text("<html></html>", encoding="utf-8")

            fake_section = NormalizedSection(
                book_slug="backup_and_restore",
                book_title="백업 및 복원",
                heading="개요",
                section_level=1,
                section_path=["백업 및 복원"],
                anchor="overview",
                source_url="https://example.com/backup_and_restore",
                viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                text="백업 및 복원 초안입니다.",
                translation_status="translated_ko_draft",
                translation_stage="translated_ko_draft",
                translation_source_language="en",
                translation_source_url="https://example.com/en/backup_and_restore",
            )
            fake_chunk = ChunkRecord(
                chunk_id="chunk-1",
                book_slug="backup_and_restore",
                book_title="백업 및 복원",
                chapter="백업 및 복원",
                section="개요",
                anchor="overview",
                source_url="https://example.com/backup_and_restore",
                viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                text="백업 및 복원 초안입니다.",
                token_count=8,
                ordinal=0,
                translation_status="translated_ko_draft",
                translation_stage="translated_ko_draft",
                translation_source_language="en",
                translation_source_url="https://example.com/en/backup_and_restore",
            )
            fake_playbook = PlaybookDocumentArtifact(
                book_slug="backup_and_restore",
                title="백업 및 복원",
                source_uri="https://example.com/backup_and_restore",
                source_language="en",
                language_hint="ko",
                translation_status="translated_ko_draft",
                translation_stage="translated_ko_draft",
                translation_source_uri="https://example.com/en/backup_and_restore",
                translation_source_language="en",
                translation_source_fingerprint="fp",
                pack_id="openshift-4-20-core",
                inferred_version="4.20",
                legal_notice_url="",
                review_status="needs_review",
                sections=(
                    PlaybookSectionArtifact(
                        section_id="s1",
                        ordinal=0,
                        heading="개요",
                        level=1,
                        path=("백업 및 복원",),
                        anchor="overview",
                        viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                        semantic_role="overview",
                        blocks=(),
                    ),
                ),
                quality_status="review_required",
                quality_flags=("translated_ko_draft",),
                source_metadata={"source_lane": "official_en_fallback"},
                anchor_map={"overview": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview"},
            )

            with (
                patch("play_book_studio.ingestion.translation_draft_generation.collect_entry"),
                patch(
                    "play_book_studio.ingestion.translation_draft_generation.entry_with_collected_metadata",
                    return_value=entry,
                ),
                patch("play_book_studio.ingestion.translation_draft_generation.extract_document_ast", return_value=object()),
                patch("play_book_studio.ingestion.translation_draft_generation.project_normalized_sections", return_value=[fake_section]),
                patch("play_book_studio.ingestion.translation_draft_generation.chunk_sections", return_value=[fake_chunk]),
                patch("play_book_studio.ingestion.translation_draft_generation.project_playbook_document", return_value=fake_playbook),
            ):
                first_report = generate_translation_drafts(settings)

            self.assertEqual(0, first_report["summary"]["reused_count"])

            with patch("play_book_studio.ingestion.translation_draft_generation.collect_entry") as collect_mock:
                second_report = generate_translation_drafts(settings)

            self.assertEqual(1, second_report["summary"]["reused_count"])
            self.assertEqual("reused", second_report["books"][0]["resume_state"])
            collect_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
