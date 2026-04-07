from __future__ import annotations

from pathlib import Path

from play_book_studio.config.settings import load_settings


def _viewer_path_to_local_html(root_dir: Path, viewer_path: str) -> Path | None:
    parsed = _parse_viewer_path(viewer_path)
    if parsed is None:
        return None
    book_slug, _ = parsed
    settings = load_settings(root_dir)
    candidate = settings.raw_html_dir / f"{book_slug}.html"
    if not candidate.exists():
        return None
    return candidate


def _parse_viewer_path(viewer_path: str) -> tuple[str, str] | None:
    value = (viewer_path or "").strip()
    if "#" in value:
        path_part, anchor = value.split("#", 1)
    else:
        path_part, anchor = value, ""
    prefix = "/docs/ocp/4.20/ko/"
    if not path_part.startswith(prefix):
        return None
    remainder = path_part[len(prefix) :]
    parts = [part for part in remainder.split("/") if part]
    if len(parts) != 2 or parts[1] != "index.html":
        return None
    return parts[0], anchor

