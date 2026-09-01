set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

__version__ := "0.6.0"
__name__ := "blender-mcp"

# --- Dashboard ---

# Open the interactive recipe dashboard in the browser
default:
    @just --list


# Synchronize deps, pre-commit hooks, and web frontend
bootstrap:
    uv sync --extra dev --group dev
    uv run pre-commit install
    Set-Location webapp/frontend; npm ci; if ($LASTEXITCODE -ne 0) { npm install }
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green
# --- Quality ---

# Execute repo-wide quality checks (Ruff + Biome)
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .
    cd webapp/frontend && npx @biomejs/biome check .

# Execute repo-wide auto-fixes and formatting (Ruff + Biome)
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .
    cd webapp/frontend && npx @biomejs/biome check --apply .
    cd webapp/frontend && npx @biomejs/biome format --write .

# --- Testing ---

# Run all Python tests with pytest
test:
    Set-Location '{{justfile_directory()}}'
    uv run pytest tests/ -v

e2e:
    powershell.exe -NoProfile -NoProfile -ExecutionPolicy Bypass -File "D:\Dev\repos\mcp-central-docs\scripts\playwright-audit.ps1" -RepoPath "{{justfile_directory()}}"

# --- Hardening ---

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check
# --- Packaging  Distribution ---

# mcpb-pack and cua-nsis-test are imported from scripts/just/fleet.just

# Serve for local stdio testing
serve:
    Set-Location '{{justfile_directory()}}'
    uv run blender-mcp-server

# --- Native App  Tauri 2 ---

# --- Build Tauri native desktop app  release  full pipeline ---
build-native:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    .\build.ps1

# Build Tauri native app (debug, skip PyInstaller)
build-native-debug:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    npx @tauri-apps/cli build --debug

# cua-nsis-test is imported from scripts/just/fleet.just

# --- SOTA Gates ---

# Format Python and JS/TS code
fmt:
    Set-Location '{{justfile_directory()}}'
    uv run ruff format .
    cd webapp/frontend && npx @biomejs/biome format --write .

# Run complete certification pipeline: lint + typecheck + test
certify: lint
    Write-Host "=== TypeScript typecheck ===" -ForegroundColor Yellow
    cd webapp/frontend && npx tsc --noEmit
    Write-Host "=== Python tests ===" -ForegroundColor Yellow
    uv run pytest tests/ -v
    Write-Host "=== Certification PASSED ===" -ForegroundColor Green


# Bootstrap: install dev deps + pre-commit hook

# Fleet depot — advertise this repo's depot to depot-mcp (vault is source, DB derivative)
# Auto-called from start.ps1 after backend healthy; run manually for stdio mode
advertise:
    powershell.exe -NoProfile -File "D:\Dev\repos\mcp-central-docs\scripts\advertise-depot.ps1" -DepotMcpUrl "http://127.0.0.1:10727"
