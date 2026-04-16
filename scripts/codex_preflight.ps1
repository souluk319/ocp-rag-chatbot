[CmdletBinding(PositionalBinding = $false)]
param(
  [string]$WriteScope = "",
  [string]$VerifyCmd = "",
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$CliArgs
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\\Scripts\\python.exe"
$GitBash = "C:\Program Files\Git\bin\bash.exe"
$RuntimeDir = Join-Path $Root "artifacts\\runtime"
$ReportPath = Join-Path $RuntimeDir "codex_preflight.json"

Set-Location -LiteralPath $Root

function Write-PreflightReport {
  param(
    [hashtable]$Payload
  )

  New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null
  $json = $Payload | ConvertTo-Json -Depth 8
  [System.IO.File]::WriteAllText($ReportPath, $json, [System.Text.UTF8Encoding]::new($false))
}

function Get-UiPort {
  param(
    [string[]]$Arguments
  )

  $port = 8765
  for ($index = 0; $index -lt $Arguments.Length; $index++) {
    if ($Arguments[$index] -eq "--port" -and ($index + 1) -lt $Arguments.Length) {
      $candidate = $Arguments[$index + 1]
      if ([int]::TryParse($candidate, [ref]$port)) {
        return $port
      }
    }
  }
  return $port
}

function Get-DirtyCount {
  $statusLines = git -C $Root status --short 2>$null
  if ($LASTEXITCODE -ne 0 -or $null -eq $statusLines) {
    return $null
  }
  return @($statusLines).Count
}

$commandName = if ($CliArgs.Count -gt 0) { [string]$CliArgs[0] } else { "" }
$report = [ordered]@{
  timestamp = (Get-Date).ToString("o")
  shell = "pwsh"
  cwd = (Get-Location).Path
  root = $Root
  command = $commandName
  cli_args = @($CliArgs)
  write_scope = $WriteScope
  verify_cmd = $VerifyCmd
  python_path = $Python
  git_bash_path = $GitBash
  dirty_count = Get-DirtyCount
  report_path = $ReportPath
}

$branchName = git -C $Root rev-parse --abbrev-ref HEAD 2>$null
if ($LASTEXITCODE -eq 0 -and $branchName) {
  $report.branch = [string]$branchName
}

$worktreeRoot = git -C $Root rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -eq 0 -and $worktreeRoot) {
  $report.worktree_path = [string]$worktreeRoot
}

if (-not (Test-Path -LiteralPath $Python)) {
  $report.status = "failed"
  $report.error = "Missing required virtual environment: $Python"
  Write-PreflightReport -Payload $report
  throw $report.error
}

$report.git_bash_available = (Test-Path -LiteralPath $GitBash)

if ([string]::IsNullOrWhiteSpace($WriteScope)) {
  $report.status = "failed"
  $report.error = "Missing required write_scope. Set -WriteScope before running commands."
  Write-PreflightReport -Payload $report
  throw $report.error
}

if ([string]::IsNullOrWhiteSpace($VerifyCmd)) {
  $report.status = "failed"
  $report.error = "Missing required verify_cmd. Set -VerifyCmd before running commands."
  Write-PreflightReport -Payload $report
  throw $report.error
}

if ($report.branch -in @("main", "master") -and $null -ne $report.dirty_count -and $report.dirty_count -gt 0) {
  $report.status = "failed"
  $report.error = "Dirty main worktree is blocked. Create or switch to a non-main worktree before running commands."
  Write-PreflightReport -Payload $report
  throw $report.error
}

if ($commandName -eq "ui") {
  $uiPort = Get-UiPort -Arguments $CliArgs
  $listener = Get-NetTCPConnection -LocalPort $uiPort -State Listen -ErrorAction SilentlyContinue |
    Select-Object -First 1
  if ($null -ne $listener) {
    $listenerPid = $listener.OwningProcess
    $listenerProc = Get-CimInstance Win32_Process -Filter "ProcessId = $listenerPid" -ErrorAction SilentlyContinue
    $report.status = "failed"
    $report.ui_port = $uiPort
    $report.ui_listener = [ordered]@{
      pid = $listenerPid
      name = if ($listenerProc) { $listenerProc.Name } else { "" }
      command_line = if ($listenerProc) { $listenerProc.CommandLine } else { "" }
    }
    $report.error = "UI port $uiPort is already in use."
    Write-PreflightReport -Payload $report
    throw "UI port $uiPort is already in use by PID $listenerPid."
  }
  $report.ui_port = $uiPort
}

$report.status = "ok"
Write-PreflightReport -Payload $report

Write-Output "[preflight] shell=pwsh"
Write-Output "[preflight] cwd=$($report.cwd)"
Write-Output "[preflight] python=$Python"
Write-Output "[preflight] git_bash=$GitBash"
Write-Output "[preflight] command=$commandName"
Write-Output "[preflight] write_scope=$WriteScope"
Write-Output "[preflight] verify_cmd=$VerifyCmd"
