from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.ingestion.official_rebuild import render_bound_markdown
from play_book_studio.ingestion.source_first import resolve_repo_binding


class SourceFirstBindingTests(unittest.TestCase):
    def test_resolve_repo_binding_supports_collection_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            mirror = root / "tmp_source" / "openshift-docs-enterprise-4.20"
            for relative_path in (
                "networking/networking_overview/understanding-networking.adoc",
                "networking/networking_overview/accessing-hosts.adoc",
                "networking/networking_overview/networking-dashboards.adoc",
                "networking/networking_overview/cidr-range-definitions.adoc",
            ):
                target = mirror / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("= Sample\n", encoding="utf-8")

            binding = resolve_repo_binding(root, "networking_overview")

        self.assertIsNotNone(binding)
        self.assertEqual("collection", binding.binding_kind)
        self.assertEqual("networking/networking_overview", binding.root_relative_path)
        self.assertEqual(
            [
                "networking/networking_overview/understanding-networking.adoc",
                "networking/networking_overview/accessing-hosts.adoc",
                "networking/networking_overview/networking-dashboards.adoc",
                "networking/networking_overview/cidr-range-definitions.adoc",
            ],
            list(binding.source_relative_paths),
        )


class OfficialRebuildRendererTests(unittest.TestCase):
    def test_render_bound_markdown_expands_includes_and_preserves_source_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = root / "guide" / "index.adoc"
            include_path = root / "guide" / "modules" / "install.adoc"
            include_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text("= Main Guide\ninclude::modules/install.adoc[]\n", encoding="utf-8")
            include_path.write_text(
                "== Installing\n[source,bash]\n----\noc get pods\n----\n",
                encoding="utf-8",
            )

            rendered = render_bound_markdown(
                title="메인 가이드",
                source_paths=[source_path],
                binding_kind="file",
            )

        self.assertIn("# 메인 가이드", rendered)
        self.assertIn("## Installing", rendered)
        self.assertIn("```bash", rendered)
        self.assertIn("oc get pods", rendered)

    def test_render_bound_markdown_groups_collection_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            topic_one = root / "collection" / "topic-one.adoc"
            topic_two = root / "collection" / "topic-two.adoc"
            topic_one.parent.mkdir(parents=True, exist_ok=True)
            topic_one.write_text("= Topic One\nText one\n", encoding="utf-8")
            topic_two.write_text("= Topic Two\n== Deep Dive\nText two\n", encoding="utf-8")

            rendered = render_bound_markdown(
                title="네트워킹",
                source_paths=[topic_one, topic_two],
                binding_kind="collection",
            )

        self.assertIn("# 네트워킹", rendered)
        self.assertIn("## Topic One", rendered)
        self.assertIn("## Topic Two", rendered)
        self.assertIn("#### Deep Dive", rendered)


if __name__ == "__main__":
    unittest.main()
