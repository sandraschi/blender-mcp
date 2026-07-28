import { AlertTriangle, Download, Filter, Info, RefreshCw, Search, Terminal, XCircle } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { getLogsREST } from "../api/mcp";

type LogLevel = "ALL" | "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";

interface LogEntry {
  timestamp: string;
  level: string;
  name: string;
  function: string;
  line: number;
  message: string;
}

const LEVELS: LogLevel[] = ["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];

const LEVEL_COLORS: Record<string, string> = {
  DEBUG: "text-gray-400",
  INFO: "text-blue-400",
  WARNING: "text-yellow-400",
  ERROR: "text-red-400",
  CRITICAL: "text-red-500 font-bold",
};

const LEVEL_BG: Record<string, string> = {
  DEBUG: "bg-gray-500/10",
  INFO: "bg-blue-500/10",
  WARNING: "bg-yellow-500/10",
  ERROR: "bg-red-500/10",
  CRITICAL: "bg-red-500/20",
};

const TIME_PRESETS = [
  { label: "5 min", value: 5 },
  { label: "15 min", value: 15 },
  { label: "1 hour", value: 60 },
  { label: "6 hours", value: 360 },
  { label: "24 hours", value: 1440 },
];

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [levelFilter, setLevelFilter] = useState<LogLevel>("ALL");
  const [searchFilter, setSearchFilter] = useState("");
  const [moduleFilter, setModuleFilter] = useState("");
  const [sinceMinutes, setSinceMinutes] = useState<number>(60);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [tail, setTail] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getLogsREST({
        level: levelFilter === "ALL" ? undefined : levelFilter,
        search: searchFilter || undefined,
        module: moduleFilter || undefined,
        since_minutes: sinceMinutes,
        limit: 500,
      });
      if (res.success && res.data) {
        const entries = (res.data as { logs: LogEntry[] }).logs ?? [];
        setLogs(entries);
      }
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }, [levelFilter, searchFilter, moduleFilter, sinceMinutes]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, [autoRefresh, fetchLogs]);

  useEffect(() => {
    if (tail && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [tail]);

  const exportLogs = (format: "json" | "csv") => {
    const data =
      format === "json"
        ? JSON.stringify(logs, null, 2)
        : [
            "timestamp,level,name,message",
            ...logs.map((l) => `${l.timestamp},${l.level},"${l.name}","${l.message.replace(/"/g, '""')}"`),
          ].join("\n");
    const blob = new Blob([data], { type: format === "json" ? "application/json" : "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `blender-mcp-logs.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const levelIcon = (level: string) => {
    if (level === "ERROR" || level === "CRITICAL") return <XCircle className="w-3.5 h-3.5" />;
    if (level === "WARNING") return <AlertTriangle className="w-3.5 h-3.5" />;
    return <Info className="w-3.5 h-3.5" />;
  };

  return (
    <div className="p-6 max-w-6xl mx-auto h-[calc(100vh-4rem)] flex flex-col" data-testid="logs-page">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight mb-1 flex items-center gap-2">
            <Terminal className="w-6 h-6 text-purple-400" />
            Logs
          </h1>
          <p className="text-muted-foreground">Server logs with filtering, search, and export.</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => exportLogs("json")}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            JSON
          </button>
          <button
            type="button"
            onClick={() => exportLogs("csv")}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            CSV
          </button>
          <button
            type="button"
            onClick={fetchLogs}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-card border border-border rounded-lg p-3 mb-4 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1">
          <Filter className="w-3.5 h-3.5 text-muted-foreground" />
          <span className="text-sm text-muted-foreground font-medium">Level:</span>
          <div className="flex gap-1">
            {LEVELS.map((lvl) => (
              <button
                key={lvl}
                type="button"
                onClick={() => setLevelFilter(lvl)}
                className={`text-sm px-2 py-0.5 rounded font-medium transition-colors ${
                  levelFilter === lvl
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:text-foreground"
                }`}
              >
                {lvl}
              </button>
            ))}
          </div>
        </div>

        <div className="w-px h-5 bg-border" />

        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground font-medium">Time:</span>
          <div className="flex gap-1">
            {TIME_PRESETS.map((preset) => (
              <button
                key={preset.value}
                type="button"
                onClick={() => setSinceMinutes(preset.value)}
                className={`text-sm px-2 py-0.5 rounded font-medium transition-colors ${
                  sinceMinutes === preset.value
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:text-foreground"
                }`}
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        <div className="w-px h-5 bg-border" />

        <div className="relative flex-1 min-w-[160px] max-w-xs">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            placeholder="Search messages..."
            className="w-full pl-8 pr-2 py-1 text-sm bg-background border border-input rounded focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>

        <div className="relative flex-1 min-w-[120px] max-w-[200px]">
          <input
            type="text"
            value={moduleFilter}
            onChange={(e) => setModuleFilter(e.target.value)}
            placeholder="Module filter..."
            className="w-full pl-2 pr-2 py-1 text-sm bg-background border border-input rounded focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>

        <div className="flex items-center gap-3 ml-auto">
          <label className="flex items-center gap-1.5 text-sm text-muted-foreground cursor-pointer select-none">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-border bg-background"
            />
            Auto-refresh
          </label>
          <label className="flex items-center gap-1.5 text-sm text-muted-foreground cursor-pointer select-none">
            <input
              type="checkbox"
              checked={tail}
              onChange={(e) => setTail(e.target.checked)}
              className="rounded border-border bg-background"
            />
            Tail
          </label>
        </div>
      </div>

      {/* Log list */}
      <div
        ref={scrollRef}
        className="flex-1 bg-[#0d1117] border border-border rounded-lg overflow-y-auto font-mono text-sm"
      >
        {logs.length === 0 && !loading && (
          <div className="h-full flex items-center justify-center text-muted-foreground text-sm">
            No logs match the current filters.
          </div>
        )}
        {logs.length === 0 && loading && (
          <div className="h-full flex items-center justify-center text-muted-foreground text-sm">Loading logs...</div>
        )}
        <div className="p-3 space-y-0.5">
          {logs.map((log, i) => (
            <div
              key={`${log.timestamp}-${i}`}
              className={`flex gap-2 px-2 py-1 rounded hover:bg-white/[0.03] transition-colors ${LEVEL_BG[log.level] ?? ""}`}
            >
              <span className="text-muted-foreground/50 shrink-0 text-[11px] leading-5 select-none w-[80px]">
                {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : ""}
              </span>
              <span
                className={`shrink-0 flex items-center gap-1 w-[80px] text-[11px] leading-5 ${LEVEL_COLORS[log.level] ?? "text-gray-400"}`}
              >
                {levelIcon(log.level)}
                {log.level}
              </span>
              <span
                className="text-muted-foreground/50 shrink-0 text-[11px] leading-5 hidden lg:inline w-auto max-w-[200px] truncate"
                title={log.name}
              >
                {log.name}
              </span>
              <span className="text-gray-300 leading-5 break-all flex-1 min-w-0">{log.message}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer bar */}
      <div className="flex items-center justify-between mt-2 text-sm text-muted-foreground">
        <span>{logs.length} log entries</span>
        <span className="text-muted-foreground/50">
          {autoRefresh ? "Auto-refreshing every 5s" : "Auto-refresh off"}
        </span>
      </div>
    </div>
  );
}
