from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.canonical import build_source_repo_document_ast
from play_book_studio.ingestion.models import CONTENT_STATUS_EN_ONLY, SOURCE_STATE_EN_ONLY, SourceManifestEntry


class CanonicalAsciiDocTests(unittest.TestCase):
    def test_build_source_repo_document_ast_preserves_repo_provenance_and_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = root / "welcome" / "index.adoc"
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(
                "\n".join(
                    [
                        "= Welcome",
                        "",
                        "OpenShift overview.",
                        "",
                        "== Install",
                        "[source,bash]",
                        "----",
                        "oc get nodes",
                        "----",
                        "",
                        "[NOTE]",
                        "====",
                        "Read the note.",
                        "====",
                        "",
                        "|===",
                        "| Name | Role",
                        "| master-0 | control-plane",
                        "|===",
                    ]
                ),
                encoding="utf-8",
            )
            entry = SourceManifestEntry(
                book_slug="welcome__index",
                title="Welcome",
                ocp_version="4.20",
                docs_language="ko",
                resolved_language="en",
                source_state=SOURCE_STATE_EN_ONLY,
                content_status=CONTENT_STATUS_EN_ONLY,
                source_lane="official_source_first",
                source_type="official_doc",
                source_collection="core",
                source_url="https://github.com/openshift/openshift-docs/blob/enterprise-4.20/welcome/index.adoc",
                resolved_source_url="https://github.com/openshift/openshift-docs/blob/enterprise-4.20/welcome/index.adoc",
                viewer_path="/docs/ocp/4.20/ko/welcome__index/index.html",
                source_repo="https://github.com/openshift/openshift-docs",
                source_branch="enterprise-4.20",
                source_binding_kind="file",
                source_relative_path="welcome/index.adoc",
                source_relative_paths=("welcome/index.adoc",),
                source_mirror_root=str(root),
                translation_source_language="en",
                translation_target_language="ko",
                translation_source_url="https://github.com/openshift/openshift-docs/blob/enterprise-4.20/welcome/index.adoc",
                primary_input_kind="source_repo",
            )

            document = build_source_repo_document_ast(
                entry=entry,
                source_paths=[source_path],
                fallback_title="Welcome",
            )

        payload = document.to_dict()
        self.assertEqual("repo", payload["source_type"])
        self.assertEqual("official_source_first", payload["provenance"]["source_lane"])
        self.assertEqual("source_repo", payload["provenance"]["primary_input_kind"])
        self.assertEqual("https://github.com/openshift/openshift-docs", payload["provenance"]["source_repo"])
        self.assertEqual(["welcome/index.adoc"], payload["provenance"]["source_relative_paths"])
        self.assertEqual("en_only", payload["provenance"]["translation_stage"])
        self.assertGreaterEqual(len(payload["sections"]), 2)
        block_kinds = payload["sections"][1]["block_kinds"]
        self.assertIn("code", block_kinds)
        self.assertIn("note", block_kinds)
        self.assertIn("table", block_kinds)

    def test_build_source_repo_document_ast_uses_fallback_title_for_unresolved_attr_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = root / "architecture" / "architecture-rhcos.adoc"
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(
                "\n".join(
                    [
                        "= {op-system-first}",
                        "",
                        "Body text.",
                    ]
                ),
                encoding="utf-8",
            )
            entry = SourceManifestEntry(
                book_slug="architecture__architecture_rhcos",
                title="Red Hat Enterprise Linux CoreOS",
                ocp_version="4.20",
                docs_language="ko",
                resolved_language="en",
                source_state=SOURCE_STATE_EN_ONLY,
                content_status=CONTENT_STATUS_EN_ONLY,
                source_lane="official_source_first",
                source_type="official_doc",
                source_collection="core",
                source_url="https://github.com/openshift/openshift-docs/blob/enterprise-4.20/architecture/architecture-rhcos.adoc",
                resolved_source_url="https://github.com/openshift/openshift-docs/blob/enterprise-4.20/architecture/architecture-rhcos.adoc",
                viewer_path="/docs/ocp/4.20/ko/architecture__architecture_rhcos/index.html",
                source_repo="https://github.com/openshift/openshift-docs",
                source_branch="enterprise-4.20",
                source_binding_kind="file",
                source_relative_path="architecture/architecture-rhcos.adoc",
                source_relative_paths=("architecture/architecture-rhcos.adoc",),
                source_mirror_root=str(root),
                translation_source_language="en",
                translation_target_language="ko",
                translation_source_url="https://github.com/openshift/openshift-docs/blob/enterprise-4.20/architecture/architecture-rhcos.adoc",
                primary_input_kind="source_repo",
            )

            document = build_source_repo_document_ast(
                entry=entry,
                source_paths=[source_path],
                fallback_title="Red Hat Enterprise Linux CoreOS",
            )

        self.assertEqual("Red Hat Enterprise Linux CoreOS", document.title)


if __name__ == "__main__":
    unittest.main()
