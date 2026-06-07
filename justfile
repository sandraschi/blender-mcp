set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

__version__ := "0.6.0"
__name__ := "blender-mcp"

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# ── Quality ───────────────────────────────────────────────────────────────────

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

# ── Testing ───────────────────────────────────────────────────────────────────

# Run all Python tests with pytest
test:
    Set-Location '{{justfile_directory()}}'
    uv run pytest tests/ -v

e2e:
    pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "D:\Dev\repos\mcp-central-docs\scripts\playwright-audit.ps1" -RepoPath "{{justfile_directory()}}"

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check
# ── Packaging & Distribution ──────────────────────────────────────────────────

# Bundle for Claude Desktop (MCPB)
mcpb-pack:
    Set-Location '{{justfile_directory()}}'
    mcpb pack . dist/blender-mcp-v{{__version__}}.mcpb

# Serve for local stdio testing
serve:
    Set-Location '{{justfile_directory()}}'
    uv run blender-mcp-server

# ── Native App (Tauri 2.0) ──────────────────────────────────────────────────

# Build Tauri native desktop app (release — full pipeline)
build-native:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    .\build.ps1

# Build Tauri native app (debug, skip PyInstaller)
build-native-debug:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    npx @tauri-apps/cli build --debug

