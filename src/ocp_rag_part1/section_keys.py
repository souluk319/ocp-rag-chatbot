from __future__ import annotations

import re
from dataclasses import replace
from typing import Iterable

from .models import NormalizedSection


KEY_SAFE_RE = re.compile(r"[^a-z0-9._-]+")


def _viewer_base_path(viewer_path: str) -> str:
    return (viewer_path or "").split("#", 1)[0]


def build_viewer_path(viewer_path: str, section_key: str) -> str:
    return f"{_viewer_base_path(viewer_path)}#{section_key}"


def _normalize_base_key(value: str) -> str:
    normalized = KEY_SAFE_RE.sub("-", (value or "").strip().lower()).strip("-")
    return normalized


def assign_section_keys(sections: Iterable[NormalizedSection]) -> list[NormalizedSection]:
    keyed: list[NormalizedSection] = []
    seen_counts: dict[str, int] = {}

    for index, section in enumerate(sections, start=1):
        if section.section_key:
            section_key = section.section_key.strip()
            keyed.append(
                replace(
                    section,
                    section_key=section_key,
                    viewer_path=build_viewer_path(section.viewer_path, section_key),
                )
            )
            continue

        base_key = _normalize_base_key(section.anchor)
        if not base_key:
            base_key = _normalize_base_key(section.heading)
        if not base_key:
            base_key = f"section-{index:04d}"

        occurrence = seen_counts.get(base_key, 0) + 1
        seen_counts[base_key] = occurrence
        section_key = base_key if occurrence == 1 else f"{base_key}__dup{occurrence}"

        keyed.append(
            replace(
                section,
                section_key=section_key,
                viewer_path=build_viewer_path(section.viewer_path, section_key),
            )
        )

    return keyed
