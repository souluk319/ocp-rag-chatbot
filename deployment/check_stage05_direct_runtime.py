from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "v2" / "2026-04-01" / "stage-05-direct-runtime-report.md"

DEFAULT_CASES: list[dict[str, str]] = [
    {"id": "def-01", "query": "\uc624\ud508\uc2dc\ud504\ud2b8\uac00 \ubb50\uc57c"},
    {"id": "def-02", "query": "OCP\uac00 \ubb50\uc57c"},
    {"id": "ops-01", "query": "\uc5c5\ub370\uc774\ud2b8 \uc804\uc5d0 \ud655\uc778\ud574\uc57c \ud560 \uc0ac\ud56d\uc740 \ubb34\uc5c7\uc778\uac00\uc694?"},
    {"id": "ops-02", "query": "\ubc29\ud654\ubcbd \uc124\uc815\uc5d0\uc11c \uc5b4\ub5a4 \ud3ec\ud2b8\ub97c \uc5f4\uc5b4\uc57c \ud558\ub098\uc694?"},
    {
        "id": "ops-03",
        "query": "disconnected/oc-mirror \uad00\ub828 \ubb38\uc11c\ub294 \uc5b4\ub514\ub97c \ubcf4\uba74 \ub418\ub098\uc694?",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a direct localhost:8000 Stage 5 runtime verification.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--request-timeout-seconds", type=float, default=20.0)
    parser.add_argument("--health-timeout-seconds", type=float, default=20.0)
    return parser.parse_args()


def contains_korean(text: str) -> bool:
    return bool(re.search(r"[\uac00-\ud7a3]", text or ""))


def fetch_viewer(session: requests.Session, base_url: str, source: dict[str, Any]) -> dict[str, Any]:
    viewer_url = str(source.get("viewer_url", "")).strip()
    resolved_url = viewer_url
    if viewer_url.startswith("/"):
        resolved_url = urljoin(base_url.rstrip("/") + "/", viewer_url.lstrip("/"))

    if not resolved_url:
        return {
            "viewer_url": "",
            "resolved_url": "",
            "status_code": None,
            "content_type": "",
            "reachable": False,
        }

    response = session.get(resolved_url, timeout=20)
    body = response.text
    content_type = response.headers.get("content-type", "")
    return {
        "viewer_url": viewer_url,
        "resolved_url": resolved_url,
        "status_code": response.status_code,
        "content_type": content_type,
        "html_detected": "<html" in body.lower(),
        "reachable": response.status_code == 200 and "text/html" in content_type.lower() and "<html" in body.lower(),
    }


def run_case(
    *,
    session: requests.Session,
    base_url: str,
    case: dict[str, str],
    request_timeout_seconds: float,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": case["id"],
        "query": case["query"],
        "status": "fail",
        "answer_preview": "",
        "answer_contains_korean": False,
        "citation_count": 0,
        "first_viewer": {},
        "done_payload": {},
        "error": "",
    }

    try:
        response = session.post(
            f"{base_url.rstrip('/')}/api/v1/chat",
            json={"query": case["query"], "mode": "operations"},
            timeout=request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        answer_text = str(payload.get("answer", ""))
        sources = payload.get("sources", [])
        done_payload = {
            "conversationId": payload.get("conversationId", ""),
            "mode": payload.get("mode", ""),
            "rewrittenQuery": payload.get("rewrittenQuery", ""),
        }
        first_viewer = fetch_viewer(session, base_url, sources[0]) if sources else {}

        answer_contains_korean = contains_korean(answer_text)
        citation_count = len(sources)
        success = bool(answer_contains_korean and citation_count > 0 and first_viewer.get("reachable", False))

        result.update(
            {
                "status": "pass" if success else "fail",
                "answer_preview": answer_text[:240],
                "answer_contains_korean": answer_contains_korean,
                "citation_count": citation_count,
                "first_viewer": first_viewer,
                "done_payload": done_payload,
                "source_paths": [str(source.get("document_path", "")).strip() for source in sources[:3]],
            }
        )
    except Exception as exc:  # pragma: no cover - direct runtime probe
        result["error"] = str(exc)

    return result


def render_report(*, base_url: str, health: dict[str, Any], cases: list[dict[str, Any]]) -> str:
    total = len(cases)
    passed = sum(1 for case in cases if case["status"] == "pass")
    lines = [
        "# Stage 5 Direct Runtime Check",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        f"- Base URL: `{base_url}`",
        f"- Health: `{json.dumps(health, ensure_ascii=False)}`",
        f"- Passed cases: `{passed}/{total}`",
        "",
        "| Case | Korean response | Citations | First viewer | Status |",
        "| --- | --- | ---: | --- | --- |",
    ]

    for case in cases:
        viewer = case.get("first_viewer", {}) or {}
        viewer_flag = "pass" if viewer.get("reachable", False) else "fail"
        lines.append(
            f"| `{case['query']}` | `{str(case['answer_contains_korean']).lower()}` | "
            f"`{case['citation_count']}` | `{viewer_flag}` | `{case['status']}` |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This check hits `localhost:8000` directly and does not modify app logic.",
            "- Each case records Korean response presence, citation count, and the first viewer reachability.",
            "- A case passes only when all three are true.",
            "",
            "## Case Details",
            "",
        ]
    )

    for case in cases:
        viewer = case.get("first_viewer", {}) or {}
        lines.extend(
            [
                f"### {case['id']}",
                f"- Query: `{case['query']}`",
                f"- Status: `{case['status']}`",
                f"- Korean response: `{case['answer_contains_korean']}`",
                f"- Citation count: `{case['citation_count']}`",
                f"- First viewer reachable: `{viewer.get('reachable', False)}`",
                f"- Viewer URL: `{viewer.get('resolved_url', '')}`",
                f"- Answer preview: {case['answer_preview'] or '(empty)'}",
                f"- Error: `{case['error'] or ''}`",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    args = parse_args()
    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    health_url = f"{args.base_url.rstrip('/')}/health"
    try:
        health_response = session.get(health_url, timeout=args.health_timeout_seconds)
        health = {
            "status_code": health_response.status_code,
            "ok": health_response.status_code == 200,
            "body": health_response.json()
            if health_response.headers.get("content-type", "").lower().startswith("application/json")
            else health_response.text[:300],
        }
    except Exception as exc:  # pragma: no cover - direct runtime probe
        health = {"ok": False, "error": str(exc)}

    cases = [
        run_case(session=session, base_url=args.base_url, case=case, request_timeout_seconds=args.request_timeout_seconds)
        for case in DEFAULT_CASES
    ]

    report = render_report(base_url=args.base_url, health=health, cases=cases)
    output_path.write_text(report, encoding="utf-8")

    failed = [case for case in cases if case["status"] != "pass"]
    summary = {
        "base_url": args.base_url,
        "health_ok": bool(health.get("ok", False)),
        "passed": len(cases) - len(failed),
        "total": len(cases),
        "failed_case_ids": [case["id"] for case in failed],
        "output": str(output_path),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if failed or not health.get("ok", False):
        raise SystemExit(f"Stage 5 direct runtime check found failures. See {output_path}")


if __name__ == "__main__":
    main()
