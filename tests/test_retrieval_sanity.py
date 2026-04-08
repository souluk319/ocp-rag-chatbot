from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.evals.sanity import summarize_results


class RetrievalSanityTests(unittest.TestCase):
    def test_summarize_results_tracks_expected_and_forbidden_rates(self) -> None:
        details = [
            {
                "id": "case-1",
                "category": "broad-intro",
                "mode": "learn",
                "query": "q1",
                "expected_book_slugs": ["overview"],
                "forbidden_book_slugs": ["installing_on_a_single_node"],
                "expected_hit_at_1": True,
                "expected_hit_at_3": True,
                "expected_hit_at_5": True,
                "forbidden_hit_at_1": False,
                "forbidden_hit_at_3": False,
                "forbidden_hit_at_5": False,
                "must_clarify": False,
                "must_refuse": False,
                "rewritten_query": "q1",
                "top_book_slugs": ["overview", "architecture"],
                "trace": {"warnings": []},
            },
            {
                "id": "case-2",
                "category": "unsupported",
                "mode": "ops",
                "query": "q2",
                "expected_book_slugs": [],
                "forbidden_book_slugs": ["installing_on_a_single_node"],
                "expected_hit_at_1": False,
                "expected_hit_at_3": False,
                "expected_hit_at_5": False,
                "forbidden_hit_at_1": True,
                "forbidden_hit_at_3": True,
                "forbidden_hit_at_5": True,
                "must_clarify": False,
                "must_refuse": True,
                "rewritten_query": "q2",
                "top_book_slugs": ["installing_on_a_single_node"],
                "trace": {"warnings": ["vector warning"]},
            },
        ]

        report = summarize_results(details)

        self.assertEqual(2, report["case_count"])
        self.assertEqual(1.0, report["overall"]["expected_hit_at_1"])
        self.assertEqual(0.5, report["overall"]["forbidden_free_at_1"])
        self.assertEqual(0.5, report["overall"]["warning_free_rate"])
        self.assertEqual(1, report["overall"]["refuse_case_count"])
        self.assertEqual(1, len(report["misses"]))


if __name__ == "__main__":
    unittest.main()
