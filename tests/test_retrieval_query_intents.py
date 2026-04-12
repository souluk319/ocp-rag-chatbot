from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_retrieval import (
    detect_out_of_corpus_version,
    detect_unsupported_product,
    build_retrieval_plan,
    fuse_ranked_hits,
    has_cluster_node_usage_intent,
    has_follow_up_entity_ambiguity,
    has_follow_up_reference,
    has_logging_ambiguity,
    has_machine_config_reboot_intent,
    has_node_drain_intent,
    has_multiple_entity_ambiguity,
    has_project_scoped_rbac_intent,
    has_rbac_assignment_intent,
    has_rbac_intent,
    has_route_ingress_compare_intent,
    has_security_doc_locator_ambiguity,
    has_update_doc_locator_ambiguity,
    normalize_query,
    query_book_adjustments,
    rewrite_query,
    RetrievalHit,
    SessionContext,
)

class TestRetrievalQueryIntents(unittest.TestCase):
    def test_normalize_query_expands_high_value_aliases(self) -> None:
        normalized = normalize_query("로그는 어디서 봐?")

        self.assertIn("로깅", normalized)
        self.assertNotIn("logging", normalized)

    def test_normalize_query_expands_security_and_architecture_aliases(self) -> None:
        normalized = normalize_query("보안 아키텍처 기본 문서")

        self.assertIn("보안", normalized)
        self.assertIn("아키텍처", normalized)
        self.assertIn("개요", normalized)
        self.assertNotIn("security", normalized)
        self.assertNotIn("architecture", normalized)
        self.assertNotIn("overview", normalized)

    def test_normalize_query_expands_architecture_explainer_prompt(self) -> None:
        normalized = normalize_query("오픈시프트 아키텍처를 설명해줘")

        self.assertIn("구조", normalized)
        self.assertIn("개요", normalized)
        self.assertIn("소개", normalized)
        self.assertIn("기본", normalized)
        self.assertIn("개념", normalized)
        self.assertNotIn("OpenShift", normalized)
        self.assertNotIn("architecture", normalized)
        self.assertNotIn("overview", normalized)

    def test_normalize_query_treats_openshift_summary_as_intro_query(self) -> None:
        normalized = normalize_query("오픈시프트에 대해 세줄요약해봐")

        self.assertIn("소개", normalized)
        self.assertIn("개요", normalized)
        self.assertIn("기본", normalized)
        self.assertIn("개념", normalized)
        self.assertNotIn("OpenShift", normalized)
        self.assertNotIn("overview", normalized)

    def test_normalize_query_treats_ocp_attached_korean_explainer_as_intro_query(self) -> None:
        normalized = normalize_query("OCP가뭐야")

        self.assertIn("OpenShift", normalized)
        self.assertIn("Container", normalized)
        self.assertIn("Platform", normalized)
        self.assertIn("소개", normalized)
        self.assertIn("개요", normalized)
        self.assertNotIn("overview", normalized)

    def test_normalize_query_treats_spaced_openshift_intro_as_intro_query(self) -> None:
        normalized = normalize_query("오픈 시프트가 뭐야?")

        self.assertIn("소개", normalized)
        self.assertIn("개요", normalized)
        self.assertIn("기본", normalized)
        self.assertIn("개념", normalized)

    def test_normalize_query_treats_openshift_usage_question_as_intro_query(self) -> None:
        normalized = normalize_query("오픈시프트는 어떤 곳에 쓰여?")

        self.assertIn("소개", normalized)
        self.assertIn("기본", normalized)
        self.assertIn("개념", normalized)

    def test_normalize_query_expands_openshift_kubernetes_compare_intent(self) -> None:
        normalized = normalize_query("오픈시프트와 쿠버네티스 차이를 세 줄로 설명해줘")

        self.assertIn("개요", normalized)
        self.assertIn("차이점", normalized)
        self.assertIn("유사점", normalized)
        self.assertNotIn("OpenShift", normalized)
        self.assertNotIn("Kubernetes", normalized)
        self.assertNotIn("comparison", normalized)
        self.assertNotIn("difference", normalized)

    def test_normalize_query_expands_etcd_backup_intent(self) -> None:
        normalized = normalize_query("etcd 백업은 어떻게 해?")

        self.assertIn("cluster-backup.sh", normalized)
        self.assertIn("backup", normalized)
        self.assertNotIn("cluster-restore.sh", normalized)

    def test_normalize_query_expands_etcd_restore_intent(self) -> None:
        normalized = normalize_query("etcd 복구는 어떻게 해?")

        self.assertIn("cluster-restore.sh", normalized)
        self.assertIn("restore", normalized)
        self.assertNotIn("cluster-backup.sh", normalized)

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

    def test_normalize_query_detects_concrete_rbac_assignment_follow_up(self) -> None:
        query = "예를들어 cywell 프로젝트의 kugnus 사용자에게 어드민 역할을 주려면 어떻게해?"

        normalized = normalize_query(query)
        rewritten = rewrite_query(
            normalized,
            SessionContext(
                current_topic="RBAC 권한 부여",
                unresolved_question="namespace admin 역할 추가",
                ocp_version="4.20",
            ),
        )

        self.assertTrue(has_rbac_intent(query))
        self.assertTrue(has_project_scoped_rbac_intent(query))
        self.assertTrue(has_rbac_assignment_intent(query))
        self.assertTrue(has_follow_up_reference(query))
        self.assertIn("rolebinding", normalized)
        self.assertIn("add-role-to-user", normalized)
        self.assertIn("admin", normalized)
        self.assertIn("주제 RBAC 권한 부여", rewritten)
        self.assertIn("OCP 4.20", rewritten)

    def test_build_retrieval_plan_exposes_follow_up_and_rewrite_diagnostics(self) -> None:
        plan = build_retrieval_plan(
            "그 복구는 어떻게 해?",
            context=SessionContext(
                current_topic="etcd 백업",
                unresolved_question="etcd 백업 이후 복구 절차",
                ocp_version="4.20",
            ),
            candidate_k=20,
        )

        self.assertTrue(plan.follow_up_detected)
        self.assertTrue(plan.rewrite_applied)
        self.assertTrue(plan.rewrite_reason)
        self.assertIn("follow", plan.rewrite_reason)
        self.assertNotEqual(plan.normalized_query, plan.rewritten_query)

    def test_rewrite_query_strips_numeric_section_prefix_from_context_topic(self) -> None:
        rewritten = rewrite_query(
            "다시 보여줘",
            SessionContext(
                current_topic="7.2.1. 노드 상태, 리소스 사용량 및 구성 확인",
                unresolved_question="클러스터 기본 상태 확인",
                ocp_version="4.20",
            ),
        )

        self.assertIn("주제 노드 상태, 리소스 사용량 및 구성 확인", rewritten)
        self.assertNotIn("주제 7.2.1.", rewritten)

    def test_build_retrieval_plan_marks_standalone_query_as_not_rewritten(self) -> None:
        plan = build_retrieval_plan(
            "오픈시프트 아키텍처를 설명해줘",
            context=SessionContext(),
            candidate_k=20,
        )

        self.assertFalse(plan.follow_up_detected)
        self.assertFalse(plan.rewrite_applied)
        self.assertIn(plan.rewrite_reason, {"no_context", "no_rewrite_needed"})
        self.assertEqual(plan.normalized_query, plan.rewritten_query)

    def test_normalize_query_expands_rbac_verify_follow_up_terms(self) -> None:
        normalized = normalize_query("그 권한이 잘 들어갔는지 확인하는 명령도 알려줘")

        self.assertIn("oc describe rolebinding.rbac -n <project>", normalized)
        self.assertIn("SelfSubjectAccessReview", normalized)
        self.assertIn("LocalSubjectAccessReview", normalized)

    def test_normalize_query_expands_rbac_revoke_follow_up_terms(self) -> None:
        normalized = normalize_query("그 권한을 회수하려면 어떻게 해?")

        self.assertIn("remove-role-from-user", normalized)
        self.assertIn("oc adm policy", normalized)

    def test_normalize_query_expands_cluster_admin_difference_follow_up_terms(self) -> None:
        normalized = normalize_query("그럼 cluster-admin이랑 차이도 짧게 말해줘")

        self.assertIn("cluster-admin", normalized)
        self.assertIn("clusterrolebinding.rbac.authorization.k8s.io", normalized)
        self.assertIn("로컬 바인딩과 클러스터 바인딩의 차이점", normalized)

    def test_normalize_query_expands_project_finalizer_cleanup_terms(self) -> None:
        normalized = normalize_query(
            "프로젝트를 oc delete로 지웠는데 계속 Terminating 상태야. finalizers 강제 제거 전에 걸린 리소스부터 찾고 싶어."
        )

        self.assertIn("Terminating", normalized)
        self.assertIn("finalizers", normalized)
        self.assertIn("metadata.finalizers", normalized)

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
        self.assertIn("key-value", normalized)
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
        self.assertLess(penalties["etcd"], 1.0)
        self.assertLess(penalties["hosted_control_planes"], 1.0)

    def test_query_book_adjustments_prefers_postinstall_over_etcd_for_backup_procedure(self) -> None:
        boosts, penalties = query_book_adjustments("etcd 백업은 실제로 어떤 절차로 해?")

        self.assertGreater(boosts["postinstallation_configuration"], boosts["etcd"])
        self.assertGreater(boosts["backup_and_restore"], 1.0)
        self.assertNotIn("etcd", penalties)
        self.assertNotIn("backup_and_restore", penalties)

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
        self.assertGreater(boosts["machine_management"], 1.0)
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

    def test_has_security_doc_locator_ambiguity_requires_scope(self) -> None:
        self.assertTrue(has_security_doc_locator_ambiguity("보안 관련 기본 문서는 뭐가 중심이야?"))
        self.assertFalse(has_security_doc_locator_ambiguity("인증 관련 기본 문서는 뭐가 중심이야?"))
        self.assertFalse(has_security_doc_locator_ambiguity("네트워크 보안 문서는 어디서 봐?"))

    def test_has_multiple_entity_ambiguity_does_not_split_mco_single_concept(self) -> None:
        self.assertFalse(has_multiple_entity_ambiguity("Machine Config Operator가 뭐야?"))

    def test_detect_out_of_corpus_version_flags_newer_minor(self) -> None:
        self.assertEqual("4.21", detect_out_of_corpus_version("OpenShift 4.21에서 새로 추가된 기능만 정리해줘"))
        self.assertIsNone(detect_out_of_corpus_version("OpenShift 4.20 아키텍처 설명해줘"))

    def test_has_follow_up_reference_detects_contextual_korean_starters(self) -> None:
        self.assertTrue(has_follow_up_reference("거기서 안 넘어가고 걸려 있는 리소스 찾는 명령어는?"))
        self.assertTrue(has_follow_up_reference("찾았는데도 안 지워지면 finalizers는 어떻게 봐?"))
        self.assertTrue(has_follow_up_reference("그 Operator는 뭘 관리해?"))
        self.assertTrue(has_follow_up_reference("그 복원 순서는?"))
        self.assertTrue(has_follow_up_reference("그 RoleBinding YAML 예시도 보여줘"))
        self.assertTrue(has_follow_up_reference("그 권한이 잘 들어갔는지 확인하는 명령도 알려줘"))
        self.assertTrue(has_follow_up_reference("그 권한을 회수하려면 어떻게 해?"))
        self.assertTrue(has_follow_up_reference("쿠버네티스와 차이도 설명해줘"))
        self.assertTrue(has_follow_up_reference("Route와 Ingress 관련 주의사항도 함께 정리해줘"))
        self.assertTrue(has_follow_up_reference("Route와 Ingress 상태 확인 방법도 같이 알려줘"))
        self.assertTrue(has_follow_up_reference("Route와 Ingress 관련 실행 예시도 같이 보여줘"))

    def test_has_route_ingress_compare_intent_detects_networking_compare_query(self) -> None:
        self.assertTrue(
            has_route_ingress_compare_intent("OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘")
        )
        self.assertFalse(has_route_ingress_compare_intent("OpenShift 아키텍처를 설명해줘"))

    def test_has_machine_config_reboot_intent_detects_reboot_reason_question(self) -> None:
        self.assertTrue(has_machine_config_reboot_intent("머신 설정 변경이 적용될 때 노드 재부팅은 왜 일어나?"))
        self.assertTrue(has_machine_config_reboot_intent("MCO 때문에 재부팅이 왜 생겨?"))
        self.assertFalse(has_machine_config_reboot_intent("Machine Config Operator는 뭘 해?"))

    def test_query_book_adjustments_boosts_mco_concept_family(self) -> None:
        boosts, penalties = query_book_adjustments("Machine Config Operator는 뭘 해?")

        self.assertGreater(boosts["machine_configuration"], 1.0)
        self.assertGreater(boosts["machine_management"], 1.0)
        self.assertGreater(boosts["architecture"], 1.0)
        self.assertGreater(boosts["overview"], 1.0)
        self.assertLess(penalties["images"], 1.0)
        self.assertLess(penalties["support"], 1.0)

    def test_query_book_adjustments_boosts_machine_config_reboot_family(self) -> None:
        boosts, penalties = query_book_adjustments("머신 설정 변경이 적용될 때 노드 재부팅은 왜 일어나?")

        self.assertGreater(boosts["machine_management"], 1.0)
        self.assertGreater(boosts["updating_clusters"], 1.0)
        self.assertLess(penalties["specialized_hardware_and_driver_enablement"], 1.0)
        self.assertLess(penalties["network_security"], 1.0)

    def test_query_book_adjustments_penalizes_support_for_mco_reboot_follow_up_context(self) -> None:
        boosts, penalties = query_book_adjustments(
            "그거 재부팅은 왜 일어나?",
            context=SessionContext(
                current_topic="Machine Config Operator",
                open_entities=["Machine Config Operator", "MCO"],
                unresolved_question="자동 재부팅 이유와 spec.paused",
            ),
        )

        self.assertGreater(boosts["machine_management"], 1.0)
        self.assertGreater(boosts["postinstallation_configuration"], 1.0)
        self.assertGreater(boosts["nodes"], 1.0)
        self.assertLess(penalties["support"], 1.0)
        self.assertLess(penalties["cli_tools"], 1.0)

    def test_query_book_adjustments_penalizes_hosted_control_planes_for_mco_operator_follow_up(self) -> None:
        boosts, penalties = query_book_adjustments(
            "그 Operator는 뭘 관리해?",
            context=SessionContext(
                current_topic="Machine Config Operator",
                open_entities=["Machine Config Operator"],
            ),
        )

        self.assertGreater(boosts["machine_management"], 1.0)
        self.assertLess(penalties["hosted_control_planes"], 1.0)

    def test_fusion_prefers_approved_mco_concept_books_over_hosted_control_planes(self) -> None:
        hosted_hit = RetrievalHit(
            chunk_id="hcp-hit",
            book_slug="hosted_control_planes",
            chapter="hcp",
            section="Hosted control plane operator 개요",
            anchor="hcp-operators",
            source_url="https://example.com/hcp",
            viewer_path="/docs/hcp.html#hcp-operators",
            text="Hosted control plane operator가 컨트롤 플레인을 관리합니다.",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        machine_hit = RetrievalHit(
            chunk_id="machine-hit",
            book_slug="machine_management",
            chapter="machine",
            section="Machine API와 Machine Config Operator",
            anchor="machine-operator",
            source_url="https://example.com/machine",
            viewer_path="/docs/machine.html#machine-operator",
            text="Machine Config Operator는 머신 구성과 노드 설정을 관리합니다.",
            source="vector",
            raw_score=0.98,
            fused_score=0.98,
        )
        architecture_hit = RetrievalHit(
            chunk_id="arch-hit",
            book_slug="architecture",
            chapter="architecture",
            section="주요 기능",
            anchor="key-features",
            source_url="https://example.com/arch",
            viewer_path="/docs/arch.html#key-features",
            text="Cluster Version Operator 및 Machine Config Operator는 플랫폼 핵심 구성 요소입니다.",
            source="vector",
            raw_score=0.97,
            fused_score=0.97,
        )

        hits = fuse_ranked_hits(
            "그 Operator는 뭘 관리해?",
            {"bm25": [hosted_hit], "vector": [machine_hit, architecture_hit]},
            context=SessionContext(
                current_topic="Machine Config Operator",
                open_entities=["Machine Config Operator"],
            ),
            top_k=3,
        )

        self.assertIn(hits[0].book_slug, {"machine_management", "architecture"})
        self.assertNotEqual("hosted_control_planes", hits[0].book_slug)

    def test_fusion_prefers_update_family_over_support_for_mco_reboot_reason_follow_up(self) -> None:
        support_hit = RetrievalHit(
            chunk_id="support-mco",
            book_slug="support",
            chapter="support",
            section="MCO 자동 재부팅 비활성화",
            anchor="disable-autoreboot",
            source_url="https://example.com/support",
            viewer_path="/docs/support.html#disable-autoreboot",
            text="MCO 변경으로 인한 원치 않는 중단을 방지하려면 MCP를 수정하여 자동 재부팅을 막을 수 있습니다.",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        update_hit = RetrievalHit(
            chunk_id="update-mco",
            book_slug="updating_clusters",
            chapter="updates",
            section="Machine Config Operator의 노드 업데이트",
            anchor="mco-node-updates",
            source_url="https://example.com/update",
            viewer_path="/docs/update.html#mco-node-updates",
            text="MCO는 각 노드에서 드레이닝, 운영 체제 업데이트, 노드 재부팅을 순차적으로 수행합니다.",
            source="vector",
            raw_score=0.99,
            fused_score=0.99,
        )
        postinstall_hit = RetrievalHit(
            chunk_id="postinstall-mco",
            book_slug="postinstallation_configuration",
            chapter="postinstall",
            section="설치 후 작업",
            anchor="post-install-tasks",
            source_url="https://example.com/postinstall",
            viewer_path="/docs/postinstall.html#post-install-tasks",
            text="MCO는 MachineConfig 오브젝트를 관리하고 노드 구성을 적용합니다.",
            source="vector",
            raw_score=0.98,
            fused_score=0.98,
        )

        hits = fuse_ranked_hits(
            "그거 재부팅은 왜 일어나?",
            {"bm25": [support_hit], "vector": [update_hit, postinstall_hit]},
            context=SessionContext(
                current_topic="Machine Config Operator",
                open_entities=["Machine Config Operator", "MCO"],
                unresolved_question="노드 재부팅 이유",
            ),
            top_k=3,
        )

        self.assertIn(hits[0].book_slug, {"updating_clusters", "postinstallation_configuration"})
        self.assertNotEqual("support", hits[0].book_slug)

    def test_has_follow_up_entity_ambiguity_requires_multiple_open_entities(self) -> None:
        context = SessionContext(
            current_topic="운영 설정 변경",
            open_entities=[
                "Machine Config Operator 자동 재부팅 비활성화",
                "이미지 레지스트리 allowedRegistries 변경",
            ]
        )
        self.assertTrue(has_follow_up_entity_ambiguity("그 설정 바꾸는 명령만 줘", context))
        self.assertTrue(has_follow_up_entity_ambiguity("3번 방법으로 하면 돼?", context))
        self.assertFalse(has_follow_up_entity_ambiguity("Machine Config Operator 설정 바꾸는 명령만 줘", context))
        specific_context = SessionContext(
            current_topic="외부 이미지 레지스트리 구성",
            open_entities=["registry", "image registry"],
        )
        self.assertFalse(has_follow_up_entity_ambiguity("아까 말한 이미지 저장소는?", specific_context))

    def test_detect_unsupported_product_flags_external_install_query(self) -> None:
        self.assertEqual("harbor", detect_unsupported_product("Harbor 설치 방법 알려줘"))
        self.assertEqual("argo cd", detect_unsupported_product("Argo CD 설치 절차 알려줘"))
        self.assertIsNone(detect_unsupported_product("OpenShift에서 Harbor 연동 방법 알려줘"))
