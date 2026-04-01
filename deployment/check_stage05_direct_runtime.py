from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "data" / "manifests" / "generated" / "stage05-direct-runtime-report.json"
BASE_URL = "http://127.0.0.1:8000"

CASES = [
    {
        "id": "definition-openshift",
        "query": "오픈시프트가 뭐야",
    },
    {
        "id": "definition-ocp",
        "query": "OCP가 뭐야",
    },
    {
        "id": "ops-firewall",
        "query": "설치 시 방화벽에서 어떤 포트와 예외를 허용해야 하나요?",
    },
    {
        "id": "ops-update",
        "query": "업데이트 전에 확인해야 할 사항은 무엇인가요?",
    },
    {
        "id": "ops-disconnected-mirror",
        "query": "폐쇄망 설치에서 oc-mirror 플러그인으로 이미지를 미러링하려면 어떤 문서를 봐야 하나요?",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def has_hangul(text: str) -> bool:
    return any("\uac00" <= char <= "\ud7a3" for char in text)


def main() -> int:
    health = requests.get(f"{BASE_URL}/health", timeout=10)
    results: list[dict[str, object]] = []

    for case in CASES:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={"query": case["query"]},
            timeout=20,
        )
        body = response.json()
        sources = body.get("sources") or []
        viewer_url = str(sources[0].get("viewer_url", "")).strip() if sources else ""
        viewer_status = None
        viewer_content_type = ""
        viewer_ok = False
        if viewer_url:
            viewer = requests.get(f"{BASE_URL}{viewer_url}", timeout=10)
            viewer_status = viewer.status_code
            viewer_content_type = viewer.headers.get("content-type", "")
            viewer_ok = viewer.status_code == 200 and "text/html" in viewer_content_type.lower()

        answer = str(body.get("answer", ""))
        result = {
            "case_id": case["id"],
            "query": case["query"],
            "status_code": response.status_code,
            "answer_preview": answer[:300],
            "answer_has_hangul": has_hangul(answer),
            "source_count": len(sources),
            "viewer_url": viewer_url,
            "viewer_status": viewer_status,
            "viewer_content_type": viewer_content_type,
            "viewer_ok": viewer_ok,
            "route": body.get("route"),
            "pass": response.status_code == 200 and has_hangul(answer) and len(sources) >= 1 and viewer_ok,
        }
        results.append(result)

    payload = {
        "checked_at": utc_now(),
        "base_url": BASE_URL,
        "health_status": health.status_code,
        "health_ok": health.status_code == 200,
        "case_count": len(results),
        "passed_count": sum(1 for item in results if item["pass"]),
        "overall_pass": health.status_code == 200 and all(item["pass"] for item in results),
        "results": results,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
