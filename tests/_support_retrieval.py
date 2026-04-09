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

from play_book_studio.config.settings import Settings
from play_book_studio.retrieval.bm25 import BM25Index
from play_book_studio.retrieval.models import RetrievalHit, SessionContext
from play_book_studio.retrieval.intake_overlay import (
    filter_doc_to_book_hits_by_selection as _filter_doc_to_book_hits_by_selection,
)
from play_book_studio.retrieval.query import (
    decompose_retrieval_queries,
    detect_out_of_corpus_version,
    detect_unsupported_product,
    has_corrective_follow_up,
    has_cluster_node_usage_intent,
    has_command_request,
    has_deployment_scaling_intent,
    has_follow_up_reference,
    has_follow_up_entity_ambiguity,
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
)
from play_book_studio.retrieval.retriever import (
    ChatRetriever,
    fuse_ranked_hits,
)
__all__ = [
    "Settings",
    "BM25Index",
    "RetrievalHit",
    "SessionContext",
    "_filter_doc_to_book_hits_by_selection",
    "decompose_retrieval_queries",
    "detect_out_of_corpus_version",
    "detect_unsupported_product",
    "has_corrective_follow_up",
    "has_cluster_node_usage_intent",
    "has_command_request",
    "has_deployment_scaling_intent",
    "has_follow_up_reference",
    "has_follow_up_entity_ambiguity",
    "has_logging_ambiguity",
    "has_machine_config_reboot_intent",
    "has_node_drain_intent",
    "has_multiple_entity_ambiguity",
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
]
