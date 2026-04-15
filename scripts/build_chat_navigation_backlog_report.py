from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DEFAULT_JSON_REPORT_PATH = ROOT / "reports" / "build_logs" / "chat_navigation_backlog_report.json"
DEFAULT_MD_REPORT_PATH = ROOT / "reports" / "build_logs" / "chat_navigation_backlog_report.md"
DEFAULT_BACKLOG_ASSET_PATH = ROOT / "data" / "wiki_relations" / "navigation_backlog.json"
DEFAULT_BACKLOG_MD_PATH = ROOT / "data" / "wiki_relations" / "navigation_backlog.md"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate suggested queries and related links from chat audit logs into a navigation backlog report.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Top N rows to keep for each backlog bucket.",
    )
    return parser


def _load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and parsed.get("record_kind") == "chat_turn_audit":
            rows.append(parsed)
    return rows


def _top_counter(counter: Counter[str], limit: int) -> list[dict[str, Any]]:
    return [
        {"value": value, "count": count}
        for value, count in counter.most_common(limit)
    ]


def _top_link_counter(counter: Counter[tuple[str, str, str]], limit: int) -> list[dict[str, Any]]:
    return [
        {"title": title, "href": href, "kind": kind, "count": count}
        for (title, href, kind), count in counter.most_common(limit)
    ]


def _build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Chat Navigation Backlog Report",
        "",
        "## 현재 판단",
        "",
        "추천 질문과 관련 탐색 링크는 다음 gold corpus / entity hub / relation graph 우선순위를 정하는 backlog 신호로 직접 사용한다.",
        "",
        f"- chat_log_path: `{report['chat_log_path']}`",
        f"- turn_count: `{report['turn_count']}`",
        f"- turns_with_suggested_queries: `{report['turns_with_suggested_queries']}`",
        f"- turns_with_related_links: `{report['turns_with_related_links']}`",
        "",
        "## Top Suggested Queries",
        "",
    ]
    for item in report["top_suggested_queries"]:
        lines.append(f"- `{item['count']}` · {item['value']}")
    lines.extend(["", "## Top Related Links", ""])
    for item in report["top_related_links"]:
        lines.append(
            f"- `{item['count']}` · [{item['title']}]({item['href']}) · kind=`{item['kind']}`"
        )
    lines.extend(["", "## Top Entity Hubs", ""])
    for item in report["top_entity_hubs"]:
        lines.append(
            f"- `{item['count']}` · [{item['title']}]({item['href']})"
        )
    lines.extend(["", "## Top Related Books", ""])
    for item in report["top_related_books"]:
        lines.append(
            f"- `{item['count']}` · [{item['title']}]({item['href']})"
        )
    lines.extend(["", "## Immediate Backlog Signals", ""])
    for item in report["immediate_backlog_signals"]:
        lines.append(
            f"- `{item['signal_type']}` · `{item['count']}` · {item['label']}"
        )
    return "\n".join(lines).strip() + "\n"


def _materialize_backlog_asset(report: dict[str, Any]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []

    for item in report.get("top_entity_hubs", []):
        if not isinstance(item, dict):
            continue
        entries.append(
            {
                "signal_id": f"entity:{str(item.get('title') or '').strip().lower().replace(' ', '-')}",
                "label": str(item.get("title") or "").strip(),
                "signal_type": "entity_hub",
                "count": int(item.get("count") or 0),
                "href": str(item.get("href") or "").strip(),
                "kind": "entity",
            }
        )

    for item in report.get("top_related_books", []):
        if not isinstance(item, dict):
            continue
        entries.append(
            {
                "signal_id": f"book:{str(item.get('title') or '').strip().lower().replace(' ', '-')}",
                "label": str(item.get("title") or "").strip(),
                "signal_type": "related_book",
                "count": int(item.get("count") or 0),
                "href": str(item.get("href") or "").strip(),
                "kind": "book",
            }
        )

    for item in report.get("top_suggested_queries", []):
        if not isinstance(item, dict):
            continue
        value = str(item.get("value") or "").strip()
        if not value:
            continue
        entries.append(
            {
                "signal_id": f"query:{value.lower().replace(' ', '-')}",
                "label": value,
                "signal_type": "suggested_query",
                "count": int(item.get("count") or 0),
                "href": "",
                "kind": "query",
            }
        )

    deduped: dict[str, dict[str, Any]] = {}
    for entry in entries:
        signal_id = str(entry.get("signal_id") or "").strip()
        if not signal_id:
            continue
        existing = deduped.get(signal_id)
        if existing is None or int(entry.get("count") or 0) > int(existing.get("count") or 0):
            deduped[signal_id] = entry

    materialized_entries = sorted(
        deduped.values(),
        key=lambda item: (int(item.get("count") or 0), str(item.get("signal_type") or ""), str(item.get("label") or "")),
        reverse=True,
    )
    return {
        "status": "ok",
        "generated_at": report.get("generated_at") or "",
        "source_report_path": str(DEFAULT_JSON_REPORT_PATH),
        "entry_count": len(materialized_entries),
        "entries": materialized_entries,
    }


def _build_backlog_markdown(asset: dict[str, Any]) -> str:
    lines = [
        "# Navigation Backlog",
        "",
        "추천 질문과 관련 탐색 링크에서 나온 다음 위키 확장 후보입니다.",
        "",
    ]
    for entry in asset.get("entries", []):
        if not isinstance(entry, dict):
            continue
        label = str(entry.get("label") or "").strip()
        signal_type = str(entry.get("signal_type") or "").strip()
        count = int(entry.get("count") or 0)
        href = str(entry.get("href") or "").strip()
        if href:
            lines.append(f"- `{count}` · `{signal_type}` · [{label}]({href})")
        else:
            lines.append(f"- `{count}` · `{signal_type}` · {label}")
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    rows = _load_rows(settings.chat_log_path)

    suggested_counter: Counter[str] = Counter()
    related_counter: Counter[tuple[str, str, str]] = Counter()
    entity_counter: Counter[tuple[str, str]] = Counter()
    book_counter: Counter[tuple[str, str]] = Counter()
    turns_with_suggested = 0
    turns_with_related = 0

    for row in rows:
        suggested_queries = row.get("suggested_queries") or []
        related_links = row.get("related_links") or []
        if suggested_queries:
            turns_with_suggested += 1
        if related_links:
            turns_with_related += 1
        for query in suggested_queries:
            normalized_query = str(query).strip()
            if normalized_query:
                suggested_counter[normalized_query] += 1
        for link in related_links:
            if not isinstance(link, dict):
                continue
            title = str(link.get("title") or link.get("label") or "").strip()
            href = str(link.get("href") or "").strip()
            kind = str(link.get("kind") or "").strip() or "unknown"
            if not title or not href:
                continue
            related_counter[(title, href, kind)] += 1
            if "/wiki/entities/" in href:
                entity_counter[(title, href)] += 1
            if "/playbooks/" in href or "/docs/" in href:
                book_counter[(title, href)] += 1

    immediate_backlog_signals: list[dict[str, Any]] = []
    for item in _top_counter(suggested_counter, args.limit):
        immediate_backlog_signals.append(
            {
                "signal_type": "suggested_query",
                "label": item["value"],
                "count": item["count"],
            }
        )
    for title, href in entity_counter:
        immediate_backlog_signals.append(
            {
                "signal_type": "entity_hub",
                "label": f"{title} -> {href}",
                "count": entity_counter[(title, href)],
            }
        )
    immediate_backlog_signals.sort(key=lambda item: int(item["count"]), reverse=True)
    immediate_backlog_signals = immediate_backlog_signals[: args.limit]

    report = {
        "status": "ok",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "chat_log_path": str(settings.chat_log_path),
        "turn_count": len(rows),
        "turns_with_suggested_queries": turns_with_suggested,
        "turns_with_related_links": turns_with_related,
        "top_suggested_queries": _top_counter(suggested_counter, args.limit),
        "top_related_links": _top_link_counter(related_counter, args.limit),
        "top_entity_hubs": [
            {"title": title, "href": href, "count": count}
            for (title, href), count in entity_counter.most_common(args.limit)
        ],
        "top_related_books": [
            {"title": title, "href": href, "count": count}
            for (title, href), count in book_counter.most_common(args.limit)
        ],
        "immediate_backlog_signals": immediate_backlog_signals,
        "json_report_path": str(DEFAULT_JSON_REPORT_PATH),
        "md_report_path": str(DEFAULT_MD_REPORT_PATH),
    }
    backlog_asset = _materialize_backlog_asset(report)

    DEFAULT_JSON_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON_REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    DEFAULT_MD_REPORT_PATH.write_text(
        _build_markdown(report),
        encoding="utf-8",
    )
    DEFAULT_BACKLOG_ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_BACKLOG_ASSET_PATH.write_text(
        json.dumps(backlog_asset, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    DEFAULT_BACKLOG_MD_PATH.write_text(
        _build_backlog_markdown(backlog_asset),
        encoding="utf-8",
    )
    report["backlog_asset_path"] = str(DEFAULT_BACKLOG_ASSET_PATH)
    report["backlog_markdown_path"] = str(DEFAULT_BACKLOG_MD_PATH)
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
