"""
Example: Using Blender MCP in GUI Mode to See Animations

This example demonstrates how to run Blender MCP with the GUI visible,
which is perfect for watching animations, verifying visual results, or
debugging 3D scenes.
"""

import asyncio
from blender_mcp.utils.blender_executor import get_blender_executor

async def create_animated_scene():
    """Create a simple animated scene with GUI visible."""
    
    # IMPORTANT: Set headless=False to enable GUI mode
    executor = get_blender_executor(headless=False)
    
    print("🎬 Creating animated scene with GUI visible...")
    print("⚠️  Note: Blender window will open!")
    
    # Create a script that sets up an animation
    script = """
import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "AnimatedCube"

# Add material
mat = bpy.data.materials.new(name="CubeMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.6, 1.0, 1.0)  # Blue
cube.data.materials.append(mat)

# Setup animation (60 frames)
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 60

# Animate rotation
for frame in range(1, 61):
    bpy.context.scene.frame_set(frame)
    
    # Rotate the cube
    rotation_z = (frame / 60) * 2 * math.pi
    cube.rotation_euler.z = rotation_z
    
    # Move up and down
    cube.location.z = 1 + math.sin(rotation_z) * 0.5
    
    # Insert keyframes
    cube.keyframe_insert(data_path="rotation_euler", index=2)
    cube.keyframe_insert(data_path="location", index=2)

# Add a camera
bpy.ops.object.camera_add(location=(5, -5, 3), rotation=(1.1, 0, 0.785))
bpy.context.scene.camera = bpy.context.active_object

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 2.0

# Set viewport shading to solid
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'

print("✅ Animation created! Press SPACEBAR in Blender to play the animation.")
print("   The cube will rotate and bounce.")
print("   Close Blender window when done.")

# Keep Blender open (comment out for headless mode)
# In GUI mode, Blender stays open until you close it manually
"""
    
    # Execute the script - Blender GUI will open!
    result = await executor.execute_script(script, script_name="animated_scene_gui")
    
    print("\n✅ Script executed! Blender GUI should be visible now.")
    print("   Press SPACEBAR to play the animation")
    print("   Close the Blender window when done")
    
    return result

async def create_simple_render_preview():
    """Create a simple scene and show it in GUI for preview."""
    
    # Enable GUI mode
    executor = get_blender_executor(headless=False)
    
    print("🎨 Creating scene for preview...")
    
    script = """
import bpy

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a suzanne monkey head
bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, 0, 1))
suzanne = bpy.context.active_object

# Add material
mat = bpy.data.materials.new(name="MonkeyMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (1.0, 0.5, 0.2, 1.0)  # Orange
bsdf.inputs["Metallic"].default_value = 0.3
bsdf.inputs["Roughness"].default_value = 0.4
suzanne.data.materials.append(mat)

# Add ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
plane = bpy.context.active_object
plane_mat = bpy.data.materials.new(name="PlaneMaterial")
plane_mat.use_nodes = True
plane_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1.0)
plane.data.materials.append(plane_mat)

# Add camera
bpy.ops.object.camera_add(location=(5, -5, 3), rotation=(1.1, 0, 0.785))
bpy.context.scene.camera = bpy.context.active_object

# Add lights
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 2.0

print("✅ Scene created! You can now preview in Blender GUI.")
print("   Press F12 to render")
print("   Or use the viewport for real-time preview")
"""
    
    result = await executor.execute_script(script, script_name="preview_scene_gui")
    
    print("\n✅ Scene ready in Blender GUI!")
    print("   Press F12 to render the scene")
    print("   Press ESC to cancel render")
    
    return result

if __name__ == "__main__":
    print("=" * 60)
    print("Blender MCP - GUI Mode Example")
    print("=" * 60)
    print()
    print("This example will open Blender with a visible GUI window.")
    print("Choose an option:")
    print("  1. Animated bouncing cube (press SPACEBAR to play)")
    print("  2. Preview scene with Suzanne (press F12 to render)")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(create_animated_scene())
    elif choice == "2":
        asyncio.run(create_simple_render_preview())
    else:
        print("Invalid choice. Running animation example...")
        asyncio.run(create_animated_scene())



