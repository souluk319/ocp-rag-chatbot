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
from play_book_studio.ingestion.source_discovery import (
    build_source_dossier,
    default_dossier_slugs,
    write_source_dossier,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build source discovery dossiers for weak books.",
    )
    parser.add_argument(
        "--slug",
        action="append",
        dest="slugs",
        default=[],
        help="Specific book slug to inspect. Repeatable. Defaults to current gap queue.",
    )
    parser.add_argument(
        "--output-dir",
        default="reports/build_logs/source_dossiers",
        help="Directory where dossier JSON files are written.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    slugs = sorted({slug.strip() for slug in args.slugs if slug.strip()}) or default_dossier_slugs(settings)
    output_dir = Path(args.output_dir).expanduser()
    if not output_dir.is_absolute():
        output_dir = (ROOT / output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    summary: list[dict[str, object]] = []
    for slug in slugs:
        dossier = build_source_dossier(settings, slug)
        write_source_dossier(output_dir / f"{slug}.json", dossier)
        summary.append(
            {
                "slug": slug,
                "content_status": dossier["current_status"]["content_status"],
                "gap_lane": dossier["current_status"]["gap_lane"],
                "official_ko_fallback_banner": dossier["official_docs"]["ko"]["contains_language_fallback_banner"],
                "repo_candidate_count": len(dossier["openshift_docs_repo_candidates"]),
                "issue_pr_candidate_count": len(dossier["issue_pr_candidates_exact_slug"]),
            }
        )

    summary_path = output_dir / "_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote source dossiers ({len(slugs)} books): {output_dir}")
    print(f"summary={summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
