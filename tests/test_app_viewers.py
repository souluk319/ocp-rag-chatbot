from __future__ import annotations

import json
import os
import tempfile
import sys
import unittest
from contextlib import contextmanager
from http import HTTPStatus
from pathlib import Path
from typing import Iterator
from urllib.parse import urlencode
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_app_ui import (
    Citation,
    _citation,
    _internal_viewer_html,
    _serialize_citation,
    _viewer_path_to_local_html,
)
from play_book_studio.app.server_routes import (
    _build_viewer_document_payload,
    _canonicalize_viewer_path,
    handle_source_meta,
    handle_viewer_document,
    _viewer_source_meta,
)
from play_book_studio.app.presenters import _build_citation_presentation_context
from play_book_studio.config.settings import load_settings

class TestAppViewers(unittest.TestCase):
    def _capture_json_response(self) -> object:
        class _CaptureHandler:
            def __init__(self) -> None:
                self.calls: list[tuple[HTTPStatus, dict[str, object]]] = []

            def _send_json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
                self.calls.append((status, payload))

        return _CaptureHandler()

    @contextmanager
    def _workspace(self, *, env_text: str | None = None) -> Iterator[Path]:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            if env_text is not None:
                (root / ".env").write_text(env_text, encoding="utf-8")
            yield root

    def _settings(self, root: Path):
        return load_settings(root)

    def _playbook_dir(self, root: Path) -> Path:
        playbook_dir = self._settings(root).playbook_books_dir
        playbook_dir.mkdir(parents=True, exist_ok=True)
        return playbook_dir

    @contextmanager
    def _patched_env(self, *, removed: tuple[str, ...] = (), **updates: str) -> Iterator[None]:
        patched_env = dict(os.environ)
        for key in removed:
            patched_env.pop(key, None)
        patched_env.update(updates)
        with patch.dict(os.environ, patched_env, clear=True):
            yield

    def test_viewer_document_payload_preserves_body_and_normalizes_assets(self) -> None:
        payload = _build_viewer_document_payload(
            """
            <html>
              <head>
                <style>:root { --bg: #fff; } body.is-embedded main { padding: 0; }</style>
                <script>window.bad = true;</script>
              </head>
              <body class="doc-body">
                <main>
                  <img src="./images/hero.png" />
                  <a href="./guide/next.html">next</a>
                  <a href="#section-1">anchor</a>
                </main>
              </body>
            </html>
            """,
            "/playbooks/wiki-runtime/active/release_notes/index.html",
        )

        self.assertEqual("doc-body", payload["body_class_name"])
        self.assertEqual(1, len(payload["inline_styles"]))
        self.assertIn(".viewer-root", payload["inline_styles"][0])
        self.assertIn('/playbooks/wiki-runtime/active/release_notes/images/hero.png', payload["html"])
        self.assertIn('/playbooks/wiki-runtime/active/release_notes/guide/next.html', payload["html"])
        self.assertIn('href="#section-1"', payload["html"])
        self.assertNotIn("<script", payload["html"])
        self.assertTrue(payload["interaction_policy"]["code_copy"])

    def test_viewer_source_meta_resolves_active_runtime_viewer_path(self) -> None:
        with self._workspace() as root:
            settings = self._settings(root)

            settings.source_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            settings.source_manifest_path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "book_slug": "support",
                                "title": "Support",
                                "source_url": "https://example.com/support",
                                "source_lane": "approved_wiki_runtime",
                                "approval_state": "approved",
                                "publication_state": "active",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            settings.normalized_docs_path.parent.mkdir(parents=True, exist_ok=True)
            settings.normalized_docs_path.write_text(
                json.dumps(
                    {
                        "book_slug": "support",
                        "book_title": "Support",
                        "heading": "Get support",
                        "section_path": ["Support", "Get support"],
                        "anchor": "contact-red-hat-support",
                        "source_url": "https://example.com/support",
                        "viewer_path": "/docs/ocp/4.20/ko/support/index.html#contact-red-hat-support",
                        "text": "본문",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            handler = self._capture_json_response()
            handle_source_meta(
                handler,
                urlencode(
                    {
                        "viewer_path": "/playbooks/wiki-runtime/active/support/index.html#contact-red-hat-support",
                    }
                ),
                root_dir=root,
            )

        self.assertEqual(1, len(handler.calls))
        status, payload = handler.calls[0]
        self.assertEqual(HTTPStatus.OK, status)
        self.assertEqual("support", payload["book_slug"])
        self.assertEqual("Get support", payload["section"])
        self.assertEqual(["Support", "Get support"], payload["section_path"])
        self.assertEqual(
            "/playbooks/wiki-runtime/active/support/index.html#contact-red-hat-support",
            payload["viewer_path"],
        )
        self.assertEqual("official_validated_runtime", payload["boundary_truth"])

    def test_viewer_source_meta_uses_registry_for_derived_docs_viewer_path(self) -> None:
        with self._workspace(env_text="ARTIFACTS_DIR=artifacts\n") as root:
            settings = self._settings(root)

            settings.playbook_documents_path.parent.mkdir(parents=True, exist_ok=True)
            settings.playbook_documents_path.write_text(
                json.dumps(
                    {
                        "book_slug": "backup_restore_operations",
                        "title": "Backup Restore Operations",
                        "source_uri": "https://example.com/backup_restore_operations",
                        "review_status": "approved",
                        "section_count": 3,
                        "source_metadata": {
                            "source_type": "operation_playbook",
                            "source_lane": "applied_playbook",
                            "approval_state": "approved",
                            "publication_state": "published",
                        },
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            handler = self._capture_json_response()
            handle_source_meta(
                handler,
                urlencode(
                    {
                        "viewer_path": "/docs/ocp/4.20/ko/backup_restore_operations/index.html",
                    }
                ),
                root_dir=root,
            )

        self.assertEqual(1, len(handler.calls))
        status, payload = handler.calls[0]
        self.assertEqual(HTTPStatus.OK, status)
        self.assertEqual("backup_restore_operations", payload["book_slug"])
        self.assertEqual("Backup Restore Operations", payload["book_title"])
        self.assertEqual("applied_playbook", payload["source_lane"])
        self.assertEqual("official_validated_runtime", payload["boundary_truth"])
        self.assertEqual(
            "/docs/ocp/4.20/ko/backup_restore_operations/index.html",
            payload["viewer_path"],
        )

    def test_viewer_document_route_falls_back_to_normalized_sections_for_known_book(self) -> None:
        with self._workspace() as root:
            settings = self._settings(root)

            settings.source_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            settings.source_manifest_path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "book_slug": "distributed_tracing",
                                "title": "Distributed Tracing",
                                "source_url": "https://example.com/distributed-tracing",
                                "source_lane": "approved_wiki_runtime",
                                "approval_state": "approved",
                                "publication_state": "active",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            settings.normalized_docs_path.parent.mkdir(parents=True, exist_ok=True)
            settings.normalized_docs_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "book_slug": "distributed_tracing",
                                "book_title": "Distributed Tracing",
                                "heading": "Overview",
                                "section_path": ["Distributed Tracing", "Overview"],
                                "anchor": "overview",
                                "viewer_path": "/docs/ocp/4.20/ko/distributed_tracing/index.html#overview",
                                "source_url": "https://example.com/distributed-tracing",
                                "text": "Distributed tracing overview.",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "book_slug": "distributed_tracing",
                                "book_title": "Distributed Tracing",
                                "heading": "Configuration",
                                "section_path": ["Distributed Tracing", "Configuration"],
                                "anchor": "configuration",
                                "viewer_path": "/docs/ocp/4.20/ko/distributed_tracing/index.html#configuration",
                                "source_url": "https://example.com/distributed-tracing",
                                "text": "Configure the collector.",
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            handler = self._capture_json_response()
            handle_viewer_document(
                handler,
                urlencode(
                    {
                        "viewer_path": "/docs/ocp/4.20/ko/distributed_tracing/index.html",
                    }
                ),
                root_dir=root,
            )

        self.assertEqual(1, len(handler.calls))
        status, payload = handler.calls[0]
        self.assertEqual(HTTPStatus.OK, status)
        self.assertEqual(
            "/docs/ocp/4.20/ko/distributed_tracing/index.html",
            payload["viewer_path"],
        )
        self.assertIn("Distributed Tracing", payload["html"])
        self.assertIn('id="overview"', payload["html"])
        self.assertIn('id="configuration"', payload["html"])

    def test_canonicalize_viewer_path_adds_index_for_short_known_paths(self) -> None:
        self.assertEqual(
            "/playbooks/wiki-runtime/active/support/index.html#contact-red-hat-support",
            _canonicalize_viewer_path("/playbooks/wiki-runtime/active/support#contact-red-hat-support"),
        )
        self.assertEqual(
            "/wiki/entities/etcd/index.html",
            _canonicalize_viewer_path("/wiki/entities/etcd"),
        )
        self.assertEqual(
            "/wiki/figures/overview/oke-about-ocp-stack-image.png/index.html",
            _canonicalize_viewer_path("/wiki/figures/overview/oke-about-ocp-stack-image.png"),
        )

    def test_viewer_source_meta_route_supports_entity_and_figure_paths(self) -> None:
        cases = [
            (
                "/wiki/entities/etcd/index.html",
                {
                    "book_slug": "etcd",
                    "book_title": "Etcd",
                    "section": "Etcd",
                    "section_path": ["Etcd"],
                    "viewer_path": "/wiki/entities/etcd/index.html",
                    "source_url": "",
                    "boundary_truth": "official_validated_runtime",
                    "runtime_truth_label": "Validated Runtime Entity Hub",
                },
            ),
            (
                "/wiki/figures/overview/oke-about-ocp-stack-image.png/index.html",
                {
                    "book_slug": "overview",
                    "book_title": "Red Hat OpenShift Kubernetes Engine",
                    "anchor": "oke-about-ocp-stack-image.png",
                    "section": "Red Hat OpenShift Kubernetes Engine",
                    "section_path": [
                        "2.1. OpenShift Container Platform 이해",
                        "Red Hat OpenShift Kubernetes Engine",
                    ],
                    "viewer_path": "/wiki/figures/overview/oke-about-ocp-stack-image.png/index.html",
                    "source_url": "/playbooks/wiki-assets/full_rebuild/overview/oke-about-ocp-stack-image.png",
                    "boundary_truth": "official_validated_runtime",
                    "runtime_truth_label": "Validated Runtime Figure",
                },
            ),
            (
                "/wiki/entities/etcd",
                {
                    "book_slug": "etcd",
                    "book_title": "Etcd",
                    "section": "Etcd",
                    "section_path": ["Etcd"],
                    "viewer_path": "/wiki/entities/etcd/index.html",
                    "source_url": "",
                    "boundary_truth": "official_validated_runtime",
                    "runtime_truth_label": "Validated Runtime Entity Hub",
                },
            ),
            (
                "/wiki/figures/overview/oke-about-ocp-stack-image.png",
                {
                    "book_slug": "overview",
                    "book_title": "Red Hat OpenShift Kubernetes Engine",
                    "anchor": "oke-about-ocp-stack-image.png",
                    "section": "Red Hat OpenShift Kubernetes Engine",
                    "section_path": [
                        "2.1. OpenShift Container Platform 이해",
                        "Red Hat OpenShift Kubernetes Engine",
                    ],
                    "viewer_path": "/wiki/figures/overview/oke-about-ocp-stack-image.png/index.html",
                    "source_url": "/playbooks/wiki-assets/full_rebuild/overview/oke-about-ocp-stack-image.png",
                    "boundary_truth": "official_validated_runtime",
                    "runtime_truth_label": "Validated Runtime Figure",
                },
            ),
        ]

        for viewer_path, expected in cases:
            with self.subTest(viewer_path=viewer_path):
                handler = self._capture_json_response()
                handle_source_meta(handler, urlencode({"viewer_path": viewer_path}), root_dir=ROOT)

                self.assertEqual(1, len(handler.calls))
                status, payload = handler.calls[0]
                self.assertEqual(HTTPStatus.OK, status)
                for key, value in expected.items():
                    self.assertEqual(value, payload[key], key)
                self.assertTrue(payload["section_match_exact"])
                self.assertEqual("approved_wiki_runtime", payload["source_lane"])
                self.assertEqual("approved", payload["approval_state"])
                self.assertEqual("active", payload["publication_state"])
                self.assertEqual("", payload["parser_backend"])
                self.assertEqual("Validated Runtime", payload["boundary_badge"])

    def test_viewer_document_route_supports_entity_and_figure_paths(self) -> None:
        cases = [
            (
                "/wiki/entities/etcd/index.html",
                "/wiki/entities/etcd/index.html",
                [
                    'class="wiki-parent-card"',
                    'class="wiki-parent-eyebrow"',
                    'href="/playbooks/wiki-runtime/active/backup_and_restore/index.html"',
                ],
            ),
            (
                "/wiki/figures/overview/oke-about-ocp-stack-image.png/index.html",
                "/wiki/figures/overview/oke-about-ocp-stack-image.png/index.html",
                [
                    'class="figure-block"',
                    '<figcaption>Red Hat OpenShift Kubernetes Engine</figcaption>',
                    'src="/playbooks/wiki-assets/full_rebuild/overview/oke-about-ocp-stack-image.png"',
                    'href="/wiki/figures/overview/oke-about-ocp-stack-image.png/index.html"',
                ],
            ),
            (
                "/wiki/entities/etcd",
                "/wiki/entities/etcd/index.html",
                [
                    'class="wiki-parent-card"',
                    'class="wiki-parent-eyebrow"',
                    'href="/playbooks/wiki-runtime/active/backup_and_restore/index.html"',
                ],
            ),
            (
                "/wiki/figures/overview/oke-about-ocp-stack-image.png",
                "/wiki/figures/overview/oke-about-ocp-stack-image.png/index.html",
                [
                    'class="figure-block"',
                    '<figcaption>Red Hat OpenShift Kubernetes Engine</figcaption>',
                    'src="/playbooks/wiki-assets/full_rebuild/overview/oke-about-ocp-stack-image.png"',
                    'href="/wiki/figures/overview/oke-about-ocp-stack-image.png/index.html"',
                ],
            ),
        ]

        for viewer_path, expected_viewer_path, markers in cases:
            with self.subTest(viewer_path=viewer_path):
                handler = self._capture_json_response()
                handle_viewer_document(handler, urlencode({"viewer_path": viewer_path}), root_dir=ROOT)

                self.assertEqual(1, len(handler.calls))
                status, payload = handler.calls[0]
                self.assertEqual(HTTPStatus.OK, status)
                self.assertEqual(expected_viewer_path, payload["viewer_path"])
                self.assertIn("html", payload)
                html = str(payload["html"])
                for marker in markers:
                    self.assertIn(marker, html)
                self.assertTrue(payload["interaction_policy"]["anchor_navigation"])

    def test_viewer_document_route_falls_back_to_runtime_markdown_when_artifacts_are_missing(self) -> None:
        with self._workspace() as root:
            runtime_dir = root / "data" / "wiki_runtime_books" / "full_rebuild"
            runtime_dir.mkdir(parents=True, exist_ok=True)
            markdown_path = runtime_dir / "monitoring.md"
            markdown_path.write_text(
                (ROOT / "data" / "wiki_runtime_books" / "full_rebuild" / "monitoring.md").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )

            manifest_path = root / "data" / "wiki_runtime_books" / "full_rebuild_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "slug": "monitoring",
                                "title": "Monitoring",
                                "runtime_path": str(markdown_path),
                                "promotion_strategy": "full_rebuild_generic_export",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            cases = [
                "/docs/ocp/4.20/ko/monitoring/index.html",
                "/playbooks/wiki-runtime/active/monitoring/index.html",
            ]

            for viewer_path in cases:
                with self.subTest(viewer_path=viewer_path):
                    handler = self._capture_json_response()
                    handle_viewer_document(handler, urlencode({"viewer_path": viewer_path}), root_dir=root)

                    self.assertEqual(1, len(handler.calls))
                    status, payload = handler.calls[0]
                    self.assertEqual(HTTPStatus.OK, status)
                    self.assertEqual(viewer_path, payload["viewer_path"])
                    html = str(payload["html"])
                    self.assertIn("Configuring and using the monitoring stack in OpenShift Container Platform", html)
                    self.assertIn("OpenShift Container Platform includes a preconfigured", html)

    def test_viewer_path_local_raw_html_fallback_is_disabled(self) -> None:
        with self._workspace() as root:
            raw_html_dir = root / "custom_raw_html"
            raw_html_dir.mkdir(parents=True)
            expected = raw_html_dir / "architecture.html"
            expected.write_text("<html><body>ok</body></html>", encoding="utf-8")

            with self._patched_env(removed=("ARTIFACTS_DIR",), RAW_HTML_DIR=str(raw_html_dir)):
                target = _viewer_path_to_local_html(
                    root,
                    "/docs/ocp/4.20/ko/architecture/index.html#overview",
                )

        self.assertIsNone(target)

    def test_viewer_path_local_raw_html_fallback_is_disabled_for_other_versions(self) -> None:
        with self._workspace(
            env_text=(
                "RAW_HTML_DIR=custom_raw_html\n"
                "OCP_VERSION=4.18\n"
            )
        ) as root:
            raw_html_dir = root / "custom_raw_html"
            raw_html_dir.mkdir(parents=True)
            expected = raw_html_dir / "architecture.html"
            expected.write_text("<html><body>ok</body></html>", encoding="utf-8")

            target = _viewer_path_to_local_html(
                root,
                "/docs/ocp/4.18/ko/architecture/index.html#overview",
            )

        self.assertIsNone(target)

    def test_serialize_citation_enriches_source_labels(self) -> None:
        with self._workspace() as root:
            settings = self._settings(root)
            manifest_path = settings.source_manifest_path
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "book_slug": "architecture",
                                "title": "아키텍처",
                                "source_url": "https://example.com/architecture",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            normalized_docs_path = settings.normalized_docs_path
            normalized_docs_path.parent.mkdir(parents=True, exist_ok=True)
            normalized_docs_path.write_text(
                json.dumps(
                    {
                        "book_slug": "architecture",
                        "book_title": "아키텍처",
                        "heading": "컨트롤 플레인",
                        "section_level": 2,
                        "section_path": ["개요", "컨트롤 플레인"],
                        "anchor": "overview",
                        "source_url": "https://example.com/architecture",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                        "text": "본문",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            with self._patched_env(
                removed=("ARTIFACTS_DIR", "RAW_HTML_DIR", "SOURCE_MANIFEST_PATH"),
            ):
                payload = _serialize_citation(root, _citation(1))

        self.assertEqual("아키텍처", payload["book_title"])
        self.assertEqual(["개요", "컨트롤 플레인"], payload["section_path"])
        self.assertEqual("개요 > 컨트롤 플레인", payload["section_path_label"])
        self.assertEqual("아키텍처 · 개요 > 컨트롤 플레인", payload["source_label"])
        self.assertEqual("core", payload["source_collection"])
        self.assertEqual("openshift-4-20-core", payload["pack_id"])
        self.assertEqual("OpenShift 4.20", payload["pack_label"])
        self.assertEqual("openshift", payload["inferred_product"])
        self.assertEqual("4.20", payload["inferred_version"])
        self.assertTrue(payload["section_match_exact"])

    def test_serialize_citation_strips_heading_number_prefix_from_source_labels(self) -> None:
        with self._workspace() as root:
            settings = self._settings(root)
            manifest_path = settings.source_manifest_path
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "book_slug": "cli_reference",
                                "title": "CLI Reference",
                                "source_url": "https://example.com/cli-reference",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            normalized_docs_path = settings.normalized_docs_path
            normalized_docs_path.parent.mkdir(parents=True, exist_ok=True)
            normalized_docs_path.write_text(
                json.dumps(
                    {
                        "book_slug": "cli_reference",
                        "book_title": "CLI Reference",
                        "heading": "2.6.1.78. oc expose",
                        "section_level": 4,
                        "section_path": [
                            "2장. OpenShift CLI(oc)",
                            "2.6. OpenShift CLI 개발자 명령 참조",
                            "2.6.1. OpenShift CLI (oc) 개발자",
                        ],
                        "anchor": "oc-expose",
                        "source_url": "https://example.com/cli-reference",
                        "viewer_path": "/docs/ocp/4.20/ko/cli_reference/index.html#oc-expose",
                        "text": "본문",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            payload = _serialize_citation(
                root,
                Citation(
                    index=1,
                    chunk_id="chunk-1",
                    book_slug="cli_reference",
                    section="2.6.1.78. oc expose",
                    anchor="oc-expose",
                    source_url="https://example.com/cli-reference",
                    viewer_path="/docs/ocp/4.20/ko/cli_reference/index.html#oc-expose",
                    excerpt="본문",
                ),
            )

        self.assertEqual("oc expose", payload["section"])
        self.assertEqual(
            [
                "OpenShift CLI(oc)",
                "OpenShift CLI 개발자 명령 참조",
                "OpenShift CLI (oc) 개발자",
            ],
            payload["section_path"],
        )
        self.assertEqual(
            "OpenShift CLI(oc) > OpenShift CLI 개발자 명령 참조 > OpenShift CLI (oc) 개발자",
            payload["section_path_label"],
        )
        self.assertEqual(
            "CLI Reference · OpenShift CLI(oc) > OpenShift CLI 개발자 명령 참조 > OpenShift CLI (oc) 개발자",
            payload["source_label"],
        )

    def test_serialize_citation_marks_section_fallback_when_anchor_missing(self) -> None:
        with self._workspace() as root:
            settings = self._settings(root)
            manifest_path = settings.source_manifest_path
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "book_slug": "architecture",
                                "title": "아키텍처",
                                "source_url": "https://example.com/architecture",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            normalized_docs_path = settings.normalized_docs_path
            normalized_docs_path.parent.mkdir(parents=True, exist_ok=True)
            normalized_docs_path.write_text(
                json.dumps(
                    {
                        "book_slug": "architecture",
                        "book_title": "아키텍처",
                        "heading": "개요",
                        "section_level": 1,
                        "section_path": ["개요"],
                        "anchor": "overview",
                        "source_url": "https://example.com/architecture",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                        "text": "본문",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            payload = _serialize_citation(
                root,
                Citation(
                    index=1,
                    chunk_id="chunk-1",
                    book_slug="architecture",
                    section="존재하지 않는 섹션",
                    anchor="missing-anchor",
                    source_url="https://example.com/architecture",
                    viewer_path="/docs/ocp/4.20/ko/architecture/index.html#missing-anchor",
                    excerpt="본문",
                ),
            )

        self.assertFalse(payload["section_match_exact"])

    def test_serialize_citation_reuses_request_local_presentation_context(self) -> None:
        with self._workspace() as root:
            settings = self._settings(root)
            settings.source_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            settings.source_manifest_path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "book_slug": "architecture",
                                "title": "아키텍처",
                                "source_url": "https://example.com/architecture",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            settings.normalized_docs_path.parent.mkdir(parents=True, exist_ok=True)
            settings.normalized_docs_path.write_text(
                json.dumps(
                    {
                        "book_slug": "architecture",
                        "book_title": "아키텍처",
                        "heading": "컨트롤 플레인",
                        "section_level": 2,
                        "section_path": ["개요", "컨트롤 플레인"],
                        "anchor": "overview",
                        "source_url": "https://example.com/architecture",
                        "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                        "text": "본문",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            with patch("play_book_studio.app.presenters.load_settings", wraps=load_settings) as load_settings_spy:
                presentation_context = _build_citation_presentation_context(root)
                first = _serialize_citation(
                    root,
                    _citation(1),
                    presentation_context=presentation_context,
                )
                second = _serialize_citation(
                    root,
                    _citation(2),
                    presentation_context=presentation_context,
                )

        self.assertEqual(first["book_title"], second["book_title"])
        self.assertEqual(first["source_label"], second["source_label"])
        self.assertEqual(first["section_path_label"], second["section_path_label"])
        self.assertEqual(1, load_settings_spy.call_count)

    def test_internal_viewer_html_falls_back_to_normalized_sections_without_playbook_artifact(self) -> None:
        with self._workspace() as root:
            settings = self._settings(root)
            normalized_docs_path = settings.normalized_docs_path
            normalized_docs_path.parent.mkdir(parents=True, exist_ok=True)
            normalized_docs_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "book_slug": "architecture",
                                "book_title": "아키텍처",
                                "heading": "개요",
                                "section_level": 1,
                                "section_path": ["개요"],
                                "anchor": "overview",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                                "text": "Red Hat OpenShift Documentation Team 법적 공지 초록\n\nOpenShift 아키텍처는 `컨트롤 플레인`과 작업자 노드로 구성됩니다.\n\n[CODE]\noc get nodes\n[/CODE]",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "book_slug": "architecture",
                                "book_title": "아키텍처",
                                "heading": "컨트롤 플레인",
                                "section_level": 2,
                                "section_path": ["개요", "컨트롤 플레인"],
                                "anchor": "control-plane",
                                "source_url": "https://example.com/architecture",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#control-plane",
                                "text": "API 서버와 스케줄러가 핵심 역할을 담당합니다.",
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with self._patched_env(removed=("ARTIFACTS_DIR", "RAW_HTML_DIR")):
                html = _internal_viewer_html(
                    root,
                    "/docs/ocp/4.20/ko/architecture/index.html#overview",
                )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn("아키텍처", html)
        self.assertIn('id="overview"', html)
        self.assertIn('id="control-plane"', html)
        self.assertIn("oc get nodes", html)

    def test_internal_viewer_html_prefers_playbook_artifact_when_available(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "architecture.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "architecture",
                        "title": "아키텍처",
                        "source_uri": "https://example.com/architecture",
                        "language_hint": "ko",
                        "pack_id": "openshift-4-20-core",
                        "inferred_version": "4.20",
                        "sections": [
                            {
                                "section_id": "architecture:overview",
                                "section_key": "architecture:overview",
                                "ordinal": 1,
                                "heading": "개요",
                                "level": 1,
                                "path": ["개요"],
                                "section_path": ["개요"],
                                "section_path_label": "개요",
                                "anchor": "overview",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                                "semantic_role": "overview",
                                "block_kinds": ["prerequisite", "procedure", "code", "note"],
                                "blocks": [
                                    {"kind": "prerequisite", "items": ["cluster-admin 권한", "oc CLI 설치"]},
                                    {"kind": "procedure", "steps": [{"ordinal": 1, "text": "리소스를 확인합니다.", "substeps": ["출력 결과를 검토합니다."]}]},
                                    {"kind": "code", "language": "shell", "code": "oc get nodes", "copy_text": "oc get nodes", "wrap_hint": True, "overflow_hint": "toggle", "caption": "예제 명령"},
                                    {"kind": "note", "variant": "warning", "title": "주의", "text": "운영 중에는 영향도를 먼저 확인합니다."},
                                ],
                            }
                        ],
                        "quality_status": "draft",
                        "quality_score": 0.0,
                        "quality_flags": [],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/architecture/index.html#overview",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn("정리된 AST 기준의 유저용 매뉴얼북을 보여줍니다.", html)
        self.assertIn("사전 요구 사항", html)
        self.assertIn("리소스를 확인합니다.", html)
        self.assertIn("운영 중에는 영향도를 먼저 확인합니다.", html)
        self.assertIn("예제 명령", html)
        self.assertIn('data-label-active="줄바꿈 해제"', html)
        self.assertIn('title="줄바꿈 해제"', html)
        self.assertIn('class="code-block overflow-toggle is-wrapped"', html)

    def test_internal_viewer_html_renders_topic_playbook_chrome(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "backup_restore_control_plane.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "backup_restore_control_plane",
                        "title": "컨트롤 플레인 백업/복구 플레이북",
                        "source_uri": "https://example.com/backup",
                        "topic_summary": "백업과 quorum 복원 절차만 추린 토픽 플레이북입니다.",
                        "source_metadata": {
                            "source_type": "topic_playbook",
                            "derived_from_title": "Backup and restore",
                        },
                        "sections": [
                            {
                                "section_id": "backup_restore_control_plane:overview",
                                "section_key": "backup_restore_control_plane:overview",
                                "ordinal": 1,
                                "heading": "개요",
                                "level": 1,
                                "path": ["개요"],
                                "section_path": ["개요"],
                                "section_path_label": "개요",
                                "anchor": "overview",
                                "viewer_path": "/docs/ocp/4.20/ko/backup_restore_control_plane/index.html#overview",
                                "semantic_role": "overview",
                                "block_kinds": ["paragraph"],
                                "blocks": [
                                    {"kind": "paragraph", "text": "복구 흐름"},
                                ],
                            }
                        ],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/backup_restore_control_plane/index.html#overview",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn("Topic Playbook", html)
        self.assertIn("백업과 quorum 복원 절차만 추린 토픽 플레이북입니다.", html)

    def test_internal_viewer_html_renders_operation_playbook_chrome(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "backup_restore_operations.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "backup_restore_operations",
                        "title": "컨트롤 플레인 백업 운영 플레이북",
                        "source_uri": "https://example.com/backup-ops",
                        "topic_summary": "백업 실행, 결과 검증, 보관 원칙만 추린 운영 절차본입니다.",
                        "source_metadata": {
                            "source_type": "operation_playbook",
                            "derived_from_title": "Backup and restore",
                        },
                        "sections": [
                            {
                                "section_id": "backup_restore_operations:overview",
                                "section_key": "backup_restore_operations:overview",
                                "ordinal": 1,
                                "heading": "개요",
                                "level": 1,
                                "path": ["개요"],
                                "section_path": ["개요"],
                                "section_path_label": "개요",
                                "anchor": "overview",
                                "viewer_path": "/docs/ocp/4.20/ko/backup_restore_operations/index.html#overview",
                                "semantic_role": "overview",
                                "block_kinds": ["paragraph"],
                                "blocks": [
                                    {"kind": "paragraph", "text": "운영 절차 요약"},
                                ],
                            }
                        ],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/backup_restore_operations/index.html#overview",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn("Operation Playbook", html)
        self.assertIn("백업 실행, 결과 검증, 보관 원칙만 추린 운영 절차본입니다.", html)

    def test_internal_viewer_html_embed_mode_omits_nested_hero(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "architecture.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "architecture",
                        "title": "아키텍처",
                        "source_uri": "https://example.com/architecture",
                        "sections": [
                            {
                                "section_id": "architecture:overview",
                                "section_key": "architecture:overview",
                                "ordinal": 1,
                                "heading": "개요",
                                "level": 1,
                                "path": ["개요"],
                                "section_path": ["개요"],
                                "section_path_label": "개요",
                                "anchor": "overview",
                                "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                                "semantic_role": "overview",
                                "block_kinds": ["paragraph"],
                                "blocks": [
                                    {"kind": "paragraph", "text": "임베드 본문만 보여야 합니다."},
                                ],
                            }
                        ],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/architecture/index.html?embed=1#overview",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn("is-embedded", html)
        self.assertNotIn('<section class="hero">', html)
        self.assertNotIn('class="section-card', html)
        self.assertIn('class="study-document study-document-embedded"', html)
        self.assertIn('class="embedded-section', html)
        self.assertIn("공식 매뉴얼 원문", html)
        self.assertIn('class="embedded-origin-link"', html)
        self.assertIn("임베드 본문만 보여야 합니다.", html)
        self.assertIn("--bg:", html)
        self.assertIn("body.is-embedded {", html)
        self.assertNotIn("--bg: #f5f1e8;", html)

    def test_internal_viewer_html_renders_table_headers_and_code_caption(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "nodes.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "nodes",
                        "title": "노드",
                        "source_uri": "https://example.com/nodes",
                        "language_hint": "ko",
                        "pack_id": "openshift-4-20-core",
                        "inferred_version": "4.20",
                        "sections": [
                            {
                                "section_id": "nodes:overview",
                                "section_key": "nodes:overview",
                                "ordinal": 1,
                                "heading": "개요",
                                "level": 1,
                                "path": ["개요"],
                                "section_path": ["개요"],
                                "section_path_label": "개요",
                                "anchor": "overview",
                                "viewer_path": "/docs/ocp/4.20/ko/nodes/index.html#overview",
                                "semantic_role": "overview",
                                "block_kinds": ["code", "table"],
                                "blocks": [
                                    {
                                        "kind": "code",
                                        "language": "yaml",
                                        "code": "kind: Pod",
                                        "copy_text": "kind: Pod",
                                        "wrap_hint": True,
                                        "overflow_hint": "toggle",
                                        "caption": "Pod 오브젝트 정의(YAML)",
                                    },
                                    {
                                        "kind": "table",
                                        "headers": ["이름", "역할"],
                                        "rows": [["master-0", "control-plane"]],
                                        "caption": "노드 역할",
                                    },
                                ],
                            }
                        ],
                        "quality_status": "ready",
                        "quality_score": 0.9,
                        "quality_flags": [],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/nodes/index.html#overview",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn("Pod 오브젝트 정의(YAML)", html)
        self.assertIn("노드 역할", html)
        self.assertIn("<thead><tr><th>이름</th><th>역할</th></tr></thead>", html)

    def test_internal_viewer_html_exposes_quick_navigation_and_metrics(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "operations.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "operations",
                        "title": "운영 개요",
                        "source_uri": "https://example.com/operations",
                        "sections": [
                            {
                                "section_id": "operations:overview",
                                "section_key": "operations:overview",
                                "ordinal": 1,
                                "heading": "개요",
                                "level": 1,
                                "path": ["개요"],
                                "section_path": ["개요"],
                                "anchor": "overview",
                                "viewer_path": "/docs/ocp/4.20/ko/operations/index.html#overview",
                                "semantic_role": "overview",
                                "blocks": [{"kind": "paragraph", "text": "운영 개요입니다."}],
                            },
                            {
                                "section_id": "operations:procedure",
                                "section_key": "operations:procedure",
                                "ordinal": 2,
                                "heading": "적용 절차",
                                "level": 1,
                                "path": ["적용 절차"],
                                "section_path": ["적용 절차"],
                                "anchor": "apply",
                                "viewer_path": "/docs/ocp/4.20/ko/operations/index.html#apply",
                                "semantic_role": "procedure",
                                "blocks": [{"kind": "paragraph", "text": "절차 안내입니다."}],
                            },
                        ],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/operations/index.html#overview",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn("Quick Navigation", html)
        self.assertIn('href="#overview"', html)
        self.assertIn('href="#apply"', html)
        self.assertIn(">절차 1<", html)

    def test_internal_viewer_html_splits_inline_command_paragraph_into_code_box(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "installation_overview.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "installation_overview",
                        "title": "설치 개요",
                        "source_uri": "https://example.com/installation_overview",
                        "language_hint": "ko",
                        "pack_id": "openshift-4-20-core",
                        "inferred_version": "4.20",
                        "sections": [
                            {
                                "section_id": "installation:apply",
                                "section_key": "installation:apply",
                                "ordinal": 1,
                                "heading": "설치 적용",
                                "level": 1,
                                "path": ["설치 적용"],
                                "section_path": ["설치 적용"],
                                "section_path_label": "설치 적용",
                                "anchor": "apply",
                                "viewer_path": "/docs/ocp/4.20/ko/installation_overview/index.html#apply",
                                "semantic_role": "procedure",
                                "block_kinds": ["paragraph"],
                                "blocks": [
                                    {
                                        "kind": "paragraph",
                                        "text": "그런 다음 `oc apply -f install-config.yaml` 명령을 실행하여 클러스터에 적용합니다.",
                                    }
                                ],
                            }
                        ],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/installation_overview/index.html#apply",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn("그런 다음 아래 명령을 실행하여 클러스터에 적용합니다.", html)
        self.assertIn("oc apply -f install-config.yaml", html)
        self.assertIn("copyViewerCode", html)
        self.assertIn("toggleViewerCodeWrap", html)

    def test_internal_viewer_html_renders_procedure_step_command_as_code_box(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "etcd.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "etcd",
                        "title": "etcd",
                        "source_uri": "https://example.com/etcd",
                        "language_hint": "ko",
                        "pack_id": "openshift-4-20-core",
                        "inferred_version": "4.20",
                        "sections": [
                            {
                                "section_id": "etcd:backup",
                                "section_key": "etcd:backup",
                                "ordinal": 1,
                                "heading": "백업 절차",
                                "level": 1,
                                "path": ["백업 절차"],
                                "section_path": ["백업 절차"],
                                "section_path_label": "백업 절차",
                                "anchor": "backup",
                                "viewer_path": "/docs/ocp/4.20/ko/etcd/index.html#backup",
                                "semantic_role": "procedure",
                                "block_kinds": ["procedure"],
                                "blocks": [
                                    {
                                        "kind": "procedure",
                                        "steps": [
                                            {
                                                "ordinal": 1,
                                                "text": "`cluster-backup.sh` 로 snapshot과 정적 pod 리소스를 생성합니다.",
                                                "substeps": [],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/etcd/index.html#backup",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn("다음 명령으로 snapshot과 정적 pod 리소스를 생성합니다.", html)
        self.assertIn("cluster-backup.sh", html)
        self.assertIn('class="procedure-list"', html)
        self.assertIn("copyViewerCode", html)

    def test_internal_viewer_html_keeps_ascii_grid_output_unwrapped(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "support.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "support",
                        "title": "지원",
                        "source_uri": "https://example.com/support",
                        "language_hint": "ko",
                        "pack_id": "openshift-4-20-core",
                        "inferred_version": "4.20",
                        "sections": [
                            {
                                "section_id": "support:ascii-grid",
                                "section_key": "support:ascii-grid",
                                "ordinal": 1,
                                "heading": "출력 예",
                                "level": 1,
                                "path": ["출력 예"],
                                "section_path": ["출력 예"],
                                "section_path_label": "출력 예",
                                "anchor": "ascii-grid",
                                "viewer_path": "/docs/ocp/4.20/ko/support/index.html#ascii-grid",
                                "semantic_role": "example",
                                "block_kinds": ["code"],
                                "blocks": [
                                    {
                                        "kind": "code",
                                        "language": "shell-session",
                                        "wrap_hint": True,
                                        "overflow_hint": "toggle",
                                        "caption": "표 출력",
                                        "code": "+-----+-----+\n| A   | B   |\n+-----+-----+\n| 1   | 2   |\n+-----+-----+",
                                    }
                                ],
                            }
                        ],
                        "quality_status": "ready",
                        "quality_score": 0.9,
                        "quality_flags": [],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/support/index.html#ascii-grid",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn('class="code-block preserve-layout overflow-toggle"', html)
        self.assertNotIn('class="code-block preserve-layout overflow-toggle is-wrapped"', html)

    def test_internal_viewer_html_preserves_raw_html_tables(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "matrix.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "matrix",
                        "title": "Matrix",
                        "source_uri": "https://example.com/matrix",
                        "sections": [
                            {
                                "section_id": "matrix:table",
                                "section_key": "matrix:table",
                                "ordinal": 1,
                                "heading": "매트릭스",
                                "level": 1,
                                "path": ["매트릭스"],
                                "section_path": ["매트릭스"],
                                "anchor": "matrix",
                                "viewer_path": "/docs/ocp/4.20/ko/matrix/index.html#matrix",
                                "semantic_role": "reference",
                                "blocks": [
                                    {
                                        "kind": "paragraph",
                                        "text": '<table><thead><tr><th colspan="2">지원</th></tr></thead><tbody><tr><td>A</td><td>B</td></tr></tbody></table>',
                                    }
                                ],
                            }
                        ],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/matrix/index.html#matrix",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn('<th colspan="2">지원</th>', html)
        self.assertIn("<td>A</td><td>B</td>", html)

    def test_internal_viewer_html_renders_structured_table_cells(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "compatibility.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "compatibility",
                        "title": "Compatibility",
                        "source_uri": "https://example.com/compatibility",
                        "sections": [
                            {
                                "section_id": "compatibility:matrix",
                                "section_key": "compatibility:matrix",
                                "ordinal": 1,
                                "heading": "지원 매트릭스",
                                "level": 2,
                                "path": ["지원", "지원 매트릭스"],
                                "section_path": ["지원", "지원 매트릭스"],
                                "anchor": "matrix",
                                "viewer_path": "/docs/ocp/4.20/ko/compatibility/index.html#matrix",
                                "semantic_role": "reference",
                                "blocks": [
                                    {
                                        "kind": "table",
                                        "caption": "버전 호환성",
                                        "header_cells": [
                                            {"text": "플랫폼", "rowspan": 2},
                                            {"text": "지원", "colspan": 2},
                                        ],
                                        "row_cells": [
                                            [
                                                {"text": "AWS"},
                                                {"text": "4.20"},
                                                {"text": "GA"},
                                            ]
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/compatibility/index.html#matrix",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn('<th rowspan="2">플랫폼</th>', html)
        self.assertIn('<th colspan="2">지원</th>', html)
        self.assertIn(">버전 호환성<", html)

    def test_internal_viewer_html_renders_figure_metadata_strip(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "networking.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "networking",
                        "title": "Networking",
                        "source_uri": "https://example.com/networking",
                        "sections": [
                            {
                                "section_id": "networking:diagram",
                                "section_key": "networking:diagram",
                                "ordinal": 1,
                                "heading": "토폴로지",
                                "level": 3,
                                "path": ["네트워킹", "토폴로지"],
                                "section_path": ["네트워킹", "토폴로지"],
                                "anchor": "topology",
                                "viewer_path": "/docs/ocp/4.20/ko/networking/index.html#topology",
                                "semantic_role": "reference",
                                "blocks": [
                                    {
                                        "kind": "figure",
                                        "src": "/playbooks/wiki-assets/networking/topology.png",
                                        "caption": "네트워크 토폴로지",
                                        "alt": "네트워크 토폴로지",
                                        "kind_label": "diagram",
                                        "diagram_type": "network_map",
                                    }
                                ],
                            }
                        ],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/networking/index.html#topology",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn('class="figure-meta"', html)
        self.assertIn("network map", html)
        self.assertIn('class="section-card section-level-3', html)

    def test_internal_viewer_html_strips_heading_number_prefix_from_visible_title(self) -> None:
        with self._workspace() as root:
            playbook_dir = self._playbook_dir(root)
            (playbook_dir / "cli_reference.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "playbook_document_v1",
                        "source_view_strategy": "playbook_ast_v1",
                        "book_slug": "cli_reference",
                        "title": "CLI Reference",
                        "source_uri": "https://example.com/cli-reference",
                        "sections": [
                            {
                                "section_id": "cli_reference:oc-expose",
                                "section_key": "cli_reference:oc-expose",
                                "ordinal": 1,
                                "heading": "2.6.1.78. oc expose",
                                "level": 4,
                                "path": [
                                    "2장. OpenShift CLI(oc)",
                                    "2.6. OpenShift CLI 개발자 명령 참조",
                                    "2.6.1. OpenShift CLI (oc) 개발자",
                                ],
                                "section_path": [
                                    "2장. OpenShift CLI(oc)",
                                    "2.6. OpenShift CLI 개발자 명령 참조",
                                    "2.6.1. OpenShift CLI (oc) 개발자",
                                ],
                                "section_path_label": "2장. OpenShift CLI(oc) > 2.6. OpenShift CLI 개발자 명령 참조 > 2.6.1. OpenShift CLI (oc) 개발자",
                                "anchor": "oc-expose",
                                "viewer_path": "/docs/ocp/4.20/ko/cli_reference/index.html#oc-expose",
                                "semantic_role": "reference",
                                "block_kinds": ["paragraph"],
                                "blocks": [
                                    {"kind": "paragraph", "text": "복제된 애플리케이션을 서비스 또는 경로로 노출"},
                                ],
                            }
                        ],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            html = _internal_viewer_html(
                root,
                "/docs/ocp/4.20/ko/cli_reference/index.html#oc-expose",
            )

        self.assertIsNotNone(html)
        assert html is not None
        self.assertIn(">oc expose</h2>", html)
        self.assertIn("OpenShift CLI(oc) &gt; OpenShift CLI 개발자 명령 참조 &gt; OpenShift CLI (oc) 개발자", html)
        self.assertNotIn(">2.6.1.78. oc expose</h2>", html)
        self.assertNotIn("2장. OpenShift CLI(oc)", html)
