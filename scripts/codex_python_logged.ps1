param(
  [Parameter(Mandatory = $true)]
  [string]$ScriptPath,
  [Parameter(Mandatory = $true)]
  [string]$WriteScope,
  [Parameter(Mandatory = $true)]
  [string]$VerifyCmd,
  [string]$LogPath = "",
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ScriptArgs
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$WrappedScript = Join-Path $PSScriptRoot "codex_python.ps1"
Set-Location -LiteralPath $Root

if (-not (Test-Path -LiteralPath $WrappedScript)) {
  throw "Missing required wrapper script: $WrappedScript"
}

$CommandName = [System.IO.Path]::GetFileNameWithoutExtension($ScriptPath)
$Timestamp = Get-Date -Format "yyyyMMddTHHmmss"
$ResolvedLogPath = if ([string]::IsNullOrWhiteSpace($LogPath)) {
  Join-Path $Root ("reports\\build_logs\\{0}.{1}.log" -f $CommandName, $Timestamp)
} elseif ([System.IO.Path]::IsPathRooted($LogPath)) {
  $LogPath
} else {
  Join-Path $Root $LogPath
}

$LogDirectory = Split-Path -Parent $ResolvedLogPath
if (-not [string]::IsNullOrWhiteSpace($LogDirectory)) {
  New-Item -ItemType Directory -Force -Path $LogDirectory | Out-Null
}

$WrappedExitCode = 0
& {
  & $WrappedScript $ScriptPath $WriteScope $VerifyCmd @ScriptArgs
  $script:WrappedExitCode = $LASTEXITCODE
} 2>&1 | Tee-Object -FilePath $ResolvedLogPath

Write-Output ("[pipeline-log] {0}" -f $ResolvedLogPath)
exit $WrappedExitCode
