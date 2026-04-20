Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Webapp Start - Standardized SOTA (Auto-Repaired V2.5)
$WebPort = 10848
$BackendPort = 10849
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 1. Kill any process squatting on the ports
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Setup frontend (package.json lives in frontend/)
$FrontendRoot = Join-Path $PSScriptRoot "frontend"
Set-Location $FrontendRoot
if (-not (Test-Path "node_modules")) { npm install }

# 3. Start the Python backend (Background)
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan

$PythonPath = "python"
# 1. Try local virtualenv
if (Test-Path "$ProjectRoot\.venv\Scripts\python.exe") {
    $PythonPath = "$ProjectRoot\.venv\Scripts\python.exe"
}
# 2. Try fully qualified path provided by user (C:\Users\sandr\AppData\Local\Programs\Python\Python313\python.exe)
elseif (Test-Path "C:\Users\sandr\AppData\Local\Programs\Python\Python313\python.exe") {
    $PythonPath = "C:\Users\sandr\AppData\Local\Programs\Python\Python313\python.exe"
}

Write-Host "Using Python: $PythonPath" -ForegroundColor Gray

# Use absolute path to uvicorn if possible, otherwise run via module
$BackendCmd = "Set-Location '$PSScriptRoot'; `$env:PYTHONPATH = '$ProjectRoot\src'; & '$PythonPath' -m uvicorn blender_mcp.server:asgi_app --host 127.0.0.1 --port $BackendPort --log-level info"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendCmd -WindowStyle Normal

# 4. Run Vite dev server from frontend directory
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green
Set-Location $FrontendRoot

# 4b. Launch background task to open browser once frontend is ready (Auto-opened by Antigravity)
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
npm run dev -- --port $WebPort --host




