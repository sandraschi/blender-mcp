# blender-mcp — AI-Powered Blender Automation

AI-Powered Automation - Control Blender with natural language through MCP.

## Commands
- **Dev Server**: `uv run python run_server.py`
- **Tests**: `uv run pytest`
- **Linting**: `uv run ruff check .`
- **Formatting**: `uv run ruff format .`
- **Type Check**: `uv run mypy src`

## Architecture
- `src/blender_mcp/server.py`: Core FastMCP server definition.
- `src/blender_mcp/handlers/`: Context-specific tool handlers (scene, object, render, etc.).
- `src/blender_mcp/utils/`: Path resolution and Blender integration utilities.
- `webapp/`: (If present) Dashboard for fleet visibility.

## Code Style & Standards
- Follow the **Portmanteau Pattern** for tool handlers.
- All tools must be `async` with comprehensive docstrings.
- Mandatory type hints for all function signatures.
- See `D:\Dev\repos\mcp-central-docs\standards\rules\mcp_registration.md` for tool registration rules.
