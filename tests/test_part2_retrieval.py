from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.shared.settings import Settings
from ocp_rag.retrieval.bm25 import BM25Index
from ocp_rag.retrieval.models import ProcedureMemory, RetrievalHit, SessionContext, TurnMemory
from ocp_rag.retrieval.query import (
    decompose_retrieval_queries,
    detect_out_of_corpus_version,
    detect_unsupported_product,
    has_cluster_node_usage_intent,
    has_follow_up_reference,
    has_logging_ambiguity,
    has_node_drain_intent,
    has_project_scoped_rbac_intent,
    has_rbac_assignment_intent,
    has_rbac_intent,
    has_update_doc_locator_ambiguity,
    normalize_query,
    query_book_adjustments,
    rewrite_query,
)
from ocp_rag.retrieval.retriever import Part2Retriever, fuse_ranked_hits


class RetrievalTests(unittest.TestCase):
    def test_decompose_retrieval_queries_splits_compare_question(self) -> None:
        queries = decompose_retrieval_queries("오픈시프트와 쿠버네티스 차이를 세 줄로 설명해줘")

        self.assertEqual(
            [
                "오픈시프트와 쿠버네티스 차이를 세 줄로 설명해줘",
                "오픈시프트 개요",
                "쿠버네티스 개요",
            ],
            queries,
        )

    def test_decompose_retrieval_queries_splits_multi_part_question(self) -> None:
        queries = decompose_retrieval_queries("etcd는 뭐고 그리고 백업은 어떻게 해?")

        self.assertEqual(
            [
                "etcd는 뭐고 그리고 백업은 어떻게 해?",
                "etcd는 뭐고",
                "백업은 어떻게 해?",
            ],
            queries,
        )

    def test_bm25_prefers_matching_korean_chunk(self) -> None:
        rows = [
            {
                "chunk_id": "chunk-etcd",
                "book_slug": "backup_and_restore",
                "chapter": "백업",
                "section": "etcd 백업",
                "anchor": "etcd-backup",
                "source_url": "https://example.com/backup",
                "viewer_path": "/docs/backup.html#etcd-backup",
                "text": "OpenShift etcd 백업과 복구 절차를 설명합니다.",
            },
            {
                "chunk_id": "chunk-route",
                "book_slug": "ingress_and_load_balancing",
                "chapter": "네트워크",
                "section": "Route",
                "anchor": "route",
                "source_url": "https://example.com/route",
                "viewer_path": "/docs/route.html#route",
                "text": "Route와 Ingress 차이를 설명합니다.",
            },
        ]
        index = BM25Index.from_rows(rows)

        hits = index.search("etcd 백업 방법", top_k=2)

        self.assertEqual("chunk-etcd", hits[0].chunk_id)

    def test_rewrite_query_uses_session_context_for_follow_up(self) -> None:
        context = SessionContext(
            current_topic="etcd 백업",
            ocp_version="4.20",
            unresolved_question="백업 이후 복구 절차",
        )

        rewritten = rewrite_query("그거 복구는?", context)

        self.assertIn("etcd 백업", rewritten)
        self.assertIn("4.20", rewritten)
        self.assertIn("그거 복구는?", rewritten)

    def test_rewrite_query_uses_session_context_for_short_implicit_follow_up(self) -> None:
        context = SessionContext(
            current_topic="etcd 백업",
            ocp_version="4.20",
            unresolved_question="백업 이후 복구 절차",
        )

        rewritten = rewrite_query("복구는?", context)

        self.assertIn("etcd 백업", rewritten)
        self.assertIn("4.20", rewritten)
        self.assertIn("복구는?", rewritten)

    def test_rewrite_query_uses_recent_turn_capsules_for_long_follow_up(self) -> None:
        context = SessionContext(
            ocp_version="4.20",
            current_topic="RBAC",
            recent_turns=[
                TurnMemory(query=f"이전 질문 {index}", topic=f"주제 {index}")
                for index in range(1, 12)
            ],
            reference_hints=["1번=authentication_and_authorization · 9.6. 사용자 역할 추가"],
        )

        rewritten = rewrite_query("그거는 왜 그렇게 해?", context)

        self.assertIn("최근 대화 캡슐", rewritten)
        self.assertIn("이전 질문 10 -> 주제 10", rewritten)
        self.assertIn("1번=authentication_and_authorization", rewritten)

    def test_rewrite_query_does_not_force_prior_topic_for_explicit_new_topic(self) -> None:
        context = SessionContext(
            current_topic="2.1.3. 클러스터 업데이트 전 etcd 백업",
            ocp_version="4.20",
        )

        rewritten = rewrite_query("오픈시프트에 대해 새줄약해봐", context)

        self.assertEqual("오픈시프트에 대해 새줄약해봐", rewritten)

    def test_rewrite_query_uses_step_and_command_ledger_for_follow_up(self) -> None:
        context = SessionContext(
            current_topic="RBAC",
            ocp_version="4.20",
            topic_journal=["OpenShift", "RBAC"],
            reference_hints=["authentication_and_authorization · 9.6. 사용자 역할 추가"],
            recent_steps=["명령을 통해 역할 바인딩 추가", "적용 결과 확인"],
            recent_commands=["oc adm policy add-role-to-user admin <user> -n <namespace>"],
        )

        rewritten = rewrite_query("2번 단계에서 그 명령 확인은?", context)

        self.assertIn("참조 단계 적용 결과 확인", rewritten)
        self.assertIn("최근 명령", rewritten)
        self.assertIn("최근 근거 메모", rewritten)

    def test_rewrite_query_uses_procedure_memory_for_next_step_follow_up(self) -> None:
        context = SessionContext(
            current_topic="RBAC",
            ocp_version="4.20",
            procedure_memory=ProcedureMemory(
                goal="namespace admin 권한 부여",
                steps=["역할 바인딩 추가", "적용 결과 확인", "권한 검증"],
                active_step_index=0,
                step_commands=[
                    "oc adm policy add-role-to-user admin alice -n joe",
                    "oc describe rolebinding -n joe",
                    "oc auth can-i create pods -n joe --as alice",
                ],
                references=["authentication_and_authorization · 9.6. 사용자 역할 추가"],
            ),
        )

        rewritten = rewrite_query("다음은?", context)

        self.assertIn("절차 목표 namespace admin 권한 부여", rewritten)
        self.assertIn("절차 참조 단계 2. 적용 결과 확인", rewritten)

    def test_rewrite_query_uses_procedure_step_command_for_step_specific_follow_up(self) -> None:
        context = SessionContext(
            current_topic="RBAC",
            ocp_version="4.20",
            procedure_memory=ProcedureMemory(
                goal="namespace admin 권한 부여",
                steps=["역할 바인딩 추가", "적용 결과 확인"],
                active_step_index=0,
                step_commands=[
                    "oc adm policy add-role-to-user admin alice -n joe",
                    "oc describe rolebinding -n joe",
                ],
                references=["authentication_and_authorization · 9.6. 사용자 역할 추가"],
            ),
        )

        rewritten = rewrite_query("2번 단계 확인 명령은?", context)

        self.assertIn("절차 참조 단계 2. 적용 결과 확인", rewritten)
        self.assertIn("절차 단계 명령 oc describe rolebinding -n joe", rewritten)

    def test_normalize_query_expands_high_value_aliases(self) -> None:
        normalized = normalize_query("로그는 어디서 봐?")

        self.assertIn("로깅", normalized)
        self.assertIn("logging", normalized)

    def test_normalize_query_expands_security_and_architecture_aliases(self) -> None:
        normalized = normalize_query("보안 아키텍처 기본 문서")

        self.assertIn("security", normalized)
        self.assertIn("architecture", normalized)
        self.assertIn("overview", normalized)

    def test_normalize_query_expands_architecture_explainer_prompt(self) -> None:
        normalized = normalize_query("오픈시프트 아키텍처를 설명해줘")

        self.assertIn("OpenShift", normalized)
        self.assertIn("architecture", normalized)
        self.assertIn("overview", normalized)

    def test_normalize_query_treats_openshift_summary_as_intro_query(self) -> None:
        normalized = normalize_query("오픈시프트에 대해 세줄요약해봐")

        self.assertIn("OpenShift", normalized)
        self.assertIn("overview", normalized)
        self.assertIn("소개", normalized)

    def test_normalize_query_treats_ocp_attached_korean_explainer_as_intro_query(self) -> None:
        normalized = normalize_query("OCP가뭐야")

        self.assertIn("OpenShift", normalized)
        self.assertIn("Container", normalized)
        self.assertIn("Platform", normalized)
        self.assertIn("overview", normalized)
        self.assertIn("소개", normalized)

    def test_normalize_query_expands_openshift_kubernetes_compare_intent(self) -> None:
        normalized = normalize_query("오픈시프트와 쿠버네티스 차이를 세 줄로 설명해줘")

        self.assertIn("OpenShift", normalized)
        self.assertIn("Kubernetes", normalized)
        self.assertIn("comparison", normalized)
        self.assertIn("difference", normalized)

    def test_normalize_query_expands_etcd_backup_intent(self) -> None:
        normalized = normalize_query("etcd 백업은 어떻게 해?")

        self.assertIn("backup", normalized)
        self.assertIn("restore", normalized)

    def test_normalize_query_expands_certificate_monitor_intent(self) -> None:
        normalized = normalize_query("ocp api 서버 인증서 만료 임박했는지 어떻게 확인해?")

        self.assertIn("monitor-certificates", normalized)
        self.assertIn("ocp-certificates", normalized)
        self.assertIn("certificate", normalized)

    def test_normalize_query_expands_project_rbac_assignment_intent(self) -> None:
        query = "특정 프로젝트에 신규 사용자 admin 권한을 주고 싶어. RBAC 설정 방법 알려줘."

        normalized = normalize_query(query)

        self.assertTrue(has_rbac_intent(query))
        self.assertTrue(has_project_scoped_rbac_intent(query))
        self.assertTrue(has_rbac_assignment_intent(query))
        self.assertIn("rolebinding", normalized)
        self.assertIn("project", normalized)
        self.assertIn("namespace", normalized)
        self.assertIn("add-role-to-user", normalized)
        self.assertIn("admin", normalized)

    def test_rbac_intent_accepts_natural_role_assignment_runbook_query(self) -> None:
        query = "alice 사용자에게 joe namespace admin 역할을 부여하고 확인하는 절차를 단계별로 알려줘"

        normalized = normalize_query(query)

        self.assertTrue(has_rbac_intent(query))
        self.assertTrue(has_project_scoped_rbac_intent(query))
        self.assertTrue(has_rbac_assignment_intent(query))
        self.assertIn("rolebinding", normalized)
        self.assertIn("namespace", normalized)
        self.assertIn("add-role-to-user", normalized)

    def test_normalize_query_expands_project_finalizer_cleanup_terms(self) -> None:
        normalized = normalize_query(
            "프로젝트를 oc delete로 지웠는데 계속 Terminating 상태야. finalizers 강제 제거 전에 걸린 리소스부터 찾고 싶어."
        )

        self.assertIn("Terminating", normalized)
        self.assertIn("finalizers", normalized)
        self.assertIn("metadata.finalizers", normalized)
        self.assertIn("error resolving", normalized)

    def test_normalize_query_expands_mco_acronym_concept_terms(self) -> None:
        normalized = normalize_query("MCO가 뭐고 건드리면 뭐가 바뀌는지 설명해줘")

        self.assertIn("Machine", normalized)
        self.assertIn("Operator", normalized)
        self.assertIn("machineconfigpool", normalized)
        self.assertIn("Ignition", normalized)

    def test_normalize_query_expands_node_drain_terms(self) -> None:
        normalized = normalize_query("특정 작업자 노드를 drain 해야 해. 예시 명령이 뭐야?")

        self.assertTrue(has_node_drain_intent("특정 작업자 노드를 drain 해야 해. 예시 명령이 뭐야?"))
        self.assertIn("oc", normalized)
        self.assertIn("drain", normalized)
        self.assertIn("ignore-daemonsets", normalized)

    def test_normalize_query_expands_cluster_node_usage_terms(self) -> None:
        normalized = normalize_query("지금 클러스터 전체 노드 CPU랑 메모리 사용량 보려면 어떤 명령 써?")

        self.assertTrue(has_cluster_node_usage_intent("지금 클러스터 전체 노드 CPU랑 메모리 사용량 보려면 어떤 명령 써?"))
        self.assertIn("oc", normalized)
        self.assertIn("top", normalized)
        self.assertIn("nodes", normalized)

    def test_normalize_query_keeps_etcd_explainer_separate_from_backup_restore(self) -> None:
        normalized = normalize_query("etcd가 왜 중요한지 설명해줘")

        self.assertIn("quorum", normalized)
        self.assertIn("cluster", normalized)
        self.assertNotIn("backup", normalized)
        self.assertNotIn("restore", normalized)

    def test_query_book_adjustments_boost_backup_docs_for_doc_locator(self) -> None:
        boosts, penalties = query_book_adjustments("백업 복구 문서는 어디서 봐?")

        self.assertGreater(boosts["backup_and_restore"], 1.0)
        self.assertGreater(boosts["etcd"], 1.0)
        self.assertGreater(boosts["postinstallation_configuration"], 1.0)
        self.assertLess(penalties["hosted_control_planes"], 1.0)
        self.assertNotIn("backup_and_restore", penalties)

    def test_query_book_adjustments_boosts_standard_etcd_restore_family_for_follow_up_context(self) -> None:
        boosts, penalties = query_book_adjustments(
            "그 복구는 어떻게 해?",
            context=SessionContext(
                current_topic="etcd 백업",
                unresolved_question="etcd 백업 이후 복구 절차",
                ocp_version="4.20",
            ),
        )

        self.assertGreater(boosts["postinstallation_configuration"], 1.0)
        self.assertGreater(boosts["etcd"], 1.0)
        self.assertLess(penalties["hosted_control_planes"], 1.0)

    def test_query_book_adjustments_boost_auth_docs_for_project_rbac_assignment(self) -> None:
        boosts, penalties = query_book_adjustments(
            "특정 프로젝트에 신규 사용자 admin 권한을 주고 싶어. RBAC 설정 방법 알려줘."
        )

        self.assertGreater(boosts["authentication_and_authorization"], 1.0)
        self.assertGreater(boosts["tutorials"], 1.0)
        self.assertGreater(boosts["postinstallation_configuration"], 1.0)
        self.assertLess(penalties["role_apis"], 1.0)
        self.assertLess(penalties["project_apis"], 1.0)

    def test_query_book_adjustments_boost_cli_tools_for_certificate_monitoring(self) -> None:
        boosts, penalties = query_book_adjustments(
            "ocp api 서버 인증서 만료 임박했는지 어떻게 확인해?"
        )

        self.assertGreater(boosts["cli_tools"], 1.0)
        self.assertLess(penalties["security_and_compliance"], 1.0)

    def test_query_book_adjustments_penalize_cli_style_books_for_generic_intro(self) -> None:
        boosts, penalties = query_book_adjustments("오픈시프트에 대해 세줄요약해봐")

        self.assertGreater(boosts["architecture"], 1.0)
        self.assertGreater(boosts["overview"], 1.0)
        self.assertLess(penalties["tutorials"], 1.0)
        self.assertLess(penalties["cli_tools"], 1.0)

    def test_query_book_adjustments_treat_ocp_attached_korean_explainer_as_intro(self) -> None:
        boosts, penalties = query_book_adjustments("OCP가뭐야")

        self.assertGreater(boosts["architecture"], 1.0)
        self.assertGreater(boosts["overview"], 1.0)
        self.assertLess(penalties["tutorials"], 1.0)
        self.assertLess(penalties["cli_tools"], 1.0)

    def test_query_book_adjustments_boost_architecture_for_mco_concept(self) -> None:
        boosts, penalties = query_book_adjustments("MCO가 뭐고 건드리면 뭐가 바뀌는지 설명해줘")

        self.assertGreater(boosts["architecture"], 1.0)
        self.assertGreater(boosts["machine_configuration"], 1.0)
        self.assertLess(penalties["support"], 1.0)
        self.assertLess(penalties["release_notes"], 1.0)

    def test_query_book_adjustments_boost_support_and_penalize_prune_for_finalizer_question(self) -> None:
        boosts, penalties = query_book_adjustments(
            "프로젝트가 Terminating 상태에서 안 없어질 때 finalizers 확인부터 정리까지 어떻게 해?"
        )

        self.assertGreater(boosts["support"], 1.0)
        self.assertLess(penalties["cli_tools"], 1.0)

    def test_query_book_adjustments_boost_nodes_family_for_drain_question(self) -> None:
        boosts, penalties = query_book_adjustments(
            "특정 작업자 노드를 drain 해야 해. 예시 명령이 뭐야?"
        )

        self.assertGreater(boosts["nodes"], 1.0)
        self.assertGreater(boosts["support"], 1.0)
        self.assertLess(penalties["updating_clusters"], 1.0)

    def test_query_book_adjustments_boost_support_family_for_cluster_node_usage(self) -> None:
        boosts, penalties = query_book_adjustments(
            "지금 클러스터 전체 노드 CPU랑 메모리 사용량 보려면 어떤 명령 써?"
        )

        self.assertGreater(boosts["support"], 1.0)
        self.assertGreater(boosts["nodes"], 1.0)
        self.assertLess(penalties["cli_tools"], 1.0)

    def test_has_logging_ambiguity_requires_scope(self) -> None:
        self.assertTrue(has_logging_ambiguity("로그는 어디서 봐?"))
        self.assertFalse(has_logging_ambiguity("감사 로그는 어디서 봐?"))
        self.assertFalse(has_logging_ambiguity("애플리케이션 로그는 어디서 봐?"))

    def test_has_update_doc_locator_ambiguity_requires_scope(self) -> None:
        self.assertTrue(has_update_doc_locator_ambiguity("업데이트 관련 문서는 뭐부터 보면 돼?"))
        self.assertFalse(has_update_doc_locator_ambiguity("4.20에서 4.21로 업데이트할 때 문서는 뭐부터 보면 돼?"))

    def test_detect_out_of_corpus_version_flags_newer_minor(self) -> None:
        self.assertEqual("4.21", detect_out_of_corpus_version("OpenShift 4.21에서 새로 추가된 기능만 정리해줘"))
        self.assertIsNone(detect_out_of_corpus_version("OpenShift 4.20 아키텍처 설명해줘"))

    def test_has_follow_up_reference_detects_contextual_korean_starters(self) -> None:
        self.assertTrue(has_follow_up_reference("거기서 안 넘어가고 걸려 있는 리소스 찾는 명령어는?"))
        self.assertTrue(has_follow_up_reference("찾았는데도 안 지워지면 finalizers는 어떻게 봐?"))

    def test_detect_unsupported_product_flags_external_install_query(self) -> None:
        self.assertEqual("harbor", detect_unsupported_product("Harbor 설치 방법 알려줘"))
        self.assertEqual("argo cd", detect_unsupported_product("Argo CD 설치 절차 알려줘"))
        self.assertIsNone(detect_unsupported_product("OpenShift에서 Harbor 연동 방법 알려줘"))

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

    def test_fusion_boosts_backup_book_for_backup_doc_locator_query(self) -> None:
        etcd_hit = RetrievalHit(
            chunk_id="etcd-hit",
            book_slug="etcd",
            chapter="etcd",
            section="etcd 재해 복구",
            anchor="etcd-dr",
            source_url="https://example.com/etcd",
            viewer_path="/docs/etcd.html#dr",
            text="etcd 백업에서 클러스터를 복구하는 절차",
            source="bm25",
            raw_score=0.80,
            fused_score=0.80,
        )
        backup_hit = RetrievalHit(
            chunk_id="backup-hit",
            book_slug="backup_and_restore",
            chapter="backup",
            section="백업 및 복구 문서 개요",
            anchor="backup-overview",
            source_url="https://example.com/backup",
            viewer_path="/docs/backup.html#overview",
            text="백업과 복구 관련 문서와 절차를 모은 가이드",
            source="vector",
            raw_score=0.74,
            fused_score=0.74,
        )

        hits = fuse_ranked_hits(
            "백업 복구 문서는 어디서 봐? 문서 guide documentation backup restore",
            {
                "bm25": [etcd_hit, backup_hit],
                "vector": [backup_hit, etcd_hit],
            },
            top_k=2,
        )

        self.assertEqual("backup_and_restore", hits[0].book_slug)

    def test_retrieve_expands_candidate_pool_for_compare_query(self) -> None:
        class StubBm25:
            def __init__(self) -> None:
                self.calls: list[tuple[str, int]] = []

            def search(self, query: str, top_k: int):
                self.calls.append((query, top_k))
                return []

        settings = Settings(root_dir=ROOT)
        bm25 = StubBm25()
        retriever = Part2Retriever(settings, bm25, vector_retriever=None)

        result = retriever.retrieve(
            "오픈시프트와 쿠버네티스 차이를 세 줄로 설명해줘",
            use_vector=False,
        )

        self.assertEqual(3, len(bm25.calls))
        self.assertTrue(all(top_k == 40 for _, top_k in bm25.calls))
        self.assertEqual(
            [
                "오픈시프트와 쿠버네티스 차이를 세 줄로 설명해줘",
                "오픈시프트 개요",
                "쿠버네티스 개요",
            ],
            result.trace["decomposed_queries"],
        )
        self.assertEqual(40, result.trace["effective_candidate_k"])

    def test_fusion_prefers_authz_books_over_api_books_for_project_rbac_assignment(self) -> None:
        auth_hit = RetrievalHit(
            chunk_id="auth-hit",
            book_slug="authentication_and_authorization",
            chapter="rbac",
            section="9.1.1. 기본 클러스터 역할",
            anchor="default-roles",
            source_url="https://example.com/auth",
            viewer_path="/docs/auth.html#default-roles",
            text="RBAC에서는 로컬 바인딩으로 프로젝트에 admin 역할을 연결할 수 있습니다.",
            source="vector",
            raw_score=0.61,
            fused_score=0.61,
        )
        tutorial_hit = RetrievalHit(
            chunk_id="tutorial-hit",
            book_slug="tutorials",
            chapter="tutorials",
            section="3.3. 보기 권한 부여",
            anchor="grant-view",
            source_url="https://example.com/tutorials",
            viewer_path="/docs/tutorials.html#grant-view",
            text="oc adm policy add-role-to-user view -z default -n user-getting-started",
            source="bm25",
            raw_score=0.60,
            fused_score=0.60,
        )
        api_hit = RetrievalHit(
            chunk_id="api-hit",
            book_slug="role_apis",
            chapter="apis",
            section="RoleBinding API 끝점",
            anchor="rolebinding-api",
            source_url="https://example.com/apis",
            viewer_path="/docs/apis.html#rolebinding-api",
            text="RoleBinding API 끝점과 POST /namespaces/{namespace}/rolebindings 설명",
            source="bm25",
            raw_score=0.66,
            fused_score=0.66,
        )

        hits = fuse_ranked_hits(
            "프로젝트 namespace admin 권한 부여 RBAC 설정 방법 rolebinding add-role-to-user",
            {
                "bm25": [api_hit, tutorial_hit, auth_hit],
                "vector": [auth_hit, tutorial_hit],
            },
            top_k=3,
        )

        self.assertEqual("authentication_and_authorization", hits[0].book_slug)
        self.assertNotEqual("role_apis", hits[0].book_slug)

    def test_fusion_keeps_compare_docs_for_openshift_kubernetes_difference_query(self) -> None:
        security_hit = RetrievalHit(
            chunk_id="security-compare",
            book_slug="security_and_compliance",
            chapter="security",
            section="2.1.2. OpenShift Container Platform의 정의",
            anchor="platform-definition",
            source_url="https://example.com/security",
            viewer_path="/docs/security.html#platform-definition",
            text="쿠버네티스 플랫폼마다 보안이 다를 수 있습니다. OpenShift Container Platform은 쿠버네티스 보안을 잠그고 운영 기능을 제공합니다.",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        compare_hit = RetrievalHit(
            chunk_id="overview-compare",
            book_slug="overview",
            chapter="overview",
            section="7.1. 유사점 및 차이점",
            anchor="similarities-and-differences",
            source_url="https://example.com/overview",
            viewer_path="/docs/overview.html#similarities-and-differences",
            text="유사점 및 차이점 비교 표입니다.",
            source="vector",
            raw_score=0.82,
            fused_score=0.82,
        )

        hits = fuse_ranked_hits(
            "오픈시프트와 쿠버네티스 차이를 세 줄로 설명해줘 OpenShift Kubernetes comparison difference",
            {"bm25": [security_hit], "vector": [compare_hit, security_hit]},
            top_k=2,
        )

        self.assertIn(hits[0].book_slug, {"security_and_compliance", "overview"})

    def test_fusion_prefers_cluster_backup_wrapper_for_etcd_procedure(self) -> None:
        generic_hit = RetrievalHit(
            chunk_id="etcd-generic",
            book_slug="postinstallation_configuration",
            chapter="etcd",
            section="4.12.5. etcd 데이터 백업",
            anchor="backing-up-etcd-data",
            source_url="https://example.com/postinstall",
            viewer_path="/docs/postinstall.html#backing-up-etcd-data",
            text="found latest kube-apiserver ... etcdctl version: 3.4.14 ... snapshot stream downloading",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        procedure_hit = RetrievalHit(
            chunk_id="etcd-procedure",
            book_slug="postinstallation_configuration",
            chapter="etcd",
            section="4.12.5. etcd 데이터 백업",
            anchor="backing-up-etcd-data",
            source_url="https://example.com/postinstall",
            viewer_path="/docs/postinstall.html#backing-up-etcd-data",
            text="cluster-backup.sh 스크립트를 실행합니다. [CODE] /usr/local/bin/cluster-backup.sh /home/core/assets/backup [/CODE]",
            source="vector",
            raw_score=0.98,
            fused_score=0.98,
        )

        hits = fuse_ranked_hits(
            "etcd 백업은 실제로 어떤 절차로 해?",
            {"bm25": [generic_hit], "vector": [procedure_hit]},
            top_k=2,
        )

        self.assertEqual("etcd-procedure", hits[0].chunk_id)

    def test_fusion_prefers_monitor_certificates_command_for_certificate_expiry_query(self) -> None:
        concept_hit = RetrievalHit(
            chunk_id="cert-concept",
            book_slug="security_and_compliance",
            chapter="security",
            section="4.3.2. 만료",
            anchor="expiry",
            source_url="https://example.com/security",
            viewer_path="/docs/security.html#expiry",
            text="서비스 CA 인증서는 26개월 동안 유효하며 순환됩니다.",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        command_hit = RetrievalHit(
            chunk_id="cert-command",
            book_slug="cli_tools",
            chapter="cli",
            section="2.7.1.25. oc adm ocp-certificates monitor-certificates",
            anchor="oc-adm-ocp-certificates-monitor-certificates",
            source_url="https://example.com/cli",
            viewer_path="/docs/cli.html#oc-adm-ocp-certificates-monitor-certificates",
            text="플랫폼 인증서 감시 [CODE] oc adm ocp-certificates monitor-certificates [/CODE]",
            source="vector",
            raw_score=0.97,
            fused_score=0.97,
        )

        hits = fuse_ranked_hits(
            "ocp api 서버 인증서 만료 임박했는지 어떻게 확인해?",
            {"bm25": [concept_hit], "vector": [command_hit]},
            top_k=2,
        )

        self.assertEqual("cert-command", hits[0].chunk_id)

    def test_retriever_short_circuits_unsupported_external_query(self) -> None:
        settings = Settings(ROOT)
        retriever = Part2Retriever(settings, BM25Index.from_rows([]), vector_retriever=None)

        result = retriever.retrieve("Harbor 설치 방법 알려줘", use_bm25=False, use_vector=False)

        self.assertEqual([], result.hits)
        self.assertTrue(
            any("outside OCP corpus" in warning for warning in result.trace["warnings"])
        )


    def test_normalize_query_treats_ocp_intro_request_as_intro_query(self) -> None:
        normalized = normalize_query("OCP 소개해줘")

        self.assertIn("OpenShift", normalized)
        self.assertIn("Container", normalized)
        self.assertIn("Platform", normalized)
        self.assertIn("overview", normalized)

    def test_normalize_query_expands_architecture_summary_request(self) -> None:
        normalized = normalize_query("아키텍처를 한 장으로 요약해줘")

        self.assertIn("OpenShift", normalized)
        self.assertIn("Container", normalized)
        self.assertIn("Platform", normalized)
        self.assertIn("architecture", normalized)
        self.assertIn("overview", normalized)

    def test_normalize_query_expands_kubernetes_compare_follow_up_toward_openshift(self) -> None:
        normalized = normalize_query("쿠버네티스와 차이도 설명해줘")

        self.assertIn("Kubernetes", normalized)
        self.assertIn("OpenShift", normalized)
        self.assertIn("comparison", normalized)
        self.assertIn("difference", normalized)

    def test_normalize_query_adds_procedure_terms_for_step_by_step_request(self) -> None:
        normalized = normalize_query("특정 namespace만 admin 권한 주는 방법 단계별로 알려줘")

        self.assertIn("절차", normalized)
        self.assertIn("단계", normalized)
        self.assertIn("procedure", normalized)

    def test_rewrite_query_uses_recent_turn_capsule_for_follow_up(self) -> None:
        rewritten = rewrite_query(
            "그거 YAML로도 돼?",
            SessionContext(
                mode="ops",
                current_topic="RBAC",
                recent_turns=[
                    TurnMemory(
                        query="특정 namespace만 admin 권한 주는 방법 단계별로 알려줘",
                        topic="RBAC",
                        answer_focus="namespace 단위 admin 권한은 RoleBinding으로 부여한다",
                        references=["authentication_and_authorization · 9.6. 사용자 역할 추가"],
                    )
                ],
            ),
        )

        self.assertIn("최근 대화 캡슐", rewritten)
        self.assertIn("topic=RBAC", rewritten)
        self.assertIn("focus=namespace 단위 admin 권한은 RoleBinding으로 부여한다", rewritten)
        self.assertIn("refs=authentication_and_authorization", rewritten)

    def test_session_context_from_dict_restores_recent_turns(self) -> None:
        context = SessionContext.from_dict(
            {
                "mode": "ops",
                "recent_turns": [
                    {
                        "query": "이전 질문",
                        "topic": "RBAC",
                        "answer_focus": "rolebinding",
                        "entities": ["RBAC"],
                        "references": ["1번=authentication_and_authorization · 9.6"],
                    }
                ],
            }
        )

        self.assertEqual(1, len(context.recent_turns))
        self.assertEqual("이전 질문", context.recent_turns[0].query)
        self.assertEqual("RBAC", context.recent_turns[0].topic)

    def test_session_context_from_dict_restores_procedure_memory(self) -> None:
        context = SessionContext.from_dict(
            {
                "current_topic": "RBAC",
                "procedure_memory": {
                    "goal": "namespace admin 권한 부여",
                    "steps": ["역할 바인딩 추가", "적용 결과 확인"],
                    "active_step_index": 1,
                    "step_commands": [
                        "oc adm policy add-role-to-user admin alice -n joe",
                        "oc describe rolebinding -n joe",
                    ],
                    "references": ["authentication_and_authorization · 9.6. 사용자 역할 추가"],
                },
            }
        )

        self.assertIsNotNone(context.procedure_memory)
        self.assertEqual("namespace admin 권한 부여", context.procedure_memory.goal)
        self.assertEqual(1, context.procedure_memory.active_step_index)
        self.assertEqual("oc describe rolebinding -n joe", context.procedure_memory.command_for(1))

if __name__ == "__main__":
    unittest.main()
