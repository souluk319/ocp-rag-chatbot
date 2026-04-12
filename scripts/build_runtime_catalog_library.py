from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DEFAULT_REPORT_PATH = ROOT / "reports" / "build_logs" / "runtime_catalog_library_report.json"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.ingestion.runtime_catalog_library import materialize_runtime_catalog_library


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize the full runtime source catalog into official playbook library assets.",
    )
    parser.add_argument(
        "--force-collect",
        action="store_true",
        help="Re-fetch runtime catalog HTML even if cached.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    report = materialize_runtime_catalog_library(
        settings,
        force_collect=args.force_collect,
    )
    DEFAULT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
