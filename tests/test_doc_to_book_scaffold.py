from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_doc_to_book import (
    DocSourceRequest,
    DocToBookDraftStore,
    DocToBookPlanner,
    resolve_pdf_capture,
    resolve_web_capture_url,
)
from ocp_doc_to_book.ingestion.capture import DocToBookCaptureService
from ocp_doc_to_book.normalization.service import DocToBookNormalizeService


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
            with patch("ocp_rag_part1.collector.requests.get", return_value=_FakeResponse()):
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
            with patch("ocp_rag_part1.collector.requests.get", return_value=_FakeResponse()):
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


if __name__ == "__main__":
    unittest.main()
