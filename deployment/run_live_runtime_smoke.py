from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.runtime_config import load_runtime_config
from deployment.stage11_activation_utils import load_index_manifest
from deployment.stage11_bundle_utils import load_json, repo_relative, utc_now, write_json


def default_opendocuments_root() -> Path:
    return REPO_ROOT.parent / "ocp-rag-v2" / "OpenDocuments"


def default_output_path() -> Path:
    return REPO_ROOT / "data" / "manifests" / "generated" / "stage12-live-runtime-report.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a live Stage 12 runtime smoke through bridge -> OpenDocuments -> gateway.")
    parser.add_argument("--index", default="current")
    parser.add_argument("--index-root", type=Path, default=REPO_ROOT / "indexes")
    parser.add_argument("--cases", type=Path, default=REPO_ROOT / "deployment" / "live_runtime_smoke_cases.json")
    parser.add_argument("--opendocuments-root", type=Path, default=default_opendocuments_root())
    parser.add_argument("--runtime-workspace", type=Path)
    parser.add_argument("--bridge-port", type=int, default=18101)
    parser.add_argument("--od-port", type=int, default=18102)
    parser.add_argument("--gateway-port", type=int, default=8000)
    parser.add_argument("--startup-timeout-seconds", type=float, default=90.0)
    parser.add_argument("--request-timeout-seconds", type=float, default=180.0)
    parser.add_argument("--output", type=Path, default=default_output_path())
    return parser.parse_args()


@dataclass
class ManagedProcess:
    name: str
    process: subprocess.Popen[str]
    log_path: Path
    _log_handle: Any

    def terminate(self) -> None:
        if self.process.poll() is None:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(self.process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            else:
                self.process.terminate()
                try:
                    self.process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    self.process.kill()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        self._log_handle.close()


def read_pointer(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def resolve_index_id(index_arg: str, index_root: Path) -> str:
    if index_arg != "current":
        return index_arg
    current_path = index_root / "current.txt"
    return read_pointer(current_path)


def runtime_workspace_for(index_id: str, configured: Path | None) -> Path:
    if configured is not None:
        return configured
    return REPO_ROOT / "workspace" / "stage12" / index_id


def write_runtime_config(workspace: Path) -> Path:
    workspace.mkdir(parents=True, exist_ok=True)
    config_path = workspace / "opendocuments.config.js"
    config_body = """module.exports = {
  workspace: 'ocp-stage12-live-runtime',
  mode: 'personal',
  model: {
    provider: 'openai',
    llm: process.env.OD_CHAT_MODEL,
    embedding: process.env.OD_EMBEDDING_MODEL,
    apiKey: process.env.OPENAI_API_KEY || 'stage12-local',
    baseUrl: process.env.OPENAI_BASE_URL,
    embeddingDimensions: Number(process.env.OD_EMBEDDING_DIMENSIONS || 384),
  },
  rag: {
    profile: 'precise',
  },
  storage: {
    db: 'sqlite',
    vectorDb: 'lancedb',
    dataDir: process.env.OPENDOCUMENTS_DATA_DIR || './.opendocuments-stage12',
  },
}
"""
    config_path.write_text(config_body, encoding="utf-8")
    return config_path


def ensure_active_workspace(index_id: str) -> Path:
    workspace = REPO_ROOT / "workspace" / "stage11" / index_id
    data_dir = workspace / ".opendocuments-stage11"
    if not data_dir.exists():
        raise SystemExit(f"Active Stage 11 workspace data is missing: {data_dir}")
    return workspace


def node20_launcher() -> list[str]:
    npx = shutil.which("npx.cmd") or shutil.which("npx")
    if npx:
        return [npx, "-p", "node@20", "node"]
    node = shutil.which("node")
    if node:
        return [node]
    raise SystemExit("Could not find a Node.js launcher for the OpenDocuments runtime.")


def start_process(*, name: str, command: list[str], cwd: Path, env: dict[str, str], log_path: Path) -> ManagedProcess:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handle = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        env=env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0,
    )
    return ManagedProcess(name=name, process=process, log_path=log_path, _log_handle=log_handle)


def detect_vector_dimensions(*, opendocuments_root: Path, data_dir: Path, log_dir: Path) -> int:
    script_path = opendocuments_root / "tmp_stage12_detect_vector_dimensions.mjs"
    script_path.write_text(
        """
import { connect } from '@lancedb/lancedb'

const vectorDir = process.argv[2]
const db = await connect(vectorDir)
const tableNames = await db.tableNames()
if (!tableNames.length) {
  throw new Error('No LanceDB tables found')
}
const table = await db.openTable(tableNames[0])
const schema = await table.schema()
const vectorField = schema.fields.find((field) => field.name === 'vector')
if (!vectorField) {
  throw new Error('Vector field not found in LanceDB schema')
}
const match = /FixedSizeList\\[(\\d+)\\]</.exec(vectorField.type.toString())
if (!match) {
  throw new Error(`Could not parse vector dimensions from schema: ${vectorField.type.toString()}`)
}
console.log(match[1])
""".strip(),
        encoding="utf-8",
    )
    try:
        result = subprocess.run(
            node20_launcher() + [str(script_path), str(data_dir / "vectors")],
            cwd=str(opendocuments_root),
            capture_output=True,
            text=True,
            check=True,
        )
    finally:
        if script_path.exists():
            script_path.unlink()

    output = result.stdout.strip().splitlines()
    if not output:
        raise SystemExit(f"Failed to detect vector dimensions: {result.stderr.strip()}")
    return int(output[-1].strip())


def tail_log(path: Path, *, lines: int = 20) -> list[str]:
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return content[-lines:]


def normalize_match_text(value: str) -> str:
    return " ".join(html.unescape(value).lower().split())


def wait_for_json(url: str, *, timeout_seconds: float, predicate) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                payload = response.json()
                if predicate(payload):
                    return payload
                last_error = f"Predicate failed for payload: {payload}"
            else:
                last_error = f"HTTP {response.status_code}"
        except Exception as exc:  # pragma: no cover - polling guard
            last_error = str(exc)
        time.sleep(1.0)
    raise SystemExit(f"Timed out waiting for {url}: {last_error}")


def wait_for_status(url: str, *, timeout_seconds: float, expected_status: int = 200) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == expected_status:
                try:
                    return response.json()
                except ValueError:
                    return {"status_code": response.status_code, "body": response.text[:500]}
            last_error = f"HTTP {response.status_code}"
        except Exception as exc:  # pragma: no cover - polling guard
            last_error = str(exc)
        time.sleep(1.0)
    raise SystemExit(f"Timed out waiting for {url}: {last_error}")


def parse_sse(response: requests.Response) -> tuple[list[dict[str, Any]], str, dict[str, Any], dict[str, int]]:
    event_type = ""
    data_lines: list[str] = []
    sources: list[dict[str, Any]] = []
    answer_parts: list[str] = []
    done_payload: dict[str, Any] = {}
    event_counts: dict[str, int] = {}

    def flush_event(current_event: str, payload_text: str) -> None:
        nonlocal sources, done_payload
        payload = json.loads(payload_text)
        event_name = current_event or "message"
        event_counts[event_name] = event_counts.get(event_name, 0) + 1
        if event_name == "sources":
            sources = payload if isinstance(payload, list) else []
        elif event_name == "chunk":
            answer_parts.append(str(payload))
        elif event_name == "done" and isinstance(payload, dict):
            done_payload = payload

    for raw_line in response.iter_lines(decode_unicode=True):
        if raw_line is None:
            continue
        line = raw_line.rstrip("\r")
        if not line:
            if data_lines:
                flush_event(event_type, "\n".join(data_lines))
            event_type = ""
            data_lines = []
            continue
        if line.startswith("event:"):
            event_type = line.split(":", 1)[1].strip()
            continue
        if line.startswith("data:"):
            data_lines.append(line.split(":", 1)[1].strip())

    if data_lines:
        flush_event(event_type, "\n".join(data_lines))

    return sources, "".join(answer_parts), done_payload, event_counts


def fetch_viewer(session: requests.Session, gateway_base_url: str, source: dict[str, Any]) -> dict[str, Any]:
    viewer_url = str(source.get("viewer_url", "")).strip()
    expected_section_title = str(source.get("section_title", "")).strip()
    resolved_url = viewer_url
    if viewer_url.startswith("/"):
        resolved_url = gateway_base_url.rstrip("/") + viewer_url

    response = session.get(resolved_url, timeout=30)
    content_type = response.headers.get("content-type", "")
    body = response.text
    expected_section_present = True
    if expected_section_title:
        expected_section_present = normalize_match_text(expected_section_title) in normalize_match_text(body)
    return {
        "viewer_url": viewer_url,
        "resolved_url": resolved_url,
        "status_code": response.status_code,
        "content_type": content_type,
        "expected_section_title": expected_section_title,
        "section_title_present": expected_section_present,
        "html_detected": "<html" in body.lower(),
        "pass": response.status_code == 200
        and "text/html" in content_type.lower()
        and "<html" in body.lower()
        and expected_section_present,
    }


def run_turn(
    *,
    session: requests.Session,
    gateway_base_url: str,
    case: dict[str, Any],
    request_timeout_seconds: float,
) -> dict[str, Any]:
    response = session.post(
        f"{gateway_base_url.rstrip('/')}/api/v1/chat/stream",
        json={"query": case["query"], "mode": case.get("mode", "operations")},
        stream=True,
        timeout=request_timeout_seconds,
    )
    response.raise_for_status()
    sources, answer_text, done_payload, event_counts = parse_sse(response)
    response.close()

    viewer_checks: list[dict[str, Any]] = []
    for source in sources[:2]:
        if str(source.get("viewer_url", "")).strip():
            viewer_checks.append(fetch_viewer(session, gateway_base_url, source))

    return {
        "id": case.get("id", ""),
        "query": case.get("query", ""),
        "mode": case.get("mode", "operations"),
        "answer_length": len(answer_text),
        "answer_preview": answer_text[:500],
        "sources": sources,
        "source_count": len(sources),
        "done_payload": done_payload,
        "event_counts": event_counts,
        "viewer_checks": viewer_checks,
        "session_cookie_present": bool(session.cookies.get("ocp_runtime_session")),
        "session_cookie_value": session.cookies.get("ocp_runtime_session", ""),
        "pass": bool(sources) and bool(done_payload) and all(check["pass"] for check in viewer_checks),
    }


def main() -> None:
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
            "OPENAI_API_KEY": env_base.get("OPENAI_API_KEY", "stage12-local"),
            "OD_CHAT_MODEL": config.chat_model,
            "OD_EMBEDDING_MODEL": config.embedding_model,
            "OD_EMBEDDING_DIMENSIONS": str(vector_dimensions),
            "OPENDOCUMENTS_DATA_DIR": str(active_data_dir),
        }
    )
    gateway_env = dict(env_base)
    gateway_env["OD_SERVER_BASE_URL"] = od_base_url
    gateway_env["OD_EMBEDDING_DIMENSIONS"] = str(vector_dimensions)

    processes: list[ManagedProcess] = []
    report: dict[str, Any] = {
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
    }

    try:
        bridge = start_process(
            name="bridge",
            command=[sys.executable, "-m", "uvicorn", "app.opendocuments_openai_bridge:app", "--host", "127.0.0.1", "--port", str(args.bridge_port)],
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
        bridge_evidence_startup = wait_for_json(
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
            + [str(args.opendocuments_root / "packages" / "cli" / "dist" / "index.js"), "start", "--port", str(args.od_port), "--no-web"],
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
            command=[sys.executable, "-m", "uvicorn", "app.ocp_runtime_gateway:app", "--host", "127.0.0.1", "--port", str(args.gateway_port)],
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

        session = requests.Session()
        cases = load_json(args.cases)
        if not isinstance(cases, list) or len(cases) < 2:
            raise SystemExit("Need at least two live runtime smoke cases.")

        first_turn = run_turn(
            session=session,
            gateway_base_url=gateway_base_url,
            case=cases[0],
            request_timeout_seconds=args.request_timeout_seconds,
        )
        second_turn = run_turn(
            session=session,
            gateway_base_url=gateway_base_url,
            case=cases[1],
            request_timeout_seconds=args.request_timeout_seconds,
        )

        first_done = first_turn.get("done_payload", {})
        second_done = second_turn.get("done_payload", {})
        same_conversation = bool(first_done) and first_done.get("conversationId") == second_done.get("conversationId")
        follow_up_rewrite = str(second_done.get("rewrittenQuery", "")).strip()
        rewrite_contains_last_document = "last_document" in follow_up_rewrite
        viewer_pass = all(check["pass"] for check in first_turn["viewer_checks"] + second_turn["viewer_checks"])
        same_cookie_value = bool(first_turn["session_cookie_value"]) and first_turn["session_cookie_value"] == second_turn["session_cookie_value"]
        bridge_evidence = wait_for_json(
            f"{bridge_base_url}/evidence",
            timeout_seconds=args.startup_timeout_seconds,
            predicate=lambda payload: isinstance(payload, dict) and payload.get("ok") is True,
        )
        telemetry = bridge_evidence.get("telemetry", {})
        bridge_checks = {
            "bridge_embedding_requests_present": int(telemetry.get("embedding_requests", 0)) > 0,
            "bridge_chat_requests_present": int(telemetry.get("chat_requests", 0)) > 0,
            "bridge_upstream_chat_success_present": int(telemetry.get("upstream_chat_success_count", 0)) > 0,
            "bridge_no_fallback_chat": int(telemetry.get("fallback_chat_count", 0)) == 0,
            "bridge_last_chat_target_ok": str(telemetry.get("last_chat_target_path", "")) == "/chat/completions",
            "bridge_embedding_model_match": str(bridge_ready.get("embedding_model", "")) == config.embedding_model,
            "bridge_embedding_dimensions_match": int(bridge_ready.get("embedding_dimensions", 0)) == vector_dimensions,
        }

        report.update(
            {
                "bridge_health": bridge_health,
                "bridge_ready": bridge_ready,
                "bridge_evidence_startup": bridge_evidence_startup,
                "bridge_evidence": bridge_evidence,
                "bridge_models": bridge_models,
                "opendocuments_health": od_health,
                "gateway_health": gateway_health,
                "cases_path": repo_relative(args.cases),
                "turns": [first_turn, second_turn],
                "checks": {
                    "first_turn_pass": first_turn["pass"],
                    "second_turn_pass": second_turn["pass"],
                    "same_conversation_id": same_conversation,
                    "same_session_cookie_value": same_cookie_value,
                    "follow_up_rewrite_contains_last_document": rewrite_contains_last_document,
                    "viewer_click_through_pass": viewer_pass,
                    "gateway_cookie_present_after_turn1": first_turn["session_cookie_present"],
                    "gateway_cookie_present_after_turn2": second_turn["session_cookie_present"],
                    **bridge_checks,
                },
            }
        )
        report["overall_pass"] = all(report["checks"].values())
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

    if not report.get("overall_pass", False):
        raise SystemExit(f"Stage 12 live runtime smoke failed. See {output_path}")

    print(f"[ok] live runtime smoke passed -> {output_path}")


if __name__ == "__main__":
    main()
