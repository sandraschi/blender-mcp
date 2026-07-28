import { Activity, Box, Cpu, FileCode2, LayoutDashboard, RefreshCw, Server, Terminal, Wrench } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { getBackendHealth, getDiagnostics, getStatus } from "../api/mcp";
import { useTauri } from "../hooks/useTauri";

const RETRY_DELAYS = [1, 2, 4, 8, 16];

function retryDelay(attempt: number): number {
  return attempt < RETRY_DELAYS.length ? RETRY_DELAYS[attempt] : 30;
}

export default function Dashboard() {
  const { isTauri, listen, invoke } = useTauri();
  const [health, setHealth] = useState<{
    ok: boolean;
    error?: string;
    version?: string;
    toolCount?: number;
  } | null>(null);
  const [status, setStatus] = useState<{
    blender: boolean;
    version?: string;
    ollama?: boolean;
  } | null>(null);
  const [restarting, setRestarting] = useState(false);
  const [attempt, setAttempt] = useState(0);

  const refresh = useCallback(async () => {
    const h = await getBackendHealth();
    setHealth({
      ok: h.ok,
      error: h.error,
      version: h.data?.version,
      toolCount: h.data?.tool_count,
    });
    if (h.ok) {
      const s = await getStatus();
      if (s.success && s.data) {
        setStatus(s.data);
      }
      const diag = await getDiagnostics();
      if (diag) {
        setHealth((prev) => (prev ? { ...prev, toolCount: diag.server.tool_count } : prev));
      }
    }
  }, []);

  // Exponential backoff polling
  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!health || health.ok) return;
    const timer = setTimeout(() => {
      setAttempt((a) => a + 1);
      void refresh();
    }, retryDelay(attempt) * 1000);
    return () => clearTimeout(timer);
  }, [health, attempt, refresh]);

  // Additionally listen for Tauri backend-status event for instant updates
  useEffect(() => {
    let unlisten: (() => void) | null = null;
    (async () => {
      unlisten = await listen<string>("backend-status", (payload) => {
        if (payload === "ready") {
          setAttempt(0);
          setRestarting(false);
          refresh();
        } else if (typeof payload === "string" && payload.startsWith("error:")) {
          setHealth({ ok: false, error: payload.replace("error:", "").trim() });
          setRestarting(false);
        }
      });
    })();
    return () => {
      if (unlisten) unlisten();
    };
  }, [listen, refresh]);

  const restartBackend = useCallback(async () => {
    setRestarting(true);
    const result = await invoke("start_backend");
    if (result === null && !isTauri) {
      setRestarting(false);
    }
  }, [invoke, isTauri]);

  return (
    <div className="p-6 max-w-6xl mx-auto" data-testid="dashboard">
      {/* Hero */}
      <div className="mb-10 bg-gradient-to-br from-indigo-500/10 via-purple-500/5 to-transparent border border-indigo-500/20 rounded-2xl p-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2.5 bg-indigo-500/20 rounded-xl">
            <Box className="w-7 h-7 text-indigo-400" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Blender MCP</h1>
        </div>
        <p className="text-lg text-muted-foreground max-w-2xl mb-3">
          An AI-agent bridge for Blender. Connect Claude, Cursor, or any MCP client directly to your Blender session —
          create objects, manage materials, run scripts, render scenes, and automate your 3D pipeline through natural
          language.
        </p>
        <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
          <span className="px-3 py-1 bg-white/5 rounded-full border border-white/10">MCP Protocol</span>
          <span className="px-3 py-1 bg-white/5 rounded-full border border-white/10">Blender 4.2+</span>
          <span className="px-3 py-1 bg-white/5 rounded-full border border-white/10">Python Scripting</span>
          <span className="px-3 py-1 bg-white/5 rounded-full border border-white/10">AI Agent Integration</span>
        </div>
      </div>

      {/* Status cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div
          className={`p-4 bg-card border rounded-lg shadow-sm ${!health?.ok && health !== null ? "border-red-500/30" : "border-border"}`}
          data-testid="kpi-server"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className={`p-2 rounded-md ${health?.ok ? "bg-green-500/10" : "bg-red-500/10"}`}>
              <Server className={`w-5 h-5 ${health?.ok ? "text-green-500" : "text-red-500"}`} />
            </div>
            <span className="font-medium text-muted-foreground">Backend</span>
          </div>
          <div className="text-2xl font-bold">{health?.ok ? "Connected" : health === null ? "..." : "Offline"}</div>
          <div className="text-sm text-muted-foreground mt-1">
            {health?.ok ? "Port 10849" : health?.error ? `Error: ${health.error}` : "Port 10849"}
          </div>
          <div className="flex items-center gap-1.5 mt-2 text-sm text-muted-foreground" data-testid="backend-dot">
            <span
              className={`relative flex h-2.5 w-2.5 ${!health?.ok && health !== null ? "bg-red-500" : health?.ok ? "bg-emerald-500" : "bg-gray-500"} rounded-full`}
            >
              {health?.ok && (
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              )}
            </span>
            <span>
              {!health?.ok && health !== null ? "Reconnecting..." : health?.ok ? "Connected" : "Connecting..."}
            </span>
          </div>
          {!health?.ok && health !== null && (
            <button
              type="button"
              onClick={restartBackend}
              disabled={restarting}
              className="mt-3 flex items-center gap-2 px-3 py-1.5 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${restarting ? "animate-spin" : ""}`} />
              {restarting ? "Restarting..." : "Restart Backend"}
            </button>
          )}
        </div>

        <div className="p-4 bg-card border border-border rounded-lg shadow-sm" data-testid="kpi-blender">
          <div className="flex items-center gap-3 mb-2">
            <div className={`p-2 rounded-md ${status?.blender ? "bg-green-500/10" : "bg-amber-500/10"}`}>
              <Cpu className={`w-5 h-5 ${status?.blender ? "text-green-500" : "text-amber-500"}`} />
            </div>
            <span className="font-medium text-muted-foreground">Blender</span>
          </div>
          <div className="text-2xl font-bold">
            {status === null ? "..." : status.blender ? "Connected" : "Not running"}
          </div>
          <div className="text-sm text-muted-foreground mt-1">v{status?.version ?? "-"}</div>
        </div>

        <div className="p-4 bg-card border border-border rounded-lg shadow-sm" data-testid="kpi-tools">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-500/10 rounded-md">
              <Wrench className="w-5 h-5 text-blue-500" />
            </div>
            <span className="font-medium text-muted-foreground">Tools</span>
          </div>
          <div className="text-2xl font-bold">{health?.toolCount ?? "..."}</div>
          <div className="text-sm text-muted-foreground mt-1">MCP tools registered</div>
        </div>

        <div className="p-4 bg-card border border-border rounded-lg shadow-sm" data-testid="kpi-ollama">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500/10 rounded-md">
              <LayoutDashboard className="w-5 h-5 text-purple-500" />
            </div>
            <span className="font-medium text-muted-foreground">Ollama</span>
          </div>
          <div className="text-2xl font-bold">{status?.ollama ? "Reachable" : "Off / unreachable"}</div>
          <div className="text-sm text-muted-foreground mt-1">Local LLM generation</div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        {[
          { href: "/scene", label: "Scene Explorer", icon: Box, color: "text-emerald-400" },
          { href: "/chat", label: "AI Chat", icon: FileCode2, color: "text-indigo-400" },
          { href: "/scripts", label: "Script Console", icon: Terminal, color: "text-amber-400" },
          { href: "/status", label: "Status & Logs", icon: Activity, color: "text-rose-400" },
        ].map((item) => (
          <a
            key={item.href}
            href={item.href}
            className="flex items-center gap-3 p-4 bg-card border border-border rounded-lg hover:bg-accent/50 transition-colors"
          >
            <item.icon className={`w-5 h-5 ${item.color}`} />
            <span className="font-medium">{item.label}</span>
          </a>
        ))}
      </div>

      {/* How it works */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-lg font-bold mb-4">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold">
              1
            </div>
            <h3 className="font-semibold">AI Agent Talks to Blender</h3>
            <p className="text-sm text-muted-foreground">
              Claude, Cursor, or any MCP client sends natural language requests to the Blender MCP server via stdio or
              HTTP.
            </p>
          </div>
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center text-purple-400 font-bold">
              2
            </div>
            <h3 className="font-semibold">Tools Execute in Blender</h3>
            <p className="text-sm text-muted-foreground">
              The server translates requests into Blender Python API calls — creating, modifying, or inspecting your 3D
              scene in real time.
            </p>
          </div>
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold">
              3
            </div>
            <h3 className="font-semibold">Results Stream Back</h3>
            <p className="text-sm text-muted-foreground">
              Results, logs, and scene data stream back to the AI agent or this dashboard — no manual switching between
              tools.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
