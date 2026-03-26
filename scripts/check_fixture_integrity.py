"""Static integrity checks for evaluation fixtures.

This script catches accidental fixture regressions before they affect the
evaluation runner:
- fixture file remains valid JSON
- required fields exist on every fixture
- conversations are well-formed
- rewrite/retrieval/answer expectations are present
- multi-turn coverage is still included
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FIXTURE = ROOT / "scripts" / "eval-fixture.seed.json"
VALID_MODES = {"education", "operations"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate evaluation fixture structure")
    parser.add_argument("--fixture", default=str(DEFAULT_FIXTURE), help="Path to the fixture JSON file")
    return parser.parse_args()


def load_fixture(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Fixture root must be a list")
    return data


def validate_fixture(fixture: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    prefix = f"fixture[{index}]"

    for key in ("id", "mode_hint", "query_class", "language", "conversation", "expected"):
        if key not in fixture:
            errors.append(f"{prefix}: missing {key}")

    if not isinstance(fixture.get("id"), str) or not fixture["id"].strip():
        errors.append(f"{prefix}: id must be a non-empty string")

    mode_hint = fixture.get("mode_hint")
    if mode_hint not in VALID_MODES:
        errors.append(f"{prefix}: mode_hint must be one of {sorted(VALID_MODES)}")

    if not isinstance(fixture.get("query_class"), str) or not fixture["query_class"].strip():
        errors.append(f"{prefix}: query_class must be a non-empty string")

    if not isinstance(fixture.get("language"), str) or not fixture["language"].strip():
        errors.append(f"{prefix}: language must be a non-empty string")

    conversation = fixture.get("conversation")
    if not isinstance(conversation, list) or not conversation:
        errors.append(f"{prefix}: conversation must be a non-empty list")
    else:
        user_turns = 0
        for turn_idx, turn in enumerate(conversation):
            turn_prefix = f"{prefix}.conversation[{turn_idx}]"
            if not isinstance(turn, dict):
                errors.append(f"{turn_prefix}: turn must be an object")
                continue
            if turn.get("role") not in {"user", "assistant", "system"}:
                errors.append(f"{turn_prefix}: invalid role {turn.get('role')!r}")
            if not isinstance(turn.get("content"), str) or not turn["content"].strip():
                errors.append(f"{turn_prefix}: content must be a non-empty string")
            if turn.get("role") == "user":
                user_turns += 1
        if user_turns == 0:
            errors.append(f"{prefix}: conversation must include at least one user turn")
        if conversation[-1].get("role") != "user":
            errors.append(f"{prefix}: conversation must end with a user turn")

    expected = fixture.get("expected")
    if not isinstance(expected, dict):
        errors.append(f"{prefix}: expected must be an object")
        return errors

    for section in ("rewrite", "retrieval", "answer"):
        if section not in expected or not isinstance(expected.get(section), dict):
            errors.append(f"{prefix}: expected.{section} must be an object")

    rewrite = expected.get("rewrite", {})
    if isinstance(rewrite, dict) and not any(
        key in rewrite for key in ("should_change", "must_equal", "must_include_any", "must_not_include_any")
    ):
        errors.append(f"{prefix}: expected.rewrite needs at least one check")

    retrieval = expected.get("retrieval", {})
    if isinstance(retrieval, dict) and not any(
        key in retrieval for key in ("source_any", "source_prefer_top3", "source_exclude_top3", "min_distinct_sources")
    ):
        errors.append(f"{prefix}: expected.retrieval needs at least one check")

    answer = expected.get("answer", {})
    if isinstance(answer, dict) and not any(
        key in answer for key in ("must_include_any", "should_include_any", "must_not_include_any", "citation_required")
    ):
        errors.append(f"{prefix}: expected.answer needs at least one check")

    return errors


def main() -> int:
    args = parse_args()
    path = Path(args.fixture)

    try:
        fixtures = load_fixture(path)
    except Exception as exc:
        print(f"Fixture integrity check failed to load {path}: {exc}")
        return 1

    failures: list[str] = []
    ids: set[str] = set()
    mode_counts: Counter[str] = Counter()
    multi_turn_count = 0

    for idx, fixture in enumerate(fixtures):
        if not isinstance(fixture, dict):
            failures.append(f"fixture[{idx}]: fixture must be an object")
            continue

        fixture_id = fixture.get("id")
        if isinstance(fixture_id, str) and fixture_id in ids:
            failures.append(f"fixture[{idx}]: duplicate id {fixture_id!r}")
        if isinstance(fixture_id, str):
            ids.add(fixture_id)

        mode_hint = fixture.get("mode_hint")
        if isinstance(mode_hint, str):
            mode_counts[mode_hint] += 1

        conversation = fixture.get("conversation")
        if isinstance(conversation, list):
            user_turns = sum(1 for turn in conversation if isinstance(turn, dict) and turn.get("role") == "user")
            if user_turns >= 2:
                multi_turn_count += 1

        failures.extend(validate_fixture(fixture, idx))

    if len(fixtures) < 8:
        failures.append(f"fixture file should contain at least 8 fixtures, got {len(fixtures)}")
    if not all(mode in mode_counts for mode in VALID_MODES):
        failures.append("fixture file must cover both education and operations modes")
    if multi_turn_count < 2:
        failures.append(f"fixture file should include at least 2 multi-turn cases, got {multi_turn_count}")

    if failures:
        print("Fixture integrity check failed.")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Fixture integrity check passed.")
    print(f"- fixture count: {len(fixtures)}")
    print(f"- mode coverage: education={mode_counts['education']}, operations={mode_counts['operations']}")
    print(f"- multi-turn cases: {multi_turn_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
