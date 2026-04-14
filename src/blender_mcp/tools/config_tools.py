"""
Config get/set for webapp (Settings page). In-memory store; no persistence across restarts.
"""

import logging
from typing import Any

from blender_mcp.app import get_app

logger = logging.getLogger(__name__)

_config_store: dict[str, Any] = {}


def _register_config_tools():
    app = get_app()

    @app.tool
    async def config_get() -> str:
        """Return current webapp config (LLM provider, URLs, selected model, etc.)."""
        import json

        out = _config_store if _config_store else {}
        return json.dumps(out)

    @app.tool
    async def config_set(
        server_host: str | None = None,
        server_port: int | None = None,
        theme: str | None = None,
        auto_sync: bool | None = None,
        notifications: bool | None = None,
        llm: dict[str, Any] | None = None,
    ) -> str:
        """Update webapp config. Pass keys: server_host, server_port, theme, auto_sync, notifications, llm."""
        import json

        global _config_store
        updates = {
            k: v
            for k, v in {
                "server_host": server_host,
                "server_port": server_port,
                "theme": theme,
                "auto_sync": auto_sync,
                "notifications": notifications,
                "llm": llm,
            }.items()
            if v is not None
        }
        _config_store = {**_config_store, **updates}
        return json.dumps({"success": True, "message": "Config updated"})


_register_config_tools()
