from __future__ import annotations

import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.app.intake_api import customer_pack_request_from_payload
from play_book_studio.intake.capture.service import CustomerPackCaptureService
from play_book_studio.intake.models import DocSourceRequest
from play_book_studio.intake.normalization.pdf import extract_pdf_pages
from play_book_studio.intake.planner import build_customer_pack_support_matrix


class IntakeSourceTruthfulnessTests(unittest.TestCase):
    def test_customer_pack_request_from_payload_rejects_unsupported_source_types(self) -> None:
        for source_type in ("png", "jpg", "jpeg", "markdown", "csv"):
            with self.subTest(source_type=source_type):
                with self.assertRaisesRegex(
                    ValueError,
                    "source_type은 web, pdf, md, asciidoc, txt, docx, pptx, xlsx, image 중 하나여야 합니다.",
                ):
                    customer_pack_request_from_payload(
                        {
                            "source_type": source_type,
                            "uri": f"/tmp/sample.{source_type}",
                            "title": "sample",
                        }
                    )

    def test_support_matrix_reports_truthful_statuses(self) -> None:
        matrix = build_customer_pack_support_matrix().to_dict()
        entries = {
            str(entry.get("format_id") or ""): dict(entry)
            for entry in matrix.get("entries") or []
            if isinstance(entry, dict)
        }

        self.assertEqual("customer_pack_format_support_matrix_v1", matrix["matrix_version"])
        self.assertEqual("supported", entries["web_html"]["support_status"])
        self.assertEqual("supported", entries["pdf_text"]["support_status"])
        self.assertEqual("staged", entries["pdf_scan_ocr"]["support_status"])
        self.assertEqual("supported", entries["docx"]["support_status"])
        self.assertEqual("supported", entries["pptx"]["support_status"])
        self.assertEqual("supported", entries["xlsx"]["support_status"])
        self.assertEqual("staged", entries["image_ocr"]["support_status"])
        self.assertEqual("rejected", entries["csv"]["support_status"])
        self.assertTrue(entries["pdf_text"]["ocr"]["enabled"])
        self.assertFalse(entries["web_html"]["ocr"]["enabled"])
        self.assertTrue(entries["pdf_scan_ocr"]["ocr"]["required"])
        self.assertIn("manual review", entries["image_ocr"]["review_rule"])

    def test_customer_pack_request_from_payload_accepts_office_and_image_source_types(self) -> None:
        for source_type in ("docx", "pptx", "xlsx", "image"):
            with self.subTest(source_type=source_type):
                request = customer_pack_request_from_payload(
                    {
                        "source_type": source_type,
                        "uri": f"/tmp/sample.{source_type}",
                        "title": "sample",
                    }
                )
                self.assertEqual(source_type, request.source_type)

    def test_capture_service_accepts_local_markdown_when_declared_as_web_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = root / "guide.md"
            source_path.write_text("# heading\n\nplaybook body", encoding="utf-8")

            record = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(
                    source_type="web",
                    uri=str(source_path),
                    title="markdown guide",
                )
            )

            captured_path = Path(record.capture_artifact_path)
            self.assertEqual("captured", record.status)
            self.assertTrue(captured_path.exists())
            self.assertTrue(record.capture_content_type.startswith("text/"))
            self.assertIn("playbook body", captured_path.read_text(encoding="utf-8"))

    def test_capture_service_rejects_binary_docx_when_declared_as_web_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = root / "guide.docx"
            source_path.write_bytes(b"PK\x03\x04fake-docx")

            with self.assertRaisesRegex(ValueError, "web capture로 읽기 어려운 파일 형식입니다"):
                CustomerPackCaptureService(root).capture(
                    request=DocSourceRequest(
                        source_type="web",
                        uri=str(source_path),
                        title="docx guide",
                    )
                )

    def test_capture_service_rejects_non_utf8_text_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = root / "guide.txt"
            source_path.write_bytes(b"\xff\xfe\x00\x00broken")

            with self.assertRaisesRegex(
                ValueError,
                "text source는 UTF-8 텍스트로 읽을 수 있는 Markdown/AsciiDoc/Text 파일이어야 합니다.",
            ):
                CustomerPackCaptureService(root).capture(
                    request=DocSourceRequest(
                        source_type="txt",
                        uri=str(source_path),
                        title="text guide",
                    )
                )

    def test_capture_service_rejects_binary_docx_when_declared_as_text_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = root / "guide.docx"
            source_path.write_bytes(b"PK\x03\x04fake-docx")

            with self.assertRaisesRegex(
                ValueError,
                "text source는 UTF-8 텍스트로 읽을 수 있는 Markdown/AsciiDoc/Text 파일이어야 합니다.",
            ):
                CustomerPackCaptureService(root).capture(
                    request=DocSourceRequest(
                        source_type="txt",
                        uri=str(source_path),
                        title="docx guide",
                    )
                )

    def test_capture_service_accepts_binary_image_when_declared_as_image_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = root / "guide.png"
            source_path.write_bytes(b"\x89PNG\r\n\x1a\nfake")

            record = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(
                    source_type="image",
                    uri=str(source_path),
                    title="image guide",
                )
            )

            self.assertEqual("captured", record.status)
            self.assertTrue(record.capture_content_type.startswith("image/"))


class ScanPdfOcrSignalTests(unittest.TestCase):
    def test_extract_pdf_pages_uses_rendered_ocr_for_scan_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "scan.pdf"
            source_path.write_bytes(b"%PDF-1.4\n%scan-only\n")

            with (
                patch(
                    "play_book_studio.intake.normalization.pdf._extract_pdf_pages_with_pypdf",
                    return_value=[],
                ),
                patch(
                    "play_book_studio.intake.normalization.pdf._extract_pdf_pages_with_mdls",
                    return_value=[],
                ),
                patch(
                    "play_book_studio.intake.normalization.pdf._extract_pdf_pages_with_string_scan",
                    return_value=[],
                ),
                patch(
                    "play_book_studio.intake.normalization.pdf._extract_pdf_pages_with_rendered_ocr",
                    return_value=["OpenShift backup restore"],
                ),
            ):
                pages = extract_pdf_pages(source_path)

        self.assertEqual(["OpenShift backup restore"], pages)

    def test_extract_pdf_pages_surfaces_pre_ocr_guidance_for_scan_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "scan.pdf"
            source_path.write_bytes(b"%PDF-1.4\n%scan-only\n")

            with (
                patch(
                    "play_book_studio.intake.normalization.pdf._extract_pdf_pages_with_pypdf",
                    return_value=[],
                ),
                patch(
                    "play_book_studio.intake.normalization.pdf._extract_pdf_pages_with_mdls",
                    return_value=[],
                ),
                patch(
                    "play_book_studio.intake.normalization.pdf._extract_pdf_pages_with_string_scan",
                    return_value=[],
                ),
                patch(
                    "play_book_studio.intake.normalization.pdf._extract_pdf_pages_with_rendered_ocr",
                    return_value=[],
                ),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "텍스트 기반 PDF인지 확인하거나 OCR runtime/사전 OCR 산출물을 준비해야 합니다.",
                ):
                    extract_pdf_pages(source_path)

    def test_extract_pdf_pages_reports_low_quality_text_before_ocr_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "low-quality.pdf"
            source_path.write_bytes(b"%PDF-1.4\n%low-quality\n")

            with (
                patch(
                    "play_book_studio.intake.normalization.pdf._extract_pdf_pages_with_pypdf",
                    return_value=["obj endobj /Type /Page /Filter /FlateDecode"],
                ),
                patch(
                    "play_book_studio.intake.normalization.pdf._extract_pdf_pages_with_mdls",
                    return_value=[],
                ),
                patch(
                    "play_book_studio.intake.normalization.pdf._extract_pdf_pages_with_string_scan",
                    return_value=["obj endobj /Type /Page /Filter /FlateDecode"],
                ),
                patch(
                    "play_book_studio.intake.normalization.pdf._extract_pdf_pages_with_rendered_ocr",
                    return_value=[],
                ),
            ):
                with self.assertRaisesRegex(ValueError, "detail=.*low quality text"):
                    extract_pdf_pages(source_path)


if __name__ == "__main__":
    unittest.main()
