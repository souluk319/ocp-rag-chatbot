from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.runtime_config import load_runtime_config
from deployment.stage11_bundle_utils import repo_relative, utc_now, write_json


def default_smoke_output() -> Path:
    return (
        REPO_ROOT
        / "data"
        / "manifests"
        / "generated"
        / "stage02-live-runtime-smoke.json"
    )


def default_output() -> Path:
    return (
        REPO_ROOT
        / "data"
        / "manifests"
        / "generated"
        / "stage02-runtime-path-authenticity-report.json"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that the Stage 2 runtime path uses bridge + OpenDocuments + gateway with the approved runtime contract."
    )
    parser.add_argument("--index", default="current")
    parser.add_argument("--smoke-output", type=Path, default=default_smoke_output())
    parser.add_argument("--output", type=Path, default=default_output())
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_log(path_str: str) -> str:
    path = Path(path_str)
    if not path.is_absolute():
        path = REPO_ROOT / path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def has_model(models_payload: dict, model_id: str) -> bool:
    data = models_payload.get("data", [])
    return any(
        str(item.get("id", "")).strip() == model_id
        for item in data
        if isinstance(item, dict)
    )


def turn_has_done_payload(turn: dict) -> bool:
    payload = turn.get("done_payload", {})
    return isinstance(payload, dict) and bool(payload.get("conversationId"))


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def main() -> int:
    args = parse_args()
    config = load_runtime_config()
    smoke_output = args.smoke_output.resolve()
    report_output = args.output.resolve()

    bridge_port = find_free_port()
    od_port = find_free_port()
    gateway_port = find_free_port()

    smoke_command = [
        sys.executable,
        str(REPO_ROOT / "deployment" / "run_live_runtime_smoke.py"),
        "--index",
        args.index,
        "--bridge-port",
        str(bridge_port),
        "--od-port",
        str(od_port),
        "--gateway-port",
        str(gateway_port),
        "--output",
        str(smoke_output),
    ]
    smoke_result = subprocess.run(
        smoke_command, cwd=str(REPO_ROOT), text=True, capture_output=True, check=False
    )
    if not smoke_output.exists():
        raise SystemExit(f"Stage 2 smoke output was not produced: {smoke_output}")

    smoke_report = load_json(smoke_output)
    bridge_log = read_log(
        str(smoke_report.get("logs", {}).get("bridge", {}).get("path", ""))
    )
    od_log = read_log(
        str(smoke_report.get("logs", {}).get("opendocuments", {}).get("path", ""))
    )
    gateway_log = read_log(
        str(smoke_report.get("logs", {}).get("gateway", {}).get("path", ""))
    )

    bridge_ready = smoke_report.get("bridge_ready", {})
    bridge_evidence = smoke_report.get("bridge_evidence", {})
    bridge_models = smoke_report.get("bridge_models", {})
    bridge_health = smoke_report.get("bridge_health", {})
    gateway_health = smoke_report.get("gateway_health", {})
    turns = smoke_report.get("turns", [])
    vector_dimensions = int(smoke_report.get("vector_dimensions", 0) or 0)
    evidence_telemetry = (
        bridge_evidence.get("telemetry", {})
        if isinstance(bridge_evidence, dict)
        else {}
    )
    last_chat_target_path = str(
        evidence_telemetry.get("last_chat_target_path", "")
    ).strip()

    checks = {
        "bridge_health_ok": bool(bridge_health.get("ok") is True),
        "bridge_ready_ok": bool(bridge_ready.get("ready") is True),
        "bridge_evidence_ok": bool(bridge_evidence.get("ok") is True),
        "runtime_mode_company_only": str(bridge_health.get("runtime_mode", "")).strip()
        == "company-only",
        "local_chat_fallback_disabled": bool(
            bridge_health.get("local_chat_fallback") is False
        ),
        "bridge_evidence_runtime_mode_company_only": str(
            bridge_evidence.get("runtime_mode", "")
        ).strip()
        == "company-only",
        "bridge_ready_model_matches_config": str(
            bridge_ready.get("embedding_model", "")
        ).strip()
        == config.embedding_model,
        "bridge_ready_dimensions_match_config": int(
            bridge_ready.get("embedding_dimensions", 0) or 0
        )
        == config.embedding_dimensions,
        "bridge_ready_dimensions_match_active_index": int(
            bridge_ready.get("embedding_dimensions", 0) or 0
        )
        == vector_dimensions,
        "bridge_ready_transport_company_proxy": str(
            bridge_ready.get("embedding_transport", "")
        ).strip()
        == "company-proxy",
        "bridge_evidence_model_matches_config": str(
            bridge_evidence.get("embedding_model", "")
        ).strip()
        == config.embedding_model,
        "bridge_evidence_dimensions_match_config": int(
            bridge_evidence.get("embedding_dimensions", 0) or 0
        )
        == config.embedding_dimensions,
        "bridge_evidence_transport_company_proxy": str(
            bridge_evidence.get("embedding_transport", "")
        ).strip()
        == "company-proxy",
        "bridge_models_include_configured_chat_model": has_model(
            bridge_models, config.chat_model
        ),
        "opendocuments_openai_plugin_loaded": "Loading model plugin: opendocuments-model-openai"
        in od_log,
        "opendocuments_no_embed_probe_failure": "embed probe failed"
        not in od_log.lower(),
        "opendocuments_no_ollama_reference": "ollama" not in od_log.lower(),
        "bridge_embedding_requests_seen": "POST /v1/embeddings" in bridge_log,
        "bridge_chat_requests_seen": "POST /v1/chat/completions" in bridge_log,
        "bridge_evidence_embedding_requests_seen": int(
            evidence_telemetry.get("embedding_requests", 0) or 0
        )
        > 0,
        "bridge_evidence_upstream_embedding_success_seen": int(
            evidence_telemetry.get("upstream_embedding_success_count", 0) or 0
        )
        > 0,
        "bridge_evidence_upstream_embedding_error_absent": int(
            evidence_telemetry.get("upstream_embedding_error_count", 0) or 0
        )
        == 0,
        "bridge_evidence_chat_requests_seen": int(
            evidence_telemetry.get("chat_requests", 0) or 0
        )
        > 0,
        "bridge_evidence_upstream_chat_success_seen": int(
            evidence_telemetry.get("upstream_chat_success_count", 0) or 0
        )
        > 0,
        "bridge_evidence_fallback_chat_absent": int(
            evidence_telemetry.get("fallback_chat_count", 0) or 0
        )
        == 0,
        "bridge_evidence_last_chat_target_path_valid": last_chat_target_path
        in {"/chat/completions", "/v1/chat/completions"},
        "bridge_evidence_last_embedding_target_path_valid": str(
            evidence_telemetry.get("last_embedding_target_path", "")
        ).strip()
        in {"/embeddings", "/v1/embeddings"},
        "bridge_evidence_last_embedding_status_ok": int(
            evidence_telemetry.get("last_embedding_status", 0) or 0
        )
        == 200,
        "bridge_evidence_last_embedding_model_matches_config": str(
            evidence_telemetry.get("last_embedding_model", "")
        ).strip()
        == config.embedding_model,
        "bridge_evidence_last_embedding_dimensions_match_active_index": int(
            evidence_telemetry.get("last_embedding_dimensions", 0) or 0
        )
        == vector_dimensions,
        "gateway_health_ok": bool(gateway_health.get("ok") is True),
        "gateway_port_conflict_absent": "error while attempting to bind on address"
        not in gateway_log.lower()
        and "eaddrinuse" not in od_log.lower(),
        "gateway_stream_requests_seen": "POST /api/v1/chat/stream" in gateway_log,
        "smoke_turns_executed": len(turns) >= 2
        and all(turn_has_done_payload(turn) for turn in turns[:2]),
    }

    report = {
        "stage": 2,
        "started_at": utc_now(),
        "index": args.index,
        "ports": {
            "bridge": bridge_port,
            "opendocuments": od_port,
            "gateway": gateway_port,
        },
        "runtime_contract": {
            "chat_model": config.chat_model,
            "embedding_model": config.embedding_model,
            "embedding_dimensions": config.embedding_dimensions,
            "runtime_mode": config.runtime_mode(),
        },
        "live_smoke": {
            "command": smoke_command,
            "exit_code": smoke_result.returncode,
            "stdout": smoke_result.stdout[-1000:],
            "stderr": smoke_result.stderr[-1000:],
            "report_path": repo_relative(smoke_output),
            "overall_pass": smoke_report.get("overall_pass"),
        },
        "checks": checks,
        "overall_pass": all(checks.values()),
        "notes": [
            "Stage 2 is a runtime-path authenticity gate.",
            "It does not require retrieval quality or citation quality to be green yet.",
            "Those quality gates remain in later stages.",
        ],
        "completed_at": utc_now(),
    }

    report_output.parent.mkdir(parents=True, exist_ok=True)
    write_json(report_output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
