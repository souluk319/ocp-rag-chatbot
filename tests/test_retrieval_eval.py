from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.evals.retrieval_eval import summarize_case_results


class RetrievalEvalTests(unittest.TestCase):
    def test_summarize_case_results_tracks_hit_rates(self) -> None:
        cases = [
            {
                "mode": "ops",
                "query_type": "ops",
                "query": "q1",
                "expected_book_slugs": ["a"],
                "top_book_slugs": ["a", "b", "c"],
                "warnings": [],
            },
            {
                "mode": "learn",
                "query_type": "follow_up",
                "query": "q2",
                "expected_book_slugs": ["z"],
                "top_book_slugs": ["x", "z", "y"],
                "warnings": ["vector warning"],
            },
        ]

        summary = summarize_case_results(cases)

        self.assertEqual(2, summary["case_count"])
        self.assertEqual(0.5, summary["overall"]["hit@1"])
        self.assertEqual(1.0, summary["overall"]["hit@3"])
        self.assertEqual(0.5, summary["overall"]["warning_free_rate"])
        self.assertEqual(0, len(summary["misses"]))


if __name__ == "__main__":
    unittest.main()
