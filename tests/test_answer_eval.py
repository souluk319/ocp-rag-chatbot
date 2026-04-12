from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.evals.answer_eval import summarize_case_results


class AnswerEvalTests(unittest.TestCase):
    def test_summarize_case_results_tracks_guardrail_rates(self) -> None:
        details = [
            {
                "id": "case-1",
                "mode": "ops",
                "query_type": "ops",
                "failure_bucket_hint": "",
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
                "warnings": [],
                "quality_flags": [],
            },
            {
                "id": "case-2",
                "mode": "ops",
                "query_type": "clarification_required",
                "failure_bucket_hint": "clarification",
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
                "quality_flags": [],
            },
            {
                "id": "case-3",
                "mode": "learn",
                "query_type": "negative",
                "failure_bucket_hint": "",
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
                "warnings": ["outside OCP corpus"],
                "quality_flags": ["warning_present"],
            },
        ]

        summary = summarize_case_results(details)

        self.assertEqual(3, summary["case_count"])
        self.assertEqual(1.0, summary["overall"]["answer_present_rate"])
        self.assertEqual(0.3333, summary["overall"]["unexpected_citation_rate"])
        self.assertEqual(0.0, summary["overall"]["pass_with_provenance_noise_rate"])
        self.assertEqual(1.0, summary["overall"]["clarification_needed_but_answered_rate"])
        self.assertEqual(0.0, summary["overall"]["no_evidence_but_asserted_rate"])
        self.assertEqual(0.6667, summary["overall"]["must_include_rate"])
        self.assertEqual(0.6667, summary["overall"]["must_exclude_rate"])
        self.assertEqual(0.5, summary["overall"]["avg_citation_precision"])
        self.assertEqual(0.6667, summary["overall"]["pass_rate"])
        self.assertEqual(1, len(summary["failures"]))
        self.assertEqual("generation", summary["failures"][0]["root_cause_tag"])
        self.assertEqual("clarification", summary["failures"][0]["failure_bucket_hint"])
        self.assertIn("clarification gate missed", summary["failures"][0]["root_cause_reason"])
        self.assertEqual("insufficient", summary["realworld_assessment"]["status"])
        self.assertEqual(1, summary["realworld_assessment"]["failed_case_count"])
        self.assertEqual(
            1,
            summary["realworld_assessment"]["root_cause_counts"]["generation"],
        )
        self.assertEqual([], summary["realworld_assessment"]["provenance_noise_case_ids"])

    def test_summarize_case_results_marks_sufficient_with_provenance_noise(self) -> None:
        details = [
            {
                "id": "case-noise",
                "mode": "learn",
                "query_type": "learn",
                "failure_bucket_hint": "topic_family_noise",
                "question": "q-noise",
                "expected_book_slugs": ["overview"],
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
                "has_unexpected_citation": True,
                "strict_expected_only": False,
                "citation_precision": 0.5,
                "warning_free": True,
                "pass": True,
                "cited_books": ["overview", "architecture"],
                "retrieved_books": ["overview", "architecture"],
                "unexpected_cited_books": ["architecture"],
                "forbidden_cited_books": [],
                "answer_text": "답변: 예시 [1][2]",
                "final_citations": [],
                "missing_required_terms": [],
                "forbidden_answer_terms": [],
                "warnings": [],
                "quality_flags": ["provenance_noise"],
            }
        ]

        summary = summarize_case_results(details)

        self.assertEqual(1.0, summary["overall"]["pass_rate"])
        self.assertEqual(1.0, summary["overall"]["pass_with_provenance_noise_rate"])
        self.assertEqual(
            "sufficient_with_provenance_noise",
            summary["realworld_assessment"]["status"],
        )
        self.assertEqual(
            ["case-noise"],
            summary["realworld_assessment"]["provenance_noise_case_ids"],
        )
        self.assertEqual({}, summary["realworld_assessment"]["root_cause_counts"])


if __name__ == "__main__":
    unittest.main()
