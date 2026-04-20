param(
  [string]$ApiBase = "http://127.0.0.1:8765",
  [switch]$RunSimulator
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

Write-Host "[demo-check] api-base=$ApiBase"

$health = Invoke-RestMethod "$ApiBase/api/health" -TimeoutSec 15
if (-not $health.ok) {
  throw "Health check failed for $ApiBase"
}

$runtime = $health.runtime
Write-Host "[demo-check] app=$($runtime.app_label)"
Write-Host "[demo-check] ocp_version=$($runtime.ocp_version)"
Write-Host "[demo-check] model=$($runtime.llm_model)"
Write-Host "[demo-check] embedding=$($runtime.embedding_model)"
Write-Host "[demo-check] reranker_enabled=$($runtime.reranker_enabled)"
Write-Host "[demo-check] qdrant_collection=$($runtime.qdrant_collection)"
Write-Host "[demo-check] graph_mode=$($runtime.graph_runtime_mode)"

if ($RunSimulator) {
  Write-Host "[demo-check] running live simulator"
  powershell -ExecutionPolicy Bypass -File .\scripts\codex_python.ps1 `
    -ScriptPath .\scripts\run_ocp420_demo_simulator.py `
    -WriteScope reports/demo_simulator/ocp420_demo_simulator_eval.json `
    -VerifyCmd "submission demo live simulator" `
    --api-base $ApiBase `
    --output reports/demo_simulator/ocp420_demo_simulator_eval.json

  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
}

Write-Host "[demo-check] completed"
