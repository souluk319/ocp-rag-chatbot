from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.shared.settings import Settings
from ocp_rag.retrieval.models import RetrievalHit, RetrievalResult, SessionContext
from ocp_rag.retrieval.query import normalize_query
from ocp_rag.retrieval.retriever import Part2Retriever
from ocp_rag.answering.context import _should_force_clarification, assemble_context
from ocp_rag.answering.answerer import Part3Answerer


def _hit(
    chunk_id: str,
    book_slug: str,
    section: str,
    text: str,
    *,
    score: float,
) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id,
        book_slug=book_slug,
        chapter=book_slug,
        section=section,
        anchor=section.lower().replace(" ", "-"),
        source_url=f"https://example.com/{book_slug}",
        viewer_path=f"/docs/{book_slug}.html#{section.lower().replace(' ', '-')}",
        text=text,
        source="hybrid",
        raw_score=score,
        fused_score=score,
    )


class _WarningRetriever:
    def retrieve(self, query, context, top_k, candidate_k, trace_callback=None):  # noqa: ANN001
        hit = RetrievalHit(
            chunk_id="chunk-1",
            book_slug="cli_tools",
            chapter="cli",
            section="2.6.1.90. oc login",
            anchor="oc-login",
            source_url="https://example.com/cli",
            viewer_path="/docs/cli.html#oc-login",
            text="Use oc login to authenticate to the cluster.",
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
            trace={
                "warnings": ["vector search failed: embedding endpoint down"],
                "timings_ms": {"bm25_search": 1.1},
            },
        )


class _FakeLLMClient:
    def generate(self, messages, trace_callback=None):  # noqa: ANN001
        return "답변: oc login 으로 클러스터에 로그인합니다. [1]"


class Bm25FallbackGroundingTests(unittest.TestCase):
    def test_normalize_query_expands_operational_queries(self) -> None:
        cases = {
            "oc login usage": ("cli", "kubeconfig", "kubeadmin"),
            "Pod Pending meaning": ("scheduling", "events", "namespace"),
            "CrashLoopBackOff troubleshooting": ("logs", "describe", "troubleshooting"),
            "Pod lifecycle concept": ("nodes", "workloads", "restartPolicy"),
        }

        for query, expected_terms in cases.items():
            normalized = normalize_query(query)
            for term in expected_terms:
                self.assertIn(term, normalized)

    def test_retrieve_falls_back_to_bm25_when_vector_search_raises(self) -> None:
        class StubBm25:
            def search(self, query: str, top_k: int):
                return [
                    RetrievalHit(
                        chunk_id="cli-login",
                        book_slug="cli_tools",
                        chapter="cli",
                        section="2.6.1.90. oc login",
                        anchor="oc-login",
                        source_url="https://example.com/cli",
                        viewer_path="/docs/cli.html#oc-login",
                        text="Use oc login to authenticate to the cluster.",
                        source="bm25",
                        raw_score=1.2,
                        fused_score=1.2,
                    )
                ]

        class ExplodingVector:
            def search(self, query: str, top_k: int):
                raise ValueError("embedding endpoint down")

        retriever = Part2Retriever(
            Settings(root_dir=ROOT),
            StubBm25(),
            vector_retriever=ExplodingVector(),
        )

        result = retriever.retrieve("oc login usage")

        self.assertEqual("cli_tools", result.hits[0].book_slug)
        self.assertEqual([], result.trace["vector"])
        self.assertTrue(any("vector search failed" in warning for warning in result.trace["warnings"]))

    def test_context_keeps_low_score_bm25_hits_when_coherent(self) -> None:
        hits = [
            _hit("chunk-1", "cli_tools", "2.6.1.90. oc login", "Use oc login with the API server.", score=0.0164),
            _hit(
                "chunk-2",
                "cli_tools",
                "2.1.4. Login to the OpenShift CLI by using a web browser",
                "The web browser flow helps you log in to the CLI.",
                score=0.0161,
            ),
            _hit(
                "chunk-3",
                "cli_tools",
                "2.2.2. Accessing kubeconfig by using the oc CLI",
                "The oc CLI can update kubeconfig after login.",
                score=0.0157,
            ),
            _hit(
                "chunk-4",
                "release_notes",
                "1.6.22. OpenShift CLI (oc)",
                "Release notes for the oc CLI.",
                score=0.0154,
            ),
        ]

        self.assertFalse(_should_force_clarification(hits, query="oc login usage"))
        bundle = assemble_context(hits, query="oc login usage", max_chunks=4)

        self.assertNotEqual([], bundle.citations)
        self.assertEqual("cli_tools", bundle.citations[0].book_slug)

    def test_answerer_preserves_vector_warning_when_bm25_fallback_succeeds(self) -> None:
        answerer = Part3Answerer(
            settings=Settings(root_dir=ROOT),
            retriever=_WarningRetriever(),
            llm_client=_FakeLLMClient(),
        )

        result = answerer.answer("oc login usage", mode="ops")

        self.assertNotEqual([], result.citations)
        self.assertTrue(any("vector search failed" in warning for warning in result.warnings))
        self.assertTrue(any("vector search failed" in warning for warning in result.retrieval_trace["warnings"]))


if __name__ == "__main__":
    unittest.main()
