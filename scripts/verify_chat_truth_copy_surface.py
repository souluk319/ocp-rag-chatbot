from __future__ import annotations

import json
import uuid
from pathlib import Path

from play_book_studio.answering.models import Citation
from play_book_studio.app.presenters import _serialize_citation
from play_book_studio.app.sessions import ChatSession, SessionStore, Turn, serialize_session_snapshot


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    store = SessionStore(root)
    session_id = f"truth-copy-{uuid.uuid4().hex}"
    session = ChatSession(session_id=session_id)
    session.history.append(
        Turn(
            turn_id=uuid.uuid4().hex,
            created_at="2026-04-14T23:59:59+09:00",
            query="customer pack truth 를 보여줘",
            mode="chat",
            answer="synthetic answer",
            primary_source_lane="customer_source_first_pack",
            primary_boundary_truth="private_customer_pack_runtime",
            primary_runtime_truth_label="Customer Source-First Pack",
            primary_boundary_badge="Private Pack Runtime",
            primary_publication_state="draft",
            primary_approval_state="unreviewed",
        )
    )
    session.revision = 1
    session.updated_at = "2026-04-14T23:59:59+09:00"
    store.update(session)

    try:
        summaries = store.list_summaries(limit=10)
        summary = next((item for item in summaries if item.get("session_id") == session_id), {})
        snapshot = serialize_session_snapshot(store.peek(session_id) or session)
        turn_payload = ((snapshot.get("turns") or [{}])[0]) if isinstance(snapshot.get("turns"), list) else {}
        official = _serialize_citation(
            root,
            Citation(
                index=1,
                chunk_id="synthetic",
                book_slug="backup_and_restore",
                section="Overview",
                anchor="",
                source_url="https://docs.redhat.com/",
                viewer_path="/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                excerpt="synthetic",
            ),
        )
        workspace_page = (root / "presentation-ui" / "src" / "pages" / "WorkspacePage.tsx").read_text(encoding="utf-8")
        report = {
            "status": "ok",
            "summary_found": bool(summary),
            "summary_boundary_truth": str(summary.get("primary_boundary_truth") or ""),
            "summary_boundary_badge": str(summary.get("primary_boundary_badge") or ""),
            "snapshot_turn_boundary_badge": str(turn_payload.get("primary_boundary_badge") or ""),
            "official_boundary_truth": str(official.get("boundary_truth") or ""),
            "official_boundary_badge": str(official.get("boundary_badge") or ""),
            "official_runtime_truth_label": str(official.get("runtime_truth_label") or ""),
            "frontend_uses_truth_surface_copy": "truthSurfaceCopy(" in workspace_page,
            "frontend_mentions_private_runtime": "Private Runtime" in workspace_page,
            "frontend_mentions_validated_runtime": "Validated Runtime" in workspace_page,
        }
        if not (
            report["summary_found"]
            and report["summary_boundary_truth"] == "private_customer_pack_runtime"
            and report["summary_boundary_badge"] == "Private Pack Runtime"
            and report["snapshot_turn_boundary_badge"] == "Private Pack Runtime"
            and report["official_boundary_truth"] == "official_validated_runtime"
            and report["official_boundary_badge"] == "Validated Runtime"
            and report["frontend_uses_truth_surface_copy"]
            and report["frontend_mentions_private_runtime"]
            and report["frontend_mentions_validated_runtime"]
        ):
            report["status"] = "failed"
            raise SystemExit(json.dumps(report, ensure_ascii=False))
    finally:
        store.delete(session_id)

    report_path = root / "reports" / "build_logs" / "chat_truth_copy_surface_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
