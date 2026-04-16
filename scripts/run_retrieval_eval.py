# retrieval eval manifest를 기준으로 hit@k와 후보 품질을 계산하는 표준 평가 스크립트.
# vector/BM25/fusion/reranker 변경의 직접 효과를 볼 때 먼저 실행한다.
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.evals.retrieval_eval import (
    build_graph_sidecar_evidence_packet,
    landing_hit_at_k,
    summarize_case_results,
)
from play_book_studio.retrieval.models import SessionContext
from play_book_studio.retrieval.retriever import ChatRetriever


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _hit_at(top_books: list[str], expected_books: set[str], k: int) -> bool:
    return any(book_slug in expected_books for book_slug in top_books[:k])


def _safe_read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the retrieval evaluation benchmark")
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "manifests" / "retrieval_eval_cases.jsonl",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--skip-vector", action="store_true")
    reranker_group = parser.add_mutually_exclusive_group()
    reranker_group.add_argument("--enable-reranker", action="store_true")
    reranker_group.add_argument("--disable-reranker", action="store_true")
    parser.add_argument("--reranker-model", type=str, default="")
    parser.add_argument("--reranker-top-n", type=int, default=0)
    parser.add_argument("--output", type=Path, default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    if args.reranker_model:
        settings.reranker_model = args.reranker_model.strip()
    if args.reranker_top_n:
        settings.reranker_top_n = max(2, args.reranker_top_n)
    enable_reranker = None
    if args.enable_reranker:
        enable_reranker = True
    elif args.disable_reranker:
        enable_reranker = False
    retriever = ChatRetriever.from_settings(
        settings,
        enable_vector=not args.skip_vector,
        enable_reranker=enable_reranker,
    )
    cases = read_jsonl(args.cases)

    details: list[dict] = []
    by_category: dict[str, list[dict]] = defaultdict(list)

    for case in cases:
        context = SessionContext.from_dict(case.get("context"))
        result = retriever.retrieve(
            str(case["query"]),
            context=context,
            top_k=args.top_k,
            candidate_k=args.candidate_k,
            use_vector=not args.skip_vector,
        )
        trace = result.trace or {}
        plan_trace = trace.get("plan") or {}
        ablation_trace = trace.get("ablation") or {}
        vector_runtime = trace.get("vector_runtime") or {}
        top_books = [hit.book_slug for hit in result.hits]
        top_hits = [
            {
                "book_slug": hit.book_slug,
                "section": hit.section,
                "anchor": hit.anchor,
                "viewer_path": hit.viewer_path,
            }
            for hit in result.hits
        ]
        expected_books = set(case.get("expected_book_slugs", []))
        expected_landing_terms = [str(item) for item in case.get("expected_landing_terms", []) if str(item).strip()]
        detail = {
            "id": case["id"],
            "category": case["category"],
            "mode": str(case.get("mode", case["category"] if case["category"] in {"ops", "learn"} else "ops")),
            "query_type": str(case.get("query_type", case["category"])),
            "query": case["query"],
            "expected_book_slugs": sorted(expected_books),
            "expected_landing_terms": expected_landing_terms,
            "rewritten_query": result.rewritten_query,
            "top_book_slugs": top_books,
            "top_hits": top_hits,
            "bm25_top_book_slugs": [str(item) for item in ablation_trace.get("bm25_top_book_slugs", [])],
            "vector_top_book_slugs": [str(item) for item in ablation_trace.get("vector_top_book_slugs", [])],
            "hybrid_top_book_slugs": [str(item) for item in ablation_trace.get("hybrid_top_book_slugs", [])],
            "reranked_top_book_slugs": [str(item) for item in ablation_trace.get("reranked_top_book_slugs", top_books)],
            "book_hit_at_1": _hit_at(top_books, expected_books, 1),
            "book_hit_at_3": _hit_at(top_books, expected_books, 3),
            "book_hit_at_5": _hit_at(top_books, expected_books, 5),
            "landing_hit_at_1": landing_hit_at_k(top_hits, sorted(expected_books), expected_landing_terms, 1),
            "landing_hit_at_3": landing_hit_at_k(top_hits, sorted(expected_books), expected_landing_terms, 3),
            "landing_hit_at_5": landing_hit_at_k(top_hits, sorted(expected_books), expected_landing_terms, 5),
            "warnings": trace.get("warnings", []),
            "reranker_applied": bool(trace.get("reranker", {}).get("applied", False)),
            "rewrite_applied": bool(plan_trace.get("rewrite_applied", False)),
            "rewrite_reason": str(plan_trace.get("rewrite_reason", "")),
            "follow_up_detected": bool(plan_trace.get("follow_up_detected", False)),
            "vector_endpoint_used": str(vector_runtime.get("endpoint_used", "")),
            "vector_endpoints_used": [str(item) for item in vector_runtime.get("endpoints_used", [])],
            "hybrid_top_support": str(ablation_trace.get("hybrid_top_support", "")),
            "rerank_top1_changed": bool(ablation_trace.get("rerank_top1_changed", False)),
            "rerank_reasons": [str(item) for item in ablation_trace.get("rerank_reasons", [])],
        }
        details.append(detail)
        by_category[case["category"]].append(detail)

    summary = summarize_case_results(details, ks=(1, 3, 5))
    answer_report = _safe_read_json(settings.answer_eval_report_path)
    report = {
        "case_count": len(cases),
        "top_k": args.top_k,
        "candidate_k": args.candidate_k,
        "reranker": {
            "enabled": retriever.reranker is not None,
            "model": getattr(retriever.reranker, "model_name", ""),
            "top_n": getattr(retriever.reranker, "top_n", 0),
        },
        "overall": {
            "case_count": summary["case_count"],
            "book_hit_at_1": summary["overall"]["hit@1"],
            "book_hit_at_3": summary["overall"]["hit@3"],
            "book_hit_at_5": summary["overall"]["hit@5"],
            "landing_case_count": summary["overall"]["landing_case_count"],
            "landing_hit_at_1": summary["overall"]["landing_hit@1"],
            "landing_hit_at_3": summary["overall"]["landing_hit@3"],
            "landing_hit_at_5": summary["overall"]["landing_hit@5"],
            "warning_free_rate": summary["overall"]["warning_free_rate"],
            "similar_document_risk_rate": summary["overall"]["similar_document_risk_rate"],
            "policy_overlay_warning_rate": summary["overall"]["policy_overlay_warning_rate"],
            "relation_aware_miss_rate": summary["overall"]["relation_aware_miss_rate"],
        },
        "stage_ablation": summary["stage_ablation"],
        "by_category": {
            category: {
                "case_count": category_summary["case_count"],
                "book_hit_at_1": category_summary["overall"]["hit@1"],
                "book_hit_at_3": category_summary["overall"]["hit@3"],
                "book_hit_at_5": category_summary["overall"]["hit@5"],
                "landing_case_count": category_summary["overall"]["landing_case_count"],
                "landing_hit_at_1": category_summary["overall"]["landing_hit@1"],
                "landing_hit_at_3": category_summary["overall"]["landing_hit@3"],
                "landing_hit_at_5": category_summary["overall"]["landing_hit@5"],
                "warning_free_rate": category_summary["overall"]["warning_free_rate"],
                "similar_document_risk_rate": category_summary["overall"]["similar_document_risk_rate"],
                "policy_overlay_warning_rate": category_summary["overall"]["policy_overlay_warning_rate"],
                "relation_aware_miss_rate": category_summary["overall"]["relation_aware_miss_rate"],
                "stage_ablation": category_summary["stage_ablation"],
            }
            for category, category_details in sorted(by_category.items())
            for category_summary in (summarize_case_results(category_details, ks=(1, 3, 5)),)
        },
        "graph_signal_counts": summary["graph_signal_counts"],
        "graph_sidecar_evidence_packet": build_graph_sidecar_evidence_packet(
            summary,
            answer_report=answer_report,
        ),
        "misses_at_5": [
            {
                **item,
                "graph_signal_tag": item.get("graph_signal_tag", ""),
                "graph_signal_reason": item.get("graph_signal_reason", ""),
            }
            for item in details
            if not item["book_hit_at_5"]
        ],
        "details": details,
    }

    output_path = args.output or settings.retrieval_eval_report_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote eval report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
