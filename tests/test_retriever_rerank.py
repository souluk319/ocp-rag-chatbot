from __future__ import annotations

import unittest

from play_book_studio.retrieval.models import RetrievalHit
from play_book_studio.retrieval.retriever_rerank import _rebalance_mco_concept_hits


def _hit(
    chunk_id: str,
    book_slug: str,
    section: str,
    text: str,
    *,
    score: float,
    anchor: str = "",
) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id,
        book_slug=book_slug,
        chapter=book_slug,
        section=section,
        anchor=anchor,
        source_url=f"https://example.com/{book_slug}",
        viewer_path=f"/docs/{book_slug}.html#{anchor or chunk_id}",
        text=text,
        source="hybrid",
        raw_score=score,
        fused_score=score,
        component_scores={
            "pre_rerank_fused_score": score,
            "reranker_score": score,
        },
    )


class TestRetrieverRerank(unittest.TestCase):
    def test_rebalance_mco_concept_prefers_machine_configuration_over_architecture(self) -> None:
        hybrid_hits = [
            _hit(
                "arch-mco",
                "architecture",
                "핵심 구성 요소",
                "Machine Config Operator와 MCP 역할을 설명합니다.",
                score=0.98,
            ),
            _hit(
                "mco-core",
                "machine_configuration",
                "About the Machine Config Operator",
                "Machine Config Operator의 역할과 업데이트 흐름을 설명합니다.",
                score=0.97,
                anchor="about-mco",
            ),
            _hit(
                "release-note",
                "release_notes",
                "릴리스 노트",
                "MCO 관련 변경을 요약합니다.",
                score=0.96,
            ),
        ]

        reranked_hits = [hybrid_hits[0], hybrid_hits[2], hybrid_hits[1]]

        reordered = _rebalance_mco_concept_hits(
            "Machine Config Operator 핵심만 짧게 정리해줘",
            hybrid_hits=hybrid_hits,
            reranked_hits=reranked_hits,
        )

        self.assertEqual("machine_configuration", reordered[0].book_slug)

    def test_rebalance_mco_follow_up_prefers_machine_configuration_over_release_notes(self) -> None:
        hybrid_hits = [
            _hit(
                "release-note",
                "release_notes",
                "릴리스 노트",
                "MCO 관련 변경을 요약합니다.",
                score=1.0,
            ),
            _hit(
                "postinstall-mco",
                "postinstallation_configuration",
                "Troubleshooting MCO",
                "Machine Config Operator 문제 해결을 설명합니다.",
                score=0.99,
                anchor="troubleshooting-mco",
            ),
            _hit(
                "mco-core",
                "machine_configuration",
                "About the Machine Config Operator",
                "Machine Config Operator의 역할과 설정 지점을 설명합니다.",
                score=0.98,
                anchor="about-mco",
            ),
            _hit(
                "operators-core",
                "operators",
                "Operator 개요",
                "Operator와 MCO의 관계를 설명합니다.",
                score=0.97,
            ),
        ]

        reranked_hits = [hybrid_hits[0], hybrid_hits[1], hybrid_hits[2], hybrid_hits[3]]

        reordered = _rebalance_mco_concept_hits(
            "그 설정은 어디서 바꿔?",
            hybrid_hits=hybrid_hits,
            reranked_hits=reranked_hits,
        )

        self.assertEqual("machine_configuration", reordered[0].book_slug)
        self.assertEqual("operators", reordered[1].book_slug)


if __name__ == "__main__":
    unittest.main()
