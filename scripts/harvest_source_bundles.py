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


def _default_queue_report() -> Path:
    candidates = sorted(ROOT.glob("reports/build_logs/gold_expansion_queue_*.json"))
    if not candidates:
        raise FileNotFoundError("No gold expansion queue report found under reports/build_logs/")
    return candidates[-1]


def _default_output_path(queue_report: Path) -> Path:
    suffix = queue_report.stem.replace("gold_expansion_queue_", "")
    return ROOT / "reports" / "build_logs" / f"source_bundle_batch_{suffix}.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Harvest bronze source bundles for the current gold expansion queue.",
    )
    parser.add_argument(
        "--queue-report",
        type=Path,
        default=None,
        help="Queue report JSON path. Defaults to the latest gold_expansion_queue_*.json.",
    )
    parser.add_argument(
        "--slug",
        action="append",
        default=[],
        help="Optional slug filter. Repeat to harvest only selected books.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Batch summary output path. Defaults to reports/build_logs/source_bundle_batch_<date>.json.",
    )
    parser.add_argument(
        "--max-repo-files",
        type=int,
        default=20,
        help="Max openshift-docs repo files to capture per book.",
    )
    parser.add_argument(
        "--max-issue-pr-candidates",
        type=int,
        default=10,
        help="Max issue/PR candidates to keep per bucket per book.",
    )
    return parser


def _load_queue(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Queue report must be a JSON list: {path}")
    return payload


def main() -> int:
    args = build_parser().parse_args()
    queue_report = args.queue_report or _default_queue_report()
    output_path = args.output or _default_output_path(queue_report)
    settings = load_settings(ROOT)
    queue = _load_queue(queue_report)

    slug_filter = {slug.strip() for slug in args.slug if slug.strip()}
    selected = [
        item for item in queue if not slug_filter or str(item.get("book_slug", "")).strip() in slug_filter
    ]

    results: list[dict[str, object]] = []
    for item in selected:
        slug = str(item.get("book_slug", "")).strip()
        if not slug:
            continue
        manifest = harvest_source_bundle(
            settings,
            slug,
            max_repo_files=args.max_repo_files,
            max_issue_pr_candidates=args.max_issue_pr_candidates,
        )
        results.append(
            {
                "book_slug": slug,
                "classification": item.get("classification"),
                "priority": item.get("priority"),
                "repo_artifact_count": len(manifest.get("repo_artifacts", [])),
                "bundle_root": manifest.get("bundle_root"),
                "issue_pr_candidates_path": manifest.get("issue_pr_candidates_path"),
            }
        )
        print(f"[bundle] {slug} repo_artifacts={len(manifest.get('repo_artifacts', []))}")

    payload = {
        "queue_report": str(queue_report),
        "selected_count": len(selected),
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
