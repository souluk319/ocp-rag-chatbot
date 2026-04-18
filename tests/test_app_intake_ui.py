from __future__ import annotations

import base64
import json
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_app_ui import (
    Citation,
    _build_customer_pack_plan,
    _build_customer_pack_support_matrix,
    _capture_customer_pack_draft,
    _create_customer_pack_draft,
    _customer_pack_meta_for_viewer_path,
    _ingest_customer_pack,
    _internal_customer_pack_viewer_html,
    _list_customer_pack_drafts,
    _load_customer_pack_book,
    _load_customer_pack_capture,
    _load_customer_pack_draft,
    _normalize_customer_pack_draft,
    _upload_customer_pack_draft,
    _serialize_citation,
)
from play_book_studio.app.server_routes import handle_customer_pack_support_matrix
from play_book_studio.config.settings import load_settings
from play_book_studio.intake.private_corpus import customer_pack_private_manifest_path

class TestAppIntakeUi(unittest.TestCase):
    def test_build_customer_pack_plan_returns_resolved_web_capture(self) -> None:
        payload = _build_customer_pack_plan(
            {
                "source_type": "web",
                "uri": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                "title": "노드",
            }
        )

        self.assertEqual("web", payload["source_type"])
        self.assertEqual("uploaded", payload["source_collection"])
        self.assertEqual("openshift-4-20-custom", payload["pack_id"])
        self.assertEqual("OpenShift 4.20 Custom Pack", payload["pack_label"])
        self.assertEqual("openshift", payload["inferred_product"])
        self.assertEqual("4.20", payload["inferred_version"])
        self.assertEqual("docs_redhat_html_single_v1", payload["capture_strategy"])
        self.assertEqual(
            "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/nodes/index",
            payload["acquisition_uri"],
        )

    def test_build_customer_pack_plan_accepts_docx_source_type(self) -> None:
        payload = _build_customer_pack_plan({"source_type": "docx", "uri": "/tmp/a.docx"})
        self.assertEqual("docx", payload["source_type"])
        self.assertEqual("docx_structured_capture_v1", payload["capture_strategy"])

    def test_build_customer_pack_plan_exposes_support_matrix_truth(self) -> None:
        payload = _build_customer_pack_plan({"source_type": "pdf", "uri": "/tmp/a.pdf", "title": "PDF"})
        matrix = payload["support_matrix"]
        summary = {str(item["source_type"]): dict(item) for item in matrix["source_type_summary"]}

        self.assertEqual("supported", payload["support_status"])
        self.assertEqual("supported", summary["pdf"]["support_status"])
        self.assertEqual("pdf_text", payload["support_route"]["format_id"])
        self.assertTrue(payload["ocr_metadata"]["enabled"])
        self.assertIn("review", payload["support_review_rule"].lower())
        self.assertIn("pdf_scan_ocr", summary["pdf"]["route_ids"])

    def test_support_matrix_helper_exposes_machine_readable_routes(self) -> None:
        matrix = _build_customer_pack_support_matrix()
        entries = {
            str(entry["format_id"]): dict(entry)
            for entry in matrix["entries"]
        }

        self.assertEqual("customer_pack_format_support_matrix_v1", matrix["matrix_version"])
        self.assertEqual("supported", entries["web_html"]["support_status"])
        self.assertEqual("supported", entries["docx"]["support_status"])
        self.assertEqual("staged", entries["pdf_scan_ocr"]["support_status"])
        self.assertEqual("staged", entries["image_ocr"]["support_status"])
        self.assertEqual("rejected", entries["csv"]["support_status"])

    def test_customer_pack_support_matrix_route_returns_same_payload(self) -> None:
        payloads: list[dict[str, object]] = []

        class _Handler:
            def _send_json(self, payload, status=None):  # noqa: ANN001
                del status
                payloads.append(dict(payload))

        handle_customer_pack_support_matrix(_Handler(), "", root_dir=Path("/tmp"))

        self.assertEqual(1, len(payloads))
        self.assertEqual("customer_pack_format_support_matrix_v1", payloads[0]["matrix_version"])
        self.assertIn("entries", payloads[0])

    def test_create_customer_pack_draft_persists_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = _create_customer_pack_draft(
                root,
                {
                    "source_type": "web",
                    "uri": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                    "title": "노드 운영 가이드",
                },
            )
            loaded = _load_customer_pack_draft(root, str(created["draft_id"]))

        self.assertEqual("planned", created["status"])
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(created["draft_id"], loaded["draft_id"])
        self.assertEqual("노드 운영 가이드", loaded["plan"]["title"])
        self.assertEqual("uploaded", loaded["source_collection"])
        self.assertEqual("OpenShift 4.20 Custom Pack", loaded["pack_label"])
        self.assertEqual("4.20", loaded["inferred_version"])
        self.assertEqual(
            "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/nodes/index",
            loaded["plan"]["acquisition_uri"],
        )

    def test_upload_customer_pack_draft_persists_uploaded_pdf_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = _upload_customer_pack_draft(
                root,
                {
                    "source_type": "pdf",
                    "uri": "guide.pdf",
                    "title": "업로드 가이드",
                    "file_name": "guide.pdf",
                    "content_base64": "JVBERi0xLjQgc2FtcGxl",
                },
            )
            uploaded_path = Path(str(created["uploaded_file_path"]))
            loaded = _load_customer_pack_draft(root, str(created["draft_id"]))
            uploaded_bytes = uploaded_path.read_bytes()

        self.assertEqual("pdf", created["request"]["source_type"])
        self.assertEqual("업로드 가이드", created["plan"]["title"])
        self.assertIsNotNone(loaded)
        self.assertEqual(str(uploaded_path), loaded["request"]["uri"])
        self.assertEqual("guide.pdf", loaded["uploaded_file_name"])
        self.assertEqual(str(uploaded_path), loaded["uploaded_file_path"])
        self.assertEqual(b"%PDF-1.4 sample", uploaded_bytes)

    def test_uploaded_binary_sources_normalize_via_stubbed_conversion(self) -> None:
        cases = [
            {
                "source_type": "docx",
                "file_name": "runbook.docx",
                "content": b"fake-docx-bytes",
                "patch_target": "play_book_studio.intake.normalization.builders.convert_with_markitdown",
                "markdown": "# 운영 런북\n\n## 백업\n\ncluster-backup.sh",
                "expected_heading": "백업",
                "expected_text": "cluster-backup.sh",
            },
            {
                "source_type": "pptx",
                "file_name": "runbook.pptx",
                "content": b"fake-pptx-bytes",
                "patch_target": "play_book_studio.intake.normalization.builders.convert_with_markitdown",
                "markdown": "# 운영 런북\n\n## 복구\n\noc delete pod -l app=example",
                "expected_heading": "복구",
                "expected_text": "oc delete pod -l app=example",
            },
            {
                "source_type": "xlsx",
                "file_name": "runbook.xlsx",
                "content": b"fake-xlsx-bytes",
                "patch_target": "play_book_studio.intake.normalization.builders.convert_with_markitdown",
                "markdown": "# 운영 런북\n\n## 시트1\n\n[TABLE]\n절차 | 명령어\n백업 | cluster-backup.sh\n[/TABLE]",
                "expected_heading": "시트1",
                "expected_text": "[TABLE]",
            },
            {
                "source_type": "pdf",
                "file_name": "runbook.pdf",
                "content": b"%PDF-1.4 sample",
                "patch_target": "play_book_studio.intake.normalization.builders.convert_with_markitdown",
                "markdown": "## 운영 런북\n\n## 백업 절차\n\ncluster-backup.sh",
                "expected_heading": "백업 절차",
                "expected_text": "cluster-backup.sh",
            },
        ]

        for case in cases:
            with self.subTest(source_type=case["source_type"]), tempfile.TemporaryDirectory() as tmpdir:
                root = Path(tmpdir)
                created = _upload_customer_pack_draft(
                    root,
                    {
                        "source_type": case["source_type"],
                        "uri": case["file_name"],
                        "title": "업로드 런북",
                        "file_name": case["file_name"],
                        "content_base64": base64.b64encode(case["content"]).decode("ascii"),
                    },
                )
                _capture_customer_pack_draft(root, {"draft_id": str(created["draft_id"])})

                with patch(case["patch_target"], return_value=case["markdown"]):
                    normalized = _normalize_customer_pack_draft(root, {"draft_id": str(created["draft_id"])})
                    book = _load_customer_pack_book(root, str(created["draft_id"]))

                self.assertEqual("normalized", normalized["status"])
                self.assertIsNotNone(book)
                assert book is not None
                self.assertEqual(case["source_type"], book["source_type"])
                self.assertEqual("업로드 런북", book["title"])
                self.assertTrue(any(case["expected_heading"] in section["heading"] for section in book["sections"]))
                self.assertTrue(any(case["expected_text"] in section["text"] for section in book["sections"]))

    def test_list_customer_pack_drafts_returns_saved_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_customer_pack_draft(
                root,
                {
                    "source_type": "pdf",
                    "uri": "/tmp/openshift-troubleshooting.pdf",
                    "title": "트러블슈팅 핸드북",
                },
            )
            payload = _list_customer_pack_drafts(root)

        self.assertEqual(1, len(payload["drafts"]))
        self.assertEqual("트러블슈팅 핸드북", payload["drafts"][0]["title"])
        self.assertEqual("pdf_text_extract_v1", payload["drafts"][0]["capture_strategy"])

    def test_list_customer_pack_drafts_surfaces_playable_asset_counts_after_normalize(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_md = root / "runbook.md"
            source_md.write_text(
                "# 운영 런북\n\n## etcd 백업\n\n```bash\noc debug node/node-0\n```\n\n## 검증\n\n완료 여부 확인",
                encoding="utf-8",
            )
            captured = _capture_customer_pack_draft(
                root,
                {
                    "source_type": "md",
                    "uri": str(source_md),
                    "title": "운영 런북",
                },
            )
            _normalize_customer_pack_draft(root, {"draft_id": str(captured["draft_id"])})
            payload = _list_customer_pack_drafts(root)

        self.assertEqual(6, payload["drafts"][0]["playable_asset_count"])
        self.assertEqual(5, payload["drafts"][0]["derived_asset_count"])
        self.assertEqual(5, len(payload["drafts"][0]["derived_assets"]))

    def test_capture_customer_pack_draft_fetches_and_serves_web_artifact(self) -> None:
        class _FakeResponse:
            encoding = "utf-8"
            apparent_encoding = "utf-8"
            text = "<html><body>captured web source</body></html>"

            def raise_for_status(self) -> None:
                return None

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with patch("play_book_studio.ingestion.collector.requests.get", return_value=_FakeResponse()):
                created = _capture_customer_pack_draft(
                    root,
                    {
                        "source_type": "web",
                        "uri": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                        "title": "노드 운영 가이드",
                    },
                )
            served = _load_customer_pack_capture(root, str(created["draft_id"]))

        self.assertEqual("captured", created["status"])
        self.assertIsNotNone(served)
        assert served is not None
        body, content_type = served
        self.assertEqual("text/html; charset=utf-8", content_type)
        self.assertIn("captured web source", body.decode("utf-8"))

    def test_normalize_customer_pack_draft_builds_internal_study_view(self) -> None:
        class _FakeResponse:
            encoding = "utf-8"
            apparent_encoding = "utf-8"
            text = """
            <html>
              <body>
                <main id="main-content">
                  <article>
                    <h1>노드 운영</h1>
                    <p>개요 설명입니다.</p>
                    <h2 id="events">이벤트 확인</h2>
                    <p>문제를 좁혀가는 절차를 설명합니다.</p>
                  </article>
                </main>
              </body>
            </html>
            """

            def raise_for_status(self) -> None:
                return None

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with patch("play_book_studio.ingestion.collector.requests.get", return_value=_FakeResponse()):
                captured = _capture_customer_pack_draft(
                    root,
                    {
                        "source_type": "web",
                        "uri": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                        "title": "노드 운영 가이드",
                    },
                )
            normalized = _normalize_customer_pack_draft(root, {"draft_id": str(captured["draft_id"])})
            book = _load_customer_pack_book(root, str(captured["draft_id"]))
            viewer_html = _internal_customer_pack_viewer_html(
                root,
                f"/playbooks/customer-packs/{captured['draft_id']}/index.html#events",
            )
            derived_viewer_html = _internal_customer_pack_viewer_html(
                root,
                f"/playbooks/customer-packs/{captured['draft_id']}/assets/{captured['draft_id']}--topic_playbook/index.html#events",
            )

        self.assertEqual("normalized", normalized["status"])
        self.assertEqual(6, normalized["playable_asset_count"])
        self.assertEqual(5, normalized["derived_asset_count"])
        self.assertEqual(5, len(normalized["derived_assets"]))
        self.assertIsNotNone(book)
        assert book is not None
        self.assertEqual(str(captured["draft_id"]), book["draft_id"])
        self.assertEqual(2, len(book["sections"]))
        self.assertEqual(6, book["playable_asset_count"])
        self.assertEqual(5, book["derived_asset_count"])
        self.assertEqual("events", book["sections"][1]["anchor"])
        self.assertIn("/playbooks/customer-packs/", book["target_viewer_path"])
        self.assertEqual(f"/api/customer-packs/captured?draft_id={captured['draft_id']}", book["source_origin_url"])
        self.assertEqual("ready", book["quality_status"])
        self.assertIsNotNone(viewer_html)
        assert viewer_html is not None
        self.assertIn("Customer Playbook Draft", viewer_html)
        self.assertIn("이벤트 확인", viewer_html)
        self.assertIn("업로드 웹 문서를 canonical section으로 정리한 내부 review view입니다.", viewer_html)
        self.assertIn("5개의 파생 플레이북 자산", viewer_html)
        self.assertIsNotNone(derived_viewer_html)
        assert derived_viewer_html is not None
        self.assertIn("Topic Playbook", derived_viewer_html)

    def test_ingest_customer_pack_runs_capture_and_normalize_in_one_call(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_md = root / "runbook.md"
            source_md.write_text(
                "# 운영 런북\n\n## etcd 백업\n\n```bash\ncluster-backup.sh /backup\n```\n\n## 검증\n\n완료 여부를 점검합니다.\n",
                encoding="utf-8",
            )

            normalized = _ingest_customer_pack(
                root,
                {
                    "source_type": "md",
                    "uri": str(source_md),
                    "title": "운영 런북",
                },
            )

        self.assertEqual("normalized", normalized["status"])
        self.assertEqual(6, normalized["playable_asset_count"])
        self.assertEqual(5, normalized["derived_asset_count"])
        self.assertIn("book", normalized)
        self.assertEqual(str(normalized["draft_id"]), normalized["book"]["draft_id"])
        self.assertIn("/playbooks/customer-packs/", normalized["book"]["target_viewer_path"])

    def test_ingest_customer_pack_materializes_private_corpus_artifacts(self) -> None:
        class _FakeTokenizer:
            model_max_length = 1024

            def __call__(self, text: str, **kwargs):
                del kwargs
                token_count = max(len(str(text).split()), 1)
                return {"input_ids": list(range(token_count))}

        class _FakeVectorRow:
            def __init__(self, values: list[float]) -> None:
                self._values = values

            def tolist(self) -> list[float]:
                return list(self._values)

        class _FakeChunkingModel:
            tokenizer = _FakeTokenizer()

        class _FakeModel:
            def encode(self, texts, **kwargs):
                del kwargs
                return [_FakeVectorRow([1.0, 0.0, 0.0]) for _ in texts]

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_md = root / "runbook.md"
            source_md.write_text(
                "# 운영 런북\n\n## ConfigMap Secret\n\nConfigMap Secret values must be synchronized before rollout.\n",
                encoding="utf-8",
            )

            with patch("play_book_studio.intake.private_corpus.load_sentence_model", return_value=_FakeModel()):
                with patch("play_book_studio.ingestion.chunking.load_sentence_model", return_value=_FakeChunkingModel()):
                    normalized = _ingest_customer_pack(
                        root,
                        {
                            "source_type": "md",
                            "uri": str(source_md),
                            "title": "운영 런북",
                            "tenant_id": "tenant-a",
                            "workspace_id": "workspace-a",
                            "approval_state": "approved",
                            "publication_state": "draft",
                        },
                    )

            self.assertIn("private_corpus", normalized)
            private_corpus = normalized["private_corpus"]
            manifest_path = customer_pack_private_manifest_path(load_settings(root), str(normalized["draft_id"]))
            corpus_dir = manifest_path.parent
            self.assertTrue(manifest_path.exists())
            self.assertTrue((corpus_dir / "chunks.jsonl").exists())
            self.assertTrue((corpus_dir / "bm25_corpus.jsonl").exists())
            self.assertTrue((corpus_dir / "vector_store.jsonl").exists())
            self.assertEqual("customer_private_corpus_v1", private_corpus["artifact_version"])
            self.assertEqual("ready", private_corpus["vector_status"])
            self.assertTrue(private_corpus["runtime_eligible"])
            self.assertEqual([], private_corpus["boundary_fail_reasons"])
            self.assertGreater(int(private_corpus["chunk_count"]), 0)
            self.assertEqual(str(normalized["draft_id"]), private_corpus["draft_id"])
            self.assertNotIn("manifest_path", private_corpus)
            self.assertNotIn("vector_error", private_corpus)

    def test_internal_customer_pack_viewer_renders_markdown_code_and_table_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_md = root / "runbook.md"
            source_md.write_text(
                "# 운영 런북\n\n## etcd 백업\n\n```bash\ncluster-backup.sh /backup\n```\n\n| 절차 | 명령어 |\n| --- | --- |\n| 백업 | cluster-backup.sh |\n",
                encoding="utf-8",
            )

            normalized = _ingest_customer_pack(
                root,
                {
                    "source_type": "md",
                    "uri": str(source_md),
                    "title": "운영 런북",
                },
            )
            viewer_html = _internal_customer_pack_viewer_html(
                root,
                f"/playbooks/customer-packs/{normalized['draft_id']}/index.html",
            )

        self.assertIsNotNone(viewer_html)
        assert viewer_html is not None
        self.assertIn('<pre><code>cluster-backup.sh /backup</code></pre>', viewer_html)
        self.assertIn("<table>", viewer_html)
        self.assertNotIn("<p>| 절차 | 명령어 |", viewer_html)

    def test_internal_customer_pack_viewer_renders_sparse_pdf_table_without_fake_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_pdf = root / "configmap-secret.pdf"
            source_pdf.write_bytes(b"%PDF-1.4 sample")

            captured = _capture_customer_pack_draft(
                root,
                {
                    "source_type": "pdf",
                    "uri": str(source_pdf),
                    "title": "ConfigMap Secret",
                },
            )

            with patch(
                "play_book_studio.intake.normalization.builders.convert_with_markitdown",
                return_value=(
                    "# ConfigMap Secret\n\n"
                    "## ConfigMap Secret 비교\n\n"
                    "| ConfigMap: | | | 일반 | 설정 데이터 | 저장 | | | |\n"
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| Secret: | | 민감한 | 정보 | 저장 | | | | |\n"
                ),
            ):
                _normalize_customer_pack_draft(root, {"draft_id": str(captured["draft_id"])})
                viewer_html = _internal_customer_pack_viewer_html(
                    root,
                    f"/playbooks/customer-packs/{captured['draft_id']}/index.html",
                )

        self.assertIsNotNone(viewer_html)
        assert viewer_html is not None
        self.assertIn("<td>ConfigMap</td>", viewer_html)
        self.assertIn("<td>일반 설정 데이터 저장</td>", viewer_html)
        self.assertNotIn("<th>ConfigMap</th>", viewer_html)
        self.assertNotIn("<td>-</td>", viewer_html)

    def test_customer_pack_meta_prefers_captured_source_url_and_quality(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "customer_packs" / "drafts"
            book_dir = root / "artifacts" / "customer_packs" / "books"
            draft_dir.mkdir(parents=True)
            book_dir.mkdir(parents=True)

            (draft_dir / "dtb-review.json").write_text(
                json.dumps(
                    {
                        "draft_id": "dtb-review",
                        "status": "normalized",
                        "created_at": "2026-04-06T00:00:00Z",
                        "updated_at": "2026-04-06T00:00:00Z",
                        "request": {
                            "source_type": "pdf",
                            "uri": "/tmp/demo.pdf",
                            "title": "데모 PDF",
                            "language_hint": "ko",
                        },
                        "plan": {
                            "book_slug": "demo-pdf",
                            "title": "데모 PDF",
                            "source_type": "pdf",
                            "source_uri": "/tmp/demo.pdf",
                            "source_collection": "uploaded",
                            "pack_id": "openshift-4-16-custom",
                            "pack_label": "OpenShift 4.16 Custom Pack",
                            "inferred_product": "openshift",
                            "inferred_version": "4.16",
                            "acquisition_uri": "/tmp/demo.pdf",
                            "capture_strategy": "pdf_text_extract_v1",
                            "acquisition_step": "capture",
                            "normalization_step": "normalize",
                            "derivation_step": "derive",
                            "notes": [],
                            "canonical_model": "canonical_book_v1",
                            "source_view_strategy": "source_view_first",
                            "retrieval_derivation": "chunks_from_canonical_sections",
                        },
                        "capture_artifact_path": "/tmp/demo.pdf",
                        "capture_content_type": "application/pdf",
                        "capture_byte_size": 12,
                        "degraded_pdf": True,
                        "degraded_reason": "too_many_heading_only_sections",
                        "fallback_used": False,
                        "fallback_backend": "surya",
                        "fallback_status": "backend_unavailable",
                        "fallback_reason": "surya_adapter_unavailable",
                        "capture_error": "",
                        "canonical_book_path": str(book_dir / "dtb-review.json"),
                        "normalized_section_count": 3,
                        "normalize_error": "",
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )
            (book_dir / "dtb-review.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "canonical_book_v1",
                        "book_slug": "demo-pdf",
                        "title": "데모 PDF",
                        "source_type": "pdf",
                        "source_uri": "/tmp/demo.pdf",
                        "language_hint": "ko",
                        "source_view_strategy": "normalized_sections_v1",
                        "retrieval_derivation": "chunks_from_canonical_sections",
                        "sections": [
                            {
                                "ordinal": 1,
                                "section_key": "demo-pdf:page-summary",
                                "heading": "Page Summary",
                                "section_level": 1,
                                "section_path": ["Page 1", "Page Summary"],
                                "section_path_label": "Page 1 > Page Summary",
                                "anchor": "page-summary",
                                "viewer_path": "/playbooks/customer-packs/dtb-review/index.html#page-summary",
                                "source_url": "/tmp/demo.pdf",
                                "text": "Page Summary",
                                "block_kinds": ["paragraph"],
                            },
                            {
                                "ordinal": 2,
                                "section_key": "demo-pdf:short-a",
                                "heading": "온프레미스",
                                "section_level": 1,
                                "section_path": ["Page 1", "온프레미스"],
                                "section_path_label": "Page 1 > 온프레미스",
                                "anchor": "short-a",
                                "viewer_path": "/playbooks/customer-packs/dtb-review/index.html#short-a",
                                "source_url": "/tmp/demo.pdf",
                                "text": "온프레미스",
                                "block_kinds": ["paragraph"],
                            },
                            {
                                "ordinal": 3,
                                "section_key": "demo-pdf:short-b",
                                "heading": "설치",
                                "section_level": 1,
                                "section_path": ["Page 1", "설치"],
                                "section_path_label": "Page 1 > 설치",
                                "anchor": "short-b",
                                "viewer_path": "/playbooks/customer-packs/dtb-review/index.html#short-b",
                                "source_url": "/tmp/demo.pdf",
                                "text": "설치",
                                "block_kinds": ["paragraph"],
                            },
                        ],
                        "notes": [],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            meta = _customer_pack_meta_for_viewer_path(root, "/playbooks/customer-packs/dtb-review/index.html#short-a")

        self.assertIsNotNone(meta)
        assert meta is not None
        self.assertEqual("/api/customer-packs/captured?draft_id=dtb-review", meta["source_url"])
        self.assertEqual("review", meta["quality_status"])
        self.assertIn("정규화 품질 검토", meta["quality_summary"])
        self.assertFalse(meta["fallback_used"])
        self.assertNotIn("quality_score", meta)
        self.assertNotIn("quality_flags", meta)
        self.assertNotIn("degraded_pdf", meta)
        self.assertNotIn("degraded_reason", meta)
        self.assertNotIn("fallback_backend", meta)
        self.assertNotIn("fallback_status", meta)
        self.assertNotIn("fallback_reason", meta)
        self.assertTrue(meta["section_match_exact"])

    def test_customer_pack_meta_marks_fallback_when_anchor_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "customer_packs" / "drafts"
            book_dir = root / "artifacts" / "customer_packs" / "books"
            draft_dir.mkdir(parents=True)
            book_dir.mkdir(parents=True)

            (draft_dir / "dtb-review.json").write_text(
                json.dumps(
                    {
                        "draft_id": "dtb-review",
                        "status": "normalized",
                        "created_at": "2026-04-06T00:00:00Z",
                        "updated_at": "2026-04-06T00:00:00Z",
                        "request": {
                            "source_type": "pdf",
                            "uri": "/tmp/demo.pdf",
                            "title": "데모 PDF",
                            "language_hint": "ko",
                        },
                        "plan": {
                            "book_slug": "demo-pdf",
                            "title": "데모 PDF",
                            "source_type": "pdf",
                            "source_uri": "/tmp/demo.pdf",
                            "source_collection": "uploaded",
                            "pack_id": "openshift-4-16-custom",
                            "pack_label": "OpenShift 4.16 Custom Pack",
                            "inferred_product": "openshift",
                            "inferred_version": "4.16",
                            "acquisition_uri": "/tmp/demo.pdf",
                            "capture_strategy": "pdf_text_extract_v1",
                            "acquisition_step": "capture",
                            "normalization_step": "normalize",
                            "derivation_step": "derive",
                            "notes": [],
                            "canonical_model": "canonical_book_v1",
                            "source_view_strategy": "source_view_first",
                            "retrieval_derivation": "chunks_from_canonical_sections",
                        },
                        "capture_artifact_path": "/tmp/demo.pdf",
                        "capture_content_type": "application/pdf",
                        "capture_byte_size": 12,
                        "capture_error": "",
                        "canonical_book_path": str(book_dir / "dtb-review.json"),
                        "normalized_section_count": 1,
                        "normalize_error": "",
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )
            (book_dir / "dtb-review.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "canonical_book_v1",
                        "book_slug": "demo-pdf",
                        "title": "데모 PDF",
                        "source_type": "pdf",
                        "source_uri": "/tmp/demo.pdf",
                        "language_hint": "ko",
                        "source_view_strategy": "normalized_sections_v1",
                        "retrieval_derivation": "chunks_from_canonical_sections",
                        "sections": [
                            {
                                "ordinal": 1,
                                "section_key": "demo-pdf:short-a",
                                "heading": "온프레미스",
                                "section_level": 1,
                                "section_path": ["Page 1", "온프레미스"],
                                "section_path_label": "Page 1 > 온프레미스",
                                "anchor": "short-a",
                                "viewer_path": "/playbooks/customer-packs/dtb-review/index.html#short-a",
                                "source_url": "/tmp/demo.pdf",
                                "text": "온프레미스",
                                "block_kinds": ["paragraph"],
                            },
                        ],
                        "notes": [],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            meta = _customer_pack_meta_for_viewer_path(root, "/playbooks/customer-packs/dtb-review/index.html#missing")

        self.assertIsNotNone(meta)
        assert meta is not None
        self.assertFalse(meta["section_match_exact"])

    def test_customer_pack_meta_supports_asset_viewer_paths_and_strips_heading_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "customer_packs" / "drafts"
            book_dir = root / "artifacts" / "customer_packs" / "books"
            draft_dir.mkdir(parents=True)
            book_dir.mkdir(parents=True)

            (draft_dir / "dtb-demo.json").write_text(
                json.dumps(
                    {
                        "draft_id": "dtb-demo",
                        "status": "normalized",
                        "created_at": "2026-04-06T00:00:00Z",
                        "updated_at": "2026-04-06T00:00:00Z",
                        "request": {
                            "source_type": "web",
                            "uri": "https://example.com/demo",
                            "title": "데모 가이드",
                            "language_hint": "ko",
                        },
                        "plan": {
                            "book_slug": "demo-guide",
                            "title": "데모 가이드",
                            "source_type": "web",
                            "source_uri": "https://example.com/demo",
                            "source_collection": "uploaded",
                            "pack_id": "openshift-4-20-custom",
                            "pack_label": "OpenShift 4.20 Custom Pack",
                            "inferred_product": "openshift",
                            "inferred_version": "4.20",
                            "acquisition_uri": "https://example.com/demo",
                            "capture_strategy": "docs_redhat_html_single_v1",
                            "acquisition_step": "capture",
                            "normalization_step": "normalize",
                            "derivation_step": "derive",
                            "notes": [],
                            "canonical_model": "canonical_book_v1",
                            "source_view_strategy": "source_view_first",
                            "retrieval_derivation": "chunks_from_canonical_sections",
                        },
                        "capture_artifact_path": "",
                        "capture_content_type": "",
                        "capture_byte_size": 0,
                        "capture_error": "",
                        "canonical_book_path": str(book_dir / "dtb-demo.json"),
                        "normalized_section_count": 1,
                        "normalize_error": "",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (book_dir / "dtb-demo--topic_playbook.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "canonical_book_v1",
                        "book_slug": "dtb-demo--topic_playbook",
                        "title": "데모 가이드 Topic Playbook",
                        "asset_slug": "dtb-demo--topic_playbook",
                        "playbook_family": "topic_playbook",
                        "family_label": "Topic Playbook",
                        "family_summary": "핵심 절차만 다시 묶은 파생 플레이북입니다.",
                        "source_type": "web",
                        "source_uri": "https://example.com/demo",
                        "language_hint": "ko",
                        "source_view_strategy": "normalized_sections_v1",
                        "retrieval_derivation": "chunks_from_canonical_sections",
                        "sections": [
                            {
                                "ordinal": 1,
                                "section_key": "demo-guide:events",
                                "heading": "2.6.1.78. oc expose",
                                "section_level": 2,
                                "section_path": [
                                    "2장. OpenShift CLI(oc)",
                                    "2.6. OpenShift CLI 개발자 명령 참조",
                                ],
                                "section_path_label": "2장. OpenShift CLI(oc) > 2.6. OpenShift CLI 개발자 명령 참조",
                                "anchor": "events",
                                "viewer_path": "/playbooks/customer-packs/dtb-demo/assets/dtb-demo--topic_playbook/index.html#events",
                                "source_url": "https://example.com/demo",
                                "text": "oc expose 절차",
                                "block_kinds": ["paragraph"],
                            }
                        ],
                        "notes": [],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            meta = _customer_pack_meta_for_viewer_path(
                root,
                "/playbooks/customer-packs/dtb-demo/assets/dtb-demo--topic_playbook/index.html#events",
            )

        self.assertIsNotNone(meta)
        assert meta is not None
        self.assertEqual("oc expose", meta["section"])
        self.assertEqual(
            ["OpenShift CLI(oc)", "OpenShift CLI 개발자 명령 참조"],
            meta["section_path"],
        )
        self.assertEqual(
            "OpenShift CLI(oc) > OpenShift CLI 개발자 명령 참조",
            meta["section_path_label"],
        )

    def test_serialize_citation_enriches_customer_pack_source_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "customer_packs" / "drafts"
            book_dir = root / "artifacts" / "customer_packs" / "books"
            draft_dir.mkdir(parents=True)
            book_dir.mkdir(parents=True)

            draft_payload = {
                "draft_id": "dtb-demo",
                "status": "normalized",
                "created_at": "2026-04-06T00:00:00Z",
                "updated_at": "2026-04-06T00:00:00Z",
                "request": {
                    "source_type": "web",
                    "uri": "https://example.com/demo",
                    "title": "데모 가이드",
                    "language_hint": "ko",
                },
                "plan": {
                    "book_slug": "demo-guide",
                    "title": "데모 가이드",
                    "source_type": "web",
                    "source_uri": "https://example.com/demo",
                    "acquisition_uri": "https://example.com/demo",
                    "capture_strategy": "docs_redhat_html_single_v1",
                    "acquisition_step": "capture",
                    "normalization_step": "normalize",
                    "derivation_step": "derive",
                    "notes": [],
                    "canonical_model": "canonical_book_v1",
                    "source_view_strategy": "source_view_first",
                    "retrieval_derivation": "chunks_from_canonical_sections",
                },
                "capture_artifact_path": "",
                "capture_content_type": "",
                "capture_byte_size": 0,
                "capture_error": "",
                "canonical_book_path": str(book_dir / "dtb-demo.json"),
                "normalized_section_count": 1,
                "normalize_error": "",
            }
            (draft_dir / "dtb-demo.json").write_text(
                json.dumps(draft_payload, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (book_dir / "dtb-demo.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "canonical_book_v1",
                        "book_slug": "demo-guide",
                        "title": "데모 가이드",
                        "source_type": "web",
                        "source_uri": "https://example.com/demo",
                        "language_hint": "ko",
                        "source_view_strategy": "normalized_sections_v1",
                        "retrieval_derivation": "chunks_from_canonical_sections",
                        "sections": [
                            {
                                "ordinal": 1,
                                "section_key": "demo-guide:events",
                                "heading": "이벤트 확인",
                                "section_level": 2,
                                "section_path": ["문제 해결", "이벤트 확인"],
                                "section_path_label": "문제 해결 > 이벤트 확인",
                                "anchor": "events",
                                "viewer_path": "/playbooks/customer-packs/dtb-demo/index.html#events",
                                "source_url": "https://example.com/demo",
                                "text": "이벤트 확인 절차",
                                "block_kinds": ["paragraph"],
                            }
                        ],
                        "notes": [],
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
                    chunk_id="dtb-demo:demo-guide:events",
                    book_slug="demo-guide",
                    section="이벤트 확인",
                    anchor="events",
                    source_url="https://example.com/demo",
                    viewer_path="/playbooks/customer-packs/dtb-demo/index.html#events",
                    excerpt="이벤트 확인 절차",
                ),
            )

        self.assertEqual("데모 가이드", payload["book_title"])
        self.assertEqual("문제 해결 > 이벤트 확인", payload["section_path_label"])
        self.assertEqual("데모 가이드 · 문제 해결 > 이벤트 확인", payload["source_label"])
        self.assertTrue(payload["section_match_exact"])

    def test_internal_customer_pack_viewer_html_uses_pdf_summary_for_pdf_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "customer_packs" / "drafts"
            book_dir = root / "artifacts" / "customer_packs" / "books"
            draft_dir.mkdir(parents=True)
            book_dir.mkdir(parents=True)

            (draft_dir / "dtb-pdf.json").write_text(
                json.dumps(
                    {
                        "draft_id": "dtb-pdf",
                        "status": "normalized",
                        "created_at": "2026-04-06T00:00:00Z",
                        "updated_at": "2026-04-06T00:00:00Z",
                        "request": {
                            "source_type": "pdf",
                            "uri": "/tmp/demo.pdf",
                            "title": "데모 PDF",
                            "language_hint": "ko",
                        },
                        "plan": {
                            "book_slug": "demo-pdf",
                            "title": "데모 PDF",
                            "source_type": "pdf",
                            "source_uri": "/tmp/demo.pdf",
                            "source_collection": "uploaded",
                            "pack_id": "openshift-4-16-custom",
                            "pack_label": "OpenShift 4.16 Custom Pack",
                            "inferred_product": "openshift",
                            "inferred_version": "4.16",
                            "acquisition_uri": "/tmp/demo.pdf",
                            "capture_strategy": "pdf_text_extract_v1",
                            "acquisition_step": "capture",
                            "normalization_step": "normalize",
                            "derivation_step": "derive",
                            "notes": [],
                            "canonical_model": "canonical_book_v1",
                            "source_view_strategy": "source_view_first",
                            "retrieval_derivation": "chunks_from_canonical_sections",
                        },
                        "capture_artifact_path": "/tmp/demo.pdf",
                        "capture_content_type": "application/pdf",
                        "capture_byte_size": 12,
                        "capture_error": "",
                        "canonical_book_path": str(book_dir / "dtb-pdf.json"),
                        "normalized_section_count": 1,
                        "normalize_error": "",
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )
            (book_dir / "dtb-pdf.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "canonical_book_v1",
                        "book_slug": "demo-pdf",
                        "title": "데모 PDF",
                        "source_type": "pdf",
                        "source_uri": "/tmp/demo.pdf",
                        "language_hint": "ko",
                        "source_view_strategy": "normalized_sections_v1",
                        "retrieval_derivation": "chunks_from_canonical_sections",
                        "sections": [
                            {
                                "ordinal": 1,
                                "section_key": "demo-pdf:short-a",
                                "heading": "온프레미스",
                                "section_level": 1,
                                "section_path": ["Page 1", "온프레미스"],
                                "section_path_label": "Page 1 > 온프레미스",
                                "anchor": "short-a",
                                "viewer_path": "/playbooks/customer-packs/dtb-pdf/index.html#short-a",
                                "source_url": "/tmp/demo.pdf",
                                "text": "온프레미스",
                                "block_kinds": ["paragraph"],
                            },
                        ],
                        "notes": [],
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            viewer_html = _internal_customer_pack_viewer_html(root, "/playbooks/customer-packs/dtb-pdf/index.html#short-a")

        self.assertIsNotNone(viewer_html)
        assert viewer_html is not None
        self.assertIn("업로드 PDF를 canonical section으로 정리한 내부 review view입니다.", viewer_html)
