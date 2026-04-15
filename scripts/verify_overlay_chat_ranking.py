from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from play_book_studio.answering.context import assemble_context
from play_book_studio.app.source_books import build_chat_navigation_links, build_chat_section_links
from play_book_studio.app.wiki_user_overlay import (
    list_wiki_user_overlays,
    remove_wiki_user_overlay,
    save_wiki_user_overlay,
)
from play_book_studio.retrieval.models import RetrievalHit, SessionContext
from play_book_studio.retrieval.retriever_rerank import _rebalance_overlay_preference_hits


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "build_logs" / "overlay_chat_ranking_report.json"
SMOKE_USER = "smoke-overlay-chat-ranking"
SMOKE_QUERY = "설치 프록시 준비 절차 알려줘"


def _cleanup_user_overlays() -> None:
    payload = list_wiki_user_overlays(ROOT, user_id=SMOKE_USER)
    for item in payload.get("items", []):
        overlay_id = str(item.get("overlay_id") or "").strip()
        if not overlay_id:
            continue
        remove_wiki_user_overlay(
            ROOT,
            {
                "user_id": SMOKE_USER,
                "overlay_id": overlay_id,
            },
        )


def _synthetic_hit(
    *,
    chunk_id: str,
    book_slug: str,
    section: str,
    anchor: str,
    text: str,
    fused_score: float,
) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id,
        book_slug=book_slug,
        chapter="",
        section=section,
        anchor=anchor,
        source_url=f"https://example.invalid/{book_slug}",
        viewer_path=f"/playbooks/wiki-runtime/active/{book_slug}/index.html#{anchor}",
        text=text,
        source="hybrid_reranked",
        raw_score=fused_score,
        fused_score=fused_score,
        section_path=(book_slug.replace("_", " ").title(), section),
        section_id=anchor,
        chunk_type="procedure",
        semantic_role="procedure",
    )


def _seed_overlay_preferences() -> None:
    save_wiki_user_overlay(
        ROOT,
        {
            "user_id": SMOKE_USER,
            "kind": "favorite",
            "target_kind": "book",
            "book_slug": "installing_on_any_platform",
            "viewer_path": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html",
            "title": "Installing on Any Platform",
            "summary": "설치 선호 북",
        },
    )
    save_wiki_user_overlay(
        ROOT,
        {
            "user_id": SMOKE_USER,
            "kind": "recent_position",
            "target_kind": "section",
            "book_slug": "installing_on_any_platform",
            "anchor": "preparing-the-cluster-for-a-proxy-environment",
            "viewer_path": "/playbooks/wiki-runtime/active/installing_on_any_platform/index.html#preparing-the-cluster-for-a-proxy-environment",
        },
    )
    save_wiki_user_overlay(
        ROOT,
        {
            "user_id": SMOKE_USER,
            "kind": "favorite",
            "target_kind": "entity_hub",
            "entity_slug": "cluster-wide-proxy",
            "viewer_path": "/wiki/entities/cluster-wide-proxy/index.html",
            "title": "Cluster-Wide Proxy",
            "summary": "프록시 허브 선호",
        },
    )


def _http_post_json(url: str, payload: dict[str, object]) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _cleanup_user_overlays()
    try:
        hits = [
            _synthetic_hit(
                chunk_id="hit-install",
                book_slug="installing_on_any_platform",
                section="Preparing the Cluster for a Proxy Environment",
                anchor="preparing-the-cluster-for-a-proxy-environment",
                text="Cluster-wide proxy configuration and install preparation steps.",
                fused_score=0.41,
            ),
            _synthetic_hit(
                chunk_id="hit-backup",
                book_slug="backup_and_restore",
                section="Check Whether Cluster-Wide Proxy Is Enabled",
                anchor="check-whether-cluster-wide-proxy-is-enabled",
                text="Check whether the cluster wide proxy is enabled before backup and restore.",
                fused_score=0.43,
            ),
        ]

        baseline_context = assemble_context(
            hits,
            query=SMOKE_QUERY,
            max_chunks=2,
        )

        _seed_overlay_preferences()

        rebalanced_hits = _rebalance_overlay_preference_hits(
            SMOKE_QUERY,
            hybrid_hits=hits,
            reranked_hits=hits,
            context=SessionContext(user_id=SMOKE_USER),
            root_dir=ROOT,
        )

        personalized_context = assemble_context(
            hits,
            query=SMOKE_QUERY,
            session_context=SessionContext(user_id=SMOKE_USER),
            root_dir=ROOT,
            max_chunks=2,
        )

        serialized_citations = [
            {
                "book_slug": hit.book_slug,
                "section": hit.section,
                "href": hit.viewer_path,
                "excerpt": hit.text,
                "source_label": " > ".join(hit.section_path) if hit.section_path else hit.section,
            }
            for hit in rebalanced_hits
        ]

        related_links = build_chat_navigation_links(
            ROOT,
            serialized_citations,
            user_id=SMOKE_USER,
        )
        related_sections = build_chat_section_links(
            ROOT,
            serialized_citations,
            user_id=SMOKE_USER,
        )

        live_chat = _http_post_json(
            "http://127.0.0.1:8765/api/chat",
            {
                "query": SMOKE_QUERY,
                "session_id": "smoke-overlay-chat-ranking",
                "mode": "ops",
                "user_id": SMOKE_USER,
                "selected_draft_ids": [],
                "restrict_uploaded_sources": False,
            },
        )

        report = {
            "status": "ok",
            "baseline_first_book": baseline_context.citations[0].book_slug if baseline_context.citations else "",
            "rebalanced_first_book": rebalanced_hits[0].book_slug if rebalanced_hits else "",
            "personalized_first_book": personalized_context.citations[0].book_slug if personalized_context.citations else "",
            "related_links_count": len(related_links),
            "related_sections_count": len(related_sections),
            "first_related_link": related_links[0] if related_links else {},
            "first_related_section": related_sections[0] if related_sections else {},
            "live_chat_first_book": (
                ((live_chat.get("citations") or [{}])[0] or {}).get("book_slug", "")
                if isinstance(live_chat, dict)
                else ""
            ),
            "live_chat_first_related": (
                ((live_chat.get("related_links") or [{}])[0] or {})
                if isinstance(live_chat, dict)
                else {}
            ),
            "live_chat_first_section": (
                ((live_chat.get("related_sections") or [{}])[0] or {})
                if isinstance(live_chat, dict)
                else {}
            ),
            "overlay_count_after_seed": list_wiki_user_overlays(ROOT, user_id=SMOKE_USER).get("count", 0),
        }
    finally:
        _cleanup_user_overlays()

    report["cleanup_after"] = list_wiki_user_overlays(ROOT, user_id=SMOKE_USER).get("count", 0)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
