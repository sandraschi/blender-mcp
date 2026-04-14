import { AlertCircle, ChevronDown, ChevronRight, File, Folder, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { getBackendHealth, getSceneData, getStatus } from "../api/mcp";

interface SceneNode {
  name: string;
  type: "COLLECTION" | "OBJECT";
  children?: SceneNode[];
}

export default function SceneExplorer() {
  const [sceneData, setSceneData] = useState<SceneNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSceneData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const health = await getBackendHealth();
      if (!health.ok) {
        setConnected(false);
        setError(
          `Backend unreachable: ${health.error}. Run webapp\\start.ps1 and ensure Python server is on port 10849.`,
        );
        setLoading(false);
        return;
      }

      const status = await getStatus();
      const hasData = status.data && typeof status.data === "object" && "blender" in status.data;
      const blenderOk = hasData && (status.data as { blender?: boolean }).blender === true;
      setConnected(!!blenderOk);

      if (hasData && !blenderOk) {
        setError("Blender not found or not running. Install Blender or set BLENDER_EXECUTABLE.");
        setLoading(false);
        return;
      }
      if (!status.success && !hasData) {
        const msg = status.error ?? "Tool bridge failed. Check backend logs.";
        setError(
          typeof msg === "string" && (msg.startsWith("{") || msg.includes("'blender'"))
            ? "Backend returned unexpected format."
            : msg,
        );
        setLoading(false);
        return;
      }
      if (!hasData) {
        setError("No status from backend. Check server logs.");
        setLoading(false);
        return;
      }

      // Load scene hierarchy
      const response = await getSceneData();
      if (response.success && response.data) {
        // Transform backend data to SceneNode format
        const collections = response.data.collections || [];
        const transformed: SceneNode[] = collections.map((col) => ({
          name: col.name,
          type: "COLLECTION",
          children:
            col.objects?.map((obj) => ({
              name: obj.name,
              type: "OBJECT" as const,
            })) || [],
        }));
        setSceneData(transformed);
      } else {
        setError(response.error || "Failed to load scene data");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSceneData();
  }, [loadSceneData]);

  const TreeNode = ({ node, depth = 0 }: { node: SceneNode; depth?: number }) => {
    const [expanded, setExpanded] = useState(true);
    const hasChildren = node.children && node.children.length > 0;

    return (
      <div className="select-none">
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              setExpanded(!expanded);
            }
          }}
          className="flex items-center py-1 hover:bg-accent/50 rounded px-2 cursor-pointer transition-colors w-full text-left"
          style={{ paddingLeft: `${depth * 1.5 + 0.5}rem` }}
        >
          <div className="mr-1 text-muted-foreground">
            {hasChildren ? (
              expanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )
            ) : (
              <div className="w-4 h-4" />
            )}
          </div>

          <div className="mr-2">
            {node.type === "COLLECTION" ? (
              <Folder className="w-4 h-4 text-blue-400" />
            ) : (
              <File className="w-4 h-4 text-orange-400" />
            )}
          </div>

          <span className="text-sm font-medium">{node.name}</span>
          <span className="ml-auto text-xs text-muted-foreground uppercase">{node.type}</span>
        </button>

        {expanded && node.children && (
          <div>
            {node.children.map((child, i) => (
              <TreeNode key={`${child.name}-${child.type}-${i}`} node={child} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight mb-1">Scene Explorer</h1>
          <p className="text-muted-foreground">
            View and manage the active Blender scene hierarchy.
          </p>
        </div>
        <button
          type="button"
          onClick={loadSceneData}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="border border-border rounded-lg bg-card overflow-hidden shadow-sm">
        <div className="p-4 border-b border-border bg-muted/30">
          <div className="flex items-center space-x-2 text-sm font-medium">
            <div className={`w-3 h-3 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`} />
            <span>{connected ? "Connected to Blender" : "Not Connected"}</span>
            {connected && <span className="text-muted-foreground">MCP backend</span>}
          </div>
        </div>
        {error && (
          <div className="p-4 bg-red-500/10 border-b border-red-500/20">
            <div className="flex items-center gap-2 text-red-500">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">{error}</span>
            </div>
          </div>
        )}
        <div className="p-2">
          {sceneData.length === 0 && !loading && !error && (
            <div className="p-4 text-center text-muted-foreground">No scene data available</div>
          )}
          {sceneData.map((node, i) => (
            <TreeNode key={`${node.name}-${node.type}-${i}`} node={node} />
          ))}
        </div>
      </div>
    </div>
  );
}
