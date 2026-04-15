from __future__ import annotations

import json
import tempfile
import urllib.request
from pathlib import Path

from play_book_studio.app.intake_api import create_customer_pack_draft, delete_customer_pack_draft
from play_book_studio.app.sessions import SessionStore, serialize_session_snapshot
from play_book_studio.intake.capture.service import CustomerPackCaptureService
from play_book_studio.intake.normalization.service import CustomerPackNormalizeService


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = REPO_ROOT / "reports" / "build_logs" / "mixed_runtime_end_to_end_report.json"
REPORT_MD = REPO_ROOT / "reports" / "build_logs" / "mixed_runtime_end_to_end_report.md"
CHAT_URL = "http://127.0.0.1:8765/api/chat"


def _post_json(url: str, payload: dict[str, object]) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    session_id = "w4-e1-t9-live-mixed-runtime"
    store = SessionStore(REPO_ROOT)
    store.delete(session_id)

    temp_path = Path(tempfile.gettempdir()) / "w4_e1_t9_customer_pack.md"
    temp_path.write_text(
        "# Customer Pack Mixed Runtime Smoke\n\n"
        "## etcd 백업 운영 메모\n\n"
        "customer pack 기준 운영 메모다. 공식 runtime 절차와 같이 확인해야 한다.\n\n"
        "```bash\n"
        "oc debug --as-root node/<node_name>\n"
        "chroot /host\n"
        "/usr/local/bin/cluster-backup.sh /home/core/assets/backup\n"
        "```\n",
        encoding="utf-8",
    )

    draft = create_customer_pack_draft(
        REPO_ROOT,
        {
            "source_type": "md",
            "uri": str(temp_path),
            "title": "Customer Pack Mixed Runtime Smoke",
            "language_hint": "ko",
        },
    )
    draft_id = str(draft["draft_id"])

    try:
        CustomerPackCaptureService(REPO_ROOT).capture(draft_id=draft_id)
        normalized = CustomerPackNormalizeService(REPO_ROOT).normalize(draft_id=draft_id).to_dict()

        response = _post_json(
            CHAT_URL,
            {
                "query": "customer pack 과 공식 runtime 을 같이 써서 etcd backup 절차를 비교해서 알려줘",
                "session_id": session_id,
                "mode": "ops",
                "user_id": "w4-e1-t9",
                "selected_draft_ids": [draft_id],
                "restrict_uploaded_sources": True,
            },
        )

        citations = [item for item in (response.get("citations") or []) if isinstance(item, dict)]
        citation_truths = [str(item.get("boundary_truth") or "").strip() for item in citations if str(item.get("boundary_truth") or "").strip()]
        citation_books = [str(item.get("book_slug") or "").strip() for item in citations if str(item.get("book_slug") or "").strip()]
        summary = next(
            (item for item in store.list_summaries(limit=50) if str(item.get("session_id") or "") == session_id),
            {},
        )
        snapshot = serialize_session_snapshot(store.peek(session_id) or store.get(session_id))
        latest_turn = ((snapshot.get("turns") or [])[-1]) if isinstance(snapshot.get("turns"), list) and snapshot.get("turns") else {}
        pipeline_selection = (((response.get("pipeline_trace") or {}).get("selection") or {}).get("selected_hits") or [])
        selected_books = [
            str(item.get("book_slug") or "").strip()
            for item in pipeline_selection
            if isinstance(item, dict) and str(item.get("book_slug") or "").strip()
        ]

        report = {
            "status": "ok",
            "draft_id": draft_id,
            "canonical_book_path": str(normalized.get("canonical_book_path") or ""),
            "response_session_id": str(response.get("session_id") or ""),
            "citation_count": len(citations),
            "citation_books": citation_books,
            "citation_truths": citation_truths,
            "selected_hit_books": selected_books,
            "selected_has_private": any(book == "customer-pack-mixed-runtime-smoke" for book in selected_books),
            "selected_has_official": any(book in {"postinstallation_configuration", "etcd", "backup_and_restore"} for book in selected_books),
            "response_boundary_truth": str(summary.get("primary_boundary_truth") or ""),
            "response_boundary_badge": str(summary.get("primary_boundary_badge") or ""),
            "response_runtime_truth_label": str(summary.get("primary_runtime_truth_label") or ""),
            "latest_turn_boundary_truth": str(latest_turn.get("primary_boundary_truth") or ""),
            "latest_turn_boundary_badge": str(latest_turn.get("primary_boundary_badge") or ""),
            "latest_turn_runtime_truth_label": str(latest_turn.get("primary_runtime_truth_label") or ""),
        }

        passed = all(
            [
                report["citation_count"] >= 2,
                "private_customer_pack_runtime" in citation_truths,
                any(truth in {"official_validated_runtime", "official_candidate_runtime"} for truth in citation_truths),
                report["selected_has_private"] is True,
                report["selected_has_official"] is True,
                report["response_boundary_truth"] == "mixed_runtime_bridge",
                report["response_boundary_badge"] == "Mixed Runtime",
                report["response_runtime_truth_label"] == "OpenShift 4.20 Runtime + Customer Source-First Pack",
                report["latest_turn_boundary_truth"] == "mixed_runtime_bridge",
                report["latest_turn_boundary_badge"] == "Mixed Runtime",
                report["latest_turn_runtime_truth_label"] == "OpenShift 4.20 Runtime + Customer Source-First Pack",
            ]
        )
        report["status"] = "ok" if passed else "failed"
    finally:
        store.delete(session_id)
        delete_customer_pack_draft(REPO_ROOT, draft_id)
        temp_path.unlink(missing_ok=True)

    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(
        "# Mixed Runtime End-to-End Report\n\n"
        + "\n".join(f"- {key}: `{value}`" for key, value in report.items())
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
