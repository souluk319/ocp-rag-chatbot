from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part2.models import RetrievalHit
from ocp_rag_part3.context import assemble_context


def _hit(
    chunk_id: str,
    book_slug: str,
    section: str,
    text: str,
    *,
    anchor: str | None = None,
    score: float = 1.0,
) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id,
        book_slug=book_slug,
        chapter=book_slug,
        section=section,
        anchor=anchor or section.lower().replace(" ", "-"),
        source_url=f"https://example.com/{book_slug}",
        viewer_path=f"/docs/{book_slug}.html#{section.lower().replace(' ', '-')}",
        text=text,
        source="hybrid",
        raw_score=score,
        fused_score=score,
    )


class ContextAssemblyTests(unittest.TestCase):
    def test_assemble_context_deduplicates_same_chunk_and_signature(self) -> None:
        bundle = assemble_context(
            [
                _hit("chunk-1", "architecture", "개요", "OpenShift 아키텍처 개요 설명"),
                _hit("chunk-1", "architecture", "개요", "OpenShift 아키텍처 개요 설명"),
                _hit("chunk-2", "architecture", "개요", "OpenShift 아키텍처 개요 설명"),
                _hit("chunk-3", "overview", "소개", "플랫폼 소개"),
                _hit("chunk-4", "overview", "소개", "플랫폼 소개 두 번째 근거"),
            ],
            max_chunks=5,
        )

        self.assertEqual(3, len(bundle.citations))
        self.assertIn("[1] book=architecture", bundle.prompt_context)
        self.assertIn("[2] book=overview", bundle.prompt_context)
        self.assertIn("[3] book=overview", bundle.prompt_context)

    def test_assemble_context_returns_empty_for_low_confidence_competing_books(self) -> None:
        bundle = assemble_context(
            [
                _hit("chunk-1", "logging", "로그", "로그 문서", score=0.0178),
                _hit("chunk-2", "monitoring", "모니터링", "모니터링 문서", score=0.0172),
                _hit("chunk-3", "observability_overview", "관찰성", "관찰성 문서", score=0.0169),
                _hit("chunk-4", "network_security", "감사 로그", "보안 로그 문서", score=0.0168),
            ],
            max_chunks=4,
        )

        self.assertEqual([], bundle.citations)
        self.assertEqual("", bundle.prompt_context)

    def test_assemble_context_skips_cross_book_mirror_sections(self) -> None:
        bundle = assemble_context(
            [
                _hit(
                    "chunk-1",
                    "operators",
                    "4.12.6.2. CLI 사용",
                    "spec.paused 를 true 로 설정하고 master 와 worker 에 patch 합니다.",
                    anchor="troubleshooting-disabling-autoreboot-mco-cli_olm-troubleshooting-operator-issues",
                    score=0.039,
                ),
                _hit(
                    "chunk-2",
                    "operators",
                    "4.12.6.2. CLI 사용",
                    "spec.paused 를 false 로 설정하여 일시 중지를 해제합니다.",
                    anchor="troubleshooting-disabling-autoreboot-mco-cli_olm-troubleshooting-operator-issues",
                    score=0.038,
                ),
                _hit(
                    "chunk-3",
                    "support",
                    "7.6.6.2. CLI 사용",
                    "spec.paused 를 true 로 설정하고 master 와 worker 에 patch 합니다.",
                    anchor="troubleshooting-disabling-autoreboot-mco-cli_troubleshooting-operator-issues",
                    score=0.037,
                ),
                _hit(
                    "chunk-4",
                    "support",
                    "7.6.6.2. CLI 사용",
                    "spec.paused 를 false 로 설정하여 일시 중지를 해제합니다.",
                    anchor="troubleshooting-disabling-autoreboot-mco-cli_troubleshooting-operator-issues",
                    score=0.036,
                ),
            ],
            max_chunks=6,
        )

        self.assertEqual(["operators", "operators"], [c.book_slug for c in bundle.citations])
