from __future__ import annotations

import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.canonical.models import (
    AstProvenance,
    CanonicalDocumentAst,
    CanonicalSectionAst,
    ParagraphBlock,
)
from play_book_studio.canonical.translate import UNIT_BATCH_SIZE, translate_document_ast
from play_book_studio.config.settings import Settings


class CanonicalTranslateTests(unittest.TestCase):
    def test_translate_document_ast_reuses_translation_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            document = CanonicalDocumentAst(
                doc_id="doc-1",
                book_slug="overview",
                title="Overview",
                source_type="web",
                source_url="https://example.com/en/overview",
                viewer_base_path="/docs/ocp/4.20/ko/overview/index.html",
                source_language="en",
                display_language="ko",
                translation_status="translated_ko_draft",
                pack_id="openshift-4-20-core",
                pack_label="OpenShift 4.20 Gold Dataset",
                inferred_product="openshift",
                inferred_version="4.20",
                sections=(
                    CanonicalSectionAst(
                        section_id="overview:intro",
                        ordinal=1,
                        heading="Introduction",
                        level=1,
                        path=("Introduction",),
                        anchor="intro",
                        source_url="https://example.com/en/overview",
                        viewer_path="/docs/ocp/4.20/ko/overview/index.html#intro",
                        semantic_role="overview",
                        blocks=(ParagraphBlock("Hello cluster operator."),),
                    ),
                ),
                provenance=AstProvenance(
                    source_fingerprint="fp-overview",
                    translation_source_fingerprint="fp-overview-en",
                    translation_source_url="https://example.com/en/overview",
                ),
            )

            first_response = (
                '{"items":['
                '{"id":"doc.title","text":"개요"},'
                '{"id":"s0.heading","text":"소개"},'
                '{"id":"s0.path.0","text":"소개"},'
                '{"id":"s0.b0.paragraph","text":"안녕하세요 클러스터 운영자."}'
                "]}"""
            )

            with patch("play_book_studio.canonical.translate.LLMClient") as client_cls:
                client = client_cls.return_value
                client.generate.return_value = first_response
                translated = translate_document_ast(document, settings)

            self.assertEqual("개요", translated.title)
            self.assertEqual("소개", translated.sections[0].heading)
            self.assertEqual(
                "안녕하세요 클러스터 운영자.",
                translated.sections[0].blocks[0].text,
            )

            with patch("play_book_studio.canonical.translate.LLMClient") as client_cls:
                client = client_cls.return_value
                client.generate.side_effect = AssertionError("cache miss")
                translated_again = translate_document_ast(document, settings)

            self.assertEqual("개요", translated_again.title)
            self.assertEqual("소개", translated_again.sections[0].heading)
            self.assertEqual(
                "안녕하세요 클러스터 운영자.",
                translated_again.sections[0].blocks[0].text,
            )

    def test_translate_document_ast_writes_progress_to_cache_per_batch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            document = CanonicalDocumentAst(
                doc_id="doc-2",
                book_slug="monitoring",
                title="Monitoring",
                source_type="web",
                source_url="https://example.com/en/monitoring",
                viewer_base_path="/docs/ocp/4.20/ko/monitoring/index.html",
                source_language="en",
                display_language="ko",
                translation_status="translated_ko_draft",
                pack_id="openshift-4-20-core",
                pack_label="OpenShift 4.20 Gold Dataset",
                inferred_product="openshift",
                inferred_version="4.20",
                sections=(
                    CanonicalSectionAst(
                        section_id="monitoring:intro",
                        ordinal=1,
                        heading="Introduction",
                        level=1,
                        path=(),
                        anchor="intro",
                        source_url="https://example.com/en/monitoring",
                        viewer_path="/docs/ocp/4.20/ko/monitoring/index.html#intro",
                        semantic_role="overview",
                        blocks=tuple(
                            ParagraphBlock(f"Leaf text {index}") for index in range(UNIT_BATCH_SIZE + 1)
                        ),
                    ),
                ),
                provenance=AstProvenance(
                    source_fingerprint="fp-monitoring",
                    translation_source_fingerprint="fp-monitoring-en",
                    translation_source_url="https://example.com/en/monitoring",
                ),
            )

            write_calls: list[dict[str, object]] = []

            def record_write(
                _document: CanonicalDocumentAst,
                _settings: Settings,
                payload: dict[str, str],
                *,
                progress: dict[str, object] | None = None,
            ) -> None:
                write_calls.append(
                    {
                        "item_count": len(payload),
                        "progress": dict(progress or {}),
                    }
                )

            def translate_batch(_client: object, batch: list[object]) -> dict[str, str]:
                return {
                    unit.unit_id: f"ko:{unit.unit_id}"
                    for unit in batch
                }

            with patch("play_book_studio.canonical.translate.LLMClient") as client_cls, patch(
                "play_book_studio.canonical.translate._translate_unit_batch",
                side_effect=translate_batch,
            ), patch(
                "play_book_studio.canonical.translate._write_translation_cache",
                side_effect=record_write,
            ):
                client_cls.return_value = object()
                translated = translate_document_ast(document, settings)

            self.assertEqual("ko:doc.title", translated.title)
            self.assertEqual(3, len(write_calls))
            self.assertEqual(
                {
                    "status": "running",
                    "completed_unit_count": 0,
                    "total_unit_count": UNIT_BATCH_SIZE + 3,
                    "pending_unit_count": UNIT_BATCH_SIZE + 3,
                    "completed_batch_count": 0,
                    "total_batch_count": 2,
                    "current_batch_index": 1,
                    "current_batch_size": 18,
                },
                write_calls[0]["progress"],
            )
            self.assertEqual(
                {
                    "status": "running",
                    "completed_unit_count": 18,
                    "total_unit_count": UNIT_BATCH_SIZE + 3,
                    "pending_unit_count": 3,
                    "completed_batch_count": 1,
                    "total_batch_count": 2,
                    "current_batch_index": 1,
                    "current_batch_size": 18,
                },
                write_calls[1]["progress"],
            )
            self.assertEqual(
                {
                    "status": "complete",
                    "completed_unit_count": UNIT_BATCH_SIZE + 3,
                    "total_unit_count": UNIT_BATCH_SIZE + 3,
                    "pending_unit_count": 0,
                    "completed_batch_count": 2,
                    "total_batch_count": 2,
                    "current_batch_index": 2,
                    "current_batch_size": 3,
                },
                write_calls[2]["progress"],
            )
            self.assertEqual(UNIT_BATCH_SIZE + 3, write_calls[-1]["item_count"])

    def test_translate_document_ast_uses_multiple_threads_for_large_books(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            paragraph_count = (UNIT_BATCH_SIZE * 5) + 1
            document = CanonicalDocumentAst(
                doc_id="doc-3",
                book_slug="backup_and_restore",
                title="Backup and restore",
                source_type="web",
                source_url="https://example.com/en/backup_and_restore",
                viewer_base_path="/docs/ocp/4.20/ko/backup_and_restore/index.html",
                source_language="en",
                display_language="ko",
                translation_status="translated_ko_draft",
                pack_id="openshift-4-20-core",
                pack_label="OpenShift 4.20 Gold Dataset",
                inferred_product="openshift",
                inferred_version="4.20",
                sections=(
                    CanonicalSectionAst(
                        section_id="backup:intro",
                        ordinal=1,
                        heading="Introduction",
                        level=1,
                        path=(),
                        anchor="intro",
                        source_url="https://example.com/en/backup_and_restore",
                        viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html#intro",
                        semantic_role="overview",
                        blocks=tuple(
                            ParagraphBlock(f"Leaf text {index}") for index in range(paragraph_count)
                        ),
                    ),
                ),
                provenance=AstProvenance(
                    source_fingerprint="fp-backup",
                    translation_source_fingerprint="fp-backup-en",
                    translation_source_url="https://example.com/en/backup_and_restore",
                ),
            )

            thread_ids: set[int] = set()

            def translate_batch(_client: object, batch: list[object]) -> dict[str, str]:
                thread_ids.add(threading.get_ident())
                time.sleep(0.02)
                return {unit.unit_id: f"ko:{unit.unit_id}" for unit in batch}

            with patch("play_book_studio.canonical.translate.LLMClient") as client_cls, patch(
                "play_book_studio.canonical.translate._translate_unit_batch",
                side_effect=translate_batch,
            ):
                client_cls.return_value = object()
                translated = translate_document_ast(document, settings)

            self.assertEqual("ko:doc.title", translated.title)
            self.assertGreater(len(thread_ids), 1)


if __name__ == "__main__":
    unittest.main()
