# source catalog를 읽어 승인 가능한 한국어 코퍼스 목록과 approval 리포트를 만든다.
# runtime에서 실제로 쓸 문서 범위를 고정할 때 먼저 실행하는 스크립트다.
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.ingestion.audit import (
    build_approved_manifest,
    build_corpus_gap_report,
    build_source_approval_report,
    build_translation_lane_report,
    write_approved_manifest,
)
from play_book_studio.config.settings import load_settings
from play_book_studio.ingestion.topic_playbooks import materialize_topic_playbooks


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
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    settings = load_settings(ROOT)
    allow_statuses = tuple(args.allow_statuses or ["approved_ko"])
    topic_playbook_summary = materialize_topic_playbooks(settings)

    report = build_source_approval_report(settings)
    gap_report = build_corpus_gap_report(settings)
    translation_lane_report = build_translation_lane_report(settings)
    entries = build_approved_manifest(settings, allowed_statuses=allow_statuses)

    report_path = settings.source_approval_report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    gap_report_path = settings.corpus_gap_report_path
    gap_report_path.parent.mkdir(parents=True, exist_ok=True)
    gap_report_path.write_text(json.dumps(gap_report, ensure_ascii=False, indent=2), encoding="utf-8")

    translation_lane_report_path = settings.translation_lane_report_path
    translation_lane_report_path.parent.mkdir(parents=True, exist_ok=True)
    translation_lane_report_path.write_text(
        json.dumps(translation_lane_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    output_manifest_path = settings.source_manifest_path
    output_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    write_approved_manifest(output_manifest_path, entries)

    print(f"wrote source approval report: {report_path}")
    print(f"wrote corpus gap report: {gap_report_path}")
    print(f"wrote translation lane report: {translation_lane_report_path}")
    print(f"wrote approved manifest ({len(entries)} books): {output_manifest_path}")
    print(json.dumps(topic_playbook_summary, ensure_ascii=False, indent=2))
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
