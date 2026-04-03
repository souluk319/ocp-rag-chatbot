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

    def test_assemble_context_keeps_second_supporting_chunk_from_same_book(self) -> None:
        bundle = assemble_context(
            [
                _hit(
                    "chunk-1",
                    "architecture",
                    "OpenShift Container Platform의 아키텍처 개요",
                    "OpenShift Container Platform의 플랫폼 및 애플리케이션 아키텍처 개요를 제공합니다.",
                    score=0.063,
                ),
                _hit(
                    "chunk-2",
                    "overview",
                    "3.2. 아키텍처",
                    "아키텍처 문서를 소개하는 개요 링크입니다.",
                    score=0.050,
                ),
                _hit(
                    "chunk-3",
                    "architecture",
                    "2.1.3.4. OpenShift Container Platform 라이프사이클",
                    "클러스터 생성, 관리, 애플리케이션 개발 및 배포, 스케일링을 보여줍니다.",
                    score=0.032,
                ),
            ],
            max_chunks=4,
        )

        self.assertEqual(2, len(bundle.citations))
        self.assertEqual("architecture", bundle.citations[0].book_slug)
        self.assertEqual("architecture", bundle.citations[1].book_slug)
        self.assertIn("라이프사이클", bundle.citations[1].section)

    def test_assemble_context_keeps_procedural_companion_book_when_command_is_present(self) -> None:
        bundle = assemble_context(
            [
                _hit(
                    "chunk-1",
                    "authentication_and_authorization",
                    "특정 SCC가 필요하도록 워크로드 구성",
                    "openshift.io/scc 를 확인하려면 oc get pod <pod_name> -o jsonpath='{.metadata.annotations.openshift\\.io\\/scc}{\"\\n\"}' 를 사용합니다.",
                    score=0.080,
                ),
                _hit(
                    "chunk-2",
                    "authentication_and_authorization",
                    "기본 보안 컨텍스트 제약 조건",
                    "anyuid SCC 는 모든 UID 및 GID 로 실행할 수 있게 합니다.",
                    score=0.074,
                ),
                _hit(
                    "chunk-3",
                    "cli_tools",
                    "oc adm policy add-scc-to-user",
                    "[CODE] oc adm policy add-scc-to-user anyuid -z <service_account_name> -n <project_name> [/CODE]",
                    score=0.067,
                ),
            ],
            max_chunks=4,
        )

        self.assertEqual(
            ["authentication_and_authorization", "authentication_and_authorization", "cli_tools"],
            [c.book_slug for c in bundle.citations],
        )
