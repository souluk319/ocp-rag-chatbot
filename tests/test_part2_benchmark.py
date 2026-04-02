from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part2.benchmark import summarize_results


class BenchmarkTests(unittest.TestCase):
    def test_summarize_results_reports_overall_and_category_rates(self) -> None:
        details = [
            {
                "category": "ops",
                "mode": "ops",
                "matched_at_1": True,
                "matched_at_3": True,
                "matched_at_5": True,
                "warnings": [],
            },
            {
                "category": "ops",
                "mode": "ops",
                "matched_at_1": False,
                "matched_at_3": True,
                "matched_at_5": True,
                "warnings": ["vector search failed"],
            },
            {
                "category": "followup",
                "mode": "learn",
                "matched_at_1": False,
                "matched_at_3": False,
                "matched_at_5": True,
                "warnings": [],
            },
        ]

        report = summarize_results(details, top_k=5, candidate_k=20)

        self.assertEqual(3, report["case_count"])
        self.assertEqual(1, report["warning_count"])
        self.assertEqual(0.3333, report["overall"]["hit_at_1"])
        self.assertEqual(0.6667, report["overall"]["hit_at_3"])
        self.assertEqual(1.0, report["overall"]["hit_at_5"])
        self.assertEqual(1.0, report["by_category"]["ops"]["hit_at_5"])
        self.assertEqual(1.0, report["by_mode"]["learn"]["hit_at_5"])


if __name__ == "__main__":
    unittest.main()
