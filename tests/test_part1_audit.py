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

from ocp_rag_part1.audit import build_data_quality_report, looks_like_mojibake_title


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
                source_manifest_path=manifests / "ocp_ko_4_20_html_single.json",
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


if __name__ == "__main__":
    unittest.main()
