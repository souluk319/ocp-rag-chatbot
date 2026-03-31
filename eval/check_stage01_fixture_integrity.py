from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "data" / "manifests" / "generated" / "stage01-fixture-integrity-report.json"
HANGUL_RE = re.compile(r"[가-힣]")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def has_replacement_char(text: str) -> bool:
    return "\ufffd" in text


def check_question(text: str, *, label: str, issues: list[str]) -> None:
    stripped = text.strip()
    if not stripped:
        issues.append(f"{label}: empty")
        return
    if has_replacement_char(stripped):
        issues.append(f"{label}: contains replacement character")
    if not HANGUL_RE.search(stripped):
        issues.append(f"{label}: no hangul detected")


def main() -> int:
    issues: list[str] = []

    live_path = REPO_ROOT / "deployment" / "live_runtime_smoke_cases.json"
    retrieval_path = REPO_ROOT / "eval" / "benchmarks" / "p0_retrieval_benchmark_cases.jsonl"
    red_team_path = REPO_ROOT / "eval" / "benchmarks" / "p0_red_team_cases.jsonl"
    multiturn_path = REPO_ROOT / "eval" / "benchmarks" / "p0_multiturn_scenarios.json"

    live_cases = load_json(live_path)
    retrieval_cases = load_jsonl(retrieval_path)
    red_team_cases = load_jsonl(red_team_path)
    multiturn_data = load_json(multiturn_path)
    multiturn_scenarios = multiturn_data.get("scenarios", [])

    for item in live_cases:
        check_question(item.get("query", ""), label=f"live:{item.get('id', '?')}", issues=issues)

    for item in retrieval_cases:
        check_question(item.get("question_ko", ""), label=f"retrieval:{item.get('id', '?')}", issues=issues)

    for item in red_team_cases:
        if "question_ko" in item:
            check_question(item.get("question_ko", ""), label=f"redteam:{item.get('id', '?')}", issues=issues)
        for turn in item.get("turns", []):
            check_question(
                turn.get("question_ko", ""),
                label=f"redteam:{item.get('id', '?')}:{turn.get('turn_index', '?')}",
                issues=issues,
            )

    for scenario in multiturn_scenarios:
        for turn in scenario.get("turns", []):
            check_question(
                turn.get("question_ko", ""),
                label=f"multiturn:{scenario.get('scenario_id', '?')}:{turn.get('turn_index', '?')}",
                issues=issues,
            )

    report = {
        "stage": 1,
        "status": "pass" if not issues else "fail",
        "files": {
            "live_runtime_smoke_cases": {"path": str(live_path.relative_to(REPO_ROOT)), "count": len(live_cases)},
            "retrieval_benchmark_cases": {"path": str(retrieval_path.relative_to(REPO_ROOT)), "count": len(retrieval_cases)},
            "red_team_cases": {"path": str(red_team_path.relative_to(REPO_ROOT)), "count": len(red_team_cases)},
            "multiturn_scenarios": {
                "path": str(multiturn_path.relative_to(REPO_ROOT)),
                "count": len(multiturn_scenarios),
                "turn_count": sum(len(s.get("turns", [])) for s in multiturn_scenarios),
            },
        },
        "issues": issues,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
