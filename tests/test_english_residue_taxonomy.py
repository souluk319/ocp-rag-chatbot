from __future__ import annotations

import unittest

from play_book_studio.english_residue_taxonomy import (
    KEEP_TERMS_CODE_PATHS,
    MIXED_LINE,
    TRANSLATE_TARGET_PROSE,
    classify_english_residue_line,
)


class EnglishResidueTaxonomyTests(unittest.TestCase):
    def test_classifies_clear_english_reader_prose_as_translate_target(self) -> None:
        result = classify_english_residue_line(
            "The Cluster Network Operator (CNO) runs a controller that performs a connection health check."
        )
        self.assertEqual(result.kind, TRANSLATE_TARGET_PROSE)

    def test_classifies_short_reader_heading_as_translate_target(self) -> None:
        result = classify_english_residue_line("Additional resources")
        self.assertEqual(result.kind, TRANSLATE_TARGET_PROSE)

    def test_keeps_product_term_only_line(self) -> None:
        result = classify_english_residue_line("OpenShift Container Platform")
        self.assertEqual(result.kind, KEEP_TERMS_CODE_PATHS)

    def test_keeps_cli_command_line(self) -> None:
        result = classify_english_residue_line("oc get pods -n openshift-cluster-version")
        self.assertEqual(result.kind, KEEP_TERMS_CODE_PATHS)

    def test_keeps_source_and_asset_trace_line(self) -> None:
        result = classify_english_residue_line(
            "_Source: `enabling-OVS-balance-slb-mode.adoc` · asset `552_OpenShift_slb_mode_0625.png`_"
        )
        self.assertEqual(result.kind, KEEP_TERMS_CODE_PATHS)

    def test_counts_markdown_link_label_as_translate_target(self) -> None:
        result = classify_english_residue_line(
            "* [Configuring a dynamic Ethernet connection using nmcli](https://access.redhat.com/documentation/example)"
        )
        self.assertEqual(result.kind, TRANSLATE_TARGET_PROSE)

    def test_marks_korean_english_line_as_mixed(self) -> None:
        result = classify_english_residue_line(
            "클러스터 관리자 As a cluster administrator, you can use the web console."
        )
        self.assertEqual(result.kind, MIXED_LINE)

    def test_marks_inline_code_plus_prose_as_mixed(self) -> None:
        result = classify_english_residue_line("Use the `oc` command to list pods.")
        self.assertEqual(result.kind, MIXED_LINE)


if __name__ == "__main__":
    unittest.main()
