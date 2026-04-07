from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.settings import Settings
from ocp_rag_part2.bm25 import BM25Index
from ocp_rag_part2.models import RetrievalHit, SessionContext
from ocp_rag_part2.query import (
    decompose_retrieval_queries,
    detect_out_of_corpus_version,
    detect_unsupported_product,
    has_corrective_follow_up,
    has_cluster_node_usage_intent,
    has_command_request,
    has_deployment_scaling_intent,
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
from ocp_rag_part2.retriever import (
    Part2Retriever,
    _filter_doc_to_book_hits_by_selection,
    fuse_ranked_hits,
)


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

    def test_decompose_retrieval_queries_adds_pod_lifecycle_concept_subqueries(self) -> None:
        queries = decompose_retrieval_queries("Pod lifecycle 개념을 초보자 기준으로 설명해줘")

        self.assertEqual(
            [
                "Pod lifecycle 개념을 초보자 기준으로 설명해줘",
                "Pod 정의와 Pod phase 개념",
                "Pod status와 phase 차이",
                "파드 생명주기 개념",
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

    def test_fuse_ranked_hits_prefers_doc_to_book_overlay_over_vector_for_exact_match(self) -> None:
        intake_hit = RetrievalHit(
            chunk_id="dtb-demo:events",
            book_slug="demo-guide",
            chapter="문제 해결",
            section="Safety Switch 확인",
            anchor="safety-switch",
            source_url="https://example.com/demo",
            viewer_path="/docs/intake/dtb-demo/index.html#safety-switch",
            text="maintenance token 77A 와 nebula-drain 플래그를 먼저 확인합니다.",
            source="doc_to_book_bm25",
            raw_score=1.0,
        )
        vector_hit = RetrievalHit(
            chunk_id="vector-1",
            book_slug="nodes",
            chapter="nodes",
            section="안전한 sysctl 및 안전하지 않은 sysctl",
            anchor="sysctl",
            source_url="https://example.com/nodes",
            viewer_path="/docs/ocp/4.20/ko/nodes/index.html#sysctl",
            text="sysctl 설정을 설명합니다.",
            source="vector",
            raw_score=1.0,
        )

        fused = fuse_ranked_hits(
            "maintenance token 77A랑 nebula-drain 플래그는 어디서 확인해?",
            {"doc_to_book_bm25": [intake_hit], "vector": [vector_hit]},
            top_k=2,
        )

        self.assertEqual("demo-guide", fused[0].book_slug)
        self.assertEqual("/docs/intake/dtb-demo/index.html#safety-switch", fused[0].viewer_path)

    def test_filter_doc_to_book_hits_by_selection_keeps_only_checked_drafts(self) -> None:
        selected_hit = RetrievalHit(
            chunk_id="draft-a:overview",
            book_slug="draft-a",
            chapter="개요",
            section="선택 문서",
            anchor="overview",
            source_url="/tmp/a.pdf",
            viewer_path="/docs/intake/draft-a/index.html#overview",
            text="선택된 업로드 문서",
            source="doc_to_book_bm25",
            raw_score=1.0,
        )
        unselected_hit = RetrievalHit(
            chunk_id="draft-b:overview",
            book_slug="draft-b",
            chapter="개요",
            section="제외 문서",
            anchor="overview",
            source_url="/tmp/b.pdf",
            viewer_path="/docs/intake/draft-b/index.html#overview",
            text="선택되지 않은 업로드 문서",
            source="doc_to_book_bm25",
            raw_score=0.9,
        )

        filtered = _filter_doc_to_book_hits_by_selection(
            [selected_hit, unselected_hit],
            context=SessionContext(
                selected_draft_ids=["draft-a"],
                restrict_uploaded_sources=True,
            ),
        )

        self.assertEqual(["draft-a:overview"], [hit.chunk_id for hit in filtered])

    def test_filter_doc_to_book_hits_by_selection_returns_no_overlay_hits_when_none_checked(self) -> None:
        hit = RetrievalHit(
            chunk_id="draft-a:overview",
            book_slug="draft-a",
            chapter="개요",
            section="선택 문서",
            anchor="overview",
            source_url="/tmp/a.pdf",
            viewer_path="/docs/intake/draft-a/index.html#overview",
            text="선택된 업로드 문서",
            source="doc_to_book_bm25",
            raw_score=1.0,
        )

        filtered = _filter_doc_to_book_hits_by_selection(
            [hit],
            context=SessionContext(
                selected_draft_ids=[],
                restrict_uploaded_sources=True,
            ),
        )

        self.assertEqual([], filtered)

    def test_retriever_includes_doc_to_book_overlay_sections_in_bm25(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root)
            (settings.doc_to_book_books_dir / "dtb-demo.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "canonical_book_v1",
                        "book_slug": "demo-guide",
                        "title": "데모 가이드",
                        "source_type": "web",
                        "source_uri": "https://example.com/demo",
                        "language_hint": "ko",
                        "source_view_strategy": "normalized_sections_v1",
                        "retrieval_derivation": "chunks_from_canonical_sections",
                        "sections": [
                            {
                                "ordinal": 1,
                                "section_key": "demo-guide:events",
                                "heading": "이벤트 확인",
                                "section_level": 2,
                                "section_path": ["문제 해결", "이벤트 확인"],
                                "section_path_label": "문제 해결 > 이벤트 확인",
                                "anchor": "events",
                                "viewer_path": "/docs/intake/dtb-demo/index.html#events",
                                "source_url": "https://example.com/demo",
                                "text": "Pod Pending 문제를 볼 때는 FailedScheduling 이벤트와 describe 결과를 먼저 확인합니다.",
                                "block_kinds": ["paragraph"],
                            }
                        ],
                        "notes": [],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            retriever = Part2Retriever(settings, BM25Index.from_rows([]), vector_retriever=None)

            result = retriever.retrieve(
                "Pod Pending 이벤트 먼저 확인해야 해?",
                context=SessionContext(restrict_uploaded_sources=False),
                use_vector=False,
                top_k=3,
                candidate_k=5,
            )

        self.assertTrue(result.hits)
        self.assertEqual("demo-guide", result.hits[0].book_slug)
        self.assertEqual("/docs/intake/dtb-demo/index.html#events", result.hits[0].viewer_path)
        self.assertTrue(result.trace["doc_to_book_bm25"])
        self.assertGreater(result.trace["metrics"]["doc_to_book_bm25"]["count"], 0)

    def test_has_deployment_scaling_intent_detects_replica_change_question(self) -> None:
        self.assertTrue(
            has_deployment_scaling_intent(
                "실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?"
            )
        )
        self.assertFalse(
            has_deployment_scaling_intent(
                "DeploymentConfig를 수동으로 스케일링하려면?"
            )
        )

    def test_fuse_ranked_hits_prefers_cli_scale_doc_for_deployment_scaling_intent(self) -> None:
        cli_hit = RetrievalHit(
            chunk_id="cli-scale",
            book_slug="cli_tools",
            chapter="2장. OpenShift CLI(oc)",
            section="2.6.1.124. oc scale",
            anchor="oc-scale",
            source_url="https://example.com/cli",
            viewer_path="/docs/ocp/4.20/ko/cli_tools/index.html#oc-scale",
            text="oc scale --current-replicas=2 --replicas=3 deployment/mysql",
            source="bm25",
            raw_score=1.0,
        )
        rbac_hit = RetrievalHit(
            chunk_id="rbac-scale",
            book_slug="authentication_and_authorization",
            chapter="9장. RBAC",
            section="9.4. 클러스터 역할 및 바인딩 보기",
            anchor="roles",
            source_url="https://example.com/rbac",
            viewer_path="/docs/ocp/4.20/ko/authentication_and_authorization/index.html#roles",
            text="deployments.apps/scale deploymentconfigs/scale 권한 예시",
            source="vector",
            raw_score=1.0,
        )

        fused = fuse_ranked_hits(
            "OCP 4.20 | 사용자 목표 실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해? | 5개에서 10개로 변경도돼?",
            {"bm25": [cli_hit], "vector": [rbac_hit]},
            context=SessionContext(
                user_goal="실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
                current_topic="Deployment 스케일링",
                ocp_version="4.20",
            ),
            top_k=2,
        )

        self.assertEqual("cli_tools", fused[0].book_slug)
        self.assertEqual("2.6.1.124. oc scale", fused[0].section)

    def test_fuse_ranked_hits_prefers_intake_structured_key_over_generic_intro_doc(self) -> None:
        intake_hit = RetrievalHit(
            chunk_id="dtb-demo:unique-switch",
            book_slug="orion-pdf-guide",
            chapter="Page 1",
            section="Unique Switch",
            anchor="unique-switch",
            source_url="/tmp/orion.pdf",
            viewer_path="/docs/intake/dtb-demo/index.html#unique-switch",
            text="orion.unique/flag=starfall-88 값을 migration 전에 설정합니다.",
            source="doc_to_book_bm25",
            raw_score=1.0,
        )
        generic_intro_hit = RetrievalHit(
            chunk_id="nodes:overview",
            book_slug="architecture",
            chapter="개요",
            section="아키텍처 개요",
            anchor="overview",
            source_url="https://example.com/architecture",
            viewer_path="/docs/ocp/4.20/ko/architecture/index.html#overview",
            text="OpenShift 아키텍처 소개 문서입니다.",
            source="bm25",
            raw_score=1.0,
        )

        fused = fuse_ranked_hits(
            "orion.unique/flag 값이 뭐야?",
            {"doc_to_book_bm25": [intake_hit], "bm25": [generic_intro_hit]},
            top_k=2,
        )

        self.assertEqual("orion-pdf-guide", fused[0].book_slug)
        self.assertEqual("/docs/intake/dtb-demo/index.html#unique-switch", fused[0].viewer_path)

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

    def test_rewrite_query_uses_user_goal_for_shorthand_numeric_follow_up(self) -> None:
        context = SessionContext(
            user_goal="실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
            current_topic="Deployment replicas",
            ocp_version="4.20",
        )

        rewritten = rewrite_query("그럼 5개에서 10개로 변경하려면?", context)

        self.assertIn("Deployment의 복제본", rewritten)
        self.assertIn("3개에서 5개", rewritten)
        self.assertIn("그럼 5개에서 10개로 변경하려면?", rewritten)

    def test_corrective_follow_up_requests_are_detected_and_rewritten(self) -> None:
        context = SessionContext(
            user_goal="실행 중인 Deployment의 복제본(Replicas) 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
            current_topic="Deployment 스케일링",
            ocp_version="4.20",
        )

        self.assertTrue(has_corrective_follow_up("아니 5개에서 10개로 변경하는 명령어"))
        self.assertTrue(has_follow_up_reference("그럼 명령어라도 알려줘"))
        self.assertTrue(has_command_request("그럼 명령어라도 알려줘"))

        rewritten = rewrite_query("아니 5개에서 10개로 변경하는 명령어", context)

        self.assertIn("사용자 목표", rewritten)
        self.assertIn("Deployment의 복제본", rewritten)
        self.assertIn("5개에서 10개", rewritten)

    def test_rewrite_query_does_not_force_prior_topic_for_explicit_new_topic(self) -> None:
        context = SessionContext(
            current_topic="2.1.3. 클러스터 업데이트 전 etcd 백업",
            ocp_version="4.20",
        )

        rewritten = rewrite_query("오픈시프트에 대해 새줄약해봐", context)

        self.assertEqual("오픈시프트에 대해 새줄약해봐", rewritten)

    def test_normalize_query_expands_pod_pending_troubleshooting_terms(self) -> None:
        normalized = normalize_query("Pod가 Pending 상태에서 오래 멈춰 있을 때 어떤 순서로 점검해야 해?")

        self.assertIn("Pending", normalized)
        self.assertIn("FailedScheduling", normalized)
        self.assertIn("describe", normalized)
        self.assertIn("events", normalized)
        self.assertIn("troubleshooting", normalized)

    def test_query_book_adjustments_penalize_api_books_for_pod_troubleshooting(self) -> None:
        boosts, penalties = query_book_adjustments(
            "CrashLoopBackOff가 반복될 때 원인 추적 순서를 알려줘"
        )

        self.assertGreater(boosts["support"], 1.0)
        self.assertGreater(boosts["validation_and_troubleshooting"], 1.0)
        self.assertGreater(boosts["nodes"], 1.0)
        self.assertGreater(boosts["building_applications"], 1.0)
        self.assertLess(penalties["workloads_apis"], 1.0)
        self.assertLess(penalties["security_and_compliance"], 1.0)
        self.assertLess(penalties["monitoring_apis"], 1.0)
        self.assertLess(penalties["network_apis"], 1.0)

    def test_normalize_query_expands_pod_lifecycle_concept_terms(self) -> None:
        normalized = normalize_query("Pod lifecycle 개념을 초보자 관점에서 설명해줘")

        self.assertIn("lifecycle", normalized)
        self.assertIn("Pending", normalized)
        self.assertIn("Running", normalized)
        self.assertIn("glossary", normalized)
        self.assertIn("status", normalized)

    def test_query_book_adjustments_bias_lifecycle_explainer_toward_architecture(self) -> None:
        boosts, penalties = query_book_adjustments(
            "Pod lifecycle 개념을 초보자 기준으로 설명해줘"
        )

        self.assertGreater(boosts["architecture"], 1.0)
        self.assertGreater(boosts["nodes"], 1.0)
        self.assertGreater(boosts["overview"], 1.0)
        self.assertLess(penalties["workloads_apis"], 1.0)
        self.assertLess(penalties["security_and_compliance"], 1.0)
        self.assertLess(penalties["installation_overview"], 1.0)

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
            source="doc_to_book_bm25",
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
            source="doc_to_book_bm25",
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
                "doc_to_book_bm25": [intake_command_a, intake_command_b],
                "vector": [concept_hit, example_hit],
            },
            top_k=4,
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

    def test_fusion_prefers_pod_issue_section_over_installation_etcd_for_pending_question(self) -> None:
        installation_hit = RetrievalHit(
            chunk_id="support-install-etcd",
            book_slug="support",
            chapter="support",
            section="7.1.9. etcd 설치 문제 조사",
            anchor="investigating-etcd-installation-issues",
            source_url="https://example.com/support",
            viewer_path="/docs/support.html#investigating-etcd-installation-issues",
            text="지원 7장. 문제 해결 > 7.1. 설치 문제 해결 > 7.1.9. etcd 설치 문제 조사 Pod의 이벤트를 검토합니다. oc describe pod/<pod_name> -n <namespace>",
            source="bm25",
            raw_score=1.0,
            fused_score=1.0,
        )
        pod_issue_hit = RetrievalHit(
            chunk_id="support-pod-issues",
            book_slug="support",
            chapter="support",
            section="7.7.1. Pod 오류 상태 이해",
            anchor="understanding-pod-error-states",
            source_url="https://example.com/support",
            viewer_path="/docs/support.html#understanding-pod-error-states",
            text="지원 7장. 문제 해결 > 7.7. Pod 문제 조사 > 7.7.1. Pod 오류 상태 이해 FailedScheduling Pending node affinity taint toleration",
            source="vector",
            raw_score=0.97,
            fused_score=0.97,
        )

        hits = fuse_ranked_hits(
            "Pod가 Pending 상태로 오래 멈춰 있을 때 어디부터 확인해야 해? Pending FailedScheduling pod issues error states node affinity taint toleration",
            {"bm25": [installation_hit], "vector": [pod_issue_hit]},
            top_k=2,
        )

        self.assertEqual("support-pod-issues", hits[0].chunk_id)

    def test_retriever_short_circuits_unsupported_external_query(self) -> None:
        settings = Settings(ROOT)
        retriever = Part2Retriever(settings, BM25Index.from_rows([]), vector_retriever=None)

        result = retriever.retrieve("Harbor 설치 방법 알려줘", use_bm25=False, use_vector=False)

        self.assertEqual([], result.hits)
        self.assertTrue(
            any("outside OCP corpus" in warning for warning in result.trace["warnings"])
        )


if __name__ == "__main__":
    unittest.main()
