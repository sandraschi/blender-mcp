import { useState } from "react";

type TabKey = "vse" | "grease-pencil" | "mesh" | "animation" | "splatting" | "vrm";

const tabs: { key: TabKey; label: string }[] = [
  { key: "vse", label: "Video Editor (VSE)" },
  { key: "grease-pencil", label: "Grease Pencil" },
  { key: "mesh", label: "Mesh & Primitives" },
  { key: "animation", label: "Animation & Rigging" },
  { key: "splatting", label: "Gaussian Splats" },
  { key: "vrm", label: "VRM Avatars" },
];

const content: Record<TabKey, { title: string; sections: { heading: string; lines: string[] }[] }> = {
  "vse": {
    title: "Video Sequence Editor",
    sections: [
      {
        heading: "Overview",
        lines: [
          "The blender_vse tool provides Blender's built-in VSE for headless video editing.",
          "Supports: video/audio/image/text strips, transitions, effects, rendering.",
          "30+ operations — list, add, cut, mute, delete, render.",
        ],
      },
      {
        heading: "Common Operations",
        lines: [
          "blender_vse(operation='list_strips') — list timeline",
          "blender_vse(operation='add_movie', filepath=..., channel=1) — add clip",
          "blender_vse(operation='add_text', text='Title', channel=3) — text overlay",
          "blender_vse(operation='render_video', output_path=..., fps=30) — render MP4",
          "blender_vse(operation='add_effect', effect_type='CROSS') — crossfade",
        ],
      },
      {
        heading: "Output Formats",
        lines: [
          "H264 / H265 MP4 — GOOD, HIGH, LOSSLESS quality",
          "DNxHD MOV — Pro video workflows",
          "ProRes — Apple ecosystem",
          "PNG / JPEG sequence — frame-by-frame output",
        ],
      },
    ],
  },
  "grease-pencil": {
    title: "Grease Pencil 2D Animation",
    sections: [
      {
        heading: "Overview",
        lines: [
          "The blender_grease_pencil tool provides Grease Pencil 2D drawing and animation.",
          "12 operations: create, draw, convert, material, layer, keyframe, onion skin, modifiers, fill, interpolate.",
        ],
      },
      {
        heading: "Common Operations",
        lines: [
          "blender_grease_pencil(operation='create', name='Sketch') — new GP object",
          "blender_grease_pencil(operation='draw_stroke', gp_object='Sketch', stroke_type='BOX')",
          "blender_grease_pencil(operation='set_material', gp_object='Sketch', color=[0,0,0,1])",
          "blender_grease_pencil(operation='onion_skinning', gp_object='Sketch', before_frames=3)",
          "blender_grease_pencil(operation='animate_stroke', gp_object='Sketch', frame_number=1)",
          "blender_grease_pencil(operation='interpolate', gp_object='Sketch', interpolation_frames=5)",
        ],
      },
      {
        heading: "Convert Types",
        lines: [
          "MESH — strokes to editable mesh geometry",
          "CURVE — strokes to bezier/NURBS curves",
          "GP_STROKES — evaluated stroke bake to new GP object",
        ],
      },
    ],
  },
  "mesh": {
    title: "Mesh & Primitives",
    sections: [
      {
        heading: "Overview",
        lines: [
          "The blender_mesh tool creates and manipulates mesh primitives.",
          "9 operations: cube, sphere, cylinder, cone, plane, torus, monkey, duplicate, delete.",
        ],
      },
      {
        heading: "Examples",
        lines: [
          "blender_mesh(operation='create_cube', name='Box', location=(0,0,0))",
          "blender_mesh(operation='create_sphere', name='Ball', radius=2, vertices=64)",
          "blender_mesh(operation='duplicate_object', name='Copy', source_name='Original')",
        ],
      },
    ],
  },
  "animation": {
    title: "Animation & Rigging",
    sections: [
      {
        heading: "Overview",
        lines: [
          "blender_animation — 21 operations: keyframes, playback, actions, baking, NLA.",
          "blender_rigging — 12 operations: armatures, bones, IK, VRM humanoid.",
        ],
      },
      {
        heading: "Keyframe Tools",
        lines: [
          "blender_animation(operation='set_keyframe', object='Cube', property='location')",
          "blender_animation(operation='insert_keyframe', object='Cube', frame=1)",
          "blender_animation(operation='bake_animation', object='Cube')",
        ],
      },
    ],
  },
  "splatting": {
    title: "Gaussian Splatting",
    sections: [
      {
        heading: "Overview",
        lines: [
          "blender_splatting provides Gaussian Splat import, crop, collision mesh, and export.",
          "6+ operations: import, worldlabs, export, collision mesh, crop, set_alpha.",
        ],
      },
      {
        heading: "Examples",
        lines: [
          "blender_splatting(operation='import_gs', file_path='scene.ply')",
          "blender_splatting(operation='worldlabs', file_path='world.spz')",
          "blender_splatting(operation='collision_mesh', file_path='scene.ply')",
        ],
      },
    ],
  },
  "vrm": {
    title: "VRM Avatars",
    sections: [
      {
        heading: "Overview",
        lines: [
          "End-to-end VRM avatar pipeline: import, rig, export for VRChat and Resonite.",
          "blender_vrm_metadata — VRM metadata management.",
          "VR Pipeline page uses blender_mesh + blender_rigging for avatar creation.",
        ],
      },
      {
        heading: "Workflow",
        lines: [
          "1. Import VRM: blender_vrm_metadata(operation='import', path='avatar.vrm')",
          "2. Add animations: blender_animation(operation='set_keyframe', ...)",
          "3. Export: blender_export(operation='export_vrm', name='avatar_animated')",
        ],
      },
    ],
  },
};

export default function Help() {
  const [activeTab, setActiveTab] = useState<TabKey>("vse");

  const tab = content[activeTab];

  return (
    <div className="p-6 space-y-6 max-w-5xl">
      <h1 className="text-2xl font-bold">Blender MCP Reference</h1>
      <p className="text-sm text-muted-foreground">Tool documentation and usage guides by discipline.</p>

      <div className="flex flex-wrap gap-2 border-b border-border pb-2">
        {tabs.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => setActiveTab(t.key)}
            className={`px-4 py-2 rounded-t-lg text-sm font-medium transition-colors ${
              activeTab === t.key
                ? "bg-primary text-primary-foreground"
                : "bg-accent text-muted-foreground hover:text-foreground"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="space-y-6">
        <h2 className="text-xl font-semibold">{tab.title}</h2>
        {tab.sections.map((section) => (
          <div key={section.heading} className="border border-border rounded-lg p-4 bg-card space-y-2">
            <h3 className="font-medium text-primary">{section.heading}</h3>
            <ul className="space-y-1">
              {section.lines.map((line, i) => (
                <li key={i} className="text-sm text-muted-foreground">
                  {line.startsWith("blender_") || line.startsWith("  blender_") ? (
                    <code className="text-xs bg-muted px-1.5 py-0.5 rounded">{line}</code>
                  ) : (
                    line
                  )}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
