from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_retrieval import (
    BM25Index,
    ChatRetriever,
    RetrievalHit,
    SessionContext,
    Settings,
    _filter_customer_pack_hits_by_selection,
    build_retrieval_plan,
    decompose_retrieval_queries,
    fuse_ranked_hits,
    has_command_request,
    has_corrective_follow_up,
    has_deployment_scaling_intent,
    has_follow_up_reference,
    normalize_query,
    query_book_adjustments,
    rewrite_query,
)


def _write_private_runtime_manifest(
    settings: Settings,
    *,
    draft_id: str,
    approval_state: str = "approved",
    tenant_id: str = "tenant-a",
    workspace_id: str = "workspace-a",
    vector_status: str = "skipped",
) -> Path:
    corpus_dir = settings.customer_pack_corpus_dir / draft_id
    corpus_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = corpus_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "artifact_version": "customer_private_corpus_v1",
                "draft_id": draft_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "pack_id": f"customer-pack:{draft_id}",
                "pack_version": draft_id,
                "classification": "private",
                "access_groups": [workspace_id, tenant_id],
                "provider_egress_policy": "local_only",
                "approval_state": approval_state,
                "publication_state": "draft",
                "redaction_state": "not_required",
                "source_lane": "customer_source_first_pack",
                "source_collection": "uploaded",
                "boundary_truth": "private_customer_pack_runtime",
                "runtime_truth_label": "Customer Source-First Pack",
                "boundary_badge": "Private Pack Runtime",
                "vector_status": vector_status,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest_path


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

    def test_fuse_ranked_hits_prefers_overlay_bm25_over_vector_for_exact_match(self) -> None:
        intake_hit = RetrievalHit(
            chunk_id="dtb-demo:events",
            book_slug="demo-guide",
            chapter="문제 해결",
            section="Safety Switch 확인",
            anchor="safety-switch",
            source_url="https://example.com/demo",
            viewer_path="/playbooks/customer-packs/dtb-demo/index.html#safety-switch",
            text="maintenance token 77A 와 nebula-drain 플래그를 먼저 확인합니다.",
            source="overlay_bm25",
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
            {"overlay_bm25": [intake_hit], "vector": [vector_hit]},
            top_k=2,
            weights={"bm25": 1.0, "overlay_bm25": 1.35, "vector": 1.0},
        )

        self.assertEqual("demo-guide", fused[0].book_slug)
        self.assertEqual("/playbooks/customer-packs/dtb-demo/index.html#safety-switch", fused[0].viewer_path)

    def test_filter_customer_pack_hits_by_selection_keeps_only_checked_drafts(self) -> None:
        selected_hit = RetrievalHit(
            chunk_id="draft-a:overview",
            book_slug="draft-a",
            chapter="개요",
            section="선택 문서",
            anchor="overview",
            source_url="/tmp/a.pdf",
            viewer_path="/playbooks/customer-packs/draft-a/index.html#overview",
            text="선택된 업로드 문서",
            source="overlay_bm25",
            raw_score=1.0,
        )
        unselected_hit = RetrievalHit(
            chunk_id="draft-b:overview",
            book_slug="draft-b",
            chapter="개요",
            section="제외 문서",
            anchor="overview",
            source_url="/tmp/b.pdf",
            viewer_path="/playbooks/customer-packs/draft-b/index.html#overview",
            text="선택되지 않은 업로드 문서",
            source="overlay_bm25",
            raw_score=0.9,
        )

        filtered = _filter_customer_pack_hits_by_selection(
            [selected_hit, unselected_hit],
            context=SessionContext(
                selected_draft_ids=["draft-a"],
                restrict_uploaded_sources=True,
            ),
        )

        self.assertEqual(["draft-a:overview"], [hit.chunk_id for hit in filtered])

    def test_filter_customer_pack_hits_by_selection_keeps_selected_root_for_derived_asset(self) -> None:
        derived_hit = RetrievalHit(
            chunk_id="draft-a--operation_playbook:overview",
            book_slug="draft-a--operation_playbook",
            chapter="개요",
            section="파생 문서",
            anchor="overview",
            source_url="/tmp/a.pdf",
            viewer_path="/playbooks/customer-packs/draft-a/assets/operation-playbook/index.html#overview",
            text="선택된 업로드의 파생 플레이북",
            source="overlay_bm25",
            raw_score=1.0,
        )

        filtered = _filter_customer_pack_hits_by_selection(
            [derived_hit],
            context=SessionContext(
                selected_draft_ids=["draft-a"],
                restrict_uploaded_sources=True,
            ),
        )

        self.assertEqual(["draft-a--operation_playbook:overview"], [hit.chunk_id for hit in filtered])

    def test_filter_customer_pack_hits_by_selection_returns_no_overlay_hits_when_none_checked(self) -> None:
        hit = RetrievalHit(
            chunk_id="draft-a:overview",
            book_slug="draft-a",
            chapter="개요",
            section="선택 문서",
            anchor="overview",
            source_url="/tmp/a.pdf",
            viewer_path="/playbooks/customer-packs/draft-a/index.html#overview",
            text="선택된 업로드 문서",
            source="overlay_bm25",
            raw_score=1.0,
        )

        filtered = _filter_customer_pack_hits_by_selection(
            [hit],
            context=SessionContext(
                selected_draft_ids=[],
                restrict_uploaded_sources=True,
            ),
        )

        self.assertEqual([], filtered)

    def test_retriever_uses_overlay_sections_when_selected_draft_is_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root)
            _write_private_runtime_manifest(settings, draft_id="dtb-demo")
            (settings.customer_pack_books_dir / "dtb-demo.json").write_text(
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
                                "viewer_path": "/playbooks/customer-packs/dtb-demo/index.html#events",
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
            retriever = ChatRetriever(settings, BM25Index.from_rows([]), vector_retriever=None)

            result = retriever.retrieve(
                "Pod Pending 이벤트 먼저 확인해야 해?",
                context=SessionContext(
                    selected_draft_ids=["dtb-demo"],
                    restrict_uploaded_sources=True,
                ),
                use_vector=False,
                top_k=3,
                candidate_k=5,
            )

        self.assertEqual("demo-guide", result.hits[0].book_slug)
        self.assertEqual("uploaded", result.hits[0].source_collection)
        self.assertIn("overlay_bm25", result.trace)
        self.assertEqual(1, result.trace["metrics"]["overlay_bm25"]["count"])

    def test_retriever_preserves_uploaded_candidate_for_explicit_customer_doc_query(self) -> None:
        class _FakeVectorRetriever:
            def search(self, query: str, top_k: int):
                del query, top_k
                return [
                    RetrievalHit(
                        chunk_id="core-backup",
                        book_slug="postinstallation_configuration",
                        chapter="postinstall",
                        section="4.12.5. etcd 데이터 백업",
                        anchor="backup",
                        source_url="https://example.com/postinstall",
                        viewer_path="/docs/postinstall.html#backup",
                        text="oc debug --as-root node\nchroot /host\n/usr/local/bin/cluster-backup.sh /home/core/assets/backup",
                        source="vector",
                        raw_score=0.92,
                        fused_score=0.92,
                    )
                ]

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root)
            _write_private_runtime_manifest(settings, draft_id="dtb-demo")
            (settings.customer_pack_books_dir / "dtb-demo.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "canonical_book_v1",
                        "book_slug": "customer-backup-runbook",
                        "title": "고객 백업 런북",
                        "source_type": "pdf",
                        "source_uri": "/tmp/customer.pdf",
                        "language_hint": "ko",
                        "source_view_strategy": "normalized_sections_v1",
                        "retrieval_derivation": "chunks_from_canonical_sections",
                        "quality_status": "ready",
                        "sections": [
                            {
                                "ordinal": 1,
                                "section_key": "customer-backup-runbook:openshift-backup-restore-runbook",
                                "heading": "OpenShift Backup Restore Runbook",
                                "section_level": 2,
                                "section_path": ["OpenShift Backup Restore Runbook"],
                                "section_path_label": "OpenShift Backup Restore Runbook",
                                "anchor": "openshift-backup-restore-runbook",
                                "viewer_path": "/playbooks/customer-packs/dtb-demo/index.html#openshift-backup-restore-runbook",
                                "source_url": "/tmp/customer.pdf",
                                "text": "1. Enter debug shell\n/usr/local/bin/cluster-backup.sh /home/core/assets/backup",
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
            retriever = ChatRetriever(
                settings,
                BM25Index.from_rows([]),
                vector_retriever=_FakeVectorRetriever(),
                reranker=None,
            )

            result = retriever.retrieve(
                "업로드 문서 기준으로 backup 절차를 알려줘",
                context=SessionContext(
                    selected_draft_ids=["dtb-demo"],
                    restrict_uploaded_sources=True,
                ),
                use_vector=True,
                top_k=3,
                candidate_k=5,
            )

        self.assertEqual("customer-backup-runbook", result.hits[0].book_slug)
        self.assertEqual("uploaded", result.hits[0].source_collection)
        self.assertEqual(1, result.trace["metrics"]["overlay_bm25"]["count"])

    def test_retriever_prioritizes_selected_uploaded_snippet_without_explicit_customer_doc_phrase(self) -> None:
        class _FakeVectorRetriever:
            def search(self, query: str, top_k: int):
                del query, top_k
                return [
                    RetrievalHit(
                        chunk_id="core-configmap-secret",
                        book_slug="authentication_and_authorization",
                        chapter="auth",
                        section="ConfigMap and Secret defaults",
                        anchor="configmap-secret",
                        source_url="https://example.com/core",
                        viewer_path="/docs/core.html#configmap-secret",
                        text="ConfigMap Secret handling in OpenShift",
                        source="vector",
                        raw_score=0.95,
                        fused_score=0.95,
                    )
                ]

        class _OfficialFirstReranker:
            def __init__(self) -> None:
                self.model_name = "official-first-reranker"
                self.top_n = 8

            def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int):
                del query, top_k
                promoted = sorted(
                    hits,
                    key=lambda hit: (
                        0 if str(hit.source_collection or "").strip() != "uploaded" else 1,
                        hit.book_slug,
                    ),
                )
                for index, hit in enumerate(promoted, start=1):
                    hit.component_scores["pre_rerank_fused_score"] = float(hit.fused_score)
                    hit.component_scores["reranker_score"] = float(10 - index)
                    hit.fused_score = float(10 - index)
                    hit.raw_score = float(10 - index)
                return promoted

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root)
            _write_private_runtime_manifest(settings, draft_id="draft-a")
            (settings.customer_pack_books_dir / "draft-a.json").write_text(
                json.dumps(
                    {
                        "canonical_model": "canonical_book_v1",
                        "book_slug": "customer-config-guide",
                        "title": "Customer Config Guide",
                        "source_type": "pdf",
                        "source_uri": "/tmp/customer.pdf",
                        "language_hint": "ko",
                        "source_view_strategy": "normalized_sections_v1",
                        "retrieval_derivation": "chunks_from_canonical_sections",
                        "quality_status": "ready",
                        "sections": [
                            {
                                "ordinal": 1,
                                "section_key": "customer-config-guide:snippet",
                                "heading": "ConfigMap Secret",
                                "section_level": 2,
                                "section_path": ["ConfigMap Secret"],
                                "section_path_label": "ConfigMap Secret",
                                "anchor": "snippet",
                                "viewer_path": "/playbooks/customer-packs/draft-a/index.html#snippet",
                                "source_url": "/tmp/customer.pdf",
                                "text": "ConfigMap Secret values must be synchronized before rollout.",
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
            retriever = ChatRetriever(
                settings,
                BM25Index.from_rows(
                    [
                        {
                            "chunk_id": "core-bm25-configmap-secret",
                            "book_slug": "configuration",
                            "chapter": "config",
                            "section": "ConfigMap Secret reference",
                            "anchor": "cfg",
                            "source_url": "https://example.com/config",
                            "viewer_path": "/docs/config.html#cfg",
                            "text": "ConfigMap Secret reference for OpenShift configuration",
                        }
                    ]
                ),
                vector_retriever=_FakeVectorRetriever(),
                reranker=_OfficialFirstReranker(),
            )

            result = retriever.retrieve(
                "ConfigMap Secret",
                context=SessionContext(
                    selected_draft_ids=["draft-a"],
                    restrict_uploaded_sources=True,
                ),
                use_vector=True,
                top_k=3,
                candidate_k=5,
            )

        self.assertEqual("customer-config-guide", result.hits[0].book_slug)
        self.assertEqual("uploaded", result.hits[0].source_collection)
        self.assertEqual("uploaded", result.trace["hybrid"][0]["source_collection"])
        self.assertEqual("uploaded", result.trace["reranked"][0]["source_collection"])
        self.assertIn("uploaded_customer_pack_priority", result.trace["reranker"]["rebalance_reasons"])

    def test_retriever_uses_private_customer_corpus_bm25_artifact_when_selected_draft_is_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root)
            corpus_dir = settings.customer_pack_corpus_dir / "draft-a"
            _write_private_runtime_manifest(settings, draft_id="draft-a", vector_status="skipped")
            (corpus_dir / "bm25_corpus.jsonl").write_text(
                json.dumps(
                    {
                        "chunk_id": "draft-a:snippet",
                        "book_slug": "customer-config-guide",
                        "chapter": "Customer Config Guide",
                        "section": "ConfigMap Secret",
                        "anchor": "snippet",
                        "source_url": "/tmp/customer.pdf",
                        "viewer_path": "/playbooks/customer-packs/draft-a/index.html#snippet",
                        "text": "ConfigMap Secret values must be synchronized before rollout.",
                        "section_path": ["ConfigMap Secret"],
                        "chunk_type": "reference",
                        "source_id": "customer_pack:draft-a",
                        "source_lane": "customer_source_first_pack",
                        "source_type": "manual_book",
                        "source_collection": "uploaded",
                        "product": "customer_pack",
                        "version": "draft-a",
                        "locale": "ko",
                        "translation_status": "approved_ko",
                        "review_status": "unreviewed",
                        "trust_score": 1.0,
                        "semantic_role": "reference",
                        "cli_commands": [],
                        "error_strings": [],
                        "k8s_objects": [],
                        "operator_names": [],
                        "verification_hints": [],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            retriever = ChatRetriever(settings, BM25Index.from_rows([]), vector_retriever=None)

            result = retriever.retrieve(
                "ConfigMap Secret",
                context=SessionContext(
                    selected_draft_ids=["draft-a"],
                    restrict_uploaded_sources=True,
                ),
                use_vector=False,
                top_k=3,
                candidate_k=5,
            )

        self.assertEqual("customer-config-guide", result.hits[0].book_slug)
        self.assertEqual("uploaded", result.hits[0].source_collection)
        self.assertEqual(1, result.trace["metrics"]["overlay_bm25"]["count"])

    def test_retriever_blocks_private_customer_corpus_bm25_artifact_when_boundary_is_not_runtime_eligible(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root)
            corpus_dir = settings.customer_pack_corpus_dir / "draft-a"
            _write_private_runtime_manifest(
                settings,
                draft_id="draft-a",
                approval_state="unreviewed",
                tenant_id="default-tenant",
                workspace_id="default-workspace",
                vector_status="skipped",
            )
            (corpus_dir / "bm25_corpus.jsonl").write_text(
                json.dumps(
                    {
                        "chunk_id": "draft-a:snippet",
                        "book_slug": "customer-config-guide",
                        "chapter": "Customer Config Guide",
                        "section": "ConfigMap Secret",
                        "anchor": "snippet",
                        "source_url": "/tmp/customer.pdf",
                        "viewer_path": "/playbooks/customer-packs/draft-a/index.html#snippet",
                        "text": "ConfigMap Secret values must be synchronized before rollout.",
                        "section_path": ["ConfigMap Secret"],
                        "chunk_type": "reference",
                        "source_id": "customer_pack:draft-a",
                        "source_lane": "customer_source_first_pack",
                        "source_type": "manual_book",
                        "source_collection": "uploaded",
                        "product": "customer_pack",
                        "version": "draft-a",
                        "locale": "ko",
                        "translation_status": "approved_ko",
                        "review_status": "unreviewed",
                        "trust_score": 1.0,
                        "semantic_role": "reference",
                        "cli_commands": [],
                        "error_strings": [],
                        "k8s_objects": [],
                        "operator_names": [],
                        "verification_hints": [],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            retriever = ChatRetriever(settings, BM25Index.from_rows([]), vector_retriever=None)

            result = retriever.retrieve(
                "ConfigMap Secret",
                context=SessionContext(
                    selected_draft_ids=["draft-a"],
                    restrict_uploaded_sources=True,
                ),
                use_vector=False,
                top_k=3,
                candidate_k=5,
            )

        self.assertEqual([], result.hits)
        self.assertEqual(0, result.trace["metrics"].get("overlay_bm25", {}).get("count", 0))

    def test_retriever_uses_private_customer_corpus_vector_artifact_without_official_qdrant(self) -> None:
        class _FakeVectorRow:
            def __init__(self, values: list[float]) -> None:
                self._values = values

            def tolist(self) -> list[float]:
                return list(self._values)

        class _FakeModel:
            def encode(self, texts, **kwargs):
                del kwargs
                return [_FakeVectorRow([1.0, 0.0, 0.0]) for _ in texts]

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = Settings(root_dir=root)
            corpus_dir = settings.customer_pack_corpus_dir / "draft-a"
            _write_private_runtime_manifest(settings, draft_id="draft-a", vector_status="ready")
            (corpus_dir / "vector_store.jsonl").write_text(
                json.dumps(
                    {
                        "chunk_id": "draft-a:snippet",
                        "book_slug": "customer-config-guide",
                        "chapter": "Customer Config Guide",
                        "section": "ConfigMap Secret",
                        "section_id": "customer-config-guide:snippet",
                        "anchor": "snippet",
                        "source_url": "/tmp/customer.pdf",
                        "viewer_path": "/playbooks/customer-packs/draft-a/index.html#snippet",
                        "text": "ConfigMap Secret values must be synchronized before rollout.",
                        "section_path": ["ConfigMap Secret"],
                        "chunk_type": "reference",
                        "source_id": "customer_pack:draft-a",
                        "source_lane": "customer_source_first_pack",
                        "source_type": "manual_book",
                        "source_collection": "uploaded",
                        "review_status": "unreviewed",
                        "trust_score": 1.0,
                        "semantic_role": "reference",
                        "block_kinds": ["paragraph"],
                        "cli_commands": [],
                        "error_strings": [],
                        "k8s_objects": [],
                        "operator_names": [],
                        "verification_hints": [],
                        "vector": [1.0, 0.0, 0.0],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            retriever = ChatRetriever(settings, BM25Index.from_rows([]), vector_retriever=None)

            with patch("play_book_studio.retrieval.intake_overlay.load_sentence_model", return_value=_FakeModel()):
                result = retriever.retrieve(
                    "ConfigMap Secret",
                    context=SessionContext(
                        selected_draft_ids=["draft-a"],
                        restrict_uploaded_sources=True,
                    ),
                    use_bm25=False,
                    use_vector=True,
                    top_k=3,
                    candidate_k=5,
                )

        self.assertEqual("customer-config-guide", result.hits[0].book_slug)
        self.assertEqual("uploaded", result.hits[0].source_collection)
        self.assertEqual("ready", result.trace["vector_runtime"]["subqueries"][0]["private_vector_status"])

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
            viewer_path="/playbooks/customer-packs/dtb-demo/index.html#unique-switch",
            text="orion.unique/flag=starfall-88 값을 migration 전에 설정합니다.",
            source="overlay_bm25",
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
            {"overlay_bm25": [intake_hit], "bm25": [generic_intro_hit]},
            top_k=2,
            weights={"bm25": 1.0, "overlay_bm25": 1.35, "vector": 1.0},
        )

        self.assertEqual("orion-pdf-guide", fused[0].book_slug)
        self.assertEqual("/playbooks/customer-packs/dtb-demo/index.html#unique-switch", fused[0].viewer_path)

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

    def test_build_retrieval_plan_expands_resolved_follow_up_into_secondary_queries(self) -> None:
        context = SessionContext(
            current_topic="etcd 백업",
            open_entities=["etcd"],
            ocp_version="4.20",
            unresolved_question="etcd 백업 이후 복구 절차",
        )

        plan = build_retrieval_plan("그 복구는 어떻게 해?", context=context, candidate_k=20)

        self.assertGreaterEqual(len(plan.rewritten_queries), 2)
        self.assertTrue(any("cluster-restore.sh" in item for item in plan.rewritten_queries))
        self.assertTrue(any("복원" == item for item in plan.rewritten_queries))

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

    def test_rewrite_query_skips_generic_openshift_usage_prompt_even_with_context(self) -> None:
        context = SessionContext(
            current_topic="OpenShift",
            open_entities=["OpenShift"],
            user_goal="노드 삭제 전에 확인할 항목",
            unresolved_question="노드 drain 이후 복구 절차",
            ocp_version="4.20",
        )

        rewritten = rewrite_query("오픈시프트는 어떤 곳에 쓰여?", context)

        self.assertEqual("오픈시프트는 어떤 곳에 쓰여?", rewritten)

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
        self.assertIn("oc", normalized)
        self.assertNotIn("events", normalized)
        self.assertNotIn("troubleshooting", normalized)

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
        self.assertIn("용어집", normalized)
        self.assertNotIn("status", normalized)

    def test_normalize_query_expands_route_ingress_compare_terms(self) -> None:
        normalized = normalize_query("OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘")

        self.assertIn("networking", normalized)
        self.assertNotIn("router", normalized)
        self.assertNotIn("ingresscontroller", normalized)
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
