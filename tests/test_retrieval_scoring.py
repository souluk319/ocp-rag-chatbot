from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_retrieval import RetrievalHit, fuse_ranked_hits

class TestRetrievalScoring(unittest.TestCase):
    def test_fusion_penalizes_reference_books_for_concept_query(self) -> None:
        explainer_hit = RetrievalHit(
            chunk_id="pod-explainer",
            book_slug="nodes",
            chapter="nodes",
            section="2.1.1. Pod 이해",
            anchor="understanding-pods",
            source_url="https://example.com/nodes",
            viewer_path="/docs/ocp/4.20/ko/nodes/index.html#understanding-pods",
            text="Pod는 쿠버네티스에서 가장 작은 배포 단위이며 phase로 상태를 표현합니다.",
            source="vector",
            raw_score=0.9,
            fused_score=0.9,
        )
        api_hit = RetrievalHit(
            chunk_id="pod-api",
            book_slug="workloads_apis",
            chapter="apis",
            section="PodStatus API",
            anchor="podstatus",
            source_url="https://example.com/workloads-apis",
            viewer_path="/docs/ocp/4.20/ko/workloads_apis/index.html#podstatus",
            text="status.phase, status.conditions, containerStatuses 필드 설명",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )

        hits = fuse_ranked_hits(
            "Pod lifecycle 개념을 초보자 관점에서 설명해줘",
            {"bm25": [api_hit], "vector": [explainer_hit]},
            top_k=2,
        )

        self.assertEqual("nodes", hits[0].book_slug)

    def test_fusion_prefers_update_guide_books_for_update_doc_locator_query(self) -> None:
        cli_hit = RetrievalHit(
            chunk_id="cli-oc-explain",
            book_slug="cli_tools",
            chapter="cli",
            section="2.6.1.54. 리소스에 대한 문서 가져오기",
            anchor="oc-explain",
            source_url="https://example.com/cli",
            viewer_path="/docs/cli.html#oc-explain",
            text="oc explain 명령으로 리소스 문서를 가져옵니다.",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        updating_hit = RetrievalHit(
            chunk_id="update-guide",
            book_slug="updating_clusters",
            chapter="업데이트",
            section="1.2. 업데이트 전 준비",
            anchor="before-updating",
            source_url="https://example.com/updating",
            viewer_path="/docs/updating.html#before-updating",
            text="클러스터 업데이트 전에 확인해야 할 준비 사항과 가이드입니다.",
            source="vector",
            raw_score=0.94,
            fused_score=0.94,
        )
        release_hit = RetrievalHit(
            chunk_id="release-notes",
            book_slug="release_notes",
            chapter="릴리스 노트",
            section="릴리스 노트 개요",
            anchor="release-notes",
            source_url="https://example.com/release-notes",
            viewer_path="/docs/release-notes.html#release-notes",
            text="업데이트 전에 현재 버전의 릴리스 노트를 검토합니다.",
            source="bm25",
            raw_score=0.9,
            fused_score=0.9,
        )

        hits = fuse_ranked_hits(
            "업데이트 관련 문서는 뭐부터 보면 돼?",
            {"bm25": [cli_hit, release_hit], "vector": [updating_hit, cli_hit]},
            top_k=3,
        )

        self.assertEqual("updating_clusters", hits[0].book_slug)
        self.assertNotEqual("cli_tools", hits[0].book_slug)

    def test_fusion_diversifies_operator_concept_hits_across_books(self) -> None:
        extension_controller_hit = RetrievalHit(
            chunk_id="operator-controller",
            book_slug="extensions",
            chapter="extensions",
            section="2.2. Operator Controller",
            anchor="operator-controller",
            source_url="https://example.com/extensions",
            viewer_path="/docs/extensions.html#operator-controller",
            text="Operator controller가 리소스를 감시합니다.",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        extension_olm_hit = RetrievalHit(
            chunk_id="olm-components",
            book_slug="extensions",
            chapter="extensions",
            section="2.1. OLM v1 구성 요소 개요",
            anchor="olm-components",
            source_url="https://example.com/extensions",
            viewer_path="/docs/extensions.html#olm-components",
            text="OLM v1 구성 요소를 설명합니다.",
            source="vector",
            raw_score=0.97,
            fused_score=0.97,
        )
        overview_hit = RetrievalHit(
            chunk_id="operator-overview",
            book_slug="overview",
            chapter="overview",
            section="3.12. Operator",
            anchor="operator",
            source_url="https://example.com/overview",
            viewer_path="/docs/overview.html#operator",
            text="Operator는 반복적인 운영 작업을 자동화하는 패턴입니다.",
            source="bm25",
            raw_score=0.93,
            fused_score=0.93,
        )

        hits = fuse_ranked_hits(
            "Operator가 뭐고 왜 필요한가?",
            {
                "bm25": [extension_controller_hit, overview_hit],
                "vector": [extension_olm_hit, extension_controller_hit, overview_hit],
            },
            top_k=3,
        )

        self.assertIn("overview", [hit.book_slug for hit in hits[:3]])
        self.assertIn("extensions", [hit.book_slug for hit in hits[:3]])
        self.assertGreaterEqual(len({hit.book_slug for hit in hits[:3]}), 2)
    def test_fusion_penalizes_english_only_hit_for_korean_query(self) -> None:
        english_hit = RetrievalHit(
            chunk_id="en-hit",
            book_slug="monitoring",
            chapter="Monitoring",
            section="Monitoring",
            anchor="monitoring",
            source_url="https://example.com/en",
            viewer_path="/docs/en.html#monitoring",
            text="Monitoring stack configuration and alerts",
            source="bm25",
            raw_score=10.0,
            fused_score=10.0,
        )
        korean_hit = RetrievalHit(
            chunk_id="ko-hit",
            book_slug="monitoring",
            chapter="모니터링",
            section="모니터링",
            anchor="monitoring-ko",
            source_url="https://example.com/ko",
            viewer_path="/docs/ko.html#monitoring",
            text="모니터링 스택 구성과 경고 설정 방법",
            source="vector",
            raw_score=9.0,
            fused_score=9.0,
        )

        hits = fuse_ranked_hits(
            "모니터링 설정",
            {
                "bm25": [english_hit, korean_hit],
                "vector": [korean_hit, english_hit],
            },
            top_k=2,
        )

        self.assertEqual("ko-hit", hits[0].chunk_id)

    def test_fusion_prefers_architecture_overview_for_generic_intro_queries(self) -> None:
        lifecycle_hit = RetrievalHit(
            chunk_id="lifecycle-hit",
            book_slug="architecture",
            chapter="아키텍처",
            section="2.1.3.4. OpenShift Container Platform 라이프사이클",
            anchor="lifecycle",
            source_url="https://example.com/architecture",
            viewer_path="/docs/architecture.html#lifecycle",
            text="OpenShift Container Platform 라이프사이클을 설명합니다.",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        overview_hit = RetrievalHit(
            chunk_id="overview-hit",
            book_slug="architecture",
            chapter="아키텍처",
            section="OpenShift Container Platform의 아키텍처 개요",
            anchor="overview",
            source_url="https://example.com/architecture",
            viewer_path="/docs/architecture.html#overview",
            text="OpenShift Container Platform의 아키텍처 개요를 설명합니다.",
            source="vector",
            raw_score=1.0,
            fused_score=1.0,
        )

        hits = fuse_ranked_hits(
            "오픈시프트에 대해 세줄요약해봐",
            {
                "bm25": [lifecycle_hit],
                "vector": [overview_hit],
            },
            top_k=2,
        )

        self.assertEqual("overview-hit", hits[0].chunk_id)

    def test_fusion_prefers_architecture_glossary_for_pod_lifecycle_explainer(self) -> None:
        architecture_hit = RetrievalHit(
            chunk_id="pod-glossary-hit",
            book_slug="architecture",
            chapter="아키텍처",
            section="1.1. 일반 용어집",
            anchor="glossary-pod",
            source_url="https://example.com/architecture",
            viewer_path="/docs/architecture.html#glossary-pod",
            text="Pod는 Kubernetes에서 하나 이상의 컨테이너를 포함하는 가장 작은 배포 단위이며 Pod phase는 Pending, Running, Succeeded, Failed, Unknown 으로 표현됩니다.",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        api_hit = RetrievalHit(
            chunk_id="pod-api-hit",
            book_slug="workloads_apis",
            chapter="workloads APIs",
            section="PodStatus API 필드",
            anchor="podstatus",
            source_url="https://example.com/workloads-apis",
            viewer_path="/docs/workloads-apis.html#podstatus",
            text="status.phase 와 status.conditions 필드를 통해 Pod 상태를 표현합니다.",
            source="vector",
            raw_score=1.0,
            fused_score=1.0,
        )
        noisy_hit = RetrievalHit(
            chunk_id="node-status-hit",
            book_slug="security_and_compliance",
            chapter="보안",
            section="6.6.4. FileIntegrityNodeStatuses 오브젝트 이해",
            anchor="filenode-status",
            source_url="https://example.com/security",
            viewer_path="/docs/security.html#filenode-status",
            text="FileIntegrityNodeStatuses 는 노드 상태를 추적합니다.",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )

        hits = fuse_ranked_hits(
            "Pod lifecycle 개념을 초보자 기준으로 설명해줘",
            {
                "bm25": [noisy_hit, architecture_hit],
                "vector": [api_hit, architecture_hit],
            },
            top_k=3,
        )

        self.assertEqual("pod-glossary-hit", hits[0].chunk_id)

    def test_fusion_prefers_pod_understanding_over_operational_pod_failure_for_lifecycle(self) -> None:
        concept_hit = RetrievalHit(
            chunk_id="pod-understanding-hit",
            book_slug="nodes",
            chapter="노드",
            section="2.1.1. Pod 이해",
            anchor="pod-understanding",
            source_url="https://example.com/nodes",
            viewer_path="/docs/nodes.html#pod-understanding",
            text="Pod에는 라이프사이클이 정의되어 있으며 Pod는 변경할 수 없는 배포 단위입니다.",
            source="vector",
            raw_score=1.0,
            fused_score=1.0,
        )
        operational_hit = RetrievalHit(
            chunk_id="pod-evicted-hit",
            book_slug="nodes",
            chapter="노드",
            section="8.4.5. Pod 제거 이해",
            anchor="pod-evicted",
            source_url="https://example.com/nodes",
            viewer_path="/docs/nodes.html#pod-evicted",
            text="oc get pod test -o yaml 결과에서 Evicted 와 phase: Failed 를 확인합니다.",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )

        hits = fuse_ranked_hits(
            "Pod lifecycle 개념을 초보자 기준으로 설명해줘",
            {
                "bm25": [operational_hit],
                "vector": [concept_hit],
            },
            top_k=2,
        )

        self.assertEqual("pod-understanding-hit", hits[0].chunk_id)

    def test_fusion_deduplicates_intake_pod_command_sections_and_keeps_concept_hits(self) -> None:
        intake_command_a = RetrievalHit(
            chunk_id="dtb-a:oc-get-pods",
            book_slug="openshift-container-platform-4-16-getting-started-ko-kr",
            chapter="getting started",
            section="$ oc get pods",
            anchor="oc-get-pods",
            source_url="https://example.com/intake-a",
            viewer_path="/docs/intake/dtb-a/index.html#oc-get-pods",
            text="출력 예와 함께 oc get pods 결과를 보여 줍니다. [CODE] $ oc get pods [/CODE]",
            source="overlay_bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        intake_command_b = RetrievalHit(
            chunk_id="dtb-b:oc-get-pods",
            book_slug="openshift-container-platform-4-16-getting-started-ko-kr",
            chapter="getting started",
            section="$ oc get pods",
            anchor="oc-get-pods",
            source_url="https://example.com/intake-b",
            viewer_path="/docs/intake/dtb-b/index.html#oc-get-pods",
            text="출력 예와 함께 oc get pods 결과를 보여 줍니다. [CODE] $ oc get pods [/CODE]",
            source="overlay_bm25",
            raw_score=0.99,
            fused_score=0.99,
        )
        concept_hit = RetrievalHit(
            chunk_id="pod-understanding-hit",
            book_slug="nodes",
            chapter="노드",
            section="2.1.1. Pod 이해",
            anchor="pod-understanding",
            source_url="https://example.com/nodes",
            viewer_path="/docs/nodes.html#pod-understanding",
            text="Pod에는 라이프사이클이 정의되어 있으며 Pod는 변경할 수 없는 배포 단위입니다.",
            source="vector",
            raw_score=0.92,
            fused_score=0.92,
        )
        example_hit = RetrievalHit(
            chunk_id="pod-example-hit",
            book_slug="nodes",
            chapter="노드",
            section="2.1.2. Pod 구성의 예",
            anchor="pod-example",
            source_url="https://example.com/nodes",
            viewer_path="/docs/nodes.html#pod-example",
            text="Pod 정의에는 라이프사이클이 시작된 후 채워지는 특성이 있습니다.",
            source="vector",
            raw_score=0.9,
            fused_score=0.9,
        )

        hits = fuse_ranked_hits(
            "Pod lifecycle 개념을 초보자 기준으로 설명해줘",
            {
                "overlay_bm25": [intake_command_a, intake_command_b],
                "vector": [concept_hit, example_hit],
            },
            top_k=4,
            weights={"bm25": 1.0, "overlay_bm25": 1.35, "vector": 1.0},
        )

        self.assertEqual("pod-understanding-hit", hits[0].chunk_id)
        self.assertEqual(2, len([hit for hit in hits if hit.book_slug == "nodes"]))
        self.assertEqual(1, len([hit for hit in hits if hit.section == "$ oc get pods"]))

    def test_fusion_boosts_books_supported_by_bm25_and_vector(self) -> None:
        vector_only_hit = RetrievalHit(
            chunk_id="nodes-hit",
            book_slug="nodes",
            chapter="nodes",
            section="기본 인증 보안 생성",
            anchor="nodes-security",
            source_url="https://example.com/nodes",
            viewer_path="/docs/nodes.html#nodes-security",
            text="기본 인증 보안 생성 절차",
            source="vector",
            raw_score=0.52,
            fused_score=0.52,
        )
        security_vector_hit = RetrievalHit(
            chunk_id="security-vector-hit",
            book_slug="security_and_compliance",
            chapter="security",
            section="기본 통신 인증서 교체",
            anchor="default-cert",
            source_url="https://example.com/security-cert",
            viewer_path="/docs/security.html#default-cert",
            text="보안과 인증서 기본 구성을 설명합니다.",
            source="vector",
            raw_score=0.51,
            fused_score=0.51,
        )
        security_bm25_hit = RetrievalHit(
            chunk_id="security-bm25-hit",
            book_slug="security_and_compliance",
            chapter="security",
            section="클러스터 이벤트 감시",
            anchor="cluster-events",
            source_url="https://example.com/security-events",
            viewer_path="/docs/security.html#cluster-events",
            text="보안 관련 기본 문서와 운영 중점 항목",
            source="bm25",
            raw_score=13.0,
            fused_score=13.0,
        )

        hits = fuse_ranked_hits(
            "보안 관련 기본 문서는 뭐가 중요해?",
            {
                "bm25": [security_bm25_hit],
                "vector": [vector_only_hit, security_vector_hit],
            },
            top_k=3,
        )

        self.assertEqual("security_and_compliance", hits[0].book_slug)

    def test_fusion_prefers_pod_troubleshooting_sections_for_crash_loop_question(self) -> None:
        noisy_support_hit = RetrievalHit(
            chunk_id="cli-log-hit",
            book_slug="support",
            chapter="support",
            section="7.12.1. OpenShift CLI (oc) 로그 수준 이해",
            anchor="oc-log-levels",
            source_url="https://example.com/support-cli",
            viewer_path="/docs/support.html#oc-log-levels",
            text="oc 명령 관련 문제가 발생하면 oc 로그 수준을 높여 API 요청과 curl 요청 세부 정보를 확인할 수 있습니다.",
            source="vector",
            raw_score=0.93,
            fused_score=0.93,
        )
        pod_diag_hit = RetrievalHit(
            chunk_id="app-diag-hit",
            book_slug="support",
            chapter="support",
            section="7.8.3. 애플리케이션 오류 조사를 위한 애플리케이션 진단 데이터 수집",
            anchor="app-diag",
            source_url="https://example.com/support-app-diag",
            viewer_path="/docs/support.html#app-diag",
            text="애플리케이션 Pod와 관련된 이벤트를 확인하려면 oc describe pod 를 실행하고, 로그는 oc logs -f pod/<pod-name> 로 검토합니다.",
            source="bm25",
            raw_score=0.88,
            fused_score=0.88,
        )
        oom_hit = RetrievalHit(
            chunk_id="oom-hit",
            book_slug="nodes",
            chapter="nodes",
            section="8.4.4. OOM 종료 정책 이해",
            anchor="oom",
            source_url="https://example.com/nodes-oom",
            viewer_path="/docs/nodes.html#oom",
            text="Pod 상태에서 reason: OOMKilled 와 restartCount 를 확인하고 oc get pod -o yaml 로 마지막 종료 상태를 봅니다.",
            source="vector",
            raw_score=0.86,
            fused_score=0.86,
        )

        hits = fuse_ranked_hits(
            "CrashLoopBackOff가 반복될 때 확인 순서를 단계적으로 설명해줘 CrashLoopBackOff restartCount OOMKilled ImagePullBackOff events describe logs",
            {
                "bm25": [pod_diag_hit, noisy_support_hit, oom_hit],
                "vector": [noisy_support_hit, oom_hit, pod_diag_hit],
            },
            top_k=3,
        )

        self.assertEqual("app-diag-hit", hits[0].chunk_id)
        self.assertNotEqual("cli-log-hit", hits[0].chunk_id)

    def test_fusion_penalizes_operator_image_pull_sections_for_crash_loop_question(self) -> None:
        operator_hit = RetrievalHit(
            chunk_id="operator-imagepull-hit",
            book_slug="support",
            chapter="support",
            section="7.6.3. CLI를 사용하여 Operator 카탈로그 소스 상태 보기",
            anchor="catalog-source",
            source_url="https://example.com/support-operator",
            viewer_path="/docs/support.html#catalog-source",
            text="example-catalog pod 상태는 ImagePullBackOff 입니다. oc describe pod example-catalog -n openshift-marketplace 로 카탈로그 소스 상태를 확인합니다.",
            source="vector",
            raw_score=0.94,
            fused_score=0.94,
        )
        app_diag_hit = RetrievalHit(
            chunk_id="app-diag-hit",
            book_slug="support",
            chapter="support",
            section="7.8.3. 애플리케이션 오류 조사를 위한 애플리케이션 진단 데이터 수집",
            anchor="app-diag",
            source_url="https://example.com/support-app-diag",
            viewer_path="/docs/support.html#app-diag",
            text="애플리케이션 Pod 이벤트를 보고 oc describe pod 와 oc logs -f 를 통해 CrashLoopBackOff 원인을 추적합니다.",
            source="bm25",
            raw_score=0.86,
            fused_score=0.86,
        )
        oom_hit = RetrievalHit(
            chunk_id="oom-hit",
            book_slug="nodes",
            chapter="nodes",
            section="8.4.4. OOM 종료 정책 이해",
            anchor="oom",
            source_url="https://example.com/nodes-oom",
            viewer_path="/docs/nodes.html#oom",
            text="restartCount 와 OOMKilled 를 확인하고 oc get pod -o yaml 로 종료 상태를 봅니다.",
            source="vector",
            raw_score=0.84,
            fused_score=0.84,
        )

        hits = fuse_ranked_hits(
            "CrashLoopBackOff가 반복될 때 원인 추적 순서를 알려줘 CrashLoopBackOff restartCount OOMKilled events describe logs",
            {
                "bm25": [app_diag_hit, operator_hit, oom_hit],
                "vector": [operator_hit, app_diag_hit, oom_hit],
            },
            top_k=3,
        )

        self.assertEqual("app-diag-hit", hits[0].chunk_id)
        self.assertNotEqual("operator-imagepull-hit", hits[0].chunk_id)

    def test_fusion_prefers_architecture_for_generic_openshift_intro_query(self) -> None:
        architecture_hit = RetrievalHit(
            chunk_id="architecture-hit",
            book_slug="architecture",
            chapter="architecture",
            section="OpenShift Container Platform 아키텍처 개요",
            anchor="architecture-overview",
            source_url="https://example.com/architecture",
            viewer_path="/docs/architecture.html#overview",
            text="OpenShift Container Platform 아키텍처 개요와 기본 개념",
            source="vector",
            raw_score=0.70,
            fused_score=0.70,
        )
        networking_hit = RetrievalHit(
            chunk_id="networking-hit",
            book_slug="networking_overview",
            chapter="networking",
            section="OpenShift Container Platform 기본 네트워크 개념",
            anchor="networking-overview",
            source_url="https://example.com/networking",
            viewer_path="/docs/networking.html#overview",
            text="OpenShift Container Platform 기본 네트워크 개념과 일반 작업 이해",
            source="bm25",
            raw_score=0.72,
            fused_score=0.72,
        )

        hits = fuse_ranked_hits(
            "오픈시프트 OpenShift 소개 overview architecture 기본 개념",
            {
                "bm25": [networking_hit, architecture_hit],
                "vector": [architecture_hit, networking_hit],
            },
            top_k=2,
        )

        self.assertEqual("architecture", hits[0].book_slug)

    def test_fusion_penalizes_feature_sections_for_basic_ocp_intro_query(self) -> None:
        feature_hit = RetrievalHit(
            chunk_id="feature-hit",
            book_slug="architecture",
            chapter="architecture",
            section="2.1.3.3. 기타 주요 기능",
            anchor="features",
            source_url="https://example.com/architecture",
            viewer_path="/docs/architecture.html#features",
            text="Operator 기반 관리와 배포 기능을 설명합니다.",
            source="bm25",
            raw_score=0.78,
            fused_score=0.78,
        )
        overview_hit = RetrievalHit(
            chunk_id="overview-hit",
            book_slug="architecture",
            chapter="architecture",
            section="1장. 아키텍처 개요",
            anchor="overview",
            source_url="https://example.com/architecture",
            viewer_path="/docs/architecture.html#overview",
            text="OpenShift Container Platform의 기본 개념과 정의를 설명합니다.",
            source="vector",
            raw_score=0.72,
            fused_score=0.72,
        )

        hits = fuse_ranked_hits(
            "OCP가뭐야 OpenShift Container Platform 개요 overview 소개 architecture 기본 개념",
            {
                "bm25": [feature_hit, overview_hit],
                "vector": [overview_hit, feature_hit],
            },
            top_k=2,
        )

        self.assertEqual("overview-hit", hits[0].chunk_id)
