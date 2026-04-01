from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "data" / "manifests" / "generated" / "stage02-ui-streaming-report.json"
BASE_URL = "http://127.0.0.1:8000"


def parse_sse(text: str) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    for block in text.split("\n\n"):
        if not block.strip():
            continue
        event_name = "message"
        data_lines: list[str] = []
        for line in block.splitlines():
            if line.startswith("event:"):
                event_name = line[6:].strip()
            elif line.startswith("data:"):
                payload = line[5:]
                if payload.startswith(" "):
                    payload = payload[1:]
                data_lines.append(payload)
        raw = "\n".join(data_lines)
        if not raw:
            continue
        try:
            payload_obj = json.loads(raw)
        except json.JSONDecodeError:
            payload_obj = raw
        events.append({"event": event_name, "payload": payload_obj})

    sources = next((event["payload"] for event in events if event["event"] == "sources"), [])
    chunks = [str(event["payload"]) for event in events if event["event"] == "chunk"]
    done = next((event["payload"] for event in events if event["event"] == "done"), {})
    return {"events": events, "sources": sources, "answer": "".join(chunks), "done": done}


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {"base_url": BASE_URL}

    root_response = requests.get(f"{BASE_URL}/", timeout=20)
    root_response.raise_for_status()
    root_html = root_response.text

    required_ui_strings = [
        "OCP 운영 도우미",
        "질문 보내기",
        "응답 아래 출처를 누르면 HTML 문서를 바로 열 수 있습니다.",
        "서비스 정상",
    ]
    ui_checks = {value: value in root_html for value in required_ui_strings}
    result["ui_checks"] = ui_checks
    result["root_content_type"] = root_response.headers.get("content-type", "")

    stream_response = requests.post(
        f"{BASE_URL}/api/v1/chat/stream",
        json={"query": "오픈시프트가 뭐야", "mode": "operations"},
        stream=True,
        timeout=30,
    )
    stream_response.raise_for_status()
    raw_stream = b"".join(chunk for chunk in stream_response.iter_content(chunk_size=None) if chunk)
    decoded_stream = raw_stream.decode("utf-8", errors="replace")
    parsed = parse_sse(decoded_stream)

    answer_text = parsed["answer"]
    sources = parsed["sources"] if isinstance(parsed["sources"], list) else []
    first_source = sources[0] if sources else {}
    viewer_url = str(first_source.get("viewer_url", ""))
    viewer_ok = False
    viewer_contains_openshift = False
    if viewer_url.startswith("/viewer/"):
      viewer_response = requests.get(f"{BASE_URL}{viewer_url}", timeout=20)
      viewer_ok = viewer_response.ok and "text/html" in viewer_response.headers.get("content-type", "")
      viewer_contains_openshift = "OpenShift" in viewer_response.text

    result["stream_checks"] = {
        "content_type": stream_response.headers.get("content-type", ""),
        "contains_replacement_char": "�" in answer_text,
        "contains_bad_english_fallback": "provided context does not contain" in answer_text.lower(),
        "contains_korean_product_name": "오픈시프트" in answer_text or "OpenShift Container Platform" in answer_text,
        "source_count": len(sources),
        "viewer_url": viewer_url,
        "viewer_ok": viewer_ok,
        "viewer_contains_openshift": viewer_contains_openshift,
    }

    result["answer_preview"] = answer_text[:500]
    result["overall_pass"] = all(ui_checks.values()) and not result["stream_checks"]["contains_replacement_char"] and not result["stream_checks"]["contains_bad_english_fallback"] and result["stream_checks"]["source_count"] >= 1 and viewer_ok

    OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
