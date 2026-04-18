from __future__ import annotations

import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.intake.normalization.degraded_pdf import (
    attempt_optional_image_markdown_fallback,
    attempt_optional_pdf_markdown_fallback,
    requested_pdf_fallback_backend,
)


class IntakeDegradedPdfTests(unittest.TestCase):
    def test_requested_pdf_fallback_backend_uses_surya_endpoint_when_backend_not_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("SURYA_OCR=http://127.0.0.1:8765/ocr\n", encoding="utf-8")
            settings = load_settings(root)

        self.assertEqual("surya", requested_pdf_fallback_backend(settings=settings))

    def test_attempt_optional_pdf_markdown_fallback_blocks_remote_egress_without_allowance(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("SURYA_OCR=http://127.0.0.1:8765/ocr\n", encoding="utf-8")
            settings = load_settings(root)
            attempt = attempt_optional_pdf_markdown_fallback(
                root / "dummy.pdf",
                settings=settings,
                allow_remote=False,
            )

        self.assertEqual("surya", attempt.backend)
        self.assertEqual("blocked", attempt.status)
        self.assertEqual("surya_remote_egress_not_allowed", attempt.reason)
        self.assertFalse(attempt.used)

    def test_attempt_optional_image_markdown_fallback_uses_surya_adapter_when_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text("SURYA_OCR=http://127.0.0.1:8765/ocr\n", encoding="utf-8")
            settings = load_settings(root)

            fake_module = types.SimpleNamespace(
                extract_image_markdown_with_surya=lambda path, *, settings=None: f"# {path.stem}\n\nOCR 성공"
            )
            with patch(
                "play_book_studio.intake.normalization.degraded_pdf.importlib.import_module",
                return_value=fake_module,
            ):
                attempt = attempt_optional_image_markdown_fallback(
                    root / "dummy.png",
                    settings=settings,
                    allow_remote=True,
                )

        self.assertEqual("surya", attempt.backend)
        self.assertEqual("ready", attempt.status)
        self.assertTrue(attempt.used)
        self.assertIn("OCR 성공", attempt.markdown)
