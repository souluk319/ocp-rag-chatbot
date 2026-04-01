param(
  [double]$HoldSeconds = 0
)

$ErrorActionPreference = "Stop"

python deployment/start_runtime_stack.py `
  --bridge-port 18101 `
  --od-port 18102 `
  --gateway-port 8000 `
  --hold-seconds $HoldSeconds
