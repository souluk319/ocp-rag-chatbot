# 내부 /docs viewer 경로를 파싱하고 로컬 raw HTML 파일로 매핑한다.
import re
from pathlib import Path
from urllib.parse import urlparse

VIEWER_PATH_RE = re.compile(r"^/docs/ocp/[^/]+/[^/]+/([^/]+)/index\.html$")


def _parse_viewer_path(viewer_path: str) -> tuple[str, str] | None:
    parsed = urlparse((viewer_path or "").strip())
    path_part = parsed.path.strip()
    match = VIEWER_PATH_RE.fullmatch(path_part)
    if match is None:
        return None
    return match.group(1), parsed.fragment.strip()


def _viewer_path_to_local_html(root_dir: Path, viewer_path: str) -> Path | None:
    _ = root_dir
    _ = viewer_path
    return None
