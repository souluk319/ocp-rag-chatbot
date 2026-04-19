param(
  [Parameter(Mandatory = $true)]
  [string]$ScriptPath,
  [Parameter(Mandatory = $true)]
  [string]$WriteScope,
  [Parameter(Mandatory = $true)]
  [string]$VerifyCmd,
  [Parameter(Mandatory = $true)]
  [string]$LogPath,
  [Parameter(Mandatory = $true)]
  [string]$StatusPath,
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ScriptArgs
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$WrappedScript = Join-Path $PSScriptRoot "codex_python.ps1"
if (-not (Test-Path -LiteralPath $WrappedScript)) {
  throw "Missing required wrapper script: $WrappedScript"
}

function Resolve-TargetPath([string]$PathValue) {
  if ([System.IO.Path]::IsPathRooted($PathValue)) {
    return $PathValue
  }
  return Join-Path $Root $PathValue
}

function Quote-Single([string]$Value) {
  return "'" + ($Value -replace "'", "''") + "'"
}

$ResolvedLogPath = Resolve-TargetPath $LogPath
$ResolvedStatusPath = Resolve-TargetPath $StatusPath
$ResolvedScriptPath = if ([System.IO.Path]::IsPathRooted($ScriptPath)) {
  $ScriptPath
} else {
  Join-Path $Root $ScriptPath
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ResolvedLogPath) | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ResolvedStatusPath) | Out-Null
Set-Content -LiteralPath $ResolvedLogPath -Value "" -Encoding utf8
@{
  status = "running"
  started_at = (Get-Date -Format o)
  script_path = $ResolvedScriptPath
  log_path = $ResolvedLogPath
} | ConvertTo-Json | Set-Content -LiteralPath $ResolvedStatusPath -Encoding utf8

$SerializedArgs = if ($ScriptArgs) {
  "@(" + (($ScriptArgs | ForEach-Object { Quote-Single $_ }) -join ", ") + ")"
} else {
  "@()"
}

$InnerCommand = @"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location -LiteralPath $(Quote-Single $Root)
\$ErrorActionPreference = 'Stop'
\$exitCode = 0
\$scriptArgs = $SerializedArgs
try {
  & {
    & $(Quote-Single $WrappedScript) $(Quote-Single $ResolvedScriptPath) $(Quote-Single $WriteScope) $(Quote-Single $VerifyCmd) @scriptArgs
    \$script:exitCode = \$LASTEXITCODE
  } 2>&1 | Tee-Object -FilePath $(Quote-Single $ResolvedLogPath) -Append
}
catch {
  (\$_ | Out-String) | Tee-Object -FilePath $(Quote-Single $ResolvedLogPath) -Append | Out-Null
  \$exitCode = 1
}
@{
  status = if (\$exitCode -eq 0) { 'completed' } else { 'failed' }
  exit_code = \$exitCode
  finished_at = (Get-Date -Format o)
  script_path = $(Quote-Single $ResolvedScriptPath)
  log_path = $(Quote-Single $ResolvedLogPath)
} | ConvertTo-Json | Set-Content -LiteralPath $(Quote-Single $ResolvedStatusPath) -Encoding utf8
exit \$exitCode
"@

$EncodedCommand = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($InnerCommand))
$Process = Start-Process -FilePath "powershell.exe" -ArgumentList @(
  "-NoProfile",
  "-ExecutionPolicy", "Bypass",
  "-EncodedCommand", $EncodedCommand
) -WorkingDirectory $Root -PassThru

[pscustomobject]@{
  pid = $Process.Id
  script_path = $ResolvedScriptPath
  log_path = $ResolvedLogPath
  status_path = $ResolvedStatusPath
  started_at = Get-Date -Format o
} | ConvertTo-Json -Depth 4
