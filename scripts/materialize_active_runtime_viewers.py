from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.app.source_books import (
    internal_active_runtime_markdown_viewer_html,
    internal_viewer_html,
)
from play_book_studio.runtime_catalog_registry import official_runtime_books


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _active_manifest_path() -> Path:
    return ROOT / "data" / "wiki_runtime_books" / "active_manifest.json"


def _translation_lane_report_dir() -> Path:
    return ROOT / "reports" / "build_logs" / "foundry_runs" / "translation_lane_report"


def _translation_lane_report_path() -> Path | None:
    report_dir = _translation_lane_report_dir()
    latest_path = report_dir / "latest.json"
    if latest_path.exists():
        return latest_path
    candidates = sorted(report_dir.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _served_root() -> Path:
    return ROOT / "artifacts" / "runtime" / "served_viewers"


def _report_path() -> Path:
    return ROOT / "reports" / "build_logs" / "active_runtime_viewer_serving_report.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _viewer_target_path(served_root: Path, viewer_path: str) -> Path:
    relative_path = urlparse(str(viewer_path or "").strip()).path.lstrip("/")
    return served_root / relative_path


def _runtime_eligible_slugs() -> set[str]:
    report_path = _translation_lane_report_path()
    if report_path is None or not report_path.exists():
        return set()
    payload = _load_json(report_path)
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
    runtime_root.mkdir(parents=True, exist_ok=True)

    registry_entries = official_runtime_books(ROOT)
    active_slugs = _active_manifest_slugs()
    eligible = _runtime_eligible_slugs()
    docs_materialized: list[dict[str, str | int]] = []
    active_materialized: list[dict[str, str | int]] = []

    for entry in registry_entries:
        docs_viewer_path = str(entry.get("docs_viewer_path") or entry.get("viewer_path") or "").strip()
        if not docs_viewer_path:
            continue
        html = internal_viewer_html(ROOT, docs_viewer_path)
        if not html:
            continue
        docs_target = _viewer_target_path(served_root, docs_viewer_path)
        docs_target.parent.mkdir(parents=True, exist_ok=True)
        docs_target.write_text(html, encoding="utf-8")
        docs_materialized.append(
            {
                "book_slug": str(entry.get("book_slug") or ""),
                "viewer_path": docs_viewer_path,
                "docs_target": str(docs_target),
                "html_bytes": len(html.encode("utf-8")),
            }
        )

    for entry in registry_entries:
        if not bool(entry.get("active_runtime")):
            continue
        slug = str(entry.get("book_slug") or "").strip()
        viewer_path = str(entry.get("active_runtime_viewer_path") or entry.get("viewer_path") or "").strip()
        if not viewer_path:
            continue
        html = internal_active_runtime_markdown_viewer_html(ROOT, viewer_path)
        if not html:
            continue

        runtime_target = runtime_root / slug / "index.html"
        runtime_target.parent.mkdir(parents=True, exist_ok=True)
        runtime_target.write_text(html, encoding="utf-8")

        active_materialized.append(
            {
                "book_slug": slug,
                "viewer_path": viewer_path,
                "runtime_target": str(runtime_target),
                "html_bytes": len(html.encode("utf-8")),
            }
        )

    report = {
        "generated_at_utc": _utc_now(),
        "active_manifest_path": str(_active_manifest_path()),
        "translation_lane_report_path": str(_translation_lane_report_path()) if _translation_lane_report_path() else "",
        "official_runtime_count": len(registry_entries),
        "active_manifest_count": len(active_slugs),
        "runtime_eligible_count": len(eligible),
        "served_root": str(served_root),
        "docs_materialized_count": len(docs_materialized),
        "active_runtime_materialized_count": len(active_materialized),
        "materialized_count": len(docs_materialized),
        "docs_books": docs_materialized,
        "active_runtime_books": active_materialized,
        "status": "ok",
    }
    _report_path().write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "docs_materialized_count": len(docs_materialized),
                "active_runtime_materialized_count": len(active_materialized),
                "served_root": str(served_root),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
