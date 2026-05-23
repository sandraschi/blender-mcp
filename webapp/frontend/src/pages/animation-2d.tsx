import { Layers, Play, SkipBack, SkipForward, StopCircle } from "lucide-react";
import { useCallback, useState } from "react";
import { callTool } from "../api/mcp";

export default function Animation2DPage() {
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [gpName, setGpName] = useState("GPencil");
  const [layerName, setLayerName] = useState("GP_Layer");
  const [frameNum, setFrameNum] = useState(1);
  const [startFrame, setStartFrame] = useState(1);
  const [endFrame, setEndFrame] = useState(24);
  const [interpFrames, setInterpFrames] = useState(5);
  const [modifierType, setModifierType] = useState("BUILD");

  const runGp = useCallback(async (params: Record<string, unknown>) => {
    setLoading(true);
    try {
      const r = await callTool("blender_grease_pencil", params);
      setOutput(r.success ? String(r.data ?? r.message ?? "OK") : String(r.error ?? "Failed"));
    } finally {
      setLoading(false);
    }
  }, []);

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
        <Layers className="w-8 h-8 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">2D Animation Timeline</h1>
          <p className="text-sm text-muted-foreground">Animate Grease Pencil strokes — keyframes, interpolation, modifiers</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <OpButton label="Insert Keyframe" icon={Play} params={{ operation: "animate_stroke", gp_object: gpName, layer_name: layerName, frame_number: frameNum }} />
        <OpButton label="Interpolate" icon={SkipForward} params={{ operation: "interpolate", gp_object: gpName, layer_name: layerName, frame_number: startFrame, interpolation_frames: interpFrames }} />
        <OpButton label="Add Modifier" icon={StopCircle} params={{ operation: "add_modifier", gp_object: gpName, modifier_type: modifierType }} />
        <OpButton label="Frame -1" icon={SkipBack} params={{ operation: "animate_stroke", gp_object: gpName, layer_name: layerName, frame_number: Math.max(1, frameNum - 1) }} />
        <OpButton label="Frame +1" icon={SkipForward} params={{ operation: "animate_stroke", gp_object: gpName, layer_name: layerName, frame_number: frameNum + 1 }} />
      </div>

      <div className="border border-border rounded-lg p-4 space-y-4 bg-card">
        <h2 className="font-semibold">Keyframe Controls</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">GP Object</label>
            <input type="text" value={gpName} onChange={(e) => setGpName(e.target.value)}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border" />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Layer</label>
            <input type="text" value={layerName} onChange={(e) => setLayerName(e.target.value)}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border" />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Frame</label>
            <input type="number" value={frameNum} onChange={(e) => setFrameNum(Number(e.target.value))} min={1}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border" />
          </div>
        </div>
      </div>

      <div className="border border-border rounded-lg p-4 space-y-4 bg-card">
        <h2 className="font-semibold">Interpolation</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Start Frame</label>
            <input type="number" value={startFrame} onChange={(e) => setStartFrame(Number(e.target.value))} min={1}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border" />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">End Frame</label>
            <input type="number" value={endFrame} onChange={(e) => setEndFrame(Number(e.target.value))} min={1}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border" />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Interpolation Frames</label>
            <input type="number" value={interpFrames} onChange={(e) => setInterpFrames(Number(e.target.value))} min={1} max={50}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border" />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Modifier</label>
            <select value={modifierType} onChange={(e) => setModifierType(e.target.value)}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border">
              <option value="BUILD">Build</option>
              <option value="NOISE">Noise</option>
              <option value="SIMPLIFY">Simplify</option>
              <option value="SMOOTH">Smooth</option>
            </select>
          </div>
        </div>
      </div>

      <div className="border border-border rounded-lg p-4 space-y-3 bg-card">
        <h2 className="font-semibold">Layer Modifiers</h2>
        <div className="flex flex-wrap gap-2">
          <OpButton label="Set Layer" icon={Layers} params={{ operation: "set_layer", gp_object: gpName, layer_name: layerName }} />
          <OpButton label="Fill Region" icon={StopCircle} params={{ operation: "fill_region", gp_object: gpName, layer_name: layerName, frame_number: frameNum }} />
        </div>
      </div>

      {output && (
        <div className="border border-border rounded-lg p-4 bg-muted/20">
          <p className="text-sm font-mono whitespace-pre-wrap text-muted-foreground">{output}</p>
        </div>
      )}
    </div>
  );
}
