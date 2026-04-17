[CmdletBinding()]
param(
    [ValidateSet("serve", "dev")]
    [string]$Mode = "serve",

    [int]$BackendPort = 8765,

    [int]$FrontendPort = 5173,

    [string]$ServeHost = "0.0.0.0"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$RunnerPath = Join-Path $PSScriptRoot "pbs-runner.ps1"
$StateDir = Join-Path $RepoRoot "tmp\local_runtime_stack"
$StatePath = Join-Path $StateDir "state.json"
$RunToken = Get-Date -Format "yyyyMMdd-HHmmss"
$BackendStdout = Join-Path $StateDir "backend.$RunToken.out.log"
$BackendStderr = Join-Path $StateDir "backend.$RunToken.err.log"
$FrontendStdout = Join-Path $StateDir "frontend.$RunToken.out.log"
$FrontendStderr = Join-Path $StateDir "frontend.$RunToken.err.log"
$FrontendDistDir = Join-Path $RepoRoot "presentation-ui\dist"

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

    if ($null -eq $Entry) {
        return $null
    }

    $pidValue = $Entry.pid
    if ($null -eq $pidValue) {
        return $null
    }

    $process = Get-Process -Id ([int]$pidValue) -ErrorAction SilentlyContinue
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

function Get-LogTail {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return ""
    }

    return (Get-Content -LiteralPath $Path -Tail 20) -join [Environment]::NewLine
}

function Test-HttpReady {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Uri,

        [int]$TimeoutMilliseconds = 3000
    )

    $request = [System.Net.HttpWebRequest]::Create($Uri)
    $request.Method = "GET"
    $request.Timeout = $TimeoutMilliseconds
    $request.ReadWriteTimeout = $TimeoutMilliseconds

    try {
        $response = [System.Net.HttpWebResponse]$request.GetResponse()
        $statusCode = [int]$response.StatusCode
        $response.Close()
        return ($statusCode -ge 200 -and $statusCode -lt 500)
    }
    catch [System.Net.WebException] {
        $httpResponse = $_.Exception.Response
        if ($null -ne $httpResponse) {
            try {
                $statusCode = [int]$httpResponse.StatusCode
            }
            catch {
                return $false
            }
            finally {
                $httpResponse.Close()
            }
            return ($statusCode -ge 200 -and $statusCode -lt 500)
        }
        return $false
    }
}

function Wait-HttpReady {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Uri,

        [Parameter(Mandatory = $true)]
        [string]$Label,

        [Parameter(Mandatory = $true)]
        [object]$Entry,

        [Parameter(Mandatory = $true)]
        [string]$ErrorLogPath,

        [int]$TimeoutSeconds = 60
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-HttpReady -Uri $Uri) {
            return
        }

        if ($null -eq (Get-TrackedProcess -Entry $Entry)) {
            $logTail = Get-LogTail -Path $ErrorLogPath
            if ([string]::IsNullOrWhiteSpace($logTail)) {
                throw "$Label exited before it became ready."
            }
            throw "$Label exited before it became ready.`n$logTail"
        }

        Start-Sleep -Seconds 1
    }

    $tail = Get-LogTail -Path $ErrorLogPath
    if ([string]::IsNullOrWhiteSpace($tail)) {
        throw "$Label did not become ready within $TimeoutSeconds seconds."
    }
    throw "$Label did not become ready within $TimeoutSeconds seconds.`n$tail"
}

function New-ProcessEntry {
    param(
        [Parameter(Mandatory = $true)]
        [System.Diagnostics.Process]$Process,

        [Parameter(Mandatory = $true)]
        [string]$Url,

        [Parameter(Mandatory = $true)]
        [string]$StdoutLog,

        [Parameter(Mandatory = $true)]
        [string]$StderrLog
    )

    return [pscustomobject]@{
        pid        = $Process.Id
        start_time = $Process.StartTime.ToString("o")
        url        = $Url
        stdout_log = $StdoutLog
        stderr_log = $StderrLog
    }
}

function Start-RunnerProcess {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("backend", "frontend")]
        [string]$Target,

        [Parameter(Mandatory = $true)]
        [string]$StdoutLog,

        [Parameter(Mandatory = $true)]
        [string]$StderrLog,

        [string]$BackendHost = "127.0.0.1"
    )

    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", $RunnerPath,
        "-Target", $Target,
        "-RepoRoot", $RepoRoot,
        "-BackendPort", "$BackendPort",
        "-FrontendPort", "$FrontendPort",
        "-BackendHost", $BackendHost
    )

    return Start-Process `
        -FilePath "powershell.exe" `
        -ArgumentList $arguments `
        -WorkingDirectory $RepoRoot `
        -RedirectStandardOutput $StdoutLog `
        -RedirectStandardError $StderrLog `
        -PassThru
}

function Ensure-Qdrant {
    $legacyContainerId = docker ps -a --filter "name=^/ocp-rag-qdrant$" --format "{{.ID}}" | Select-Object -First 1
    if (-not [string]::IsNullOrWhiteSpace($legacyContainerId)) {
        $isRunning = (docker inspect -f "{{.State.Running}}" ocp-rag-qdrant).Trim()
        if ($isRunning -eq "true") {
            Write-Host "qdrant  : reusing legacy container ocp-rag-qdrant"
            return [pscustomobject]@{
                qdrant_url       = "http://127.0.0.1:6333"
                qdrant_mode      = "legacy_named"
                started_by_stack = $false
            }
        }

        docker start ocp-rag-qdrant | Out-Host
        Write-Host "qdrant  : started legacy container ocp-rag-qdrant"
        return [pscustomobject]@{
            qdrant_url       = "http://127.0.0.1:6333"
            qdrant_mode      = "legacy_named"
            started_by_stack = $true
        }
    }

    Push-Location -LiteralPath $RepoRoot
    try {
        docker compose up -d qdrant | Out-Host
    }
    finally {
        Pop-Location
    }

    return [pscustomobject]@{
        qdrant_url       = "http://127.0.0.1:6333"
        qdrant_mode      = "compose"
        started_by_stack = $true
    }
}

function Invoke-RunnerTarget {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("frontend-build")]
        [string]$Target
    )

    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", $RunnerPath,
        "-Target", $Target,
        "-RepoRoot", $RepoRoot,
        "-BackendPort", "$BackendPort",
        "-FrontendPort", "$FrontendPort"
    )

    & powershell.exe @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Runner target '$Target' failed with exit code $LASTEXITCODE."
    }
}

function Get-ShareUrls {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    try {
        $addresses = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction Stop |
            Where-Object {
                $_.IPAddress -ne "127.0.0.1" -and
                $_.IPAddress -notlike "169.254.*" -and
                $_.PrefixOrigin -ne "WellKnown"
            } |
            Select-Object -ExpandProperty IPAddress -Unique
    }
    catch {
        return @()
    }

    return @($addresses | ForEach-Object { "http://${_}:$Port" })
}

function Write-ServeSummary {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ModeName,

        [Parameter(Mandatory = $true)]
        [string]$BackendHost
    )

    Write-Host "PBS stack is ready."
    Write-Host "mode    : $ModeName"
    Write-Host "backend : http://127.0.0.1:$BackendPort"
    if ($BackendHost -eq "0.0.0.0") {
        foreach ($shareUrl in Get-ShareUrls -Port $BackendPort) {
            Write-Host "shared  : $shareUrl"
        }
    }
    if ($ModeName -eq "dev") {
        Write-Host "frontend: http://127.0.0.1:$FrontendPort"
    }
    Write-Host "qdrant  : http://127.0.0.1:6333"
    Write-Host "logs    : $StateDir"
    Write-Host "stop    : powershell -ExecutionPolicy Bypass -File scripts\\pbs-down.ps1"
}

if (-not (Test-Path -LiteralPath $RunnerPath)) {
    throw "Runner script not found: $RunnerPath"
}

Get-Command docker -ErrorAction Stop | Out-Null

$pythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Python virtualenv not found. Run 'python -m venv .venv' first."
}

$nodeModulesDir = Join-Path $RepoRoot "presentation-ui\node_modules"
if (-not (Test-Path -LiteralPath $nodeModulesDir)) {
    throw "presentation-ui dependencies are missing. Run 'cd presentation-ui; npm install' first."
}

Get-Command npm.cmd -ErrorAction Stop | Out-Null

New-Item -ItemType Directory -Force -Path $StateDir | Out-Null

$existingState = Read-StackState
$existingBackend = if ($existingState) { Get-TrackedProcess -Entry $existingState.backend } else { $null }
$existingFrontend = if ($existingState) { Get-TrackedProcess -Entry $existingState.frontend } else { $null }

if ($existingBackend -or $existingFrontend) {
    Write-Host "PBS stack is already running."
    if ($existingState.mode) {
        Write-Host "mode    : $($existingState.mode)"
    }
    if ($existingBackend) {
        Write-Host "backend : http://127.0.0.1:$BackendPort (pid $($existingBackend.Id))"
    }
    if ($existingFrontend) {
        Write-Host "frontend: http://127.0.0.1:$FrontendPort (pid $($existingFrontend.Id))"
    }
    Write-Host "stop    : powershell -ExecutionPolicy Bypass -File scripts\\pbs-down.ps1"
    exit 0
}

if (Test-Path -LiteralPath $StatePath) {
    Remove-Item -LiteralPath $StatePath -Force
}

$backendEntry = $null
$frontendEntry = $null

try {
    $infraState = Ensure-Qdrant

    if ($Mode -eq "serve") {
        Invoke-RunnerTarget -Target "frontend-build"
        if (-not (Test-Path -LiteralPath $FrontendDistDir)) {
            throw "frontend build completed without dist output: $FrontendDistDir"
        }
    }

    $backendHost = $ServeHost
    $backendProcess = Start-RunnerProcess `
        -Target "backend" `
        -StdoutLog $BackendStdout `
        -StderrLog $BackendStderr `
        -BackendHost $backendHost
    $backendEntry = New-ProcessEntry `
        -Process $backendProcess `
        -Url "http://127.0.0.1:$BackendPort" `
        -StdoutLog $BackendStdout `
        -StderrLog $BackendStderr
    Wait-HttpReady `
        -Uri "http://127.0.0.1:$BackendPort/api/health" `
        -Label "backend" `
        -Entry $backendEntry `
        -ErrorLogPath $BackendStderr `
        -TimeoutSeconds 120

    if ($Mode -eq "dev") {
        $frontendProcess = Start-RunnerProcess -Target "frontend" -StdoutLog $FrontendStdout -StderrLog $FrontendStderr
        $frontendEntry = New-ProcessEntry `
            -Process $frontendProcess `
            -Url "http://127.0.0.1:$FrontendPort" `
            -StdoutLog $FrontendStdout `
            -StderrLog $FrontendStderr
        Wait-HttpReady `
            -Uri "http://127.0.0.1:$FrontendPort" `
            -Label "frontend" `
            -Entry $frontendEntry `
            -ErrorLogPath $FrontendStderr
    }

    $state = [pscustomobject]@{
        started_at = (Get-Date).ToString("o")
        repo_root  = $RepoRoot
        mode       = $Mode
        backend    = $backendEntry
        frontend   = $frontendEntry
        infra      = $infraState
    }

    $state | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $StatePath -Encoding utf8

    Write-ServeSummary -ModeName $Mode -BackendHost $backendHost
}
catch {
    Stop-TrackedProcess -Entry $frontendEntry -Label "frontend"
    Stop-TrackedProcess -Entry $backendEntry -Label "backend"
    throw
}
