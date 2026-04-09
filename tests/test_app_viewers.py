from __future__ import annotations

import json
import os
import tempfile
import sys
import unittest
from pathlib import Path

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

class TestAppViewers(unittest.TestCase):
    def test_viewer_path_local_raw_html_fallback_is_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw_html_dir = root / "custom_raw_html"
            raw_html_dir.mkdir(parents=True)
            expected = raw_html_dir / "architecture.html"
            expected.write_text("<html><body>ok</body></html>", encoding="utf-8")

            old_artifacts = os.environ.get("ARTIFACTS_DIR")
            old_raw = os.environ.get("RAW_HTML_DIR")
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ["RAW_HTML_DIR"] = str(raw_html_dir)
                target = _viewer_path_to_local_html(
                    root,
                    "/docs/ocp/4.20/ko/architecture/index.html#overview",
                )
            finally:
                if old_artifacts is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_artifacts
                if old_raw is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw

        self.assertIsNone(target)

    def test_viewer_path_local_raw_html_fallback_is_disabled_for_other_versions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw_html_dir = root / "custom_raw_html"
            raw_html_dir.mkdir(parents=True)
            expected = raw_html_dir / "architecture.html"
            expected.write_text("<html><body>ok</body></html>", encoding="utf-8")
            (root / ".env").write_text(
                "RAW_HTML_DIR=custom_raw_html\n"
                "OCP_VERSION=4.18\n",
                encoding="utf-8",
            )

            target = _viewer_path_to_local_html(
                root,
                "/docs/ocp/4.18/ko/architecture/index.html#overview",
            )

        self.assertIsNone(target)

    def test_serialize_citation_enriches_source_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "manifests" / "ocp_ko_4_20_html_single.json"
            manifest_path.parent.mkdir(parents=True)
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

            normalized_docs_path = root / "artifacts" / "corpus" / "normalized_docs.jsonl"
            normalized_docs_path.parent.mkdir(parents=True)
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

            old_artifacts = os.environ.get("ARTIFACTS_DIR")
            old_raw = os.environ.get("RAW_HTML_DIR")
            old_manifest = os.environ.get("SOURCE_MANIFEST_PATH")
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ.pop("RAW_HTML_DIR", None)
                os.environ.pop("SOURCE_MANIFEST_PATH", None)
                payload = _serialize_citation(root, _citation(1))
            finally:
                if old_artifacts is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_artifacts
                if old_raw is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw
                if old_manifest is None:
                    os.environ.pop("SOURCE_MANIFEST_PATH", None)
                else:
                    os.environ["SOURCE_MANIFEST_PATH"] = old_manifest

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

    def test_serialize_citation_marks_section_fallback_when_anchor_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "manifests" / "ocp_ko_4_20_html_single.json"
            manifest_path.parent.mkdir(parents=True)
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

            normalized_docs_path = root / "artifacts" / "corpus" / "normalized_docs.jsonl"
            normalized_docs_path.parent.mkdir(parents=True)
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

    def test_internal_viewer_html_requires_playbook_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            normalized_docs_path = root / "artifacts" / "corpus" / "normalized_docs.jsonl"
            normalized_docs_path.parent.mkdir(parents=True)
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

            old_artifacts = os.environ.get("ARTIFACTS_DIR")
            old_raw = os.environ.get("RAW_HTML_DIR")
            try:
                os.environ.pop("ARTIFACTS_DIR", None)
                os.environ.pop("RAW_HTML_DIR", None)
                html = _internal_viewer_html(
                    root,
                    "/docs/ocp/4.20/ko/architecture/index.html#overview",
                )
            finally:
                if old_artifacts is None:
                    os.environ.pop("ARTIFACTS_DIR", None)
                else:
                    os.environ["ARTIFACTS_DIR"] = old_artifacts
                if old_raw is None:
                    os.environ.pop("RAW_HTML_DIR", None)
                else:
                    os.environ["RAW_HTML_DIR"] = old_raw

        self.assertIsNone(html)

    def test_internal_viewer_html_prefers_playbook_artifact_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            playbook_dir = root / "artifacts" / "corpus" / "playbooks"
            playbook_dir.mkdir(parents=True)
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
        self.assertIn(">줄바꿈 해제<", html)
        self.assertIn(">넓게 보기<", html)

    def test_internal_viewer_html_embed_mode_omits_nested_hero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            playbook_dir = root / "artifacts" / "corpus" / "playbooks"
            playbook_dir.mkdir(parents=True)
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
        self.assertIn("--bg: #f3f5f7;", html)
        self.assertIn("background: linear-gradient(180deg, #f8f9fb 0%, #f1f3f5 100%);", html)
        self.assertNotIn("--bg: #f5f1e8;", html)

    def test_internal_viewer_html_renders_table_headers_and_code_caption(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            playbook_dir = root / "artifacts" / "corpus" / "playbooks"
            playbook_dir.mkdir(parents=True)
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

    def test_internal_viewer_html_keeps_ascii_grid_output_unwrapped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            playbook_dir = root / "artifacts" / "corpus" / "playbooks"
            playbook_dir.mkdir(parents=True)
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
        self.assertIn('class="code-block preserve-layout"', html)
        self.assertNotIn('class="code-block preserve-layout is-wrapped"', html)

