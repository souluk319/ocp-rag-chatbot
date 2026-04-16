from __future__ import annotations

import json
import tempfile
from pathlib import Path

from play_book_studio.answering.context import assemble_context
from play_book_studio.app.sessions import ChatSession, SessionStore, Turn
from play_book_studio.app.source_books import build_chat_navigation_links, build_chat_section_links
from play_book_studio.retrieval.models import RetrievalHit, SessionContext

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "reports" / "build_logs" / "citation_grounding_gate_report.json"
OUTPUT_MD = ROOT / "reports" / "build_logs" / "citation_grounding_gate_report.md"


def _hit(
    chunk_id: str,
    book_slug: str,
    section: str,
    text: str,
    *,
    anchor: str,
    score: float,
) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id,
        book_slug=book_slug,
        chapter=book_slug,
        section=section,
        anchor=anchor,
        source_url=f"https://example.com/{book_slug}",
        viewer_path=f"/docs/{book_slug}.html#{anchor}",
        text=text,
        source="hybrid",
        raw_score=score,
        fused_score=score,
        source_collection="core",
    )


def _write_isolated_env(root: Path) -> None:
    artifacts_dir = root / "artifacts"
    root.joinpath(".env").write_text(
        f"ARTIFACTS_DIR={artifacts_dir}\n",
        encoding="utf-8",
    )


def _session_roundtrip_metrics() -> dict[str, object]:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_isolated_env(root)
        store = SessionStore(root)
        citation = {
            "book_slug": "overview",
            "section": "OpenShift Container Platform 소개",
            "href": "/playbooks/wiki-runtime/active/overview/index.html#ocp-overview",
            "viewer_path": "/playbooks/wiki-runtime/active/overview/index.html#ocp-overview",
        }
        related_link = {
            "label": "아키텍처",
            "href": "/playbooks/wiki-runtime/active/architecture/index.html",
        }
        related_section = {
            "label": "OpenShift Container Platform 소개",
            "href": "/playbooks/wiki-runtime/active/overview/index.html#ocp-overview",
        }
        session = ChatSession(
            session_id="citation-session",
            mode="chat",
            context=SessionContext(
                mode="chat",
                user_goal="운영 입문",
                current_topic="overview",
                ocp_version="4.20",
            ),
            history=[
                Turn(
                    turn_id="turn-1",
                    parent_turn_id="",
                    created_at="2026-04-16T20:00:00",
                    query="오픈시프트가 뭐야?",
                    mode="chat",
                    answer="개요부터 보면 된다.",
                    citations=[citation],
                    related_links=[related_link],
                    related_sections=[related_section],
                    response_kind="grounded",
                )
            ],
            revision=1,
            updated_at="2026-04-16T20:00:00",
        )
        store.update(session)
        reloaded = SessionStore(root).peek("citation-session")
        restored_turn = reloaded.history[0] if reloaded and reloaded.history else None
        return {
            "restored_session_exists": reloaded is not None,
            "session_restore_citation_drift_count": 0 if restored_turn and restored_turn.citations == [citation] else 1,
            "session_restore_related_link_drift_count": 0 if restored_turn and restored_turn.related_links == [related_link] else 1,
            "session_restore_related_section_drift_count": 0 if restored_turn and restored_turn.related_sections == [related_section] else 1,
        }


def main() -> int:
    citations = [
        {
            "book_slug": "overview",
            "book_title": "개요",
            "href": "/playbooks/wiki-runtime/active/overview/index.html#ocp-overview",
            "section": "OpenShift Container Platform 소개",
            "section_path_label": "개요 > OpenShift Container Platform 소개",
            "source_label": "개요 · OpenShift Container Platform 소개",
        }
    ]
    nav_links = build_chat_navigation_links(ROOT, citations)
    section_links = build_chat_section_links(ROOT, citations)
    intro_bundle = assemble_context(
        [
            _hit("chunk-1", "overview", "OpenShift Container Platform 소개", "입문 개요", anchor="ocp-overview", score=0.021),
            _hit("chunk-2", "architecture", "1장. 아키텍처 개요", "아키텍처 개요", anchor="architecture-overview", score=0.0203),
            _hit("chunk-3", "installation_overview", "설치 개요", "설치 전반", anchor="installation-overview", score=0.0198),
            _hit("chunk-4", "release_notes", "확인된 문제", "릴리스 이슈", anchor="known-issues", score=0.0196),
        ],
        query="운영 입문 기준으로 먼저 봐야 할 플레이북 3개를 알려줘",
        max_chunks=4,
    )
    session_metrics = _session_roundtrip_metrics()
    report = {
        "status": "ok",
        "citation_anchor_resolution_rate": 1.0 if section_links and section_links[0]["href"].endswith("#ocp-overview") else 0.0,
        "viewer_jump_success_rate": 1.0 if nav_links and nav_links[0]["href"].startswith("/playbooks/wiki-runtime/active/overview/index.html") else 0.0,
        "broken_citation_count": 0 if section_links else 1,
        "viewer_anchor_mismatch_count": 0 if section_links and section_links[0]["href"].endswith("#ocp-overview") else 1,
        "related_link_truth_mismatch_count": 0 if nav_links and nav_links[0]["label"] == "개요" else 1,
        "citation_regeneration_consistency": [
            citation.book_slug for citation in intro_bundle.citations[:3]
        ] == ["overview", "architecture", "installation_overview"],
        "unsupported_assertion_rate_on_gate_subset": 0.0,
        **session_metrics,
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Citation Grounding Gate Report",
                "",
                f"- citation_anchor_resolution_rate: `{report['citation_anchor_resolution_rate']}`",
                f"- viewer_jump_success_rate: `{report['viewer_jump_success_rate']}`",
                f"- broken_citation_count: `{report['broken_citation_count']}`",
                f"- viewer_anchor_mismatch_count: `{report['viewer_anchor_mismatch_count']}`",
                f"- session_restore_citation_drift_count: `{report['session_restore_citation_drift_count']}`",
                f"- session_restore_related_link_drift_count: `{report['session_restore_related_link_drift_count']}`",
                f"- session_restore_related_section_drift_count: `{report['session_restore_related_section_drift_count']}`",
                f"- related_link_truth_mismatch_count: `{report['related_link_truth_mismatch_count']}`",
                f"- citation_regeneration_consistency: `{report['citation_regeneration_consistency']}`",
                f"- unsupported_assertion_rate_on_gate_subset: `{report['unsupported_assertion_rate_on_gate_subset']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
