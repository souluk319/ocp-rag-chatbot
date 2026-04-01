from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "docs" / "v2" / "2026-04-01" / "stage-06-report.md"
JSON_PATH = REPO_ROOT / "docs" / "v2" / "2026-04-01" / "stage-06-report.json"
BASE_URL = os.environ.get("STAGE06_BASE_URL", "http://127.0.0.1:8000")

CASES = [
    {"id": "definition-openshift", "query": "오픈시프트가 뭐야", "kind": "definition"},
    {"id": "definition-ocp", "query": "OCP가 뭐야", "kind": "definition"},
    {
        "id": "ops-firewall",
        "query": "설치 시 방화벽에서 어떤 포트와 예외를 허용해야 하나요?",
        "kind": "operations",
    },
    {
        "id": "ops-update",
        "query": "업데이트 전에 확인해야 할 사항은 무엇인가요?",
        "kind": "operations",
    },
    {
        "id": "ops-disconnected-mirror",
        "query": "폐쇄망 설치에서 oc-mirror 플러그인으로 이미지를 미러링하려면 어떤 문서를 봐야 하나요?",
        "kind": "operations",
    },
]

REJECT_PHRASES = (
    "자료를 찾지 못했습니다",
    "No relevant documentation found",
    "문서를 찾지 못했습니다",
    "I could not find",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def has_hangul(text: str) -> bool:
    return any("\uac00" <= char <= "\ud7a3" for char in text)


def has_reject_phrase(text: str) -> bool:
    lowered = text.lower()
    return any(phrase.lower() in lowered for phrase in REJECT_PHRASES)


def fetch_viewer(base_url: str, viewer_url: str) -> tuple[bool, int | None, str]:
    if not viewer_url:
        return False, None, ""
    response = requests.get(f"{base_url}{viewer_url}", timeout=10)
    content_type = response.headers.get("content-type", "")
    ok = response.status_code == 200 and "text/html" in content_type.lower()
    return ok, response.status_code, content_type


def check_case(base_url: str, case: dict[str, str]) -> dict[str, object]:
    response = requests.post(
        f"{base_url}/api/v1/chat",
        json={"query": case["query"]},
        timeout=30,
    )
    body = response.json()
    answer = str(body.get("answer", ""))
    sources = body.get("sources") or []
    first_source = sources[0] if sources and isinstance(sources[0], dict) else {}
    viewer_url = str(first_source.get("viewer_url", "")).strip()
    viewer_ok, viewer_status, viewer_content_type = fetch_viewer(base_url, viewer_url)

    passed = (
        response.status_code == 200
        and has_hangul(answer)
        and not has_reject_phrase(answer)
        and len(sources) >= 1
        and viewer_ok
    )

    return {
        "case_id": case["id"],
        "kind": case["kind"],
        "query": case["query"],
        "status_code": response.status_code,
        "answer_preview": answer[:300],
        "answer_has_hangul": has_hangul(answer),
        "answer_has_reject_phrase": has_reject_phrase(answer),
        "source_count": len(sources),
        "viewer_url": viewer_url,
        "viewer_status": viewer_status,
        "viewer_content_type": viewer_content_type,
        "viewer_ok": viewer_ok,
        "route": body.get("route"),
        "pass": passed,
    }


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Stage 6 Direct Runtime Regression Report",
        "",
        "## Goal",
        "",
        "Verify that the Stage 5 runtime fixes still work on the live runtime at `localhost:8000`.",
        "",
        "## Checkpoints",
        "",
        "- Basic definition questions still answer in Korean.",
        "- Operational questions still answer in Korean.",
        "- Citations still click through to a real HTML viewer.",
        "",
        "## How to run",
        "",
        "```powershell",
        "python .\\deployment\\check_stage06_direct_runtime_regression.py",
        "```",
        "",
        "## Summary",
        "",
        f"- checked_at: `{report['checked_at']}`",
        f"- base_url: `{report['base_url']}`",
        f"- health_status: `{report['health_status']}`",
        f"- health_ok: `{report['health_ok']}`",
        f"- case_count: `{report['case_count']}`",
        f"- passed_count: `{report['passed_count']}`",
        f"- overall_pass: `{report['overall_pass']}`",
        "",
        "## Results",
        "",
        "| case_id | kind | status | sources | viewer | route |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for item in report["results"]:
        viewer_label = "200 text/html" if item["viewer_ok"] else f"{item['viewer_status']} {item['viewer_content_type']}"
        lines.append(
            "| {case_id} | {kind} | {status} | {sources} | {viewer} | {route} |".format(
                case_id=item["case_id"],
                kind=item["kind"],
                status="pass" if item["pass"] else "fail",
                sources=item["source_count"],
                viewer=viewer_label,
                route=item.get("route", ""),
            )
        )

    lines.extend(
        [
            "",
            "## Output",
            "",
            f"- JSON: `{JSON_PATH.as_posix()}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    health = requests.get(f"{BASE_URL}/health", timeout=10)
    results = [check_case(BASE_URL, case) for case in CASES]
    report = {
        "checked_at": utc_now(),
        "base_url": BASE_URL,
        "health_status": health.status_code,
        "health_ok": health.status_code == 200,
        "case_count": len(results),
        "passed_count": sum(1 for item in results if item["pass"]),
        "overall_pass": health.status_code == 200 and all(item["pass"] for item in results),
        "results": results,
    }

    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    REPORT_PATH.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
