from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _candidate_manifest_path() -> Path:
    return ROOT / "data" / "gold_candidate_books" / "wave1_manifest.json"


def _runtime_root() -> Path:
    return ROOT / "data" / "wiki_runtime_books" / "wave1"


def _runtime_manifest_path() -> Path:
    return ROOT / "data" / "wiki_runtime_books" / "wave1_manifest.json"


def _runtime_catalog_path() -> Path:
    return ROOT / "data" / "wiki_runtime_books" / "wave1_catalog.md"


def _runtime_report_path() -> Path:
    return ROOT / "reports" / "build_logs" / "wave1_wiki_runtime_promotion_report.json"


def _catalog_markdown(created_at: str, promoted: list[dict[str, str]]) -> str:
    lines = [
        "# Wave 1 Wiki Runtime Catalog",
        "",
        "## 현재 판단",
        "",
        "이 카탈로그는 wave1 gold candidate 중 실제 위키 runtime 표면으로 승격한 md 북만 모아둔 것이다.",
        "",
        f"- generated_at_utc: `{created_at}`",
        "",
        "## Entries",
        "",
    ]
    for item in promoted:
        lines.extend(
            [
                f"### `{item['slug']}`",
                "",
                f"- title: `{item['title']}`",
                f"- runtime_path: [{Path(item['runtime_path']).name}]({item['runtime_path']})",
                f"- source_candidate_path: [{Path(item['source_candidate_path']).name}]({item['source_candidate_path']})",
                f"- promotion_strategy: `{item['promotion_strategy']}`",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    candidate_manifest_path = _candidate_manifest_path()
    if not candidate_manifest_path.exists():
        raise FileNotFoundError(f"Missing candidate manifest: {candidate_manifest_path}")
    manifest = json.loads(candidate_manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("entries") if isinstance(manifest.get("entries"), list) else []
    runtime_root = _runtime_root()
    runtime_root.mkdir(parents=True, exist_ok=True)
    _runtime_report_path().parent.mkdir(parents=True, exist_ok=True)
    created_at = _utc_now()

    promoted: list[dict[str, str]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        slug = str(entry.get("slug") or "").strip()
        title = str(entry.get("title") or slug)
        source_candidate_path = Path(str(entry.get("promoted_path") or "")).resolve()
        if not slug or not source_candidate_path.exists():
            continue
        runtime_path = runtime_root / f"{slug}.md"
        runtime_path.write_text(source_candidate_path.read_text(encoding="utf-8"), encoding="utf-8")
        promoted.append(
            {
                "slug": slug,
                "title": title,
                "source_candidate_path": str(source_candidate_path),
                "runtime_path": str(runtime_path),
                "promotion_strategy": str(entry.get("promotion_strategy") or "wave1_candidate_to_runtime"),
            }
        )

    runtime_manifest = {
        "generated_at_utc": created_at,
        "runtime_count": len(promoted),
        "promotion_group": "wave1_wiki_runtime",
        "entries": promoted,
    }
    _runtime_manifest_path().write_text(json.dumps(runtime_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    _runtime_catalog_path().write_text(_catalog_markdown(created_at, promoted), encoding="utf-8")
    _runtime_report_path().write_text(
        json.dumps(
            {
                "status": "ok",
                "generated_at_utc": created_at,
                "runtime_root": str(runtime_root),
                "manifest_path": str(_runtime_manifest_path()),
                "catalog_path": str(_runtime_catalog_path()),
                "count": len(promoted),
                "entries": promoted,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "count": len(promoted),
                "runtime_root": str(runtime_root),
                "manifest_path": str(_runtime_manifest_path()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
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
