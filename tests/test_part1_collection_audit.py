from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.collection_audit import classify_collection_status, extract_book_xml_lang


class CollectionAuditTests(unittest.TestCase):
    def test_extract_book_xml_lang_reads_book_wrapper_language(self) -> None:
        html = '<div xml:lang="ko-KR" class="book"><h1>아키텍처</h1></div>'

        self.assertEqual("ko-KR", extract_book_xml_lang(html))

    def test_classify_collection_status_marks_vendor_english_fallback(self) -> None:
        status = classify_collection_status(
            source_url=(
                "https://docs.redhat.com/ko/documentation/"
                "openshift_container_platform/4.20/html-single/backup_and_restore/index"
            ),
            xml_lang="en-US",
            raw_exists=True,
        )

        self.assertEqual("vendor_english_fallback", status)

    def test_classify_collection_status_marks_ko_variant_ok(self) -> None:
        status = classify_collection_status(
            source_url=(
                "https://docs.redhat.com/ko/documentation/"
                "openshift_container_platform/4.20/html-single/architecture/index"
            ),
            xml_lang="ko-KR",
            raw_exists=True,
        )

        self.assertEqual("ko_variant_ok", status)


if __name__ == "__main__":
    unittest.main()
