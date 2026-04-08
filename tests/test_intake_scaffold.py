from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.intake import (
    DocSourceRequest,
    DocToBookDraftStore,
    DocToBookPlanner,
    resolve_pdf_capture,
    resolve_web_capture_url,
)
from play_book_studio.intake.capture.service import DocToBookCaptureService
from play_book_studio.intake.normalization.pdf import PdfOutlineEntry, _normalize_page_text, extract_pdf_pages
from play_book_studio.intake.normalization.service import (
    DocToBookNormalizeService,
    _build_pdf_rows_from_docling_markdown,
    _prepare_pdf_page_text,
    _segment_pdf_page,
)
from play_book_studio.intake.service import evaluate_canonical_book_quality


class DocToBookScaffoldTests(unittest.TestCase):
    def test_web_source_prefers_html_single_capture_language(self) -> None:
        draft = DocToBookPlanner().plan(
            DocSourceRequest(
                source_type="web",
                uri="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
            )
        )

        self.assertEqual("web", draft.source_type)
        self.assertEqual(
            "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/nodes/index",
            draft.acquisition_uri,
        )
        self.assertEqual("uploaded", draft.source_collection)
        self.assertEqual("openshift-4-20-custom", draft.pack_id)
        self.assertEqual("OpenShift 4.20 Custom Pack", draft.pack_label)
        self.assertEqual("openshift", draft.inferred_product)
        self.assertEqual("4.20", draft.inferred_version)
        self.assertEqual("docs_redhat_html_single_v1", draft.capture_strategy)
        self.assertIn("html-single", draft.acquisition_step)
        self.assertIn("source-view document first", draft.derivation_step)

    def test_pdf_source_keeps_structure_recovery_note(self) -> None:
        draft = DocToBookPlanner().plan(
            DocSourceRequest(
                source_type="pdf",
                uri="/tmp/ocp-troubleshooting-guide.pdf",
            )
        )

        self.assertEqual("pdf", draft.source_type)
        self.assertEqual("ocp-troubleshooting-guide", draft.book_slug)
        self.assertEqual("/tmp/ocp-troubleshooting-guide.pdf", draft.acquisition_uri)
        self.assertEqual("uploaded", draft.source_collection)
        self.assertEqual("openshift-uploaded-custom", draft.pack_id)
        self.assertEqual("OpenShift Custom Pack", draft.pack_label)
        self.assertEqual("openshift", draft.inferred_product)
        self.assertEqual("unknown", draft.inferred_version)
        self.assertEqual("pdf_text_extract_v1", draft.capture_strategy)
        self.assertIn("PDF pages", draft.acquisition_step)
        self.assertTrue(any("Page numbers" in note for note in draft.notes))

    def test_resolve_web_capture_url_converts_docs_redhat_html_book_to_html_single(self) -> None:
        capture_url, strategy = resolve_web_capture_url(
            "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes"
        )

        self.assertEqual(
            "https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/nodes/index",
            capture_url,
        )
        self.assertEqual("docs_redhat_html_single_v1", strategy)

    def test_resolve_pdf_capture_keeps_uri_and_marks_pdf_strategy(self) -> None:
        capture_uri, strategy = resolve_pdf_capture("/tmp/openshift-guide.pdf")

        self.assertEqual("/tmp/openshift-guide.pdf", capture_uri)
        self.assertEqual("pdf_text_extract_v1", strategy)

    def test_docling_markdown_builds_structured_pdf_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            request = DocSourceRequest(
                source_type="pdf",
                uri="/tmp/openshift-guide.pdf",
                title="OpenShift_Container_Platform-4.16-Getting_started-ko-KR",
            )
            record = DocToBookDraftStore(Path(tmpdir)).create(request)
            markdown = """## OpenShift Container Platform 4.16
## Legal Notice
copyright body
## 1 장 . KUBERNETES 개요
Kubernetes overview body
## 1.1. KUBERNETES 구성 요소
Component body
## 2 장 . OPENSHIFT CONTAINER PLATFORM 개요
OpenShift overview body
## 2.1. OPENSHIFT CONTAINER PLATFORM 의 일반 용어집
Glossary body
## Kubernetes
Glossary term body
"""
            rows = _build_pdf_rows_from_docling_markdown(markdown, record)

        self.assertEqual(
            [
                "1 장 . KUBERNETES 개요",
                "1.1. KUBERNETES 구성 요소",
                "2 장 . OPENSHIFT CONTAINER PLATFORM 개요",
                "2.1. OPENSHIFT CONTAINER PLATFORM 의 일반 용어집",
                "Kubernetes",
            ],
            [row["heading"] for row in rows],
        )
        self.assertEqual(["1 장 . KUBERNETES 개요"], rows[0]["section_path"])
        self.assertEqual(
            ["2 장 . OPENSHIFT CONTAINER PLATFORM 개요", "2.1. OPENSHIFT CONTAINER PLATFORM 의 일반 용어집", "Kubernetes"],
            rows[4]["section_path"],
        )
        self.assertIn("Kubernetes overview body", rows[0]["text"])
        self.assertNotIn("Legal Notice", "\n".join(str(row["text"]) for row in rows))

    def test_docling_aux_headings_are_inlined_into_parent_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            request = DocSourceRequest(
                source_type="pdf",
                uri="/tmp/guide.pdf",
                title="Guide",
            )
            record = DocToBookDraftStore(Path(tmpdir)).create(request)
            markdown = """## 3.2. 웹 콘솔에 로그인
로그인 안내
## 사전 요구 사항
권한이 있어야 합니다.
## 프로세스
1. 로그인합니다.
## 추가 리소스
더 읽기
"""
            rows = _build_pdf_rows_from_docling_markdown(markdown, record)

        self.assertEqual(1, len(rows))
        self.assertEqual("3.2. 웹 콘솔에 로그인", rows[0]["heading"])
        self.assertIn("### 사전 요구 사항", rows[0]["text"])
        self.assertIn("### 프로세스", rows[0]["text"])
        self.assertIn("### 추가 리소스", rows[0]["text"])

    def test_quality_review_detects_pdf_footer_contamination(self) -> None:
        long_body = "충분히 긴 본문 문장입니다. " * 4
        payload = {
            "sections": [
                {"heading": "1.1. section", "text": f"{long_body}\n\n1 장 . 설치 준비\n\n계속"},
                {"heading": "1.2. section", "text": f"{long_body}\n\n1 장 . 설치 준비\n\n계속"},
                {"heading": "1.3. section", "text": long_body},
                {"heading": "1.4. section", "text": long_body},
                {"heading": "1.5. section", "text": long_body},
                {"heading": "1.6. section", "text": long_body},
                {"heading": "1.7. section", "text": long_body},
                {"heading": "1.8. section", "text": long_body},
            ]
        }
        quality = evaluate_canonical_book_quality(payload)
        self.assertEqual("review", quality["quality_status"])
        self.assertIn("chapter_footer_contamination", quality["quality_flags"])

    def test_build_canonical_book_from_normalized_rows_preserves_source_view_fields(self) -> None:
        planner = DocToBookPlanner()
        book = planner.build_canonical_book(
            [
                {
                    "book_slug": "architecture",
                    "book_title": "아키텍처",
                    "heading": "개요",
                    "section_level": 1,
                    "section_path": ["개요"],
                    "anchor": "overview",
                    "source_url": "https://example.com/architecture",
                    "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#overview",
                    "text": "설명 문단\n\n[CODE]\noc get nodes\n[/CODE]",
                },
                {
                    "book_slug": "architecture",
                    "book_title": "아키텍처",
                    "heading": "컨트롤 플레인",
                    "section_level": 2,
                    "section_path": ["개요", "컨트롤 플레인"],
                    "anchor": "control-plane",
                    "source_url": "https://example.com/architecture",
                    "viewer_path": "/docs/ocp/4.20/ko/architecture/index.html#control-plane",
                    "text": "구성 요소 표\n\n[TABLE]\n이름 | 역할\napi-server | 제어\n[/TABLE]",
                },
            ]
        )

        self.assertEqual("canonical_book_v1", book.canonical_model)
        self.assertEqual("uploaded", book.source_collection)
        self.assertEqual("custom-uploaded-custom", book.pack_id)
        self.assertEqual("User Custom Pack", book.pack_label)
        self.assertEqual("unknown", book.inferred_product)
        self.assertEqual("unknown", book.inferred_version)
        self.assertEqual("normalized_sections_v1", book.source_view_strategy)
        self.assertEqual("chunks_from_canonical_sections", book.retrieval_derivation)
        self.assertEqual(2, len(book.sections))
        self.assertEqual("architecture:overview", book.sections[0].section_key)
        self.assertEqual("개요", book.sections[0].section_path_label)
        self.assertEqual(("paragraph", "code"), book.sections[0].block_kinds)
        self.assertEqual("개요 > 컨트롤 플레인", book.sections[1].section_path_label)
        self.assertEqual(("paragraph", "table"), book.sections[1].block_kinds)

    def test_draft_store_persists_and_lists_doc_to_book_requests(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            store = DocToBookDraftStore(root)

            created = store.create(
                DocSourceRequest(
                    source_type="web",
                    uri="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                    title="노드 가이드",
                )
            )
            loaded = store.get(created.draft_id)
            listed = store.list()

        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(created.draft_id, loaded.draft_id)
        self.assertEqual("planned", loaded.status)
        self.assertEqual("노드 가이드", loaded.plan.title)
        self.assertEqual("docs_redhat_html_single_v1", loaded.plan.capture_strategy)
        self.assertEqual(1, len(listed))
        self.assertEqual(created.draft_id, listed[0].draft_id)

    def test_draft_store_backfills_pack_metadata_for_legacy_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            drafts_dir = root / "artifacts" / "doc_to_book" / "drafts"
            drafts_dir.mkdir(parents=True)
            (drafts_dir / "dtb-legacy.json").write_text(
                json.dumps(
                    {
                        "draft_id": "dtb-legacy",
                        "status": "planned",
                        "created_at": "2026-04-06T00:00:00Z",
                        "updated_at": "2026-04-06T00:00:00Z",
                        "request": {
                            "source_type": "pdf",
                            "uri": "/tmp/OpenShift_Container_Platform-4.16-demo.pdf",
                            "title": "",
                            "language_hint": "ko",
                        },
                        "plan": {
                            "book_slug": "openshift-container-platform-4-16-demo",
                            "title": "OpenShift_Container_Platform-4.16-demo",
                            "source_type": "pdf",
                            "source_uri": "/tmp/OpenShift_Container_Platform-4.16-demo.pdf",
                            "acquisition_uri": "/tmp/OpenShift_Container_Platform-4.16-demo.pdf",
                            "capture_strategy": "pdf_text_extract_v1",
                            "acquisition_step": "legacy",
                            "normalization_step": "legacy",
                            "derivation_step": "legacy",
                            "notes": [],
                        },
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            legacy = DocToBookDraftStore(root).get("dtb-legacy")

        self.assertIsNotNone(legacy)
        assert legacy is not None
        self.assertEqual("uploaded", legacy.plan.source_collection)
        self.assertEqual("openshift-4-16-custom", legacy.plan.pack_id)
        self.assertEqual("OpenShift 4.16 Custom Pack", legacy.plan.pack_label)
        self.assertEqual("openshift", legacy.plan.inferred_product)
        self.assertEqual("4.16", legacy.plan.inferred_version)

    def test_capture_service_fetches_web_html_into_capture_artifact(self) -> None:
        class _FakeResponse:
            encoding = "utf-8"
            apparent_encoding = "utf-8"
            text = "<html><body><h1>Nodes</h1></body></html>"

            def raise_for_status(self) -> None:
                return None

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            service = DocToBookCaptureService(root)
            with patch("play_book_studio.ingestion.collector.requests.get", return_value=_FakeResponse()):
                record = service.capture(
                    request=DocSourceRequest(
                        source_type="web",
                        uri="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                        title="노드",
                    )
                )

            artifact_path = Path(record.capture_artifact_path)
            content = artifact_path.read_text(encoding="utf-8")
            self.assertEqual("captured", record.status)
            self.assertTrue(artifact_path.exists())
            self.assertEqual("text/html; charset=utf-8", record.capture_content_type)
            self.assertIn("<h1>Nodes</h1>", content)

    def test_capture_service_reads_uploaded_local_html_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            local_html = root / "uploaded.html"
            local_html.write_text("<html><body><h1>Uploaded</h1></body></html>", encoding="utf-8")

            service = DocToBookCaptureService(root)
            record = service.capture(
                request=DocSourceRequest(
                    source_type="web",
                    uri=str(local_html),
                    title="업로드 HTML",
                )
            )

            artifact_path = Path(record.capture_artifact_path)
            content = artifact_path.read_text(encoding="utf-8")
            self.assertEqual("captured", record.status)
            self.assertTrue(artifact_path.exists())
            self.assertIn("<h1>Uploaded</h1>", content)

    def test_capture_service_rejects_pdf_file_when_web_source_type_is_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_pdf = root / "wrong-source.pdf"
            source_pdf.write_bytes(b"%PDF-1.4 sample")

            service = DocToBookCaptureService(root)
            with self.assertRaisesRegex(ValueError, "선택한 파일은 PDF입니다"):
                service.capture(
                    request=DocSourceRequest(
                        source_type="web",
                        uri=str(source_pdf),
                        title="잘못된 소스 타입",
                    )
                )

    def test_capture_service_copies_pdf_into_capture_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_pdf = root / "guide.pdf"
            source_pdf.write_bytes(b"%PDF-1.4 sample")

            service = DocToBookCaptureService(root)
            record = service.capture(
                request=DocSourceRequest(
                    source_type="pdf",
                    uri=str(source_pdf),
                    title="가이드",
                )
            )

            artifact_path = Path(record.capture_artifact_path)
            self.assertEqual("captured", record.status)
            self.assertTrue(artifact_path.exists())
            self.assertEqual("application/pdf", record.capture_content_type)
            self.assertEqual(b"%PDF-1.4 sample", artifact_path.read_bytes())

    def test_normalize_service_builds_canonical_book_from_captured_web_html(self) -> None:
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
                    <pre>oc get events -n openshift-config</pre>
                  </article>
                </main>
              </body>
            </html>
            """

            def raise_for_status(self) -> None:
                return None

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            capture_service = DocToBookCaptureService(root)
            with patch("play_book_studio.ingestion.collector.requests.get", return_value=_FakeResponse()):
                captured = capture_service.capture(
                    request=DocSourceRequest(
                        source_type="web",
                        uri="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html/nodes",
                        title="노드 운영",
                    )
                )

            normalized = DocToBookNormalizeService(root).normalize(draft_id=captured.draft_id)
            canonical_path = Path(normalized.canonical_book_path)
            payload = canonical_path.read_text(encoding="utf-8")
            canonical_exists = canonical_path.exists()

        self.assertEqual("normalized", normalized.status)
        self.assertTrue(canonical_exists)
        self.assertEqual(2, normalized.normalized_section_count)
        self.assertIn('"canonical_model": "canonical_book_v1"', payload)
        self.assertIn('"viewer_path": "/docs/intake/', payload)
        self.assertIn('oc get events -n openshift-config', payload)

    def test_normalize_service_builds_canonical_book_from_captured_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_pdf = root / "runbook.pdf"
            source_pdf.write_bytes(b"%PDF-1.4 sample")

            captured = DocToBookCaptureService(root).capture(
                request=DocSourceRequest(
                    source_type="pdf",
                    uri=str(source_pdf),
                    title="유지보수 런북",
                )
            )

            with patch(
                "play_book_studio.intake.normalization.service.extract_pdf_pages",
                return_value=[
                    "Overview\n\n이 문서는 점검 전환 순서를 설명합니다.\n\nSafety Switch\n\ndemo.cywell.io/maintenance=nebula-drain",
                    "Procedure\n\n1. worker-0에 annotation을 설정합니다.\n\nRollback\n\nannotation을 제거합니다.",
                ],
            ):
                normalized = DocToBookNormalizeService(root).normalize(draft_id=captured.draft_id)

            canonical_path = Path(normalized.canonical_book_path)
            payload = canonical_path.read_text(encoding="utf-8")
            canonical_exists = canonical_path.exists()

        self.assertEqual("normalized", normalized.status)
        self.assertTrue(canonical_exists)
        self.assertGreaterEqual(normalized.normalized_section_count, 3)
        self.assertIn('"source_type": "pdf"', payload)
        self.assertIn('"viewer_path": "/docs/intake/', payload)
        self.assertIn('demo.cywell.io/maintenance=nebula-drain', payload)

    def test_normalize_service_prefers_pdf_outline_for_section_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_pdf = root / "outlined.pdf"
            source_pdf.write_bytes(b"%PDF-1.4 sample")

            captured = DocToBookCaptureService(root).capture(
                request=DocSourceRequest(
                    source_type="pdf",
                    uri=str(source_pdf),
                    title="아웃라인 PDF",
                )
            )

            with patch(
                "play_book_studio.intake.normalization.service.extract_pdf_pages",
                return_value=[
                    "OpenShift Container Platform 4.16 시작하기 2",
                    "1 장 . KUBERNETES 개요 Kubernetes 는 컨테이너 오케스트레이션 툴입니다. 1.1. KUBERNETES 구성 요소 kube-apiserver 설명",
                    "1.2. KUBERNETES 리소스 Operator 설명 2 장 . OPENSHIFT CONTAINER PLATFORM 개요 OpenShift 설명",
                ],
            ), patch(
                "play_book_studio.intake.normalization.service.extract_pdf_outline",
                return_value=[
                    PdfOutlineEntry(level=1, title="1장. KUBERNETES 개요"),
                    PdfOutlineEntry(level=2, title="1.1. KUBERNETES 구성 요소"),
                    PdfOutlineEntry(level=2, title="1.2. KUBERNETES 리소스"),
                    PdfOutlineEntry(level=1, title="2장. OPENSHIFT CONTAINER PLATFORM 개요"),
                ],
            ):
                normalized = DocToBookNormalizeService(root).normalize(draft_id=captured.draft_id)

            payload = json.loads(Path(normalized.canonical_book_path).read_text(encoding="utf-8"))

        self.assertEqual("normalized", normalized.status)
        headings = [section["heading"] for section in payload["sections"]]
        self.assertEqual(
            [
                "1장. KUBERNETES 개요",
                "1.1. KUBERNETES 구성 요소",
                "1.2. KUBERNETES 리소스",
                "2장. OPENSHIFT CONTAINER PLATFORM 개요",
            ],
            headings,
        )
        self.assertEqual(["1장. KUBERNETES 개요"], payload["sections"][0]["section_path"])
        self.assertEqual(
            ["1장. KUBERNETES 개요", "1.1. KUBERNETES 구성 요소"],
            payload["sections"][1]["section_path"],
        )

    def test_extract_pdf_pages_rejects_binary_pdf_stream_garbage(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_pdf = Path(tmpdir) / "garbage.pdf"
            source_pdf.write_bytes(
                b"%PDF-1.4\n"
                b"1 0 obj\n<< /Type /Page >>\nstream\n"
                b"(OpenShift Container Platform 4.16 t\x04\xd2\xb8 0\x18 $X)\n"
                b"endstream\nendobj\nxref\n"
            )

            with self.assertRaisesRegex(ValueError, "PDF 텍스트를 추출하지 못했습니다"):
                extract_pdf_pages(source_pdf)

    def test_normalize_page_text_repairs_fragmented_linebreaks(self) -> None:
        normalized = _normalize_page_text(
            "OpenShift Container Platform 4.16\n에이전트\n에이전트\n \n기반\n기반\n \n설치\n설치"
        )

        self.assertEqual("OpenShift Container Platform 4.16 에이전트 기반 설치", normalized)

    def test_prepare_pdf_page_text_removes_cover_prefix_and_splits_markers(self) -> None:
        prepared = _prepare_pdf_page_text(
            "OpenShift Container Platform 4.16 에이전트 기반 설치 관리자를 사용하여 온프레미스 클러스터 설치 3 "
            "1 장 . 에이전트 기반 설치 관리자를 사용하여 설치 준비 "
            "1.1. 에이전트 기반 설치 관리자 정보 "
            "1.2. 에이전트 기반 설치 관리자 이해"
        )

        self.assertTrue(prepared.startswith("1 장 ."))
        self.assertIn("\n\n1.1.", prepared)
        self.assertIn("\n\n1.2.", prepared)

    def test_segment_pdf_page_uses_numbered_markers_as_sections(self) -> None:
        sections = _segment_pdf_page(
            "1 장 . 에이전트 기반 설치 관리자를 사용하여 설치 준비 "
            "1.1. 에이전트 기반 설치 관리자 정보 에이전트 기반 설치 방법은 원하는 방식으로 진행합니다. "
            "1.2. 에이전트 기반 설치 관리자 이해 지원 서비스 흐름을 설명합니다."
        )

        self.assertGreaterEqual(len(sections), 3)
        self.assertTrue(sections[0][0].startswith("1 장"))
        self.assertTrue(sections[1][0].startswith("1.1."))
        self.assertTrue(sections[2][0].startswith("1.2."))

    def test_normalize_service_repairs_excessively_fragmented_pdf_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_pdf = root / "fragmented.pdf"
            source_pdf.write_bytes(b"%PDF-1.4 sample")

            captured = DocToBookCaptureService(root).capture(
                request=DocSourceRequest(
                    source_type="pdf",
                    uri=str(source_pdf),
                    title="파편화 PDF",
                )
            )

            fragmented_pages = ["\n".join(["에이전트", "기반", "설치", "관리자를", "사용하여"] * 120)] * 50
            with patch(
                "play_book_studio.intake.normalization.service.extract_pdf_pages",
                return_value=fragmented_pages,
            ):
                normalized = DocToBookNormalizeService(root).normalize(draft_id=captured.draft_id)

        self.assertEqual("normalized", normalized.status)
        self.assertLessEqual(normalized.normalized_section_count, 60)


if __name__ == "__main__":
    unittest.main()
