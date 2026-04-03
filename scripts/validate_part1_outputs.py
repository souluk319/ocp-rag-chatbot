from __future__ import annotations

import argparse
import json
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.settings import load_settings
from ocp_rag_part1.validation import build_validation_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Part 1 preprocessing outputs")
    parser.add_argument(
        "--expected-process-subset",
        choices=("all", "high-value"),
        default="high-value",
    )
    parser.add_argument("--skip-qdrant-id-check", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    report = build_validation_report(
        settings,
        expected_process_subset=args.expected_process_subset,
        include_qdrant_id_check=not args.skip_qdrant_id_check,
    )

    output_path = settings.part1_dir / "validation_report.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote validation report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
