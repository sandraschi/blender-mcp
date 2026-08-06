"""Tools for LLM discovery, model CRUD, and Blender script generation (Ollama/LM Studio)."""

import logging
import re
from typing import Any, Literal

import httpx

from blender_mcp.app import get_app

logger = logging.getLogger(__name__)

_READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
_MUTATING = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}
_DESTRUCTIVE = {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": False}
OLLAMA_DEFAULT = "http://localhost:11434"

BLENDER_SCRIPT_SYSTEM = """You are a Blender Python (bpy) expert. Output only a single, valid Python script. No markdown, no code fences, no explanation. Use only 'import bpy' and standard library. Script must create or modify the scene as requested. Start with import bpy."""


async def _ollama_generate(prompt: str, model: str, url: str = "http://localhost:11434", timeout: float = 120.0) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{url.rstrip('/')}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("response", "")


def _extract_code(text: str) -> str:
    text = text.strip()
    if "```" in text:
        match = re.search(r"```(?:python)?\s*([\s\S]*?)```", text)
        if match:
            return match.group(1).strip()
    return text


def _register_llm_tools():
    app = get_app()

    @app.tool(annotations=_READ_ONLY)
    async def list_local_models() -> dict[str, Any]:
        """Discover local LLM models from Ollama and LM Studio.

        ## Return Format
        Standard dict with keys: success, summary, result

        ## Examples
        ```python
        await call_tool("list_local_models")
        ```
        """
        models = {"ollama": [], "lm_studio": [], "errors": []}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags", timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                    models["ollama"] = [m["name"] for m in data.get("models", [])]
        except Exception as e:
            err_msg = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
            logger.debug(f"Ollama discovery failed: {err_msg}")
            models["errors"].append(f"Ollama: {err_msg}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:1234/v1/models", timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                    models["lm_studio"] = [m["id"] for m in data.get("data", [])]
        except Exception as e:
            err_msg = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
            logger.debug(f"LM Studio discovery failed: {err_msg}")
            models["errors"].append(f"LM Studio: {err_msg}")
        return {
            "success": True,
            "operation": "list_local_models",
            "summary": f"Discovered {len(models['ollama'])} Ollama and {len(models['lm_studio'])} LM Studio models",
            "result": models,
        }

    @app.tool(annotations=_MUTATING)
    async def generate_blender_script(
        prompt: str,
        model: str = "llama3.2",
        ollama_url: str = "http://localhost:11434",
    ) -> dict:
        """Generate a Blender Python script from a natural language prompt using a local LLM (Ollama).

        ## Return Format
        Standard dict with keys: success, script, error

        ## Examples
        ```python
        await call_tool("generate_blender_script", {"prompt": "create a cube at origin", "model": "llama3.2"})
        ```
        """
        if not prompt or not prompt.strip():
            return {"success": False, "script": "", "error": "Empty prompt"}
        full_prompt = f"{BLENDER_SCRIPT_SYSTEM}\n\nUser request: {prompt.strip()}"
        try:
            out = await _ollama_generate(full_prompt, model=model, url=ollama_url)
            script = _extract_code(out)
            if not script.startswith("import bpy"):
                script = "import bpy\n\n" + script
            return {"success": True, "script": script, "error": None}
        except Exception as e:
            logger.exception("generate_blender_script failed")
            err_msg = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
            return {"success": False, "script": "", "error": err_msg}

    @app.tool(annotations=_MUTATING)
    async def llm_models(
        operation: Literal["list", "pull", "remove"] = "list",
        model_name: str | None = None,
        ollama_url: str = OLLAMA_DEFAULT,
    ) -> dict:
        """
        Portmanteau: list, pull, or remove Ollama models (CRUD for local LLM models).

        Operations:
        - list: return installed Ollama model names (and LM Studio if reachable).
        - pull: pull model from Ollama registry (requires model_name). Slow for large models.
        - remove: delete an Ollama model from disk (requires model_name).

        Args:
            operation: list, pull, or remove
            model_name: required for pull and remove (e.g. llama3.2, codellama)
            ollama_url: Ollama API base URL

        Returns:
            Dict with success, summary, result (list of names) or error.

        ## Return Format
        Standard dict with keys: success, summary, result

        ## Examples
        ```python
        await call_tool("llm_models", {"operation": "list"})
        ```
        """
        base = ollama_url.rstrip("/")
        if operation in ("pull", "remove") and not (model_name and model_name.strip()):
            return {"success": False, "summary": "model_name required for pull/remove", "result": []}
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                if operation == "list":
                    r = await client.get(f"{base}/api/tags")
                    r.raise_for_status()
                    data = r.json()
                    names = [m.get("name", m.get("model", "")) for m in data.get("models", [])]
                    return {"success": True, "summary": f"Found {len(names)} Ollama models", "result": names}
                if operation == "pull":
                    r = await client.post(f"{base}/api/pull", json={"name": model_name.strip()})
                    r.raise_for_status()
                    return {"success": True, "summary": f"Pull started for {model_name}", "result": [model_name]}
                if operation == "remove":
                    r = await client.delete(f"{base}/api/delete", json={"name": model_name.strip()})
                    r.raise_for_status()
                    return {"success": True, "summary": f"Removed {model_name}", "result": []}
        except Exception as e:
            logger.warning("llm_models %s failed: %s", operation, e)
            err_msg = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
            return {"success": False, "summary": err_msg, "result": []}
        return {"success": False, "summary": f"Unknown operation: {operation}", "result": []}


_register_llm_tools()
