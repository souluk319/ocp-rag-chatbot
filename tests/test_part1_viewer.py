from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.models import NormalizedSection
from ocp_rag_part1.settings import Settings
from ocp_rag_part1.viewer import render_book_viewer, write_viewer_docs


class Part1ViewerTests(unittest.TestCase):
    def test_render_book_viewer_includes_heading_anchor_and_code_block(self) -> None:
        html = render_book_viewer(
            "architecture",
            [
                NormalizedSection(
                    book_slug="architecture",
                    book_title="아키텍처",
                    heading="OpenShift Container Platform의 아키텍처 개요",
                    section_level=1,
                    section_path=["아키텍처"],
                    anchor="overview",
                    source_url="https://example.com/architecture",
                    viewer_path="/docs/ocp/4.20/ko/architecture/index.html#overview",
                    text="첫 문단입니다.\n\n[CODE]\noc get nodes\n[/CODE]",
                )
            ],
            policy={
                "language_status": "ko_first",
                "recommended_action": "keep",
                "translation_priority": "none",
            },
        )

        self.assertIn("OpenShift Container Platform의 아키텍처 개요", html)
        self.assertIn('id="overview"', html)
        self.assertIn("<pre><code>oc get nodes</code></pre>", html)
        self.assertIn("한국어 우선", html)

    def test_render_book_viewer_shows_translation_priority_badge_for_english_first_book(self) -> None:
        html = render_book_viewer(
            "backup_and_restore",
            [
                NormalizedSection(
                    book_slug="backup_and_restore",
                    book_title="Backup and restore",
                    heading="Backup and restore",
                    section_level=1,
                    section_path=["Backup and restore"],
                    anchor="backup-overview",
                    source_url="https://example.com/backup",
                    viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html#backup-overview",
                    text="Restore the cluster from a backup.",
                )
            ],
            policy={
                "language_status": "en_first",
                "recommended_action": "translate_priority",
                "translation_priority": "urgent",
            },
        )

        self.assertIn("영문 우선", html)
        self.assertIn("번역 우선", html)

    def test_write_viewer_docs_writes_book_index_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(Path(tmpdir))
            sections = [
                NormalizedSection(
                    book_slug="etcd",
                    book_title="etcd",
                    heading="etcd 재해 복구",
                    section_level=1,
                    section_path=["etcd"],
                    anchor="dr-overview",
                    source_url="https://example.com/etcd",
                    viewer_path="/docs/ocp/4.20/ko/etcd/index.html#dr-overview",
                    text="복구 절차 설명",
                )
            ]

            written = write_viewer_docs(sections, settings)

            target = settings.viewer_docs_dir / "etcd" / "index.html"
            self.assertEqual(1, written)
            self.assertTrue(target.exists())
            self.assertIn("복구 절차 설명", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
