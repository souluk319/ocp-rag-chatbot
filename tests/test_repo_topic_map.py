from __future__ import annotations

import unittest
from pathlib import Path

from play_book_studio.ingestion.repo_topic_map import discover_enterprise_topic_map_entries


class RepoTopicMapTests(unittest.TestCase):
    def test_discovers_repo_wide_enterprise_topic_units(self) -> None:
        root = Path(__file__).resolve().parents[1]
        entries = discover_enterprise_topic_map_entries(root)
        self.assertGreater(len(entries), 1000)

        by_path = {entry.source_relative_path: entry for entry in entries}
        self.assertIn("welcome/index.adoc", by_path)
        self.assertIn("architecture/index.adoc", by_path)
        self.assertIn("release_notes/ocp-4-20-release-notes.adoc", by_path)

        self.assertEqual(by_path["welcome/index.adoc"].slug, "welcome__index")
        self.assertEqual(by_path["architecture/index.adoc"].title, "Architecture overview")


if __name__ == "__main__":
    unittest.main()
