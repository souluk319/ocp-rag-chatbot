from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:8000"
OUTPUT_PATH = REPO_ROOT / "data" / "manifests" / "generated" / "stage04-citation-viewer-report.json"

CASES = [
    {
        "case_id": "basic-openshift",
        "query": "오픈시프트가 뭐야",
        "expected_viewer_fragment": "/viewer/openshift-docs-core-validation/architecture/",
    },
    {
        "case_id": "basic-ocp",
        "query": "OCP가 뭐야",
        "expected_viewer_fragment": "/viewer/openshift-docs-core-validation/architecture/",
    },
    {
        "case_id": "ops-firewall",
        "query": "방화벽 설정은 왜 필요한가요?",
        "expected_viewer_fragment": "/viewer/openshift-docs-core-validation/installing/install_config/configuring-firewall.html",
    },
    {
        "case_id": "ops-update-readiness",
        "query": "업데이트 전 확인사항은 무엇인가요?",
        "expected_viewer_fragment": "/viewer/openshift-docs-core-validation/post_installation_configuration/day_2_core_cnf_clusters/updating/update-before-the-update.html",
    },
]


def run_case(case: dict[str, str]) -> dict[str, Any]:
    response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        json={"query": case["query"], "mode": "operations"},
        timeout=60,
    )
    payload = response.json()
    sources = payload.get("sources", []) or []
    first = sources[0] if sources else {}
    viewer_url = str(first.get("viewer_url", ""))
    viewer_status = None
    viewer_content_type = ""
    viewer_pass = False

    if viewer_url.startswith("/viewer/"):
        viewer_response = requests.get(f"{BASE_URL}{viewer_url}", timeout=30)
        viewer_status = viewer_response.status_code
        viewer_content_type = viewer_response.headers.get("content-type", "")
        viewer_pass = viewer_response.ok and "text/html" in viewer_content_type

    return {
        "case_id": case["case_id"],
        "query": case["query"],
        "status_code": response.status_code,
        "source_count": len(sources),
        "first_title": str(first.get("title", "")),
        "first_document_path": str(first.get("document_path", "")),
        "first_viewer_url": viewer_url,
        "viewer_status": viewer_status,
        "viewer_content_type": viewer_content_type,
        "viewer_pass": viewer_pass,
        "viewer_expected_match": case["expected_viewer_fragment"] in viewer_url,
        "pass": (
            response.ok
            and len(sources) >= 1
            and bool(str(first.get("title", "")).strip())
            and viewer_pass
            and case["expected_viewer_fragment"] in viewer_url
        ),
    }


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    root_html = requests.get(f"{BASE_URL}/", timeout=20).text
    ui_enter_send_enabled = 'event.key === "Enter" && !event.shiftKey' in root_html

    cases = [run_case(case) for case in CASES]
    result = {
        "base_url": BASE_URL,
        "ui_enter_send_enabled": ui_enter_send_enabled,
        "cases": cases,
    }
    result["overall_pass"] = ui_enter_send_enabled and all(case["pass"] for case in cases)

    OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
