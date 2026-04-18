from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

REPORT_PATH = ROOT / "reports" / "build_logs" / "official_rebuild_quarantine_report.json"
QUARANTINE_ROOT = ROOT / "data" / "quarantine" / "official_source_parser_binding_and_clean_rebuild_20260418"

MOVE_TARGETS = (
    "data/gold_candidate_books/full_rebuild",
    "data/gold_candidate_books/full_rebuild_manifest.json",
    "data/gold_candidate_books/full_rebuild_catalog.md",
    "data/wiki_runtime_books/full_rebuild",
    "data/wiki_runtime_books/full_rebuild_manifest.json",
    "data/wiki_runtime_books/full_rebuild_catalog.md",
    "data/wiki_assets/full_rebuild",
    "data/wiki_relations/figure_assets.json",
    "data/wiki_relations/diagram_assets.json",
    "reports/build_logs/ocp420_full_rebuild_materialization_report.json",
    "reports/build_logs/ocp420_full_rebuild_report.json",
    "reports/build_logs/ocp420_one_click_runtime_report.json",
)

LOGICAL_QUARANTINE_CANDIDATES = (
    "data/gold_manualbook_ko/playbooks",
    "data/bronze/raw_html",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _timestamp_token(utc_now: str) -> str:
    return utc_now.replace(":", "").replace("-", "").replace("+00:00", "Z")


def main() -> int:
    generated_at = _utc_now()
    quarantine_root = QUARANTINE_ROOT / _timestamp_token(generated_at)
    moved: list[dict[str, str]] = []
    skipped: list[str] = []

    for relative_path in MOVE_TARGETS:
        source_path = (ROOT / relative_path).resolve()
        try:
            source_path.relative_to(ROOT.resolve())
        except ValueError:
            skipped.append(relative_path)
            continue
        if not source_path.exists():
            skipped.append(relative_path)
            continue
        target_path = (quarantine_root / relative_path).resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(target_path))
        moved.append(
            {
                "source_path": str(source_path),
                "quarantine_path": str(target_path),
            }
        )

    payload = {
        "status": "ok",
        "generated_at_utc": generated_at,
        "quarantine_root": str(quarantine_root.resolve()),
        "moved_count": len(moved),
        "moved": moved,
        "skipped_missing_or_outside_root": skipped,
        "logical_quarantine_candidates": list(LOGICAL_QUARANTINE_CANDIDATES),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
