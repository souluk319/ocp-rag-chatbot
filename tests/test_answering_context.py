from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.retrieval.models import RetrievalHit
from play_book_studio.answering.context import _should_force_clarification, assemble_context


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

    def test_follow_up_query_keeps_context_even_when_scores_are_close(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "support",
                "7.6.6.2. CLI를 사용하여 Machine Config Operator가 자동으로 재부팅되지 않도록 비활성화",
                "MachineConfigPool spec.paused 필드를 true 로 설정합니다.",
                score=0.0166,
            ),
            _hit(
                "chunk-2",
                "network_security",
                "6장. IPsec 암호화 구성",
                "재부팅 작업이 두 번 발생할 수 있습니다.",
                score=0.0161,
            ),
            _hit(
                "chunk-3",
                "updating_clusters",
                "1.4.1. 업데이트 기간에 영향을 미치는 요소",
                "MCO 새 머신 구성으로 컴퓨팅 노드를 재부팅합니다.",
                score=0.0159,
            ),
        ]

        self.assertFalse(_should_force_clarification(hits, query="그 설정은 어디서 바꿔?"))
        bundle = assemble_context(hits, query="그 설정은 어디서 바꿔?", max_chunks=4)
        self.assertNotEqual([], bundle.citations)
        self.assertEqual("support", bundle.citations[0].book_slug)

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

    def test_mco_concept_prefers_architecture_family_over_support(self) -> None:
        hits = [
            _hit("chunk-1", "support", "7.6.6.2. CLI 사용", "spec.paused 로 재부팅을 막습니다.", score=0.041),
            _hit("chunk-2", "architecture", "6.1. 머신 구성 풀을 사용한 노드 구성 관리", "Machine Config Operator 와 MCP 역할", score=0.038),
            _hit("chunk-3", "overview", "6장. OpenShift Container Platform의 일반 용어집", "MCO 정의", score=0.037),
            _hit("chunk-4", "machine_management", "8.1.4. 인프라 머신의 머신 구성 풀 생성", "MachineConfigPool 설명", score=0.036),
        ]

        bundle = assemble_context(
            hits,
            query="Machine Config Operator가 뭐야?",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertIn(bundle.citations[0].book_slug, {"architecture", "overview", "machine_management"})

    def test_pod_lifecycle_concept_keeps_context_and_prefers_explainer_sections(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "nodes",
                "2.1.1. Pod 이해",
                "Pod에는 라이프사이클이 정의되어 있으며 Pod는 변경할 수 없는 배포 단위입니다.",
                score=0.031,
            ),
            _hit(
                "chunk-2",
                "nodes",
                "2.1.2. Pod 구성의 예",
                "Pod 정의에는 라이프사이클이 시작된 후 채워지는 특성이 있습니다.",
                score=0.029,
            ),
            _hit(
                "chunk-3",
                "workloads_apis",
                "14.1.324. .status",
                "PodStatus는 Pod 상태에 대한 정보를 나타냅니다.",
                score=0.027,
            ),
        ]

        bundle = assemble_context(
            hits,
            query="Pod lifecycle 개념을 초보자 기준으로 설명해줘",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("nodes", bundle.citations[0].book_slug)
        self.assertEqual("2.1.1. Pod 이해", bundle.citations[0].section)

    def test_crash_loop_context_prefers_general_diagnostics_and_avoids_duplicate_oom_section(self) -> None:
        hits = [
            _hit(
                "chunk-0",
                "support",
                "7.6.3. CLI를 사용하여 Operator 카탈로그 소스 상태 보기",
                "example-catalog pod 상태는 ImagePullBackOff 이며 openshift-marketplace 네임스페이스에서 oc describe pod 로 확인합니다.",
                score=0.043,
            ),
            _hit(
                "chunk-1",
                "nodes",
                "8.4.4. OOM 종료 정책 이해",
                "oc get pod -o yaml 로 OOMKilled 와 restartCount 를 확인합니다.",
                score=0.041,
            ),
            _hit(
                "chunk-2",
                "nodes",
                "8.4.4. OOM 종료 정책 이해",
                "lastState.terminated.reason 이 OOMKilled 인지 확인합니다.",
                score=0.039,
            ),
            _hit(
                "chunk-3",
                "support",
                "7.8.3. 애플리케이션 오류 조사를 위한 애플리케이션 진단 데이터 수집",
                "애플리케이션 Pod 이벤트를 보고 oc describe pod 와 oc logs -f 를 사용합니다.",
                score=0.038,
            ),
            _hit(
                "chunk-4",
                "nodes",
                "8.1.3. 이벤트 목록",
                "BackOff 이벤트와 Failed 이벤트를 통해 재시작 실패를 확인합니다.",
                score=0.036,
            ),
        ]

        bundle = assemble_context(
            hits,
            query="CrashLoopBackOff가 반복될 때 확인 순서를 단계적으로 설명해줘",
            max_chunks=5,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("support", bundle.citations[0].book_slug)
        self.assertIn("애플리케이션 오류 조사", bundle.citations[0].section)
        self.assertTrue(
            all("카탈로그 소스 상태 보기" not in citation.section for citation in bundle.citations)
        )
        self.assertEqual(
            1,
            sum(int(c.section == "8.4.4. OOM 종료 정책 이해") for c in bundle.citations),
        )

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
