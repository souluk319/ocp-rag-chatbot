from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.retrieval.query_terms import normalize_query


class QueryTermsCoreTests(unittest.TestCase):
    def test_generic_openshift_intro_query_uses_compact_intro_terms(self) -> None:
        normalized = normalize_query("오픈시프트가 뭐야")

        self.assertEqual("오픈시프트가 뭐야 개요 플랫폼", normalized)
        self.assertNotIn("소개", normalized)
        self.assertNotIn("기본", normalized)
        self.assertNotIn("개념", normalized)

    def test_generic_kubernetes_intro_query_uses_compact_intro_terms(self) -> None:
        normalized = normalize_query("쿠버네티스가 뭐야")

        self.assertEqual("쿠버네티스가 뭐야 개요 플랫폼", normalized)
        self.assertNotIn("소개", normalized)
        self.assertNotIn("기본", normalized)
        self.assertNotIn("개념", normalized)


if __name__ == "__main__":
    unittest.main()
