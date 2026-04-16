from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "generate_full_rebuild_wiki_relations.py"
SPEC = importlib.util.spec_from_file_location("generate_full_rebuild_wiki_relations", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GenerateFullRebuildWikiRelationsTests(unittest.TestCase):
    def test_candidate_relations_drop_garbage_books_from_active_navigation(self) -> None:
        title_by_slug = {
            "updating_clusters": "Updating Clusters",
            "release_notes": "Release Notes",
            "support": "Support",
            "validation_and_troubleshooting": "Validation and Troubleshooting",
            "backup_and_restore": "Backup and Restore",
            "monitoring": "Monitoring",
        }
        entity_hubs = {
            "installation-day2": {"title": "Installation and Day-2"},
            "lifecycle-and-support": {"title": "Lifecycle and Support"},
            "control-plane-nodes": {"title": "Control Plane Nodes"},
        }

        relations = MODULE._build_candidate_relations(title_by_slug, entity_hubs)

        updating = relations["updating_clusters"]
        self.assertEqual(
            [item["href"] for item in updating["related_docs"]],
            [
                "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                "/playbooks/wiki-runtime/active/monitoring/index.html",
            ],
        )
        self.assertEqual(
            [item["href"] for item in updating["next_reading_path"]],
            [
                "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                "/playbooks/wiki-runtime/active/monitoring/index.html",
            ],
        )
        self.assertEqual(updating["siblings"], [])
        self.assertEqual(
            [item["href"] for item in updating["entities"]],
            ["/wiki/entities/installation-day2/index.html", "/wiki/entities/control-plane-nodes/index.html"],
        )

    def test_candidate_relations_zero_out_garbage_source_books(self) -> None:
        title_by_slug = {
            "release_notes": "Release Notes",
            "support": "Support",
            "validation_and_troubleshooting": "Validation and Troubleshooting",
            "backup_and_restore": "Backup and Restore",
        }

        relations = MODULE._build_candidate_relations(title_by_slug, {})

        for slug in ("release_notes", "support", "validation_and_troubleshooting"):
            self.assertEqual(relations[slug]["entities"], [])
            self.assertEqual(relations[slug]["related_docs"], [])
            self.assertEqual(relations[slug]["next_reading_path"], [])
            self.assertEqual(relations[slug]["siblings"], [])

    def test_chat_aliases_do_not_emit_garbage_targets(self) -> None:
        aliases = MODULE._build_chat_aliases(
            {
                "updating_clusters": {
                    "entities": [
                        {"label": "Lifecycle and Support", "href": "/wiki/entities/lifecycle-and-support/index.html"},
                        {"label": "Installation and Day-2", "href": "/wiki/entities/installation-day2/index.html"},
                    ],
                    "related_docs": [
                        {"label": "Release Notes", "href": "/playbooks/wiki-runtime/active/release_notes/index.html"},
                        {"label": "Backup and Restore", "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html"},
                    ],
                    "next_reading_path": [
                        {"label": "Support", "href": "/playbooks/wiki-runtime/active/support/index.html"},
                    ],
                }
            }
        )

        self.assertEqual(
            aliases["updating_clusters"],
            [
                {"label": "Installation and Day-2", "href": "/wiki/entities/installation-day2/index.html", "kind": "entity"},
                {"label": "Backup and Restore", "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html", "kind": "book"},
            ],
        )
