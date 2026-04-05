# How Blender "Connection" Works

There is **no persistent connection** to Blender. No socket, no add-on, no live Blender instance.

## Mechanism: Subprocess per script

1. **Webapp** calls backend tool `script_execute` with `{ code: "..." }`.
2. **Backend** (`BlenderExecutor`) writes the script to a temp file and runs:
   - `blender --background --factory-startup --python <temp_script.py>`
3. Blender starts, runs the script, exits. Stdout/stderr are captured and returned.
4. Temp file is deleted.

So every "Execute in Blender" = **spawn a new Blender process**, run the script, **process exits**. No shared state, no live UI.

## Requirements

- **Blender installed** and on PATH, or set **`BLENDER_EXECUTABLE`** (env or config) to the full path to `blender` (or `blender.exe` on Windows).
- **validate_blender_executable()** must pass (see `src/blender_mcp/config.py`). If it fails, status shows "Blender not found" and script execution returns an error.

## Why it can feel "nonfunctional"

- Blender not found → all script runs fail.
- Script errors (e.g. missing add-on like `primitive_solid_add` for dodecahedron) → Blender exits non-zero, error message in output.
- No live connection → you cannot "sync" a running Blender UI; each run is a fresh headless run.

## Optional: GUI mode

`BlenderExecutor(headless=False)` would start Blender with GUI for that run; the webapp uses headless by default so scripts run without opening a window.

---

## LLM script generation (Construct page)

- **Ollama** is used to generate Blender scripts from natural language (e.g. "Make a chair").
- **Settings > LLM Provider**: choose Ollama, set URL (default `http://localhost:11434`), click **Refresh** to list models, then **Load** a model (e.g. `llama3.2`).
- **Construct**: "Generate Script" calls the backend tool `generate_blender_script(prompt, model, ollama_url)`; the selected model in Settings is used. If no model is selected, `llama3.2` is used. Ollama must be running and the model must be pulled (e.g. `ollama pull llama3.2`).
- Model list comes from the same backend via `list_local_models` (Ollama `/api/tags` and LM Studio `/v1/models`). No separate "bridge" on port 8000; the webapp talks only to the Blender MCP backend (port 10849 by default).
