from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.runtime_config import load_runtime_config
from deployment.run_live_runtime_smoke import (
    default_opendocuments_root,
    detect_vector_dimensions,
    ensure_active_workspace,
    node20_launcher,
    resolve_index_id,
    runtime_workspace_for,
    start_process,
    tail_log,
    wait_for_json,
    wait_for_status,
    write_runtime_config,
)
from deployment.stage11_activation_utils import load_index_manifest
from deployment.stage11_bundle_utils import repo_relative, utc_now, write_json


def default_output_path() -> Path:
    return REPO_ROOT / "data" / "manifests" / "generated" / "stage14-runtime-launch-report.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start the v2 runtime stack (bridge -> OpenDocuments -> gateway) for operator use."
    )
    parser.add_argument("--index", default="current")
    parser.add_argument("--index-root", type=Path, default=REPO_ROOT / "indexes")
    parser.add_argument("--opendocuments-root", type=Path, default=default_opendocuments_root())
    parser.add_argument("--runtime-workspace", type=Path)
    parser.add_argument("--bridge-port", type=int, default=18101)
    parser.add_argument("--od-port", type=int, default=18102)
    parser.add_argument("--gateway-port", type=int, default=8000)
    parser.add_argument("--startup-timeout-seconds", type=float, default=90.0)
    parser.add_argument("--hold-seconds", type=float, default=0.0)
    parser.add_argument("--output", type=Path, default=default_output_path())
    parser.add_argument(
        "--skip-viewer-check",
        action="store_true",
        help="Skip the startup viewer click-through check.",
    )
    return parser.parse_args()


def viewer_startup_check(gateway_base_url: str, index_manifest: dict, *, skip: bool) -> dict[str, object]:
    if skip:
        return {"skipped": True, "pass": True}

    documents = index_manifest.get("documents", [])
    if not documents:
        return {"skipped": False, "pass": False, "reason": "index manifest has no documents"}

    viewer_url = str(documents[0].get("viewer_url", "")).strip()
    if not viewer_url:
        return {"skipped": False, "pass": False, "reason": "first document has no viewer_url"}

    resolved = gateway_base_url.rstrip("/") + viewer_url if viewer_url.startswith("/") else viewer_url
    response = requests.get(resolved, timeout=30)
    content_type = response.headers.get("content-type", "")
    body = response.text[:400]
    return {
        "skipped": False,
        "viewer_url": viewer_url,
        "resolved_url": resolved,
        "status_code": response.status_code,
        "content_type": content_type,
        "pass": response.status_code == 200 and "text/html" in content_type.lower() and "<html" in body.lower(),
    }


def main() -> int:
    args = parse_args()
    config = load_runtime_config()
    missing = config.missing_required_keys()
    if missing:
        raise SystemExit(f"Runtime config is incomplete: {missing}")

    index_id = resolve_index_id(args.index, args.index_root)
    index_dir, index_manifest = load_index_manifest(index_id, index_root=args.index_root)
    active_workspace = ensure_active_workspace(index_dir.name)
    active_data_dir = active_workspace / ".opendocuments-stage11"
    runtime_workspace = runtime_workspace_for(index_dir.name, args.runtime_workspace)
    runtime_config_path = write_runtime_config(runtime_workspace)

    bridge_base_url = f"http://127.0.0.1:{args.bridge_port}"
    od_base_url = f"http://127.0.0.1:{args.od_port}"
    gateway_base_url = f"http://127.0.0.1:{args.gateway_port}"
    output_path = args.output.resolve()
    log_dir = output_path.parent / f"{output_path.stem}-logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    vector_dimensions = detect_vector_dimensions(
        opendocuments_root=args.opendocuments_root,
        data_dir=active_data_dir,
        log_dir=log_dir,
    )

    env_base = os.environ.copy()
    env_base["PYTHONIOENCODING"] = "utf-8"

    bridge_env = dict(env_base)
    bridge_env["OD_EMBEDDING_DIMENSIONS"] = str(vector_dimensions)

    od_env = dict(env_base)
    od_env.update(
        {
            "OPENAI_BASE_URL": f"{bridge_base_url}/v1",
            "OPENAI_API_KEY": env_base.get("OPENAI_API_KEY", "stage14-local"),
            "OD_CHAT_MODEL": config.chat_model,
            "OD_EMBEDDING_MODEL": config.embedding_model,
            "OD_EMBEDDING_DIMENSIONS": str(vector_dimensions),
            "OPENDOCUMENTS_DATA_DIR": str(active_data_dir),
        }
    )

    gateway_env = dict(env_base)
    gateway_env["OD_SERVER_BASE_URL"] = od_base_url
    gateway_env["OD_EMBEDDING_DIMENSIONS"] = str(vector_dimensions)

    report: dict[str, object] = {
        "started_at": utc_now(),
        "index_id": index_manifest.get("index_id", index_dir.name),
        "bundle_id": index_manifest.get("bundle_id", ""),
        "active_workspace": repo_relative(active_workspace),
        "active_data_dir": repo_relative(active_data_dir),
        "runtime_workspace": repo_relative(runtime_workspace),
        "runtime_config_path": repo_relative(runtime_config_path),
        "opendocuments_root": str(args.opendocuments_root),
        "vector_dimensions": vector_dimensions,
        "ports": {
            "bridge": args.bridge_port,
            "opendocuments": args.od_port,
            "gateway": args.gateway_port,
        },
        "managed_runtime": {
            "gateway_injected_od_server_base_url": od_base_url,
            "chat_model": config.chat_model,
            "embedding_model": config.embedding_model,
        },
    }

    processes = []
    exit_code = 0

    try:
        bridge = start_process(
            name="bridge",
            command=[
                sys.executable,
                "-m",
                "uvicorn",
                "app.opendocuments_openai_bridge:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(args.bridge_port),
            ],
            cwd=REPO_ROOT,
            env=bridge_env,
            log_path=log_dir / "bridge.log",
        )
        processes.append(bridge)
        bridge_health = wait_for_json(
            f"{bridge_base_url}/health",
            timeout_seconds=args.startup_timeout_seconds,
            predicate=lambda payload: isinstance(payload, dict) and payload.get("ok") is True,
        )
        bridge_ready = wait_for_json(
            f"{bridge_base_url}/ready",
            timeout_seconds=args.startup_timeout_seconds,
            predicate=lambda payload: isinstance(payload, dict) and payload.get("ready") is True,
        )
        bridge_evidence = wait_for_json(
            f"{bridge_base_url}/evidence",
            timeout_seconds=args.startup_timeout_seconds,
            predicate=lambda payload: isinstance(payload, dict) and payload.get("ok") is True,
        )
        bridge_models = wait_for_status(
            f"{bridge_base_url}/v1/models",
            timeout_seconds=args.startup_timeout_seconds,
            expected_status=200,
        )

        od_server = start_process(
            name="opendocuments",
            command=node20_launcher()
            + [
                str(args.opendocuments_root / "packages" / "cli" / "dist" / "index.js"),
                "start",
                "--port",
                str(args.od_port),
                "--no-web",
            ],
            cwd=runtime_workspace,
            env=od_env,
            log_path=log_dir / "opendocuments.log",
        )
        processes.append(od_server)
        od_health = wait_for_json(
            f"{od_base_url}/api/v1/health",
            timeout_seconds=args.startup_timeout_seconds,
            predicate=lambda payload: isinstance(payload, dict) and payload.get("status") == "ok",
        )

        gateway = start_process(
            name="gateway",
            command=[
                sys.executable,
                "-m",
                "uvicorn",
                "app.ocp_runtime_gateway:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(args.gateway_port),
            ],
            cwd=REPO_ROOT,
            env=gateway_env,
            log_path=log_dir / "gateway.log",
        )
        processes.append(gateway)
        gateway_health = wait_for_json(
            f"{gateway_base_url}/health",
            timeout_seconds=args.startup_timeout_seconds,
            predicate=lambda payload: isinstance(payload, dict) and payload.get("ok") is True,
        )

        viewer_check = viewer_startup_check(gateway_base_url, index_manifest, skip=args.skip_viewer_check)

        report["health"] = {
            "bridge": bridge_health,
            "bridge_ready": bridge_ready,
            "bridge_evidence": bridge_evidence,
            "bridge_models": bridge_models,
            "opendocuments": od_health,
            "gateway": gateway_health,
            "viewer_check": viewer_check,
        }
        report["endpoints"] = {
            "bridge_health": f"{bridge_base_url}/health",
            "bridge_ready": f"{bridge_base_url}/ready",
            "bridge_evidence": f"{bridge_base_url}/evidence",
            "bridge_models": f"{bridge_base_url}/v1/models",
            "opendocuments_health": f"{od_base_url}/api/v1/health",
            "gateway_health": f"{gateway_base_url}/health",
            "gateway_chat_stream": f"{gateway_base_url}/api/v1/chat/stream",
        }
        report["startup_pass"] = bool(viewer_check.get("pass", False))

        print(
            json.dumps(
                {
                    "startup_pass": report["startup_pass"],
                    "index_id": report["index_id"],
                    "embedding_model": config.embedding_model,
                    "embedding_dimensions": vector_dimensions,
                    "gateway_chat_stream": report["endpoints"]["gateway_chat_stream"],
                    "viewer_check": viewer_check,
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        if not report["startup_pass"]:
            raise SystemExit("Runtime stack startup checks failed.")

        if args.hold_seconds > 0:
            time.sleep(args.hold_seconds)
        else:
            print("[info] Runtime stack is running. Press Ctrl+C to stop.")
            while True:
                time.sleep(1.0)
    except KeyboardInterrupt:
        report["stopped_by"] = "keyboard_interrupt"
    except SystemExit as exc:
        exit_code = int(exc.code) if isinstance(exc.code, int) else 1
        report["error"] = str(exc)
    except Exception as exc:  # pragma: no cover - startup guard
        exit_code = 1
        report["error"] = repr(exc)
    finally:
        for process in reversed(processes):
            process.terminate()
        report["completed_at"] = utc_now()
        report["logs"] = {
            name: {
                "path": repo_relative(log_dir / f"{name}.log"),
                "tail": tail_log(log_dir / f"{name}.log"),
            }
            for name in ("bridge", "opendocuments", "gateway")
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(output_path, report)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
