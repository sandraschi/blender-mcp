import { useState } from 'react'
import { Puzzle, Search, Download, ToggleLeft, ToggleRight, List, Info, Loader2, ExternalLink, RefreshCw } from 'lucide-react'
import { callTool } from '../api/mcp'

interface KnownAddon {
    name: string
    url: string
    description: string
}

interface InstalledAddon {
    module: string
    enabled: boolean
}

export default function AddonManagerPage() {
    const [knownResults, setKnownResults] = useState<KnownAddon[]>([])
    const [installed, setInstalled] = useState<InstalledAddon[]>([])
    const [searchQuery, setSearchQuery] = useState('')
    const [customUrl, setCustomUrl] = useState('')
    const [loading, setLoading] = useState(false)
    const [actionLoading, setActionLoading] = useState<string | null>(null)
    const [message, setMessage] = useState<{ text: string; ok: boolean } | null>(null)
    const [addonsDir, setAddonsDir] = useState<string>('')

    const msg = (text: string, ok = true) => setMessage({ text, ok })

    const searchKnown = async () => {
        setLoading(true)
        try {
            const res = await callTool<{ success: boolean; results?: KnownAddon[]; query?: string }>(
                'manage_blender_addons', { operation: 'search', query: searchQuery }
            )
            if (res.success && res.data?.results) {
                setKnownResults(res.data.results)
            } else {
                msg(res.error ?? 'Search failed', false)
            }
        } finally { setLoading(false) }
    }

    const getInfo = async () => {
        setLoading(true)
        try {
            const res = await callTool<{ success: boolean; known_addons?: KnownAddon[]; addons_directory?: string }>(
                'manage_blender_addons', { operation: 'info' }
            )
            if (res.success && res.data?.known_addons) {
                setKnownResults(res.data.known_addons)
                setAddonsDir(res.data.addons_directory ?? '')
            } else {
                msg(res.error ?? 'Info failed', false)
            }
        } finally { setLoading(false) }
    }

    const installKnown = async (name: string) => {
        setActionLoading(name)
        try {
            const res = await callTool<{ success: boolean; message?: string; error?: string }>(
                'manage_blender_addons', { operation: 'install_known', addon_name: name, enable_after: true }
            )
            if (res.data?.success) {
                msg(res.data.message ?? `Installed ${name}`)
            } else {
                msg(res.data?.error ?? res.error ?? `Install failed`, false)
            }
        } finally { setActionLoading(null) }
    }

    const installFromUrl = async () => {
        if (!customUrl) { msg('URL required', false); return }
        setLoading(true)
        try {
            const res = await callTool<{ success: boolean; message?: string; error?: string }>(
                'manage_blender_addons', { operation: 'install_url', url: customUrl, enable_after: true }
            )
            if (res.data?.success) {
                msg(res.data.message ?? 'Installed')
                setCustomUrl('')
            } else {
                msg(res.data?.error ?? res.error ?? 'Install failed', false)
            }
        } finally { setLoading(false) }
    }

    const listInstalled = async () => {
        setLoading(true)
        try {
            const res = await callTool<{ success: boolean; addons?: InstalledAddon[]; count?: number }>(
                'manage_blender_addons', { operation: 'list_installed' }
            )
            if (res.success && res.data?.addons) {
                setInstalled(res.data.addons)
                msg(`${res.data.count ?? res.data.addons.length} addons found`)
            } else {
                msg(res.error ?? 'List failed', false)
            }
        } finally { setLoading(false) }
    }

    const toggleAddon = async (module: string, enable: boolean) => {
        setActionLoading(module)
        try {
            const res = await callTool<{ success: boolean; message?: string; error?: string }>(
                'manage_blender_addons', { operation: enable ? 'enable' : 'disable', addon_name: module }
            )
            if (res.data?.success) {
                msg(res.data.message ?? `${enable ? 'Enabled' : 'Disabled'} ${module}`)
                setInstalled(prev => prev.map(a => a.module === module ? { ...a, enabled: enable } : a))
            } else {
                msg(res.data?.error ?? res.error ?? 'Toggle failed', false)
            }
        } finally { setActionLoading(null) }
    }

    return (
        <div className="p-6 max-w-6xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight mb-1 flex items-center gap-2">
                        <Puzzle className="w-6 h-6" /> Addon Manager
                    </h1>
                    <p className="text-muted-foreground text-sm">
                        Install and manage Blender addons. Required for Gaussian Splat / WorldLabs import.
                    </p>
                </div>
                <button onClick={getInfo} disabled={loading}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors">
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                    Load Registry
                </button>
            </div>

            {message && (
                <div className={`px-4 py-2 rounded-md text-sm font-medium ${message.ok ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                    {message.text}
                </div>
            )}

            {addonsDir && (
                <div className="px-4 py-2 rounded-md text-xs text-muted-foreground bg-muted/30 border border-border font-mono">
                    Addons directory: {addonsDir}
                </div>
            )}

            {/* WorldLabs callout */}
            <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4">
                <h3 className="font-semibold text-blue-400 mb-1 text-sm">WorldLabs / Gaussian Splat Setup</h3>
                <p className="text-xs text-muted-foreground mb-3">
                    To import <strong>.ply</strong> files from WorldLabs, you need a 3DGS Blender addon. 
                    Install <strong>gaussian_splat</strong> below, then use the Mesh/Collider/Splat page 
                    or call <code className="bg-muted px-1 rounded">blender_splatting(operation='worldlabs', file_path='...')</code>.
                </p>
                <button
                    onClick={() => installKnown('gaussian_splat')}
                    disabled={actionLoading === 'gaussian_splat'}
                    className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-md hover:bg-blue-500/30 transition-colors disabled:opacity-50">
                    {actionLoading === 'gaussian_splat' ? <Loader2 className="w-3 h-3 animate-spin" /> : <Download className="w-3 h-3" />}
                    Install gaussian_splat addon
                </button>
            </div>

            {/* Known addons */}
            <div className="bg-card border border-border rounded-lg p-5 space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="font-semibold flex items-center gap-2"><Search className="w-4 h-4" /> Known Addon Registry</h2>
                </div>
                <div className="flex gap-2">
                    <input
                        className="flex-1 px-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
                        placeholder='Search (e.g. "gaussian", "scatter", "gis")…'
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && searchKnown()}
                    />
                    <button onClick={searchKnown} disabled={loading}
                        className="px-4 py-2 text-sm font-medium bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors">
                        Search
                    </button>
                    <button onClick={getInfo} disabled={loading}
                        className="px-4 py-2 text-sm font-medium bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors">
                        Show All
                    </button>
                </div>

                {knownResults.length > 0 && (
                    <div className="space-y-2">
                        {knownResults.map(addon => (
                            <div key={addon.name} className="flex items-center justify-between gap-3 p-3 bg-background border border-border rounded-md">
                                <div className="min-w-0 flex-1">
                                    <div className="flex items-center gap-2">
                                        <span className="font-mono text-sm font-medium">{addon.name}</span>
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-0.5 truncate">{addon.description}</p>
                                    <a href={addon.url} target="_blank" rel="noreferrer"
                                        className="text-xs text-blue-400 hover:underline flex items-center gap-1 mt-0.5 truncate">
                                        <ExternalLink className="w-2.5 h-2.5 shrink-0" />
                                        {addon.url.replace('https://github.com/', '')}
                                    </a>
                                </div>
                                <button
                                    onClick={() => installKnown(addon.name)}
                                    disabled={actionLoading === addon.name}
                                    className="shrink-0 flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors">
                                    {actionLoading === addon.name ? <Loader2 className="w-3 h-3 animate-spin" /> : <Download className="w-3 h-3" />}
                                    Install
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Custom URL install */}
            <div className="bg-card border border-border rounded-lg p-5 space-y-3">
                <h2 className="font-semibold flex items-center gap-2"><Download className="w-4 h-4" /> Install from URL</h2>
                <p className="text-xs text-muted-foreground">ZIP archive or single .py file. GitHub archive URLs work directly.</p>
                <div className="flex gap-2">
                    <input
                        className="flex-1 px-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
                        placeholder="https://github.com/user/repo/archive/refs/heads/main.zip"
                        value={customUrl}
                        onChange={e => setCustomUrl(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && installFromUrl()}
                    />
                    <button onClick={installFromUrl} disabled={loading || !customUrl}
                        className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors">
                        Install
                    </button>
                </div>
            </div>

            {/* Installed addons */}
            <div className="bg-card border border-border rounded-lg p-5 space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="font-semibold flex items-center gap-2"><List className="w-4 h-4" /> Installed Addons</h2>
                    <button onClick={listInstalled} disabled={loading}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors">
                        <RefreshCw className="w-3 h-3" /> Load
                    </button>
                </div>

                {installed.length > 0 ? (
                    <div className="space-y-1 max-h-80 overflow-y-auto">
                        {installed.map(addon => (
                            <div key={addon.module} className="flex items-center justify-between px-3 py-2 bg-background border border-border rounded-md">
                                <span className="font-mono text-xs truncate flex-1">{addon.module}</span>
                                <button
                                    onClick={() => toggleAddon(addon.module, !addon.enabled)}
                                    disabled={actionLoading === addon.module}
                                    className={`ml-2 shrink-0 transition-colors ${addon.enabled ? 'text-green-400 hover:text-green-300' : 'text-muted-foreground hover:text-foreground'}`}
                                    title={addon.enabled ? 'Disable' : 'Enable'}>
                                    {actionLoading === addon.module
                                        ? <Loader2 className="w-4 h-4 animate-spin" />
                                        : addon.enabled ? <ToggleRight className="w-5 h-5" /> : <ToggleLeft className="w-5 h-5" />
                                    }
                                </button>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-6 text-muted-foreground">
                        <Info className="w-8 h-8 mx-auto mb-2 opacity-30" />
                        <p className="text-xs">Click <strong>Load</strong> to list addons from running Blender.</p>
                    </div>
                )}
            </div>
        </div>
    )
}
