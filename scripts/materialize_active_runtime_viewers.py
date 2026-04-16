from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.app.source_books import internal_gold_candidate_markdown_viewer_html


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _active_manifest_path() -> Path:
    return ROOT / "data" / "wiki_runtime_books" / "active_manifest.json"


def _translation_lane_report_path() -> Path:
    return ROOT / "reports" / "build_logs" / "foundry_runs" / "translation_lane_report" / "2026-04-15T08-31-00.json"


def _served_root() -> Path:
    return ROOT / "artifacts" / "runtime" / "served_viewers"


def _report_path() -> Path:
    return ROOT / "reports" / "build_logs" / "active_runtime_viewer_serving_report.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _runtime_eligible_slugs() -> set[str]:
    payload = _load_json(_translation_lane_report_path())
    allowed: set[str] = set()
    for book in payload.get("books", []):
        if not isinstance(book, dict):
            continue
        slug = str(book.get("book_slug") or "").strip()
        lane = book.get("translation_lane") if isinstance(book.get("translation_lane"), dict) else {}
        if slug and bool(lane.get("runtime_eligible")):
            allowed.add(slug)
    return allowed


def _active_manifest_slugs() -> list[str]:
    payload = _load_json(_active_manifest_path())
    rows = payload.get("entries") if isinstance(payload.get("entries"), list) else []
    slugs: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("book_slug") or row.get("slug") or "").strip()
        if slug:
            slugs.append(slug)
    return slugs


def main() -> int:
    served_root = _served_root()
    runtime_root = served_root / "playbooks" / "wiki-runtime" / "active"
    docs_root = served_root / "docs" / "ocp"
    runtime_root.mkdir(parents=True, exist_ok=True)
    docs_root.mkdir(parents=True, exist_ok=True)

    active_slugs = _active_manifest_slugs()
    eligible = _runtime_eligible_slugs()
    materialized: list[dict[str, str | int]] = []

    for slug in active_slugs:
        if slug not in eligible:
            continue
        viewer_path = f"/playbooks/wiki-runtime/active/{slug}/index.html"
        html = internal_gold_candidate_markdown_viewer_html(ROOT, viewer_path)
        if not html:
            continue

        runtime_target = runtime_root / slug / "index.html"
        runtime_target.parent.mkdir(parents=True, exist_ok=True)
        runtime_target.write_text(html, encoding="utf-8")

        docs_target = docs_root / slug / "index.html"
        docs_target.parent.mkdir(parents=True, exist_ok=True)
        docs_target.write_text(html, encoding="utf-8")

        materialized.append(
            {
                "book_slug": slug,
                "viewer_path": viewer_path,
                "runtime_target": str(runtime_target),
                "docs_target": str(docs_target),
                "html_bytes": len(html.encode("utf-8")),
            }
        )

    report = {
        "generated_at_utc": _utc_now(),
        "active_manifest_path": str(_active_manifest_path()),
        "translation_lane_report_path": str(_translation_lane_report_path()),
        "served_root": str(served_root),
        "materialized_count": len(materialized),
        "books": materialized,
        "status": "ok",
    }
    _report_path().write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"materialized_count": len(materialized), "served_root": str(served_root)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
