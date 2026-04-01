from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any

import requests


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:8000"
OUTPUT_PATH = (
    REPO_ROOT / "data" / "manifests" / "generated" / "stage03-runtime-lock-report.json"
)


def port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    current_index = (
        (REPO_ROOT / "indexes" / "current.txt").read_text(encoding="utf-8").strip()
    )
    runbook_text = (REPO_ROOT / "deployment" / "operator-runbook-stage14.md").read_text(
        encoding="utf-8"
    )
    stage14_text = (REPO_ROOT / "docs" / "v2" / "stage14-runtime-launch.md").read_text(
        encoding="utf-8"
    )
    launcher_text = (REPO_ROOT / "deployment" / "start_runtime_stack.py").read_text(
        encoding="utf-8"
    )
    wrapper_text = (REPO_ROOT / "deployment" / "start_local_runtime.ps1").read_text(
        encoding="utf-8"
    )

    health_response = requests.get(f"{BASE_URL}/health", timeout=20)
    root_response = requests.get(f"{BASE_URL}/", timeout=20)
    chat_response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        json={"query": "오픈시프트가 뭐야", "mode": "operations"},
        timeout=30,
    )

    health = health_response.json()
    chat_payload = chat_response.json()
    sources = chat_payload.get("sources", []) or []
    first_source = sources[0] if sources else {}

    result: dict[str, Any] = {
        "base_url": BASE_URL,
        "expected_ports": {"gateway": 8000, "bridge": 18101, "opendocuments": 18102},
        "port_checks": {
            "gateway_8000": port_open(8000),
            "bridge_18101": port_open(18101),
            "opendocuments_18102": port_open(18102),
        },
        "health_checks": {
            "health_ok": health_response.ok and bool(health.get("ok")),
            "runtime_mode_company_chat_plus_local_embeddings": health.get(
                "runtime_mode"
            )
            == "company-chat-plus-local-embeddings",
            "active_index_matches_pointer": health.get("active_index_id")
            == current_index,
            "active_manifest_exists": Path(
                str(health.get("active_manifest_path", ""))
            ).exists(),
            "active_document_count_positive": int(
                health.get("active_document_count", 0)
            )
            > 0,
        },
        "http_checks": {
            "root_ok": root_response.ok
            and "text/html" in root_response.headers.get("content-type", ""),
            "chat_ok": chat_response.ok,
            "chat_has_sources": len(sources) >= 1,
            "chat_first_viewer_internal": str(
                first_source.get("viewer_url", "")
            ).startswith("/viewer/"),
        },
        "launcher_contract_checks": {
            "launcher_bridge_18101": '--bridge-port", type=int, default=18101'
            in launcher_text,
            "launcher_od_18102": '--od-port", type=int, default=18102' in launcher_text,
            "launcher_gateway_8000": '--gateway-port", type=int, default=8000'
            in launcher_text,
            "wrapper_mentions_locked_ports": all(
                token in wrapper_text for token in ("18101", "18102", "8000")
            ),
            "runbook_mentions_localhost_8000": "http://127.0.0.1:8000" in runbook_text,
            "stage14_doc_mentions_localhost_8000": any(
                token in stage14_text
                for token in (
                    "http://127.0.0.1:8000",
                    "gateway/UI: `8000`",
                    "gateway: `8000`",
                )
            ),
        },
        "active_index_id": health.get("active_index_id"),
        "current_index_pointer": current_index,
        "first_viewer_url": first_source.get("viewer_url", ""),
    }

    result["overall_pass"] = (
        all(result["port_checks"].values())
        and all(result["health_checks"].values())
        and all(result["http_checks"].values())
        and all(result["launcher_contract_checks"].values())
    )

    OUTPUT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
