from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.ingest.audit import build_data_quality_report
from ocp_rag.shared.settings import load_settings


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="Build the ingest data quality report")


def main() -> int:
    build_parser().parse_args()
    settings = load_settings(ROOT, create_dirs=True)
    report = build_data_quality_report(settings)
    output_path = settings.ingest_data_quality_report_path
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote data quality report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
