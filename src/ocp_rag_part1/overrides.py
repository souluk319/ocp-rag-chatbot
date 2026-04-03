from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .models import NormalizedSection
from .section_keys import assign_section_keys


OverrideKey = tuple[str, str]


def _override_key(section: NormalizedSection) -> OverrideKey:
    return (section.book_slug, section.section_key or section.anchor)


def read_override_sections(path: Path) -> list[NormalizedSection]:
    rows: list[NormalizedSection] = []
    if not path.exists():
        return rows

    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(NormalizedSection(**json.loads(line)))
    return assign_section_keys(rows)


def write_override_sections(path: Path, sections: Iterable[NormalizedSection]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for section in sections:
            handle.write(json.dumps(section.to_dict(), ensure_ascii=False) + "\n")


def deduplicate_override_sections(
    sections: Iterable[NormalizedSection],
) -> tuple[list[NormalizedSection], int]:
    deduped: dict[OverrideKey, NormalizedSection] = {}
    duplicate_count = 0
    for section in sections:
        key = _override_key(section)
        if key in deduped:
            duplicate_count += 1
        deduped[key] = section
    return list(deduped.values()), duplicate_count


def load_translation_overrides(settings) -> dict[OverrideKey, NormalizedSection]:
    overrides: dict[OverrideKey, NormalizedSection] = {}
    if not settings.translation_overrides_dir.exists():
        return overrides

    for path in sorted(settings.translation_overrides_dir.glob("*.jsonl")):
        sections, _duplicate_count = deduplicate_override_sections(read_override_sections(path))
        for section in sections:
            overrides[_override_key(section)] = section
    return overrides


def apply_translation_overrides(
    sections: list[NormalizedSection],
    overrides: dict[OverrideKey, NormalizedSection],
) -> tuple[list[NormalizedSection], int]:
    if not overrides:
        return list(sections), 0

    merged: list[NormalizedSection] = []
    applied = 0
    for section in sections:
        key = _override_key(section)
        override = overrides.get(key)
        if override is not None:
            merged.append(override)
            applied += 1
        else:
            merged.append(section)
    return merged, applied
