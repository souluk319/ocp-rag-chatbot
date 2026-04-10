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
from play_book_studio.ingestion.synthesis_lane import write_synthesis_lane_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Promote bronze bundle readiness into translation/manual-review working sets.",
    )
    parser.add_argument(
        "--report-path",
        default="reports/build_logs/synthesis_lane_report.json",
        help="Where to write the synthesis lane report JSON.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    report_path = Path(args.report_path).expanduser()
    if not report_path.is_absolute():
        report_path = (ROOT / report_path).resolve()
    report = write_synthesis_lane_outputs(settings, report_path=report_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
