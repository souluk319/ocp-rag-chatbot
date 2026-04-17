[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$StateDir = Join-Path $RepoRoot "tmp\local_runtime_stack"
$StatePath = Join-Path $StateDir "state.json"

function Read-StackState {
    if (-not (Test-Path -LiteralPath $StatePath)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function Get-TrackedProcess {
    param(
        [Parameter(Mandatory = $false)]
        [object]$Entry
    )

    if ($null -eq $Entry -or $null -eq $Entry.pid) {
        return $null
    }

    $process = Get-Process -Id ([int]$Entry.pid) -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        return $null
    }

    $trackedStart = [string]$Entry.start_time
    if (-not [string]::IsNullOrWhiteSpace($trackedStart)) {
        $currentStart = $process.StartTime.ToString("o")
        if ($currentStart -ne $trackedStart) {
            return $null
        }
    }

    return $process
}

function Stop-TrackedProcess {
    param(
        [Parameter(Mandatory = $false)]
        [object]$Entry,

        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    $process = Get-TrackedProcess -Entry $Entry
    if ($null -eq $process) {
        return
    }

    & taskkill.exe /PID $process.Id /T /F *> $null
    Write-Host "stopped $Label ($($process.Id))"
}

function Stop-Qdrant {
    param(
        [Parameter(Mandatory = $false)]
        [object]$InfraState
    )

    $qdrantMode = if ($InfraState) { [string]$InfraState.qdrant_mode } else { "" }
    $startedByStack = if ($InfraState) { [bool]$InfraState.started_by_stack } else { $false }

    if ($qdrantMode -eq "legacy_named") {
        if ($startedByStack) {
            docker stop ocp-rag-qdrant | Out-Host
        }
        else {
            Write-Host "legacy qdrant container was already running; left in place."
        }
        return
    }

    Push-Location -LiteralPath $RepoRoot
    try {
        docker compose stop qdrant | Out-Host
    }
    finally {
        Pop-Location
    }
}

$state = Read-StackState
if ($state) {
    Stop-TrackedProcess -Entry $state.frontend -Label "frontend"
    Stop-TrackedProcess -Entry $state.backend -Label "backend"
    Remove-Item -LiteralPath $StatePath -Force -ErrorAction SilentlyContinue
}
else {
    Write-Host "No tracked PBS app processes were found."
}

Stop-Qdrant -InfraState $state.infra

Write-Host "logs: $StateDir"
