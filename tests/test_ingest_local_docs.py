from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.ingest.local_docs import extract_sections_from_local_path
from ocp_rag.ingest.pipeline import run_local_document_pipeline
from ocp_rag.shared.settings import Settings


class LocalDocumentIngestTests(unittest.TestCase):
    def test_extract_sections_from_markdown_preserves_headings_and_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "rbac-guide.md"
            source.write_text(
                "# RBAC Guide\n\n"
                "권한을 부여하는 절차입니다.\n\n"
                "## 명령 예시\n\n"
                "```bash\n"
                "oc adm policy add-role-to-user admin alice -n demo\n"
                "```\n",
                encoding="utf-8",
            )

            entry, sections = extract_sections_from_local_path(source)

            self.assertEqual("rbac-guide", entry.book_slug)
            self.assertEqual(2, len(sections))
            self.assertEqual("RBAC Guide", sections[0].heading)
            self.assertEqual("명령 예시", sections[1].heading)
            self.assertIn("[CODE]", sections[1].text)
            self.assertIn("oc adm policy add-role-to-user admin alice -n demo", sections[1].text)

    def test_extract_sections_from_html_fragment_works_without_ocp_article_shell(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "notes.html"
            source.write_text(
                "<html><body><h1>Pod Pending</h1><p>이유를 점검합니다.</p>"
                "<h2 id='check-events'>Events 확인</h2>"
                "<pre>oc describe pod mypod -n demo</pre></body></html>",
                encoding="utf-8",
            )

            entry, sections = extract_sections_from_local_path(source)

            self.assertEqual("notes", entry.book_slug)
            self.assertEqual(2, len(sections))
            self.assertEqual("Pod Pending", sections[0].heading)
            self.assertEqual("Events 확인", sections[1].heading)
            self.assertIn("[CODE]", sections[1].text)
            self.assertTrue(sections[1].viewer_path.endswith("#check-events"))

    def test_run_local_document_pipeline_writes_preview_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root, create_dirs=True)
            markdown = root / "doc.txt"
            markdown.write_text("문서 개요\n\noc get pods", encoding="utf-8")
            html = root / "doc2.html"
            html.write_text("<html><body><h1>OpenShift</h1><p>플랫폼 설명</p></body></html>", encoding="utf-8")

            report = run_local_document_pipeline(settings, inputs=[markdown, html])

            output_dir = Path(report["output_dir"])
            self.assertTrue((output_dir / "normalized_docs.jsonl").exists())
            self.assertTrue((output_dir / "chunks.jsonl").exists())
            self.assertTrue((output_dir / "bm25_corpus.jsonl").exists())
            self.assertTrue((output_dir / "source_manifest_local.json").exists())
            self.assertEqual(2, report["document_count"])
            self.assertGreaterEqual(report["section_count"], 2)

            manifest_rows = json.loads((output_dir / "source_manifest_local.json").read_text(encoding="utf-8"))
            self.assertEqual(2, len(manifest_rows))
            self.assertEqual("normalized_local_doc", manifest_rows[0]["viewer_strategy"])

    def test_run_local_document_pipeline_preserves_display_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root, create_dirs=True)
            markdown = root / "98ab12cd-ops-guide.md"
            markdown.write_text("# Checklist\n\noc get pods -A", encoding="utf-8")

            report = run_local_document_pipeline(
                settings,
                inputs=[
                    {
                        "path": markdown,
                        "title": "ops-guide",
                        "book_slug": "ops-guide",
                    }
                ],
            )

            output_dir = Path(report["output_dir"])
            manifest_rows = json.loads((output_dir / "source_manifest_local.json").read_text(encoding="utf-8"))
            normalized_rows = [
                json.loads(line)
                for line in (output_dir / "normalized_docs.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]

            self.assertEqual("ops-guide", manifest_rows[0]["title"])
            self.assertEqual("/docs/local/ops-guide/index.html", manifest_rows[0]["viewer_path"])
            self.assertEqual("ops-guide", normalized_rows[0]["book_title"])
            self.assertEqual("/docs/local/ops-guide/index.html#checklist", normalized_rows[0]["viewer_path"])


if __name__ == "__main__":
    unittest.main()
