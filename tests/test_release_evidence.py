from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.verify_release_evidence import build_release_evidence_report


class ReleaseEvidenceTests(unittest.TestCase):
    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_release_evidence_blocks_when_current_rehearsal_and_product_gate_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_json(
                root / "reports" / "build_logs" / "release_candidate_freeze_packet.json",
                {"status": "ok"},
            )

            report = build_release_evidence_report(root)

        self.assertEqual("blocked", report["status"])
        self.assertIn("product_rehearsal_report_missing", report["blockers"])
        self.assertIn("release_candidate_freeze_packet_missing_product_gate", report["blockers"])

    def test_release_evidence_accepts_current_product_rehearsal_and_product_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_json(
                root / "reports" / "build_logs" / "product_rehearsal_report.json",
                {
                    "status": "ok",
                    "critical_scenario_pass_rate": 1.0,
                    "blockers": [],
                },
            )
            self._write_json(
                root / "reports" / "build_logs" / "release_candidate_freeze_packet.json",
                {"status": "ok", "product_gate": {"pass_rate": 1.0}, "supporting_packets": []},
            )
            self._write_json(
                root / "reports" / "build_logs" / "buyer_packet_bundle_index.json",
                {"packet_count": 1},
            )

            report = build_release_evidence_report(root)

        self.assertEqual("ok", report["status"])
        self.assertEqual([], report["blockers"])
        self.assertTrue(report["release_packet_has_product_gate"])


if __name__ == "__main__":
    unittest.main()
