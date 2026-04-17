# repo_bloat_cleanup_20260417

- kickoff: user explicitly called out test bloat, redundant files, and glue-code accumulation as the current repo-level failure mode
- objective: do not reframe this as “quality is fine”; inventory actual bloat first, then remove only safe dead paths and leave explicit residue for the next cut
- locked validation: frontend lint/build/test plus focused backend pytest around the recently touched runtime surfaces
- action: added `scripts/repo_hygiene.py` to audit tracked file concentration and clean generated junk under `src/tests/scripts`, root `.pytest_cache`, and `presentation-ui/dist`
- action: added explicit `presentation-ui/dist/` ignore entry to repo `.gitignore`
- evidence: first hygiene pass removed 16 junk targets totaling `5,125,620` bytes; post-validation cleanup removed another 14 regenerated targets totaling `2,759,528` bytes
- residue: tracked bloat still concentrates in `reports`, `tests`, and several oversized backend/frontend files; no tracked test file deletion was attempted in this packet because that crosses into destructive cleanup
