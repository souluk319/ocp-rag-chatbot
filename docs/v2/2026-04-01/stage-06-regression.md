# Stage 6 - Direct localhost regression

## Purpose

Verify that the Stage 5 runtime behavior is still intact on the live `localhost:8000` runtime.

## What this stage checks

- Basic definition questions still answer in Korean.
- Operational questions still answer in Korean.
- Citations still click through to a real HTML viewer.

## Live checkpoints

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/api/v1/chat`

## Run command

```powershell
python .\deployment\check_stage06_direct_runtime_regression.py
```

## Completion rule

This stage only passes when the user can directly verify the behavior in the browser at `localhost:8000`.
