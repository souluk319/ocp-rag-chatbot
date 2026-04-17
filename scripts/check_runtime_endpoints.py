# 현재 runtime이 바라보는 LLM/embedding/Qdrant/UI 상태를 리포트로 남기는 스크립트.
# 시연 전 점검이나 endpoint 전환 확인용으로 가장 자주 쓰는 운영 점검 도구다.
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.app.runtime_report import write_runtime_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write the runtime readiness report")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--ui-base-url", default="http://127.0.0.1:8765")
    parser.add_argument("--recent-turns", type=int, default=3)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_path, report = write_runtime_report(
        ROOT,
        output_path=args.output,
        ui_base_url=args.ui_base_url,
        recent_turns=args.recent_turns,
        sample=True,
    )
    print(f"wrote runtime report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
