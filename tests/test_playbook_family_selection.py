from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.ingestion.playbook_family_selection import (
    build_playbook_family_selection_report_from_rows,
)


def _section(heading: str, text: str) -> dict[str, object]:
    return {
        "heading": heading,
        "section_path_label": heading,
        "blocks": [{"kind": "paragraph", "text": text}],
    }


class PlaybookFamilySelectionTests(unittest.TestCase):
    def test_selection_prefers_synthesized_for_official_doc_roots(self) -> None:
        rows = [
            {
                "book_slug": "install",
                "title": "설치 개요",
                "translation_status": "approved_ko",
                "review_status": "approved",
                "section_count": 3,
                "source_metadata": {"source_type": "official_doc"},
                "sections": [
                    _section("개요", "설치 준비 부트스트랩 검증"),
                    _section("절차", "설치 절차 부트스트랩 검증"),
                    _section("참조", "설치 요구 사항 검증"),
                ],
            },
            {
                "book_slug": "install_topic_playbook",
                "title": "설치 토픽 플레이북",
                "translation_status": "approved_ko",
                "review_status": "approved",
                "section_count": 2,
                "source_metadata": {
                    "source_type": "topic_playbook",
                    "derived_from_book_slug": "install",
                },
                "sections": [
                    _section("개요", "설치 준비"),
                    _section("절차", "설치 절차"),
                ],
            },
            {
                "book_slug": "install_operations_playbook",
                "title": "설치 운영 플레이북",
                "translation_status": "approved_ko",
                "review_status": "approved",
                "section_count": 2,
                "source_metadata": {
                    "source_type": "operation_playbook",
                    "derived_from_book_slug": "install",
                },
                "sections": [
                    _section("절차", "설치 절차 검증"),
                    _section("점검", "설치 요구 사항"),
                ],
            },
            {
                "book_slug": "install_policy_overlay_book",
                "title": "설치 정책 오버레이 북",
                "translation_status": "approved_ko",
                "review_status": "approved",
                "section_count": 1,
                "source_metadata": {
                    "source_type": "policy_overlay_book",
                    "derived_from_book_slug": "install",
                },
                "sections": [_section("정책", "설치 요구 사항")],
            },
            {
                "book_slug": "install_troubleshooting_playbook",
                "title": "설치 트러블슈팅 플레이북",
                "translation_status": "approved_ko",
                "review_status": "approved",
                "section_count": 1,
                "source_metadata": {
                    "source_type": "troubleshooting_playbook",
                    "derived_from_book_slug": "install",
                },
                "sections": [_section("장애", "부트스트랩 실패 검증")],
            },
            {
                "book_slug": "install_synthesized_playbook",
                "title": "설치 합성 플레이북",
                "translation_status": "approved_ko",
                "review_status": "approved",
                "section_count": 3,
                "source_metadata": {
                    "source_type": "synthesized_playbook",
                    "derived_from_book_slug": "install",
                },
                "sections": [
                    _section("개요", "설치 준비 부트스트랩 검증"),
                    _section("절차", "설치 절차 부트스트랩 검증"),
                    _section("참조", "설치 요구 사항 검증"),
                ],
            },
            {
                "book_slug": "monitoring",
                "title": "모니터링 운영 플레이북",
                "translation_status": "approved_ko",
                "review_status": "approved",
                "section_count": 2,
                "source_metadata": {"source_type": "manual_synthesis"},
                "sections": [
                    _section("개요", "모니터링 경보"),
                    _section("운영", "Prometheus 경보 대응"),
                ],
            },
            {
                "book_slug": "monitoring_operations_playbook",
                "title": "모니터링 운영 플레이북",
                "translation_status": "approved_ko",
                "review_status": "approved",
                "section_count": 2,
                "source_metadata": {
                    "source_type": "operation_playbook",
                    "derived_from_book_slug": "monitoring",
                },
                "sections": [
                    _section("개요", "모니터링 경보"),
                    _section("운영", "Prometheus 경보 대응"),
                ],
            },
        ]

        report = build_playbook_family_selection_report_from_rows(rows)

        self.assertEqual(2, report["source_truth_count"])
        self.assertEqual("synthesized_playbook", report["official_doc_summary"]["overall_winner_family"])
        self.assertTrue(report["official_doc_summary"]["selection_ready"])
        self.assertEqual("official_doc_roots", report["convergence"]["selection_basis"])
        self.assertEqual("source_truth_only", report["convergence"]["publish_default"])
        self.assertEqual("synthesized_playbook", report["convergence"]["single_derived_family"])


if __name__ == "__main__":
    unittest.main()
