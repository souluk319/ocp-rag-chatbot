# Stage 14 Operator Runbook

## Purpose

Stage 14 turns the validated Stage 12 serving path into a repeatable operator launch path.

This runbook is for bringing up the runtime stack itself:

- embedding/chat bridge
- OpenDocuments HTTP server
- product runtime gateway
- HTML citation viewer route

It is not the corpus refresh runbook. Stage 11 still owns refresh, activation, and rollback.

## Startup prerequisites

Before startup, confirm:

1. `.env` contains the approved company endpoint and model values
2. embedding baseline is `BAAI/bge-m3`
3. an active Stage 11 index exists in `indexes/current.txt`
4. `workspace/stage11/<active-index>/` exists
5. runtime contract check passes

Recommended preflight:

```powershell
python deployment/check_runtime_contract.py
```

Expected interpretation:

- `missing_required_keys = []`
- `missing_gateway_keys` may still include `OD_SERVER_BASE_URL` when the launcher is used, because the launcher injects it for the gateway process

## One-command launch

Run:

```powershell
python deployment/start_runtime_stack.py
```

This launcher will:

1. resolve the active Stage 11 index
2. detect the active vector dimension from the Stage 11 LanceDB store
3. start the local bridge
4. start OpenDocuments against the active Stage 11 data directory
5. start the product gateway with launcher-injected `OD_SERVER_BASE_URL`
6. verify health endpoints
7. verify that a citation HTML document can be opened through the gateway

By default, the stack stays up until interrupted.

## Short-lived startup validation

For a bounded launch test:

```powershell
python deployment/start_runtime_stack.py --hold-seconds 10
```

This is useful for CI-like smoke checks or quick operator verification.

## Default endpoints

- bridge health: `http://127.0.0.1:18101/health`
- OpenDocuments health: `http://127.0.0.1:18102/api/v1/health`
- gateway health: `http://127.0.0.1:18103/health`
- gateway chat stream: `http://127.0.0.1:18103/api/v1/chat/stream`

## Logs and report

The launcher writes:

- report: `data/manifests/generated/stage14-runtime-launch-report.json`
- logs:
  - `data/manifests/generated/stage14-runtime-launch-logs/bridge.log`
  - `data/manifests/generated/stage14-runtime-launch-logs/opendocuments.log`
  - `data/manifests/generated/stage14-runtime-launch-logs/gateway.log`

## Stop behavior

- foreground mode: `Ctrl+C`
- on Windows, child processes are torn down with `taskkill /T /F`

## Interpretation

Stage 14 launch success means:

- the serving stack can be started by an operator with one command
- the active index is wired into OpenDocuments correctly
- the gateway can serve health and citation HTML

Stage 14 does not replace:

- Stage 9 retrieval-quality authority
- Stage 10 evaluation authority
- Stage 11 refresh and rollback authority
