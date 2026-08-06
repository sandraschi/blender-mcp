"""AI chat tool for Blender MCP — reads blender-expert SKILL.md as system context."""

import logging
from pathlib import Path

try:
    from fastmcp import Context
except ImportError:
    from typing import Any as Context

logger = logging.getLogger(__name__)

_READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
_MUTATING = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}
_DESTRUCTIVE = {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": False}
SKILL_PATH = Path(__file__).resolve().parent.parent.parent.parent / "skills" / "blender-expert" / "SKILL.md"


def _load_skill_context() -> str:
    """Load the blender-expert SKILL.md content as system context."""
    try:
        if SKILL_PATH.exists():
            return SKILL_PATH.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning("Failed to load SKILL.md: %s", e)
    return "You are a Blender MCP assistant. Help users with 3D modeling, animation, rendering, and Blender automation."


def _register_chat_tools():
    from blender_mcp.app import get_app

    app = get_app()

    @app.tool(annotations=_READ_ONLY)
    async def ai_chat(ctx: Context, message: str) -> dict:
        """Chat with the Blender AI assistant. Provides natural-language help with Blender operations.

        Uses the blender-expert SKILL.md as system context so the LLM knows available tools
        and workflows. Uses ctx.sample() when the host supports sampling; falls back to Ollama.

        Args:
            message: The user's chat message.

        ## Return Format
        Standard dict with keys: success, message, data

        ## Examples
        ```python
        await call_tool("ai_chat", {"message": "How do I create a cube?"})
        ```
        """
        if not message or not message.strip():
            return {"success": False, "data": {"response": "Please provide a message."}}

        system_ctx = _load_skill_context()
        try:
            result = await ctx.sample(
                content=f"{system_ctx}\n\nUser: {message.strip()}",
                metadata={"type": "chat", "topic": "blender"},
                max_tokens=8192,
                temperature=0.5,
            )
            return {"success": True, "data": {"response": result.content, "actions": []}}
        except Exception as e:
            logger.debug("ctx.sample not available (%s), falling back to Ollama", e)

        try:
            import httpx

            system_prompt = f"You are a Blender expert. Use this context:\n\n{system_ctx}\n\nRespond helpfully."
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.2",
                        "prompt": f"{system_prompt}\n\nUser: {message.strip()}",
                        "stream": False,
                    },
                    timeout=60.0,
                )
                r.raise_for_status()
                data = r.json()
                return {"success": True, "data": {"response": data.get("response", ""), "actions": []}}
        except Exception as e2:
            logger.error("ai_chat fallback failed: %s", e2)
            return {
                "success": True,
                "data": {
                    "response": (
                        "I can help with Blender operations. Try using the Construct tool to generate "
                        "scripts, or use the sidebar tools for specific operations like modeling, "
                        "materials, animation, and rendering."
                    ),
                    "actions": ["/construct", "/materials", "/scene"],
                },
            }


_register_chat_tools()
