from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.app import source_books


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    out_dir = ROOT / "data" / "wiki_relations"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = ROOT / "reports" / "build_logs" / "wave1_wiki_relations_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    payloads = {
        "entity_hubs.json": source_books.ENTITY_HUBS,
        "chat_navigation_aliases.json": source_books.CHAT_NAVIGATION_ALIASES,
        "candidate_relations.json": source_books.WIKI_CANDIDATE_RELATIONS,
    }
    written: dict[str, str] = {}
    for filename, payload in payloads.items():
        target = out_dir / filename
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        written[filename] = str(target)

    report = {
        "status": "ok",
        "generated_at_utc": _utc_now(),
        "output_dir": str(out_dir),
        "written_files": written,
        "entity_hub_count": len(source_books.ENTITY_HUBS),
        "chat_navigation_alias_count": len(source_books.CHAT_NAVIGATION_ALIASES),
        "candidate_relation_count": len(source_books.WIKI_CANDIDATE_RELATIONS),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
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
