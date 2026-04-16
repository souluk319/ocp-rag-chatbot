from __future__ import annotations

import json
import uuid
from pathlib import Path

from play_book_studio.app.sessions import ChatSession, SessionStore, Turn, serialize_session_snapshot
from play_book_studio.execution_guard import run_guarded_script


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    store = SessionStore(root)
    session_id = f"verify-{uuid.uuid4().hex}"
    session = ChatSession(session_id=session_id)
    session.history.append(
        Turn(
            turn_id=uuid.uuid4().hex,
            created_at="2026-04-14T23:59:59+09:00",
            query="customer pack runtime truth 를 보여줘",
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

        workspace_page = (root / "presentation-ui" / "src" / "pages" / "WorkspacePage.tsx").read_text(encoding="utf-8")
        report = {
            "status": "ok",
            "summary_found": bool(summary),
            "summary_boundary_badge": str(summary.get("primary_boundary_badge") or ""),
            "summary_runtime_truth_label": str(summary.get("primary_runtime_truth_label") or ""),
            "summary_source_lane": str(summary.get("primary_source_lane") or ""),
            "snapshot_turn_boundary_badge": str(turn_payload.get("primary_boundary_badge") or ""),
            "snapshot_turn_runtime_truth_label": str(turn_payload.get("primary_runtime_truth_label") or ""),
            "snapshot_turn_source_lane": str(turn_payload.get("primary_source_lane") or ""),
            "frontend_has_assistant_truth_row": "assistant-truth-row" in workspace_page,
            "frontend_has_session_truth_row": "session-truth-row" in workspace_page,
        }
        if not (
            report["summary_found"]
            and report["summary_boundary_badge"] == "Private Pack Runtime"
            and report["summary_runtime_truth_label"] == "Customer Source-First Pack"
            and report["snapshot_turn_boundary_badge"] == "Private Pack Runtime"
            and report["snapshot_turn_runtime_truth_label"] == "Customer Source-First Pack"
            and report["frontend_has_assistant_truth_row"]
            and report["frontend_has_session_truth_row"]
        ):
            report["status"] = "failed"
            raise SystemExit(json.dumps(report, ensure_ascii=False))
    finally:
        store.delete(session_id)

    report_path = root / "reports" / "build_logs" / "customer_pack_chat_history_surface_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
