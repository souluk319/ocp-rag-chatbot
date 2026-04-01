# Stage 6 Direct Runtime Regression Report

## Goal

Verify that the Stage 5 runtime fixes still work on the live runtime at `localhost:8000`.

## Checkpoints

- Basic definition questions still answer in Korean.
- Operational questions still answer in Korean.
- Citations still click through to a real HTML viewer.

## How to run

```powershell
python .\deployment\check_stage06_direct_runtime_regression.py
```

## Summary

- checked_at: `2026-04-01T03:21:36.083827+00:00`
- base_url: `http://127.0.0.1:8000`
- health_status: `200`
- health_ok: `True`
- case_count: `5`
- passed_count: `5`
- overall_pass: `True`

## Results

| case_id | kind | status | sources | viewer | route |
| --- | --- | --- | --- | --- | --- |
| definition-openshift | definition | pass | 2 | 200 text/html | manifest_runtime_rescue |
| definition-ocp | definition | pass | 2 | 200 text/html | manifest_runtime_rescue |
| ops-firewall | operations | pass | 1 | 200 text/html | manifest_runtime_rescue |
| ops-update | operations | pass | 2 | 200 text/html | manifest_runtime_rescue |
| ops-disconnected-mirror | operations | pass | 2 | 200 text/html | manifest_runtime_rescue |

## Output

- JSON: `C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-06-direct-runtime-report.json`
