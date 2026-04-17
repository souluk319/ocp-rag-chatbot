[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("backend", "frontend", "frontend-build")]
    [string]$Target,

    [string]$RepoRoot = "",

    [int]$BackendPort = 8765,

    [int]$FrontendPort = 5173,

    [string]$BackendHost = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
}

Set-Location -LiteralPath $RepoRoot

if ($Target -eq "backend") {
    $pythonPath = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $pythonPath)) {
        throw "Python virtualenv not found: $pythonPath"
    }

    $srcPath = Join-Path $RepoRoot "src"
    if ([string]::IsNullOrWhiteSpace($env:PYTHONPATH)) {
        $env:PYTHONPATH = $srcPath
    }
    else {
        $env:PYTHONPATH = "$srcPath;$($env:PYTHONPATH)"
    }

    & $pythonPath -m play_book_studio.cli ui --no-browser --host $BackendHost --port $BackendPort
    exit $LASTEXITCODE
}

$uiDir = Join-Path $RepoRoot "presentation-ui"
if (-not (Test-Path -LiteralPath (Join-Path $uiDir "node_modules"))) {
    throw "presentation-ui dependencies are missing. Run 'cd presentation-ui; npm install' first."
}

Get-Command npm.cmd -ErrorAction Stop | Out-Null
Set-Location -LiteralPath $uiDir

if ($Target -eq "frontend-build") {
    & npm.cmd run build
    exit $LASTEXITCODE
}

& npm.cmd run dev -- --host 127.0.0.1 --port $FrontendPort --strictPort
exit $LASTEXITCODE
