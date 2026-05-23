import { Clapperboard, Film, Image, Plus, Square, Trash2 } from "lucide-react";
import { useCallback, useState } from "react";
import { callTool } from "../api/mcp";

export default function StoryboardPage() {
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [gpName, setGpName] = useState("Storyboard");
  const [shotCount, setShotCount] = useState(6);
  const [shotName, setShotName] = useState("Shot_01");
  const [fromLayer, setFromLayer] = useState("");
  const [toLayer, setToLayer] = useState("");

  const runGp = useCallback(async (params: Record<string, unknown>) => {
    setLoading(true);
    try {
      const r = await callTool("blender_grease_pencil", params);
      setOutput(r.success ? String(r.data ?? r.message ?? "OK") : String(r.error ?? "Failed"));
    } finally {
      setLoading(false);
    }
  }, []);

  const createStoryboard = useCallback(async () => {
    setLoading(true);
    try {
      const r = await callTool("blender_grease_pencil", { operation: "create", name: gpName });
      setOutput(r.success ? `Storyboard '${gpName}' created with ${shotCount} shots` : String(r.error ?? "Failed"));
    } finally {
      setLoading(false);
    }
  }, [gpName, shotCount]);

  const OpButton = ({ label, icon: Icon, params, variant = "default" }: {
    label: string; icon: React.ElementType; params: Record<string, unknown>; variant?: "default" | "danger";
  }) => (
    <button type="button" disabled={loading} onClick={() => runGp(params)}
      className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
        variant === "danger" ? "bg-red-500/10 text-red-400 hover:bg-red-500/20"
          : "bg-accent text-accent-foreground hover:bg-accent/80"
      } disabled:opacity-50`}
    >
      <Icon className="w-4 h-4" /><span>{label}</span>
    </button>
  );

  return (
    <div className="p-6 space-y-6 max-w-4xl">
      <div className="flex items-center space-x-3">
        <Clapperboard className="w-8 h-8 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">Storyboard</h1>
          <p className="text-sm text-muted-foreground">
            Frame-by-frame storyboard viewer and shot management using Grease Pencil
          </p>
        </div>
      </div>

      <div className="border border-border rounded-lg p-4 space-y-4 bg-card">
        <h2 className="font-semibold flex items-center space-x-2">
          <Film className="w-5 h-5" />
          <span>Create Storyboard</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Storyboard Name</label>
            <input type="text" value={gpName} onChange={(e) => setGpName(e.target.value)}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border" />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Shot Count</label>
            <input type="number" value={shotCount} onChange={(e) => setShotCount(Number(e.target.value))} min={1} max={100}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border" />
          </div>
          <div className="flex items-end">
            <button type="button" onClick={createStoryboard} disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              <Plus className="w-4 h-4" /><span>Create</span>
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <OpButton label="List Layers" icon={Square} params={{ operation: "list_layers", gp_object: gpName }} />
        <OpButton label="Onion Skin" icon={Image} params={{ operation: "onion_skinning", gp_object: gpName, before_frames: 2, after_frames: 2 }} />
      </div>

      <div className="border border-border rounded-lg p-4 space-y-4 bg-card">
        <h2 className="font-semibold">Shot Management</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Shot Name</label>
            <input type="text" value={shotName} onChange={(e) => setShotName(e.target.value)}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border" />
          </div>
        </div>
      </div>

      <div className="border border-border rounded-lg p-4 space-y-3 bg-card">
        <h2 className="font-semibold flex items-center space-x-2">
          <Trash2 className="w-4 h-4" />
          <span>Cleanup</span>
        </h2>
        <OpButton label="Delete Storyboard" icon={Trash2} params={{ operation: "delete_strokes", gp_object: gpName }} variant="danger" />
      </div>

      {output && (
        <div className="border border-border rounded-lg p-4 bg-muted/20">
          <p className="text-sm font-mono whitespace-pre-wrap text-muted-foreground">{output}</p>
        </div>
      )}
    </div>
  );
}
