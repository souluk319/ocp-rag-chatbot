from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.audit import (
    build_approved_manifest,
    build_source_approval_report,
    write_approved_manifest,
)
from ocp_rag_part1.settings import load_settings


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build source approval report and approved Korean manifest.",
    )
    parser.add_argument(
        "--allow-status",
        action="append",
        dest="allow_statuses",
        default=[],
        help="Content status to keep in the output manifest. Repeatable. Defaults to approved_ko.",
    )
    parser.add_argument(
        "--report-path",
        help="Optional output path for the approval report JSON.",
    )
    parser.add_argument(
        "--output-manifest-path",
        help="Optional output path for the approved manifest JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    settings = load_settings(ROOT)
    allow_statuses = tuple(args.allow_statuses or ["approved_ko"])

    report = build_source_approval_report(settings)
    entries = build_approved_manifest(settings, allowed_statuses=allow_statuses)

    report_path = Path(args.report_path).expanduser() if args.report_path else (
        settings.part1_dir / "source_approval_report.json"
    )
    if not report_path.is_absolute():
        report_path = (ROOT / report_path).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    output_manifest_path = (
        Path(args.output_manifest_path).expanduser()
        if args.output_manifest_path
        else (settings.manifest_dir / "ocp_ko_4_20_approved_ko.json")
    )
    if not output_manifest_path.is_absolute():
        output_manifest_path = (ROOT / output_manifest_path).resolve()
    output_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    write_approved_manifest(output_manifest_path, entries)

    print(f"wrote source approval report: {report_path}")
    print(f"wrote approved manifest ({len(entries)} books): {output_manifest_path}")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
