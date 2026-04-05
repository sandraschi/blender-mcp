import { useState } from 'react'
import { Box, Package, Layers, Download, Search, Plus, AlertCircle } from 'lucide-react'
import {
    addonsList,
    addonsInstallFromUrl,
    addonsSearch,
    downloadAndImport,
    splatImport,
    getBackendHealth,
} from '../api/mcp'

type TabId = 'mesh' | 'collider' | 'splat' | 'addons'

export default function MeshColliderSplat() {
    const [activeTab, setActiveTab] = useState<TabId>('mesh')
    const [meshUrl, setMeshUrl] = useState('')
    const [meshLoading, setMeshLoading] = useState(false)
    const [meshResult, setMeshResult] = useState<string | null>(null)
    const [splatPath, setSplatPath] = useState('')
    const [splatLoading, setSplatLoading] = useState(false)
    const [splatResult, setSplatResult] = useState<string | null>(null)
    const [addonUrl, setAddonUrl] = useState('')
    const [addonSearchQuery, setAddonSearchQuery] = useState('gaussian splat')
    const [addonSearchResults, setAddonSearchResults] = useState<Array<{ name: string; url: string; description: string }>>([])
    const [addonsInstalled, setAddonsInstalled] = useState<Array<{ name: string; enabled: boolean }>>([])
    const [addonsLoading, setAddonsLoading] = useState(false)
    const [addonInstallResult, setAddonInstallResult] = useState<string | null>(null)
    const [backendOk, setBackendOk] = useState<boolean | null>(null)

    const checkBackend = async () => {
        const r = await getBackendHealth()
        setBackendOk(r.ok)
    }

    const handleMeshDownload = async () => {
        if (!meshUrl.trim()) return
        setMeshLoading(true)
        setMeshResult(null)
        try {
            const res = await downloadAndImport(meshUrl.trim(), true)
            const msg = res.success && res.data != null
                ? (typeof res.data === 'object' && res.data && 'output' in res.data ? (res.data as { output?: string }).output : String(res.data))
                : res.error ?? 'Download/import failed'
            setMeshResult(msg ?? 'Done')
        } catch (e) {
            setMeshResult(e instanceof Error ? e.message : 'Error')
        } finally {
            setMeshLoading(false)
        }
    }

    const handleSplatImport = async () => {
        if (!splatPath.trim()) return
        setSplatLoading(true)
        setSplatResult(null)
        try {
            const res = await splatImport(splatPath.trim())
            const msg = res.success && res.data != null
                ? (typeof res.data === 'object' && res.data && 'output' in res.data ? (res.data as { output?: string }).output : String(res.data))
                : res.error ?? 'Import failed. Ensure a 3DGS add-on is installed.'
            setSplatResult(msg ?? 'Done')
        } catch (e) {
            setSplatResult(e instanceof Error ? e.message : 'Error')
        } finally {
            setSplatLoading(false)
        }
    }

    const handleAddonSearch = async () => {
        setAddonsLoading(true)
        setAddonSearchResults([])
        try {
            const res = await addonsSearch(addonSearchQuery)
            if (res.success && res.data) {
                const data = res.data as { results?: Array<{ name: string; url: string; description: string }> }
                if (data.results) setAddonSearchResults(data.results)
            }
        } finally {
            setAddonsLoading(false)
        }
    }

    const handleAddonInstallByUrl = async () => {
        if (!addonUrl.trim()) return
        setAddonInstallResult(null)
        const res = await addonsInstallFromUrl(addonUrl.trim(), true)
        const data = res.data as { status?: string; message?: string; error?: string } | undefined
        if (data?.status === 'SUCCESS') setAddonInstallResult(data.message ?? 'Installed')
        else setAddonInstallResult(data?.error ?? res.error ?? 'Install failed')
    }

    const loadAddonsList = async () => {
        setAddonsLoading(true)
        setAddonsInstalled([])
        try {
            const res = await addonsList()
            if (res.success && res.data) {
                const data = res.data as { addons?: Array<{ name: string; enabled: boolean }> }
                if (data.addons) setAddonsInstalled(data.addons)
            } else if (res.error) {
                setAddonInstallResult(res.error)
            }
        } finally {
            setAddonsLoading(false)
        }
    }

    const tabs: { id: TabId; label: string; icon: typeof Box }[] = [
        { id: 'mesh', label: 'Mesh', icon: Box },
        { id: 'collider', label: 'Collider', icon: Layers },
        { id: 'splat', label: 'Splat', icon: Package },
        { id: 'addons', label: 'Add-ons', icon: Plus },
    ]

    return (
        <div className="p-6 max-w-4xl space-y-6">
            <div className="flex items-center gap-2">
                <Package className="w-6 h-6 text-primary" />
                <h1 className="text-2xl font-semibold">Mesh / Collider / Splat</h1>
            </div>
            {backendOk === false && (
                <div className="flex items-center gap-2 p-3 rounded-lg bg-destructive/10 text-destructive">
                    <AlertCircle className="w-5 h-5" />
                    <span>Backend not reachable. Run webapp start script.</span>
                    <button type="button" onClick={checkBackend} className="ml-auto text-sm underline">Retry</button>
                </div>
            )}
            {backendOk === null && (
                <button type="button" onClick={checkBackend} className="text-sm text-muted-foreground underline">Check backend</button>
            )}

            <div className="flex gap-2 border-b border-border pb-2">
                {tabs.map(({ id, label, icon: Icon }) => (
                    <button
                        key={id}
                        type="button"
                        onClick={() => setActiveTab(id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${activeTab === id ? 'bg-accent text-accent-foreground' : 'text-muted-foreground hover:bg-accent/50'}`}
                    >
                        <Icon className="w-4 h-4" />
                        {label}
                    </button>
                ))}
            </div>

            {activeTab === 'mesh' && (
                <section className="space-y-4">
                    <h2 className="text-lg font-medium">Download & import mesh</h2>
                    <p className="text-sm text-muted-foreground">Enter a URL to an OBJ, FBX, GLB, STL, PLY, etc. File is downloaded and imported into Blender.</p>
                    <div className="flex gap-2">
                        <input
                            type="url"
                            placeholder="https://example.com/model.obj"
                            value={meshUrl}
                            onChange={e => setMeshUrl(e.target.value)}
                            className="flex-1 px-3 py-2 rounded-md border border-input bg-background"
                        />
                        <button
                            type="button"
                            onClick={handleMeshDownload}
                            disabled={meshLoading}
                            className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                        >
                            <Download className="w-4 h-4" />
                            {meshLoading ? 'Downloading…' : 'Download & import'}
                        </button>
                    </div>
                    {meshResult && <pre className="p-3 rounded-lg bg-muted text-sm overflow-auto">{meshResult}</pre>}
                </section>
            )}

            {activeTab === 'collider' && (
                <section className="space-y-4">
                    <h2 className="text-lg font-medium">Collider</h2>
                    <p className="text-sm text-muted-foreground">Create collision geometry from mesh or primitives. Use Construct or run a script (e.g. convex hull, box, sphere) via Script Console.</p>
                </section>
            )}

            {activeTab === 'splat' && (
                <section className="space-y-4">
                    <h2 className="text-lg font-medium">Gaussian splat import</h2>
                    <p className="text-sm text-muted-foreground">Import a 3DGS splat file (.ply or add-on format). Requires a Gaussian splat add-on (e.g. FastGS) installed via the Add-ons tab.</p>
                    <div className="flex gap-2">
                        <input
                            type="text"
                            placeholder="Path to .ply or splat file (local path on server)"
                            value={splatPath}
                            onChange={e => setSplatPath(e.target.value)}
                            className="flex-1 px-3 py-2 rounded-md border border-input bg-background"
                        />
                        <button
                            type="button"
                            onClick={handleSplatImport}
                            disabled={splatLoading}
                            className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                        >
                            {splatLoading ? 'Importing…' : 'Import splat'}
                        </button>
                    </div>
                    {splatResult && <pre className="p-3 rounded-lg bg-muted text-sm overflow-auto">{splatResult}</pre>}
                </section>
            )}

            {activeTab === 'addons' && (
                <section className="space-y-6">
                    <h2 className="text-lg font-medium">Add-ons</h2>
                    <p className="text-sm text-muted-foreground">Install add-ons from URL (ZIP or .py). For Gaussian splats, install FastGS or 3DGS add-on then enable in Blender Preferences.</p>

                    <div>
                        <h3 className="font-medium mb-2">Install from URL</h3>
                        <div className="flex gap-2">
                            <input
                                type="url"
                                placeholder="https://github.com/.../archive/refs/heads/main.zip"
                                value={addonUrl}
                                onChange={e => setAddonUrl(e.target.value)}
                                className="flex-1 px-3 py-2 rounded-md border border-input bg-background"
                            />
                            <button
                                type="button"
                                onClick={handleAddonInstallByUrl}
                                className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
                            >
                                <Download className="w-4 h-4" />
                                Install
                            </button>
                        </div>
                        {addonInstallResult && <p className="mt-2 text-sm text-muted-foreground">{addonInstallResult}</p>}
                    </div>

                    <div>
                        <h3 className="font-medium mb-2">Search known add-ons</h3>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={addonSearchQuery}
                                onChange={e => setAddonSearchQuery(e.target.value)}
                                placeholder="e.g. gaussian splat"
                                className="flex-1 px-3 py-2 rounded-md border border-input bg-background"
                            />
                            <button
                                type="button"
                                onClick={handleAddonSearch}
                                disabled={addonsLoading}
                                className="flex items-center gap-2 px-4 py-2 rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80"
                            >
                                <Search className="w-4 h-4" />
                                Search
                            </button>
                        </div>
                        {addonSearchResults.length > 0 && (
                            <ul className="mt-3 space-y-2">
                                {addonSearchResults.map((r) => (
                                    <li key={r.name} className="p-3 rounded-lg border border-border">
                                        <div className="font-medium">{r.name}</div>
                                        <div className="text-sm text-muted-foreground">{r.description}</div>
                                        <button
                                            type="button"
                                            onClick={() => { setAddonUrl(r.url); setAddonInstallResult(null); }}
                                            className="mt-2 text-sm text-primary hover:underline"
                                        >
                                            Use this URL
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>

                    <div>
                        <h3 className="font-medium mb-2">Installed add-ons (from Blender)</h3>
                        <button
                            type="button"
                            onClick={loadAddonsList}
                            disabled={addonsLoading}
                            className="px-4 py-2 rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80 disabled:opacity-50"
                        >
                            {addonsLoading ? 'Loading…' : 'List add-ons'}
                        </button>
                        {addonsInstalled.length > 0 && (
                            <ul className="mt-3 space-y-1 text-sm">
                                {addonsInstalled.map((a) => (
                                    <li key={a.name} className="flex items-center gap-2">
                                        <span>{a.name}</span>
                                        <span className={a.enabled ? 'text-green-600' : 'text-muted-foreground'}>{a.enabled ? 'enabled' : 'disabled'}</span>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                </section>
            )}
        </div>
    )
}
