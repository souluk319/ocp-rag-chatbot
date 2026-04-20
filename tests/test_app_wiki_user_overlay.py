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

    def test_edited_card_overlay_upserts_by_target_and_preserves_document_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("ARTIFACTS_DIR=artifacts\n", encoding="utf-8")

            first = save_wiki_user_overlay(
                root,
                {
                    "user_id": "studio-user",
                    "kind": "edited_card",
                    "title": "Cluster Version Operator",
                    "card_title": "Cluster Version Operator",
                    "summary": "viewer card snapshot",
                    "target_kind": "section",
                    "book_slug": "updating_clusters",
                    "anchor": "cluster-version-operator",
                    "viewer_path": "/docs/ocp/4.20/ko/updating_clusters/index.html#cluster-version-operator",
                    "source_anchor": "cluster-version-operator",
                    "source_viewer_path": "/docs/ocp/4.20/ko/updating_clusters/index.html#cluster-version-operator",
                    "document_title": "Cluster Version Operator 수정본",
                    "body": "업그레이드 전 preflight check를 따로 기록한다.",
                    "text_style": {
                        "tone": "teal",
                        "size": "lg",
                        "weight": "strong",
                    },
                    "text_annotations": [
                        {
                            "annotation_id": "ann-edit-1",
                            "kind": "edit",
                            "anchor": "cluster-version-operator",
                            "text": "업그레이드 이전에 preflight check 항목을 먼저 확인한다.",
                            "block_path": "0.2",
                            "style": {
                                "tone": "violet",
                                "size": "lg",
                                "weight": "strong",
                            },
                        },
                        {
                            "annotation_id": "ann-add-1",
                            "kind": "add",
                            "anchor": "cluster-version-operator",
                            "text": "관련 경고 이벤트를 함께 적어둔다.",
                            "x_ratio": 0.32,
                            "y_ratio": 0.44,
                            "style": {
                                "tone": "cyan",
                                "size": "md",
                                "weight": "regular",
                            },
                        },
                    ],
                    "strokes": [
                        {
                            "path": "M 4.0 5.0 L 12.0 14.0",
                            "tool": "highlighter",
                            "style": {"id": "amber"},
                        }
                    ],
                },
            )
            second = save_wiki_user_overlay(
                root,
                {
                    "user_id": "studio-user",
                    "kind": "edited_card",
                    "title": "Cluster Version Operator",
                    "card_title": "Cluster Version Operator",
                    "summary": "viewer card snapshot",
                    "target_kind": "section",
                    "book_slug": "updating_clusters",
                    "anchor": "cluster-version-operator",
                    "viewer_path": "/docs/ocp/4.20/ko/updating_clusters/index.html#cluster-version-operator",
                    "source_anchor": "cluster-version-operator",
                    "source_viewer_path": "/docs/ocp/4.20/ko/updating_clusters/index.html#cluster-version-operator",
                    "body": "업그레이드 직후 MCP 확인까지 체크한다.",
                    "text_style": {
                        "tone": "invalid-tone",
                        "size": "sm",
                        "weight": "invalid-weight",
                    },
                    "text_annotations": [
                        {
                            "annotation_id": "",
                            "kind": "edit",
                            "anchor": "cluster-version-operator",
                            "text": "업그레이드 직후 MCP 확인까지 체크한다.",
                            "block_path": "0.2",
                            "style": {
                                "tone": "invalid-tone",
                                "size": "sm",
                                "weight": "invalid-weight",
                            },
                        },
                        {
                            "kind": "add",
                            "anchor": "cluster-version-operator",
                            "text": "새로 추가한 운영 메모를 카드 위에 남긴다.",
                            "x_ratio": 7,
                            "y_ratio": -3,
                            "style": {
                                "tone": "lime",
                                "size": "md",
                                "weight": "regular",
                            },
                        },
                        {
                            "kind": "edit",
                            "anchor": "cluster-version-operator",
                            "text": "",
                            "block_path": "0.5",
                        },
                    ],
                    "strokes": [],
                },
            )

            self.assertEqual(first["record"]["overlay_id"], second["record"]["overlay_id"])
            self.assertEqual(first["record"]["document_id"], second["record"]["document_id"])
            self.assertEqual("업그레이드 직후 MCP 확인까지 체크한다.", second["record"]["body"])
            self.assertEqual({"tone": "amber", "size": "sm", "weight": "regular"}, second["record"]["text_style"])
            self.assertEqual([], second["record"]["strokes"])
            self.assertEqual(2, len(second["record"]["text_annotations"]))
            self.assertEqual("edit", second["record"]["text_annotations"][0]["kind"])
            self.assertEqual({"tone": "amber", "size": "sm", "weight": "regular"}, second["record"]["text_annotations"][0]["style"])
            self.assertEqual(1.0, second["record"]["text_annotations"][1]["x_ratio"])
            self.assertEqual(0.0, second["record"]["text_annotations"][1]["y_ratio"])
            self.assertEqual("lime", second["record"]["text_annotations"][1]["style"]["tone"])

            overlays = list_wiki_user_overlays(root, user_id="studio-user")
            self.assertEqual(1, overlays["count"])
            self.assertEqual("edited_card", overlays["items"][0]["kind"])
            self.assertEqual("cluster-version-operator", overlays["items"][0]["source_anchor"])
            self.assertEqual(2, len(overlays["items"][0]["payload"]["text_annotations"]))

            signals = build_wiki_overlay_signal_payload(root, user_id="studio-user")
            self.assertEqual(1, signals["summary"]["edited_card_count"])
            self.assertEqual(1, signals["user_focus"]["edited_card_count"])
            self.assertEqual(1, signals["top_targets"][0]["kind_breakdown"]["edited_card"])


if __name__ == "__main__":
    unittest.main()
