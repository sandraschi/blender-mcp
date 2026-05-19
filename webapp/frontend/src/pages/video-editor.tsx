import { Clapperboard, Film, Image, Music, Play, Scissors, Trash2, Video } from "lucide-react";
import { useCallback, useState } from "react";
import { callTool } from "../api/mcp";

type VseStrip = {
  name: string;
  type: string;
  channel: number;
  frame_start: number;
  frame_final_start: number;
  frame_final_end: number;
  mute: boolean;
  lock: boolean;
  blend_type: string;
};

export default function VideoEditor() {
  const [strips, setStrips] = useState<VseStrip[]>([]);
  const [timelineInfo, setTimelineInfo] = useState<Record<string, unknown>>({});
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);

  const [moviePath, setMoviePath] = useState("");
  const [soundPath, setSoundPath] = useState("");
  const [textContent, setTextContent] = useState("");
  const [outPath, setOutPath] = useState("C:/output/video.mp4");
  const [renderFps, setRenderFps] = useState(30);

  const refreshStrips = useCallback(async () => {
    setLoading(true);
    try {
      const r = await callTool("blender_vse", { operation: "list_strips" });
      if (r.success) {
        const data = typeof r.data === "string" ? r.data : JSON.stringify(r.data);
        const match = data.match(/VSE_STRIPS:\s*(\[[\s\S]*\])/);
        if (match) {
          setStrips(JSON.parse(match[1]));
          setOutput("Strips loaded");
        } else if (data.includes("VSE_EMPTY") || data.includes("No strips")) {
          setStrips([]);
          setOutput("No strips in timeline");
        } else {
          setOutput(data);
        }
      } else {
        setOutput(r.error || "Failed to list strips");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const runVse = useCallback(
    async (params: Record<string, unknown>) => {
      setLoading(true);
      try {
        const r = await callTool("blender_vse", params);
        setOutput(r.success ? String(r.data ?? r.message ?? "OK") : String(r.error ?? "Failed"));
        await refreshStrips();
      } finally {
        setLoading(false);
      }
    },
    [refreshStrips],
  );

  const refreshTimeline = useCallback(async () => {
    const r = await callTool("blender_vse", { operation: "get_timeline_info" });
    if (r.success) {
      const data = typeof r.data === "string" ? r.data : JSON.stringify(r.data);
      const match = data.match(/VSE_TIMELINE:\s*(\{[\s\S]*\})/);
      if (match) setTimelineInfo(JSON.parse(match[1]));
    }
  }, []);

  const OperationButton = ({
    label,
    icon: Icon,
    params,
    variant = "default",
  }: {
    label: string;
    icon: React.ElementType;
    params: Record<string, unknown>;
    variant?: "default" | "danger";
  }) => (
    <button
      type="button"
      disabled={loading}
      onClick={() => runVse(params)}
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
        <Clapperboard className="w-8 h-8 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">Video Editor (VSE)</h1>
          <p className="text-sm text-muted-foreground">
            Blender built-in Video Sequence Editor — headless strip management & rendering
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <OperationButton label="List Strips" icon={Film} params={{ operation: "list_strips" }} />
        <OperationButton label="Timeline Info" icon={Play} params={{ operation: "get_timeline_info" }} />
        <OperationButton label="Clear All" icon={Trash2} params={{ operation: "clear_vse" }} variant="danger" />
        <button
          type="button"
          disabled={loading}
          onClick={() => { refreshStrips(); refreshTimeline(); }}
          className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors disabled:opacity-50"
        >
          <Video className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Add Strips */}
      <div className="border border-border rounded-lg p-4 space-y-4 bg-card">
        <h2 className="font-semibold flex items-center space-x-2">
          <Image className="w-5 h-5" />
          <span>Add Strips</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Movie File Path</label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={moviePath}
                onChange={(e) => setMoviePath(e.target.value)}
                placeholder="C:/footage/clip.mp4"
                className="flex-1 px-3 py-2 bg-secondary rounded-lg text-sm border border-border focus:outline-none focus:ring-1 focus:ring-primary"
              />
              <OperationButton label="Add Movie" icon={Video} params={{ operation: "add_movie", filepath: moviePath, channel: 1 }} />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Audio File Path</label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={soundPath}
                onChange={(e) => setSoundPath(e.target.value)}
                placeholder="C:/audio/bgm.wav"
                className="flex-1 px-3 py-2 bg-secondary rounded-lg text-sm border border-border focus:outline-none focus:ring-1 focus:ring-primary"
              />
              <OperationButton label="Add Sound" icon={Music} params={{ operation: "add_sound", filepath: soundPath, channel: 5 }} />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Text Overlay</label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                placeholder="My Title"
                className="flex-1 px-3 py-2 bg-secondary rounded-lg text-sm border border-border focus:outline-none focus:ring-1 focus:ring-primary"
              />
              <OperationButton
                label="Add Text"
                icon={Scissors}
                params={{ operation: "add_text", text: textContent, channel: 3, length: 120, font_size: 48 }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Strip List */}
      <div className="border border-border rounded-lg p-4 space-y-3 bg-card">
        <h2 className="font-semibold flex items-center space-x-2">
          <Film className="w-5 h-5" />
          <span>Timeline Strips ({strips.length})</span>
        </h2>

        {strips.length === 0 ? (
          <p className="text-sm text-muted-foreground">No strips. Add a movie, sound, or text strip to get started.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-muted-foreground">
                  <th className="pb-2 font-medium">Name</th>
                  <th className="pb-2 font-medium">Type</th>
                  <th className="pb-2 font-medium">Channel</th>
                  <th className="pb-2 font-medium">Start</th>
                  <th className="pb-2 font-medium">End</th>
                  <th className="pb-2 font-medium">Mute</th>
                  <th className="pb-2 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {strips.map((s) => (
                  <tr key={s.name} className="border-b border-border/50 hover:bg-secondary/30">
                    <td className="py-2 font-medium">{s.name}</td>
                    <td className="py-2 text-muted-foreground">{s.type}</td>
                    <td className="py-2">{s.channel}</td>
                    <td className="py-2">{s.frame_final_start}</td>
                    <td className="py-2">{s.frame_final_end}</td>
                    <td className="py-2">{s.mute ? "Muted" : "On"}</td>
                    <td className="py-2">
                      <div className="flex space-x-1">
                        <OperationButton
                          label={s.mute ? "Unmute" : "Mute"}
                          icon={s.mute ? Play : Film}
                          params={{ operation: "mute_strip", strip_name: s.name, mute: !s.mute }}
                        />
                        <OperationButton
                          label="Del"
                          icon={Trash2}
                          params={{ operation: "delete_strip", strip_name: s.name }}
                          variant="danger"
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Render */}
      <div className="border border-border rounded-lg p-4 space-y-4 bg-card">
        <h2 className="font-semibold flex items-center space-x-2">
          <Play className="w-5 h-5" />
          <span>Render Video</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Output Path</label>
            <input
              type="text"
              value={outPath}
              onChange={(e) => setOutPath(e.target.value)}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">FPS</label>
            <select
              value={renderFps}
              onChange={(e) => setRenderFps(Number(e.target.value))}
              className="w-full px-3 py-2 bg-secondary rounded-lg text-sm border border-border focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option value={24}>24</option>
              <option value={25}>25</option>
              <option value={30}>30</option>
              <option value={60}>60</option>
            </select>
          </div>
          <div className="flex items-end">
            <OperationButton
              label="Render H264 MP4"
              icon={Play}
              params={{
                operation: "render_video",
                output_path: outPath,
                resolution_x: 1920,
                resolution_y: 1080,
                frame_start: 1,
                frame_end: 300,
                codec: "H264",
                container: "MPEG4",
                fps: renderFps,
                quality: "GOOD",
              }}
            />
          </div>
        </div>
      </div>

      {/* Output */}
      {output && (
        <div className="border border-border rounded-lg p-4 bg-muted/20">
          <p className="text-sm font-mono whitespace-pre-wrap text-muted-foreground">{output}</p>
        </div>
      )}
    </div>
  );
}
