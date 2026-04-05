/**
 * MCP API Client for Blender MCP WebApp
 * 
 * Connects to the FastMCP backend via HTTP/WebSocket
 * Base URL: /mcp (proxied to backend port, e.g. 10849)
 */

const API_BASE = '/mcp'

/**
 * Check if backend is reachable (does not use tool bridge).
 * Use to show a clear error when proxy or server is wrong.
 */
export async function getBackendHealth(): Promise<{ ok: boolean; error?: string }> {
    try {
        const r = await fetch(`${API_BASE}/api/v1/health`)
        if (!r.ok) return { ok: false, error: `HTTP ${r.status}` }
        return { ok: true }
    } catch (e) {
        return { ok: false, error: e instanceof Error ? e.message : 'Network error' }
    }
}

interface MCPRequest {
    tool: string
    params: Record<string, unknown>
}

interface MCPResponse<T = unknown> {
    success: boolean
    data?: T
    error?: string
    message?: string
}

/**
 * Call an MCP tool on the backend
 */
export async function callTool<T>(tool: string, params: Record<string, unknown> = {}): Promise<MCPResponse<T>> {
    try {
        const response = await fetch(`${API_BASE}/tool`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tool, params } as MCPRequest),
        })

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        return await response.json() as MCPResponse<T>
    } catch (error) {
        console.error(`MCP tool call failed: ${tool}`, error)
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error',
        }
    }
}

/**
 * Get server status and health (JSON format for webapp)
 */
export async function getStatus(): Promise<MCPResponse<{
    status: string
    blender: boolean
    version?: string
}>> {
    return callTool('blender_status', { operation: 'status', format: 'json' })
}

/**
 * Get scene hierarchy from Blender
 */
export async function getSceneData(): Promise<MCPResponse<{
    collections: Array<{
        name: string
        objects: Array<{
            name: string
            type: string
        }>
    }>
}>> {
    return callTool('scene_get_hierarchy')
}

/**
 * Send AI chat message
 */
export async function sendChatMessage(message: string): Promise<MCPResponse<{
    response: string
    actions?: string[]
}>> {
    return callTool('ai_chat', { message })
}

/**
 * Execute AI constructor command
 */
export async function executeAICommand(prompt: string): Promise<MCPResponse<{
    result: string
    objects_created?: string[]
}>> {
    return callTool('ai_constructor', { prompt })
}

/**
 * Get available materials
 */
export async function getMaterials(): Promise<MCPResponse<{
    materials: Array<{
        name: string
        category: string
        type: string
    }>
}>> {
    return callTool('materials_list')
}

/**
 * Apply material to object
 */
export async function applyMaterial(objectName: string, materialName: string): Promise<MCPResponse> {
    return callTool('material_apply', { object: objectName, material: materialName })
}

/**
 * Get system logs
 */
export async function getLogs(limit = 50): Promise<MCPResponse<{
    logs: Array<{
        timestamp: string
        level: string
        message: string
    }>
}>> {
    return callTool('blender_status', { operation: 'status', include_system_info: true, limit })
}

/**
 * Get server configuration
 */
export async function getConfig(): Promise<MCPResponse<Record<string, unknown>>> {
    return callTool('config_get')
}

/**
 * Update server configuration
 */
export async function updateConfig(config: Record<string, unknown>): Promise<MCPResponse> {
    return callTool('config_set', config)
}

/**
 * Execute Python script in Blender
 */
export async function executeScript(code: string): Promise<MCPResponse<{
    output: string
    success: boolean
}>> {
    return callTool('script_execute', { code })
}

/**
 * List local LLM models (Ollama and LM Studio) via backend.
 */
export async function listLocalModels(): Promise<MCPResponse<{
    ollama: string[]
    lm_studio: string[]
    errors?: string[]
}>> {
    const res = await callTool<{ success?: boolean; result?: { ollama?: string[]; lm_studio?: string[]; errors?: string[] }; summary?: string }>('list_local_models', {})
    if (!res.success || !res.data) return { success: false, error: res.error ?? 'No data' }
    const result = (res.data as { result?: { ollama?: string[]; lm_studio?: string[]; errors?: string[] } }).result
    if (!result) return { success: false, error: 'No result' }
    return {
        success: true,
        data: {
            ollama: result.ollama ?? [],
            lm_studio: result.lm_studio ?? [],
            errors: result.errors,
        },
    }
}

/** Addon management via manage_blender_addons tool */
export async function addonManage(operation: string, params: Record<string, unknown> = {}): Promise<MCPResponse> {
    return callTool('manage_blender_addons', { operation, ...params })
}

/** Legacy wrappers kept for backward compatibility — delegate to addonManage */
export async function addonsList(): Promise<MCPResponse> {
    return addonManage('list_installed')
}

export async function addonsInstallFromUrl(url: string, enableOnInstall = true): Promise<MCPResponse> {
    return addonManage('install_url', { url, enable_after: enableOnInstall })
}

export async function addonsSearch(query: string): Promise<MCPResponse> {
    return addonManage('search', { query })
}

/** Object repository operations */
export async function repositoryList(): Promise<MCPResponse> {
    return callTool('manage_object_repo', { operation: 'list_objects' })
}

export async function repositorySave(params: {
    object_name: string
    object_name_display?: string
    description?: string
    category?: string
    quality_rating?: number
    tags?: string[]
}): Promise<MCPResponse> {
    return callTool('manage_object_repo', { operation: 'save', ...params })
}

export async function repositoryLoad(params: {
    object_id: string
    position?: [number, number, number]
    scale?: [number, number, number]
    target_name?: string
}): Promise<MCPResponse> {
    return callTool('manage_object_repo', { operation: 'load', ...params })
}

export async function repositorySearch(params: {
    query?: string
    category?: string
    tags?: string[]
    min_quality?: number
    limit?: number
}): Promise<MCPResponse> {
    return callTool('manage_object_repo', { operation: 'search', ...params })
}

/** WorldLabs Gaussian Splat import (auto-installs addon if needed) */
export async function splatWorldlabs(filePath: string): Promise<MCPResponse> {
    return callTool('blender_splatting', { operation: 'worldlabs', file_path: filePath })
}

/** Import Gaussian splat file (requires 3DGS add-on installed). */
export async function splatImport(filePath: string): Promise<MCPResponse<{ output?: string }>> {
    return callTool('blender_splatting', { operation: 'import_gs', file_path: filePath })
}

/**
 * Generate a Blender Python script from a prompt using local LLM (Ollama).
 * Requires Ollama running with the chosen model (e.g. llama3.2).
 */
export async function generateBlenderScript(
    prompt: string,
    model: string = 'llama3.2',
    ollamaUrl: string = 'http://localhost:11434',
): Promise<MCPResponse<{ script: string; error?: string | null }>> {
    const res = await callTool<{ success?: boolean; script?: string; error?: string | null }>('generate_blender_script', {
        prompt,
        model,
        ollama_url: ollamaUrl,
    })
    if (!res.success) return { success: false, error: (res.data as { error?: string })?.error ?? res.error }
    const data = res.data as { script?: string; error?: string | null }
    return { success: true, data: { script: data?.script ?? '', error: data?.error ?? null } }
}

/**
 * Download a file from URL and import it into Blender.
 */
export async function downloadAndImport(url: string, importIntoScene: boolean = true): Promise<MCPResponse> {
    return callTool('blender_download', { operation: 'download', url, import_into_scene: importIntoScene })
}
