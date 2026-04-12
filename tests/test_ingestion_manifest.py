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

from play_book_studio.ingestion.collector import collect_entry, raw_html_metadata_path
from play_book_studio.config.settings import load_settings
from play_book_studio.ingestion.manifest import (
    build_manifest_update_report,
    build_source_catalog_entries,
    parse_manifest_entries,
)
from play_book_studio.ingestion.models import SourceManifestEntry
from play_book_studio.ingestion.pipeline import load_runtime_manifest_entries


class Part1ManifestTests(unittest.TestCase):
    def test_source_manifest_entry_serializes_default_security_boundary(self) -> None:
        payload = SourceManifestEntry(
            book_slug="nodes",
            title="노드",
            source_url="https://example.com/nodes",
            resolved_source_url="https://example.com/nodes",
            viewer_path="/docs/ocp/4.20/ko/nodes/index.html",
            high_value=True,
        ).to_dict()

        self.assertEqual("public", payload["tenant_id"])
        self.assertEqual("core", payload["workspace_id"])
        self.assertEqual("public", payload["classification"])
        self.assertEqual(["public"], payload["access_groups"])
        self.assertEqual("unspecified", payload["provider_egress_policy"])
        self.assertTrue(payload["pack_id"])
        self.assertTrue(payload["pack_version"])

    def test_parse_manifest_entries_uses_active_pack_version_and_language(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "OCP_VERSION=4.18\n"
                "DOCS_LANGUAGE=ko\n",
                encoding="utf-8",
            )
            settings = load_settings(root)
            entries = parse_manifest_entries(
                """
                <html><body>
                  <a href="/ko/documentation/openshift_container_platform/4.18/html/architecture">아키텍처</a>
                  <a href="/ko/documentation/openshift_container_platform/4.20/html/nodes">노드</a>
                </body></html>
                """,
                settings,
            )

        self.assertEqual(["architecture"], [entry.book_slug for entry in entries])
        self.assertEqual("4.18", entries[0].ocp_version)
        self.assertEqual("ko", entries[0].docs_language)
        self.assertEqual(
            "/docs/ocp/4.18/ko/architecture/index.html",
            entries[0].viewer_path,
        )

    def test_build_manifest_update_report_tracks_added_removed_and_changed_books(self) -> None:
        previous = [
            SourceManifestEntry(
                product_slug="openshift_container_platform",
                ocp_version="4.20",
                docs_language="ko",
                source_kind="html-single",
                book_slug="architecture",
                title="아키텍처",
                index_url="https://example.com/ko/index",
                source_url="https://example.com/architecture",
                resolved_source_url="https://example.com/architecture",
                resolved_language="ko",
                source_state="published_native",
                source_state_reason="ok",
                catalog_source_label="test",
                viewer_path="/docs/ocp/4.20/ko/architecture/index.html",
                high_value=True,
                source_fingerprint="old-arch",
            ),
            SourceManifestEntry(
                product_slug="openshift_container_platform",
                ocp_version="4.20",
                docs_language="ko",
                source_kind="html-single",
                book_slug="nodes",
                title="노드",
                index_url="https://example.com/ko/index",
                source_url="https://example.com/nodes",
                resolved_source_url="https://example.com/nodes",
                resolved_language="ko",
                source_state="published_native",
                source_state_reason="ok",
                catalog_source_label="test",
                viewer_path="/docs/ocp/4.20/ko/nodes/index.html",
                high_value=True,
                source_fingerprint="nodes-1",
            ),
        ]
        current = [
            SourceManifestEntry(
                product_slug="openshift_container_platform",
                ocp_version="4.20",
                docs_language="ko",
                source_kind="html-single",
                book_slug="architecture",
                title="아키텍처 개요",
                index_url="https://example.com/ko/index",
                source_url="https://example.com/architecture",
                resolved_source_url="https://example.com/architecture",
                resolved_language="ko",
                source_state="published_native",
                source_state_reason="ok",
                catalog_source_label="test",
                viewer_path="/docs/ocp/4.20/ko/architecture/index.html",
                high_value=True,
                source_fingerprint="new-arch",
            ),
            SourceManifestEntry(
                product_slug="openshift_container_platform",
                ocp_version="4.20",
                docs_language="ko",
                source_kind="html-single",
                book_slug="monitoring",
                title="모니터링",
                index_url="https://example.com/ko/index",
                source_url="https://example.com/monitoring",
                resolved_source_url="https://example.com/monitoring",
                resolved_language="ko",
                source_state="published_native",
                source_state_reason="ok",
                catalog_source_label="test",
                viewer_path="/docs/ocp/4.20/ko/monitoring/index.html",
                high_value=True,
                source_fingerprint="monitoring-1",
            ),
        ]

        report = build_manifest_update_report(previous, current)

        self.assertEqual(1, report["summary"]["added_count"])
        self.assertEqual(1, report["summary"]["removed_count"])
        self.assertEqual(1, report["summary"]["changed_count"])
        self.assertEqual(["4.20/ko/html-single/monitoring"], report["added"])
        self.assertEqual(["4.20/ko/html-single/nodes"], report["removed"])
        self.assertEqual("architecture", report["changed"][0]["book_slug"])
        self.assertEqual("4.20", report["changed"][0]["ocp_version"])
        self.assertEqual("ko", report["changed"][0]["docs_language"])
        self.assertIn("title", report["changed"][0]["changes"])
        self.assertIn("source_fingerprint", report["changed"][0]["changes"])

    def test_collect_entry_refetches_when_source_fingerprint_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_html_dir = Path(tmpdir)
            settings = SimpleNamespace(
                raw_html_dir=raw_html_dir,
                request_retries=1,
                request_backoff_seconds=0,
                request_timeout_seconds=5,
                user_agent="test-agent",
            )
            entry = SourceManifestEntry(
                product_slug="openshift_container_platform",
                ocp_version="4.20",
                docs_language="ko",
                source_kind="html-single",
                book_slug="architecture",
                title="아키텍처",
                index_url="https://example.com/ko/index",
                source_url="https://example.com/architecture",
                resolved_source_url="https://example.com/architecture",
                resolved_language="ko",
                source_state="published_native",
                source_state_reason="ok",
                catalog_source_label="test",
                viewer_path="/docs/ocp/4.20/ko/architecture/index.html",
                high_value=True,
                source_fingerprint="fingerprint-v1",
            )

            from play_book_studio.ingestion import collector as collector_module

            original_fetch = collector_module.fetch_html_response
            try:
                fetch_calls: list[str] = []

                def fake_fetch(url: str, _settings: object):
                    fetch_calls.append(url)
                    html = (
                        """
                        <html>
                          <body>
                            <a href="/ko/documentation/openshift_container_platform/4.20/html/legal_notice/index">법적 공지</a>
                            <p>OpenShift documentation is licensed under the Apache License 2.0.</p>
                          </body>
                        </html>
                        """
                        if len(fetch_calls) == 1
                        else """
                        <html>
                          <body>
                            <a href="/ko/documentation/openshift_container_platform/4.20/html/legal_notice/index">법적 공지</a>
                            <p>OpenShift documentation is licensed under the Apache License 2.0.</p>
                            <p>Modified versions must remove all Red Hat trademarks.</p>
                          </body>
                        </html>
                        """
                    )
                    return SimpleNamespace(
                        url=url,
                        text=html,
                        encoding="utf-8",
                        apparent_encoding="utf-8",
                        headers={"Last-Modified": "Thu, 10 Apr 2026 00:00:00 GMT"},
                    )

                collector_module.fetch_html_response = fake_fetch

                collect_entry(entry, settings)
                collect_entry(entry, settings)
                self.assertEqual(1, len(fetch_calls))

                updated_entry = SourceManifestEntry(
                    product_slug="openshift_container_platform",
                    ocp_version="4.20",
                    docs_language="ko",
                    source_kind="html-single",
                    book_slug="architecture",
                    title="아키텍처",
                    index_url="https://example.com/ko/index",
                    source_url="https://example.com/architecture",
                    resolved_source_url="https://example.com/architecture",
                    resolved_language="ko",
                    source_state="published_native",
                    source_state_reason="ok",
                    catalog_source_label="test",
                    viewer_path="/docs/ocp/4.20/ko/architecture/index.html",
                    high_value=True,
                    source_fingerprint="fingerprint-v2",
                )
                collect_entry(updated_entry, settings)
                self.assertEqual(2, len(fetch_calls))

                metadata = json.loads(
                    raw_html_metadata_path(settings, "architecture").read_text(encoding="utf-8")
                )
                self.assertEqual("fingerprint-v2", metadata["source_fingerprint"])
                self.assertEqual(
                    "https://example.com/ko/documentation/openshift_container_platform/4.20/html/legal_notice/index",
                    metadata["legal_notice_url"],
                )
                self.assertIn("Apache License 2.0", metadata["license_or_terms"])
                self.assertEqual("2026-04-10T00:00:00Z", metadata["updated_at"])
                self.assertIn("Modified versions must remove all Red Hat trademarks.", metadata["license_or_terms"])
            finally:
                collector_module.fetch_html_response = original_fetch

    def test_load_runtime_manifest_entries_prefers_approved_manifest_over_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifests = root / "manifests"
            manifests.mkdir(parents=True)
            source_catalog = manifests / "ocp_ko_4_20_html_single.json"
            approved_manifest = manifests / "ocp_ko_4_20_approved_ko.json"
            source_catalog.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "catalog",
                        "count": 2,
                        "entries": [
                            {
                                "book_slug": "architecture",
                                "title": "아키텍처",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                                "high_value": True,
                            },
                            {
                                "book_slug": "monitoring",
                                "title": "Monitoring",
                                "source_url": "https://example.com/monitoring",
                                "viewer_path": "/docs/ocp/4.20/ko/monitoring/index.html",
                                "high_value": True,
                            },
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            approved_manifest.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "source": "approved",
                        "count": 1,
                        "entries": [
                            {
                                "book_slug": "architecture",
                                "title": "아키텍처",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html",
                                "high_value": True,
                                "content_status": "approved_ko",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            settings = SimpleNamespace(
                source_manifest_path=approved_manifest,
                source_catalog_path=source_catalog,
            )

            entries = load_runtime_manifest_entries(settings)

        self.assertEqual(["architecture"], [entry.book_slug for entry in entries])

    def test_load_runtime_manifest_entries_requires_approved_manifest(self) -> None:
        settings = SimpleNamespace(
            source_manifest_path=Path("missing-approved.json"),
            source_catalog_path=Path("catalog.json"),
        )

        with self.assertRaises(FileNotFoundError):
            load_runtime_manifest_entries(settings)

    def test_build_source_catalog_entries_sweeps_versions_and_marks_en_only_when_ko_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "SOURCE_CATALOG_VERSIONS=4.20\n"
                "SOURCE_CATALOG_LANGUAGES=ko,en\n",
                encoding="utf-8",
            )
            settings = load_settings(root)

            from play_book_studio.ingestion import manifest as manifest_module

            original_fetch = manifest_module.fetch_docs_index
            try:
                html_by_index = {
                    "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/": """
                    <html><body>
                      <a href="/ko/documentation/openshift_container_platform/4.20/html/architecture">아키텍처</a>
                    </body></html>
                    """,
                    "https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/": """
                    <html><body>
                      <a href="/en/documentation/openshift_container_platform/4.20/html/architecture">Architecture</a>
                      <a href="/en/documentation/openshift_container_platform/4.20/html/operators">Operators</a>
                    </body></html>
                    """,
                }

                def fake_fetch(_settings, *, index_url=None):
                    return html_by_index[str(index_url)]

                manifest_module.fetch_docs_index = fake_fetch

                entries = build_source_catalog_entries(settings)
            finally:
                manifest_module.fetch_docs_index = original_fetch

        self.assertEqual(
            [
                ("4.20", "en", "architecture", "published_native"),
                ("4.20", "en", "operators", "en_only"),
                ("4.20", "ko", "architecture", "published_native"),
            ],
            [
                (entry.ocp_version, entry.docs_language, entry.book_slug, entry.source_state)
                for entry in entries
            ],
        )


if __name__ == "__main__":
    unittest.main()
