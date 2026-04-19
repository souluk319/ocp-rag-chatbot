from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from play_book_studio.config.settings import load_settings
from play_book_studio.runtime_catalog_registry import (
    active_manifest_runtime_slugs,
    official_runtime_book_entry,
    official_runtime_book_registry,
)


class RuntimeCatalogRegistryTests(unittest.TestCase):
    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _write_jsonl(self, path: Path, rows: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in rows),
            encoding="utf-8",
        )

    def test_registry_merges_active_manifest_source_manifest_and_playbook_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("ARTIFACTS_DIR=artifacts\n", encoding="utf-8")
            settings = load_settings(root)

            self._write_json(
                settings.source_manifest_path,
                {
                    "entries": [
                        {
                            "book_slug": "support",
                            "title": "Support",
                            "source_url": "https://example.com/support",
                            "source_lane": "approved_wiki_runtime",
                            "source_type": "official_doc",
                            "approval_state": "approved",
                            "publication_state": "active",
                            "source_repo": "https://github.com/example/openshift-docs",
                            "source_branch": "enterprise-4.20",
                            "source_binding_kind": "file",
                            "source_relative_path": "support/index.adoc",
                            "source_relative_paths": ["support/index.adoc"],
                            "fallback_source_url": "https://docs.example.com/support",
                        },
                        {
                            "book_slug": "operators",
                            "title": "Operators",
                            "source_url": "https://example.com/operators",
                            "source_lane": "applied_playbook",
                            "source_type": "manual_synthesis",
                            "approval_state": "needs_review",
                            "publication_state": "draft",
                            "content_status": "translated_ko_draft",
                        },
                    ]
                },
            )
            self._write_json(
                root / "data" / "wiki_runtime_books" / "active_manifest.json",
                {
                    "generated_at_utc": "2026-04-17T11:00:00+00:00",
                    "active_group": "full_rebuild",
                    "entries": [
                        {
                            "slug": "support",
                            "title": "Support",
                            "source_candidate_path": str(root / "support.md"),
                            "runtime_path": str(root / "runtime" / "support.md"),
                        }
                    ],
                },
            )
            self._write_jsonl(
                settings.playbook_documents_path,
                [
                    {
                        "book_slug": "backup_and_restore",
                        "title": "Backup and restore",
                        "source_uri": "https://example.com/backup_and_restore",
                        "review_status": "approved",
                        "section_count": 12,
                        "source_metadata": {
                            "source_type": "manual_synthesis",
                            "source_lane": "applied_playbook",
                            "approval_state": "approved",
                            "publication_state": "published",
                            "updated_at": "2026-04-17T11:10:00Z",
                        },
                    },
                    {
                        "book_slug": "installing_on_any_platform",
                        "title": "Installing on any platform",
                        "source_uri": "https://github.com/example/openshift-docs/blob/enterprise-4.20/installing/installing_on_any_platform/index.adoc",
                        "review_status": "unreviewed",
                        "translation_stage": "en_only",
                        "section_count": 18,
                        "source_metadata": {
                            "source_type": "official_doc",
                            "source_lane": "official_source_first",
                            "primary_input_kind": "source_repo",
                            "source_repo": "https://github.com/example/openshift-docs",
                            "source_branch": "enterprise-4.20",
                            "source_binding_kind": "file",
                            "source_relative_path": "installing/installing_on_any_platform/index.adoc",
                            "source_relative_paths": ["installing/installing_on_any_platform/index.adoc"],
                            "approval_state": "unreviewed",
                            "publication_state": "candidate",
                            "updated_at": "2026-04-18T09:00:00Z",
                        },
                    },
                    {
                        "book_slug": "backup_restore_operations",
                        "title": "Backup Restore Operations",
                        "source_uri": "https://example.com/backup_restore_operations",
                        "review_status": "approved",
                        "section_count": 4,
                        "source_metadata": {
                            "source_type": "operation_playbook",
                            "source_lane": "applied_playbook",
                            "approval_state": "approved",
                            "publication_state": "published",
                            "updated_at": "2026-04-17T11:11:00Z",
                        },
                    },
                    {
                        "book_slug": "private_runbook",
                        "title": "Private Runbook",
                        "source_uri": "https://example.com/private_runbook",
                        "review_status": "approved",
                        "section_count": 2,
                        "source_metadata": {
                            "source_type": "manual_synthesis",
                            "source_lane": "customer_source_first_pack",
                            "approval_state": "approved",
                            "publication_state": "published",
                            "classification": "private",
                        },
                    },
                ],
            )

            registry = official_runtime_book_registry(root)
            active_slugs = active_manifest_runtime_slugs(root)

        self.assertEqual(
            {"support", "backup_and_restore", "backup_restore_operations"},
            set(registry),
        )
        self.assertEqual(["support"], active_slugs)
        self.assertEqual(
            "/playbooks/wiki-runtime/active/support/index.html",
            registry["support"]["viewer_path"],
        )
        self.assertTrue(registry["support"]["active_runtime"])
        self.assertEqual(
            "https://github.com/example/openshift-docs@enterprise-4.20:support/index.adoc",
            registry["support"]["source_ref"],
        )
        self.assertEqual("file", registry["support"]["source_binding_kind"])
        self.assertEqual(["support/index.adoc"], registry["support"]["source_relative_paths"])
        self.assertEqual("https://docs.example.com/support", registry["support"]["fallback_source_url"])
        self.assertTrue(registry["support"]["source_fingerprint"])
        self.assertEqual(
            "/docs/ocp/4.20/ko/backup_restore_operations/index.html",
            registry["backup_restore_operations"]["viewer_path"],
        )
        self.assertNotIn("installing_on_any_platform", registry)
        self.assertEqual(
            "operation_playbook",
            registry["backup_restore_operations"]["source_type"],
        )
        self.assertEqual(
            "applied_playbook",
            registry["backup_restore_operations"]["source_lane"],
        )

    def test_registry_falls_back_to_source_manifest_when_playbook_documents_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("ARTIFACTS_DIR=artifacts\n", encoding="utf-8")
            settings = load_settings(root)

            self._write_json(
                settings.source_manifest_path,
                {
                    "entries": [
                        {
                            "book_slug": "architecture",
                            "title": "Architecture",
                            "source_url": "https://example.com/architecture",
                            "source_lane": "official_ko",
                            "source_type": "official_doc",
                            "approval_state": "approved",
                            "publication_state": "active",
                        }
                    ]
                },
            )

            entry = official_runtime_book_entry(root, "architecture")

        self.assertEqual("Architecture", entry["title"])
        self.assertEqual("/docs/ocp/4.20/ko/architecture/index.html", entry["viewer_path"])
        self.assertEqual("official_ko", entry["source_lane"])

    def test_registry_cache_busts_when_viewer_settings_change_without_manifest_mtime_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            env_path = root / ".env"
            env_path.write_text(
                "ARTIFACTS_DIR=artifacts\nDOCS_LANGUAGE=ko\nSOURCE_MANIFEST_PATH=artifacts/shared/source_manifest.json\n",
                encoding="utf-8",
            )
            settings = load_settings(root)

            self._write_json(
                settings.source_manifest_path,
                {
                    "entries": [
                        {
                            "book_slug": "architecture",
                            "title": "Architecture",
                            "source_url": "https://example.com/architecture",
                            "source_lane": "official_ko",
                            "source_type": "official_doc",
                            "approval_state": "approved",
                            "publication_state": "active",
                        }
                    ]
                },
            )

            first_entry = official_runtime_book_entry(root, "architecture")

            env_path.write_text(
                (
                    "ARTIFACTS_DIR=artifacts\n"
                    "DOCS_LANGUAGE=en\n"
                    "SOURCE_MANIFEST_PATH=artifacts/shared/source_manifest.json\n"
                    "VIEWER_PATH_TEMPLATE=/docs/custom/{version}/{lang}/{slug}/viewer.html\n"
                ),
                encoding="utf-8",
            )

            second_entry = official_runtime_book_entry(root, "architecture")

        self.assertEqual("/docs/ocp/4.20/ko/architecture/index.html", first_entry["viewer_path"])
        self.assertEqual("/docs/custom/4.20/en/architecture/viewer.html", second_entry["viewer_path"])
        self.assertNotEqual(first_entry["viewer_path"], second_entry["viewer_path"])


if __name__ == "__main__":
    unittest.main()
