from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
QUESTION_SET_PATH = REPO_ROOT / "deployment" / "stage08_demo_questions.json"
REPORT_MD_PATH = REPO_ROOT / "docs" / "v2" / "2026-04-01" / "stage-08-report.md"
REPORT_JSON_PATH = REPO_ROOT / "docs" / "v2" / "2026-04-01" / "stage-08-report.json"
BASE_URL = "http://127.0.0.1:8000"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def has_hangul(text: str) -> bool:
    return any("\uac00" <= c <= "\ud7a3" for c in text)


def fetch_viewer(viewer_url: str) -> dict[str, object]:
    if not viewer_url:
        return {"ok": False, "status": None, "content_type": ""}
    response = requests.get(f"{BASE_URL}{viewer_url}", timeout=15)
    content_type = response.headers.get("content-type", "")
    return {
        "ok": response.status_code == 200 and "text/html" in content_type.lower(),
        "status": response.status_code,
        "content_type": content_type,
    }


def check_single_question(query: str, expected_family: str) -> dict[str, object]:
    response = requests.post(f"{BASE_URL}/api/v1/chat", json={"query": query}, timeout=30)
    body = response.json()
    sources = body.get("sources") or []
    first = sources[0] if sources and isinstance(sources[0], dict) else {}
    viewer_url = str(first.get("viewer_url", ""))
    viewer = fetch_viewer(viewer_url)
    pass_result = (
        response.status_code == 200
        and has_hangul(str(body.get("answer", "")))
        and len(sources) >= 1
        and viewer["ok"]
        and expected_family in viewer_url
    )
    return {
        "query": query,
        "status_code": response.status_code,
        "route": body.get("route"),
        "answer_preview": str(body.get("answer", ""))[:220],
        "answer_has_hangul": has_hangul(str(body.get("answer", ""))),
        "source_count": len(sources),
        "viewer_url": viewer_url,
        "viewer_ok": viewer["ok"],
        "viewer_status": viewer["status"],
        "viewer_content_type": viewer["content_type"],
        "expected_family": expected_family,
        "pass": pass_result,
    }


def check_follow_up(turn_1: str, turn_2: str, expected_family: str) -> dict[str, object]:
    session = requests.Session()
    first_response = session.post(f"{BASE_URL}/api/v1/chat", json={"query": turn_1}, timeout=30)
    first_body = first_response.json()
    second_response = session.post(f"{BASE_URL}/api/v1/chat", json={"query": turn_2}, timeout=30)
    second_body = second_response.json()

    first_sources = first_body.get("sources") or []
    second_sources = second_body.get("sources") or []
    second_first = second_sources[0] if second_sources and isinstance(second_sources[0], dict) else {}
    second_viewer_url = str(second_first.get("viewer_url", ""))
    viewer = fetch_viewer(second_viewer_url)

    pass_result = (
        first_response.status_code == 200
        and second_response.status_code == 200
        and has_hangul(str(second_body.get("answer", "")))
        and len(second_sources) >= 1
        and viewer["ok"]
        and expected_family in second_viewer_url
    )
    return {
        "turn_1": turn_1,
        "turn_2": turn_2,
        "turn_1_source_count": len(first_sources),
        "turn_2_source_count": len(second_sources),
        "turn_2_route": second_body.get("route"),
        "turn_2_answer_preview": str(second_body.get("answer", ""))[:220],
        "turn_2_answer_has_hangul": has_hangul(str(second_body.get("answer", ""))),
        "viewer_url": second_viewer_url,
        "viewer_ok": viewer["ok"],
        "viewer_status": viewer["status"],
        "viewer_content_type": viewer["content_type"],
        "expected_family": expected_family,
        "pass": pass_result,
    }


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Stage 8 Demo Readiness Report",
        "",
        "## Verdict",
        "",
        f"`{'pass' if report['overall_pass'] else 'partial'}`",
        "",
        "Stage 8 is about demo readiness only.",
        "It is not a production-readiness claim.",
        "",
        "## Direct demo checks",
        "",
        f"- checked_at: `{report['checked_at']}`",
        f"- base_url: `{report['base_url']}`",
        f"- health_status: `{report['health_status']}`",
        f"- ui_status: `{report['ui_status']}`",
        f"- primary_passed: `{report['primary_passed_count']}/{report['primary_case_count']}`",
        f"- follow_up_pass: `{report['follow_up']['pass']}`",
        "",
        "## Primary demo questions",
        "",
        "| id | status | sources | viewer | route |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in report["primary_results"]:
        viewer_label = "200 text/html" if item["viewer_ok"] else f"{item['viewer_status']} {item['viewer_content_type']}"
        lines.append(
            f"| {item['id']} | {'pass' if item['pass'] else 'fail'} | {item['source_count']} | {viewer_label} | {item['route']} |"
        )

    lines.extend(
        [
            "",
            "## Follow-up demo",
            "",
            f"- turn_2 status: `{'pass' if report['follow_up']['pass'] else 'fail'}`",
            f"- turn_2 sources: `{report['follow_up']['turn_2_source_count']}`",
            f"- turn_2 viewer: `{'200 text/html' if report['follow_up']['viewer_ok'] else str(report['follow_up']['viewer_status'])}`",
            "",
            "## Secondary watchlist",
            "",
        ]
    )
    for item in report["secondary_watchlist"]:
        lines.append(f"- `{item['query']}`: {item['risk']}")

    lines.extend(
        [
            "",
            "## User-visible checkpoint",
            "",
            "- Open `http://127.0.0.1:8000`",
            "- Ask the primary demo questions in order",
            "- Click the first citation on each answer",
            "- Run the follow-up pair after the update question",
            "",
            "## Output",
            "",
            f"- JSON: `{REPORT_JSON_PATH.as_posix()}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    question_set = json.loads(QUESTION_SET_PATH.read_text(encoding="utf-8"))
    health = requests.get(f"{BASE_URL}/health", timeout=15)
    ui = requests.get(BASE_URL, timeout=15)

    primary_results = []
    for item in question_set["primary_demo_questions"]:
        result = check_single_question(item["query"], item["expected_viewer_family"])
        result["id"] = item["id"]
        result["reason"] = item["reason"]
        primary_results.append(result)

    follow_up = question_set["follow_up_demo"]
    follow_up_result = check_follow_up(
        follow_up["turn_1"],
        follow_up["turn_2"],
        follow_up["expected_viewer_family"],
    )

    report = {
        "checked_at": utc_now(),
        "base_url": BASE_URL,
        "health_status": health.status_code,
        "ui_status": ui.status_code,
        "primary_case_count": len(primary_results),
        "primary_passed_count": sum(1 for item in primary_results if item["pass"]),
        "primary_results": primary_results,
        "follow_up": follow_up_result,
        "secondary_watchlist": question_set["secondary_watchlist"],
    }
    report["overall_pass"] = (
        report["health_status"] == 200
        and report["ui_status"] == 200
        and report["primary_passed_count"] == report["primary_case_count"]
        and report["follow_up"]["pass"]
    )

    REPORT_JSON_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
