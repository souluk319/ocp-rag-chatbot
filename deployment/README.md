# Deployment Scope

This directory now holds the deployment and air-gap contracts for v2.

Current contents cover:

- runtime contract validation for the approved company path
- approved transfer bundle schema
- closed-network refresh flow and rollback expectations
- bundle layout, manifest lineage, and index activation contracts
- operator runbook and baseline seed helper for the first approved refresh cycle
- Stage 11 readiness preflight

Key entry points:

- `deployment/check_runtime_contract.py`
- `deployment/check_stage11_readiness.py`
- `deployment/initialize_stage11_baseline.py`
- `deployment/activation-smoke-case-ids.json`
- `deployment/airgap-flow.md`
- `deployment/bundle-schema.yaml`
- `deployment/approval-record-schema.yaml`
- `deployment/bundle-layout-contract.md`
- `deployment/manifest-lineage-contract.md`
- `deployment/index-activation-contract.md`
- `deployment/operator-runbook-stage11.md`
- `deployment/stage11-readiness.md`
- `docs/v2/stage11-readiness.md`
