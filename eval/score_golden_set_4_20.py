from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip().lower().lstrip("/")


def has_hangul(text: str) -> bool:
    return any("\uac00" <= char <= "\ud7a3" for char in text)


def contains_any(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords if keyword)


def source_scope_terms_pass(answer: str, scope_terms: list[str]) -> bool:
    if not scope_terms:
        return True
    lowered = answer.lower()
    return any(term.lower() in lowered for term in scope_terms if term)


def count_group_matches(text: str, groups: list[list[str]]) -> tuple[int, int]:
    lowered = text.lower()
    matched = 0
    for group in groups:
        if any(keyword.lower() in lowered for keyword in group if keyword):
            matched += 1
    return matched, len(groups)


def structural_pass(answer: str, expected_shape: str, scope_policy: str) -> bool:
    if scope_policy == "out_of_scope":
        return True

    checks: list[bool] = []
    if "체크리스트형" in expected_shape:
        checks.append(any(token in answer for token in ["확인", "점검", "체크리스트", "준비"]))
    if "단계형" in expected_shape or "순서형" in expected_shape:
        checks.append(any(token in answer for token in ["1.", "2.", "먼저", "다음", "이후"]))
    if "비교" in expected_shape:
        checks.append(any(token in answer for token in ["차이", "비교", "구분", "기준"]))
    if "문서 유도형" in expected_shape:
        checks.append(any(token in answer for token in ["문서", "가이드", "참고", "확인"]))
    if "설명형" in expected_shape:
        checks.append(any(token in answer for token in ["역할", "의미", "개요", "설명"]))
    if "원인" in expected_shape or "분기" in expected_shape:
        checks.append(any(token in answer for token in ["원인", "경우", "확인", "점검", "아니면"]))

    return all(checks) if checks else True


def refusal_pass(answer: str, refusal_keywords: list[str]) -> bool:
    lowered = answer.lower()
    refusal_groups = [
        ["범위", "지원하지", "지원 불가", "전용"],
        ["공식", "o.c.p", "ocp", "OpenShift Container Platform".lower()],
        refusal_keywords,
    ]
    matched = 0
    for group in refusal_groups:
        if any(keyword.lower() in lowered for keyword in group if keyword):
            matched += 1
    return matched >= 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score the enterprise-4.20 Golden Set run.")
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--rubric", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cases = {record["id"]: record for record in load_jsonl(args.cases)}
    rubric = {record["id"]: record for record in load_json(args.rubric)}
    results = {record["benchmark_case_id"]: record for record in load_jsonl(args.results)}

    per_case: list[dict] = []
    summary_by_group: dict[str, Counter] = defaultdict(Counter)
    in_scope_case_count = 0
    raw_recall_hits = 0
    reranked_recall_hits = 0
    answer_accuracy_hits = 0
    citation_accuracy_hits = 0
    hallucination_count = 0

    for case_id, case in cases.items():
        rule = rubric[case_id]
        result = results.get(case_id, {})
        answer_text = str(result.get("answer_text", "")).strip()
        raw_candidates = result.get("retrieval_candidates", [])
        reranked_candidates = result.get("reranked_candidates", [])
        citations = result.get("citations", [])
        expected_paths = [normalize_path(path) for path in rule.get("expected_document_paths", [])]
        scope_policy = str(rule.get("scope_policy", "in_scope"))
        group = str(rule.get("group", "unknown"))

        raw_paths = [normalize_path(item.get("document_path", "")) for item in raw_candidates[:10]]
        reranked_paths = [normalize_path(item.get("document_path", "")) for item in reranked_candidates[:10]]
        citation_paths = [normalize_path(item.get("document_path", "")) for item in citations]

        raw_recall_pass = bool(expected_paths) and any(path in raw_paths for path in expected_paths)
        reranked_recall_pass = bool(expected_paths) and any(path in reranked_paths for path in expected_paths)

        if scope_policy == "in_scope":
            in_scope_case_count += 1
            raw_recall_hits += int(raw_recall_pass)
            reranked_recall_hits += int(reranked_recall_pass)

        citation_pass = (
            len(citation_paths) == 0 if scope_policy == "out_of_scope"
            else any(path in citation_paths for path in expected_paths)
        )

        required_groups = rule.get("required_keyword_groups", [])
        matched_groups, total_groups = count_group_matches(answer_text, required_groups)
        keyword_score = (matched_groups / total_groups) if total_groups else 1.0
        scope_terms_ok = source_scope_terms_pass(answer_text, rule.get("required_source_scope_terms", []))
        refusal_ok = refusal_pass(answer_text, rule.get("refusal_any_keywords", [])) if scope_policy == "out_of_scope" else False
        forbidden_hit = contains_any(answer_text, rule.get("forbidden_keywords", []))
        structure_ok = structural_pass(answer_text, str(rule.get("expected_answer_shape", "")), scope_policy)
        answer_has_korean = has_hangul(answer_text)

        if scope_policy == "out_of_scope":
            answer_accuracy_pass = answer_has_korean and refusal_ok and citation_pass
            hallucination_detected = not refusal_ok or len(citation_paths) > 0
        else:
            answer_accuracy_pass = (
                answer_has_korean
                and citation_pass
                and not forbidden_hit
                and structure_ok
                and keyword_score >= 0.5
                and scope_terms_ok
                and not contains_any(answer_text, ["정보가 없습니다", "확정하기 어렵습니다", "모르겠습니다"])
            )
            hallucination_detected = (not citation_pass and bool(answer_text)) or forbidden_hit

        answer_accuracy_hits += int(answer_accuracy_pass)
        citation_accuracy_hits += int(citation_pass)
        hallucination_count += int(hallucination_detected)

        case_record = {
            "id": case_id,
            "group": group,
            "scope_policy": scope_policy,
            "question_ko": case["question_ko"],
            "raw_recall_pass": raw_recall_pass,
            "reranked_recall_pass": reranked_recall_pass,
            "citation_pass": citation_pass,
            "answer_accuracy_pass": answer_accuracy_pass,
            "hallucination_detected": hallucination_detected,
            "keyword_group_score": round(keyword_score, 4),
            "matched_keyword_groups": matched_groups,
            "total_keyword_groups": total_groups,
            "scope_terms_ok": scope_terms_ok,
            "structure_ok": structure_ok,
            "refusal_ok": refusal_ok,
            "forbidden_hit": forbidden_hit,
            "answer_preview": answer_text[:300],
            "citation_paths": citation_paths,
            "expected_paths": expected_paths,
        }
        per_case.append(case_record)

        summary_by_group[group]["case_count"] += 1
        summary_by_group[group]["citation_pass"] += int(citation_pass)
        summary_by_group[group]["answer_accuracy_pass"] += int(answer_accuracy_pass)
        summary_by_group[group]["hallucination_free"] += int(not hallucination_detected)
        if scope_policy == "in_scope":
            summary_by_group[group]["raw_recall_pass"] += int(raw_recall_pass)
            summary_by_group[group]["reranked_recall_pass"] += int(reranked_recall_pass)
            summary_by_group[group]["in_scope_count"] += 1

    total_case_count = len(cases)
    summary = {
        "total_case_count": total_case_count,
        "in_scope_case_count": in_scope_case_count,
        "raw_recall@10": round(raw_recall_hits / in_scope_case_count, 4) if in_scope_case_count else 0.0,
        "reranked_recall@10": round(reranked_recall_hits / in_scope_case_count, 4) if in_scope_case_count else 0.0,
        "answer_accuracy": round(answer_accuracy_hits / total_case_count, 4) if total_case_count else 0.0,
        "hallucination_rate": round(hallucination_count / total_case_count, 4) if total_case_count else 0.0,
        "citation_accuracy": round(citation_accuracy_hits / total_case_count, 4) if total_case_count else 0.0,
        "success_criteria": {
            "recall_target": 0.9,
            "accuracy_target": 0.85,
            "hallucination_target": 0.0,
            "citation_accuracy_target": 1.0,
        },
    }
    summary["pass"] = (
        summary["reranked_recall@10"] >= summary["success_criteria"]["recall_target"]
        and summary["answer_accuracy"] >= summary["success_criteria"]["accuracy_target"]
        and summary["hallucination_rate"] <= summary["success_criteria"]["hallucination_target"]
        and summary["citation_accuracy"] >= summary["success_criteria"]["citation_accuracy_target"]
    )

    grouped_output = {}
    for group, counters in summary_by_group.items():
        in_scope_count = counters.get("in_scope_count", 0)
        grouped_output[group] = {
            "case_count": counters["case_count"],
            "raw_recall@10": round(counters["raw_recall_pass"] / in_scope_count, 4) if in_scope_count else None,
            "reranked_recall@10": round(counters["reranked_recall_pass"] / in_scope_count, 4) if in_scope_count else None,
            "answer_accuracy": round(counters["answer_accuracy_pass"] / counters["case_count"], 4) if counters["case_count"] else 0.0,
            "hallucination_rate": round(1 - (counters["hallucination_free"] / counters["case_count"]), 4) if counters["case_count"] else 0.0,
            "citation_accuracy": round(counters["citation_pass"] / counters["case_count"], 4) if counters["case_count"] else 0.0,
        }

    report = {
        "summary": summary,
        "by_group": grouped_output,
        "cases": per_case,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
