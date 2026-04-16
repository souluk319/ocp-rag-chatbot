from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELATION_DIR = ROOT / "data" / "wiki_relations"
REPORT_PATH = ROOT / "reports" / "build_logs" / "relation_asset_cleanup_report.json"
REPORT_MD_PATH = ROOT / "reports" / "build_logs" / "relation_asset_cleanup_report.md"

GARBAGE_BOOK_SLUGS = {
    "release_notes",
    "support",
    "validation_and_troubleshooting",
    "cli_tools",
    "disconnected_environments",
}
GARBAGE_ENTITY_SLUGS = {
    "lifecycle-and-support",
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _book_slug_from_href(href: str) -> str:
    parts = [part for part in str(href or "").split("/") if part]
    if "index.html" not in parts or len(parts) < 2:
        return ""
    return parts[-2]


def _entity_slug_from_href(href: str) -> str:
    parts = [part for part in str(href or "").split("/") if part]
    if len(parts) < 3 or parts[0] != "wiki" or parts[1] != "entities":
        return ""
    return parts[2]


def _count_book_targets(payload: dict[str, Any]) -> int:
    total = 0
    for relation in payload.values():
        if not isinstance(relation, dict):
            continue
        for key in ("related_docs", "next_reading_path", "siblings"):
            for item in relation.get(key, []):
                if not isinstance(item, dict):
                    continue
                if _book_slug_from_href(str(item.get("href") or "")) in GARBAGE_BOOK_SLUGS:
                    total += 1
    return total


def _count_entity_targets(payload: dict[str, Any]) -> int:
    total = 0
    for relation in payload.values():
        if not isinstance(relation, dict):
            continue
        for item in relation.get("entities", []):
            if not isinstance(item, dict):
                continue
            if _entity_slug_from_href(str(item.get("href") or "")) in GARBAGE_ENTITY_SLUGS:
                total += 1
    return total


def _count_alias_targets(payload: dict[str, Any]) -> int:
    total = 0
    for items in payload.values():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            href = str(item.get("href") or "")
            if _book_slug_from_href(href) in GARBAGE_BOOK_SLUGS or _entity_slug_from_href(href) in GARBAGE_ENTITY_SLUGS:
                total += 1
    return total


def main() -> int:
    candidate_relations = _load_json(RELATION_DIR / "candidate_relations.json")
    chat_aliases = _load_json(RELATION_DIR / "chat_navigation_aliases.json")
    section_relation_index = _load_json(RELATION_DIR / "section_relation_index.json")
    report = {
        "status": "ok",
        "generated_from": str(RELATION_DIR),
        "candidate_relation_count": len(candidate_relations),
        "chat_alias_count": len(chat_aliases),
        "section_relation_book_count": int(section_relation_index.get("book_count") or 0),
        "related_navigation_top_n_garbage_slug_count": _count_book_targets(candidate_relations),
        "related_navigation_garbage_entity_count": _count_entity_targets(candidate_relations),
        "chat_alias_garbage_target_count": _count_alias_targets(chat_aliases),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD_PATH.write_text(
        "\n".join(
            [
                "# Relation Asset Cleanup Report",
                "",
                f"- candidate_relation_count: `{report['candidate_relation_count']}`",
                f"- chat_alias_count: `{report['chat_alias_count']}`",
                f"- section_relation_book_count: `{report['section_relation_book_count']}`",
                f"- related_navigation_top_n_garbage_slug_count: `{report['related_navigation_top_n_garbage_slug_count']}`",
                f"- related_navigation_garbage_entity_count: `{report['related_navigation_garbage_entity_count']}`",
                f"- chat_alias_garbage_target_count: `{report['chat_alias_garbage_target_count']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
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
