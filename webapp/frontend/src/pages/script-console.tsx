import { FileCode, Play, Save, Trash2 } from "lucide-react";
import { useState } from "react";
import { executeScript } from "../api/mcp";

export default function ScriptConsole() {
  const [code, setCode] = useState(
    "import bpy\n\n# Create a cube\nbpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))\n\n# Add a subsurf modifier\nobj = bpy.context.active_object\nmod = obj.modifiers.new(name='Subsurf', type='SUBSURF')\nmod.levels = 2",
  );
  const [output, setOutput] = useState<string[]>([]);
  const [executing, setExecuting] = useState(false);

  const executeScriptHandler = async () => {
    setExecuting(true);
    setOutput((prev) => [...prev, ">>> Executing script..."]);

    try {
      const response = await executeScript(code);
      if (response.success && response.data) {
        setOutput((prev) => [...prev, response.data?.output || "Script executed successfully"]);
      } else {
        setOutput((prev) => [...prev, `Error: ${response.error || "Failed to execute script"}`]);
      }
    } catch (err) {
      setOutput((prev) => [
        ...prev,
        `Error: ${err instanceof Error ? err.message : "Unknown error"}`,
      ]);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight mb-1">Script Console</h1>
          <p className="text-muted-foreground">Direct Python execution in Blender.</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            type="button"
            className="flex items-center space-x-2 px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
          >
            <Save className="w-4 h-4" />
            <span>Save</span>
          </button>
          <button
            type="button"
            onClick={executeScriptHandler}
            disabled={executing}
            className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20 disabled:opacity-50"
          >
            <Play className={`w-4 h-4 fill-current ${executing ? "animate-pulse" : ""}`} />
            <span>{executing ? "Running..." : "Run Script"}</span>
          </button>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 min-h-0">
        <div className="flex flex-col border border-border rounded-lg bg-card overflow-hidden shadow-sm">
          <div className="p-2 border-b border-border bg-muted/30 flex justify-between items-center">
            <span className="text-xs font-semibold text-muted-foreground px-2">EDITOR</span>
            <FileCode className="w-4 h-4 text-muted-foreground opacity-50" />
          </div>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="flex-1 p-4 bg-[#1e1e1e] text-[#d4d4d4] font-mono text-sm resize-none focus:outline-none leading-relaxed"
            spellCheck={false}
          />
        </div>

        <div className="flex flex-col border border-border rounded-lg bg-card overflow-hidden shadow-sm">
          <div className="p-2 border-b border-border bg-muted/30 flex justify-between items-center">
            <span className="text-xs font-semibold text-muted-foreground px-2">OUTPUT</span>
            <button
              type="button"
              onClick={() => setOutput([])}
              className="p-1 hover:bg-destructive/10 hover:text-destructive rounded transition-colors"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          </div>
          <div className="flex-1 p-4 bg-[#0d1117] font-mono text-sm overflow-y-auto">
            {output.length === 0 && (
              <span className="text-muted-foreground opacity-30 italic">No output...</span>
            )}
            {output.map((line, i) => (
              <div
                key={`output-${i}-${line.substring(0, 5)}`}
                className="text-gray-300 border-b border-white/5 pb-1 mb-1 last:border-0 last:pb-0 last:mb-0"
              >
                {line}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
