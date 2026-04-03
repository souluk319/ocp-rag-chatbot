from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.models import NormalizedSection
from ocp_rag_part1.overrides import (
    apply_translation_overrides,
    deduplicate_override_sections,
    load_translation_overrides,
    write_override_sections,
)


def make_section(*, anchor: str, heading: str, text: str) -> NormalizedSection:
    return NormalizedSection(
        book_slug="monitoring",
        book_title="Monitoring",
        heading=heading,
        section_level=1,
        section_path=[heading],
        anchor=anchor,
        source_url="https://example.com/monitoring",
        viewer_path=f"/docs/ocp/4.20/ko/monitoring/index.html#{anchor}",
        text=text,
    )


class OverrideTests(unittest.TestCase):
    def test_apply_translation_overrides_replaces_matching_section(self) -> None:
        original = [make_section(anchor="monitoring-overview", heading="Monitoring", text="English")]
        override = make_section(anchor="monitoring-overview", heading="모니터링", text="한국어 번역")

        merged, applied = apply_translation_overrides(
            original,
            {("monitoring", "monitoring-overview"): override},
        )

        self.assertEqual(1, applied)
        self.assertEqual("모니터링", merged[0].heading)
        self.assertEqual("한국어 번역", merged[0].text)

    def test_deduplicate_override_sections_keeps_last_value_per_anchor(self) -> None:
        sections = [
            make_section(anchor="same-anchor", heading="First", text="old"),
            make_section(anchor="same-anchor", heading="Second", text="new"),
            make_section(anchor="other-anchor", heading="Other", text="other"),
        ]

        deduped, duplicate_count = deduplicate_override_sections(sections)

        self.assertEqual(1, duplicate_count)
        self.assertEqual(2, len(deduped))
        self.assertEqual("new", deduped[0].text)
        self.assertEqual("other-anchor", deduped[1].anchor)

    def test_load_translation_overrides_ignores_duplicate_rows_in_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            overrides_dir = Path(temp_dir)
            path = overrides_dir / "monitoring.jsonl"
            old = make_section(anchor="same-anchor", heading="First", text="old")
            new = make_section(anchor="same-anchor", heading="First", text="new")
            old.section_key = "same-anchor"
            new.section_key = "same-anchor"
            path.write_text(
                "\n".join(
                    [
                        json.dumps(old.to_dict(), ensure_ascii=False),
                        json.dumps(new.to_dict(), ensure_ascii=False),
                        json.dumps(
                            make_section(anchor="other-anchor", heading="Other", text="other").to_dict(),
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            settings = SimpleNamespace(translation_overrides_dir=overrides_dir)

            overrides = load_translation_overrides(settings)

            self.assertEqual(2, len(overrides))
            self.assertEqual("new", overrides[("monitoring", "same-anchor")].text)
            self.assertEqual("other", overrides[("monitoring", "other-anchor")].text)

    def test_load_translation_overrides_keeps_distinct_duplicate_anchor_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            overrides_dir = Path(temp_dir)
            path = overrides_dir / "monitoring.jsonl"
            path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            make_section(anchor="same-anchor", heading="First", text="one").to_dict(),
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            make_section(anchor="same-anchor", heading="Second", text="two").to_dict(),
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            settings = SimpleNamespace(translation_overrides_dir=overrides_dir)

            overrides = load_translation_overrides(settings)

            self.assertEqual(2, len(overrides))
            self.assertEqual("one", overrides[("monitoring", "same-anchor")].text)
            self.assertEqual("two", overrides[("monitoring", "same-anchor__dup2")].text)

    def test_write_override_sections_writes_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "monitoring.jsonl"

            write_override_sections(
                path,
                [
                    make_section(anchor="a", heading="A", text="one"),
                    make_section(anchor="b", heading="B", text="two"),
                ],
            )

            content = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(2, len(content))
            self.assertIn('"anchor": "a"', content[0])


if __name__ == "__main__":
    unittest.main()
