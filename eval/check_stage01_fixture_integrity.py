from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OPENSHIFT_DOCS_ROOT = REPO_ROOT.parent / "openshift-docs"
HANGUL_RE = re.compile(r"[가-힣]")


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Stage 1 fixture integrity.")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "data" / "manifests" / "generated" / "stage01-fixture-integrity-report.json",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def has_hangul(text: str) -> bool:
    return bool(HANGUL_RE.search(text))


def no_replacement_char(text: str) -> bool:
    return "\ufffd" not in text


def doc_exists(relative_path: str) -> bool:
    return (OPENSHIFT_DOCS_ROOT / relative_path).exists()


def validate_live_smoke_cases(path: Path) -> tuple[list[CheckResult], list[dict[str, Any]]]:
    rows = load_json(path)
    results = [CheckResult("live_smoke_count", len(rows) >= 2, {"count": len(rows)})]

    issues: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for row in rows:
        row_id = str(row.get("id", "")).strip()
        query = str(row.get("query", "")).strip()
        ok = bool(row_id and query and row_id not in seen_ids and has_hangul(query) and no_replacement_char(query))
        if not ok:
            issues.append({"id": row_id, "query": query})
        seen_ids.add(row_id)

    results.append(CheckResult("live_smoke_rows", not issues, {"issues": issues}))
    return results, rows


def validate_retrieval_cases(path: Path) -> tuple[list[CheckResult], list[dict[str, Any]]]:
    rows = load_jsonl(path)
    results = [CheckResult("retrieval_case_count", len(rows) == 13, {"count": len(rows)})]

    issues: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for row in rows:
        row_id = str(row.get("id", "")).strip()
        question = str(row.get("question_ko", "")).strip()
        source_dirs = [str(item) for item in row.get("expected_source_dirs", [])]
        doc_paths = [str(item) for item in row.get("expected_document_paths", [])]

        ok = bool(row_id and question and row_id not in seen_ids and has_hangul(question) and no_replacement_char(question))
        ok = ok and bool(source_dirs and doc_paths)
        for source_dir in source_dirs:
            if not any(doc_path.startswith(f"{source_dir}/") for doc_path in doc_paths):
                ok = False
        for doc_path in doc_paths:
            if not doc_exists(doc_path):
                ok = False

        if not ok:
            issues.append({"id": row_id, "question": question, "source_dirs": source_dirs, "doc_paths": doc_paths})
        seen_ids.add(row_id)

    results.append(CheckResult("retrieval_rows", not issues, {"issues": issues}))
    return results, rows


def validate_red_team_cases(path: Path) -> tuple[list[CheckResult], list[dict[str, Any]]]:
    rows = load_jsonl(path)
    results = [CheckResult("red_team_case_count", len(rows) == 7, {"count": len(rows)})]

    issues: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for row in rows:
        row_id = str(row.get("id", "")).strip()
        question = str(row.get("question_ko", "")).strip()
        turns = row.get("turns", [])

        ok = bool(row_id and row_id not in seen_ids)
        if question:
            ok = ok and has_hangul(question) and no_replacement_char(question)
        elif turns:
            for turn in turns:
                turn_question = str(turn.get("question_ko", "")).strip()
                if not turn_question or not has_hangul(turn_question) or not no_replacement_char(turn_question):
                    ok = False
                doc_path = str(turn.get("reference_doc_path", "")).strip()
                if doc_path and not doc_exists(doc_path):
                    ok = False
        else:
            ok = False

        if not ok:
            issues.append(
                {
                    "id": row_id,
                    "question": question,
                    "turn_questions": [str(turn.get("question_ko", "")).strip() for turn in turns],
                }
            )
        seen_ids.add(row_id)

    results.append(CheckResult("red_team_rows", not issues, {"issues": issues}))
    return results, rows


def validate_multiturn(path: Path) -> tuple[list[CheckResult], dict[str, Any]]:
    payload = load_json(path)
    scenarios = payload.get("scenarios", [])
    results = [CheckResult("multiturn_scenario_count", len(scenarios) == 2, {"count": len(scenarios)})]

    issues: list[dict[str, Any]] = []
    total_turns = 0
    seen_ids: set[str] = set()
    for scenario in scenarios:
        scenario_id = str(scenario.get("scenario_id", "")).strip()
        turns = scenario.get("turns", [])
        total_turns += len(turns)
        if not scenario_id or scenario_id in seen_ids:
            issues.append({"scenario_id": scenario_id, "reason": "duplicate_or_empty"})
            continue
        seen_ids.add(scenario_id)

        for turn in turns:
            question = str(turn.get("question_ko", "")).strip()
            source_dir = str(turn.get("expected_source_dir", "")).strip()
            doc_path = str(turn.get("expected_document_path", "")).strip()
            ok = bool(question and has_hangul(question) and no_replacement_char(question))
            ok = ok and bool(source_dir and doc_path and doc_path.startswith(f"{source_dir}/") and doc_exists(doc_path))
            if not ok:
                issues.append(
                    {
                        "scenario_id": scenario_id,
                        "turn_index": turn.get("turn_index"),
                        "question": question,
                        "source_dir": source_dir,
                        "doc_path": doc_path,
                    }
                )

    results.append(CheckResult("multiturn_total_turns", total_turns == 10, {"turn_count": total_turns}))
    results.append(CheckResult("multiturn_turns", not issues, {"issues": issues}))
    return results, payload


def main() -> int:
    args = parse_args()

    checks: list[CheckResult] = []
    live_results, live_rows = validate_live_smoke_cases(REPO_ROOT / "deployment" / "live_runtime_smoke_cases.json")
    retrieval_results, retrieval_rows = validate_retrieval_cases(
        REPO_ROOT / "eval" / "benchmarks" / "p0_retrieval_benchmark_cases.jsonl"
    )
    red_team_results, red_team_rows = validate_red_team_cases(
        REPO_ROOT / "eval" / "benchmarks" / "p0_red_team_cases.jsonl"
    )
    multiturn_results, multiturn_payload = validate_multiturn(
        REPO_ROOT / "eval" / "benchmarks" / "p0_multiturn_scenarios.json"
    )

    checks.extend(live_results)
    checks.extend(retrieval_results)
    checks.extend(red_team_results)
    checks.extend(multiturn_results)

    overall_pass = all(check.passed for check in checks)
    report = {
        "stage": "stage01-fixture-integrity",
        "overall_pass": overall_pass,
        "openshift_docs_root": str(OPENSHIFT_DOCS_ROOT),
        "summary": {
            "live_smoke_cases": len(live_rows),
            "retrieval_cases": len(retrieval_rows),
            "red_team_cases": len(red_team_rows),
            "multiturn_scenarios": len(multiturn_payload.get("scenarios", [])),
        },
        "checks": [
            {
                "name": check.name,
                "passed": check.passed,
                "details": check.details,
            }
            for check in checks
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"overall_pass": overall_pass, "output": str(args.output)}, ensure_ascii=False))
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
