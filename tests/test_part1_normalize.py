from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.models import SourceManifestEntry
from ocp_rag_part1.normalize import extract_sections


class NormalizeTests(unittest.TestCase):
    def test_extract_sections_skips_noise_headings(self) -> None:
        html = """
        <html>
          <body>
            <main id="main-content">
              <article>
                <h1>테스트 문서</h1>
                <h2 id="intro">소개</h2>
                <p>한국어 설명입니다.</p>
                <h2 id="legal">Legal Notice</h2>
                <p>Copyright 2026 Red Hat</p>
                <h3 id="fallback">이 콘텐츠는 선택한 언어로 제공되지 않습니다.</h3>
                <p>OpenShift Container Platform 4.20</p>
              </article>
            </main>
          </body>
        </html>
        """
        entry = SourceManifestEntry(
            book_slug="test_book",
            title="테스트 문서",
            source_url="https://example.com/test",
            viewer_path="/docs/test/index.html",
            high_value=True,
        )

        sections = extract_sections(html, entry)

        self.assertEqual(1, len(sections))
        self.assertEqual("소개", sections[0].heading)
        self.assertIn("한국어 설명", sections[0].text)


if __name__ == "__main__":
    unittest.main()
