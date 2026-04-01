from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from deployment.stage11_bundle_utils import load_json, repo_relative, repo_root, utc_now, write_json


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def read_pointer(path: Path, *, default: str) -> str:
    if not path.exists():
        return default
    value = path.read_text(encoding="utf-8").strip()
    return value or default


def write_pointer(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{value.strip()}\n", encoding="utf-8")


def resolve_index_dir(index: str | Path, *, index_root: Path | None = None) -> Path:
    if isinstance(index, Path):
        candidate = index
    else:
        candidate = Path(str(index))
    if candidate.exists():
        return candidate.resolve()
    root = index_root or (repo_root() / "indexes")
    return (root / str(index)).resolve()


def index_manifest_path(index_dir: Path) -> Path:
    return index_dir / "manifests" / "index-manifest.json"


def load_index_manifest(index: str | Path, *, index_root: Path | None = None) -> tuple[Path, dict[str, Any]]:
    index_dir = resolve_index_dir(index, index_root=index_root)
    manifest_path = index_manifest_path(index_dir)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Index manifest is missing: {manifest_path}")
    return index_dir, load_json(manifest_path)


def document_path_from_record(record: dict[str, Any]) -> str:
    source_url = str(record.get("source_url", "")).strip()
    marker = "/blob/main/"
    if marker in source_url:
        return source_url.split(marker, 1)[1]

    local_path = str(record.get("local_path", "")).strip().replace("\\", "/")
    if "/openshift-docs/" in local_path:
        return local_path.split("/openshift-docs/", 1)[1]

    normalized_path = str(record.get("normalized_path", "")).strip().replace("\\", "/")
    source_id = str(record.get("source_id", "")).strip()
    source_marker = f"/documents/{source_id}/" if source_id else "/documents/"
    if source_marker in normalized_path:
        relative = normalized_path.split(source_marker, 1)[1]
        return re.sub(r"\.txt$", ".adoc", relative)

    explicit = str(record.get("document_path", "")).strip()
    return explicit


def ensure_index_layout(index_dir: Path) -> None:
    (index_dir / "manifests").mkdir(parents=True, exist_ok=True)
    (index_dir / "reports").mkdir(parents=True, exist_ok=True)


def update_index_manifest_state(
    index_dir: Path,
    *,
    state: str,
    state_note: str,
    extra_updates: dict[str, Any] | None = None,
) -> dict[str, Any]:
    manifest_path = index_manifest_path(index_dir)
    manifest = load_json(manifest_path)
    manifest["state"] = state
    manifest["state_note"] = state_note
    manifest["state_updated_at"] = utc_now()
    if extra_updates:
        manifest.update(extra_updates)
    write_json(manifest_path, manifest)
    return manifest


def archive_index_snapshot(
    index_dir: Path,
    *,
    archive_root: Path,
    reason: str,
    related_index_id: str,
    operator: str,
) -> Path:
    archive_dir = archive_root / index_dir.name
    if archive_dir.exists():
        shutil.rmtree(archive_dir)
    archive_dir.mkdir(parents=True, exist_ok=True)

    for relative_dir in ("manifests", "reports"):
        source = index_dir / relative_dir
        if source.exists():
            shutil.copytree(source, archive_dir / relative_dir)

    write_json(
        archive_dir / "archive-entry.json",
        {
            "index_id": index_dir.name,
            "source_index_path": repo_relative(index_dir),
            "archive_path": repo_relative(archive_dir),
            "archived_at": utc_now(),
            "reason": reason,
            "related_index_id": related_index_id,
            "operator": operator,
        },
    )
    return archive_dir
