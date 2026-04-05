"""
Config get/set for webapp (Settings page). In-memory store; no persistence across restarts.
"""

import logging
from typing import Any, Dict, Optional

from blender_mcp.app import get_app

logger = logging.getLogger(__name__)

_config_store: Dict[str, Any] = {}


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
        server_host: Optional[str] = None,
        server_port: Optional[int] = None,
        theme: Optional[str] = None,
        auto_sync: Optional[bool] = None,
        notifications: Optional[bool] = None,
        llm: Optional[Dict[str, Any]] = None,
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
