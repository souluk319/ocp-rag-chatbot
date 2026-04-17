[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Pattern,

    [Parameter(Position = 1)]
    [string[]]$Paths = @("src", "tests", "scripts", "presentation-ui/src"),

    [switch]$FixedStrings,

    [switch]$CaseSensitive
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $RepoRoot

function Write-StatusLine {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    [Console]::Error.WriteLine($Message)
}

function Resolve-SearchFiles {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Inputs
    )

    $files = New-Object System.Collections.Generic.List[string]
    foreach ($inputPath in $Inputs) {
        $candidate = Join-Path $RepoRoot $inputPath
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            $files.Add($candidate)
            continue
        }
        if (Test-Path -LiteralPath $candidate -PathType Container) {
            foreach ($file in Get-ChildItem -LiteralPath $candidate -Recurse -File -ErrorAction SilentlyContinue) {
                $files.Add($file.FullName)
            }
        }
    }
    return $files
}

function Write-SelectStringResults {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SearchPattern,

        [Parameter(Mandatory = $true)]
        [string[]]$SearchPaths
    )

    $files = Resolve-SearchFiles -Inputs $SearchPaths
    if ($files.Count -eq 0) {
        return $false
    }

    $matches = Select-String -Path $files -Pattern $SearchPattern -SimpleMatch:$FixedStrings -CaseSensitive:$CaseSensitive
    if (-not $matches) {
        return $false
    }

    foreach ($match in $matches) {
        $relativePath = Resolve-Path -LiteralPath $match.Path | ForEach-Object { $_.Path.Replace("$RepoRoot\", "") }
        [Console]::Out.WriteLine(("{0}:{1}:{2}" -f $relativePath, $match.LineNumber, $match.Line.TrimEnd()))
    }
    return $true
}

function Invoke-Rg {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$RgArguments
    )

    $candidateCommands = @(
        (Get-Command rg.cmd -ErrorAction SilentlyContinue),
        (Get-Command rg.exe -ErrorAction SilentlyContinue)
    ) | Where-Object { $null -ne $_ }

    foreach ($candidate in $candidateCommands) {
        try {
            $output = & $candidate.Source @RgArguments 2>$null
            if ($LASTEXITCODE -eq 0 -and $null -ne $output) {
                $output
            }
            return @{
                Invoked = $true
                ExitCode = $LASTEXITCODE
                Source = $candidate.Source
            }
        }
        catch {
            continue
        }
    }

    return @{
        Invoked = $false
        ExitCode = 2
        Source = ""
    }
}

$resolvedPaths = New-Object System.Collections.Generic.List[string]
$missingPaths = New-Object System.Collections.Generic.List[string]
foreach ($path in $Paths) {
    if ([string]::IsNullOrWhiteSpace($path)) {
        continue
    }
    $candidate = Join-Path $RepoRoot $path
    if (Test-Path -LiteralPath $candidate) {
        $resolvedPaths.Add($candidate)
    }
    else {
        $missingPaths.Add($path)
    }
}

if ($missingPaths.Count -gt 0) {
    $joined = [string]::Join(", ", $missingPaths)
    Write-StatusLine "[path-error] Missing search paths relative to repo root: $joined"
    exit 3
}

$arguments = @("--line-number", "--color", "never")
if ($FixedStrings) {
    $arguments += "--fixed-strings"
}
if ($CaseSensitive) {
    $arguments += "--case-sensitive"
}
$arguments += $Pattern
$arguments += $Paths

$rgResult = Invoke-Rg -RgArguments $arguments

if ($rgResult.Invoked) {
    $exitCode = [int]$rgResult.ExitCode
    if ($exitCode -eq 0) {
        exit 0
    }
    if ($exitCode -eq 1) {
        Write-StatusLine "[no-match] No results found for pattern '$Pattern'."
        exit 0
    }
}

Write-StatusLine "[rg-fallback] rg invocation was unavailable in this environment. Falling back to Select-String."
$fallbackMatched = Write-SelectStringResults -SearchPattern $Pattern -SearchPaths $Paths

if ($fallbackMatched) {
    exit 0
}
Write-StatusLine "[no-match] No results found for pattern '$Pattern'."
exit 0
