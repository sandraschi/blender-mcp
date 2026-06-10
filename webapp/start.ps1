Param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$NoBrowser
)

# webapp/start.ps1 — delegate to repo-root industrial launcher (uv sync, uv run, health-safe).
$RepoRoot = Split-Path -Parent $PSScriptRoot
$RootStart = Join-Path $RepoRoot "start.ps1"

if (-not (Test-Path -LiteralPath $RootStart)) {
    Write-Host "ERROR: Missing $RootStart" -ForegroundColor Red
    exit 1
}

$argList = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $RootStart)
if ($Headless) { $argList += "-Headless" }
if ($BackendOnly) { $argList += "-BackendOnly" }
if ($NoBrowser) { $argList += "-NoBrowser" }

& powershell.exe @argList
exit $LASTEXITCODE
