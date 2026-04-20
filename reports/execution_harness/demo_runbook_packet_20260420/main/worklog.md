# demo_runbook_packet_20260420 / main

- goal lock:
  - package the already-validated simulator scenarios into a human-run assignment demo script
  - reduce live demo prep friction with a single preflight command
- change scope:
  - docs only plus one helper script
- non-goals:
  - do not change runtime retrieval logic
  - do not alter simulator scenario semantics
  - do not mix unrelated worktree changes into this packet
- validation target:
  - runbook is aligned to the 5 simulator scenarios and evaluation criteria
  - prep script reaches the live backend health endpoint and prints runtime metadata
- evidence:
  - `docs/ocp420_assignment_demo_runbook.md` created with 5 scenario order, demo talking points, evaluation mapping, and code anchors
  - `scripts/run_submission_demo_checks.ps1` created to hit live health and optionally rerun the validated demo simulator
  - `powershell -ExecutionPolicy Bypass -File scripts\\run_submission_demo_checks.ps1` passed against `http://127.0.0.1:8765`
