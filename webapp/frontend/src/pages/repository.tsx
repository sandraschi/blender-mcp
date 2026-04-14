import { Box, Database, Download, Loader2, RefreshCw, Save, Search, Star, Tag } from "lucide-react";
import { useState } from "react";
import { callTool } from "../api/mcp";

interface RepoObject {
  id: string;
  name: string;
  blender_name?: string;
  description?: string;
  category?: string;
  tags?: string[];
  estimated_quality?: number;
  version?: string;
  updated_at?: string;
}

export default function RepositoryPage() {
  const [objects, setObjects] = useState<RepoObject[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [minQuality, setMinQuality] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ text: string; ok: boolean } | null>(null);

  // Save form
  const [saveObjectName, setSaveObjectName] = useState("");
  const [saveDisplayName, setSaveDisplayName] = useState("");
  const [saveDescription, setSaveDescription] = useState("");
  const [saveCategory, setSaveCategory] = useState("general");
  const [saveQuality, setSaveQuality] = useState(5);
  const [saveTags, setSaveTags] = useState("");

  // Load form
  const [loadId, setLoadId] = useState("");
  const [loadPos, setLoadPos] = useState("0,0,0");
  const [loadScale, setLoadScale] = useState("1,1,1");

  const parseVec = (s: string): [number, number, number] => {
    const parts = s.split(",").map(Number);
    return [parts[0] ?? 0, parts[1] ?? 0, parts[2] ?? 0];
  };

  const msg = (text: string, ok = true) => setMessage({ text, ok });

  const listAll = async () => {
    setLoading(true);
    try {
      const res = await callTool<{ success: boolean; objects?: RepoObject[]; total?: number }>(
        "manage_object_repo",
        { operation: "list_objects" },
      );
      if (res.success && res.data?.objects) {
        setObjects(res.data.objects);
        msg(`${res.data.total ?? res.data.objects.length} objects in repository`);
      } else {
        msg(res.error ?? "Failed to list objects", false);
      }
    } finally {
      setLoading(false);
    }
  };

  const search = async () => {
    setLoading(true);
    try {
      const res = await callTool<{ success: boolean; objects?: RepoObject[] }>(
        "manage_object_repo",
        {
          operation: "search",
          query: query || undefined,
          category: category || undefined,
          min_quality: minQuality > 0 ? minQuality : undefined,
          limit: 50,
        },
      );
      if (res.success && res.data?.objects) {
        setObjects(res.data.objects);
        msg(`${res.data.objects.length} results`);
      } else {
        msg(res.error ?? "Search failed", false);
      }
    } finally {
      setLoading(false);
    }
  };

  const saveObject = async () => {
    if (!saveObjectName) {
      msg("Blender object name required", false);
      return;
    }
    setLoading(true);
    try {
      const res = await callTool<{ success: boolean; message?: string; object_id?: string }>(
        "manage_object_repo",
        {
          operation: "save",
          object_name: saveObjectName,
          object_name_display: saveDisplayName || saveObjectName,
          description: saveDescription,
          category: saveCategory,
          quality_rating: saveQuality,
          tags: saveTags
            ? saveTags
                .split(",")
                .map((t) => t.trim())
                .filter(Boolean)
            : [],
        },
      );
      if (res.data?.success) {
        msg(res.data.message ?? `Saved as ${res.data.object_id}`);
        listAll();
      } else {
        msg(res.data?.message ?? res.error ?? "Save failed", false);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadObject = async (id?: string) => {
    const targetId = id ?? loadId;
    if (!targetId) {
      msg("Object ID required", false);
      return;
    }
    setLoading(true);
    try {
      const res = await callTool<{ success: boolean; message?: string }>("manage_object_repo", {
        operation: "load",
        object_id: targetId,
        position: parseVec(loadPos),
        scale: parseVec(loadScale),
      });
      if (res.data?.success) {
        msg(res.data.message ?? `Loaded ${targetId}`);
      } else {
        msg(res.data?.message ?? res.error ?? "Load failed", false);
      }
    } finally {
      setLoading(false);
    }
  };

  const qualityColor = (q?: number) => {
    if (!q) return "text-muted-foreground";
    if (q >= 8) return "text-green-400";
    if (q >= 5) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight mb-1 flex items-center gap-2">
            <Database className="w-6 h-6" /> Object Repository
          </h1>
          <p className="text-muted-foreground text-sm">
            Save, load and search versioned Blender objects — stored in ~/.blender-mcp/repository/
          </p>
        </div>
        <button
          type="button"
          onClick={listAll}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 text-sm bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          Refresh
        </button>
      </div>

      {message && (
        <div
          className={`px-4 py-2 rounded-md text-sm font-medium ${message.ok ? "bg-green-500/10 text-green-400 border border-green-500/20" : "bg-red-500/10 text-red-400 border border-red-500/20"}`}
        >
          {message.text}
        </div>
      )}

      {/* Save + Load forms */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Save */}
        <div className="bg-card border border-border rounded-lg p-5 space-y-3">
          <h2 className="font-semibold flex items-center gap-2">
            <Save className="w-4 h-4" /> Save Active Object
          </h2>
          <input
            className="w-full px-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Blender object name (exact)"
            value={saveObjectName}
            onChange={(e) => setSaveObjectName(e.target.value)}
          />
          <input
            className="w-full px-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Display name"
            value={saveDisplayName}
            onChange={(e) => setSaveDisplayName(e.target.value)}
          />
          <input
            className="w-full px-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Description"
            value={saveDescription}
            onChange={(e) => setSaveDescription(e.target.value)}
          />
          <div className="grid grid-cols-2 gap-2">
            <select
              className="px-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
              value={saveCategory}
              onChange={(e) => setSaveCategory(e.target.value)}
            >
              {[
                "general",
                "character",
                "architecture",
                "vehicle",
                "prop",
                "environment",
                "scifi",
              ].map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-yellow-400 shrink-0" />
              <input
                type="number"
                min={1}
                max={10}
                className="w-full px-2 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
                value={saveQuality}
                onChange={(e) => setSaveQuality(Number(e.target.value))}
              />
            </div>
          </div>
          <input
            className="w-full px-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Tags (comma-separated)"
            value={saveTags}
            onChange={(e) => setSaveTags(e.target.value)}
          />
          <button
            type="button"
            onClick={saveObject}
            disabled={loading || !saveObjectName}
            className="w-full px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            Save to Repository
          </button>
        </div>

        {/* Load */}
        <div className="bg-card border border-border rounded-lg p-5 space-y-3">
          <h2 className="font-semibold flex items-center gap-2">
            <Download className="w-4 h-4" /> Load Object
          </h2>
          <input
            className="w-full px-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Object ID (from search results)"
            value={loadId}
            onChange={(e) => setLoadId(e.target.value)}
          />
          <input
            className="w-full px-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Position x,y,z"
            value={loadPos}
            onChange={(e) => setLoadPos(e.target.value)}
          />
          <input
            className="w-full px-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Scale x,y,z"
            value={loadScale}
            onChange={(e) => setLoadScale(e.target.value)}
          />
          <button
            type="button"
            onClick={() => loadObject()}
            disabled={loading || !loadId}
            className="w-full px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            Load into Scene
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="bg-card border border-border rounded-lg p-5 space-y-3">
        <h2 className="font-semibold flex items-center gap-2">
          <Search className="w-4 h-4" /> Search
        </h2>
        <div className="flex gap-2 flex-wrap">
          <input
            className="flex-1 min-w-[160px] px-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Search query..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && search()}
          />
          <input
            className="w-32 px-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          />
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 text-yellow-400 shrink-0" />
            <input
              type="number"
              min={0}
              max={10}
              className="w-16 px-2 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
              placeholder="Min"
              value={minQuality || ""}
              onChange={(e) => setMinQuality(Number(e.target.value))}
            />
          </div>
          <button
            type="button"
            onClick={search}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
          >
            Search
          </button>
          <button
            type="button"
            onClick={listAll}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
          >
            List All
          </button>
        </div>
      </div>

      {/* Results */}
      {objects.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          {objects.map((obj) => (
            <div
              key={obj.id}
              className="bg-card border border-border rounded-lg p-4 space-y-2 hover:border-primary/50 transition-colors"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  <Box className="w-4 h-4 text-primary shrink-0" />
                  <span className="font-medium text-sm truncate">{obj.name}</span>
                </div>
                <span
                  className={`text-xs font-bold shrink-0 ${qualityColor(obj.estimated_quality)}`}
                >
                  ★{obj.estimated_quality ?? "?"}
                </span>
              </div>
              {obj.description && (
                <p className="text-xs text-muted-foreground line-clamp-2">{obj.description}</p>
              )}
              <div className="flex items-center gap-2 flex-wrap">
                {obj.category && (
                  <span className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded-full">
                    {obj.category}
                  </span>
                )}
                {obj.tags?.slice(0, 3).map((t) => (
                  <span
                    key={t}
                    className="text-xs px-2 py-0.5 bg-secondary text-secondary-foreground rounded-full flex items-center gap-1"
                  >
                    <Tag className="w-2.5 h-2.5" />
                    {t}
                  </span>
                ))}
              </div>
              <div className="flex items-center justify-between pt-1">
                <span className="text-xs text-muted-foreground font-mono">
                  {obj.id.slice(0, 8)}…
                </span>
                <button
                  type="button"
                  onClick={() => {
                    setLoadId(obj.id);
                    loadObject(obj.id);
                  }}
                  disabled={loading}
                  className="text-xs px-3 py-1 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors"
                >
                  Load
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {objects.length === 0 && !loading && (
        <div className="text-center py-12 text-muted-foreground">
          <Database className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p className="text-sm">Repository empty or not yet loaded.</p>
          <p className="text-xs mt-1">
            Click <strong>Refresh</strong> or <strong>List All</strong> to load.
          </p>
        </div>
      )}
    </div>
  );
}
