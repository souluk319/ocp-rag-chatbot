from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
REPORT_PATH = ROOT / "reports" / "build_logs" / "ocp420_full_rebuild_report.json"

STEPS = [
    {
        "step_id": "build_manifest",
        "script": ROOT / "scripts" / "build_ocp420_full_rebuild_manifest.py",
        "write_scope": "manifests/ocp420_source_first_full_rebuild_manifest.json + reports/build_logs/ocp420_full_rebuild_manifest_report.json",
        "verify_cmd": "full rebuild manifest exists with source_first/fallback counts",
    },
    {
        "step_id": "build_navigation_backlog",
        "script": ROOT / "scripts" / "build_chat_navigation_backlog_report.py",
        "write_scope": "reports/build_logs/chat_navigation_backlog_report.* + data/wiki_relations/navigation_backlog.*",
        "verify_cmd": "navigation backlog exists",
        "args": ["--limit", "12"],
    },
    {
        "step_id": "promote_priority_targets",
        "script": ROOT / "scripts" / "promote_navigation_backlog_targets.py",
        "write_scope": "data/wiki_relations/priority_targets.* + reports/build_logs/priority_targets_report.json",
        "verify_cmd": "priority targets exist",
    },
]


def main() -> int:
    results: list[dict[str, Any]] = []
    for step in STEPS:
        args = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ROOT / "scripts" / "codex_python.ps1"),
            str(step["script"]),
            str(step["write_scope"]),
            str(step["verify_cmd"]),
        ]
        args.extend(step.get("args") or [])
        completed = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
        results.append(
            {
                "step_id": step["step_id"],
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
        if completed.returncode != 0:
            payload = {"status": "failed", "step_results": results}
            REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
            REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return completed.returncode

    payload = {"status": "ok", "step_results": results}
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
