[CmdletBinding(PositionalBinding = $false)]
param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$CommandArgs
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$GitBash = "C:\Program Files\Git\bin\bash.exe"

if (-not (Test-Path -LiteralPath $GitBash)) {
  throw "Missing required Git Bash: $GitBash"
}

if ($CommandArgs.Count -eq 0) {
  throw "Missing command. Use codex_git_bash.ps1 <command...>"
}

$escapedArgs = foreach ($arg in $CommandArgs) {
  "'" + ($arg -replace "'", "'\\''") + "'"
}
$joinedArgs = [string]::Join(" ", $escapedArgs)
$repoRootForBash = $Root -replace "\\", "/"

& $GitBash -lc "cd '$repoRootForBash' && $joinedArgs"
exit $LASTEXITCODE
