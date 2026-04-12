param(
  [Parameter(Mandatory = $true)]
  [string]$ScriptPath,
  [Parameter(Mandatory = $true)]
  [string]$WriteScope,
  [Parameter(Mandatory = $true)]
  [string]$VerifyCmd,
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ScriptArgs
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\\Scripts\\python.exe"
$Preflight = Join-Path $PSScriptRoot "codex_preflight.ps1"
Set-Location -LiteralPath $Root
if (-not (Test-Path -LiteralPath $Python)) {
  throw "Missing required virtual environment: $Python"
}
if (-not (Test-Path -LiteralPath $Preflight)) {
  throw "Missing required preflight script: $Preflight"
}

$ResolvedScript = if ([System.IO.Path]::IsPathRooted($ScriptPath)) {
  $ScriptPath
} else {
  Join-Path $Root $ScriptPath
}
if (-not (Test-Path -LiteralPath $ResolvedScript)) {
  throw "Missing required script: $ResolvedScript"
}

$CommandName = [System.IO.Path]::GetFileNameWithoutExtension($ResolvedScript)
& $Preflight -WriteScope $WriteScope -VerifyCmd $VerifyCmd $CommandName @ScriptArgs
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}

$env:PLAY_BOOK_LAUNCHER = "codex_python.ps1"
$env:PLAY_BOOK_WRITE_SCOPE = $WriteScope
$env:PLAY_BOOK_VERIFY_CMD = $VerifyCmd

& $Python $ResolvedScript @ScriptArgs
exit $LASTEXITCODE
