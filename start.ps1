Param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$NoBrowser,
    [switch]$ReuseIfRunning
)

# --- SOTA Headless Standard 2026 ---
if ($Headless -and ($Host.Name -ne 'ConsoleHost' -or -not (Get-Variable -Name "NoRelaunch" -ErrorAction SilentlyContinue))) {
    $argList = @("-File", $PSCommandPath, "-NoRelaunch")
    if ($BackendOnly) { $argList += "-BackendOnly" }
    $argList += "-NoBrowser"
    Start-Process pwsh.exe -ArgumentList $argList -WindowStyle Hidden
    exit
}
# -----------------------------------

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
$WebPort = 10848
$BackendPort = 10849

$FleetStartPath = Join-Path $RepoRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath

Write-Host "=== blender-mcp Industrial Startup ===" -ForegroundColor Cyan

$portResolve = @{
    Ports      = @($WebPort, $BackendPort)
    Label      = "blender-mcp"
    AllowReuse = $ReuseIfRunning
}
if ($ReuseIfRunning) {
    $portResolve.HealthChecks = @{
        $BackendPort = "http://127.0.0.1:$BackendPort/api/v1/health"
        $WebPort     = "http://127.0.0.1:$WebPort/"
    }
}
$portState = Resolve-FleetPortConflict @portResolve
if ($portState.Action -eq 'Blocked') { exit 1 }
if ($portState.Reuse) {
    if (-not $NoBrowser -and -not $BackendOnly) {
        Start-Process "http://127.0.0.1:$WebPort/"
    }
    return
}

if ($env:SKIP_SYNC -eq "1") {
    Write-Host "[1/3] Skipping Python deps (SKIP_SYNC=1)" -ForegroundColor DarkGray
} else {
    Write-Host "[1/3] Syncing Python deps (uv sync) ..." -ForegroundColor Cyan
    Set-Location $RepoRoot
    uv sync
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

Write-Host "[2/3] Starting Backend (port $BackendPort) ..." -ForegroundColor Cyan
$backendProc = Start-Process uv -ArgumentList "run", "uvicorn", "blender_mcp.server:asgi_app", "--host", "127.0.0.1", "--port", "$BackendPort" `
    -WorkingDirectory $RepoRoot `
    -PassThru -NoNewWindow
Write-Host "  [ok] Backend PID: $($backendProc.Id)" -ForegroundColor DarkGreen

$healthUrl = "http://127.0.0.1:$BackendPort/api/v1/health"
$backendReady = $false
for ($i = 0; $i -lt 90; $i++) {
    try {
        $r = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $backendReady = $true; break }
    } catch {}
    if ($backendProc.HasExited) {
        Write-Host "ERROR: Backend exited before health check passed." -ForegroundColor Red
        exit 1
    }
    Start-Sleep -Seconds 1
}
if (-not $backendReady) {
    Write-Host "ERROR: Backend not healthy at $healthUrl within 90s." -ForegroundColor Red
    exit 1
}
Write-Host "  [ok] Backend healthy at $healthUrl" -ForegroundColor DarkGreen

if ($BackendOnly) {
    Write-Host "Backend-only mode active. Press Ctrl+C to exit." -ForegroundColor Yellow
    Wait-Process -Id $backendProc.Id
    exit
}

Write-Host "[3/3] Starting Frontend (webapp/frontend) ..." -ForegroundColor Cyan
$FrontendDir = Join-Path $RepoRoot "webapp\frontend"
if (Test-Path $FrontendDir) {
    Set-Location $FrontendDir
    if (-not (Test-Path "node_modules")) { npm install }
    Start-Process npm -ArgumentList "run", "dev", "--", "--port", "$WebPort", "--host" -WorkingDirectory $FrontendDir
}

Write-Host "Startup Complete." -ForegroundColor Green
if (-not $NoBrowser) {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:$WebPort/"
}

try {
    while ($true) {
        Start-Sleep -Seconds 5
        if ($backendProc.HasExited) { Write-Host "Backend exited!" -ForegroundColor Red; break }
    }
} finally {
    if ($backendProc -and -not $backendProc.HasExited) {
        Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
    }
}
