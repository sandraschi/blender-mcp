import { Circle, Eraser, Minus, Pen, Square, Trash2 } from "lucide-react";
import { useCallback, useState } from "react";
import { callTool } from "../api/mcp";

export default function GreasePencilPage() {
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [gpName, setGpName] = useState("GPencil");
  const [strokeType, setStrokeType] = useState("LINE");
  const [colorR, setColorR] = useState(0);
  const [colorG, setColorG] = useState(0);
  const [colorB, setColorB] = useState(0);
  const [thickness, setThickness] = useState(2);
  const [radius, setRadius] = useState(1);
  const [layerName, setLayerName] = useState("GP_Layer");

  const runGp = useCallback(async (params: Record<string, unknown>) => {
    setLoading(true);
    try {
      const r = await callTool("blender_grease_pencil", params);
      setOutput(r.success ? String(r.data ?? r.message ?? "OK") : String(r.error ?? "Failed"));
    } finally {
      setLoading(false);
    }
  }, []);

  const color = [colorR / 255, colorG / 255, colorB / 255, 1.0];

  const OpButton = ({ label, icon: Icon, params, variant = "default" }: {
    label: string; icon: React.ElementType; params: Record<string, unknown>; variant?: "default" | "danger";
  }) => (
    <button
      type="button"
      disabled={loading}
      onClick={() => runGp(params)}
      className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
        variant === "danger"
          ? "bg-red-500/10 text-red-400 hover:bg-red-500/20"
          : "bg-accent text-accent-foreground hover:bg-accent/80"
      } disabled:opacity-50`}
    >
      <Icon className="w-4 h-4" />
      <span>{label}</span>
    </button>
  );

  return (
    <div className="p-6 space-y-6 max-w-4xl">
      <div className="flex items-center space-x-3">
        <Pen className="w-8 h-8 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">Grease Pencil</h1>
          <p className="text-sm text-muted-foreground">
            Create and edit 2D Grease Pencil objects — strokes, layers, materials
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <OpButton label="Create GP" icon={Pen} params={{ operation: "create", name: gpName }} />
        <OpButton label="List Layers" icon={Square} params={{ operation: "list_layers", gp_object: gpName }} />
        <OpButton label="Delete All Strokes" icon={Eraser} params={{ operation: "delete_strokes", gp_object: gpName, layer_name: layerName }} variant="danger" />
        <OpButton label="Onion Skin On" icon={Circle} params={{ operation: "onion_skinning", gp_object: gpName, before_frames: 3, after_frames: 3 }} />
      </div>

      <div className="border border-border rounded-lg p-4 space-y-4 bg-card">
        <h2 className="font-semibold flex items-center space-x-2">
          <Pen className="w-5 h-5" />
          <span>Create Grease Pencil</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Object Name</label>
            <input
              type="text" value={gpName} onChange={(e) => setGpName(e.target.value)}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border"
            />
          </div>
          <div className="flex items-end">
            <OpButton label="Create" icon={Pen} params={{ operation: "create", name: gpName }} />
          </div>
        </div>
      </div>

      <div className="border border-border rounded-lg p-4 space-y-4 bg-card">
        <h2 className="font-semibold flex items-center space-x-2">
          <Minus className="w-5 h-5" />
          <span>Draw Stroke on {gpName}</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Stroke Type</label>
            <select value={strokeType} onChange={(e) => setStrokeType(e.target.value)}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border">
              <option value="LINE">Line</option>
              <option value="BOX">Box</option>
              <option value="CIRCLE">Circle</option>
              <option value="ARC">Arc</option>
              <option value="CURVE">Curve</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Thickness</label>
            <input type="number" value={thickness} onChange={(e) => setThickness(Number(e.target.value))} min={0.1} step={0.5}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border" />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Radius (Circle)</label>
            <input type="number" value={radius} onChange={(e) => setRadius(Number(e.target.value))} min={0.1} step={0.5}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Layer</label>
            <input type="text" value={layerName} onChange={(e) => setLayerName(e.target.value)}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border" />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Stroke Color (RGB 0-255)</label>
            <div className="flex space-x-2">
              <input type="number" value={colorR} onChange={(e) => setColorR(Number(e.target.value))} min={0} max={255}
                className="w-12 px-2 py-2 bg-secondary rounded-lg text-sm border border-border text-center" placeholder="R" />
              <input type="number" value={colorG} onChange={(e) => setColorG(Number(e.target.value))} min={0} max={255}
                className="w-12 px-2 py-2 bg-secondary rounded-lg text-sm border border-border text-center" placeholder="G" />
              <input type="number" value={colorB} onChange={(e) => setColorB(Number(e.target.value))} min={0} max={255}
                className="w-12 px-2 py-2 bg-secondary rounded-lg text-sm border border-border text-center" placeholder="B" />
              <div className="w-8 h-8 rounded border border-border" style={{ backgroundColor: `rgb(${colorR},${colorG},${colorB})` }} />
            </div>
          </div>
          <div className="flex items-end space-x-2">
            <OpButton label="Draw" icon={Pen} params={{
              operation: "draw_stroke", gp_object: gpName, stroke_type: strokeType,
              color, thickness, layer_name: layerName, radius,
            }} />
            <OpButton label="Set Material" icon={Circle} params={{
              operation: "set_material", gp_object: gpName, material_name: `${gpName}_Mat`,
              color,
            }} />
          </div>
        </div>
      </div>

      <div className="border border-border rounded-lg p-4 space-y-3 bg-card">
        <h2 className="font-semibold flex items-center space-x-2">
          <Trash2 className="w-5 h-5" />
          <span>Convert & Cleanup</span>
        </h2>
        <div className="flex flex-wrap gap-2">
          <OpButton label="Convert to Mesh" icon={Square} params={{ operation: "convert", gp_object: gpName, target_type: "MESH" }} />
          <OpButton label="Convert to Curve" icon={Minus} params={{ operation: "convert", gp_object: gpName, target_type: "CURVE" }} />
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
