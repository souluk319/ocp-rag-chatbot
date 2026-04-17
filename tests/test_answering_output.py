from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_answering import (
    ChatAnswerer,
    Citation,
    RetrievalHit,
    RetrievalResult,
    SessionContext,
    Settings,
    _BareCommandLLMClient,
    _DuplicateCitationLLMClient,
    _DuplicateCitationRetriever,
    _FakeRetriever,
    _MultiCitationRetriever,
    _NarrativeNoCitationLLMClient,
    _NoCitationLLMClient,
    _PodLifecycleRetriever,
    _PodPendingRetriever,
    _SinglePodLifecycleRetriever,
    _SinglePodPendingRetriever,
    ensure_korean_product_terms,
    finalize_citations,
    normalize_answer_text,
    normalize_answer_markup_blocks,
    restore_readable_paragraphs,
    reshape_ops_answer_text,
    select_fallback_citations,
    shape_actionable_ops_answer,
    strip_intro_offtopic_noise,
    strip_structured_key_extra_guidance,
    strip_weak_additional_guidance,
    summarize_session_context,
)

class TestAnsweringOutput(unittest.TestCase):
    def test_normalize_answer_text_enforces_single_answer_prefix(self) -> None:
        normalized = normalize_answer_text("### 답변\n안녕하세요\nOpenShift 설명입니다. [1]")

        self.assertEqual("답변: OpenShift 설명입니다. [1]", normalized)

    def test_normalize_answer_markup_blocks_converts_internal_code_tags(self) -> None:
        normalized = normalize_answer_markup_blocks(
            "답변: 확인 순서는 다음과 같습니다.\n[CODE]\noc describe pod/<pod>\n[/CODE]"
        )

        self.assertNotIn("[CODE]", normalized)
        self.assertIn("```bash", normalized)
        self.assertIn("oc describe pod/<pod>", normalized)

    def test_normalize_answer_markup_blocks_converts_internal_table_tags(self) -> None:
        normalized = normalize_answer_markup_blocks(
            "답변: 표는 아래와 같습니다.\n[TABLE]\n이름 | 상태\npod-a | Pending\n[/TABLE]"
        )

        self.assertNotIn("[TABLE]", normalized)
        self.assertIn("```text", normalized)
        self.assertIn("이름 | 상태", normalized)

    def test_reshape_ops_answer_text_wraps_bare_command(self) -> None:
        reshaped = reshape_ops_answer_text(
            "답변: $ oc adm policy add-role-to-user admin <사용자명> -n <namespace> [1]",
            mode="ops",
        )

        self.assertTrue(reshaped.startswith("답변: 아래 명령을 사용하세요 [1]."))
        self.assertIn("```bash", reshaped)
        self.assertIn("oc adm policy add-role-to-user admin <사용자명> -n <namespace>", reshaped)

    def test_strip_weak_additional_guidance_removes_empty_disclaimer_tail(self) -> None:
        stripped = strip_weak_additional_guidance(
            "답변: 표준 절차는 다음과 같습니다 [1].\n\n추가 가이드: 현재 제공된 근거에 명시되어 있지 않습니다.",
            mode="ops",
            citations=[Citation(
                index=1,
                chunk_id="chunk-1",
                book_slug="postinstallation_configuration",
                section="4.12.5. etcd 데이터 백업",
                anchor="backup",
                source_url="https://example.com",
                viewer_path="/docs/example.html#backup",
                excerpt="cluster-backup.sh",
            )],
        )

        self.assertEqual("답변: 표준 절차는 다음과 같습니다 [1].", stripped)

    def test_strip_structured_key_extra_guidance_removes_speculative_tail(self) -> None:
        stripped = strip_structured_key_extra_guidance(
            "답변: 값은 `starfall-88` 입니다 [1].\n\n추가 가이드: 예: orion status check 등으로 확인하세요.",
            query="orion.unique/flag 값이 뭐야?",
            mode="ops",
        )

        self.assertEqual("답변: 값은 `starfall-88` 입니다 [1].", stripped)

    def test_ensure_korean_product_terms_keeps_both_names_for_compare_answer(self) -> None:
        updated = ensure_korean_product_terms(
            "답변: 오픈시프트는 쿠버네티스 기반 플랫폼입니다.",
            query="오픈시프트랑 쿠버네티스 차이를 설명해줘 OpenShift",
        )

        self.assertIn("오픈시프트(OpenShift)", updated)

    def test_ensure_korean_product_terms_adds_practical_tail_for_intro_query(self) -> None:
        updated = ensure_korean_product_terms(
            "답변: 오픈시프트는 쿠버네티스 기반 플랫폼입니다.",
            query="OCP가 뭐야?",
        )

        self.assertIn("실무에서는 이 플랫폼이 무엇을 관리하고 어떤 운영 작업을 대신해 주는지", updated)

    def test_ensure_korean_product_terms_adds_practical_tail_for_compare_query(self) -> None:
        updated = ensure_korean_product_terms(
            "답변: OpenShift는 쿠버네티스 기반 플랫폼입니다.",
            query="오픈시프트와 쿠버네티스 차이를 설명해줘",
        )

        self.assertIn("실무에서는 공통점보다 운영 기능의 차이와 사용 위치부터 보면 선택이 쉬워집니다.", updated)

    def test_restore_readable_paragraphs_splits_long_intro_answer(self) -> None:
        updated = restore_readable_paragraphs(
            "답변: 오픈시프트(OpenShift)는 쿠버네티스 기반 플랫폼입니다 [1]. "
            "실무에서는 애플리케이션 배포와 운영 자동화에 사용합니다 [2]. "
            "원하면 아키텍처와 운영 관점 차이도 이어서 설명하겠습니다 [3]."
        )

        self.assertIn("[2].\n\n원하면", updated)
        self.assertIn("실무에서는 애플리케이션 배포와 운영 자동화에 사용합니다 [2].", updated)

    def test_strip_intro_offtopic_noise_removes_etcd_backup_sentence(self) -> None:
        updated = strip_intro_offtopic_noise(
            "답변: 오픈시프트는 플랫폼입니다. 클러스터 업데이트 전에는 반드시 etcd 백업을 수행해야 합니다.",
            query="오픈시프트가 뭐야?",
        )

        self.assertNotIn("etcd 백업", updated)

    def test_summarize_session_context_flattens_follow_up_hints(self) -> None:
        summary = summarize_session_context(
            SessionContext(
                mode="ops",
                current_topic="etcd 백업",
                open_entities=["etcd"],
                unresolved_question="복원 절차",
                ocp_version="4.20",
            )
        )

        self.assertIn("현재 주제: etcd 백업", summary)
        self.assertIn("열린 엔터티: etcd", summary)
        self.assertIn("미해결 질문: 복원 절차", summary)

    def test_finalize_citations_collapses_duplicate_targets(self) -> None:
        citations = [
            Citation(
                index=1,
                chunk_id="chunk-1",
                book_slug="support",
                section="7.2.1. 노드 상태, 리소스 사용량 및 구성 확인",
                anchor="checking-node-resource-usage",
                source_url="https://example.com/support",
                viewer_path="/docs/ocp/4.20/ko/support/index.html#checking-node-resource-usage",
                excerpt="oc adm top nodes",
            ),
            Citation(
                index=2,
                chunk_id="chunk-2",
                book_slug="support",
                section="7.2.1. 노드 상태, 리소스 사용량 및 구성 확인",
                anchor="checking-node-resource-usage",
                source_url="https://example.com/support",
                viewer_path="/docs/ocp/4.20/ko/support/index.html#checking-node-resource-usage",
                excerpt="oc adm top node my-node",
            ),
        ]

        answer_text, final_citations, cited_indices = finalize_citations(
            "답변: `oc adm top nodes` 명령을 사용하세요 [1][2].",
            citations,
        )

        self.assertEqual("답변: `oc adm top nodes` 명령을 사용하세요 [1].", answer_text)
        self.assertEqual([1], cited_indices)
        self.assertEqual(1, len(final_citations))

    def test_finalize_citations_strips_invalid_reference_markers(self) -> None:
        citations = [
            Citation(
                index=1,
                chunk_id="chunk-1",
                book_slug="nodes",
                section="8.1.3. 이벤트 목록",
                anchor="events",
                source_url="https://example.com/nodes",
                viewer_path="/docs/nodes.html#events",
                excerpt="이벤트",
            )
        ]

        answer_text, final_citations, cited_indices = finalize_citations(
            "답변: 먼저 [1][2]를 보고, 다음 단계도 [2] 대신 [1]을 기준으로 판단합니다.",
            citations,
        )

        self.assertEqual(
            "답변: 먼저 [1]를 보고, 다음 단계도 대신 [1]을 기준으로 판단합니다.",
            answer_text,
        )
        self.assertEqual([1], cited_indices)
        self.assertEqual(1, len(final_citations))

    def test_finalize_citations_preserves_code_block_indentation(self) -> None:
        citations = [
            Citation(
                index=1,
                chunk_id="chunk-1",
                book_slug="authentication_and_authorization",
                section="9.6. 사용자 역할 추가",
                anchor="adding-user-role",
                source_url="https://example.com/auth",
                viewer_path="/docs/auth.html#adding-user-role",
                excerpt="RoleBinding YAML",
            )
        ]

        answer_text, _, _ = finalize_citations(
            "답변: YAML 예시는 아래와 같습니다 [1].\n\n"
            "```yaml\n"
            "metadata:\n"
            "  name: admin-0\n"
            "  namespace: joe\n"
            "subjects:\n"
            "- apiGroup: rbac.authorization.k8s.io\n"
            "  kind: User\n"
            "  name: alice\n"
            "```",
            citations,
        )

        self.assertIn("  name: admin-0", answer_text)
        self.assertIn("  namespace: joe", answer_text)
        self.assertIn("  kind: User", answer_text)

    def test_answerer_deduplicates_same_section_citations(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_DuplicateCitationRetriever(),
            llm_client=_DuplicateCitationLLMClient(),
        )

        result = answerer.answer(
            "지금 클러스터 내 전체 노드들의 CPU랑 메모리 사용량을 한눈에 확인하고 싶은데, 어떤 CLI 명령어를 써야 해?",
            mode="ops",
        )

        self.assertEqual(
            "답변: `oc adm top nodes`는 클러스터 전체 노드의 CPU와 메모리 사용량을 빠르게 훑어볼 때 먼저 쓰는 명령입니다 [1].\n\n"
            "노드 과부하, 리소스 불균형, 드레인이나 점검 전에 현재 사용량을 확인해야 할 때 유용합니다 [1]. "
            "특정 노드만 보고 싶으면 `oc adm top node <node-name>` 형태로 좁혀서 확인하면 됩니다 [1].\n\n"
            "```bash\noc adm top nodes\n```",
            result.answer,
        )
        self.assertEqual([1], result.cited_indices)
        self.assertEqual(1, len(result.citations))
        self.assertEqual(
            "/docs/ocp/4.20/ko/support/index.html#checking-node-resource-usage",
            result.citations[0].viewer_path,
        )

    def test_answerer_blocks_single_missing_inline_citation(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_FakeRetriever(),
            llm_client=_NoCitationLLMClient(),
        )

        result = answerer.answer(
            "특정 namespace에만 admin 권한 주려면 어떤 명령 써?",
            mode="ops",
        )

        self.assertEqual("no_answer", result.response_kind)
        self.assertIn("현재 Playbook Library에 해당 자료가 없습니다", result.answer)
        self.assertEqual([], result.cited_indices)
        self.assertEqual(0, len(result.citations))
        self.assertIn("answer has no inline citations", result.warnings)

    def test_select_fallback_citations_deduplicates_and_limits(self) -> None:
        citations = [
            Citation(
                index=1,
                chunk_id="chunk-1",
                book_slug="support",
                section="A",
                anchor="same",
                source_url="https://example.com/support",
                viewer_path="/docs/support.html#same",
                excerpt="first",
            ),
            Citation(
                index=2,
                chunk_id="chunk-2",
                book_slug="support",
                section="A",
                anchor="same",
                source_url="https://example.com/support",
                viewer_path="/docs/support.html#same",
                excerpt="second",
            ),
            Citation(
                index=3,
                chunk_id="chunk-3",
                book_slug="nodes",
                section="B",
                anchor="other",
                source_url="https://example.com/nodes",
                viewer_path="/docs/nodes.html#other",
                excerpt="third",
            ),
        ]

        selected = select_fallback_citations(citations, limit=2)

        self.assertEqual(2, len(selected))
        self.assertEqual([1, 2], [citation.index for citation in selected])
        self.assertEqual(
            ["/docs/support.html#same", "/docs/nodes.html#other"],
            [citation.viewer_path for citation in selected],
        )

    def test_answerer_blocks_learn_answer_when_inline_citations_are_missing(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_MultiCitationRetriever(),
            llm_client=_NarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("OpenShift 아키텍처를 설명해줘", mode="learn")

        self.assertEqual("no_answer", result.response_kind)
        self.assertEqual([], result.citations)
        self.assertEqual(
            "답변: 현재 Playbook Library에 해당 자료가 없습니다. 자료 추가가 필요합니다.",
            result.answer,
        )
        self.assertIn("answer has no inline citations", result.warnings)

    def test_answerer_runtime_preserves_grounded_multi_hit_answer_when_inline_citations_are_missing(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_MultiCitationRetriever(),
            llm_client=_NarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("OpenShift 아키텍처를 운영 관점에서 짧게 설명해줘", mode="runtime")

        self.assertEqual("rag", result.response_kind)
        self.assertIn("[1]", result.answer)
        self.assertIn("[2]", result.answer)
        self.assertNotIn("현재 Playbook Library에 해당 자료가 없습니다", result.answer)
        self.assertEqual([1, 2], result.cited_indices)
        self.assertCountEqual(
            ["OpenShift 아키텍처 개요", "플랫폼 개요"],
            [citation.section for citation in result.citations],
        )

    def test_answerer_runtime_preserves_grounded_duplicate_section_answer_when_inline_citations_are_missing(self) -> None:
        class _RbacProcedureRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hits = [
                    RetrievalHit(
                        chunk_id="rbac-procedure-1",
                        book_slug="authentication_and_authorization",
                        chapter="authentication_and_authorization",
                        section="9.6. 사용자 역할 추가",
                        anchor="adding-user-role",
                        source_url="https://example.com/auth",
                        viewer_path="/docs/auth.html#adding-user-role",
                        text="oc adm policy add-role-to-user <role> <user> -n <project>",
                        source="hybrid",
                        raw_score=1.0,
                        fused_score=1.0,
                    ),
                    RetrievalHit(
                        chunk_id="rbac-procedure-2",
                        book_slug="authentication_and_authorization",
                        chapter="authentication_and_authorization",
                        section="9.6. 사용자 역할 추가",
                        anchor="adding-user-role",
                        source_url="https://example.com/auth",
                        viewer_path="/docs/auth.html#adding-user-role",
                        text="oc describe rolebinding.rbac -n <project>",
                        source="hybrid",
                        raw_score=0.97,
                        fused_score=0.97,
                    ),
                ]
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=hits,
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _RbacNarrativeNoCitationLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return (
                    "답변: 먼저 역할을 바인딩하고, 적용 후에는 rolebinding 상태를 확인해 검증하면 됩니다.\n\n"
                    "```bash\n"
                    "oc adm policy add-role-to-user <role> <user> -n <project>\n"
                    "```\n\n"
                    "```bash\n"
                    "oc describe rolebinding.rbac -n <project>\n"
                    "```"
                )

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_RbacProcedureRetriever(),
            llm_client=_RbacNarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("인증 및 권한 부여 핵심 절차를 알려줘", mode="runtime")

        self.assertEqual("rag", result.response_kind)
        self.assertIn("[1]", result.answer)
        self.assertNotIn("현재 Playbook Library에 해당 자료가 없습니다", result.answer)
        self.assertEqual([1], result.cited_indices)
        self.assertEqual(
            ["9.6. 사용자 역할 추가"],
            [citation.section for citation in result.citations],
        )

    def test_answerer_shapes_english_mixed_etcd_backup_query_into_code_block(self) -> None:
        class _EtcdBackupSectionOnlyRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hit = RetrievalHit(
                    chunk_id="etcd-backup-section",
                    book_slug="postinstallation_configuration",
                    chapter="설치 후 구성",
                    section="4.12.5. etcd 데이터 백업",
                    anchor="etcd-backup",
                    source_url="https://example.com/postinstall",
                    viewer_path="/docs/postinstall.html#etcd-backup",
                    text="etcd 데이터를 백업합니다.",
                    source="hybrid",
                    raw_score=1.0,
                    fused_score=1.0,
                )
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=[hit],
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _EtcdBackupNarrativeLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return "답변: etcd 데이터 백업은 클러스터 전체 프록시가 활성화된 상태에서 수행합니다."

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_EtcdBackupSectionOnlyRetriever(),
            llm_client=_EtcdBackupNarrativeLLMClient(),
        )

        result = answerer.answer("etcd backup은 어떻게함?", mode="ops")

        self.assertIn("oc debug --as-root node/<node_name>", result.answer)
        self.assertIn("chroot /host", result.answer)
        self.assertIn("cluster-backup.sh", result.answer)
        self.assertIn("```bash", result.answer)
        self.assertIn("[1]", result.answer)
        self.assertNotIn("inline citations auto-repaired", result.warnings)

    def test_answerer_shapes_project_terminating_into_command_first_guide(self) -> None:
        class _ProjectTerminatingRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hit = RetrievalHit(
                    chunk_id="project-terminating",
                    book_slug="building_applications",
                    chapter="building_applications",
                    section="2.1.7. 프로젝트 삭제",
                    anchor="project-delete",
                    source_url="https://example.com/postinstall",
                    viewer_path="/docs/postinstall.html#project-delete",
                    text="oc get projects\noc get all -n <project>",
                    source="hybrid",
                    raw_score=1.0,
                    fused_score=1.0,
                )
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=[hit],
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _NarrativeTerminatingLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return "답변: 프로젝트 삭제가 멈춘 상태를 요약해서 설명합니다."

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_ProjectTerminatingRetriever(),
            llm_client=_NarrativeTerminatingLLMClient(),
        )

        result = answerer.answer("프로젝트가 Terminating에서 안 지워질 때 어떻게 해?", mode="ops")

        self.assertIn("```bash", result.answer)
        self.assertIn("oc get projects", result.answer)
        self.assertIn("oc get all -n <project>", result.answer)
        self.assertIn("먼저 종료 중인 네임스페이스와 관련 리소스 상태를 확인", result.answer)
        self.assertNotIn("요약해서 설명합니다", result.answer)

    def test_shape_actionable_ops_answer_moves_inline_command_into_code_block(self) -> None:
        citations = [
            Citation(
                index=1,
                chunk_id="chunk-1",
                book_slug="postinstallation_configuration",
                section="2.1.7. 프로젝트 삭제",
                anchor="project-delete",
                source_url="https://example.com/postinstall",
                viewer_path="/docs/postinstall.html#project-delete",
                excerpt="oc get all -n <project>",
            )
        ]

        shaped = shape_actionable_ops_answer(
            "답변: 먼저 관련 리소스를 확인하려면 `oc get all -n <project>` 명령을 사용합니다 [1].",
            query="프로젝트가 Terminating에서 안 지워질 때 어떻게 해?",
            citations=citations,
        )

        self.assertIn("```bash\noc get all -n <project>\n```", shaped)
        self.assertTrue(shaped.startswith("답변: 먼저 남아 있는 리소스와 상태를 아래 명령으로 확인하면 됩니다 [1]."))

    def test_answerer_shapes_rbac_yaml_follow_up_into_manifest_example(self) -> None:
        class _RbacYamlRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hit = RetrievalHit(
                    chunk_id="rbac-yaml",
                    book_slug="authentication_and_authorization",
                    chapter="authentication_and_authorization",
                    section="9.6. 사용자 역할 추가",
                    anchor="adding-user-role",
                    source_url="https://example.com/auth",
                    viewer_path="/docs/auth.html#adding-user-role",
                    text="RoleBinding 예시는 apiVersion, kind, metadata, subjects, roleRef를 사용합니다.",
                    source="hybrid",
                    raw_score=1.0,
                    fused_score=1.0,
                )
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=[hit],
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _NarrativeNoCitationLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return "답변: 제공된 문서에는 RoleBinding 예시가 있습니다."

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_RbacYamlRetriever(),
            llm_client=_NarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("그 RoleBinding YAML 예시도 보여줘", mode="ops")

        self.assertIn("```yaml", result.answer)
        self.assertIn("kind: RoleBinding", result.answer)
        self.assertIn("name: admin-0", result.answer)
        self.assertIn("- apiGroup: rbac.authorization.k8s.io", result.answer)
        self.assertIn("roleRef:", result.answer)
        self.assertIn("```bash\noc apply -f rolebinding.yaml\n```", result.answer)
        self.assertIn("[1]", result.answer)

    def test_answerer_shapes_rbac_verify_follow_up_into_describe_command(self) -> None:
        class _RbacVerifyRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hit = RetrievalHit(
                    chunk_id="rbac-verify",
                    book_slug="authorization_apis",
                    chapter="authorization_apis",
                    section="SelfSubjectAccessReview",
                    anchor="selfsubjectaccessreview",
                    source_url="https://example.com/apis",
                    viewer_path="/docs/apis.html#selfsubjectaccessreview",
                    text="SelfSubjectAccessReview와 SelfSubjectRulesReview로 권한을 검증할 수 있습니다. oc describe rolebinding.rbac -n <project>",
                    source="hybrid",
                    raw_score=1.0,
                    fused_score=1.0,
                )
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=[hit],
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _NarrativeVerifyLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return "답변: 권한 검증은 관련 API를 확인해 보세요."

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_RbacVerifyRetriever(),
            llm_client=_NarrativeVerifyLLMClient(),
        )

        result = answerer.answer("그 권한이 잘 들어갔는지 확인하는 명령도 알려줘", mode="ops")

        self.assertIn("oc describe rolebinding.rbac -n <project>", result.answer)
        self.assertIn("SelfSubjectRulesReview", result.answer)
        self.assertIn("[1]", result.answer)

    def test_answerer_shapes_namespace_admin_answer_into_two_code_blocks(self) -> None:
        class _NamespaceAdminRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hit = RetrievalHit(
                    chunk_id="rbac-admin-command",
                    book_slug="authentication_and_authorization",
                    chapter="authentication_and_authorization",
                    section="9.6. 사용자 역할 추가",
                    anchor="adding-user-role",
                    source_url="https://example.com/auth",
                    viewer_path="/docs/auth.html#adding-user-role",
                    text=(
                        "oc adm policy add-role-to-user admin <user> -n <project>\n"
                        "예를 들면 oc adm policy add-role-to-user admin alice -n joe"
                    ),
                    source="hybrid",
                    raw_score=1.0,
                    fused_score=1.0,
                )
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=[hit],
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _NamespaceNarrativeLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return "답변: 특정 네임스페이스에만 admin 권한을 주려면 다음 명령을 사용하세요."

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_NamespaceAdminRetriever(),
            llm_client=_NamespaceNarrativeLLMClient(),
        )

        result = answerer.answer("특정 namespace에만 admin 권한 주려면 어떤 명령 써?", mode="ops")

        self.assertIn("```bash\noc adm policy add-role-to-user admin <user> -n <project>\n```", result.answer)
        self.assertIn("```bash\noc adm policy add-role-to-user admin alice -n joe\n```", result.answer)
        self.assertEqual(2, result.answer.count("```bash"))

    def test_answerer_shapes_concrete_namespace_admin_follow_up_with_target_substitution(self) -> None:
        class _NamespaceAdminRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hit = RetrievalHit(
                    chunk_id="rbac-admin-command",
                    book_slug="authentication_and_authorization",
                    chapter="authentication_and_authorization",
                    section="9.6. 사용자 역할 추가",
                    anchor="adding-user-role",
                    source_url="https://example.com/auth",
                    viewer_path="/docs/auth.html#adding-user-role",
                    text=(
                        "oc adm policy add-role-to-user admin <user> -n <project>\n"
                        "예를 들면 oc adm policy add-role-to-user admin alice -n joe"
                    ),
                    source="hybrid",
                    raw_score=1.0,
                    fused_score=1.0,
                )
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=[hit],
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _NamespaceNarrativeLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return "답변: namespace에 admin 역할을 부여하려면 관련 명령을 사용하세요."

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_NamespaceAdminRetriever(),
            llm_client=_NamespaceNarrativeLLMClient(),
        )

        result = answerer.answer(
            "예를들어 cywell 프로젝트의 kugnus 사용자에게 어드민 역할을 주려면 어떻게해?",
            mode="ops",
        )

        self.assertIn("`cywell` 프로젝트의 `kugnus` 사용자", result.answer)
        self.assertIn("```bash\noc adm policy add-role-to-user admin kugnus -n cywell\n```", result.answer)
        self.assertIn("```bash\noc adm policy add-role-to-user admin <user> -n <project>\n```", result.answer)
        self.assertEqual(2, result.answer.count("```bash"))

    def test_answerer_does_not_hijack_etcd_follow_up_into_rbac_answer(self) -> None:
        class _EtcdBackupTroubleshootingRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hit = RetrievalHit(
                    chunk_id="etcd-backup-follow-up",
                    book_slug="postinstallation_configuration",
                    chapter="postinstallation_configuration",
                    section="4.12.5. etcd 데이터 백업",
                    anchor="etcd-backup",
                    source_url="https://example.com/postinstall",
                    viewer_path="/docs/postinstall.html#etcd-backup",
                    text="oc debug --as-root node/<node_name>\nchroot /host\n/usr/local/bin/cluster-backup.sh /home/core/assets/backup",
                    source="hybrid",
                    raw_score=1.0,
                    fused_score=1.0,
                )
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query="백업이나 복원 중 문제가 나면 어디부터 확인해야 해? 백업",
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=[hit],
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _EtcdTroubleshootingNarrativeLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return "답변: 먼저 관련 구성을 확인해 보세요."

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_EtcdBackupTroubleshootingRetriever(),
            llm_client=_EtcdTroubleshootingNarrativeLLMClient(),
        )

        result = answerer.answer("백업이나 복원 중 문제가 나면 어디부터 확인해야 해?", mode="ops")

        self.assertIn("절차가 실제로 끝까지 수행됐는지", result.answer)
        self.assertIn("cluster-backup.sh", result.answer)
        self.assertIn("oc debug --as-root node/<node_name>", result.answer)
        self.assertNotIn("RoleBinding", result.answer)
        self.assertNotIn("SelfSubjectRulesReview", result.answer)

    def test_answerer_shapes_etcd_restore_follow_up_with_grounded_restore_command(self) -> None:
        class _EtcdRestoreRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hits = [
                    RetrievalHit(
                        chunk_id="etcd-restore-1",
                        book_slug="etcd",
                        chapter="etcd",
                        section="4.3.2.4. etcd 백업에서 수동으로 클러스터 복원",
                        anchor="restore-manual",
                        source_url="https://example.com/etcd",
                        viewer_path="/docs/etcd.html#restore-manual",
                        text="etcd 백업 디렉터리를 각 컨트롤 플레인 호스트에 복사합니다.",
                        source="hybrid",
                        raw_score=1.0,
                        fused_score=1.0,
                    ),
                    RetrievalHit(
                        chunk_id="etcd-restore-2",
                        book_slug="etcd",
                        chapter="etcd",
                        section="4.3.2.4. etcd 백업에서 수동으로 클러스터 복원",
                        anchor="restore-manual",
                        source_url="https://example.com/etcd",
                        viewer_path="/docs/etcd.html#restore-manual",
                        text="ETCDCTL_API=3 /usr/bin/etcdctl snapshot restore /var/lib/etcd/<snapshot_yyyy-mm-dd_hhmmss>.db",
                        source="hybrid",
                        raw_score=0.99,
                        fused_score=0.99,
                    ),
                    RetrievalHit(
                        chunk_id="etcd-restore-3",
                        book_slug="etcd",
                        chapter="etcd",
                        section="4.3.2.4. etcd 백업에서 수동으로 클러스터 복원",
                        anchor="restore-manual",
                        source_url="https://example.com/etcd",
                        viewer_path="/docs/etcd.html#restore-manual",
                        text="crictl ps | grep etcd | grep -v operator",
                        source="hybrid",
                        raw_score=0.98,
                        fused_score=0.98,
                    ),
                ]
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query="OCP 4.20 | 주제 etcd 백업 | 엔터티 etcd | 미해결 질문 etcd 백업 이후 복구 절차 | 그 복구는 어떻게 해? 복원",
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=hits,
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _NoCitationRestoreLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return "답변: 각 노드에 백업 디렉터리를 준비한 뒤 상태를 확인하세요."

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_EtcdRestoreRetriever(),
            llm_client=_NoCitationRestoreLLMClient(),
        )

        result = answerer.answer("그 복구는 어떻게 해?", mode="ops")

        self.assertIn("복원", result.answer)
        self.assertIn("etcdctl snapshot restore", result.answer)
        self.assertIn("[1]", result.answer)
        self.assertNotEqual([], result.citations)

    def test_answerer_shapes_node_drain_answer_even_when_llm_omits_inline_citation(self) -> None:
        class _NodeDrainRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hit = RetrievalHit(
                    chunk_id="node-drain",
                    book_slug="nodes",
                    chapter="nodes",
                    section="6.2.1. 노드에서 Pod를 비우는 방법 이해",
                    anchor="drain-node",
                    source_url="https://example.com/nodes",
                    viewer_path="/docs/nodes.html#drain-node",
                    text=(
                        "oc adm drain worker-0 --ignore-daemonsets --delete-emptydir-data\n"
                        "oc adm uncordon worker-0\n"
                        "--delete-emptydir-data 사용 전 로컬 데이터 손실 영향을 확인합니다."
                    ),
                    source="hybrid",
                    raw_score=1.0,
                    fused_score=1.0,
                    cli_commands=(
                        "oc adm drain worker-0 --ignore-daemonsets --delete-emptydir-data",
                        "oc adm uncordon worker-0",
                    ),
                )
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=[hit],
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _NoCitationDrainLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return (
                    "답변: 아래처럼 실행하세요.\n\n"
                    "```bash\noc adm drain worker-0 --ignore-daemonsets --delete-emptydir-data\n```"
                )

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_NodeDrainRetriever(),
            llm_client=_NoCitationDrainLLMClient(),
        )

        result = answerer.answer(
            "특정 작업자 노드 점검 때문에 비워야 해. drain 명령 예시랑 주의점만 짧게 줘",
            mode="ops",
        )

        self.assertIn("oc adm drain worker-0 --ignore-daemonsets --delete-emptydir-data", result.answer)
        self.assertIn("oc adm uncordon worker-0", result.answer)
        self.assertIn("[1]", result.answer)
        self.assertEqual([], result.warnings)
        self.assertNotEqual([], result.citations)

    def test_answerer_shapes_rbac_revoke_follow_up_into_remove_command(self) -> None:
        class _RbacRevokeRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hit = RetrievalHit(
                    chunk_id="rbac-revoke",
                    book_slug="authentication_and_authorization",
                    chapter="authentication_and_authorization",
                    section="9.6. 사용자 역할 제거",
                    anchor="remove-user-role",
                    source_url="https://example.com/auth",
                    viewer_path="/docs/auth.html#remove-user-role",
                    text="oc adm policy remove-role-from-user admin <user> -n <project> 명령으로 로컬 역할 바인딩을 제거합니다.",
                    source="hybrid",
                    raw_score=1.0,
                    fused_score=1.0,
                )
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=[hit],
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _NarrativeRevokeLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return "답변: 권한은 제거할 수 있습니다."

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_RbacRevokeRetriever(),
            llm_client=_NarrativeRevokeLLMClient(),
        )

        result = answerer.answer("그 권한을 회수하려면 어떻게 해?", mode="ops")

        self.assertIn("oc adm policy remove-role-from-user admin <user> -n <project>", result.answer)
        self.assertIn("```bash", result.answer)
        self.assertIn("[1]", result.answer)

    def test_answerer_prunes_images_citation_from_mco_concept_answer(self) -> None:
        class _McoConceptRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hits = [
                    RetrievalHit(
                        chunk_id="mco-images",
                        book_slug="images",
                        chapter="images",
                        section="Cluster image configuration",
                        anchor="image-config",
                        source_url="https://example.com/images",
                        viewer_path="/docs/images.html#image-config",
                        text="image.config.openshift.io/cluster 변경을 설명합니다.",
                        source="hybrid",
                        raw_score=1.0,
                        fused_score=1.0,
                    ),
                    RetrievalHit(
                        chunk_id="mco-core",
                        book_slug="machine_configuration",
                        chapter="machine_configuration",
                        section="About the Machine Config Operator",
                        anchor="about-mco",
                        source_url="https://example.com/mco",
                        viewer_path="/docs/mco.html#about-mco",
                        text="Machine Config Operator의 역할과 업데이트 흐름을 설명합니다.",
                        source="hybrid",
                        raw_score=0.99,
                        fused_score=0.99,
                    ),
                ]
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=hits,
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _McoConceptLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return (
                    "답변: Machine Config Operator는 노드 구성을 적용하고 변경을 롤아웃하는 핵심 제어기입니다 [1][2]."
                )

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_McoConceptRetriever(),
            llm_client=_McoConceptLLMClient(),
        )

        result = answerer.answer("Machine Config Operator가 뭐고 건드리면 뭐가 바뀌는지 설명해줘", mode="learn")

        self.assertEqual([1], result.cited_indices)
        self.assertEqual(["machine_configuration"], [citation.book_slug for citation in result.citations])
        self.assertNotIn("[2]", result.answer)

    def test_answerer_prunes_etcd_companion_citation_from_standard_backup_answer(self) -> None:
        class _StandardEtcdBackupRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hits = [
                    RetrievalHit(
                        chunk_id="backup-standard",
                        book_slug="postinstallation_configuration",
                        chapter="postinstallation_configuration",
                        section="4.12.5. etcd 데이터 백업",
                        anchor="backing-up-etcd-data_post-install-cluster-tasks",
                        source_url="https://example.com/postinstall",
                        viewer_path="/docs/postinstall.html#backing-up-etcd-data_post-install-cluster-tasks",
                        text="cluster-backup.sh 절차를 설명합니다.",
                        source="hybrid",
                        raw_score=1.0,
                        fused_score=1.0,
                    ),
                    RetrievalHit(
                        chunk_id="backup-companion",
                        book_slug="etcd",
                        chapter="etcd",
                        section="4.1.1. etcd 데이터 백업",
                        anchor="backing-up-etcd-data_etcd-backup",
                        source_url="https://example.com/etcd",
                        viewer_path="/docs/etcd.html#backing-up-etcd-data_etcd-backup",
                        text="전용 etcd 문서의 companion 설명입니다.",
                        source="hybrid",
                        raw_score=0.99,
                        fused_score=0.99,
                    ),
                ]
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=hits,
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _StandardEtcdBackupLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return "답변: 표준 절차는 설치 후 구성 문서를 기준으로 보면 됩니다 [1][2]."

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_StandardEtcdBackupRetriever(),
            llm_client=_StandardEtcdBackupLLMClient(),
        )

        result = answerer.answer("etcd 백업은 실제로 어떤 절차로 해? 표준적인 방법만 짧게 알려줘", mode="ops")

        self.assertEqual([1], result.cited_indices)
        self.assertEqual(["postinstallation_configuration"], [citation.book_slug for citation in result.citations])
        self.assertNotIn("[2]", result.answer)

    def test_answerer_shapes_cluster_admin_difference_follow_up(self) -> None:
        class _RbacDiffRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hits = [
                    RetrievalHit(
                        chunk_id="rbac-diff-1",
                        book_slug="authentication_and_authorization",
                        chapter="authentication_and_authorization",
                        section="프로젝트 권한 관리",
                        anchor="project-admin",
                        source_url="https://example.com/auth",
                        viewer_path="/docs/auth.html#project-admin",
                        text="admin은 프로젝트 범위의 로컬 바인딩에 주로 사용합니다.",
                        source="hybrid",
                        raw_score=1.0,
                        fused_score=1.0,
                    ),
                    RetrievalHit(
                        chunk_id="rbac-diff-2",
                        book_slug="authorization_apis",
                        chapter="authorization_apis",
                        section="ClusterRoleBinding",
                        anchor="clusterrolebinding",
                        source_url="https://example.com/apis",
                        viewer_path="/docs/apis.html#clusterrolebinding",
                        text="cluster-admin은 ClusterRoleBinding으로 클러스터 범위에 바인딩합니다.",
                        source="hybrid",
                        raw_score=0.98,
                        fused_score=0.98,
                    ),
                ]
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=hits,
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        class _NarrativeDiffLLMClient:
            def generate(self, messages, trace_callback=None):  # noqa: ANN001
                return "답변: 둘은 다릅니다."

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_RbacDiffRetriever(),
            llm_client=_NarrativeDiffLLMClient(),
        )

        result = answerer.answer("그럼 cluster-admin이랑 차이도 짧게 말해줘", mode="ops")

        self.assertIn("`admin`은 특정 프로젝트 또는 namespace", result.answer)
        self.assertIn("`cluster-admin`은 클러스터 전역", result.answer)
        self.assertIn("ClusterRoleBinding", result.answer)

    def test_answerer_shapes_pod_lifecycle_learn_response_from_grounded_citations(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_PodLifecycleRetriever(),
            llm_client=_NarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("Pod lifecycle 개념을 초보자 기준으로 설명해줘", mode="learn")

        self.assertIn("Pod 라이프사이클은 Pod가 생성되고 노드에 배치된 뒤", result.answer)
        self.assertIn("생성/배치", result.answer)
        self.assertIn("종료/교체", result.answer)
        self.assertIn("[1]", result.answer)
        self.assertNotIn("같이 보면 좋은 문서", result.answer)
        self.assertEqual(
            ["2.1.1. Pod 이해", "2.1.2. Pod 구성의 예"],
            [citation.section for citation in result.citations],
        )

    def test_answerer_shapes_pod_lifecycle_without_leaking_missing_second_citation(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_SinglePodLifecycleRetriever(),
            llm_client=_NarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("Pod lifecycle 개념을 초보자 기준으로 설명해줘", mode="learn")

        self.assertIn("[1]", result.answer)
        self.assertNotIn("[2]", result.answer)
        self.assertEqual([1], result.cited_indices)
        self.assertEqual(1, len(result.citations))

    def test_answerer_shapes_pod_pending_learn_response_from_grounded_citations(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_PodPendingRetriever(),
            llm_client=_NarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("Pod Pending일 때 어디부터 확인해야 해?", mode="learn")

        self.assertIn("Pod가 `Pending`이면 가장 먼저", result.answer)
        self.assertIn("oc describe pod <pod-name> -n <pod-namespace>", result.answer)
        self.assertIn("FailedScheduling", result.answer)
        self.assertIn("[1]", result.answer)
        self.assertIn("[2]", result.answer)
        self.assertEqual(
            ["8.1.3. 이벤트 목록", "4.4.4.2. 일치하는 라벨이 없는 노드 유사성"],
            [citation.section for citation in result.citations],
        )

    def test_answerer_shapes_pod_pending_without_leaking_missing_second_citation(self) -> None:
        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_SinglePodPendingRetriever(),
            llm_client=_NarrativeNoCitationLLMClient(),
        )

        result = answerer.answer("Pod Pending일 때 어디부터 확인해야 해?", mode="learn")

        self.assertIn("[1]", result.answer)
        self.assertNotIn("[2]", result.answer)
        self.assertEqual([1], result.cited_indices)
        self.assertEqual(1, len(result.citations))

    def test_answerer_reshapes_bare_ops_command_response(self) -> None:
        class _RbacCommandRetriever:
            def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
                hit = RetrievalHit(
                    chunk_id="rbac-admin-command",
                    book_slug="authentication_and_authorization",
                    chapter="authentication_and_authorization",
                    section="9.6. 사용자 역할 추가",
                    anchor="adding-user-role",
                    source_url="https://example.com/auth",
                    viewer_path="/docs/auth.html#adding-user-role",
                    text="oc adm policy add-role-to-user admin <사용자명> -n <namespace>",
                    source="hybrid",
                    raw_score=1.0,
                    fused_score=1.0,
                )
                return RetrievalResult(
                    query=query,
                    normalized_query=query,
                    rewritten_query=query,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    context=(context or SessionContext()).to_dict(),
                    hits=[hit],
                    trace={"warnings": [], "timings_ms": {"bm25_search": 1.0}},
                )

        settings = Settings(root_dir=ROOT)
        answerer = ChatAnswerer(
            settings=settings,
            retriever=_RbacCommandRetriever(),
            llm_client=_BareCommandLLMClient(),
        )

        result = answerer.answer(
            "특정 namespace에만 admin 권한 주려면 어떤 명령 써?",
            mode="ops",
        )

        self.assertIn("`admin` 권한", result.answer)
        self.assertIn("```bash", result.answer)
        self.assertIn("oc adm policy add-role-to-user admin <user> -n <project>", result.answer)
        self.assertEqual([1], result.cited_indices)
