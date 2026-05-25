"""Grease Pencil 2D animation tools for Blender MCP."""

import logging

from blender_mcp.app import get_app
from blender_mcp.compat import *

logger = logging.getLogger(__name__)


def _register_grease_pencil_tools():
    app = get_app()

    @app.tool
    async def blender_grease_pencil(
        operation: str = "create",
        name: str = "GPencil",
        gp_object: str = "",
        stroke_type: str = "LINE",
        points: list | None = None,
        layer_name: str = "GP_Layer",
        frame_number: int = 1,
        color: list | None = None,
        thickness: float = 1.0,
        cyclic: bool = False,
        location: list | None = None,
        target_type: str = "MESH",
        keep_original: bool = False,
        width: float = 2.0,
        height: float = 2.0,
        radius: float = 1.0,
        selection_type: str = "ALL",
        material_name: str = "",
        fill_color: list | None = None,
        modifier_type: str = "BUILD",
        modifier_settings: str = "",
        svg_path: str = "",
        before_frames: int = 3,
        after_frames: int = 3,
        interpolation_frames: int = 5,
        from_layer: str = "",
        to_layer: str = "",
    ) -> str:
        """
        PORTMANTEAU RATIONALE:
        Consolidates 12 Grease Pencil 2D animation operations into a single tool.

        **Operations:**
        - **create**: Create a new Grease Pencil object with layer and initial frame
        - **draw_stroke**: Draw strokes (LINE, BOX, CIRCLE, ARC, CURVE) with color/thickness
        - **convert**: Convert Grease Pencil to MESH, CURVE, or new GP strokes
        - **set_material**: Create and assign GP material with stroke/fill color
        - **set_layer**: Create, reorder, lock, toggle visibility of GP layers
        - **animate_stroke**: Keyframe stroke properties (location, rotation, scale) over time
        - **onion_skinning**: Enable/disable onion skin with before/after frame count
        - **add_modifier**: Apply GP modifiers (BUILD, NOISE, SIMPLIFY, SMOOTH)
        - **fill_region**: Fill enclosed stroke regions with color
        - **interpolate**: Generate in-between frames between two GP frames
        - **delete_strokes**: Remove strokes from a GP frame by selection type
        - **list_layers**: List all layers and frame info on a GP object

        Args:
            operation: The GP operation to perform
            name: Name for new GP object (used by: create)
            gp_object: Target GP object name (used by: draw_stroke, convert, set_material, etc.)
            stroke_type: LINE|BOX|CIRCLE|ARC|CURVE (used by: draw_stroke)
            points: Point coordinates for LINE/CURVE strokes (used by: draw_stroke)
            layer_name: Target layer name (used by: draw_stroke, set_layer, animate_stroke)
            frame_number: Frame number for drawing (used by: draw_stroke, interpolate)
            color: RGBA stroke color 0-1 (used by: draw_stroke, set_material)
            thickness: Stroke thickness (used by: draw_stroke)
            cyclic: Close the stroke (used by: draw_stroke)
            location: Placement location (used by: create)
            target_type: MESH|CURVE|GP_STROKES (used by: convert)
            keep_original: Keep original after conversion (used by: convert)
            width: Box width (used by: draw_stroke BOX)
            height: Box height (used by: draw_stroke BOX)
            radius: Circle radius (used by: draw_stroke CIRCLE)
            selection_type: ALL|VISIBLE|INVERT (used by: delete_strokes)
            material_name: Name for new material (used by: set_material)
            fill_color: RGBA fill color 0-1 (used by: set_material, fill_region)
            modifier_type: BUILD|NOISE|SIMPLIFY|SMOOTH (used by: add_modifier)
            modifier_settings: JSON string of modifier settings (used by: add_modifier)
            svg_path: File path to SVG (used by: import_svg)
            before_frames: Frames before current (used by: onion_skinning)
            after_frames: Frames after current (used by: onion_skinning)
            interpolation_frames: Number of in-between frames (used by: interpolate)
            from_layer: Source layer for transfer (used by: set_layer)
            to_layer: Target layer (used by: set_layer)

        Returns:
            str: Operation result with status and details
        """
        from blender_mcp.handlers.grease_pencil_handler import (
            add_gp_modifier,
            animate_gp_stroke,
            convert_grease_pencil,
            create_grease_pencil,
            delete_gp_strokes,
            draw_grease_pencil_stroke,
            fill_gp_region,
            interpolate_gp_frames,
            list_gp_layers,
            onion_skinning_gp,
            set_gp_layer,
            set_gp_material,
        )

        logger.info(f"blender_grease_pencil called: operation='{operation}', name='{name}', gp_object='{gp_object}'")

        try:
            if operation == "create":
                return await create_grease_pencil(
                    name=name,
                    placement="ORIGIN",
                    location={"location": list(location)} if location else None,
                )

            elif operation == "draw_stroke":
                return await draw_grease_pencil_stroke(
                    gp_object=gp_object,
                    stroke_type=stroke_type,
                    points=[tuple(p) for p in points] if points else None,
                    layer_name=layer_name,
                    frame_number=frame_number,
                    color=list(color),
                    thickness=thickness,
                    cyclic=cyclic,
                    width=width,
                    height=height,
                    radius=radius,
                )

            elif operation == "convert":
                return await convert_grease_pencil(
                    gp_object=gp_object,
                    target_type=target_type,
                    keep_original=keep_original,
                )

            elif operation == "set_material":
                return await set_gp_material(
                    gp_object=gp_object,
                    material_name=material_name or f"GP_Mat_{name}",
                    stroke_color=list(color),
                    fill_color=list(fill_color),
                )

            elif operation == "set_layer":
                return await set_gp_layer(
                    gp_object=gp_object,
                    layer_name=layer_name,
                    from_layer=from_layer,
                    to_layer=to_layer,
                )

            elif operation == "animate_stroke":
                return await animate_gp_stroke(
                    gp_object=gp_object,
                    layer_name=layer_name,
                    frame_number=frame_number,
                )

            elif operation == "onion_skinning":
                return await onion_skinning_gp(
                    gp_object=gp_object,
                    before_frames=before_frames,
                    after_frames=after_frames,
                )

            elif operation == "add_modifier":
                return await add_gp_modifier(
                    gp_object=gp_object,
                    modifier_type=modifier_type,
                    settings=modifier_settings,
                )

            elif operation == "fill_region":
                return await fill_gp_region(
                    gp_object=gp_object,
                    layer_name=layer_name,
                    frame_number=frame_number,
                    fill_color=list(fill_color),
                )

            elif operation == "interpolate":
                return await interpolate_gp_frames(
                    gp_object=gp_object,
                    layer_name=layer_name,
                    frame_start=frame_number,
                    frame_end=frame_number + interpolation_frames + 1,
                    num_frames=interpolation_frames,
                )

            elif operation == "delete_strokes":
                return await delete_gp_strokes(
                    gp_object=gp_object,
                    layer_name=layer_name,
                    selection_type=selection_type,
                )

            elif operation == "list_layers":
                return await list_gp_layers(gp_object=gp_object)

            else:
                return f"Unknown operation: {operation}"

        except Exception as e:
            logger.error(f"Error in GP operation '{operation}': {e!s}")
            return f"Error in GP operation '{operation}': {e!s}"


_register_grease_pencil_tools()
