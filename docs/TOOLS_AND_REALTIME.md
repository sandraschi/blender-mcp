# Tools Overview, CRUD Gaps, and Realtime Control

## Portmanteau tools: what exists

| Area | Portmanteau? | What exists | CRUD? |
|------|--------------|-------------|-------|
| **Models (LLM)** | No (single tools) | `list_local_models` (discover Ollama + LM Studio), `generate_blender_script(prompt, model, ollama_url)` | List only. No pull/remove via MCP. |
| **Scripts** | No | `script_execute(code)` run in Blender; `generate_blender_script(prompt, ...)` generate via LLM | Execute + generate. No list/save/delete of stored scripts. |
| **Config** | No | `config_get`, `config_set` | Get/set only (in-memory). |
| **Status** | Yes | `blender_status(operation=status\|system_info\|health_check\|performance_monitor)` | Read-only. |
| **Scene, mesh, materials, etc.** | Yes | `blender_scene`, `blender_mesh`, `blender_materials`, … (operation-based) | Varies per tool. |

So: **no portmanteau for models CRUD** (only list). **No portmanteau for script CRUD** (execute + generate exist as separate tools; no stored script library). **Execute-in-Blender exists**: `script_execute(code)`.

---

## Is the MCP server useful?

Yes, but with limits.

- **Useful for:** Headless script runs, LLM-generated scripts (Ollama), status/health, config, scene/mesh/materials/export/validation/VR workflows via the existing portmanteau tools. Claude/Cursor can drive Blender without a GUI.
- **Limitation:** No **realtime** control. Each `script_execute` is a new Blender process; there is no live connection to a running Blender instance, so no streaming commands, no “sync viewport” or “select object now”.

So it’s useful for automation and batch-style workflows, not for interactive, realtime control of an open Blender session.

---

## Realtime control: not only CLI

We currently use **only the Blender CLI** (subprocess: `blender --background --python script.py`). Blender itself does **not** ship a built-in socket/API server, but **realtime control is possible via add-ons**:

1. **Blender Remote** (e.g. [igamenovoer/blender-remote](https://github.com/igamenovoer/blender-remote))  
   - Add-on in Blender + JSON-RPC (e.g. over TCP).  
   - Real-time control, optional MCP server (BLD_Remote_MCP).  
   - Background and GUI use.

2. **b3dnet** ([cgtinker/b3dnet](https://github.com/cgtinker/b3dnet))  
   - TCP to Blender for realtime apps.

3. **BlenderRemotify**  
   - Socket add-on; repo archived (Jan 2023).

So: **we only use the CLI today; there are add-ons that enable realtime control.** To get realtime in this project we’d need to:

- Integrate or require one of these add-ons (e.g. Blender Remote), and  
- Run a small “realtime bridge” in this repo that talks to the add-on (socket/JSON-RPC) and exposes MCP tools that send commands to the **running** Blender instance instead of starting a new process.

That would be an additional mechanism alongside the existing `script_execute` (CLI) path.

---

## Summary

| Question | Answer |
|----------|--------|
| Portmanteau for models CRUD? | No; only `list_local_models`. Can add `llm_models(operation=list\|pull\|remove)`. |
| Portmanteau for script CRUD? | No; we have `script_execute` and `generate_blender_script`, no stored-script list/save/delete. |
| Execute script in Blender tool? | Yes: `script_execute(code)`. |
| Is the MCP server useful? | Yes for automation and LLM-driven workflows; not for realtime control as implemented today. |
| Only Blender CLI? | Yes, in this repo: only CLI subprocess. |
| Blender plugins for realtime? | Yes: e.g. Blender Remote, b3dnet. We don’t use them yet; adding one would enable realtime control. |
