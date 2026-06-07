Param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$NoBrowser

# Fast port helpers (scripts/PortHelpers.ps1)
Param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$NoBrowser
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

Write-Host "=== blender-mcp Industrial Startup ===" -ForegroundColor Cyan

# 1. Kill stale
$WebPort = 10848
$BackendPort = 10849
foreach ($p in @($WebPort, $BackendPort)) {
    $procIds = Get-PortListenerPidsFast -Port $port
    foreach ($c in $conns) {
        try { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
    }
}

# 2. Python deps
if ($env:SKIP_SYNC -eq "1") {
    Write-Host "[1/3] Skipping Python deps (SKIP_SYNC=1)" -ForegroundColor DarkGray
} else {
    Write-Host "[1/3] Syncing Python deps (uv sync) ..." -ForegroundColor Cyan
    Set-Location $RepoRoot
    uv sync
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

# 3. Start Backend
Write-Host "[2/3] Starting Backend (port $BackendPort) ..." -ForegroundColor Cyan
$backendProc = Start-Process uv -ArgumentList "run", "uvicorn", "blender_mcp.server:asgi_app", "--host", "127.0.0.1", "--port", "$BackendPort" `
    -WorkingDirectory $RepoRoot `
    -PassThru -NoNewWindow
Write-Host "  [ok] Backend PID: $($backendProc.Id)" -ForegroundColor DarkGreen

if ($BackendOnly) {
    Write-Host "Backend-only mode active. Press Ctrl+C to exit." -ForegroundColor Yellow
    Wait-Process -Id $backendProc.Id
    exit
}

# 4. Start Frontend
Write-Host "[3/3] Starting Frontend (webapp/frontend) ..." -ForegroundColor Cyan
$FrontendDir = Join-Path $RepoRoot "webapp\frontend"
if (Test-Path $FrontendDir) {
    Set-Location $FrontendDir
    if (-not (Test-Path "node_modules")) { npm install }
    Start-Process npm -ArgumentList "run", "dev", "--", "--port", "$WebPort", "--host" -WorkingDirectory $FrontendDir
}

Write-Host "Startup Complete." -ForegroundColor Green
if (-not $NoBrowser) {
    # Wait a bit for Vite
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:$WebPort"
}

# Keep alive
try {
    while ($true) {
        Start-Sleep -Seconds 5
        if ($backendProc.HasExited) { Write-Host "Backend exited!" -ForegroundColor Red; break }
    }
} finally {
    if ($backendProc -and -not $backendProc.HasExited) {
        Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
    }
}_PortHelpers = Join-Path $PSScriptRoot 'scripts\PortHelpers.ps1'
if (Test-Path -LiteralPath Param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$NoBrowser
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

Write-Host "=== blender-mcp Industrial Startup ===" -ForegroundColor Cyan

# 1. Kill stale
$WebPort = 10848
$BackendPort = 10849
foreach ($p in @($WebPort, $BackendPort)) {
    $procIds = Get-PortListenerPidsFast -Port $port
    foreach ($c in $conns) {
        try { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
    }
}

# 2. Python deps
if ($env:SKIP_SYNC -eq "1") {
    Write-Host "[1/3] Skipping Python deps (SKIP_SYNC=1)" -ForegroundColor DarkGray
} else {
    Write-Host "[1/3] Syncing Python deps (uv sync) ..." -ForegroundColor Cyan
    Set-Location $RepoRoot
    uv sync
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

# 3. Start Backend
Write-Host "[2/3] Starting Backend (port $BackendPort) ..." -ForegroundColor Cyan
$backendProc = Start-Process uv -ArgumentList "run", "uvicorn", "blender_mcp.server:asgi_app", "--host", "127.0.0.1", "--port", "$BackendPort" `
    -WorkingDirectory $RepoRoot `
    -PassThru -NoNewWindow
Write-Host "  [ok] Backend PID: $($backendProc.Id)" -ForegroundColor DarkGreen

if ($BackendOnly) {
    Write-Host "Backend-only mode active. Press Ctrl+C to exit." -ForegroundColor Yellow
    Wait-Process -Id $backendProc.Id
    exit
}

# 4. Start Frontend
Write-Host "[3/3] Starting Frontend (webapp/frontend) ..." -ForegroundColor Cyan
$FrontendDir = Join-Path $RepoRoot "webapp\frontend"
if (Test-Path $FrontendDir) {
    Set-Location $FrontendDir
    if (-not (Test-Path "node_modules")) { npm install }
    Start-Process npm -ArgumentList "run", "dev", "--", "--port", "$WebPort", "--host" -WorkingDirectory $FrontendDir
}

Write-Host "Startup Complete." -ForegroundColor Green
if (-not $NoBrowser) {
    # Wait a bit for Vite
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:$WebPort"
}

# Keep alive
try {
    while ($true) {
        Start-Sleep -Seconds 5
        if ($backendProc.HasExited) { Write-Host "Backend exited!" -ForegroundColor Red; break }
    }
} finally {
    if ($backendProc -and -not $backendProc.HasExited) {
        Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
    }
}_PortHelpers) { . Param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$NoBrowser
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

Write-Host "=== blender-mcp Industrial Startup ===" -ForegroundColor Cyan

# 1. Kill stale
$WebPort = 10848
$BackendPort = 10849
foreach ($p in @($WebPort, $BackendPort)) {
    $procIds = Get-PortListenerPidsFast -Port $port
    foreach ($c in $conns) {
        try { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
    }
}

# 2. Python deps
if ($env:SKIP_SYNC -eq "1") {
    Write-Host "[1/3] Skipping Python deps (SKIP_SYNC=1)" -ForegroundColor DarkGray
} else {
    Write-Host "[1/3] Syncing Python deps (uv sync) ..." -ForegroundColor Cyan
    Set-Location $RepoRoot
    uv sync
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

# 3. Start Backend
Write-Host "[2/3] Starting Backend (port $BackendPort) ..." -ForegroundColor Cyan
$backendProc = Start-Process uv -ArgumentList "run", "uvicorn", "blender_mcp.server:asgi_app", "--host", "127.0.0.1", "--port", "$BackendPort" `
    -WorkingDirectory $RepoRoot `
    -PassThru -NoNewWindow
Write-Host "  [ok] Backend PID: $($backendProc.Id)" -ForegroundColor DarkGreen

if ($BackendOnly) {
    Write-Host "Backend-only mode active. Press Ctrl+C to exit." -ForegroundColor Yellow
    Wait-Process -Id $backendProc.Id
    exit
}

# 4. Start Frontend
Write-Host "[3/3] Starting Frontend (webapp/frontend) ..." -ForegroundColor Cyan
$FrontendDir = Join-Path $RepoRoot "webapp\frontend"
if (Test-Path $FrontendDir) {
    Set-Location $FrontendDir
    if (-not (Test-Path "node_modules")) { npm install }
    Start-Process npm -ArgumentList "run", "dev", "--", "--port", "$WebPort", "--host" -WorkingDirectory $FrontendDir
}

Write-Host "Startup Complete." -ForegroundColor Green
if (-not $NoBrowser) {
    # Wait a bit for Vite
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:$WebPort"
}

# Keep alive
try {
    while ($true) {
        Start-Sleep -Seconds 5
        if ($backendProc.HasExited) { Write-Host "Backend exited!" -ForegroundColor Red; break }
    }
} finally {
    if ($backendProc -and -not $backendProc.HasExited) {
        Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
    }
}_PortHelpers }
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

Write-Host "=== blender-mcp Industrial Startup ===" -ForegroundColor Cyan

# 1. Kill stale
$WebPort = 10848
$BackendPort = 10849
foreach ($p in @($WebPort, $BackendPort)) {
    $procIds = Get-PortListenerPidsFast -Port $port
    foreach ($c in $conns) {
        try { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
    }
}

# 2. Python deps
if ($env:SKIP_SYNC -eq "1") {
    Write-Host "[1/3] Skipping Python deps (SKIP_SYNC=1)" -ForegroundColor DarkGray
} else {
    Write-Host "[1/3] Syncing Python deps (uv sync) ..." -ForegroundColor Cyan
    Set-Location $RepoRoot
    uv sync
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

# 3. Start Backend
Write-Host "[2/3] Starting Backend (port $BackendPort) ..." -ForegroundColor Cyan
$backendProc = Start-Process uv -ArgumentList "run", "uvicorn", "blender_mcp.server:asgi_app", "--host", "127.0.0.1", "--port", "$BackendPort" `
    -WorkingDirectory $RepoRoot `
    -PassThru -NoNewWindow
Write-Host "  [ok] Backend PID: $($backendProc.Id)" -ForegroundColor DarkGreen

if ($BackendOnly) {
    Write-Host "Backend-only mode active. Press Ctrl+C to exit." -ForegroundColor Yellow
    Wait-Process -Id $backendProc.Id
    exit
}

# 4. Start Frontend
Write-Host "[3/3] Starting Frontend (webapp/frontend) ..." -ForegroundColor Cyan
$FrontendDir = Join-Path $RepoRoot "webapp\frontend"
if (Test-Path $FrontendDir) {
    Set-Location $FrontendDir
    if (-not (Test-Path "node_modules")) { npm install }
    Start-Process npm -ArgumentList "run", "dev", "--", "--port", "$WebPort", "--host" -WorkingDirectory $FrontendDir
}

Write-Host "Startup Complete." -ForegroundColor Green
if (-not $NoBrowser) {
    # Wait a bit for Vite
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:$WebPort"
}

# Keep alive
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
