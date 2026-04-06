from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.answering.eval import summarize_case_results


class Part3EvalTests(unittest.TestCase):
    def test_summarize_case_results_tracks_guardrail_rates(self) -> None:
        details = [
            {
                "mode": "ops",
                "query_type": "ops",
                "question": "q1",
                "expected_book_slugs": ["etcd"],
                "forbidden_book_slugs": [],
                "clarification_expected": False,
                "no_answer_expected": False,
                "has_answer": True,
                "has_korean": True,
                "answer_format_valid": True,
                "has_inline_citations": True,
                "citation_indices_valid": True,
                "clarification_detected": False,
                "no_answer_detected": False,
                "clarification_needed_but_answered": False,
                "no_evidence_but_asserted": False,
                "must_include_pass": True,
                "must_exclude_pass": True,
                "cited_expected_book": True,
                "has_unexpected_citation": False,
                "strict_expected_only": True,
                "citation_precision": 1.0,
                "warning_free": True,
                "pass": True,
                "cited_books": ["etcd"],
                "retrieved_books": ["etcd", "backup_and_restore"],
                "answer_text": "답변: 예시 [1]",
                "final_citations": [],
                "missing_required_terms": [],
                "forbidden_answer_terms": [],
            },
            {
                "mode": "ops",
                "query_type": "clarification_required",
                "question": "q2",
                "expected_book_slugs": ["images"],
                "forbidden_book_slugs": ["support"],
                "clarification_expected": True,
                "no_answer_expected": False,
                "has_answer": True,
                "has_korean": True,
                "answer_format_valid": True,
                "has_inline_citations": True,
                "citation_indices_valid": True,
                "clarification_detected": False,
                "no_answer_detected": False,
                "clarification_needed_but_answered": True,
                "no_evidence_but_asserted": False,
                "must_include_pass": False,
                "must_exclude_pass": True,
                "cited_expected_book": True,
                "has_unexpected_citation": True,
                "strict_expected_only": False,
                "citation_precision": 0.5,
                "warning_free": True,
                "pass": False,
                "cited_books": ["images", "support"],
                "retrieved_books": ["images", "support"],
                "answer_text": "답변: 단정적으로 답함 [1][2]",
                "final_citations": [],
                "rewritten_query": "rewritten q2",
                "unexpected_cited_books": ["support"],
                "forbidden_cited_books": ["support"],
                "missing_required_terms": ["확인"],
                "forbidden_answer_terms": [],
                "cited_indices": [1, 2],
                "warnings": [],
            },
            {
                "mode": "learn",
                "query_type": "negative",
                "question": "q3",
                "expected_book_slugs": [],
                "forbidden_book_slugs": [],
                "clarification_expected": False,
                "no_answer_expected": True,
                "has_answer": True,
                "has_korean": True,
                "answer_format_valid": True,
                "has_inline_citations": False,
                "citation_indices_valid": True,
                "clarification_detected": False,
                "no_answer_detected": True,
                "clarification_needed_but_answered": False,
                "no_evidence_but_asserted": False,
                "must_include_pass": True,
                "must_exclude_pass": False,
                "cited_expected_book": False,
                "has_unexpected_citation": False,
                "strict_expected_only": True,
                "citation_precision": 0.0,
                "warning_free": False,
                "pass": True,
                "cited_books": [],
                "retrieved_books": ["overview"],
                "answer_text": "답변: 제공된 문서만으로는 확인할 수 없습니다.",
                "final_citations": [],
                "missing_required_terms": [],
                "forbidden_answer_terms": ["최신"],
            },
        ]

        summary = summarize_case_results(details)

        self.assertEqual(3, summary["case_count"])
        self.assertEqual(1.0, summary["overall"]["answer_present_rate"])
        self.assertEqual(0.3333, summary["overall"]["unexpected_citation_rate"])
        self.assertEqual(1.0, summary["overall"]["clarification_needed_but_answered_rate"])
        self.assertEqual(0.0, summary["overall"]["no_evidence_but_asserted_rate"])
        self.assertEqual(0.6667, summary["overall"]["must_include_rate"])
        self.assertEqual(0.6667, summary["overall"]["must_exclude_rate"])
        self.assertEqual(0.5, summary["overall"]["avg_citation_precision"])
        self.assertEqual(0.6667, summary["overall"]["pass_rate"])
        self.assertEqual(1, len(summary["failures"]))


if __name__ == "__main__":
    unittest.main()
