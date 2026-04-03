from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.language_policy import describe_language_policy, load_language_policy_map
from ocp_rag_part1.settings import load_settings
from ocp_rag_part2.models import SessionContext
from ocp_rag_part3 import Part3Answerer
from ocp_rag_part4.server import _viewer_path_to_local_html


DEFAULT_CASES = [
    ("learn", "OpenShift 아키텍처를 설명해줘"),
    ("ops", "etcd 백업은 어떻게 해?"),
    ("ops", "백업 복구 문서는 어디서 봐?"),
    ("learn", "Machine Config Operator가 뭐 하는 거야?"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify the real answer -> citation -> internal viewer flow."
    )
    parser.add_argument("--mode", default=None, help="Run a single query in one mode.")
    parser.add_argument("--query", default=None, help="Run a single query instead of the defaults.")
    return parser


def _cases_from_args(args: argparse.Namespace) -> list[tuple[str, str]]:
    if args.query:
        return [(args.mode or "ops", args.query)]
    return list(DEFAULT_CASES)


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    answerer = Part3Answerer.from_settings(settings)
    policy_map = load_language_policy_map(settings)

    for mode, query in _cases_from_args(args):
        result = answerer.answer(
            query,
            mode=mode,
            context=SessionContext(mode=mode, ocp_version="4.20"),
            top_k=5,
            candidate_k=20,
            max_context_chunks=6,
        )
        print("=" * 88)
        print(f"mode={mode}")
        print(f"query={query}")
        print(f"rewritten_query={result.rewritten_query}")
        print(f"warnings={result.warnings}")
        print(f"answer={result.answer}")
        if not result.citations:
            print("citations=[]")
            continue

        for citation in result.citations:
            local_html = _viewer_path_to_local_html(ROOT, citation.viewer_path)
            policy_display = describe_language_policy(policy_map.get(citation.book_slug))
            print(
                "citation="
                f"[{citation.index}] {citation.book_slug} | {citation.section} | "
                f"viewer={citation.viewer_path} | local_exists={bool(local_html and local_html.exists())} | "
                f"badge={policy_display['badge']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
