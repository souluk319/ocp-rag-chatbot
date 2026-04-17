[CmdletBinding()]
param(
    [int]$BackendPort = 8765,
    [int]$FrontendPort = 5173,
    [string]$ServeHost = "0.0.0.0"
)

$ErrorActionPreference = "Stop"

$PbsUpPath = Join-Path $PSScriptRoot "pbs-up.ps1"
if (-not (Test-Path -LiteralPath $PbsUpPath)) {
    throw "pbs-up script not found: $PbsUpPath"
}

& powershell.exe `
    -NoProfile `
    -ExecutionPolicy Bypass `
    -File $PbsUpPath `
    -Mode dev `
    -BackendPort $BackendPort `
    -FrontendPort $FrontendPort `
    -ServeHost $ServeHost
exit $LASTEXITCODE
