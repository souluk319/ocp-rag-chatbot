from __future__ import annotations

import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = ROOT / "reports" / "build_logs" / "buyer_demo_live_packet.json"
REPORT_JSON = ROOT / "reports" / "build_logs" / "buyer_demo_live_packet_verification_report.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "buyer_demo_live_packet_verification_report.md"


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object json: {path}")
    return payload


def _fetch_status(url: str) -> int:
    with urllib.request.urlopen(url, timeout=60) as response:
        return int(response.status)


def _post_json_status(url: str, payload: dict[str, object]) -> int:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return int(response.status)


def main() -> int:
    packet = _load_json(PACKET_JSON)
    steps = [item for item in packet.get("steps") or [] if isinstance(item, dict)]

    get_probe_urls = [
        "http://127.0.0.1:8765/api/data-control-room",
        "http://127.0.0.1:8765/playbooks/wiki-runtime/active/backup_and_restore/index.html?embed=1",
        "http://127.0.0.1:8765/wiki/entities/etcd/index.html?embed=1",
    ]
    statuses = {url: _fetch_status(url) for url in get_probe_urls}
    statuses["http://127.0.0.1:8765/api/chat[POST]"] = _post_json_status(
        "http://127.0.0.1:8765/api/chat",
        {
            "query": "etcd 백업 절차와 관련 문서를 보여줘",
            "session_id": "buyer-demo-live-packet-verify",
            "mode": "ops",
            "user_id": "buyer-demo-live-packet-verify",
        },
    )

    report = {
        "status": "ok",
        "packet_exists": PACKET_JSON.exists(),
        "step_count": len(steps),
        "has_playbook_library_step": any(str(item.get("app_route") or "") == "/playbook-library" for item in steps),
        "has_workspace_step": any(str(item.get("app_route") or "") == "/workspace" for item in steps),
        "has_runtime_viewer_step": any("playbooks/wiki-runtime/active/backup_and_restore" in str(item.get("runtime_url") or "") for item in steps),
        "has_entity_hub_step": any("/wiki/entities/etcd/" in str(item.get("runtime_url") or "") for item in steps),
        "has_mixed_runtime_step": any("mixed_runtime_bridge" in str(item.get("expected_truth") or "") or "private_customer_pack_runtime" in str(item.get("expected_truth") or "") for item in steps),
        "expected_truth_badges": packet.get("expected_truth_badges") or [],
        "probe_statuses": statuses,
    }

    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(
        "# Buyer Demo Live Packet Verification Report\n\n"
        + f"- status: `{report['status']}`\n"
        + f"- step_count: `{report['step_count']}`\n"
        + f"- has_playbook_library_step: `{report['has_playbook_library_step']}`\n"
        + f"- has_workspace_step: `{report['has_workspace_step']}`\n"
        + f"- has_runtime_viewer_step: `{report['has_runtime_viewer_step']}`\n"
        + f"- has_entity_hub_step: `{report['has_entity_hub_step']}`\n"
        + f"- has_mixed_runtime_step: `{report['has_mixed_runtime_step']}`\n"
        + "\n".join(f"- {url} -> `{status}`" for url, status in statuses.items())
        + "\n",
        encoding="utf-8",
    )

    ok = (
        report["packet_exists"]
        and report["step_count"] >= 6
        and report["has_playbook_library_step"]
        and report["has_workspace_step"]
        and report["has_runtime_viewer_step"]
        and report["has_entity_hub_step"]
        and report["has_mixed_runtime_step"]
        and all(status == 200 for status in statuses.values())
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
