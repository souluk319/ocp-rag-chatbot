# Evaluation Runner

This repo now includes a reproducible fixture runner for judge-facing evidence.

## What it does

- Replays `scripts/eval-fixture.seed.json` against a live API.
- Supports both JSON and SSE streaming transports.
- Scores each fixture with three groups of checks:
  - rewrite
  - retrieval
  - answer
- Writes a machine-readable JSON report and, optionally, a Markdown summary.

## Check semantics

- `must_include_any` means at least one listed string must appear.
- `must_not_include_any` means none of the listed strings may appear.
- `citation_required` is satisfied when the response payload includes non-empty `sources`.
- `requires_step_list` checks for a numbered or bulleted step list in the answer.
- `requires_command_example` checks for an `oc` or `kubectl` command example in the answer.

## Windows-friendly usage

```powershell
python scripts/eval_fixture_runner.py --fixture scripts/eval-fixture.seed.json --endpoint http://127.0.0.1:8000 --format both --output data/eval_report.json
```

To exercise the streaming path:

```powershell
python scripts/eval_fixture_runner.py --fixture scripts/eval-fixture.seed.json --endpoint http://127.0.0.1:8000 --transport stream --format both --output data/eval_report.json
```

## Output files

- JSON report: `data/eval_report.json`
- Markdown report: `data/eval_report.md`

The JSON payload includes:

- `generated_at`
- `endpoint`
- `transport`
- `summary`
- `fixtures`

Each fixture result includes:

- `fixture_id`
- `mode_hint`
- `query_class`
- `rewritten_query`
- `sources`
- `checks`
- `passed`
- `duration_ms`

## Notes

- The runner replays user turns in order and keeps a single `session_id` per fixture.
- Assistant turns in the fixture file are treated as reference context, because the current API only accepts user prompts.
- The runner exits with code `1` if any fixture fails, which makes it easy to plug into CI or a manual pre-commit check.
