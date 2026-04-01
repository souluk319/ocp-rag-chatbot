from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import uvicorn


def load_gateway_app():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "app" / "ocp_runtime_gateway.py"
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    spec = importlib.util.spec_from_file_location("ocp_runtime_gateway_exact", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load gateway module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the exact local gateway module from this repo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = load_gateway_app()
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
