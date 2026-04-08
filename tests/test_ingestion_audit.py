from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.ingestion.audit import (
    build_approved_manifest,
    build_corpus_gap_report,
    build_data_quality_report,
    build_source_approval_report,
    looks_like_mojibake_title,
    write_approved_manifest,
)
from play_book_studio.ingestion.manifest import read_manifest


class Part1AuditTests(unittest.TestCase):
    def test_looks_like_mojibake_title_flags_broken_korean(self) -> None:
        self.assertTrue(looks_like_mojibake_title("怨좉툒 ?ㅽ듃?뚰궧"))
        self.assertTrue(looks_like_mojibake_title("?꾪궎?띿쿂"))

    def test_looks_like_mojibake_title_accepts_clean_titles(self) -> None:
        self.assertFalse(looks_like_mojibake_title("고급 네트워킹"))
        self.assertFalse(looks_like_mojibake_title("Backup and restore"))

    def test_build_data_quality_report_separates_manifest_and_chunk_title_quality(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifests = root / "manifests"
            part1 = root / "part1"
            raw_html = part1 / "raw_html"
            manifests.mkdir(parents=True)
            raw_html.mkdir(parents=True)

            manifest_payload = {
                "version": 1,
                "source": "test",
                "count": 1,
                "entries": [
                    {
                        "book_slug": "advanced_networking",
                        "title": "怨좉툒 ?ㅽ듃?뚰궧",
                        "source_url": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/advanced_networking/index",
                        "viewer_path": "/docs/ocp/4.20/ko/advanced_networking/index.html",
                        "high_value": True,
                    }
                ],
            }
            (manifests / "ocp_ko_4_20_html_single.json").write_text(
                json.dumps(manifest_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            normalized_row = {
                "book_slug": "advanced_networking",
                "book_title": "고급 네트워킹",
                "heading": "개요",
                "section_level": 1,
                "section_path": ["고급 네트워킹"],
                "anchor": "overview",
                "source_url": manifest_payload["entries"][0]["source_url"],
                "viewer_path": "/docs/ocp/4.20/ko/advanced_networking/index.html#overview",
                "text": "고급 네트워킹 문서입니다.",
            }
            chunk_row = {
                "chunk_id": "chunk-1",
                "book_slug": "advanced_networking",
                "book_title": "고급 네트워킹",
                "chapter": "고급 네트워킹",
                "section": "개요",
                "anchor": "overview",
                "source_url": manifest_payload["entries"][0]["source_url"],
                "viewer_path": "/docs/ocp/4.20/ko/advanced_networking/index.html#overview",
                "text": "고급 네트워킹 문서입니다.",
                "token_count": 10,
                "ordinal": 0,
            }
            (part1 / "normalized_docs.jsonl").write_text(
                json.dumps(normalized_row, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (part1 / "chunks.jsonl").write_text(
                json.dumps(chunk_row, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (part1 / "bm25_corpus.jsonl").write_text(
                json.dumps(
                    {
                        "chunk_id": "chunk-1",
                        "book_slug": "advanced_networking",
                        "chapter": "고급 네트워킹",
                        "section": "개요",
                        "anchor": "overview",
                        "source_url": manifest_payload["entries"][0]["source_url"],
                        "viewer_path": "/docs/ocp/4.20/ko/advanced_networking/index.html#overview",
                        "text": "고급 네트워킹 문서입니다.",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (part1 / "preprocessing_log.json").write_text(
                json.dumps(
                    {
                        "per_book_stats": [
                            {"book_slug": "advanced_networking", "title": "怨좉툒 ?ㅽ듃?뚰궧"}
                        ]
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (raw_html / "advanced_networking.html").write_text(
                """
                <html>
                  <body>
                    <main id="main-content">
                      <article>
                        <h1>고급 네트워킹</h1>
                      </article>
                    </main>
                  </body>
                </html>
                """,
                encoding="utf-8",
            )

            settings = SimpleNamespace(
                source_catalog_path=manifests / "ocp_ko_4_20_html_single.json",
                normalized_docs_path=part1 / "normalized_docs.jsonl",
                chunks_path=part1 / "chunks.jsonl",
                bm25_corpus_path=part1 / "bm25_corpus.jsonl",
                preprocessing_log_path=part1 / "preprocessing_log.json",
                raw_html_dir=raw_html,
            )

            report = build_data_quality_report(settings)

        self.assertEqual(1, report["title_audit"]["manifest_mojibake_count"])
        self.assertEqual(1, report["title_audit"]["preprocessing_log_mojibake_count"])
        self.assertEqual(0, report["title_audit"]["normalized_title_mojibake_count"])
        self.assertEqual(0, report["title_audit"]["chunk_title_mojibake_count"])
        self.assertTrue(report["checks"]["raw_html_titles_clean"])
        self.assertTrue(report["checks"]["normalized_titles_clean"])
        self.assertTrue(report["checks"]["chunk_titles_clean"])
        self.assertFalse(report["checks"]["manifest_titles_clean"])

    def test_source_approval_report_marks_mixed_and_approved_books(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifests = root / "manifests"
            part1 = root / "part1"
            raw_html = part1 / "raw_html"
            manifests.mkdir(parents=True)
            raw_html.mkdir(parents=True)

            manifest_payload = {
                "version": 1,
                "source": "test",
                "count": 2,
                "entries": [
                    {
                        "book_slug": "architecture",
                        "title": "아키텍처",
                        "source_url": "https://example.com/architecture",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                        "high_value": True,
                    },
                    {
                        "book_slug": "backup_and_restore",
                        "title": "Backup and restore",
                        "source_url": "https://example.com/backup_and_restore",
                        "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html",
                        "high_value": True,
                    },
                ],
            }
            source_manifest_path = manifests / "ocp_ko_4_20_html_single.json"
            source_manifest_path.write_text(
                json.dumps(manifest_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            normalized_rows = [
                {
                    "book_slug": "architecture",
                    "book_title": "아키텍처",
                    "heading": "개요",
                    "section_level": 1,
                    "section_path": ["개요"],
                    "anchor": "overview",
                    "source_url": "https://example.com/architecture",
                    "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                    "text": "OpenShift 아키텍처는 컨트롤 플레인과 작업자 노드로 구성됩니다.",
                },
                {
                    "book_slug": "backup_and_restore",
                    "book_title": "Backup and restore",
                    "heading": "Backup and restore",
                    "section_level": 1,
                    "section_path": ["Backup and restore"],
                    "anchor": "overview",
                    "source_url": "https://example.com/backup_and_restore",
                    "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                    "text": "This content is only available in English.",
                },
            ]
            (part1 / "normalized_docs.jsonl").write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in normalized_rows) + "\n",
                encoding="utf-8",
            )
            chunk_rows = [
                {
                    "chunk_id": "chunk-1",
                    "book_slug": "architecture",
                    "book_title": "아키텍처",
                    "chapter": "아키텍처",
                    "section": "개요",
                    "anchor": "overview",
                    "source_url": "https://example.com/architecture",
                    "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                    "text": "OpenShift 아키텍처는 컨트롤 플레인과 작업자 노드로 구성됩니다.",
                    "token_count": 12,
                    "ordinal": 0,
                },
                {
                    "chunk_id": "chunk-2",
                    "book_slug": "backup_and_restore",
                    "book_title": "Backup and restore",
                    "chapter": "Backup and restore",
                    "section": "Overview",
                    "anchor": "overview",
                    "source_url": "https://example.com/backup_and_restore",
                    "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                    "text": "This content is only available in English.",
                    "token_count": 9,
                    "ordinal": 0,
                },
            ]
            (part1 / "chunks.jsonl").write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in chunk_rows) + "\n",
                encoding="utf-8",
            )
            (raw_html / "architecture.html").write_text(
                "<html><body><main id='main-content'><article><h1>아키텍처</h1></article></main></body></html>",
                encoding="utf-8",
            )
            (raw_html / "backup_and_restore.html").write_text(
                """
                <html>
                  <body>
                    <main id="main-content">
                      <article>
                        <h1>Backup and restore</h1>
                        <p>This content is not available in the selected language.</p>
                      </article>
                    </main>
                  </body>
                </html>
                """,
                encoding="utf-8",
            )

            settings = SimpleNamespace(
                source_catalog_path=source_manifest_path,
                normalized_docs_path=part1 / "normalized_docs.jsonl",
                chunks_path=part1 / "chunks.jsonl",
                raw_html_dir=raw_html,
            )

            report = build_source_approval_report(settings)

        self.assertEqual(1, report["summary"]["approved_ko_count"])
        self.assertEqual(1, report["summary"]["en_only_count"])
        self.assertEqual(
            "docs.redhat.com published Korean html-single",
            report["policy"]["primary_source"],
        )
        self.assertEqual("approved_ko", report["books"][0]["content_status"])
        self.assertEqual("en_only", report["books"][1]["content_status"])
        self.assertTrue(report["books"][0]["citation_eligible"])
        self.assertFalse(report["books"][1]["citation_eligible"])

    def test_source_approval_report_preserves_translation_draft_lane(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifests = root / "manifests"
            part1 = root / "part1"
            raw_html = part1 / "raw_html"
            manifests.mkdir(parents=True)
            raw_html.mkdir(parents=True)

            source_manifest_path = manifests / "ocp_ko_4_20_html_single.json"
            source_manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 1,
                        "entries": [
                            {
                                "book_slug": "machine_configuration",
                                "title": "머신 구성",
                                "source_url": "https://example.com/machine_configuration",
                                "viewer_path": "/docs/ocp/4.20/ko/machine_configuration/index.html",
                                "high_value": True,
                                "content_status": "translated_ko_draft",
                                "approval_notes": "machine translation draft",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (part1 / "normalized_docs.jsonl").write_text(
                json.dumps(
                    {
                        "book_slug": "machine_configuration",
                        "book_title": "머신 구성",
                        "heading": "개요",
                        "section_level": 1,
                        "section_path": ["개요"],
                        "anchor": "overview",
                        "source_url": "https://example.com/machine_configuration",
                        "viewer_path": "/docs/ocp/4.20/ko/machine_configuration/index.html#overview",
                        "text": "머신 구성 초안 번역 문서입니다.",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (part1 / "chunks.jsonl").write_text(
                json.dumps(
                    {
                        "chunk_id": "chunk-1",
                        "book_slug": "machine_configuration",
                        "book_title": "머신 구성",
                        "chapter": "머신 구성",
                        "section": "개요",
                        "anchor": "overview",
                        "source_url": "https://example.com/machine_configuration",
                        "viewer_path": "/docs/ocp/4.20/ko/machine_configuration/index.html#overview",
                        "text": "머신 구성 초안 번역 문서입니다.",
                        "token_count": 8,
                        "ordinal": 0,
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (raw_html / "machine_configuration.html").write_text(
                "<html><body><main id='main-content'><article><h1>Machine configuration</h1></article></main></body></html>",
                encoding="utf-8",
            )

            settings = SimpleNamespace(
                source_catalog_path=source_manifest_path,
                normalized_docs_path=part1 / "normalized_docs.jsonl",
                chunks_path=part1 / "chunks.jsonl",
                raw_html_dir=raw_html,
            )

            report = build_source_approval_report(settings)

        self.assertEqual(1, report["summary"]["translated_ko_draft_count"])
        self.assertEqual("translated_ko_draft", report["books"][0]["content_status"])
        self.assertFalse(report["books"][0]["citation_eligible"])
        self.assertEqual("needs_review", report["books"][0]["approval_status"])
        self.assertEqual(
            "translated Korean draft requires review before citation",
            report["books"][0]["citation_block_reason"],
        )
        self.assertEqual("translation_first", report["books"][0]["gap_lane"])

    def test_corpus_gap_report_groups_translation_and_manual_review_priorities(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifests = root / "manifests"
            part1 = root / "part1"
            raw_html = part1 / "raw_html"
            manifests.mkdir(parents=True)
            raw_html.mkdir(parents=True)

            source_manifest_path = manifests / "ocp_ko_4_20_html_single.json"
            source_manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 3,
                        "entries": [
                            {
                                "book_slug": "backup_and_restore",
                                "title": "Backup and restore",
                                "source_url": "https://example.com/backup_and_restore",
                                "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html",
                                "high_value": True,
                            },
                            {
                                "book_slug": "operators",
                                "title": "Operator",
                                "source_url": "https://example.com/operators",
                                "viewer_path": "/docs/ocp/4.20/ko/operators/index.html",
                                "high_value": True,
                            },
                            {
                                "book_slug": "architecture",
                                "title": "아키텍처",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                                "high_value": True,
                            },
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (part1 / "normalized_docs.jsonl").write_text(
                json.dumps(
                    {
                        "book_slug": "architecture",
                        "book_title": "아키텍처",
                        "heading": "개요",
                        "section_level": 1,
                        "section_path": ["개요"],
                        "anchor": "overview",
                        "source_url": "https://example.com/architecture",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                        "text": "OpenShift 아키텍처는 컨트롤 플레인과 작업자 노드로 구성됩니다.",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (part1 / "chunks.jsonl").write_text(
                json.dumps(
                    {
                        "chunk_id": "chunk-1",
                        "book_slug": "architecture",
                        "book_title": "아키텍처",
                        "chapter": "아키텍처",
                        "section": "개요",
                        "anchor": "overview",
                        "source_url": "https://example.com/architecture",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                        "text": "OpenShift 아키텍처는 컨트롤 플레인과 작업자 노드로 구성됩니다.",
                        "token_count": 12,
                        "ordinal": 0,
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (raw_html / "backup_and_restore.html").write_text(
                "<html><body><p>This content is not available in the selected language.</p></body></html>",
                encoding="utf-8",
            )
            (raw_html / "operators.html").write_text(
                "<html><body><article><h1>Operator</h1></article></body></html>",
                encoding="utf-8",
            )
            (raw_html / "architecture.html").write_text(
                "<html><body><article><h1>아키텍처</h1></article></body></html>",
                encoding="utf-8",
            )

            settings = SimpleNamespace(
                source_catalog_path=source_manifest_path,
                normalized_docs_path=part1 / "normalized_docs.jsonl",
                chunks_path=part1 / "chunks.jsonl",
                raw_html_dir=raw_html,
            )

            report = build_corpus_gap_report(settings)

        self.assertEqual(2, report["summary"]["high_value_issue_count"])
        self.assertEqual(["backup_and_restore"], [item["book_slug"] for item in report["translation_first"]])
        self.assertEqual(["operators"], [item["book_slug"] for item in report["manual_review_first"]])

    def test_build_approved_manifest_filters_out_non_korean_books(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifests = root / "manifests"
            part1 = root / "part1"
            raw_html = part1 / "raw_html"
            manifests.mkdir(parents=True)
            raw_html.mkdir(parents=True)

            source_manifest_path = manifests / "ocp_ko_4_20_html_single.json"
            source_manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 2,
                        "entries": [
                            {
                                "book_slug": "architecture",
                                "title": "아키텍처",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                                "high_value": True,
                            },
                            {
                                "book_slug": "backup_and_restore",
                                "title": "Backup and restore",
                                "source_url": "https://example.com/backup_and_restore",
                                "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html",
                                "high_value": True,
                            },
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (part1 / "normalized_docs.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "book_slug": "architecture",
                                "book_title": "아키텍처",
                                "heading": "개요",
                                "section_level": 1,
                                "section_path": ["개요"],
                                "anchor": "overview",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                                "text": "OpenShift 아키텍처는 컨트롤 플레인과 작업자 노드로 구성됩니다.",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "book_slug": "backup_and_restore",
                                "book_title": "Backup and restore",
                                "heading": "Overview",
                                "section_level": 1,
                                "section_path": ["Overview"],
                                "anchor": "overview",
                                "source_url": "https://example.com/backup_and_restore",
                                "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                                "text": "This content is only available in English.",
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (part1 / "chunks.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "chunk_id": "chunk-1",
                                "book_slug": "architecture",
                                "book_title": "아키텍처",
                                "chapter": "아키텍처",
                                "section": "개요",
                                "anchor": "overview",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                                "text": "OpenShift 아키텍처는 컨트롤 플레인과 작업자 노드로 구성됩니다.",
                                "token_count": 12,
                                "ordinal": 0,
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "chunk_id": "chunk-2",
                                "book_slug": "backup_and_restore",
                                "book_title": "Backup and restore",
                                "chapter": "Backup and restore",
                                "section": "Overview",
                                "anchor": "overview",
                                "source_url": "https://example.com/backup_and_restore",
                                "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                                "text": "This content is only available in English.",
                                "token_count": 9,
                                "ordinal": 0,
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (raw_html / "architecture.html").write_text(
                "<html><body><main id='main-content'><article><h1>아키텍처</h1></article></main></body></html>",
                encoding="utf-8",
            )
            (raw_html / "backup_and_restore.html").write_text(
                "<html><body><p>This content is not available in the selected language.</p></body></html>",
                encoding="utf-8",
            )

            settings = SimpleNamespace(
                source_catalog_path=source_manifest_path,
                normalized_docs_path=part1 / "normalized_docs.jsonl",
                chunks_path=part1 / "chunks.jsonl",
                raw_html_dir=raw_html,
            )

            entries = build_approved_manifest(settings)
            output_path = manifests / "approved_ko.json"
            write_approved_manifest(output_path, entries)
            written_entries = read_manifest(output_path)

        self.assertEqual(["architecture"], [entry.book_slug for entry in entries])
        self.assertEqual(["architecture"], [entry.book_slug for entry in written_entries])
        self.assertEqual("approved_ko", written_entries[0].content_status)
        self.assertEqual("internal_text", written_entries[0].viewer_strategy)


if __name__ == "__main__":
    unittest.main()
