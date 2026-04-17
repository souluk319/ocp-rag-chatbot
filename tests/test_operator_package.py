from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from play_book_studio.delivery.operator_package import (
    PACKAGE_ID,
    PACKAGE_MANIFEST_NAME,
    PACKAGE_MARKDOWN_NAME,
    PACKAGE_ZIP_NAME,
    REPORT_JSON_NAME,
    REPORT_MD_NAME,
    build_operator_package,
)


ROOT = Path(__file__).resolve().parents[1]


class OperatorPackageTests(unittest.TestCase):
    def test_build_operator_package_writes_delivery_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            output_dir = temp_root / "delivery"
            report_dir = temp_root / "reports"

            report = build_operator_package(ROOT, output_dir=output_dir, report_dir=report_dir)

            self.assertEqual("ok", report["status"])
            self.assertEqual(PACKAGE_ID, report["package_id"])
            self.assertEqual(4, report["book_count"])
            self.assertEqual(
                ["operators", "cli_tools", "web_console", "disconnected_environments"],
                report["book_slugs"],
            )

            manifest_path = output_dir / PACKAGE_MANIFEST_NAME
            markdown_path = output_dir / PACKAGE_MARKDOWN_NAME
            zip_path = output_dir / PACKAGE_ZIP_NAME
            report_json_path = report_dir / REPORT_JSON_NAME
            report_md_path = report_dir / REPORT_MD_NAME

            self.assertTrue(manifest_path.exists())
            self.assertTrue(markdown_path.exists())
            self.assertTrue(zip_path.exists())
            self.assertTrue(report_json_path.exists())
            self.assertTrue(report_md_path.exists())

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(PACKAGE_ID, manifest["package_id"])
            self.assertEqual("operators", manifest["books"][0]["slug"])
            self.assertTrue(manifest["reading_sequence"])
            self.assertTrue(manifest["key_runtime_sections"])
            self.assertTrue(manifest["key_figures"])

            with ZipFile(zip_path) as archive:
                names = set(archive.namelist())

            self.assertIn(PACKAGE_MANIFEST_NAME, names)
            self.assertIn(PACKAGE_MARKDOWN_NAME, names)
            self.assertIn("books/operators.md", names)
            self.assertIn("books/cli_tools.md", names)
            self.assertIn("books/web_console.md", names)
            self.assertIn("books/disconnected_environments.md", names)


if __name__ == "__main__":
    unittest.main()
