from __future__ import annotations

import argparse
import json
import sys
import threading
from datetime import datetime
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib import request

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.answering.answerer import Part3Answerer
from play_book_studio.app.server import _build_handler
from play_book_studio.app.sessions import SessionStore
from play_book_studio.config.settings import load_settings


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run demo chat regression against the real answerer via /api/chat")
    parser.add_argument(
        "--single-turn-cases",
        type=Path,
        default=ROOT / "manifests" / "demo_safe_questions.jsonl",
    )
    parser.add_argument(
        "--multiturn-cases",
        type=Path,
        default=ROOT / "manifests" / "demo_multiturn_scenarios.jsonl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=120.0,
    )
    return parser


def _post_chat(*, port: int, session_id: str, query: str, timeout: float) -> dict:
    req = request.Request(
        f"http://127.0.0.1:{port}/api/chat",
        data=json.dumps({"session_id": session_id, "query": query}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _single_turn_case_status(case: dict, payload: dict) -> tuple[bool, list[str]]:
    expected = set(case.get("expected_book_slugs", []))
    citations = payload.get("citations", []) or []
    cited_books = {str(item.get("book_slug") or "") for item in citations}
    answer = str(payload.get("answer") or "")
    response_kind = str(payload.get("response_kind") or "")
    reasons: list[str] = []
    if response_kind != "rag":
        reasons.append(f"response_kind={response_kind}")
    if not citations:
        reasons.append("citations=0")
    if expected and cited_books.isdisjoint(expected):
        reasons.append(f"expected_books_miss={sorted(expected)} vs {sorted(cited_books)}")
    if "제공된 근거" in answer and "없" in answer:
        reasons.append("grounded_no_answer")
    return not reasons, reasons


def _turn_status(turn: dict, payload: dict) -> tuple[bool, list[str]]:
    expected_books = set(turn.get("expected_book_slugs", []))
    citations = payload.get("citations", []) or []
    cited_books = {str(item.get("book_slug") or "") for item in citations}
    current_topic = str(((payload.get("context") or {}).get("current_topic")) or "")
    answer = str(payload.get("answer") or "")
    response_kind = str(payload.get("response_kind") or "")
    reasons: list[str] = []
    if response_kind != "rag":
        reasons.append(f"response_kind={response_kind}")
    if not citations:
        reasons.append("citations=0")
    if expected_books and cited_books.isdisjoint(expected_books):
        reasons.append(f"expected_books_miss={sorted(expected_books)} vs {sorted(cited_books)}")
    if current_topic != str(turn.get("expected_topic") or ""):
        reasons.append(f"topic={current_topic!r}")
    if "제공된 근거" in answer and "없" in answer:
        reasons.append("grounded_no_answer")
    return not reasons, reasons


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    answerer = Part3Answerer.from_settings(settings)
    store = SessionStore()
    handler = _build_handler(answerer=answerer, store=store, root_dir=ROOT)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    single_turn_cases = read_jsonl(args.single_turn_cases)
    multiturn_cases = read_jsonl(args.multiturn_cases)

    report: dict[str, object] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "server_url": f"http://127.0.0.1:{port}",
        "single_turn_cases_file": str(args.single_turn_cases),
        "multiturn_cases_file": str(args.multiturn_cases),
        "settings": {
            "ocp_version": settings.ocp_version,
            "docs_language": settings.docs_language,
            "qdrant_url": settings.qdrant_url,
            "qdrant_collection": settings.qdrant_collection,
            "llm_endpoint": settings.llm_endpoint,
            "llm_model": settings.llm_model,
            "embedding_base_url": settings.embedding_base_url,
            "embedding_model": settings.embedding_model,
        },
        "single_turn": {"details": []},
        "multiturn": {"details": []},
    }

    try:
        single_pass = 0
        for case in single_turn_cases:
            payload = _post_chat(
                port=port,
                session_id=str(case["id"]),
                query=str(case["query"]),
                timeout=args.request_timeout,
            )
            ok, reasons = _single_turn_case_status(case, payload)
            single_pass += int(ok)
            report["single_turn"]["details"].append(
                {
                    "id": case["id"],
                    "query": case["query"],
                    "expected_book_slugs": case.get("expected_book_slugs", []),
                    "response_kind": payload.get("response_kind"),
                    "current_topic": (payload.get("context") or {}).get("current_topic"),
                    "cited_book_slugs": [item.get("book_slug") for item in payload.get("citations", [])],
                    "warnings": payload.get("warnings", []),
                    "pass": ok,
                    "reasons": reasons,
                }
            )

        multi_pass = 0
        for scenario in multiturn_cases:
            session_id = str(scenario["id"])
            turn_details: list[dict[str, object]] = []
            scenario_ok = True
            for turn in scenario["turns"]:
                payload = _post_chat(
                    port=port,
                    session_id=session_id,
                    query=str(turn["query"]),
                    timeout=args.request_timeout,
                )
                ok, reasons = _turn_status(turn, payload)
                scenario_ok = scenario_ok and ok
                turn_details.append(
                    {
                        "turn": turn["turn"],
                        "query": turn["query"],
                        "expected_topic": turn["expected_topic"],
                        "expected_book_slugs": turn.get("expected_book_slugs", []),
                        "response_kind": payload.get("response_kind"),
                        "current_topic": (payload.get("context") or {}).get("current_topic"),
                        "history_size": payload.get("history_size"),
                        "cited_book_slugs": [item.get("book_slug") for item in payload.get("citations", [])],
                        "warnings": payload.get("warnings", []),
                        "pass": ok,
                        "reasons": reasons,
                    }
                )
            multi_pass += int(scenario_ok)
            report["multiturn"]["details"].append(
                {
                    "id": scenario["id"],
                    "title": scenario.get("title"),
                    "track": scenario.get("track"),
                    "pass": scenario_ok,
                    "turns": turn_details,
                }
            )

        report["single_turn"]["case_count"] = len(single_turn_cases)
        report["single_turn"]["pass_count"] = single_pass
        report["single_turn"]["pass_rate"] = round(single_pass / max(len(single_turn_cases), 1), 4)
        report["multiturn"]["case_count"] = len(multiturn_cases)
        report["multiturn"]["pass_count"] = multi_pass
        report["multiturn"]["pass_rate"] = round(multi_pass / max(len(multiturn_cases), 1), 4)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    output_path = args.output or (settings.runtime_dir / "demo_chat_regression_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote demo regression report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    single_ok = report["single_turn"]["pass_count"] == report["single_turn"]["case_count"]
    multi_ok = report["multiturn"]["pass_count"] == report["multiturn"]["case_count"]
    return 0 if single_ok and multi_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
