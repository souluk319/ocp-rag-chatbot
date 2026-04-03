from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.language_policy import classify_book_language_policy


class LanguagePolicyTests(unittest.TestCase):
    def test_high_value_english_book_becomes_translate_priority(self) -> None:
        policy = classify_book_language_policy(
            book_slug="backup_and_restore",
            title="Backup and restore",
            high_value=True,
            section_count=448,
            hangul_section_ratio=0.0,
        )

        self.assertEqual("en_first", policy["language_status"])
        self.assertEqual("allow_with_warning", policy["retrieval_policy"])
        self.assertEqual("translate_priority", policy["recommended_action"])
        self.assertEqual("urgent", policy["translation_priority"])

    def test_low_priority_english_book_is_excluded_by_default(self) -> None:
        policy = classify_book_language_policy(
            book_slug="custom_low_value_book",
            title="Custom low value book",
            high_value=False,
            section_count=20,
            hangul_section_ratio=0.0,
        )

        self.assertEqual("exclude_default", policy["retrieval_policy"])
        self.assertEqual("exclude_default", policy["recommended_action"])

    def test_korean_first_book_stays_normal(self) -> None:
        policy = classify_book_language_policy(
            book_slug="architecture",
            title="아키텍처",
            high_value=True,
            section_count=92,
            hangul_section_ratio=1.0,
        )

        self.assertEqual("ko_first", policy["language_status"])
        self.assertEqual("normal", policy["retrieval_policy"])
        self.assertEqual("keep", policy["recommended_action"])


if __name__ == "__main__":
    unittest.main()
