# OCP 문서 source catalog/approved manifest를 갱신하는 스크립트.
# 문서 업데이트 추적이나 승인 manifest 재생성이 필요할 때 쓴다.
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.ingestion.pipeline import ensure_manifest
from play_book_studio.config.settings import load_settings


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build multiversion OCP source catalog from docs.redhat.com html-single indexes.",
    )
    parser.add_argument(
        "--versions",
        help="Comma-separated OCP versions to scan. Defaults to settings/source catalog scope.",
    )
    parser.add_argument(
        "--languages",
        help="Comma-separated docs languages to scan. Defaults to settings/source catalog scope.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    settings = load_settings(ROOT)
    if args.versions:
        settings.source_catalog_versions_override = args.versions
    if args.languages:
        settings.source_catalog_languages_override = args.languages
    entries = ensure_manifest(settings, refresh=True)
    print(f"wrote source catalog: {settings.source_catalog_path}")
    print(f"wrote update report: {settings.source_manifest_update_report_path}")
    print(f"entries: {len(entries)}")
    print(f"high-value entries: {sum(1 for entry in entries if entry.high_value)}")
    print(f"versions: {', '.join(sorted({entry.ocp_version for entry in entries}))}")
    print(f"languages: {', '.join(sorted({entry.docs_language for entry in entries}))}")
    print(f"source states: {', '.join(sorted({entry.source_state for entry in entries}))}")
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
