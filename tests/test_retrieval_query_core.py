from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_retrieval import *  # noqa: F401,F403

class TestRetrievalQueryCore(unittest.TestCase):
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

    def test_decompose_retrieval_queries_adds_update_doc_locator_subqueries(self) -> None:
        queries = decompose_retrieval_queries("업데이트 관련 문서는 뭐부터 보면 돼?")

        self.assertEqual(
            [
                "업데이트 관련 문서는 뭐부터 보면 돼?",
                "OpenShift 클러스터 업데이트 가이드",
                "OpenShift 릴리스 노트",
                "업데이트 전 준비 문서",
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

    def test_fuse_ranked_hits_prefers_custom_overlay_over_vector_for_exact_match(self) -> None:
        intake_hit = RetrievalHit(
            chunk_id="dtb-demo:events",
            book_slug="demo-guide",
            chapter="문제 해결",
            section="Safety Switch 확인",
            anchor="safety-switch",
            source_url="https://example.com/demo",
            viewer_path="/docs/intake/dtb-demo/index.html#safety-switch",
            text="maintenance token 77A 와 nebula-drain 플래그를 먼저 확인합니다.",
            source="custom_bm25",
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
            {"custom_bm25": [intake_hit], "vector": [vector_hit]},
            top_k=2,
            weights={"bm25": 1.0, "custom_bm25": 1.35, "vector": 1.0},
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
            source="custom_bm25",
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
            source="custom_bm25",
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
            source="custom_bm25",
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

    def test_retriever_disables_custom_overlay_sections_in_default_bm25_path(self) -> None:
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

        self.assertEqual([], result.hits)
        self.assertEqual([], result.trace["custom_bm25"])
        self.assertEqual(0, result.trace["metrics"]["custom_bm25"]["count"])

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
            source="custom_bm25",
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
            {"custom_bm25": [intake_hit], "bm25": [generic_intro_hit]},
            top_k=2,
            weights={"bm25": 1.0, "custom_bm25": 1.35, "vector": 1.0},
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

    def test_rewrite_query_uses_route_ingress_context_for_compare_follow_up(self) -> None:
        context = SessionContext(
            user_goal="OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘",
            current_topic="Route와 Ingress 비교",
            open_entities=["OpenShift", "Route", "Ingress"],
            ocp_version="4.20",
        )

        rewritten = rewrite_query("쿠버네티스와 차이도 설명해줘", context)

        self.assertIn("Route와 Ingress 비교", rewritten)
        self.assertIn("OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘", rewritten)
        self.assertIn("쿠버네티스와 차이도 설명해줘", rewritten)

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

    def test_normalize_query_expands_route_ingress_compare_terms(self) -> None:
        normalized = normalize_query("OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘")

        self.assertIn("networking", normalized)
        self.assertIn("router", normalized)
        self.assertIn("ingresscontroller", normalized)
        self.assertIn("애플리케이션 노출", normalized)

    def test_query_book_adjustments_bias_route_ingress_compare_toward_networking_family(self) -> None:
        boosts, penalties = query_book_adjustments(
            "OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘"
        )

        self.assertGreater(boosts["networking_overview"], 1.0)
        self.assertGreater(boosts["ingress_and_load_balancing"], 1.0)
        self.assertLess(penalties["architecture"], 1.0)
        self.assertLess(penalties["overview"], 1.0)
        self.assertLess(penalties["security_and_compliance"], 1.0)

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

    def test_query_book_adjustments_bias_update_doc_locator_toward_update_books(self) -> None:
        boosts, penalties = query_book_adjustments("업데이트 관련 문서는 뭐부터 보면 돼?")

        self.assertGreater(boosts["updating_clusters"], 1.0)
        self.assertGreater(boosts["release_notes"], 1.0)
        self.assertGreater(boosts["overview"], 1.0)
        self.assertLess(penalties["cli_tools"], 1.0)
        self.assertLess(penalties["config_apis"], 1.0)
