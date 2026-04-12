from __future__ import annotations

import base64
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from docx import Document as DocxDocument
from openpyxl import Workbook
from PIL import Image, ImageDraw
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = ROOT / "tests"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_app_ui import _build_customer_pack_plan, _upload_customer_pack_draft
from play_book_studio.intake import CustomerPackPlanner, DocSourceRequest
from play_book_studio.intake.capture.service import CustomerPackCaptureService
from play_book_studio.intake.normalization.service import CustomerPackNormalizeService


class IntakeMultiformatTests(unittest.TestCase):
    def test_build_customer_pack_plan_accepts_markdown(self) -> None:
        payload = _build_customer_pack_plan(
            {
                "source_type": "md",
                "uri": "/tmp/runbook.md",
                "title": "런북",
            }
        )

        self.assertEqual("md", payload["source_type"])
        self.assertEqual("markdown_text_capture_v1", payload["capture_strategy"])

    def test_upload_customer_pack_draft_preserves_markdown_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = _upload_customer_pack_draft(
                root,
                {
                    "source_type": "md",
                    "uri": "runbook.md",
                    "title": "런북",
                    "file_name": "runbook.md",
                    "content_base64": "IyDrn7zrsJUKCiMjIGV0Y2Qg67Cx7JeF",
                },
            )

        self.assertTrue(str(created["uploaded_file_path"]).endswith(".md"))

    def test_upload_customer_pack_draft_preserves_asciidoc_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = _upload_customer_pack_draft(
                root,
                {
                    "source_type": "asciidoc",
                    "uri": "runbook.adoc",
                    "title": "런북",
                    "file_name": "runbook.adoc",
                    "content_base64": "PSDsmrTsmIEg656c67aBPT0KCl09IGV0Y2Qg67Cx7JeF",
                },
            )

        self.assertTrue(str(created["uploaded_file_path"]).endswith(".adoc"))

    def test_upload_customer_pack_draft_preserves_text_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = _upload_customer_pack_draft(
                root,
                {
                    "source_type": "txt",
                    "uri": "runbook.txt",
                    "title": "런북",
                    "file_name": "runbook.txt",
                    "content_base64": "7Jq07JiBIOyghOywuO2VmOyduA==",
                },
            )

        self.assertTrue(str(created["uploaded_file_path"]).endswith(".txt"))

    def test_markdown_source_uses_text_capture_strategy(self) -> None:
        draft = CustomerPackPlanner().plan(
            DocSourceRequest(
                source_type="md",
                uri="/tmp/runbook.md",
            )
        )

        self.assertEqual("markdown_text_capture_v1", draft.capture_strategy)
        self.assertIn("Markdown", draft.acquisition_step)

    def test_asciidoc_source_uses_text_capture_strategy(self) -> None:
        draft = CustomerPackPlanner().plan(
            DocSourceRequest(
                source_type="asciidoc",
                uri="/tmp/runbook.adoc",
            )
        )

        self.assertEqual("asciidoc_text_capture_v1", draft.capture_strategy)
        self.assertIn("AsciiDoc", draft.acquisition_step)

    def test_text_source_uses_plain_text_capture_strategy(self) -> None:
        draft = CustomerPackPlanner().plan(
            DocSourceRequest(
                source_type="txt",
                uri="/tmp/runbook.txt",
            )
        )

        self.assertEqual("plain_text_capture_v1", draft.capture_strategy)
        self.assertIn("Text", draft.acquisition_step)

    def test_docx_source_uses_binary_capture_strategy(self) -> None:
        draft = CustomerPackPlanner().plan(
            DocSourceRequest(
                source_type="docx",
                uri="/tmp/runbook.docx",
            )
        )

        self.assertEqual("docx_structured_capture_v1", draft.capture_strategy)
        self.assertIn("Word", draft.acquisition_step)

    def test_pptx_source_uses_binary_capture_strategy(self) -> None:
        draft = CustomerPackPlanner().plan(
            DocSourceRequest(
                source_type="pptx",
                uri="/tmp/runbook.pptx",
            )
        )

        self.assertEqual("pptx_slide_capture_v1", draft.capture_strategy)
        self.assertIn("PowerPoint", draft.acquisition_step)

    def test_xlsx_source_uses_binary_capture_strategy(self) -> None:
        draft = CustomerPackPlanner().plan(
            DocSourceRequest(
                source_type="xlsx",
                uri="/tmp/runbook.xlsx",
            )
        )

        self.assertEqual("xlsx_sheet_capture_v1", draft.capture_strategy)
        self.assertIn("Excel", draft.acquisition_step)

    def test_image_source_uses_ocr_capture_strategy(self) -> None:
        draft = CustomerPackPlanner().plan(
            DocSourceRequest(
                source_type="image",
                uri="/tmp/runbook.png",
            )
        )

        self.assertEqual("image_ocr_capture_v1", draft.capture_strategy)
        self.assertIn("Image", draft.acquisition_step)

    def test_capture_service_reads_local_markdown_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_md = root / "runbook.md"
            source_md.write_text("# 런북\n\n## etcd 백업\n\n```bash\noc debug node/node-0\n```", encoding="utf-8")

            record = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="md", uri=str(source_md), title="런북")
            )

            artifact_path = Path(record.capture_artifact_path)
            self.assertEqual("captured", record.status)
            self.assertTrue(artifact_path.exists())
            self.assertTrue(artifact_path.name.endswith(".md"))

    def test_capture_service_reads_local_asciidoc_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_adoc = root / "runbook.adoc"
            source_adoc.write_text("= 운영 런북\n\n== etcd 백업\n\n[source,bash]\n----\noc debug node/node-0\n----", encoding="utf-8")

            record = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="asciidoc", uri=str(source_adoc), title="런북")
            )

            artifact_path = Path(record.capture_artifact_path)
            self.assertEqual("captured", record.status)
            self.assertTrue(artifact_path.exists())
            self.assertTrue(artifact_path.name.endswith(".adoc"))

    def test_upload_customer_pack_draft_preserves_docx_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "runbook.docx"
            document = DocxDocument()
            document.add_heading("운영 런북", level=1)
            document.save(source)
            created = _upload_customer_pack_draft(
                root,
                {
                    "source_type": "docx",
                    "uri": "runbook.docx",
                    "title": "런북",
                    "file_name": "runbook.docx",
                    "content_base64": base64.b64encode(source.read_bytes()).decode("utf-8"),
                },
            )

        self.assertTrue(str(created["uploaded_file_path"]).endswith(".docx"))

    def test_capture_service_reads_local_docx_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_docx = root / "runbook.docx"
            document = DocxDocument()
            document.add_heading("운영 런북", level=1)
            document.add_paragraph("etcd 백업 절차")
            document.save(source_docx)

            record = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="docx", uri=str(source_docx), title="런북")
            )

            artifact_path = Path(record.capture_artifact_path)
            self.assertEqual("captured", record.status)
            self.assertTrue(artifact_path.exists())
            self.assertTrue(artifact_path.name.endswith(".docx"))

    def test_capture_service_reads_local_pptx_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_pptx = root / "runbook.pptx"
            presentation = Presentation()
            slide = presentation.slides.add_slide(presentation.slide_layouts[1])
            slide.shapes.title.text = "운영 런북"
            slide.placeholders[1].text = "etcd 백업 절차"
            presentation.save(source_pptx)

            record = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="pptx", uri=str(source_pptx), title="런북")
            )

            artifact_path = Path(record.capture_artifact_path)
            self.assertEqual("captured", record.status)
            self.assertTrue(artifact_path.exists())
            self.assertTrue(artifact_path.name.endswith(".pptx"))

    def test_capture_service_reads_local_xlsx_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_xlsx = root / "runbook.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "etcd"
            sheet.append(["절차", "명령어"])
            sheet.append(["백업", "cluster-backup.sh"])
            workbook.save(source_xlsx)

            record = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="xlsx", uri=str(source_xlsx), title="런북")
            )

            artifact_path = Path(record.capture_artifact_path)
            self.assertEqual("captured", record.status)
            self.assertTrue(artifact_path.exists())
            self.assertTrue(artifact_path.name.endswith(".xlsx"))

    def test_capture_service_reads_local_image_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_png = root / "runbook.png"
            image = Image.new("RGB", (320, 100), color="white")
            draw = ImageDraw.Draw(image)
            draw.text((20, 30), "OpenShift backup restore", fill="black")
            image.save(source_png)

            record = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="image", uri=str(source_png), title="런북")
            )

            artifact_path = Path(record.capture_artifact_path)
            self.assertEqual("captured", record.status)
            self.assertTrue(artifact_path.exists())
            self.assertTrue(artifact_path.name.endswith(".png"))

    def test_normalize_service_builds_sections_from_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_md = root / "runbook.md"
            source_md.write_text(
                "# 운영 런북\n\n## etcd 백업\n\n```bash\noc debug node/node-0\n```\n\n## 검증\n\n완료 여부 확인",
                encoding="utf-8",
            )

            captured = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="md", uri=str(source_md), title="운영 런북")
            )
            normalized = CustomerPackNormalizeService(root).normalize(draft_id=captured.draft_id)
            payload = json.loads(Path(normalized.canonical_book_path).read_text(encoding="utf-8"))
            topic_book_path = root / "artifacts" / "customer_packs" / "books" / f"{captured.draft_id}--topic_playbook.json"
            operation_book_path = root / "artifacts" / "customer_packs" / "books" / f"{captured.draft_id}--operation_playbook.json"
            self.assertTrue(topic_book_path.exists())
            self.assertTrue(operation_book_path.exists())

        self.assertEqual("normalized", normalized.status)
        self.assertGreaterEqual(normalized.normalized_section_count, 2)
        self.assertEqual("md", payload["source_type"])
        self.assertEqual(6, payload["playable_asset_count"])
        self.assertEqual(5, payload["derived_asset_count"])
        self.assertEqual(5, len(payload["derived_assets"]))
        self.assertTrue(any("[CODE]" in section["text"] for section in payload["sections"]))

    def test_normalize_service_builds_sections_from_asciidoc(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_adoc = root / "runbook.adoc"
            source_adoc.write_text(
                "= 운영 런북\n\n== etcd 백업\n\n[source,bash]\n----\noc debug node/node-0\n----\n\n== 검증\n\n완료 여부 확인",
                encoding="utf-8",
            )

            captured = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="asciidoc", uri=str(source_adoc), title="운영 런북")
            )
            normalized = CustomerPackNormalizeService(root).normalize(draft_id=captured.draft_id)
            payload = json.loads(Path(normalized.canonical_book_path).read_text(encoding="utf-8"))

        self.assertEqual("normalized", normalized.status)
        self.assertEqual("asciidoc", payload["source_type"])
        self.assertTrue(any("etcd 백업" in section["heading"] for section in payload["sections"]))
        self.assertTrue(
            any("oc debug node/node-0" in section["text"] for section in payload["sections"])
        )

    def test_normalize_service_builds_sections_from_plain_text_numeric_headings(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_txt = root / "runbook.txt"
            source_txt.write_text(
                "1 운영 개요\n\n개요 설명\n\n2.1 etcd 백업\n\noc debug node/node-0\n\n2.2 검증\n\n완료 여부 확인",
                encoding="utf-8",
            )

            captured = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="txt", uri=str(source_txt), title="운영 런북")
            )
            normalized = CustomerPackNormalizeService(root).normalize(draft_id=captured.draft_id)
            payload = json.loads(Path(normalized.canonical_book_path).read_text(encoding="utf-8"))

        headings = [section["heading"] for section in payload["sections"]]
        self.assertEqual("normalized", normalized.status)
        self.assertEqual("txt", payload["source_type"])
        self.assertTrue(any("2.1 etcd 백업" in heading for heading in headings))
        self.assertTrue(any("2.2 검증" in heading for heading in headings))

    def test_normalize_service_uses_ocr_docling_fallback_for_scan_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_pdf = root / "scan.pdf"
            source_pdf.write_bytes(b"%PDF-1.4 sample")

            captured = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="pdf", uri=str(source_pdf), title="스캔 PDF")
            )

            with patch(
                "play_book_studio.intake.normalization.service.extract_pdf_markdown_with_docling",
                side_effect=ValueError("docling no text"),
            ), patch(
                "play_book_studio.intake.normalization.service.extract_pdf_markdown_with_docling_ocr",
                return_value="## 복구 절차\n\nOCR로 추출된 텍스트",
            ), patch(
                "play_book_studio.intake.normalization.service.extract_pdf_pages",
                side_effect=ValueError("scan pdf"),
            ):
                normalized = CustomerPackNormalizeService(root).normalize(draft_id=captured.draft_id)
                payload = json.loads(Path(normalized.canonical_book_path).read_text(encoding="utf-8"))

        self.assertEqual("normalized", normalized.status)
        self.assertEqual("복구 절차", payload["sections"][0]["heading"])

    def test_docx_source_is_honestly_rejected(self) -> None:
        payload = _build_customer_pack_plan({"source_type": "docx", "uri": "/tmp/demo.docx"})
        self.assertEqual("docx", payload["source_type"])
        self.assertEqual("docx_structured_capture_v1", payload["capture_strategy"])

    def test_normalize_service_builds_sections_from_docx(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_docx = root / "runbook.docx"
            document = DocxDocument()
            document.add_heading("운영 런북", level=1)
            document.add_heading("etcd 백업", level=2)
            document.add_paragraph("oc debug node/node-0")
            table = document.add_table(rows=2, cols=2)
            table.rows[0].cells[0].text = "절차"
            table.rows[0].cells[1].text = "명령어"
            table.rows[1].cells[0].text = "백업"
            table.rows[1].cells[1].text = "cluster-backup.sh"
            document.save(source_docx)

            captured = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="docx", uri=str(source_docx), title="운영 런북")
            )
            normalized = CustomerPackNormalizeService(root).normalize(draft_id=captured.draft_id)
            payload = json.loads(Path(normalized.canonical_book_path).read_text(encoding="utf-8"))

        self.assertEqual("normalized", normalized.status)
        self.assertEqual("docx", payload["source_type"])
        self.assertTrue(any("etcd 백업" in section["heading"] for section in payload["sections"]))
        self.assertTrue(any("[TABLE]" in section["text"] for section in payload["sections"]))

    def test_normalize_service_builds_sections_from_pptx(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_pptx = root / "runbook.pptx"
            presentation = Presentation()
            slide = presentation.slides.add_slide(presentation.slide_layouts[1])
            slide.shapes.title.text = "etcd 백업"
            slide.placeholders[1].text = "cluster-backup.sh 실행"
            presentation.save(source_pptx)

            captured = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="pptx", uri=str(source_pptx), title="운영 런북")
            )
            normalized = CustomerPackNormalizeService(root).normalize(draft_id=captured.draft_id)
            payload = json.loads(Path(normalized.canonical_book_path).read_text(encoding="utf-8"))

        self.assertEqual("normalized", normalized.status)
        self.assertEqual("pptx", payload["source_type"])
        self.assertTrue(any("etcd 백업" in section["heading"] for section in payload["sections"]))
        self.assertTrue(any("cluster-backup.sh" in section["text"] for section in payload["sections"]))

    def test_normalize_service_builds_sections_from_xlsx(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_xlsx = root / "runbook.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "backup"
            sheet.append(["절차", "명령어"])
            sheet.append(["백업", "cluster-backup.sh"])
            workbook.save(source_xlsx)

            captured = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="xlsx", uri=str(source_xlsx), title="운영 런북")
            )
            normalized = CustomerPackNormalizeService(root).normalize(draft_id=captured.draft_id)
            payload = json.loads(Path(normalized.canonical_book_path).read_text(encoding="utf-8"))

        self.assertEqual("normalized", normalized.status)
        self.assertEqual("xlsx", payload["source_type"])
        self.assertTrue(any("backup" in section["heading"].lower() for section in payload["sections"]))
        self.assertTrue(any("[TABLE]" in section["text"] for section in payload["sections"]))

    def test_normalize_service_builds_sections_from_image_ocr(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_png = root / "runbook.png"
            image = Image.new("RGB", (320, 100), color="white")
            draw = ImageDraw.Draw(image)
            draw.text((20, 30), "OpenShift backup restore", fill="black")
            image.save(source_png)

            captured = CustomerPackCaptureService(root).capture(
                request=DocSourceRequest(source_type="image", uri=str(source_png), title="OCR 런북")
            )

            with patch(
                "play_book_studio.intake.normalization.builders.extract_image_markdown_with_docling",
                return_value="## OCR 절차\n\ncluster-backup.sh",
            ):
                normalized = CustomerPackNormalizeService(root).normalize(draft_id=captured.draft_id)
                payload = json.loads(Path(normalized.canonical_book_path).read_text(encoding="utf-8"))

        self.assertEqual("normalized", normalized.status)
        self.assertEqual("image", payload["source_type"])
        self.assertTrue(any("OCR 절차" in section["heading"] for section in payload["sections"]))


if __name__ == "__main__":
    unittest.main()
