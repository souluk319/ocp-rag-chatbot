from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_app_ui import *  # noqa: F401,F403

class TestAppIntakeUi(unittest.TestCase):
    def test_build_doc_to_book_plan_returns_resolved_web_capture(self) -> None:
        payload = _build_doc_to_book_plan(
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

    def test_build_doc_to_book_plan_rejects_unknown_source_type(self) -> None:
        with self.assertRaisesRegex(ValueError, "source_type은 web 또는 pdf여야 합니다."):
            _build_doc_to_book_plan({"source_type": "docx", "uri": "/tmp/a.docx"})

    def test_create_doc_to_book_draft_persists_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = _create_doc_to_book_draft(
                root,
                {
                    "source_type": "web",
                    "uri": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                    "title": "노드 운영 가이드",
                },
            )
            loaded = _load_doc_to_book_draft(root, str(created["draft_id"]))

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

    def test_upload_doc_to_book_draft_persists_uploaded_pdf_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = _upload_doc_to_book_draft(
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
            loaded = _load_doc_to_book_draft(root, str(created["draft_id"]))
            uploaded_bytes = uploaded_path.read_bytes()

        self.assertEqual("pdf", created["request"]["source_type"])
        self.assertEqual("업로드 가이드", created["plan"]["title"])
        self.assertIsNotNone(loaded)
        self.assertEqual(str(uploaded_path), loaded["request"]["uri"])
        self.assertEqual("guide.pdf", loaded["uploaded_file_name"])
        self.assertEqual(str(uploaded_path), loaded["uploaded_file_path"])
        self.assertEqual(b"%PDF-1.4 sample", uploaded_bytes)

    def test_list_doc_to_book_drafts_returns_saved_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_doc_to_book_draft(
                root,
                {
                    "source_type": "pdf",
                    "uri": "/tmp/openshift-troubleshooting.pdf",
                    "title": "트러블슈팅 핸드북",
                },
            )
            payload = _list_doc_to_book_drafts(root)

        self.assertEqual(1, len(payload["drafts"]))
        self.assertEqual("트러블슈팅 핸드북", payload["drafts"][0]["title"])
        self.assertEqual("pdf_text_extract_v1", payload["drafts"][0]["capture_strategy"])

    def test_capture_doc_to_book_draft_fetches_and_serves_web_artifact(self) -> None:
        class _FakeResponse:
            encoding = "utf-8"
            apparent_encoding = "utf-8"
            text = "<html><body>captured web source</body></html>"

            def raise_for_status(self) -> None:
                return None

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with patch("play_book_studio.ingestion.collector.requests.get", return_value=_FakeResponse()):
                created = _capture_doc_to_book_draft(
                    root,
                    {
                        "source_type": "web",
                        "uri": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                        "title": "노드 운영 가이드",
                    },
                )
            served = _load_doc_to_book_capture(root, str(created["draft_id"]))

        self.assertEqual("captured", created["status"])
        self.assertIsNotNone(served)
        assert served is not None
        body, content_type = served
        self.assertEqual("text/html; charset=utf-8", content_type)
        self.assertIn("captured web source", body.decode("utf-8"))

    def test_normalize_doc_to_book_draft_builds_internal_study_view(self) -> None:
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
                captured = _capture_doc_to_book_draft(
                    root,
                    {
                        "source_type": "web",
                        "uri": "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                        "title": "노드 운영 가이드",
                    },
                )
            normalized = _normalize_doc_to_book_draft(root, {"draft_id": str(captured["draft_id"])})
            book = _load_doc_to_book_book(root, str(captured["draft_id"]))
            viewer_html = _internal_doc_to_book_viewer_html(
                root,
                f"/docs/intake/{captured['draft_id']}/index.html#events",
            )

        self.assertEqual("normalized", normalized["status"])
        self.assertIsNotNone(book)
        assert book is not None
        self.assertEqual(str(captured["draft_id"]), book["draft_id"])
        self.assertEqual(2, len(book["sections"]))
        self.assertEqual("events", book["sections"][1]["anchor"])
        self.assertIn("/docs/intake/", book["target_viewer_path"])
        self.assertEqual(f"/api/doc-to-book/captured?draft_id={captured['draft_id']}", book["source_origin_url"])
        self.assertEqual("ready", book["quality_status"])
        self.assertIsNotNone(viewer_html)
        assert viewer_html is not None
        self.assertIn("Doc-to-Book Study Viewer", viewer_html)
        self.assertIn("이벤트 확인", viewer_html)
        self.assertIn("capture된 웹 문서를 canonical section으로 정리한 내부 study view입니다.", viewer_html)

    def test_doc_to_book_meta_prefers_captured_source_url_and_quality(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "doc_to_book" / "drafts"
            book_dir = root / "artifacts" / "doc_to_book" / "books"
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
                                "viewer_path": "/docs/intake/dtb-review/index.html#page-summary",
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
                                "viewer_path": "/docs/intake/dtb-review/index.html#short-a",
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
                                "viewer_path": "/docs/intake/dtb-review/index.html#short-b",
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

            meta = _doc_to_book_meta_for_viewer_path(root, "/docs/intake/dtb-review/index.html#short-a")

        self.assertIsNotNone(meta)
        assert meta is not None
        self.assertEqual("/api/doc-to-book/captured?draft_id=dtb-review", meta["source_url"])
        self.assertEqual("review", meta["quality_status"])
        self.assertIn("정규화 품질 검토", meta["quality_summary"])
        self.assertTrue(meta["section_match_exact"])

    def test_doc_to_book_meta_marks_fallback_when_anchor_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "doc_to_book" / "drafts"
            book_dir = root / "artifacts" / "doc_to_book" / "books"
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
                                "viewer_path": "/docs/intake/dtb-review/index.html#short-a",
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

            meta = _doc_to_book_meta_for_viewer_path(root, "/docs/intake/dtb-review/index.html#missing")

        self.assertIsNotNone(meta)
        assert meta is not None
        self.assertFalse(meta["section_match_exact"])

    def test_serialize_citation_enriches_doc_to_book_source_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "doc_to_book" / "drafts"
            book_dir = root / "artifacts" / "doc_to_book" / "books"
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
                                "viewer_path": "/docs/intake/dtb-demo/index.html#events",
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
                    viewer_path="/docs/intake/dtb-demo/index.html#events",
                    excerpt="이벤트 확인 절차",
                ),
            )

        self.assertEqual("데모 가이드", payload["book_title"])
        self.assertEqual("문제 해결 > 이벤트 확인", payload["section_path_label"])
        self.assertEqual("데모 가이드 · 문제 해결 > 이벤트 확인", payload["source_label"])
        self.assertTrue(payload["section_match_exact"])

    def test_internal_doc_to_book_viewer_html_uses_pdf_summary_for_pdf_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            draft_dir = root / "artifacts" / "doc_to_book" / "drafts"
            book_dir = root / "artifacts" / "doc_to_book" / "books"
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
                                "viewer_path": "/docs/intake/dtb-pdf/index.html#short-a",
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

            viewer_html = _internal_doc_to_book_viewer_html(root, "/docs/intake/dtb-pdf/index.html#short-a")

        self.assertIsNotNone(viewer_html)
        assert viewer_html is not None
        self.assertIn("capture된 PDF를 canonical section으로 정리한 내부 study view입니다.", viewer_html)
