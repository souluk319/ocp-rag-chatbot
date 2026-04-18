from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.retrieval.models import RetrievalHit, SessionContext
from play_book_studio.answering.context import _should_force_clarification, assemble_context


def _hit(
    chunk_id: str,
    book_slug: str,
    section: str,
    text: str,
    *,
    anchor: str | None = None,
    score: float = 1.0,
    source: str = "hybrid",
    component_scores: dict[str, float] | None = None,
    chunk_type: str = "reference",
    semantic_role: str = "unknown",
    cli_commands: tuple[str, ...] = (),
    source_collection: str = "core",
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
        source=source,
        raw_score=score,
        fused_score=score,
        chunk_type=chunk_type,
        semantic_role=semantic_role,
        cli_commands=cli_commands,
        source_collection=source_collection,
        component_scores=component_scores or {},
    )


class ContextAssemblyTests(unittest.TestCase):
    def test_assemble_context_seeds_uploaded_customer_pack_for_explicit_query(self) -> None:
        bundle = assemble_context(
            [
                _hit(
                    "uploaded-1",
                    "customer-backup-runbook",
                    "OpenShift Backup Restore Runbook",
                    "1. Enter debug shell\n/usr/local/bin/cluster-backup.sh /home/core/assets/backup",
                    score=0.022,
                    source_collection="uploaded",
                ),
                _hit(
                    "core-1",
                    "postinstallation_configuration",
                    "4.12.5. etcd 데이터 백업",
                    "공식 문서의 etcd 백업 절차입니다.",
                    score=0.026,
                    chunk_type="command",
                    semantic_role="procedure",
                    cli_commands=("oc debug --as-root node/<node_name>",),
                ),
            ],
            query="업로드 문서 기준으로 backup 절차를 알려줘",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("customer-backup-runbook", bundle.citations[0].book_slug)

    def test_assemble_context_seeds_uploaded_customer_pack_for_selected_draft_scope(self) -> None:
        bundle = assemble_context(
            [
                _hit(
                    "uploaded-1",
                    "customer-backup-runbook",
                    "OpenShift Backup Restore Runbook",
                    "1. Enter debug shell\n/usr/local/bin/cluster-backup.sh /home/core/assets/backup",
                    score=0.02,
                    source_collection="uploaded",
                ),
                _hit(
                    "core-1",
                    "postinstallation_configuration",
                    "4.12.5. etcd 데이터 백업",
                    "공식 문서의 etcd 백업 절차입니다.",
                    score=0.026,
                    chunk_type="command",
                    semantic_role="procedure",
                    cli_commands=("oc debug --as-root node/<node_name>",),
                ),
            ],
            query="backup 절차를 알려줘",
            session_context=SessionContext(
                selected_draft_ids=["dtb-demo"],
                restrict_uploaded_sources=True,
            ),
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("customer-backup-runbook", bundle.citations[0].book_slug)

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
        self.assertNotIn("security_and_compliance", [citation.book_slug for citation in bundle.citations])

    def test_generic_intro_prefers_intro_over_glossary_and_deep_architecture(self) -> None:
        bundle = assemble_context(
            [
                _hit(
                    "chunk-1",
                    "security_and_compliance",
                    "2.1.2. OpenShift Container Platform 용어집",
                    "OpenShift 관련 용어를 설명합니다.",
                    anchor="glossary",
                    score=0.039,
                ),
                _hit(
                    "chunk-2",
                    "architecture",
                    "2.1.3.1. 사용자 정의 운영 체제",
                    "RHCOS와 CRI-O를 설명합니다.",
                    anchor="custom-os",
                    score=0.038,
                ),
                _hit(
                    "chunk-3",
                    "architecture",
                    "2.1.3. OpenShift Container Platform 개요",
                    "OpenShift Container Platform 개요를 설명합니다.",
                    anchor="architecture-overview",
                    score=0.036,
                    semantic_role="overview",
                ),
                _hit(
                    "chunk-4",
                    "overview",
                    "OpenShift Container Platform 소개",
                    "OpenShift Platform 기능을 처음 설명합니다.",
                    anchor="ocp-overview",
                    score=0.035,
                    semantic_role="overview",
                ),
            ],
            query="오픈시프트가 뭐야?",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("overview", bundle.citations[0].book_slug)
        self.assertEqual("OpenShift Container Platform 소개", bundle.citations[0].section)

    def test_kubernetes_intro_prefers_intro_context_over_irrelevant_book(self) -> None:
        bundle = assemble_context(
            [
                _hit(
                    "chunk-1",
                    "release_notes",
                    "확인된 문제",
                    "이번 릴리스에서 확인된 문제를 설명합니다.",
                    anchor="known-issues",
                    score=0.041,
                ),
                _hit(
                    "chunk-2",
                    "architecture",
                    "2.1.3. OpenShift Container Platform 개요",
                    "OpenShift는 Kubernetes 기반 플랫폼입니다.",
                    anchor="architecture-overview",
                    score=0.037,
                    semantic_role="overview",
                ),
                _hit(
                    "chunk-3",
                    "overview",
                    "OpenShift Container Platform 소개",
                    "OpenShift와 Kubernetes 관계를 처음 설명합니다.",
                    anchor="ocp-overview",
                    score=0.036,
                    semantic_role="overview",
                ),
            ],
            query="쿠버네티스는뭔데",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertIn(bundle.citations[0].book_slug, {"overview", "architecture"})
        self.assertNotEqual("release_notes", bundle.citations[0].book_slug)

    def test_intro_recommendation_query_keeps_diverse_playbook_context(self) -> None:
        query = "운영 입문 기준으로 먼저 봐야 할 플레이북 3개를 알려줘"
        hits = [
            _hit(
                "chunk-1",
                "overview",
                "OpenShift Container Platform 소개",
                "처음 읽는 운영 입문용 개요입니다.",
                anchor="ocp-overview",
                score=0.021,
                semantic_role="overview",
            ),
            _hit(
                "chunk-2",
                "architecture",
                "1장. 아키텍처 개요",
                "플랫폼 구조를 이해하기 위한 아키텍처 개요입니다.",
                anchor="architecture-overview",
                score=0.0203,
                semantic_role="overview",
            ),
            _hit(
                "chunk-3",
                "installation_overview",
                "설치 개요",
                "설치 전반과 운영 진입 경로를 설명합니다.",
                anchor="installation-overview",
                score=0.0198,
                semantic_role="overview",
            ),
            _hit(
                "chunk-4",
                "release_notes",
                "확인된 문제",
                "릴리스 이슈 목록입니다.",
                anchor="known-issues",
                score=0.0196,
            ),
        ]

        self.assertFalse(_should_force_clarification(hits, query=query))
        bundle = assemble_context(hits, query=query, max_chunks=4)

        self.assertNotEqual([], bundle.citations)
        self.assertEqual(
            ["overview", "architecture", "installation_overview"],
            [citation.book_slug for citation in bundle.citations[:3]],
        )
        self.assertNotIn("release_notes", [citation.book_slug for citation in bundle.citations])

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

    def test_registry_storage_ops_query_keeps_context_even_when_books_compete(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "registry",
                "이미지 레지스트리 스토리지 구성",
                "이미지 레지스트리의 스토리지를 구성합니다.",
                score=-1.30,
                source="hybrid_reranked",
                component_scores={
                    "pre_rerank_fused_score": 0.044,
                    "reranker_score": -1.30,
                },
                chunk_type="procedure",
                semantic_role="procedure",
            ),
            _hit(
                "chunk-2",
                "images",
                "이미지 레지스트리 저장소 미러링 설정",
                "이미지 레지스트리 저장소 미러링 설정 절차입니다.",
                score=-1.25,
                source="hybrid_reranked",
                component_scores={
                    "pre_rerank_fused_score": 0.042,
                    "reranker_score": -1.25,
                },
                chunk_type="command",
                semantic_role="procedure",
                cli_commands=("oc create -f registryrepomirror.yaml",),
            ),
            _hit(
                "chunk-3",
                "installing_on_any_platform",
                "베어 메탈 및 기타 수동 설치에 대한 레지스트리 저장소 구성",
                "수동 설치 환경에서 이미지 레지스트리 저장소를 구성하는 절차입니다.",
                score=-1.22,
                source="hybrid_reranked",
                component_scores={
                    "pre_rerank_fused_score": 0.041,
                    "reranker_score": -1.22,
                },
                chunk_type="command",
                semantic_role="procedure",
                cli_commands=("oc edit configs.imageregistry/cluster",),
            ),
        ]

        query = "이미지 레지스트리 저장소를 구성하려면?"
        self.assertFalse(_should_force_clarification(hits, query=query))
        bundle = assemble_context(hits, query=query, max_chunks=4)

        self.assertNotEqual([], bundle.citations)
        self.assertIn(bundle.citations[0].book_slug, {"images", "installing_on_any_platform"})
        self.assertIn("images", [citation.book_slug for citation in bundle.citations])
        self.assertIn("installing_on_any_platform", [citation.book_slug for citation in bundle.citations])

    def test_route_ingress_follow_up_compare_keeps_context_even_when_books_compete(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "networking_overview",
                "1.3.1. Ingress 및 Route 오브젝트를 사용하여 애플리케이션 노출",
                "Route와 Ingress를 사용해 애플리케이션을 노출하는 방법을 설명합니다.",
                score=0.0182,
            ),
            _hit(
                "chunk-2",
                "overview",
                "4.3. Kubernetes 개념 가이드라인",
                "Kubernetes 개념과 비교 기준을 설명합니다.",
                score=0.0179,
            ),
            _hit(
                "chunk-3",
                "architecture",
                "1장. 아키텍처 개요",
                "OpenShift 플랫폼 개요입니다.",
                score=0.0176,
            ),
        ]

        bundle = assemble_context(
            hits,
            query="쿠버네티스와 차이도 설명해줘",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertIn(bundle.citations[0].book_slug, {"networking_overview", "overview"})

    def test_node_drain_context_prefers_nodes_support_family_over_shutdown_book(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "backup_and_restore",
                "2.2. Shutting down the cluster",
                "oc adm cordon <node> 로 종료 전 준비를 설명합니다.",
                score=1.0,
                chunk_type="procedure",
                semantic_role="procedure",
                cli_commands=("oc adm cordon <node>",),
            ),
            _hit(
                "chunk-2",
                "nodes",
                "6.2.1. 노드에서 Pod를 비우는 방법 이해",
                "oc adm drain worker-0 --ignore-daemonsets --delete-emptydir-data",
                score=0.92,
                chunk_type="command",
                semantic_role="procedure",
                cli_commands=("oc adm drain worker-0 --ignore-daemonsets --delete-emptydir-data",),
            ),
            _hit(
                "chunk-3",
                "support",
                "7.2.1. 노드 유지보수 절차",
                "drain 전후 점검 순서를 설명합니다.",
                score=0.9,
                chunk_type="procedure",
                semantic_role="procedure",
            ),
            _hit(
                "chunk-4",
                "cli_tools",
                "2.7.1.11. oc adm drain",
                "oc adm drain <node>",
                score=0.88,
                chunk_type="reference",
                semantic_role="procedure",
                cli_commands=("oc adm drain <node>",),
            ),
        ]

        bundle = assemble_context(
            hits,
            query="특정 작업자 노드 점검 때문에 비워야 해. drain 명령 예시랑 주의점만 짧게 줘",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertIn(bundle.citations[0].book_slug, {"nodes", "support"})
        self.assertNotIn("backup_and_restore", [citation.book_slug for citation in bundle.citations])

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
        self.assertIn(bundle.citations[0].book_slug, {"extensions", "overview"})
        self.assertNotIn("support", [citation.book_slug for citation in bundle.citations])

    def test_operator_concept_locks_context_to_operator_family_when_present(self) -> None:
        hits = [
            _hit("chunk-1", "operators", "2.4.1.2.6. Operator 상태", "Operator 상태와 관리", score=1.2319),
            _hit("chunk-2", "architecture", "1.1. OpenShift Container Platform 아키텍처의 일반 용어집", "Operator 정의", score=0.4559),
            _hit("chunk-3", "installation_overview", "3.2.16. OLM(Operator Lifecycle Manager) 클래식 기능", "OLM 기능 설명", score=0.3735),
            _hit("chunk-4", "operators", "2.4.4.5.1. 카탈로그 우선순위", "카탈로그 우선순위 설명", score=0.352),
        ]

        bundle = assemble_context(
            hits,
            query="Operator가 왜 필요한지 예시까지 설명해줘",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("operators", bundle.citations[0].book_slug)
        self.assertEqual(["operators"], [citation.book_slug for citation in bundle.citations])

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

        self.assertGreaterEqual(len(bundle.citations), 2)
        self.assertGreaterEqual(
            sum(int(citation.book_slug == "postinstallation_configuration") for citation in bundle.citations),
            2,
        )
        self.assertEqual("postinstallation_configuration", bundle.citations[0].book_slug)

    def test_cluster_node_usage_prefers_support_only_when_support_hits_exist(self) -> None:
        hits = [
            _hit("chunk-1", "nodes", "6.1.3. 노드의 메모리 및 CPU 사용량 통계 보기", "oc adm top nodes", score=0.043),
            _hit("chunk-2", "nodes", "6.1.3. 노드의 메모리 및 CPU 사용량 통계 보기", "oc adm top node <node>", score=0.041),
            _hit("chunk-3", "support", "7.2.1. 노드 상태, 리소스 사용량 및 구성 확인", "oc adm top nodes", score=0.039),
            _hit("chunk-4", "support", "7.2.1. 노드 상태, 리소스 사용량 및 구성 확인", "oc adm top node <node>", score=0.038),
        ]

        bundle = assemble_context(
            hits,
            query="지금 클러스터 전체 노드 CPU랑 메모리 사용량 한 번에 보려면 어떤 명령 써?",
            max_chunks=5,
        )

        self.assertEqual(
            ["support"] * len(bundle.citations),
            [citation.book_slug for citation in bundle.citations],
        )

    def test_backup_only_etcd_context_keeps_postinstall_and_etcd_companion(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "etcd",
                "4.3.2. etcd 백업 및 복원",
                "cluster-restore.sh",
                anchor="etcd-backup-restore",
                score=0.048,
            ),
            _hit(
                "chunk-2",
                "postinstallation_configuration",
                "4.12.5. etcd 데이터 백업",
                "cluster-backup.sh",
                anchor="etcd-backup",
                score=0.036,
            ),
            _hit(
                "chunk-3",
                "postinstallation_configuration",
                "4.12.5. etcd 데이터 백업",
                "oc debug --as-root node",
                anchor="etcd-backup",
                score=0.035,
            ),
        ]

        bundle = assemble_context(
            hits,
            query="etcd 백업은 실제로 어떤 절차로 해? 표준적인 방법만 짧게 알려줘",
            max_chunks=5,
        )

        self.assertEqual("postinstallation_configuration", bundle.citations[0].book_slug)
        self.assertIn("postinstallation_configuration", [citation.book_slug for citation in bundle.citations])
        self.assertIn("etcd", [citation.book_slug for citation in bundle.citations])

    def test_backup_only_etcd_context_allows_cross_book_mirror_companion(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "postinstallation_configuration",
                "4.12.5. etcd 데이터 백업",
                "cluster-backup.sh",
                anchor="etcd-backup",
                score=0.041,
            ),
            _hit(
                "chunk-2",
                "backup_and_restore",
                "4.12.5. etcd 데이터 백업",
                "같은 절차를 백업/복원 전용 문서에서도 설명합니다.",
                anchor="etcd-backup",
                score=0.039,
            ),
        ]

        bundle = assemble_context(
            hits,
            query="etcd 백업은 실제로 어떤 절차로 해?",
            max_chunks=4,
        )

        self.assertEqual(
            ["postinstallation_configuration", "backup_and_restore"],
            [citation.book_slug for citation in bundle.citations],
        )

    def test_reranked_hits_use_pre_rerank_score_for_context_cutoff(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "authentication_and_authorization",
                "9.6. 사용자 역할 추가",
                "oc adm policy add-role-to-user admin <user> -n <project>",
                score=-1.72,
                source="hybrid_reranked",
                component_scores={
                    "pre_rerank_fused_score": 0.046,
                    "reranker_score": -1.72,
                },
            ),
            _hit(
                "chunk-2",
                "postinstallation_configuration",
                "9.2.6. 사용자 역할 추가",
                "oc adm policy add-role-to-user admin <user> -n <project>",
                score=-1.81,
                source="hybrid_reranked",
                component_scores={
                    "pre_rerank_fused_score": 0.042,
                    "reranker_score": -1.81,
                },
            ),
        ]

        bundle = assemble_context(
            hits,
            query="특정 이름공간에 어드민 권한 주는법은?",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertEqual(
            "authentication_and_authorization",
            bundle.citations[0].book_slug,
        )

    def test_rbac_context_prefers_authorization_book_over_postinstall_mirror(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "postinstallation_configuration",
                "9.2.7. 로컬 역할 바인딩 예",
                "RoleBinding YAML 예시입니다.",
                score=0.044,
            ),
            _hit(
                "chunk-2",
                "authentication_and_authorization",
                "9.7. 로컬 역할 바인딩 예",
                "RoleBinding YAML 예시입니다.",
                score=0.042,
            ),
        ]

        bundle = assemble_context(
            hits,
            query="그 RoleBinding YAML 예시도 보여줘",
            max_chunks=4,
        )

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("authentication_and_authorization", bundle.citations[0].book_slug)

    def test_troubleshooting_doc_locator_prefers_support_path_over_release_notes_and_console(self) -> None:
        hits = [
            _hit(
                "chunk-1",
                "web_console",
                "10.5.3. 작업 단계",
                "문제 조사 흐름의 콘솔 단계 요약입니다.",
                score=-2.4,
                source="hybrid_reranked",
                component_scores={
                    "pre_rerank_fused_score": 0.1564,
                    "reranker_score": -2.4,
                },
            ),
            _hit(
                "chunk-2",
                "support",
                "7.7. Pod 문제 조사",
                "문제가 생기면 먼저 관련 상태와 이벤트를 조사합니다.",
                score=-2.9,
                source="hybrid_reranked",
                component_scores={
                    "pre_rerank_fused_score": 0.2063,
                    "reranker_score": -2.9,
                },
            ),
            _hit(
                "chunk-3",
                "release_notes",
                "1.9.8.2. 버그 수정",
                "해결된 이슈 목록입니다.",
                score=-2.8,
                source="hybrid_reranked",
                component_scores={
                    "pre_rerank_fused_score": 0.2069,
                    "reranker_score": -2.8,
                },
            ),
            _hit(
                "chunk-4",
                "support",
                "1.4. 문제 해결",
                "문제 유형별로 점검 순서를 안내합니다.",
                score=-3.0,
                source="hybrid_reranked",
                component_scores={
                    "pre_rerank_fused_score": 0.2060,
                    "reranker_score": -3.0,
                },
            ),
            _hit(
                "chunk-5",
                "validation_and_troubleshooting",
                "1.4. 클러스터 버전, 상태 및 업데이트 세부 정보 가져오기",
                "상태를 점검하는 기본 확인 절차입니다.",
                score=-3.1,
                source="hybrid_reranked",
                component_scores={
                    "pre_rerank_fused_score": 0.1912,
                    "reranker_score": -3.1,
                },
            ),
        ]

        query = "문제가 생기면 위키 안에서 어떤 순서로 이동해야 하는지 알려줘"
        self.assertFalse(_should_force_clarification(hits, query=query))
        bundle = assemble_context(hits, query=query, max_chunks=4)

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("support", bundle.citations[0].book_slug)
        self.assertNotIn("release_notes", [citation.book_slug for citation in bundle.citations])
