from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from play_book_studio.app.wiki_relations import load_wiki_relation_assets
from play_book_studio.app.wiki_user_overlay import (
    list_wiki_user_overlays,
    remove_wiki_user_overlay,
    save_wiki_user_overlay,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT_DIR / "reports" / "build_logs" / "wiki_user_overlay_storage_report.json"
USER_ID = "smoke-user"
SERVER_BASE = "http://127.0.0.1:8765"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _first_figure_target(root_dir: Path) -> tuple[str, str]:
    del root_dir
    assets = load_wiki_relation_assets().get("figure_assets")
    if not isinstance(assets, dict):
        raise RuntimeError("figure_assets relation이 없습니다.")
    entries = assets.get("entries")
    if not isinstance(entries, dict):
        raise RuntimeError("figure_assets.entries relation이 없습니다.")
    for slug, records in entries.items():
        if not isinstance(records, list):
            continue
        for record in records:
            if not isinstance(record, dict):
                continue
            asset_name = (
                str(record.get("asset_name") or "").strip()
                or Path(urllib.parse.urlparse(str(record.get("asset_url") or "")).path).name.strip()
                or Path(urllib.parse.urlparse(str(record.get("viewer_path") or "")).path).parent.name.strip()
            )
            if asset_name:
                return str(slug).strip(), asset_name
    raise RuntimeError("사용 가능한 figure asset을 찾지 못했습니다.")


def _first_section_target(root_dir: Path) -> tuple[str, str]:
    del root_dir
    assets = load_wiki_relation_assets().get("section_relation_index")
    if not isinstance(assets, dict):
        raise RuntimeError("section_relation_index relation이 없습니다.")
    by_book = assets.get("by_book")
    if not isinstance(by_book, dict):
        raise RuntimeError("section_relation_index.by_book relation이 없습니다.")
    for slug, records in by_book.items():
        if not isinstance(records, list):
            continue
        for record in records:
            if not isinstance(record, dict):
                continue
            href = str(record.get("href") or "").strip()
            if "#" not in href:
                continue
            anchor = href.split("#", 1)[1].strip()
            if anchor:
                return str(slug).strip(), anchor
    raise RuntimeError("사용 가능한 section anchor를 찾지 못했습니다.")


def _cleanup_user(root_dir: Path, user_id: str) -> dict[str, Any]:
    before = list_wiki_user_overlays(root_dir, user_id=user_id)
    removed = 0
    for item in before.get("items", []):
        overlay_id = str(item.get("overlay_id") or "").strip()
        if not overlay_id:
            continue
        result = remove_wiki_user_overlay(
            root_dir,
            {"user_id": user_id, "overlay_id": overlay_id},
        )
        removed += int(result.get("removed") or 0)
    after = list_wiki_user_overlays(root_dir, user_id=user_id)
    return {
        "before_count": int(before.get("count") or 0),
        "removed": removed,
        "after_count": int(after.get("count") or 0),
    }


def _post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    root_dir = ROOT_DIR
    figure_book_slug, figure_asset_name = _first_figure_target(root_dir)
    section_book_slug, section_anchor = _first_section_target(root_dir)

    report: dict[str, Any] = {
        "status": "error",
        "user_id": USER_ID,
        "cleanup_before": {},
        "saved_records": [],
        "function_smoke": {},
        "http_smoke": {"attempted": False, "ok": False},
        "cleanup_after": {},
    }

    _ensure_parent(REPORT_PATH)
    report["cleanup_before"] = _cleanup_user(root_dir, USER_ID)

    favorite = save_wiki_user_overlay(
        root_dir,
        {
            "user_id": USER_ID,
            "kind": "favorite",
            "target_kind": "book",
            "book_slug": "backup_and_restore",
            "title": "Backup and Restore",
            "summary": "smoke favorite",
        },
    )
    report["saved_records"].append(favorite["record"])

    check = save_wiki_user_overlay(
        root_dir,
        {
            "user_id": USER_ID,
            "kind": "check",
            "target_kind": "section",
            "book_slug": section_book_slug,
            "anchor": section_anchor,
            "status": "checked",
        },
    )
    report["saved_records"].append(check["record"])

    note = save_wiki_user_overlay(
        root_dir,
        {
            "user_id": USER_ID,
            "kind": "note",
            "target_kind": "entity_hub",
            "entity_slug": "etcd",
            "body": "overlay smoke note",
            "pinned": True,
        },
    )
    report["saved_records"].append(note["record"])

    recent_position = save_wiki_user_overlay(
        root_dir,
        {
            "user_id": USER_ID,
            "kind": "recent_position",
            "target_kind": "figure",
            "book_slug": figure_book_slug,
            "asset_name": figure_asset_name,
        },
    )
    report["saved_records"].append(recent_position["record"])

    listed = list_wiki_user_overlays(root_dir, user_id=USER_ID)
    items = listed.get("items") or []
    report["function_smoke"] = {
        "count": int(listed.get("count") or 0),
        "kinds": [str(item.get("kind") or "") for item in items],
        "target_kinds": [str(item.get("target_kind") or "") for item in items],
        "all_resolved_have_viewer_path": all(
            str((item.get("resolved_target") or {}).get("viewer_path") or "").strip()
            for item in items
        ),
        "book_ref_present": any(str(item.get("target_ref") or "").startswith("book:") for item in items),
        "entity_ref_present": any(str(item.get("target_ref") or "").startswith("entity:") for item in items),
        "section_ref_present": any(str(item.get("target_ref") or "").startswith("section:") for item in items),
        "figure_ref_present": any(str(item.get("target_ref") or "").startswith("figure:") for item in items),
    }

    try:
        report["http_smoke"]["attempted"] = True
        base = SERVER_BASE.rstrip("/")
        list_url = f"{base}/api/wiki-overlays?{urllib.parse.urlencode({'user_id': USER_ID})}"
        listed_http = _get_json(list_url)
        http_save = _post_json(
            f"{base}/api/wiki-overlays",
            {
                "user_id": USER_ID,
                "kind": "favorite",
                "target_kind": "book",
                "book_slug": "installing_on_any_platform",
            },
        )
        http_remove = _post_json(
            f"{base}/api/wiki-overlays/remove",
            {
                "user_id": USER_ID,
                "kind": "favorite",
                "target_ref": "book:installing_on_any_platform",
            },
        )
        report["http_smoke"] = {
            "attempted": True,
            "ok": True,
            "list_count": int(listed_http.get("count") or 0),
            "save_saved": bool(http_save.get("saved")),
            "remove_removed": int(http_remove.get("removed") or 0),
        }
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        report["http_smoke"] = {
            "attempted": True,
            "ok": False,
            "error": str(exc),
        }

    report["cleanup_after"] = _cleanup_user(root_dir, USER_ID)
    report["status"] = "ok"
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
