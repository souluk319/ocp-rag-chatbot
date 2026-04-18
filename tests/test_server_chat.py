from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.app.server_chat import _summarize_citation_truth


class TestServerChat(unittest.TestCase):
    def test_summarize_citation_truth_keeps_mixed_official_private_boundary(self) -> None:
        payload = {
            "citations": [
                {
                    "book_slug": "architecture",
                    "boundary_truth": "official_validated_runtime",
                    "runtime_truth_label": "Official Runtime",
                    "source_lane": "official_ko",
                    "boundary_badge": "Official Runtime",
                    "approval_state": "approved",
                    "publication_state": "active",
                },
                {
                    "book_slug": "customer-config-guide",
                    "boundary_truth": "private_customer_pack_runtime",
                    "runtime_truth_label": "Customer Source-First Pack",
                    "source_lane": "customer_source_first_pack",
                    "boundary_badge": "Private Pack Runtime",
                    "approval_state": "unreviewed",
                    "publication_state": "draft",
                },
            ]
        }

        summary = _summarize_citation_truth(payload)

        self.assertEqual("mixed_runtime_bridge", summary["source_lane"])
        self.assertEqual("mixed_runtime_bridge", summary["boundary_truth"])
        self.assertEqual("Mixed Runtime", summary["boundary_badge"])
        self.assertEqual("mixed", summary["publication_state"])
        self.assertEqual("mixed", summary["approval_state"])
        self.assertIn("Official Runtime", summary["runtime_truth_label"])
        self.assertIn("Customer Source-First Pack", summary["runtime_truth_label"])


if __name__ == "__main__":
    unittest.main()
