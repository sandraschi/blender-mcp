import {
  Activity,
  Box,
  Camera,
  Cpu,
  Layers,
  Palette,
  ScanEye,
  Sparkles,
  Wrench,
} from "lucide-react";
import { useState } from "react";
import { callTool, getBackendHealth } from "../api/mcp";

type TabId =
  | "vision"
  | "shaders"
  | "mesh-edit"
  | "sculpt"
  | "geonodes"
  | "ai-gen"
  | "jobs"
  | "validation"
  | "monitoring";

function ResultBox({ text }: { text: string | null }) {
  if (!text) return null;
  return (
    <pre className="mt-3 p-3 text-xs bg-muted rounded-lg overflow-x-auto whitespace-pre-wrap border border-border">
      {text}
    </pre>
  );
}

export default function AgentToolsPage() {
  const [tab, setTab] = useState<TabId>("vision");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

  const [outputPath, setOutputPath] = useState("D:/Temp/blender_mcp/review.png");
  const [outputDir, setOutputDir] = useState("D:/Temp/blender_mcp/angles");
  const [objectName, setObjectName] = useState("Cube");
  const [materialName, setMaterialName] = useState("AgentMaterial");
  const [groupName, setGroupName] = useState("AgentGeoNodes");
  const [aiPrompt, setAiPrompt] = useState("low poly wooden crate");
  const [aiBackend, setAiBackend] = useState("tripo");
  const [jobScript, setJobScript] = useState("import bpy\nprint('async job ok')");
  const [batchInputDir, setBatchInputDir] = useState("D:/Temp/blender_mcp/images");
  const [brushName, setBrushName] = useState("Grab");

  const tabs: { id: TabId; label: string; icon: typeof Camera }[] = [
    { id: "vision", label: "Vision", icon: ScanEye },
    { id: "shaders", label: "Shaders / Comp", icon: Palette },
    { id: "mesh-edit", label: "Mesh Edit", icon: Wrench },
    { id: "sculpt", label: "Sculpt", icon: Box },
    { id: "geonodes", label: "GeoNodes", icon: Layers },
    { id: "ai-gen", label: "AI Generate", icon: Sparkles },
    { id: "jobs", label: "Async Jobs", icon: Cpu },
    { id: "validation", label: "Validate / Batch", icon: Activity },
    { id: "monitoring", label: "Telemetry", icon: Activity },
  ];

  const run = async (tool: string, params: Record<string, unknown>) => {
    setLoading(true);
    setResult(null);
    try {
      const res = await callTool(tool, params);
      setResult(JSON.stringify(res, null, 2));
    } catch (e) {
      setResult(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  const checkBackend = async () => {
    const r = await getBackendHealth();
    setBackendOk(r.ok);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Agent Tools</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Phases 1–5: vision loops, shaders, mesh edit, sculpt, geonodes, AI mesh, jobs, validation,
            batch, and telemetry.
          </p>
        </div>
        <button
          type="button"
          onClick={checkBackend}
          className="px-3 py-1.5 text-sm bg-secondary rounded-md hover:bg-secondary/80"
        >
          Check backend
        </button>
      </div>

      {backendOk !== null && (
        <p className={`text-sm ${backendOk ? "text-green-500" : "text-red-500"}`}>
          Backend {backendOk ? "online" : "offline"} — run webapp start.ps1 if needed.
        </p>
      )}

      <div className="flex flex-wrap gap-2 border-b border-border pb-2">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => {
              setTab(t.id);
              setResult(null);
            }}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === t.id
                ? "bg-primary text-primary-foreground"
                : "bg-accent text-muted-foreground hover:text-foreground"
            }`}
          >
            <t.icon className="w-4 h-4" />
            {t.label}
          </button>
        ))}
      </div>

      <div className="border border-border rounded-lg p-5 bg-card space-y-4">
        {tab === "vision" && (
          <>
            <h2 className="font-semibold">Vision &amp; review loop</h2>
            <p className="text-sm text-muted-foreground">
              Live GUI + bridge addon recommended for viewport capture. Headless falls back to still
              render.
            </p>
            <label className="block text-sm">
              Output directory (multi-angle / review bundle)
              <input
                className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                value={outputDir}
                onChange={(e) => setOutputDir(e.target.value)}
              />
            </label>
            <label className="block text-sm">
              Output path
              <input
                className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                value={outputPath}
                onChange={(e) => setOutputPath(e.target.value)}
              />
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() =>
                  run("blender_render", {
                    operation: "screenshot_viewport",
                    output_path: outputPath,
                  })
                }
              >
                Screenshot viewport
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("blender_vision_refine", {
                    operation: "review_bundle",
                    output_dir: outputDir,
                    goal: "Improve scene toward user goal",
                  })
                }
              >
                Review bundle
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("blender_render", {
                    operation: "render_multi_angle",
                    output_dir: outputDir,
                    angles: 4,
                  })
                }
              >
                Multi-angle stills
              </button>
            </div>
          </>
        )}

        {tab === "shaders" && (
          <>
            <h2 className="font-semibold">Shader &amp; compositor graphs</h2>
            <input
              className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
              value={materialName}
              onChange={(e) => setMaterialName(e.target.value)}
              placeholder="Material name"
            />
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() =>
                  run("blender_shaders", {
                    operation: "create_material",
                    material_name: materialName,
                  })
                }
              >
                Create material
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() => run("blender_compositor", { operation: "enable" })}
              >
                Enable compositor
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() => run("blender_compositor", { operation: "glow" })}
              >
                Add glow
              </button>
            </div>
          </>
        )}

        {tab === "mesh-edit" && (
          <>
            <h2 className="font-semibold">Mesh edit (live session preferred)</h2>
            <input
              className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
              value={objectName}
              onChange={(e) => setObjectName(e.target.value)}
            />
            <div className="flex flex-wrap gap-2">
              {(["extrude", "inset", "bevel_modifier", "subdivide", "triangulate"] as const).map(
                (op) => (
                  <button
                    key={op}
                    type="button"
                    disabled={loading}
                    className="px-3 py-2 bg-secondary rounded-md text-sm"
                    onClick={() =>
                      run("blender_mesh", { operation: op, name: objectName, prefer_session: true })
                    }
                  >
                    {op}
                  </button>
                ),
              )}
            </div>
          </>
        )}

        {tab === "sculpt" && (
          <>
            <h2 className="font-semibold">Sculpt mode</h2>
            <input
              className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm mb-2"
              value={objectName}
              onChange={(e) => setObjectName(e.target.value)}
              placeholder="Object name"
            />
            <input
              className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
              value={brushName}
              onChange={(e) => setBrushName(e.target.value)}
              placeholder="Brush name"
            />
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() =>
                  run("blender_sculpt", {
                    operation: "enter",
                    object_name: objectName,
                    prefer_session: true,
                  })
                }
              >
                Enter sculpt
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("blender_sculpt", {
                    operation: "set_brush",
                    object_name: objectName,
                    brush_name: brushName,
                  })
                }
              >
                Set brush
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("blender_sculpt", { operation: "dynotopo", object_name: objectName })
                }
              >
                Dynotopo
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() => run("blender_sculpt", { operation: "list_brushes" })}
              >
                List brushes
              </button>
            </div>
          </>
        )}

        {tab === "geonodes" && (
          <>
            <h2 className="font-semibold">Geometry Nodes</h2>
            <input
              className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm mb-2"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
            />
            <input
              className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
              value={objectName}
              onChange={(e) => setObjectName(e.target.value)}
              placeholder="Target object"
            />
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() =>
                  run("blender_geonodes", { operation: "create_group", group_name: groupName })
                }
              >
                Create group
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("blender_geonodes", {
                    operation: "assign_modifier",
                    group_name: groupName,
                    object_name: objectName,
                  })
                }
              >
                Assign modifier
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() => run("blender_geonodes", { operation: "list_node_types" })}
              >
                List node types
              </button>
            </div>
          </>
        )}

        {tab === "ai-gen" && (
          <>
            <h2 className="font-semibold">AI mesh generation</h2>
            <p className="text-sm text-muted-foreground">
              Requires TRIPO_API_KEY, RODIN_API_KEY, or HUNYUAN3D_API_KEY in server environment.
            </p>
            <textarea
              className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm min-h-[80px]"
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
            />
            <select
              className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
              value={aiBackend}
              onChange={(e) => setAiBackend(e.target.value)}
            >
              <option value="tripo">tripo</option>
              <option value="rodin">rodin</option>
              <option value="hunyuan">hunyuan</option>
            </select>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() =>
                  run("blender_ai_generate", {
                    operation: "generate",
                    prompt: aiPrompt,
                    backend: aiBackend,
                    object_name: objectName,
                  })
                }
              >
                Generate &amp; import
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() => run("blender_ai_generate", { operation: "list_backends" })}
              >
                List backends
              </button>
            </div>
          </>
        )}

        {tab === "jobs" && (
          <>
            <h2 className="font-semibold">Async job queue</h2>
            <textarea
              className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm font-mono min-h-[100px]"
              value={jobScript}
              onChange={(e) => setJobScript(e.target.value)}
            />
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() =>
                  run("blender_jobs", {
                    operation: "submit",
                    script: jobScript,
                    script_name: "webapp_job",
                  })
                }
              >
                Submit job
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() => run("blender_jobs", { operation: "list" })}
              >
                List jobs
              </button>
            </div>
          </>
        )}

        {tab === "validation" && (
          <>
            <h2 className="font-semibold">Validation &amp; batch</h2>
            <input
              className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm mb-2"
              value={objectName}
              onChange={(e) => setObjectName(e.target.value)}
              placeholder="Object for geometry audit"
            />
            <input
              className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
              value={batchInputDir}
              onChange={(e) => setBatchInputDir(e.target.value)}
              placeholder="Batch input directory"
            />
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() =>
                  run("blender_validation", {
                    operation: "validate_geometry",
                    object_name: objectName,
                  })
                }
              >
                Validate geometry
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("blender_validation", {
                    operation: "check_manifold",
                    object_name: objectName,
                  })
                }
              >
                Check manifold
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("blender_batch", {
                    operation: "resize",
                    input_dir: batchInputDir,
                    pattern: "*.png",
                    width: 1024,
                    height: 1024,
                  })
                }
              >
                Batch resize PNG
              </button>
            </div>
          </>
        )}

        {tab === "monitoring" && (
          <>
            <h2 className="font-semibold">Telemetry &amp; Docker</h2>
            <ul className="text-sm text-muted-foreground space-y-2 list-disc pl-5">
              <li>Prometheus metrics: port 9091 and /metrics on MCP HTTP (10849)</li>
              <li>JSON logs: BLENDER_MCP_LOG_FORMAT=json for Loki</li>
              <li>Docker: docker compose --profile monitoring up -d</li>
              <li>GHCR: ghcr.io/sandraschi/blender-mcp:latest</li>
            </ul>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() => run("blender_api_docs", { identifier: "bpy.types.Mesh" })}
              >
                API docs sample
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() => run("blender_status", { operation: "status", format: "json" })}
              >
                Server status
              </button>
            </div>
            <p className="text-xs text-muted-foreground">
              Open Grafana at http://localhost:3000 when monitoring profile is running. See
              docs/MONITORING.md in repo.
            </p>
          </>
        )}

        {loading && <p className="text-sm text-muted-foreground">Running MCP tool...</p>}
        <ResultBox text={result} />
      </div>
    </div>
  );
}
