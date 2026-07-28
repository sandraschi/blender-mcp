import { Activity, Clock, Cpu, RefreshCw, Server, Wifi } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { getStatus } from "../api/mcp";

export default function Status() {
  const [status, setStatus] = useState<{
    operational: boolean;
    version: string;
  }>({ operational: false, version: "-" });
  const [loading, setLoading] = useState(false);
  const [pingMs, setPingMs] = useState<number | null>(null);

  const loadStatus = useCallback(async () => {
    setLoading(true);
    const start = performance.now();
    try {
      const res = await getStatus();
      const elapsed = Math.round(performance.now() - start);
      setPingMs(elapsed);
      if (res.success && res.data) {
        setStatus({
          operational: res.data.blender ?? true,
          version: res.data.version || "1.0.0",
        });
      }
    } catch {
      setPingMs(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 10000);
    return () => clearInterval(interval);
  }, [loadStatus]);

  return (
    <div className="p-6 max-w-6xl mx-auto" data-testid="status-page">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight mb-1">System Status</h1>
          <p className="text-muted-foreground">Server health and connectivity.</p>
        </div>
        <button
          type="button"
          onClick={loadStatus}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 text-sm bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 bg-card border border-border rounded-lg">
          <div className="flex items-center gap-3 mb-2">
            <div className={`p-2 rounded-md ${status.operational ? "bg-green-500/10" : "bg-red-500/10"}`}>
              <Activity className={`w-5 h-5 ${status.operational ? "text-green-500" : "text-red-500"}`} />
            </div>
            <span className="font-medium text-muted-foreground">Status</span>
          </div>
          <div className="text-2xl font-bold">{status.operational ? "Operational" : "Offline"}</div>
          <div className={`text-sm mt-1 ${status.operational ? "text-green-500" : "text-red-500"}`}>
            {status.operational ? "Connected" : "Not Connected"}
          </div>
        </div>

        <div className="p-4 bg-card border border-border rounded-lg">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-500/10 rounded-md">
              <Server className="w-5 h-5 text-blue-500" />
            </div>
            <span className="font-medium text-muted-foreground">Server</span>
          </div>
          <div className="text-2xl font-bold">blender-mcp</div>
          <div className="text-sm text-muted-foreground mt-1">v{status.version}</div>
        </div>

        <div className="p-4 bg-card border border-border rounded-lg">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500/10 rounded-md">
              <Clock className="w-5 h-5 text-purple-500" />
            </div>
            <span className="font-medium text-muted-foreground">Latency</span>
          </div>
          <div className="text-2xl font-bold">{pingMs !== null ? `${pingMs} ms` : "---"}</div>
          <div className="text-sm text-muted-foreground mt-1">API round-trip</div>
        </div>

        <div className="p-4 bg-card border border-border rounded-lg">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-orange-500/10 rounded-md">
              <Wifi className="w-5 h-5 text-orange-500" />
            </div>
            <span className="font-medium text-muted-foreground">Blender</span>
          </div>
          <div className={`text-2xl font-bold ${status.operational ? "text-green-500" : "text-yellow-500"}`}>
            {status.operational ? "Connected" : "Disconnected"}
          </div>
          <div className="text-sm text-muted-foreground mt-1">Blender 4.2+</div>
        </div>
      </div>

      <div className="mt-8 p-6 bg-card border border-border rounded-lg">
        <div className="flex items-center gap-2 mb-1">
          <Cpu className="w-4 h-4 text-muted-foreground" />
          <h3 className="font-medium">Diagnostics</h3>
        </div>
        <p className="text-sm text-muted-foreground mt-2">
          For detailed server logs with filtering, search, and export, visit the{" "}
          <a href="/logs" className="text-primary hover:underline">
            Logs page
          </a>
          .
        </p>
      </div>
    </div>
  );
}
