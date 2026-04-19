from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.app.wiki_user_overlay import (
    build_wiki_overlay_signal_payload,
    list_wiki_user_overlays,
    remove_wiki_user_overlay,
    save_wiki_user_overlay,
)


class TestAppWikiUserOverlay(unittest.TestCase):
    def test_save_list_and_remove_ink_overlay_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("ARTIFACTS_DIR=artifacts\n", encoding="utf-8")

            saved = save_wiki_user_overlay(
                root,
                {
                    "user_id": "studio-user",
                    "kind": "ink",
                    "title": "Architecture",
                    "target_kind": "section",
                    "book_slug": "architecture",
                    "anchor": "overview",
                    "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                    "strokes": [
                        {
                            "path": "M 10.0 12.0 L 24.0 28.0",
                            "tool": "pen",
                            "style": {
                                "id": "cyan",
                                "label": "Cyan",
                                "penColor": "rgba(14, 165, 233, 0.96)",
                                "highlighterColor": "rgba(34, 211, 238, 0.28)",
                            },
                        },
                        {
                            "path": "",
                            "tool": "highlighter",
                            "style": {"id": "amber"},
                        },
                    ],
                },
            )

            record = saved["record"]
            self.assertEqual("ink", record["kind"])
            self.assertEqual("section:architecture#overview", record["target_ref"])
            self.assertEqual(1, len(record["strokes"]))
            self.assertEqual("pen", record["strokes"][0]["tool"])

            overlays = list_wiki_user_overlays(root, user_id="studio-user")
            self.assertEqual(1, overlays["count"])
            self.assertEqual("ink", overlays["items"][0]["kind"])
            self.assertEqual(1, len(overlays["items"][0]["strokes"]))

            removed = remove_wiki_user_overlay(
                root,
                {
                    "user_id": "studio-user",
                    "overlay_id": str(record["overlay_id"]),
                },
            )
            self.assertEqual(1, removed["removed"])
            self.assertEqual(0, removed["count"])

    def test_ink_overlay_upserts_by_target_and_updates_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("ARTIFACTS_DIR=artifacts\n", encoding="utf-8")

            first = save_wiki_user_overlay(
                root,
                {
                    "user_id": "studio-user",
                    "kind": "ink",
                    "title": "Operations",
                    "target_kind": "book",
                    "book_slug": "operations",
                    "viewer_path": "/playbooks/customer-packs/draft-001/index.html",
                    "strokes": [
                        {
                            "path": "M 1.0 1.0 L 2.0 2.0",
                            "tool": "pen",
                            "style": {"id": "rose"},
                        }
                    ],
                },
            )
            second = save_wiki_user_overlay(
                root,
                {
                    "user_id": "studio-user",
                    "kind": "ink",
                    "title": "Operations",
                    "target_kind": "book",
                    "book_slug": "operations",
                    "viewer_path": "/playbooks/customer-packs/draft-001/index.html",
                    "strokes": [
                        {
                            "path": "M 5.0 5.0 L 8.0 8.0",
                            "tool": "highlighter",
                            "style": {"id": "lime"},
                        }
                    ],
                },
            )

            self.assertEqual(first["record"]["overlay_id"], second["record"]["overlay_id"])
            self.assertEqual(1, second["count"])
            self.assertEqual("highlighter", second["record"]["strokes"][0]["tool"])

            signals = build_wiki_overlay_signal_payload(root, user_id="studio-user")
            self.assertEqual(1, signals["summary"]["total_overlay_count"])
            self.assertEqual(1, signals["summary"]["ink_count"])
            self.assertEqual(1, signals["user_focus"]["ink_count"])
            self.assertEqual(1, signals["top_targets"][0]["kind_breakdown"]["ink"])


if __name__ == "__main__":
    unittest.main()
