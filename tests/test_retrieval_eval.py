from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.evals.retrieval_eval import summarize_case_results
from play_book_studio.evals.retrieval_eval import build_graph_sidecar_evidence_packet
from play_book_studio.evals.retrieval_eval import classify_graph_signal


class RetrievalEvalTests(unittest.TestCase):
    def test_classify_graph_signal_marks_clean_when_expected_family_is_ranked_first(self) -> None:
        signal, reason = classify_graph_signal(
            {
                "query_type": "ops",
                "expected_book_slugs": ["backup_and_restore"],
                "top_book_slugs": ["backup_and_restore", "etcd"],
                "warnings": [],
            },
            max_k=5,
        )

        self.assertEqual("clean", signal)
        self.assertIn("ranked first", reason)

    def test_classify_graph_signal_prefers_similar_document_when_expected_family_exists_within_cutoff(self) -> None:
        signal, reason = classify_graph_signal(
            {
                "query_type": "follow-up",
                "expected_book_slugs": ["backup_and_restore"],
                "top_book_slugs": ["etcd", "backup_and_restore", "disaster_recovery"],
                "warnings": [],
            },
            max_k=5,
        )

        self.assertEqual("similar-document", signal)
        self.assertIn("lost rank", reason)

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
        self.assertEqual(0.5, summary["overall"]["similar_document_risk_rate"])
        self.assertEqual(1, summary["graph_signal_counts"]["similar-document"])
        self.assertEqual(0, len(summary["misses"]))

    def test_summarize_case_results_tags_policy_and_relation_misses(self) -> None:
        cases = [
            {
                "id": "policy-1",
                "mode": "ops",
                "query_type": "ops",
                "query": "argo cd 설치 절차",
                "expected_book_slugs": [],
                "top_book_slugs": [],
                "warnings": ["query appears outside OCP corpus: argo cd"],
            },
            {
                "id": "followup-1",
                "mode": "ops",
                "query_type": "follow-up",
                "query": "그 복구는?",
                "expected_book_slugs": ["backup_and_restore"],
                "top_book_slugs": ["support", "overview"],
                "warnings": [],
            },
        ]

        summary = summarize_case_results(cases)

        self.assertEqual(0.5, summary["overall"]["policy_overlay_warning_rate"])
        self.assertEqual(0.5, summary["overall"]["relation_aware_miss_rate"])
        self.assertEqual(1, summary["graph_signal_counts"]["policy-overlay"])
        self.assertEqual(1, summary["graph_signal_counts"]["relation-aware-retrieval"])
        self.assertEqual("policy-overlay", summary["misses"][0]["graph_signal_tag"])
        self.assertEqual("relation-aware-retrieval", summary["misses"][1]["graph_signal_tag"])

    def test_summarize_case_results_exposes_stage_ablation_metrics(self) -> None:
        cases = [
            {
                "id": "case-1",
                "mode": "ops",
                "query_type": "ops",
                "query": "etcd 백업은 어떻게 해?",
                "expected_book_slugs": ["backup_and_restore"],
                "top_book_slugs": ["backup_and_restore", "etcd"],
                "bm25_top_book_slugs": ["backup_and_restore", "etcd"],
                "vector_top_book_slugs": ["support", "etcd"],
                "hybrid_top_book_slugs": ["backup_and_restore", "etcd"],
                "reranked_top_book_slugs": ["backup_and_restore", "etcd"],
                "rewrite_applied": True,
                "follow_up_detected": True,
                "rewrite_reason": "follow_up_reference",
                "vector_endpoint_used": "points/search",
                "hybrid_top_support": "both",
                "rerank_top1_changed": True,
                "rerank_reasons": ["support rescue"],
                "warnings": [],
            },
            {
                "id": "case-2",
                "mode": "ops",
                "query_type": "follow-up",
                "query": "그 복구는?",
                "expected_book_slugs": ["backup_and_restore"],
                "top_book_slugs": ["backup_and_restore", "support"],
                "bm25_top_book_slugs": ["support", "etcd"],
                "vector_top_book_slugs": [],
                "hybrid_top_book_slugs": ["support", "backup_and_restore"],
                "reranked_top_book_slugs": ["backup_and_restore", "support"],
                "rewrite_applied": False,
                "follow_up_detected": False,
                "rewrite_reason": "",
                "vector_endpoint_used": "points/query",
                "hybrid_top_support": "bm25",
                "rerank_top1_changed": False,
                "rerank_reasons": [],
                "warnings": [],
            },
        ]

        summary = summarize_case_results(cases)

        self.assertIn("stage_ablation", summary)
        stage_ablation = summary["stage_ablation"]
        stages = stage_ablation["stages"]
        self.assertEqual(0.5, stages["bm25"]["hit@1"])
        self.assertEqual(0.0, stages["vector"]["hit@1"])
        self.assertEqual(0.5, stages["hybrid"]["hit@1"])
        self.assertEqual(1.0, stages["reranked"]["hit@1"])
        self.assertEqual(0.5, stage_ablation["vector_empty_rate"])
        self.assertEqual(0.5, stage_ablation["hybrid_lift_over_bm25_at_5"])
        self.assertEqual(0.5, stage_ablation["rerank_lift_over_hybrid_at_1"])
        self.assertEqual(0.0, stage_ablation["rerank_regression_rate_at_1"])
        self.assertEqual(0.5, stage_ablation["rewrite_applied_rate"])
        self.assertEqual(0.5, stage_ablation["follow_up_detected_rate"])
        self.assertEqual(0.5, stage_ablation["rerank_top1_changed_rate"])
        self.assertEqual(1, stage_ablation["hybrid_hit_at_1_case_count"])
        self.assertEqual({"follow_up_reference": 1}, stage_ablation["rewrite_reason_counts"])
        self.assertEqual({"points/query": 1, "points/search": 1}, stage_ablation["vector_endpoint_counts"])
        self.assertEqual({"bm25": 1, "both": 1}, stage_ablation["hybrid_top_support_counts"])
        self.assertEqual({"support rescue": 1}, stage_ablation["rerank_reason_counts"])

    def test_build_graph_sidecar_evidence_packet_defers_when_only_provenance_noise_remains(self) -> None:
        retrieval_summary = {
            "overall": {"hit@1": 1.0, "hit@5": 1.0},
            "graph_signal_counts": {},
        }
        answer_report = {
            "overall": {"pass_rate": 1.0},
            "realworld_assessment": {
                "status": "sufficient_with_provenance_noise",
                "provenance_noise_case_ids": ["rw-learn-002", "rw-learn-003"],
            },
        }

        packet = build_graph_sidecar_evidence_packet(retrieval_summary, answer_report=answer_report)

        self.assertEqual("defer_graph_sidecar", packet["decision"])
        self.assertEqual("provenance_traversal", packet["next_trigger_to_revisit"])
        self.assertEqual(2, packet["answer_evidence"]["provenance_noise_count"])

    def test_build_graph_sidecar_evidence_packet_revisits_for_similar_document_rank_conflict(self) -> None:
        retrieval_summary = {
            "overall": {"hit@1": 0.9375, "hit@5": 1.0},
            "graph_signal_counts": {"similar-document": 1},
        }
        answer_report = {
            "overall": {"pass_rate": 1.0},
            "realworld_assessment": {
                "status": "sufficient_with_provenance_noise",
                "provenance_noise_case_ids": ["rw-learn-002", "rw-learn-003"],
            },
        }

        packet = build_graph_sidecar_evidence_packet(retrieval_summary, answer_report=answer_report)

        self.assertEqual("revisit_graph_sidecar", packet["decision"])
        self.assertEqual("similar_document_validation", packet["next_trigger_to_revisit"])
        self.assertEqual(1, packet["retrieval_evidence"]["similar_document_count"])
        self.assertEqual(1, packet["retrieval_evidence"]["graph_shaped_count"])

    def test_build_graph_sidecar_evidence_packet_defers_for_generic_retrieval_miss(self) -> None:
        retrieval_summary = {
            "overall": {"hit@1": 0.75, "hit@5": 0.75},
            "graph_signal_counts": {"retrieval-miss": 1},
        }

        packet = build_graph_sidecar_evidence_packet(retrieval_summary, answer_report={})

        self.assertEqual("defer_graph_sidecar", packet["decision"])
        self.assertEqual("retrieval_baseline", packet["next_trigger_to_revisit"])
        self.assertEqual(0, packet["retrieval_evidence"]["graph_shaped_count"])
        self.assertEqual(1, packet["retrieval_evidence"]["retrieval_miss_count"])

    def test_build_graph_sidecar_evidence_packet_prioritizes_relation_aware_over_other_graph_signals(self) -> None:
        retrieval_summary = {
            "overall": {"hit@1": 0.8, "hit@5": 1.0},
            "graph_signal_counts": {
                "relation-aware-retrieval": 1,
                "policy-overlay": 2,
                "similar-document": 3,
            },
        }

        packet = build_graph_sidecar_evidence_packet(retrieval_summary, answer_report={})

        self.assertEqual("revisit_graph_sidecar", packet["decision"])
        self.assertEqual("relation_aware_retrieval", packet["next_trigger_to_revisit"])

    def test_build_graph_sidecar_evidence_packet_prioritizes_policy_overlay_over_similar_document(self) -> None:
        retrieval_summary = {
            "overall": {"hit@1": 0.9, "hit@5": 1.0},
            "graph_signal_counts": {
                "policy-overlay": 1,
                "similar-document": 4,
            },
        }

        packet = build_graph_sidecar_evidence_packet(retrieval_summary, answer_report={})

        self.assertEqual("revisit_graph_sidecar", packet["decision"])
        self.assertEqual("policy_overlay_branching", packet["next_trigger_to_revisit"])

    def test_build_graph_sidecar_evidence_packet_stays_deferred_when_retrieval_and_answers_are_clean(self) -> None:
        retrieval_summary = {
            "overall": {"hit@1": 1.0, "hit@5": 1.0},
            "graph_signal_counts": {},
        }
        answer_report = {
            "overall": {"pass_rate": 1.0},
            "realworld_assessment": {"status": "sufficient"},
        }

        packet = build_graph_sidecar_evidence_packet(retrieval_summary, answer_report=answer_report)

        self.assertEqual("defer_graph_sidecar", packet["decision"])
        self.assertEqual("none", packet["next_trigger_to_revisit"])
        self.assertEqual(0, packet["retrieval_evidence"]["graph_shaped_count"])
        self.assertEqual(0, packet["answer_evidence"]["provenance_noise_count"])


if __name__ == "__main__":
    unittest.main()
