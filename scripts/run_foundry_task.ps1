param(
  [Parameter(Mandatory = $true)]
  [string]$Profile,
  [string]$LogPath = "",
  [int]$Retries = 2,
  [int]$RetryDelaySeconds = 900
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Runner = Join-Path $PSScriptRoot "run_gold_foundry.py"
$Preflight = Join-Path $PSScriptRoot "codex_preflight.ps1"
$Python = Join-Path $Root ".venv\\Scripts\\python.exe"
$WriteScope = "reports\\build_logs\\task_scheduler;reports\\build_logs\\foundry_runs"
$VerifyCmd = "`"$Python`" `"$Runner`" --profile $Profile --fail-on-release-blocking --retries $Retries --retry-delay-seconds $RetryDelaySeconds"
Set-Location -LiteralPath $Root
if (-not (Test-Path -LiteralPath $Python)) {
  throw "Missing required virtual environment: $Python"
}
if (-not (Test-Path -LiteralPath $Preflight)) {
  throw "Missing required preflight script: $Preflight"
}
if ([string]::IsNullOrWhiteSpace($LogPath)) {
  $LogDir = Join-Path $Root "reports\\build_logs\\task_scheduler"
  New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
  $LogPath = Join-Path $LogDir "$Profile.log"
} else {
  $LogDir = Split-Path -Parent $LogPath
  if ($LogDir) {
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
  }
}

& $Preflight -WriteScope $WriteScope -VerifyCmd $VerifyCmd "foundry" "--profile" $Profile
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}

$env:PLAY_BOOK_LAUNCHER = "run_foundry_task.ps1"
$env:PLAY_BOOK_WRITE_SCOPE = $WriteScope
$env:PLAY_BOOK_VERIFY_CMD = $VerifyCmd

$arguments = @(
  $Runner,
  "--profile", $Profile,
  "--fail-on-release-blocking",
  "--retries", "$Retries",
  "--retry-delay-seconds", "$RetryDelaySeconds"
)

& $Python @arguments *>> $LogPath
exit $LASTEXITCODE
