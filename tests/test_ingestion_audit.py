from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
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
    build_translation_lane_report,
    looks_like_mojibake_title,
    write_approved_manifest,
)
from play_book_studio.ingestion.collector import raw_html_metadata_path
from play_book_studio.ingestion.audit_rules import (
    body_language_guess,
    classify_content_status,
    is_english_like_title,
)
from play_book_studio.ingestion.manifest import read_manifest


class Part1AuditTests(unittest.TestCase):
    @contextmanager
    def _workspace(self) -> Iterator[Path]:
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def _audit_layout(self, root: Path, *, corpus_dir_name: str = "part1") -> tuple[Path, Path, Path]:
        manifests = root / "manifests"
        corpus = root / corpus_dir_name
        raw_html = corpus / "raw_html"
        manifests.mkdir(parents=True, exist_ok=True)
        raw_html.mkdir(parents=True, exist_ok=True)
        return manifests, corpus, raw_html

    def _ensure_dir(self, path: Path) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _audit_settings(
        self,
        root: Path,
        *,
        corpus_dir_name: str = "part1",
        source_catalog_name: str = "ocp_ko_4_20_html_single.json",
        **overrides: object,
    ) -> SimpleNamespace:
        manifests, corpus, raw_html = self._audit_layout(root, corpus_dir_name=corpus_dir_name)
        defaults = {
            "source_catalog_path": manifests / source_catalog_name,
            "normalized_docs_path": corpus / "normalized_docs.jsonl",
            "chunks_path": corpus / "chunks.jsonl",
            "bm25_corpus_path": corpus / "bm25_corpus.jsonl",
            "preprocessing_log_path": corpus / "preprocessing_log.json",
            "raw_html_dir": raw_html,
            "corpus_dir": corpus,
            "source_manifest_path": manifests / "approved_wiki_runtime.json",
            "translation_draft_manifest_path": manifests / "translation_draft_manifest.json",
            "playbook_books_dir": root / "playbooks",
            "playbook_documents_path": root / "playbook_documents.jsonl",
            "viewer_path_template": "/docs/ocp/{version}/{lang}/{slug}/index.html",
            "ocp_version": "4.20",
            "docs_language": "ko",
        }
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def _corpus_settings(self, root: Path, **overrides: object) -> SimpleNamespace:
        return self._audit_settings(
            root,
            corpus_dir_name="corpus",
            source_catalog_name="ocp_multiversion_html_single_catalog.json",
            **overrides,
        )

    def test_looks_like_mojibake_title_flags_broken_korean(self) -> None:
        self.assertTrue(looks_like_mojibake_title("怨좉툒 ?ㅽ듃?뚰궧"))
        self.assertTrue(looks_like_mojibake_title("?꾪궎?띿쿂"))

    def test_looks_like_mojibake_title_accepts_clean_titles(self) -> None:
        self.assertFalse(looks_like_mojibake_title("고급 네트워킹"))
        self.assertFalse(looks_like_mojibake_title("Backup and restore"))

    def test_classify_content_status_marks_blocked_when_sections_or_chunks_missing(self) -> None:
        status, reason = classify_content_status(
            section_count=0,
            chunk_count=0,
            hangul_section_ratio=0.0,
            hangul_chunk_ratio=0.0,
            title_english_like=True,
            fallback_detected=False,
        )
        self.assertEqual("blocked", status)
        self.assertEqual("missing normalized sections or chunks", reason)

    def test_classify_content_status_marks_mixed_for_english_like_title_with_korean_body(self) -> None:
        self.assertTrue(is_english_like_title("Backup and restore"))
        status, reason = classify_content_status(
            section_count=3,
            chunk_count=3,
            hangul_section_ratio=1.0,
            hangul_chunk_ratio=1.0,
            title_english_like=True,
            fallback_detected=False,
        )
        self.assertEqual("mixed", status)
        self.assertEqual(
            "book title is English-like even though body is mostly Korean",
            reason,
        )

    def test_classify_content_status_marks_mixed_when_body_is_partially_korean(self) -> None:
        status, reason = classify_content_status(
            section_count=4,
            chunk_count=4,
            hangul_section_ratio=0.75,
            hangul_chunk_ratio=0.75,
            title_english_like=False,
            fallback_detected=False,
        )
        self.assertEqual("mixed", status)
        self.assertEqual("book mixes Korean and non-Korean body text", reason)

    def test_body_language_guess_prefers_fallback_over_ratio(self) -> None:
        self.assertEqual("en_only", body_language_guess(hangul_chunk_ratio=0.9, fallback_detected=True))
        self.assertEqual("mixed", body_language_guess(hangul_chunk_ratio=0.5, fallback_detected=False))
        self.assertEqual("ko", body_language_guess(hangul_chunk_ratio=0.95, fallback_detected=False))

    def test_build_data_quality_report_separates_manifest_and_chunk_title_quality(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)

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

            settings = self._audit_settings(root)

            report = build_data_quality_report(settings)

        self.assertEqual(1, report["title_audit"]["manifest_mojibake_count"])
        self.assertEqual(1, report["title_audit"]["preprocessing_log_mojibake_count"])
        self.assertEqual(0, report["title_audit"]["normalized_title_mojibake_count"])
        self.assertEqual(0, report["title_audit"]["chunk_title_mojibake_count"])
        self.assertTrue(report["checks"]["raw_html_titles_clean"])
        self.assertTrue(report["checks"]["normalized_titles_clean"])
        self.assertTrue(report["checks"]["chunk_titles_clean"])
        self.assertTrue(report["checks"]["normalized_titles_align_with_raw_html"])
        self.assertTrue(report["checks"]["chunk_titles_align_with_raw_html"])
        self.assertFalse(report["checks"]["manifest_titles_clean"])

    def test_build_data_quality_report_uses_original_title_for_manual_synthesis(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)

            manifest_payload = {
                "version": 1,
                "source": "test",
                "count": 1,
                "entries": [
                    {
                        "book_slug": "backup_and_restore",
                        "title": "Backup and restore",
                        "source_url": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/backup_and_restore/index",
                        "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html",
                        "high_value": True,
                    }
                ],
            }
            (manifests / "ocp_ko_4_20_html_single.json").write_text(
                json.dumps(manifest_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            normalized_row = {
                "book_slug": "backup_and_restore",
                "book_title": "백업 및 복구 운영 플레이북",
                "original_title": "Backup and restore",
                "source_type": "manual_synthesis",
                "source_lane": "applied_playbook",
                "heading": "개요",
                "section_level": 1,
                "section_path": ["개요"],
                "anchor": "overview",
                "source_url": manifest_payload["entries"][0]["source_url"],
                "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                "text": "백업 및 복구 절차를 안내합니다.",
            }
            chunk_row = {
                "chunk_id": "chunk-1",
                "book_slug": "backup_and_restore",
                "book_title": "Backup and restore",
                "original_title": "Backing up and restoring cluster state",
                "source_type": "manual_synthesis",
                "source_lane": "applied_playbook",
                "chapter": "백업 및 복구 운영 플레이북",
                "section": "개요",
                "anchor": "overview",
                "source_url": manifest_payload["entries"][0]["source_url"],
                "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                "text": "백업 및 복구 절차를 안내합니다.",
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
                        "book_slug": "backup_and_restore",
                        "chapter": "백업 및 복구 운영 플레이북",
                        "section": "개요",
                        "anchor": "overview",
                        "source_url": manifest_payload["entries"][0]["source_url"],
                        "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview",
                        "text": "백업 및 복구 절차를 안내합니다.",
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
                            {"book_slug": "backup_and_restore", "title": "Backup and restore"}
                        ]
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (raw_html / "backup_and_restore.html").write_text(
                """
                <html>
                  <body>
                    <main id="main-content">
                      <article>
                        <h1>Backup and restore</h1>
                      </article>
                    </main>
                  </body>
                </html>
                """,
                encoding="utf-8",
            )

            settings = self._audit_settings(root)

            report = build_data_quality_report(settings)

        self.assertEqual(0, report["title_audit"]["normalized_raw_html_mismatch_count"])
        self.assertEqual(0, report["title_audit"]["chunk_raw_html_mismatch_count"])
        self.assertTrue(report["checks"]["normalized_titles_align_with_raw_html"])
        self.assertTrue(report["checks"]["chunk_titles_align_with_raw_html"])

    def test_build_data_quality_report_ignores_raw_html_only_books_outside_processed_subset(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)

            manifest_payload = {
                "version": 1,
                "source": "test",
                "count": 2,
                "entries": [
                    {
                        "book_slug": "architecture",
                        "title": "아키텍처",
                        "source_url": "https://docs.example/architecture",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                        "high_value": True,
                    },
                    {
                        "book_slug": "monitoring",
                        "title": "모니터링",
                        "source_url": "https://docs.example/monitoring",
                        "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html",
                        "high_value": True,
                    },
                ],
            }
            (manifests / "ocp_ko_4_20_html_single.json").write_text(
                json.dumps(manifest_payload, ensure_ascii=False, indent=2),
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
                        "source_url": "https://docs.example/architecture",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                        "text": "아키텍처 문서입니다.",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (part1 / "chunks.jsonl").write_text(
                json.dumps(
                    {
                        "chunk_id": "architecture-1",
                        "book_slug": "architecture",
                        "book_title": "아키텍처",
                        "chapter": "아키텍처",
                        "section": "개요",
                        "anchor": "overview",
                        "source_url": "https://docs.example/architecture",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                        "text": "아키텍처 문서입니다.",
                        "token_count": 4,
                        "ordinal": 0,
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (part1 / "bm25_corpus.jsonl").write_text(
                json.dumps(
                    {
                        "chunk_id": "architecture-1",
                        "book_slug": "architecture",
                        "chapter": "아키텍처",
                        "section": "개요",
                        "anchor": "overview",
                        "source_url": "https://docs.example/architecture",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                        "text": "아키텍처 문서입니다.",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (part1 / "preprocessing_log.json").write_text(
                json.dumps(
                    {"per_book_stats": [{"book_slug": "architecture", "title": "아키텍처"}]},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (raw_html / "architecture.html").write_text(
                "<html><body><article><h1>아키텍처</h1></article></body></html>",
                encoding="utf-8",
            )
            (raw_html / "monitoring.html").write_text(
                "<html><body><article><h1>모니터링</h1></article></body></html>",
                encoding="utf-8",
            )

            settings = self._audit_settings(root)

            report = build_data_quality_report(settings)

        self.assertEqual(0, report["title_audit"]["normalized_raw_html_mismatch_count"])
        self.assertEqual(0, report["title_audit"]["chunk_raw_html_mismatch_count"])
        self.assertTrue(report["checks"]["normalized_titles_align_with_raw_html"])
        self.assertTrue(report["checks"]["chunk_titles_align_with_raw_html"])

    def test_build_data_quality_report_skips_chunk_title_match_for_manual_synthesis(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)

            (manifests / "ocp_ko_4_20_html_single.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 1,
                        "entries": [
                            {
                                "book_slug": "monitoring",
                                "title": "Monitoring",
                                "source_url": "https://example.com/monitoring",
                                "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html",
                                "high_value": True,
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
                        "book_slug": "monitoring",
                        "book_title": "모니터링",
                        "original_title": "Monitoring",
                        "source_type": "manual_synthesis",
                        "source_lane": "applied_playbook",
                        "heading": "개요",
                        "section_level": 1,
                        "section_path": ["개요"],
                        "anchor": "overview",
                        "source_url": "https://example.com/monitoring",
                        "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html#overview",
                        "text": "모니터링 문서입니다.",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (part1 / "chunks.jsonl").write_text(
                json.dumps(
                    {
                        "chunk_id": "monitoring-1",
                        "book_slug": "monitoring",
                        "book_title": "모니터링",
                        "original_title": "Monitoring",
                        "source_type": "manual_synthesis",
                        "source_lane": "applied_playbook",
                        "chapter": "모니터링",
                        "section": "개요",
                        "anchor": "overview",
                        "source_url": "https://example.com/monitoring",
                        "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html#overview",
                        "text": "모니터링 문서입니다.",
                        "token_count": 4,
                        "ordinal": 0,
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (part1 / "bm25_corpus.jsonl").write_text("", encoding="utf-8")
            (part1 / "preprocessing_log.json").write_text(
                json.dumps({"per_book_stats": [{"book_slug": "monitoring", "title": "Monitoring"}]}, ensure_ascii=False),
                encoding="utf-8",
            )
            (raw_html / "monitoring.html").write_text(
                "<html><body><article><h1>Monitoring</h1></article></body></html>",
                encoding="utf-8",
            )

            settings = self._audit_settings(root)

            report = build_data_quality_report(settings)

        self.assertEqual(0, report["title_audit"]["chunk_raw_html_mismatch_count"])
        self.assertTrue(report["checks"]["chunk_titles_align_with_raw_html"])

    def test_build_data_quality_report_blocks_playbooks_with_weak_structure_or_english_headings(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)
            playbooks = self._ensure_dir(part1 / "playbooks")

            manifest_payload = {
                "version": 1,
                "source": "test",
                "count": 2,
                "entries": [
                    {
                        "book_slug": "validation_and_troubleshooting",
                        "title": "검증 및 문제 해결",
                        "source_url": "https://example.com/validation_and_troubleshooting",
                        "viewer_path": "/docs/ocp/4.20/ko/validation_and_troubleshooting/index.html",
                        "high_value": True,
                    },
                    {
                        "book_slug": "monitoring",
                        "title": "모니터링",
                        "source_url": "https://example.com/monitoring",
                        "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html",
                        "high_value": True,
                    },
                ],
            }
            (manifests / "ocp_ko_4_20_html_single.json").write_text(
                json.dumps(manifest_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            normalized_rows = [
                {
                    "book_slug": "validation_and_troubleshooting",
                    "book_title": "검증 및 문제 해결",
                    "heading": "개요",
                    "section_level": 1,
                    "section_path": ["개요"],
                    "anchor": "overview",
                    "source_url": "https://example.com/validation_and_troubleshooting",
                    "viewer_path": "/docs/ocp/4.20/ko/validation_and_troubleshooting/index.html#overview",
                    "text": "검증 절차를 설명합니다.",
                },
                {
                    "book_slug": "monitoring",
                    "book_title": "모니터링",
                    "heading": "Overview",
                    "section_level": 1,
                    "section_path": ["Overview"],
                    "anchor": "overview",
                    "source_url": "https://example.com/monitoring",
                    "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html#overview",
                    "text": "Monitoring guide.",
                },
            ]
            (part1 / "normalized_docs.jsonl").write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in normalized_rows) + "\n",
                encoding="utf-8",
            )
            chunk_rows = [
                {
                    "chunk_id": "chunk-1",
                    "book_slug": "validation_and_troubleshooting",
                    "book_title": "검증 및 문제 해결",
                    "chapter": "검증 및 문제 해결",
                    "section": "개요",
                    "anchor": "overview",
                    "source_url": "https://example.com/validation_and_troubleshooting",
                    "viewer_path": "/docs/ocp/4.20/ko/validation_and_troubleshooting/index.html#overview",
                    "text": "검증 절차를 설명합니다.",
                    "token_count": 5,
                    "ordinal": 0,
                },
                {
                    "chunk_id": "chunk-2",
                    "book_slug": "monitoring",
                    "book_title": "모니터링",
                    "chapter": "모니터링",
                    "section": "Overview",
                    "anchor": "overview",
                    "source_url": "https://example.com/monitoring",
                    "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html#overview",
                    "text": "Monitoring guide.",
                    "token_count": 4,
                    "ordinal": 0,
                },
            ]
            (part1 / "chunks.jsonl").write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in chunk_rows) + "\n",
                encoding="utf-8",
            )
            (part1 / "bm25_corpus.jsonl").write_text(
                "\n".join(
                    json.dumps(
                        {
                            "chunk_id": row["chunk_id"],
                            "book_slug": row["book_slug"],
                            "chapter": row["chapter"],
                            "section": row["section"],
                            "anchor": row["anchor"],
                            "source_url": row["source_url"],
                            "viewer_path": row["viewer_path"],
                            "text": row["text"],
                        },
                        ensure_ascii=False,
                    )
                    for row in chunk_rows
                )
                + "\n",
                encoding="utf-8",
            )
            (part1 / "preprocessing_log.json").write_text(
                json.dumps({"per_book_stats": []}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (raw_html / "validation_and_troubleshooting.html").write_text(
                "<html><body><article><h1>검증 및 문제 해결</h1></article></body></html>",
                encoding="utf-8",
            )
            (raw_html / "monitoring.html").write_text(
                "<html><body><article><h1>모니터링</h1></article></body></html>",
                encoding="utf-8",
            )
            (playbooks / "validation_and_troubleshooting.json").write_text(
                json.dumps(
                    {
                        "book_slug": "validation_and_troubleshooting",
                        "title": "검증 및 문제 해결",
                        "translation_status": "approved_ko",
                        "sections": [
                            {"heading": "설치 검증", "semantic_role": "procedure", "blocks": [{"kind": "code"}]},
                            {"heading": "문제 진단", "semantic_role": "reference", "blocks": []},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (playbooks / "monitoring.json").write_text(
                json.dumps(
                    {
                        "book_slug": "monitoring",
                        "title": "Monitoring",
                        "translation_status": "approved_ko",
                        "sections": [
                            {"heading": "Overview", "semantic_role": "unknown", "blocks": []},
                            {"heading": "Alerting", "semantic_role": "unknown", "blocks": []},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            settings = self._audit_settings(root, playbook_books_dir=playbooks)

            report = build_data_quality_report(settings)

        self.assertFalse(report["checks"]["playbook_semantic_roles_valid"])
        self.assertFalse(report["checks"]["playbook_korean_headings_valid"])
        self.assertEqual(1, report["manualbook_audit"]["failing_book_count"])
        self.assertEqual("monitoring", report["manualbook_audit"]["failing_books"][0]["book_slug"])

    def test_build_data_quality_report_downgrades_manual_synthesis_english_headings_to_warning(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)
            playbooks = self._ensure_dir(part1 / "playbooks")

            (manifests / "ocp_ko_4_20_html_single.json").write_text(
                json.dumps({"entries": []}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (part1 / "normalized_docs.jsonl").write_text("", encoding="utf-8")
            (part1 / "chunks.jsonl").write_text("", encoding="utf-8")
            (part1 / "bm25_corpus.jsonl").write_text("", encoding="utf-8")
            (part1 / "preprocessing_log.json").write_text(
                json.dumps({}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (playbooks / "monitoring.json").write_text(
                json.dumps(
                    {
                        "book_slug": "monitoring",
                        "title": "Monitoring",
                        "translation_status": "approved_ko",
                        "source_metadata": {
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                        },
                        "sections": [
                            {"heading": "Overview", "semantic_role": "procedure", "blocks": []},
                            {"heading": "Alerting", "semantic_role": "reference", "blocks": []},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            settings = self._audit_settings(root, playbook_books_dir=playbooks)

            report = build_data_quality_report(settings)

        self.assertTrue(report["checks"]["playbook_semantic_roles_valid"])
        self.assertTrue(report["checks"]["playbook_korean_headings_valid"])
        self.assertEqual(0, report["manualbook_audit"]["failing_book_count"])
        self.assertEqual(1, report["manualbook_audit"]["warning_book_count"])
        self.assertEqual("monitoring", report["manualbook_audit"]["warning_books"][0]["book_slug"])
        self.assertTrue(report["manualbook_audit"]["warning_books"][0]["heading_gate_exempt"])

    def test_build_data_quality_report_allows_command_and_extension_headings(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)
            playbooks = self._ensure_dir(root / "playbooks")

            (manifests / "ocp_ko_4_20_html_single.json").write_text(
                json.dumps({"entries": []}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (part1 / "normalized_docs.jsonl").write_text("", encoding="utf-8")
            (part1 / "chunks.jsonl").write_text("", encoding="utf-8")
            (part1 / "bm25_corpus.jsonl").write_text("", encoding="utf-8")
            (part1 / "preprocessing_log.json").write_text(
                json.dumps({}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (playbooks / "cli_tools.json").write_text(
                json.dumps(
                    {
                        "book_slug": "cli_tools",
                        "title": "CLI 도구",
                        "translation_status": "approved_ko",
                        "sections": [
                            {"heading": "1 장. OpenShift Container Platform CLI 도구 개요", "semantic_role": "overview", "blocks": []},
                            {"heading": "2.6.1.1. oc annotate", "semantic_role": "reference", "blocks": []},
                            {"heading": "2.6.1.2. oc auth can-i", "semantic_role": "reference", "blocks": []},
                            {"heading": "2.6.1.3. console.action/filter", "semantic_role": "reference", "blocks": []},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            settings = self._audit_settings(root, playbook_books_dir=playbooks)

            report = build_data_quality_report(settings)

        self.assertTrue(report["checks"]["playbook_semantic_roles_valid"])
        self.assertTrue(report["checks"]["playbook_korean_headings_valid"])
        self.assertEqual(0, report["manualbook_audit"]["failing_book_count"])

    def test_source_approval_report_marks_mixed_and_approved_books(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)

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

            settings = self._audit_settings(root, source_catalog_path=source_manifest_path)

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

    def test_source_approval_report_backfills_provenance_from_raw_html_metadata(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)

            source_manifest_path = manifests / "ocp_ko_4_20_html_single.json"
            source_manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 1,
                        "entries": [
                            {
                                "book_slug": "architecture",
                                "title": "아키텍처",
                                "source_url": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/architecture/index",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                                "high_value": True,
                                "content_status": "approved_ko",
                                "approval_status": "approved",
                                "review_status": "unreviewed",
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
                        "book_slug": "architecture",
                        "book_title": "아키텍처",
                        "heading": "개요",
                        "section_level": 1,
                        "section_path": ["개요"],
                        "anchor": "overview",
                        "source_url": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/architecture/index",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                        "text": "아키텍처 문서입니다.",
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
                        "source_url": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/architecture/index",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                        "text": "아키텍처 문서입니다.",
                        "token_count": 4,
                        "ordinal": 0,
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (raw_html / "architecture.html").write_text(
                "<html><body><article><h1>아키텍처</h1></article></body></html>",
                encoding="utf-8",
            )
            settings = self._audit_settings(root, source_catalog_path=source_manifest_path)
            raw_html_metadata_path(settings, "architecture").write_text(
                json.dumps(
                    {
                        "resolved_source_url": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/architecture/index",
                        "resolved_language": "ko",
                        "fallback_detected": False,
                        "legal_notice_url": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/legal_notice/index",
                        "license_or_terms": "OpenShift documentation is licensed under the Apache License 2.0.",
                        "updated_at": "2026-04-10T00:00:00Z",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            report = build_source_approval_report(settings)

        row = report["books"][0]
        self.assertEqual("approved", row["review_status"])
        self.assertEqual("official_ko", row["source_lane"])
        self.assertEqual(
            "openshift_container_platform:4.20:ko:architecture",
            row["source_id"],
        )
        self.assertEqual(
            "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/legal_notice/index",
            row["legal_notice_url"],
        )
        self.assertEqual(
            "OpenShift documentation is licensed under the Apache License 2.0.",
            row["license_or_terms"],
        )
        self.assertEqual("2026-04-10T00:00:00Z", row["updated_at"])

    def test_source_approval_report_preserves_translation_draft_lane(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)

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

            settings = self._audit_settings(
                root,
                source_catalog_path=source_manifest_path,
                corpus_dir=part1,
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
        self.assertEqual(
            "translated_ko_draft",
            report["books"][0]["translation_lane"]["stage"],
        )
        self.assertTrue(
            report["books"][0]["translation_lane"]["artifact_targets"]["playbook_book_path"].endswith(
                "machine_configuration.json"
            )
        )

    def test_translation_lane_report_tracks_required_and_draft_states(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)

            source_manifest_path = manifests / "ocp_ko_4_20_html_single.json"
            source_manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 2,
                        "entries": [
                            {
                                "book_slug": "monitoring",
                                "title": "모니터링",
                                "source_url": "https://example.com/monitoring",
                                "resolved_source_url": "https://example.com/en/monitoring",
                                "resolved_language": "en",
                                "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html",
                                "high_value": True,
                                "content_status": "en_only",
                                "source_fingerprint": "fp-monitoring",
                            },
                            {
                                "book_slug": "machine_configuration",
                                "title": "머신 구성",
                                "source_url": "https://example.com/machine_configuration",
                                "resolved_source_url": "https://example.com/en/machine_configuration",
                                "resolved_language": "en",
                                "viewer_path": "/docs/ocp/4.20/ko/machine_configuration/index.html",
                                "high_value": True,
                                "content_status": "translated_ko_draft",
                                "source_fingerprint": "fp-machine-config",
                            },
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (part1 / "normalized_docs.jsonl").write_text("", encoding="utf-8")
            (part1 / "chunks.jsonl").write_text("", encoding="utf-8")
            (raw_html / "monitoring.html").write_text(
                "This content is not available in the selected language",
                encoding="utf-8",
            )
            (raw_html / "machine_configuration.html").write_text(
                "This content is not available in the selected language",
                encoding="utf-8",
            )

            settings = self._audit_settings(
                root,
                source_catalog_path=source_manifest_path,
                corpus_dir=part1,
                docs_language="ko",
            )

            report = build_translation_lane_report(settings)

        self.assertEqual(2, report["summary"]["active_queue_count"])
        self.assertEqual(1, report["summary"]["translation_required_count"])
        self.assertEqual(1, report["summary"]["translated_ko_draft_count"])
        books_by_slug = {item["book_slug"]: item for item in report["books"]}
        self.assertEqual(
            "translated_ko_draft",
            books_by_slug["monitoring"]["translation_lane"]["next_status"],
        )
        self.assertEqual(
            "approved_ko",
            books_by_slug["machine_configuration"]["translation_lane"]["next_status"],
        )

    def test_corpus_gap_report_groups_translation_and_manual_review_priorities(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)

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

            settings = self._audit_settings(root, source_catalog_path=source_manifest_path)

            report = build_corpus_gap_report(settings)

        self.assertEqual(2, report["summary"]["high_value_issue_count"])
        self.assertEqual(["backup_and_restore"], [item["book_slug"] for item in report["translation_first"]])
        self.assertEqual(["operators"], [item["book_slug"] for item in report["manual_review_first"]])

    def test_build_approved_manifest_filters_out_non_korean_books(self) -> None:
        with self._workspace() as root:
            manifests, part1, raw_html = self._audit_layout(root)

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

            settings = self._audit_settings(root, source_catalog_path=source_manifest_path)

            entries = build_approved_manifest(settings)
            output_path = manifests / "approved_ko.json"
            write_approved_manifest(output_path, entries)
            written_entries = read_manifest(output_path)

        self.assertEqual(["architecture"], [entry.book_slug for entry in entries])
        self.assertEqual(["architecture"], [entry.book_slug for entry in written_entries])
        self.assertEqual("approved_ko", written_entries[0].content_status)
        self.assertEqual("internal_text", written_entries[0].viewer_strategy)

    def test_source_approval_report_overlays_translation_draft_manifest(self) -> None:
        with self._workspace() as root:
            manifests, corpus, raw_html = self._audit_layout(root, corpus_dir_name="corpus")

            source_catalog_path = manifests / "ocp_multiversion_html_single_catalog.json"
            source_catalog_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 1,
                        "entries": [
                            {
                                "product_slug": "openshift_container_platform",
                                "ocp_version": "4.20",
                                "docs_language": "ko",
                                "source_kind": "html-single",
                                "book_slug": "machine_configuration",
                                "title": "Machine configuration",
                                "source_url": "https://example.com/machine_configuration",
                                "resolved_source_url": "https://example.com/en/machine_configuration",
                                "resolved_language": "en",
                                "viewer_path": "/docs/ocp/4.20/ko/machine_configuration/index.html",
                                "high_value": True,
                                "source_fingerprint": "fp-machine-configuration",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            translated_manifest_path = manifests / "ocp_ko_4_20_translated_ko_draft.json"
            translated_manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 1,
                        "entries": [
                            {
                                "product_slug": "openshift_container_platform",
                                "ocp_version": "4.20",
                                "docs_language": "ko",
                                "source_kind": "html-single",
                                "book_slug": "machine_configuration",
                                "title": "머신 구성",
                                "source_url": "https://example.com/machine_configuration",
                                "resolved_source_url": "https://example.com/en/machine_configuration",
                                "resolved_language": "en",
                                "viewer_path": "/docs/ocp/4.20/ko/machine_configuration/index.html",
                                "high_value": True,
                                "content_status": "translated_ko_draft",
                                "translation_source_language": "en",
                                "translation_source_url": "https://example.com/en/machine_configuration",
                                "translation_source_fingerprint": "fp-machine-configuration",
                                "source_fingerprint": "fp-machine-configuration",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (corpus / "normalized_docs.jsonl").write_text(
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
                        "text": "머신 구성 초안 문서입니다.",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (corpus / "chunks.jsonl").write_text(
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
                        "text": "머신 구성 초안 문서입니다.",
                        "token_count": 6,
                        "ordinal": 0,
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (raw_html / "machine_configuration.html").write_text(
                "<html><body><article><h1>Machine configuration</h1></article></body></html>",
                encoding="utf-8",
            )

            settings = self._corpus_settings(
                root,
                source_catalog_path=source_catalog_path,
                translation_draft_manifest_path=translated_manifest_path,
            )

            report = build_source_approval_report(settings)

        self.assertEqual("translated_ko_draft", report["books"][0]["content_status"])
        self.assertEqual("머신 구성", report["books"][0]["title"])
        self.assertEqual("en", report["books"][0]["translation_lane"]["source_language"])

    def test_source_approval_report_preserves_approved_manual_synthesis_overlay(self) -> None:
        with self._workspace() as root:
            manifests, corpus, raw_html = self._audit_layout(root, corpus_dir_name="corpus")

            source_catalog_path = manifests / "ocp_multiversion_html_single_catalog.json"
            source_catalog_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 1,
                        "entries": [
                            {
                                "product_slug": "openshift_container_platform",
                                "ocp_version": "4.20",
                                "docs_language": "ko",
                                "source_kind": "html-single",
                                "book_slug": "etcd",
                                "title": "etcd",
                                "source_url": "https://example.com/etcd",
                                "resolved_source_url": "https://example.com/etcd",
                                "resolved_language": "ko",
                                "viewer_path": "/docs/ocp/4.20/ko/etcd/index.html",
                                "high_value": True,
                                "source_fingerprint": "fp-etcd",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            approved_manifest_path = manifests / "ocp_ko_4_20_approved_ko.json"
            approved_manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 1,
                        "entries": [
                            {
                                "product_slug": "openshift_container_platform",
                                "ocp_version": "4.20",
                                "docs_language": "ko",
                                "source_kind": "html-single",
                                "book_slug": "etcd",
                                "title": "etcd 백업 및 복구 플레이북",
                                "source_url": "https://example.com/etcd",
                                "resolved_source_url": "https://example.com/etcd",
                                "resolved_language": "ko",
                                "viewer_path": "/docs/ocp/4.20/ko/etcd/index.html",
                                "high_value": True,
                                "source_fingerprint": "fp-etcd",
                                "content_status": "approved_ko",
                                "approval_status": "approved",
                                "review_status": "approved",
                                "source_type": "manual_synthesis",
                                "source_lane": "applied_playbook",
                                "source_collection": "core",
                                "original_title": "Disaster recovery",
                                "trust_score": 0.98,
                                "translation_source_language": "en",
                                "translation_target_language": "ko",
                                "translation_source_url": "https://example.com/en/etcd",
                                "translation_source_fingerprint": "fp-etcd-en",
                                "translation_stage": "approved_ko",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            translated_manifest_path = manifests / "ocp_ko_4_20_translated_ko_draft.json"
            translated_manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 1,
                        "entries": [
                            {
                                "product_slug": "openshift_container_platform",
                                "ocp_version": "4.20",
                                "docs_language": "ko",
                                "source_kind": "html-single",
                                "book_slug": "etcd",
                                "title": "etcd draft",
                                "source_url": "https://example.com/etcd",
                                "resolved_source_url": "https://example.com/en/etcd",
                                "resolved_language": "en",
                                "viewer_path": "/docs/ocp/4.20/ko/etcd/index.html",
                                "high_value": True,
                                "source_fingerprint": "fp-etcd",
                                "content_status": "translated_ko_draft",
                                "approval_status": "needs_review",
                                "review_status": "needs_review",
                                "source_type": "official_doc",
                                "translation_source_language": "en",
                                "translation_target_language": "ko",
                                "translation_source_url": "https://example.com/en/etcd",
                                "translation_source_fingerprint": "fp-etcd-en",
                                "translation_stage": "translated_ko_draft",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (corpus / "normalized_docs.jsonl").write_text("", encoding="utf-8")
            (corpus / "chunks.jsonl").write_text("", encoding="utf-8")

            settings = self._corpus_settings(
                root,
                source_catalog_path=source_catalog_path,
                source_manifest_path=approved_manifest_path,
                translation_draft_manifest_path=translated_manifest_path,
            )

            report = build_source_approval_report(settings)
            entries = build_approved_manifest(settings)

        self.assertEqual(1, report["summary"]["approved_ko_count"])
        self.assertEqual(0, report["summary"]["high_value_issue_count"])
        self.assertEqual("approved_ko", report["books"][0]["content_status"])
        self.assertEqual("manual_synthesis", report["books"][0]["source_type"])
        self.assertEqual(1, len(entries))
        self.assertEqual("manual_synthesis", entries[0].source_type)
        self.assertEqual("approved", entries[0].review_status)
        self.assertEqual("approved_ko", entries[0].translation_stage)

    def test_build_approved_manifest_backfills_approved_manual_synthesis_from_playbook_documents(self) -> None:
        with self._workspace() as root:
            manifests, corpus, raw_html = self._audit_layout(root, corpus_dir_name="corpus")
            gold_manualbook = self._ensure_dir(root / "data" / "gold_manualbook_ko")

            source_catalog_path = manifests / "ocp_multiversion_html_single_catalog.json"
            source_catalog_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 1,
                        "entries": [
                            {
                                "product_slug": "openshift_container_platform",
                                "ocp_version": "4.20",
                                "docs_language": "ko",
                                "source_kind": "html-single",
                                "book_slug": "backup_and_restore",
                                "title": "Backup and restore",
                                "source_url": "https://example.com/backup_and_restore",
                                "resolved_source_url": "https://example.com/backup_and_restore",
                                "resolved_language": "ko",
                                "viewer_path": "/docs/ocp/4.20/ko/backup_and_restore/index.html",
                                "high_value": True,
                                "source_fingerprint": "fp-backup",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            approved_manifest_path = manifests / "ocp_ko_4_20_approved_ko.json"
            approved_manifest_path.write_text(
                json.dumps({"version": 1, "source": "test", "count": 0, "entries": []}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (corpus / "normalized_docs.jsonl").write_text("", encoding="utf-8")
            (corpus / "chunks.jsonl").write_text("", encoding="utf-8")
            (gold_manualbook / "playbook_documents.jsonl").write_text(
                json.dumps(
                    {
                        "book_slug": "backup_and_restore",
                        "title": "컨트롤 플레인 백업/복구 플레이북",
                        "version": "4.20",
                        "locale": "ko",
                        "source_uri": "https://example.com/backup_and_restore",
                        "translation_status": "approved_ko",
                        "review_status": "approved",
                        "source_metadata": {
                            "source_id": "manual_synthesis:backup_and_restore",
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                            "source_collection": "core",
                        },
                        "anchor_map": {
                            "overview": "/docs/ocp/4.20/ko/backup_and_restore/index.html#overview"
                        },
                        "sections": [],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            settings = self._corpus_settings(
                root,
                source_catalog_path=source_catalog_path,
                source_manifest_path=approved_manifest_path,
                playbook_documents_path=gold_manualbook / "playbook_documents.jsonl",
            )

            report = build_source_approval_report(settings)
            entries = build_approved_manifest(settings)

        self.assertEqual(1, report["summary"]["approved_ko_count"])
        self.assertEqual(0, report["summary"]["high_value_issue_count"])
        self.assertEqual("backup_and_restore", report["books"][0]["book_slug"])
        self.assertEqual("approved_ko", report["books"][0]["content_status"])
        self.assertEqual("manual_synthesis", report["books"][0]["source_type"])
        self.assertEqual(1, len(entries))
        self.assertEqual("backup_and_restore", entries[0].book_slug)
        self.assertEqual("manual_synthesis", entries[0].source_type)
        self.assertEqual("approved", entries[0].approval_status)

    def test_source_approval_report_preserves_manual_synthesis_with_heading_warning(self) -> None:
        with self._workspace() as root:
            manifests, corpus, raw_html = self._audit_layout(root, corpus_dir_name="corpus")
            playbooks = self._ensure_dir(corpus / "playbooks")

            source_catalog_path = manifests / "ocp_multiversion_html_single_catalog.json"
            source_catalog_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 1,
                        "entries": [
                            {
                                "product_slug": "openshift_container_platform",
                                "ocp_version": "4.20",
                                "docs_language": "ko",
                                "source_kind": "html-single",
                                "book_slug": "monitoring",
                                "title": "Monitoring",
                                "source_url": "https://example.com/monitoring",
                                "resolved_source_url": "https://example.com/monitoring",
                                "resolved_language": "ko",
                                "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html",
                                "high_value": True,
                                "source_fingerprint": "fp-monitoring",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            approved_manifest_path = manifests / "ocp_ko_4_20_approved_ko.json"
            approved_manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 1,
                        "entries": [
                            {
                                "product_slug": "openshift_container_platform",
                                "ocp_version": "4.20",
                                "docs_language": "ko",
                                "source_kind": "html-single",
                                "book_slug": "monitoring",
                                "title": "모니터링 운영 플레이북",
                                "source_url": "https://example.com/monitoring",
                                "resolved_source_url": "https://example.com/monitoring",
                                "resolved_language": "ko",
                                "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html",
                                "high_value": True,
                                "source_fingerprint": "fp-monitoring",
                                "content_status": "approved_ko",
                                "approval_status": "approved",
                                "review_status": "approved",
                                "source_type": "manual_synthesis",
                                "source_lane": "applied_playbook",
                                "translation_stage": "approved_ko",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (corpus / "normalized_docs.jsonl").write_text("", encoding="utf-8")
            (corpus / "chunks.jsonl").write_text("", encoding="utf-8")
            (playbooks / "monitoring.json").write_text(
                json.dumps(
                    {
                        "book_slug": "monitoring",
                        "title": "Monitoring",
                        "translation_status": "approved_ko",
                        "source_metadata": {
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                        },
                        "sections": [
                            {
                                "heading": "Overview",
                                "semantic_role": "procedure",
                                "blocks": [],
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            settings = self._corpus_settings(
                root,
                source_catalog_path=source_catalog_path,
                source_manifest_path=approved_manifest_path,
                playbook_books_dir=playbooks,
            )

            report = build_source_approval_report(settings)
            entries = build_approved_manifest(settings)

        self.assertEqual(1, report["summary"]["approved_ko_count"])
        self.assertEqual(0, report["summary"]["high_value_issue_count"])
        self.assertEqual("approved_ko", report["books"][0]["content_status"])
        self.assertEqual("approved", report["books"][0]["approval_status"])
        self.assertEqual("approved", report["books"][0]["review_status"])
        self.assertFalse(report["books"][0]["manualbook_reader_grade_failed"])
        self.assertEqual(1, len(entries))
        self.assertEqual("monitoring", entries[0].book_slug)

    def test_source_approval_report_respects_bundle_dossier_over_generated_korean_artifacts(self) -> None:
        with self._workspace() as root:
            manifests, corpus, raw_html = self._audit_layout(root, corpus_dir_name="corpus")
            source_bundles = self._ensure_dir(corpus / "source_bundles")

            source_catalog_path = manifests / "ocp_multiversion_html_single_catalog.json"
            source_catalog_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "test",
                        "count": 2,
                        "entries": [
                            {
                                "product_slug": "openshift_container_platform",
                                "ocp_version": "4.20",
                                "docs_language": "ko",
                                "source_kind": "html-single",
                                "book_slug": "architecture",
                                "title": "아키텍처",
                                "source_url": "https://example.com/architecture",
                                "resolved_source_url": "https://example.com/architecture",
                                "resolved_language": "ko",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                                "high_value": True,
                            },
                            {
                                "product_slug": "openshift_container_platform",
                                "ocp_version": "4.20",
                                "docs_language": "ko",
                                "source_kind": "html-single",
                                "book_slug": "machine_configuration",
                                "title": "머신 구성",
                                "source_url": "https://example.com/machine_configuration",
                                "resolved_source_url": "https://example.com/machine_configuration",
                                "resolved_language": "ko",
                                "viewer_path": "/docs/ocp/4.20/ko/machine_configuration/index.html",
                                "high_value": True,
                            },
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
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
                    "text": "아키텍처 문서입니다.",
                },
                {
                    "book_slug": "machine_configuration",
                    "book_title": "머신 구성",
                    "heading": "개요",
                    "section_level": 1,
                    "section_path": ["개요"],
                    "anchor": "overview",
                    "source_url": "https://example.com/machine_configuration",
                    "viewer_path": "/docs/ocp/4.20/ko/machine_configuration/index.html#overview",
                    "text": "머신 구성 문서입니다.",
                },
            ]
            (corpus / "normalized_docs.jsonl").write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in normalized_rows) + "\n",
                encoding="utf-8",
            )
            chunk_rows = [
                {
                    "chunk_id": "architecture-1",
                    "book_slug": "architecture",
                    "book_title": "아키텍처",
                    "chapter": "아키텍처",
                    "section": "개요",
                    "anchor": "overview",
                    "source_url": "https://example.com/architecture",
                    "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                    "text": "아키텍처 문서입니다.",
                    "token_count": 4,
                    "ordinal": 0,
                },
                {
                    "chunk_id": "machine-1",
                    "book_slug": "machine_configuration",
                    "book_title": "머신 구성",
                    "chapter": "머신 구성",
                    "section": "개요",
                    "anchor": "overview",
                    "source_url": "https://example.com/machine_configuration",
                    "viewer_path": "/docs/ocp/4.20/ko/machine_configuration/index.html#overview",
                    "text": "머신 구성 문서입니다.",
                    "token_count": 4,
                    "ordinal": 0,
                },
            ]
            (corpus / "chunks.jsonl").write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in chunk_rows) + "\n",
                encoding="utf-8",
            )
            (raw_html / "architecture.html").write_text(
                "<html><body><article><h1>아키텍처</h1></article></body></html>",
                encoding="utf-8",
            )
            (raw_html / "machine_configuration.html").write_text(
                "<html><body><article><h1>머신 구성</h1></article></body></html>",
                encoding="utf-8",
            )
            bundle = source_bundles / "machine_configuration"
            bundle.mkdir(parents=True)
            (bundle / "dossier.json").write_text(
                json.dumps(
                    {
                        "current_status": {
                            "content_status": "translated_ko_draft",
                            "gap_lane": "translation_first",
                        }
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            settings = self._corpus_settings(root, source_catalog_path=source_catalog_path)

            report = build_source_approval_report(settings)
            approved_entries = build_approved_manifest(settings)

        rows = {row["book_slug"]: row for row in report["books"]}
        self.assertEqual("approved_ko", rows["architecture"]["content_status"])
        self.assertEqual("translated_ko_draft", rows["machine_configuration"]["content_status"])
        self.assertEqual(1, report["summary"]["approved_ko_count"])
        self.assertEqual(1, report["summary"]["high_value_issue_count"])
        self.assertEqual(["architecture"], [entry.book_slug for entry in approved_entries])


if __name__ == "__main__":
    unittest.main()
