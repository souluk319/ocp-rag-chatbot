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
from play_book_studio.ingestion.source_bundle import harvest_source_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Harvest bronze source bundle for a weak book.",
    )
    parser.add_argument("--slug", required=True, help="Book slug to harvest.")
    parser.add_argument(
        "--max-repo-files",
        type=int,
        default=20,
        help="Max openshift-docs repo files to capture.",
    )
    parser.add_argument(
        "--max-issue-pr-candidates",
        type=int,
        default=10,
        help="Max issue/PR candidates to keep per bucket.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    manifest = harvest_source_bundle(
        settings,
        args.slug,
        max_repo_files=args.max_repo_files,
        max_issue_pr_candidates=args.max_issue_pr_candidates,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
