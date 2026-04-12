# ingestion 산출물 파일의 존재와 기본 스키마를 검사하는 검증 스크립트.
# collect/normalize/chunk 결과가 중간에서 깨지지 않았는지 확인할 때 쓴다.
from __future__ import annotations

import argparse
import json
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.config.validation import build_validation_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate ingestion outputs")
    parser.add_argument(
        "--expected-process-subset",
        choices=("all", "high-value"),
        default="high-value",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    report = build_validation_report(
        settings,
        expected_process_subset=args.expected_process_subset,
        include_qdrant_id_check=True,
    )

    output_path = settings.corpus_dir / "validation_report.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote validation report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
