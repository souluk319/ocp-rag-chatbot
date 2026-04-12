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
from play_book_studio.ingestion.source_bundle_quality import build_source_bundle_quality_report
from play_book_studio.ingestion.topic_playbooks import materialize_topic_playbooks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build source bundle readiness report.",
    )
    parser.add_argument(
        "--output",
        default="reports/build_logs/source_bundle_quality_report.json",
        help="Path where the quality report JSON is written.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    materialize_topic_playbooks(settings)
    report = build_source_bundle_quality_report(settings)
    output_path = Path(args.output).expanduser()
    if not output_path.is_absolute():
        output_path = (ROOT / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote bundle quality report: {output_path}")
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
