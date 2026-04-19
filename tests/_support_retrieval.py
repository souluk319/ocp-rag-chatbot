from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import Settings
from play_book_studio.retrieval.bm25 import BM25Index
from play_book_studio.retrieval.models import RetrievalHit, SessionContext
from play_book_studio.retrieval.intake_overlay import (
    filter_customer_pack_hits_by_selection as _filter_customer_pack_hits_by_selection,
)
from play_book_studio.retrieval.query import (
    decompose_retrieval_queries,
    detect_out_of_corpus_version,
    detect_unsupported_product,
    has_corrective_follow_up,
    has_cluster_node_usage_intent,
    has_command_request,
    has_deployment_scaling_intent,
    has_doc_locator_intent,
    has_follow_up_reference,
    has_follow_up_entity_ambiguity,
    has_logging_ambiguity,
    has_machine_config_reboot_intent,
    has_node_drain_intent,
    has_multiple_entity_ambiguity,
    has_postinstall_doc_locator_ambiguity,
    has_project_scoped_rbac_intent,
    has_rbac_assignment_intent,
    has_rbac_intent,
    has_route_ingress_compare_intent,
    has_security_doc_locator_ambiguity,
    has_update_doc_locator_ambiguity,
    normalize_query,
    query_book_adjustments,
    rewrite_query,
)
from play_book_studio.retrieval.retriever import (
    ChatRetriever,
    fuse_ranked_hits,
)
from play_book_studio.retrieval.retriever_plan import build_retrieval_plan


class SeededBm25:
    def __init__(self, hits: list[RetrievalHit] | None = None, *, record_calls: bool = False) -> None:
        self.hits = list(hits or [])
        self.record_calls = record_calls
        self.calls: list[tuple[str, int]] = []

    def search(self, query: str, top_k: int) -> list[RetrievalHit]:
        if self.record_calls:
            self.calls.append((query, top_k))
        return list(self.hits[:top_k])


class SeededReranker:
    def __init__(self, hits: list[RetrievalHit], *, model_name: str = "fake-reranker", top_n: int = 8) -> None:
        self.hits = hits
        self.model_name = model_name
        self.top_n = top_n

    def rerank(self, query: str, hits: list[RetrievalHit], *, top_k: int) -> list[RetrievalHit]:
        del query, hits, top_k
        return list(self.hits)


class FakeRetrieverWithReranker:
    def __init__(self, hits: list[RetrievalHit], *, root_dir: Path = ROOT) -> None:
        self.reranker = SeededReranker(hits)
        self.settings = SimpleNamespace(root_dir=root_dir)


class _FakeReranker(SeededReranker):
    pass


class _FakeRetrieverWithReranker(FakeRetrieverWithReranker):
    pass


__all__ = [
    "Settings",
    "BM25Index",
    "RetrievalHit",
    "SessionContext",
    "SeededBm25",
    "_filter_customer_pack_hits_by_selection",
    "decompose_retrieval_queries",
    "detect_out_of_corpus_version",
    "detect_unsupported_product",
    "has_corrective_follow_up",
    "has_cluster_node_usage_intent",
    "has_command_request",
    "has_deployment_scaling_intent",
    "has_doc_locator_intent",
    "has_follow_up_reference",
    "has_follow_up_entity_ambiguity",
    "has_logging_ambiguity",
    "has_machine_config_reboot_intent",
    "has_node_drain_intent",
    "has_multiple_entity_ambiguity",
    "has_postinstall_doc_locator_ambiguity",
    "has_project_scoped_rbac_intent",
    "has_rbac_assignment_intent",
    "has_rbac_intent",
    "has_route_ingress_compare_intent",
    "has_security_doc_locator_ambiguity",
    "has_update_doc_locator_ambiguity",
    "normalize_query",
    "query_book_adjustments",
    "rewrite_query",
    "ChatRetriever",
    "fuse_ranked_hits",
    "build_retrieval_plan",
    "SeededReranker",
    "FakeRetrieverWithReranker",
    "_FakeReranker",
    "_FakeRetrieverWithReranker",
]
