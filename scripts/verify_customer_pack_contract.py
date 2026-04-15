from __future__ import annotations

import json
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


DOCS = {
    "customer_contract": REPO_ROOT / "archive" / "root_contracts" / "CUSTOMER_SOURCE_FIRST_PACK_CONTRACT.md",
    "parsed_contract": REPO_ROOT / "PARSED_ARTIFACT_CONTRACT.md",
    "security_contract": REPO_ROOT / "SECURITY_BOUNDARY_CONTRACT.md",
    "project": REPO_ROOT / "PROJECT.md",
    "product_contract": REPO_ROOT / "Q1_8_PRODUCT_CONTRACT.md",
    "architecture": REPO_ROOT / "P0_ARCHITECTURE_FREEZE_ADDENDUM.md",
    "task_board": REPO_ROOT / "TASK_BOARD.yaml",
}


REQUIRED_TERMS = {
    "customer_source_first_pack": [
        "customer_contract",
        "parsed_contract",
        "security_contract",
        "product_contract",
        "architecture",
    ],
    "pack runtime": [
        "customer_contract",
        "parsed_contract",
        "project",
    ],
    "pack boundary": [
        "customer_contract",
        "security_contract",
        "project",
        "product_contract",
    ],
    "official / private / mixed": [
        "customer_contract",
        "security_contract",
        "product_contract",
    ],
}


def main() -> int:
    contents = {name: path.read_text(encoding="utf-8") for name, path in DOCS.items() if path.suffix != ".yaml"}
    task_board = yaml.safe_load(DOCS["task_board"].read_text(encoding="utf-8"))

    phase = next(phase for phase in task_board["phases"] if phase["id"] == "W4")
    epic = next(epic for epic in phase["epics"] if epic["id"] == "W4-E1")
    task = next(task for task in epic["tasks"] if task["id"] == "W4-E1-T1")

    term_checks: dict[str, dict[str, bool]] = {}
    all_ok = True
    for term, doc_names in REQUIRED_TERMS.items():
        per_doc = {}
        for doc_name in doc_names:
            ok = term in contents[doc_name]
            per_doc[doc_name] = ok
            all_ok &= ok
        term_checks[term] = per_doc

    report = {
        "status": "ok" if all_ok and task["status"] == "done" else "fail",
        "task_status": task["status"],
        "task_test": task["tests"][0],
        "term_checks": term_checks,
        "customer_contract_exists": DOCS["customer_contract"].exists(),
        "yaml_ok": True,
    }

    out_dir = REPO_ROOT / "reports" / "build_logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "customer_pack_contract_report.json"
    md_path = out_dir / "customer_pack_contract_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Customer Pack Contract Report",
        "",
        f"- status: `{report['status']}`",
        f"- task_status: `{report['task_status']}`",
        f"- task_test: `{report['task_test']}`",
        f"- customer_contract_exists: `{report['customer_contract_exists']}`",
        f"- yaml_ok: `{report['yaml_ok']}`",
        "",
        "## Term Checks",
        "",
    ]
    for term, checks in term_checks.items():
        lines.append(f"### `{term}`")
        lines.append("")
        for doc_name, ok in checks.items():
            lines.append(f"- `{doc_name}`: `{ok}`")
        lines.append("")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
