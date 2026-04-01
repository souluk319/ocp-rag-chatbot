from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.multiturn_memory import SessionMemoryManager
from app.ocp_policy import OcpPolicyEngine


def default_smoke_report() -> Path:
    return REPO_ROOT / "data" / "manifests" / "generated" / "s15c-core-smoke-report-bridge.json"


def default_benchmark_cases() -> Path:
    return REPO_ROOT / "eval" / "benchmarks" / "p0_retrieval_benchmark_cases.jsonl"


def default_smoke_results() -> Path:
    return REPO_ROOT / "indexes" / "s15c-core" / "smoke-results.jsonl"


def default_manifest() -> Path:
    return REPO_ROOT / "data" / "staging" / "s15c" / "manifests" / "staged-manifest.json"


def default_output() -> Path:
    return REPO_ROOT / "data" / "manifests" / "generated" / "stage03-retrieval-root-cause-report.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze widened-corpus retrieval failures for Stage 3.")
    parser.add_argument("--smoke-report", type=Path, default=default_smoke_report())
    parser.add_argument("--benchmark-cases", type=Path, default=default_benchmark_cases())
    parser.add_argument("--smoke-results", type=Path, default=default_smoke_results())
    parser.add_argument("--manifest", type=Path, default=default_manifest())
    parser.add_argument("--output", type=Path, default=default_output())
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        rows.append(json.loads(stripped))
    return rows


def normalize_document_path(document_path: str, source_id: str) -> str:
    normalized = str(document_path or "").replace("\\", "/").strip()
    prefix = f"{source_id}/"
    if normalized.startswith(prefix):
        return normalized[len(prefix) :]
    return normalized


def top_level_from_document_path(document_path: str, source_id: str) -> str:
    normalized = normalize_document_path(document_path, source_id)
    if "/" in normalized:
        return normalized.split("/", 1)[0]
    return normalized


def score_spread(candidates: list[dict[str, Any]]) -> float:
    scores = [float(item.get("score", 0.0)) for item in candidates]
    if not scores:
        return 0.0
    return max(scores) - min(scores)


def build_rewrite(question_ko: str) -> dict[str, Any]:
    memory = SessionMemoryManager()
    turn = memory.process_turn(
        session_id="stage03",
        turn_index=1,
        question_ko=question_ko,
    )
    return turn["turn"]


def manifest_index_by_path(manifest_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    source_id = str(manifest_payload.get("source_id", "")).strip()
    indexed: dict[str, dict[str, Any]] = {}
    for document in manifest_payload.get("documents", []):
        local_key = normalize_document_path(document.get("source_url", "").split("/blob/", 1)[-1].split("/", 2)[-1], "")
        indexed[normalize_document_path(document.get("source_id", "") + "/" + document.get("local_path", ""), source_id)] = document
        indexed[normalize_document_path(document.get("source_id", "") + "/" + document.get("source_url", ""), source_id)] = document
        indexed[normalize_document_path(document.get("source_id", "") + "/" + document.get("local_path", "").replace("\\", "/"), source_id)] = document
        normalized_local = str(document.get("local_path", "")).replace("\\", "/")
        marker = "/openshift-docs/"
        if marker in normalized_local:
            indexed[normalized_local.split(marker, 1)[1]] = document
        if local_key:
            indexed[local_key] = document
    return indexed


def concise_document_summary(document: dict[str, Any] | None) -> dict[str, Any]:
    if not document:
        return {}
    return {
        "title": document.get("title", ""),
        "top_level_dir": document.get("top_level_dir", ""),
        "category": document.get("category", ""),
        "trust_level": document.get("trust_level", ""),
        "viewer_url": document.get("viewer_url", ""),
        "section_count": document.get("section_count", 0),
    }


def candidate_summary(candidate: dict[str, Any], source_id: str, manifest_by_path: dict[str, dict[str, Any]]) -> dict[str, Any]:
    normalized_document_path = normalize_document_path(candidate.get("document_path", ""), source_id)
    manifest_doc = manifest_by_path.get(normalized_document_path)
    raw_source_dir = str(candidate.get("source_dir", "")).strip()
    inferred_top_level_dir = top_level_from_document_path(candidate.get("document_path", ""), source_id)
    return {
        "rank": candidate.get("rank"),
        "raw_source_dir": raw_source_dir,
        "inferred_top_level_dir": inferred_top_level_dir,
        "document_path": normalized_document_path,
        "score": candidate.get("score"),
        "section_title": candidate.get("section_title", ""),
        "viewer_url": candidate.get("viewer_url", ""),
        "document": concise_document_summary(manifest_doc),
    }


def analyze_case(
    *,
    benchmark_case: dict[str, Any],
    smoke_result: dict[str, Any],
    source_id: str,
    manifest_by_path: dict[str, dict[str, Any]],
    policy: OcpPolicyEngine,
) -> dict[str, Any]:
    question_ko = str(benchmark_case.get("question_ko", "")).strip()
    rewrite_state = build_rewrite(question_ko)
    signals = policy.analyze_query(question_ko, mode="operations")

    raw_candidates = [candidate_summary(item, source_id, manifest_by_path) for item in smoke_result.get("retrieval_candidates", [])]
    reranked_candidates = [candidate_summary(item, source_id, manifest_by_path) for item in smoke_result.get("reranked_candidates", [])]
    citations = [candidate_summary(item, source_id, manifest_by_path) for item in smoke_result.get("citations", [])]

    expected_source_dirs = list(benchmark_case.get("expected_source_dirs", []))
    expected_document_paths = list(benchmark_case.get("expected_document_paths", []))
    expected_documents = [concise_document_summary(manifest_by_path.get(path)) for path in expected_document_paths]

    raw_top10 = raw_candidates[:10]
    reranked_top1 = reranked_candidates[0] if reranked_candidates else {}
    raw_top1 = raw_candidates[0] if raw_candidates else {}
    citation_top1 = citations[0] if citations else {}
    raw_source_dirs = [item["raw_source_dir"] for item in raw_top10]
    inferred_source_dirs = [item["inferred_top_level_dir"] for item in raw_top10]

    source_id_mislabel = bool(raw_top10) and all(item == source_id for item in raw_source_dirs)
    raw_installing_bias = bool(raw_top10) and all(item == "installing" for item in inferred_source_dirs)
    expected_doc_present_in_raw_top10 = any(item["document_path"] in expected_document_paths for item in raw_top10)
    expected_doc_present_in_reranked = any(item["document_path"] in expected_document_paths for item in reranked_candidates)
    citation_hits_expected = any(item["document_path"] in expected_document_paths for item in citations)
    raw_spread = score_spread(smoke_result.get("retrieval_candidates", [])[:10])
    plateau_detected = raw_spread <= 1e-6

    probable_causes: list[str] = []
    if source_id_mislabel:
        probable_causes.append("candidate_source_dir_is_source_id_not_top_level_dir")
    if raw_installing_bias:
        probable_causes.append("raw_candidates_collapse_into_installing_dir")
    if plateau_detected:
        probable_causes.append("raw_similarity_scores_are_effectively_uniform")
    if not expected_doc_present_in_raw_top10:
        probable_causes.append("expected_document_missing_from_raw_top10")
    if raw_top1 and reranked_top1 and raw_top1.get("document_path") != reranked_top1.get("document_path"):
        probable_causes.append("reranker_changes_top1_without_recovering_expected_document")
    if not citation_hits_expected:
        probable_causes.append("citation_inherits_wrong_reranked_document")
    if signals.preferred_source_dirs and set(signals.preferred_source_dirs).intersection(expected_source_dirs) and not expected_doc_present_in_reranked:
        probable_causes.append("policy_signal_matches_expected_dir_but_does_not_reach_final_candidate")

    return {
        "case_id": benchmark_case.get("id"),
        "scenario_id": benchmark_case.get("scenario_id"),
        "question_ko": question_ko,
        "query_class": benchmark_case.get("expected_query_class", ""),
        "expected_source_dirs": expected_source_dirs,
        "expected_document_paths": expected_document_paths,
        "expected_documents": expected_documents,
        "rewrite_analysis": {
            "classification": rewrite_state.get("classification", ""),
            "rewritten_query": rewrite_state.get("rewritten_query", ""),
            "active_topic": rewrite_state.get("active_topic", ""),
            "source_dir": rewrite_state.get("source_dir", ""),
            "issues": rewrite_state.get("issues", []),
        },
        "policy_signals": signals.to_dict(),
        "raw_top10": raw_top10,
        "reranked_top3": reranked_candidates[:3],
        "citations": citations,
        "diagnostics": {
            "raw_source_dir_values": raw_source_dirs,
            "raw_inferred_source_dirs": inferred_source_dirs,
            "raw_score_spread_top10": raw_spread,
            "raw_score_plateau_detected": plateau_detected,
            "source_id_mislabel_detected": source_id_mislabel,
            "raw_installing_bias_detected": raw_installing_bias,
            "expected_doc_present_in_raw_top10": expected_doc_present_in_raw_top10,
            "expected_doc_present_in_reranked": expected_doc_present_in_reranked,
            "citation_hits_expected_document": citation_hits_expected,
        },
        "probable_causes": probable_causes,
    }


def main() -> int:
    args = parse_args()
    smoke_report = load_json(args.smoke_report)
    failed_case_ids = list(smoke_report.get("retrieval_alignment_failed_case_ids", []))
    benchmark_cases = {row["id"]: row for row in load_jsonl(args.benchmark_cases)}
    smoke_results = {row["benchmark_case_id"]: row for row in load_jsonl(args.smoke_results)}
    manifest_payload = load_json(args.manifest)
    source_id = str(manifest_payload.get("source_id", "")).strip()
    manifest_by_path = manifest_index_by_path(manifest_payload)
    policy = OcpPolicyEngine.from_path()

    case_reports: list[dict[str, Any]] = []
    for case_id in failed_case_ids:
        benchmark_case = benchmark_cases.get(case_id)
        smoke_result = smoke_results.get(case_id)
        if not benchmark_case or not smoke_result:
            continue
        case_reports.append(
            analyze_case(
                benchmark_case=benchmark_case,
                smoke_result=smoke_result,
                source_id=source_id,
                manifest_by_path=manifest_by_path,
                policy=policy,
            )
        )

    summary = {
        "failed_case_count": len(case_reports),
        "failed_case_ids": failed_case_ids,
        "raw_installing_bias_count": sum(
            1 for item in case_reports if item["diagnostics"]["raw_installing_bias_detected"]
        ),
        "source_id_mislabel_count": sum(
            1 for item in case_reports if item["diagnostics"]["source_id_mislabel_detected"]
        ),
        "uniform_score_plateau_count": sum(
            1 for item in case_reports if item["diagnostics"]["raw_score_plateau_detected"]
        ),
        "expected_doc_missing_from_raw_top10_count": sum(
            1 for item in case_reports if not item["diagnostics"]["expected_doc_present_in_raw_top10"]
        ),
        "citation_expected_miss_count": sum(
            1 for item in case_reports if not item["diagnostics"]["citation_hits_expected_document"]
        ),
        "probable_cause_counts": {},
    }
    cause_counts: dict[str, int] = {}
    for case in case_reports:
        for cause in case["probable_causes"]:
            cause_counts[cause] = cause_counts.get(cause, 0) + 1
    summary["probable_cause_counts"] = cause_counts

    report = {
        "stage": 3,
        "source_report": str(args.smoke_report),
        "source_results": str(args.smoke_results),
        "source_manifest": str(args.manifest),
        "summary": summary,
        "cases": case_reports,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
