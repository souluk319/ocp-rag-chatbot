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


def _source_manifest_path(group: str) -> Path:
    return ROOT / "data" / "wiki_runtime_books" / f"{group}_manifest.json"


def _active_manifest_path() -> Path:
    return ROOT / "data" / "wiki_runtime_books" / "active_manifest.json"


def _active_catalog_path() -> Path:
    return ROOT / "data" / "wiki_runtime_books" / "active_catalog.md"


def _report_path() -> Path:
    return ROOT / "reports" / "build_logs" / "wiki_runtime_activation_report.json"


def _catalog_markdown(created_at: str, group: str, entries: list[dict[str, str]]) -> str:
    lines = [
        "# Active Wiki Runtime Catalog",
        "",
        "## 현재 판단",
        "",
        "이 카탈로그는 현재 서비스 viewer 와 chatbot runtime 이 직접 읽는 active wiki runtime md만 모아둔 것이다.",
        "",
        f"- generated_at_utc: `{created_at}`",
        f"- active_group: `{group}`",
        "",
        "## Entries",
        "",
    ]
    for item in entries:
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


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    group = str(args[0] if args else "full_rebuild").strip()
    if not group:
        raise ValueError("Runtime group is required.")

    source_manifest_path = _source_manifest_path(group)
    if not source_manifest_path.exists():
        raise FileNotFoundError(f"Missing runtime group manifest: {source_manifest_path}")

    payload = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    entries = payload.get("entries") if isinstance(payload.get("entries"), list) else []
    created_at = _utc_now()

    active_manifest = {
        "generated_at_utc": created_at,
        "active_group": group,
        "runtime_count": len(entries),
        "source_manifest_path": str(source_manifest_path.resolve()),
        "entries": entries,
    }
    _active_manifest_path().write_text(
        json.dumps(active_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _active_catalog_path().write_text(
        _catalog_markdown(created_at, group, [entry for entry in entries if isinstance(entry, dict)]),
        encoding="utf-8",
    )
    _report_path().parent.mkdir(parents=True, exist_ok=True)
    _report_path().write_text(
        json.dumps(
            {
                "status": "ok",
                "generated_at_utc": created_at,
                "active_group": group,
                "source_manifest_path": str(source_manifest_path.resolve()),
                "active_manifest_path": str(_active_manifest_path().resolve()),
                "active_catalog_path": str(_active_catalog_path().resolve()),
                "runtime_count": len(entries),
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
                "active_group": group,
                "runtime_count": len(entries),
                "active_manifest_path": str(_active_manifest_path().resolve()),
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
            lambda: main(),
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
