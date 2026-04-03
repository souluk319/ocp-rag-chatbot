from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.models import NormalizedSection
from ocp_rag_part1.section_keys import assign_section_keys


def make_section(anchor: str, heading: str) -> NormalizedSection:
    return NormalizedSection(
        book_slug="backup_and_restore",
        book_title="Backup and Restore",
        heading=heading,
        section_level=2,
        section_path=[heading],
        anchor=anchor,
        source_url="https://example.com/backup",
        viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html",
        text="text",
    )


class SectionKeyTests(unittest.TestCase):
    def test_assign_section_keys_makes_duplicate_anchors_unique(self) -> None:
        sections = assign_section_keys(
            [
                make_section("backup-etcd", "Backing up etcd"),
                make_section("backup-etcd", "Additional resources"),
            ]
        )

        self.assertEqual("backup-etcd", sections[0].section_key)
        self.assertEqual("backup-etcd__dup2", sections[1].section_key)
        self.assertEqual(
            "/docs/ocp/4.20/ko/backup_and_restore/index.html#backup-etcd",
            sections[0].viewer_path,
        )
        self.assertEqual(
            "/docs/ocp/4.20/ko/backup_and_restore/index.html#backup-etcd__dup2",
            sections[1].viewer_path,
        )

    def test_assign_section_keys_preserves_existing_key(self) -> None:
        section = NormalizedSection(
            book_slug="backup_and_restore",
            book_title="Backup and Restore",
            heading="Backing up etcd",
            section_level=2,
            section_path=["Backing up etcd"],
            anchor="backup-etcd",
            source_url="https://example.com/backup",
            viewer_path="/docs/ocp/4.20/ko/backup_and_restore/index.html#backup-etcd",
            text="text",
            section_key="backup-etcd__dup2",
        )

        keyed = assign_section_keys([section])

        self.assertEqual("backup-etcd__dup2", keyed[0].section_key)
        self.assertEqual(
            "/docs/ocp/4.20/ko/backup_and_restore/index.html#backup-etcd__dup2",
            keyed[0].viewer_path,
        )


if __name__ == "__main__":
    unittest.main()
