# Grease Pencil — 2D Animation in blender-mcp

The `blender_grease_pencil` portmanteau tool provides full Grease Pencil 2D animation
capability from any MCP client (Claude Desktop, Cursor, etc.).

## Quick Start

```
blender_grease_pencil(operation="create", name="MySketch")
blender_grease_pencil(operation="draw_stroke", gp_object="MySketch",
    stroke_type="BOX", width=2, height=2, color=[0,0,0,1])
blender_grease_pencil(operation="onion_skinning", gp_object="MySketch",
    before_frames=3, after_frames=3)
blender_grease_pencil(operation="animate_stroke", gp_object="MySketch",
    layer_name="GP_Layer", frame_number=1)
blender_grease_pencil(operation="interpolate", gp_object="MySketch",
    frame_number=1, interpolation_frames=5)
```

## Operations (12)

| Operation | Params | Description |
|-----------|--------|-------------|
| `create` | name, location | Create a new Grease Pencil object |
| `draw_stroke` | gp_object, stroke_type, points, color, thickness, layer, frame | Draw LINE/BOX/CIRCLE/ARC/CURVE strokes |
| `convert` | gp_object, target_type, keep_original | Convert GP to MESH/CURVE/GP_STROKES |
| `set_material` | gp_object, material_name, color, fill_color | Create and assign GP material |
| `set_layer` | gp_object, layer_name | Create, reorder GP layers |
| `animate_stroke` | gp_object, layer_name, frame_number | Keyframe location/rotation/scale |
| `onion_skinning` | gp_object, before_frames, after_frames | Toggle onion skin overlay |
| `add_modifier` | gp_object, modifier_type | BUILD/NOISE/SIMPLIFY/SMOOTH modifiers |
| `fill_region` | gp_object, layer, frame, fill_color | Fill enclosed regions with color |
| `interpolate` | gp_object, layer, frame_number, interpolation_frames | Generate in-between frames |
| `delete_strokes` | gp_object, layer, selection_type | Remove strokes from frame |
| `list_layers` | gp_object | List all layers, frames, stroke counts |

## Stroke Types

| Type | Description | Required Params |
|------|-------------|-----------------|
| `LINE` | Freehand polyline | points ([[x,y,z],...]) |
| `BOX` | Rectangle | width, height |
| `CIRCLE` | Ellipse | radius |
| `ARC` | Arc curve | points |
| `CURVE` | Bezier-like | points |

## Convert Target Types

| Type | Result |
|------|--------|
| `MESH` | GP strokes → editable mesh |
| `CURVE` | GP strokes → bezier/NURBS curve |
| `GP_STROKES` | Evaluate and bake to new GP object |

## Webapp Pages

| Route | Page |
|-------|------|
| `/grease-pencil` | Canvas view, layer panel, brush/material controls, draw/preview |
| `/animation-2d` | Timeline, keyframe editor, onion skin, interpolation, modifiers |
| `/storyboard` | Frame-by-frame storyboard viewer, shot management |

## Fleet Integration

```
tahoma2d-mcp (traditional 2D pipeline)
        │
        ▼
   blender-mcp Grease Pencil (3D-integrated 2D, hybrid scenes)
        │
        ▼
   godot-mcp (2D game sprites, animation sheets)
```

## See Also

- `src/blender_mcp/tools/grease_pencil_tools.py` — MCP tool registration
- `src/blender_mcp/handlers/grease_pencil_handler.py` — Blender Python script handlers
- `webapp/frontend/src/pages/grease-pencil.tsx` — Canvas UI
- `webapp/frontend/src/pages/animation-2d.tsx` — Timeline UI
- `webapp/frontend/src/pages/storyboard.tsx` — Storyboard UI
