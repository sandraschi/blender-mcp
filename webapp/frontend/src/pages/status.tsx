import { useState, useEffect } from 'react'
import { Activity, Server, Clock, Shield, Terminal, RefreshCw } from 'lucide-react'
import { getStatus, getLogs } from '../api/mcp'

export default function Status() {
    const [logs, setLogs] = useState<Array<{ time: string, level: string, msg: string }>>([])
    const [status, setStatus] = useState<{
        operational: boolean
        memory: string
        latency: number
        version: string
    }>({
        operational: false,
        memory: '-',
        latency: 0,
        version: '-'
    })
    const [loading, setLoading] = useState(false)

    const loadStatus = async () => {
        setLoading(true)
        try {
            const [statusRes, logsRes] = await Promise.all([getStatus(), getLogs(50)])
            
            if (statusRes.success && statusRes.data) {
                setStatus({
                    operational: statusRes.data.blender,
                    memory: '2.4 GB', // Would come from backend
                    latency: 12, // Would come from backend
                    version: statusRes.data.version || '1.0.0'
                })
            }

            // Transform logs if available
            if (logsRes.success && logsRes.data?.logs) {
                setLogs(logsRes.data.logs.map(log => ({
                    time: new Date(log.timestamp).toLocaleTimeString(),
                    level: log.level,
                    msg: log.message
                })))
            }
        } catch (err) {
            console.error('Failed to load status:', err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        loadStatus()
        const interval = setInterval(loadStatus, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="p-6 max-w-6xl mx-auto">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight mb-1">System Status</h1>
                    <p className="text-muted-foreground">Monitor server health and logs.</p>
                </div>
                <button
                    onClick={loadStatus}
                    disabled={loading}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
                >
                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <div className="p-4 bg-card border border-border rounded-lg shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <div className={`p-2 rounded-md ${status.operational ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                            <Activity className={`w-5 h-5 ${status.operational ? 'text-green-500' : 'text-red-500'}`} />
                        </div>
                        <span className="font-medium text-muted-foreground">Status</span>
                    </div>
                    <div className="text-2xl font-bold">{status.operational ? 'Operational' : 'Offline'}</div>
                    <div className={`text-xs mt-1 ${status.operational ? 'text-green-500' : 'text-red-500'}`}>
                        {status.operational ? 'Connected' : 'Not Connected'}
                    </div>
                </div>

                <div className="p-4 bg-card border border-border rounded-lg shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-blue-500/10 rounded-md">
                            <Server className="w-5 h-5 text-blue-500" />
                        </div>
                        <span className="font-medium text-muted-foreground">Memory</span>
                    </div>
                    <div className="text-2xl font-bold">{status.memory}</div>
                    <div className="text-xs text-muted-foreground mt-1">/ 64 GB Total</div>
                </div>

                <div className="p-4 bg-card border border-border rounded-lg shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-purple-500/10 rounded-md">
                            <Clock className="w-5 h-5 text-purple-500" />
                        </div>
                        <span className="font-medium text-muted-foreground">Latency</span>
                    </div>
                    <div className="text-2xl font-bold">{status.latency} ms</div>
                    <div className="text-xs text-muted-foreground mt-1">Localhost</div>
                </div>

                <div className="p-4 bg-card border border-border rounded-lg shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-orange-500/10 rounded-md">
                            <Shield className="w-5 h-5 text-orange-500" />
                        </div>
                        <span className="font-medium text-muted-foreground">Version</span>
                    </div>
                    <div className="text-2xl font-bold">v{status.version}</div>
                    <div className="text-xs text-muted-foreground mt-1">Blender 4.2+</div>
                </div>
            </div>

            <div className="bg-card border border-border rounded-lg shadow-sm overflow-hidden flex flex-col h-[400px]">
                <div className="p-4 border-b border-border bg-muted/30 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Terminal className="w-4 h-4 text-muted-foreground" />
                        <h3 className="font-medium">System Logs</h3>
                    </div>
                    <div className="flex gap-2">
                        <button className="text-xs px-2 py-1 bg-background border border-border rounded hover:bg-accent">Clear</button>
                        <button className="text-xs px-2 py-1 bg-background border border-border rounded hover:bg-accent">Download</button>
                    </div>
                </div>
                <div className="flex-1 p-4 overflow-y-auto font-mono text-sm space-y-2 bg-[#0d1117]">
                    {logs.map((log, i) => (
                        <div key={i} className="flex gap-3">
                            <span className="text-muted-foreground opacity-50 shrink-0 select-none">{log.time}</span>
                            <span className={`shrink-0 w-12 font-bold ${log.level === 'INFO' ? 'text-blue-400' :
                                    log.level === 'WARN' ? 'text-yellow-400' :
                                        log.level === 'ERROR' ? 'text-red-400' :
                                            'text-gray-400'
                                }`}>{log.level}</span>
                            <span className="text-gray-300 break-all">{log.msg}</span>
                        </div>
                    ))}
                    <div className="flex gap-3 animate-pulse">
                        <span className="text-muted-foreground opacity-50 shrink-0">10:44:05</span>
                        <span className="shrink-0 w-12 font-bold text-gray-500">...</span>
                        <span className="text-gray-500">Listening for events...</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
