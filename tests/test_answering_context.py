from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.retrieval.models import RetrievalHit
from ocp_rag.answering.context import _should_force_clarification, assemble_context


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

    def test_assemble_context_prefers_substantive_duplicate_excerpt(self) -> None:
        bundle = assemble_context(
            [
                _hit(
                    "chunk-1",
                    "overview",
                    "7.1. 유사점 및 차이점",
                    "개요 7장. About OpenShift Kubernetes Engine > 7.1. 유사점 및 차이점 /TABLE]",
                    score=0.0718,
                ),
                _hit(
                    "chunk-2",
                    "overview",
                    "7.1. 유사점 및 차이점",
                    "개요 7장. About OpenShift Kubernetes Engine > 7.1. 유사점 및 차이점\n\n다음 표에서 OpenShift Kubernetes Engine과 OpenShift Container Platform의 유사점과 차이점을 확인할 수 있습니다.",
                    score=0.0674,
                ),
            ],
            query="쿠버네티스와 차이도 설명해줘",
            max_chunks=4,
        )

        self.assertEqual(1, len(bundle.citations))
        self.assertIn("차이점", bundle.citations[0].excerpt)

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

    def test_clarification_gate_ignores_duplicate_top_hits_from_same_section(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "security_and_compliance",
                "2.1.2. OpenShift Container Platform의 정의",
                "쿠버네티스 플랫폼마다 보안이 다를 수 있습니다.",
                anchor="platform-definition",
                score=0.0379,
            ),
            _hit(
                "chunk-2",
                "security_and_compliance",
                "2.1.2. OpenShift Container Platform의 정의",
                "OpenShift Container Platform은 쿠버네티스 보안을 잠그고 운영 기능을 제공합니다.",
                anchor="platform-definition",
                score=0.0379,
            ),
            _hit(
                "chunk-3",
                "architecture",
                "1장. 아키텍처 개요",
                "OpenShift Container Platform은 Kubernetes 기반의 플랫폼입니다.",
                anchor="architecture-overview",
                score=0.0305,
            ),
            _hit(
                "chunk-4",
                "overview",
                "7.1. 유사점 및 차이점",
                "비교 표입니다.",
                anchor="similarities-and-differences",
                score=0.0246,
            ),
        ]

        self.assertFalse(_should_force_clarification(hits))
        bundle = assemble_context(hits, max_chunks=4)
        self.assertNotEqual([], bundle.citations)

    def test_compare_query_keeps_context_even_with_multiple_books(self) -> None:
        hits = [
            _hit("chunk-1", "overview", "7.1. 유사점 및 차이점", "OpenShift와 Kubernetes 차이 설명", score=0.031),
            _hit("chunk-2", "architecture", "1장. 아키텍처 개요", "OpenShift는 Kubernetes 기반 플랫폼", score=0.029),
            _hit("chunk-3", "security_and_compliance", "2.1.2. 정의", "보안과 운영 기능", score=0.027),
        ]

        bundle = assemble_context(
            hits,
            query="오픈시프트랑 쿠버네티스 차이를 설명해줘",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertIn(bundle.citations[0].book_slug, {"overview", "architecture"})

    def test_operator_concept_prefers_expected_concept_books(self) -> None:
        hits = [
            _hit("chunk-1", "architecture", "1.1. 일반 용어집", "Operator 정의", score=0.041),
            _hit("chunk-2", "extensions", "6.3. OpenShift Container Platform의 Operator", "Operator controller", score=0.038),
            _hit("chunk-3", "overview", "7.1. 유사점 및 차이점", "운영 자동화", score=0.036),
            _hit("chunk-4", "support", "문제 해결", "지원 문서", score=0.03),
        ]

        bundle = assemble_context(
            hits,
            query="Operator가 왜 필요한지 예시까지 설명해줘",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertIn(bundle.citations[0].book_slug, {"extensions", "overview", "architecture"})
        self.assertNotIn("support", [citation.book_slug for citation in bundle.citations])

    def test_procedure_query_allows_more_same_book_chunks(self) -> None:
        hits = [
            _hit("chunk-1", "postinstallation_configuration", "4.12.5. etcd 데이터 백업", "oc debug --as-root node", score=0.041),
            _hit("chunk-2", "postinstallation_configuration", "4.12.5. etcd 데이터 백업", "chroot /host", score=0.039),
            _hit("chunk-3", "postinstallation_configuration", "4.12.5. etcd 데이터 백업", "cluster-backup.sh", score=0.038),
            _hit("chunk-4", "hosted_control_planes", "9.3.1. hosted etcd 백업", "velero", score=0.03),
        ]

        bundle = assemble_context(
            hits,
            query="etcd 백업은 실제로 어떤 절차로 해?",
            max_chunks=5,
        )

        self.assertGreaterEqual(len(bundle.citations), 3)
        self.assertEqual(
            ["postinstallation_configuration"] * len(bundle.citations),
            [citation.book_slug for citation in bundle.citations],
        )
    def test_intro_query_keeps_context_for_ocp_intro_request(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "overview",
                "5.2. self-managed edition",
                "OpenShift Container Platform (OCP) overview.",
                score=0.0208,
            ),
            _hit(
                "chunk-2",
                "updating_clusters",
                "1.2. update overview",
                "OCP update process overview.",
                score=0.0205,
            ),
            _hit(
                "chunk-3",
                "hosted_control_planes",
                "8.3.2. supported versions",
                "Hosted control planes supported versions.",
                score=0.019,
            ),
        ]

        bundle = assemble_context(
            hits,
            query="OCP 소개해줘",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("overview", bundle.citations[0].book_slug)

    def test_architecture_summary_query_keeps_context_without_explicit_ocp_token(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "architecture",
                "OpenShift Container Platform의 아키텍처 개요",
                "OpenShift 아키텍처 개요 설명",
                score=0.0177,
            ),
            _hit(
                "chunk-2",
                "architecture",
                "1.1. OpenShift Container Platform 아키텍처의 일반 용어집",
                "OpenShift 아키텍처 일반 용어 설명",
                score=0.0174,
            ),
            _hit(
                "chunk-3",
                "storage",
                "6.22.10.1. vSphere CSI 토폴로지 요구사항",
                "스토리지 관련 문서",
                score=0.0172,
            ),
        ]

        bundle = assemble_context(
            hits,
            query="아키텍처를 한 장으로 요약해줘",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("architecture", bundle.citations[0].book_slug)

    def test_kubernetes_compare_follow_up_keeps_context(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "installation_overview",
                "3.2.10.1. 프로젝트",
                "설치 개요 문서",
                score=0.0381,
            ),
            _hit(
                "chunk-2",
                "overview",
                "4.2. Kubernetes 리소스",
                "Kubernetes 리소스 설명",
                score=0.0370,
            ),
            _hit(
                "chunk-3",
                "overview",
                "7.1. 유사점 및 차이점",
                "OpenShift와 Kubernetes 차이 설명",
                score=0.0353,
            ),
        ]

        bundle = assemble_context(
            hits,
            query="쿠버네티스와 차이도 설명해줘",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertIn("overview", [citation.book_slug for citation in bundle.citations])

    def test_oc_login_low_score_bm25_hits_keep_context(self) -> None:
        hits = [
            _hit("chunk-1", "cli_tools", "2.6.1.90. oc login", "Use oc login with the API server.", score=0.0164),
            _hit(
                "chunk-2",
                "cli_tools",
                "2.1.4. Login to the OpenShift CLI by using a web browser",
                "The web browser flow helps you log in to the CLI.",
                score=0.0161,
            ),
            _hit(
                "chunk-3",
                "cli_tools",
                "2.2.2. Accessing kubeconfig by using the oc CLI",
                "The oc CLI can update kubeconfig after login.",
                score=0.0157,
            ),
            _hit(
                "chunk-4",
                "release_notes",
                "1.6.22. OpenShift CLI (oc)",
                "Release notes for the oc CLI.",
                score=0.0154,
            ),
        ]

        self.assertFalse(_should_force_clarification(hits, query="oc login usage"))
        bundle = assemble_context(hits, query="oc login usage", max_chunks=4)

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("cli_tools", bundle.citations[0].book_slug)

    def test_pod_pending_low_score_hits_keep_context_when_cli_and_nodes_align(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "cli_tools",
                "2.6.1.75. oc events",
                "Use oc events to inspect why a pod is pending.",
                score=0.0164,
            ),
            _hit(
                "chunk-2",
                "cli_tools",
                "2.6.1.72. oc describe",
                "Use oc describe pod to inspect scheduling failures.",
                score=0.0161,
            ),
            _hit(
                "chunk-3",
                "nodes",
                "4.10.3.3. Scheduling pods onto nodes",
                "Pod scheduling can fail because of resource pressure or constraints.",
                score=0.0159,
            ),
            _hit(
                "chunk-4",
                "authentication_and_authorization",
                "3.8. OAuth API event troubleshooting",
                "OAuth API event troubleshooting.",
                score=0.0155,
            ),
        ]

        self.assertFalse(_should_force_clarification(hits, query="Pod Pending meaning"))
        bundle = assemble_context(hits, query="Pod Pending meaning", max_chunks=4)

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("cli_tools", bundle.citations[0].book_slug)

    def test_pod_lifecycle_low_score_hits_keep_context_when_nodes_and_workloads_align(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "nodes",
                "2.1.2. Pod configuration examples",
                "Pod configuration includes restartPolicy and container settings.",
                score=0.0166,
            ),
            _hit(
                "chunk-2",
                "nodes",
                "7.2.1. Understanding init containers",
                "A pod can have init containers before app containers run.",
                score=0.0163,
            ),
            _hit(
                "chunk-3",
                "workloads_apis",
                "14.1.169. .spec.initContainers",
                "The Pod spec exposes initContainers and status fields.",
                score=0.016,
            ),
            _hit(
                "chunk-4",
                "edge_computing",
                "13.3. Topology Aware Lifecycle Manager installation",
                "Lifecycle Manager content that should not dominate pod lifecycle questions.",
                score=0.0152,
            ),
        ]

        self.assertFalse(_should_force_clarification(hits, query="Pod lifecycle concept"))
        bundle = assemble_context(hits, query="Pod lifecycle concept", max_chunks=4)

        self.assertNotEqual([], bundle.citations)
        self.assertIn(bundle.citations[0].book_slug, {"nodes", "workloads_apis"})
