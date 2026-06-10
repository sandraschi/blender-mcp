@echo off
REM Hard restart blender-mcp
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0webapp\stop.ps1"
if errorlevel 1 (
    echo stop failed
    pause
    exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0webapp\start.ps1"
pause
