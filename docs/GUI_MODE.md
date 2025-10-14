# 🎬 Blender MCP - GUI Mode

## Overview

Blender MCP supports **both headless and GUI modes**:

- **Headless Mode** (default): Runs Blender in the background without a window - perfect for automation and servers
- **GUI Mode**: Opens Blender with the full graphical interface - perfect for watching animations, previewing renders, and visual debugging

## When to Use Each Mode

### 🚀 **Headless Mode** (Default)
**Best for:**
- ✅ Server deployments
- ✅ CI/CD pipelines
- ✅ Batch processing
- ✅ Automation scripts
- ✅ Background rendering
- ✅ Docker containers
- ✅ Cloud environments

**Command:** `blender.exe --background --factory-startup --python script.py`

### 🎨 **GUI Mode**
**Best for:**
- ✅ **Watching animations** play in real-time
- ✅ **Previewing renders** before final output
- ✅ Visual debugging and verification
- ✅ Interactive scene exploration
- ✅ Learning and experimentation
- ✅ Manual adjustments

**Command:** `blender.exe --factory-startup --python script.py`

## How to Enable GUI Mode

### Method 1: Using `get_blender_executor()`

```python
from blender_mcp.utils.blender_executor import get_blender_executor

# Headless mode (default)
executor = get_blender_executor()  # or get_blender_executor(headless=True)

# GUI mode - Blender window will open!
executor = get_blender_executor(headless=False)
```

### Method 2: Direct BlenderExecutor instantiation

```python
from blender_mcp.utils.blender_executor import BlenderExecutor

# Headless mode (default)
executor = BlenderExecutor()  # or BlenderExecutor(headless=True)

# GUI mode
executor = BlenderExecutor(headless=False)
```

## Complete Example: Animated Scene with GUI

```python
import asyncio
from blender_mcp.utils.blender_executor import get_blender_executor

async def create_animated_cube():
    # Enable GUI mode
    executor = get_blender_executor(headless=False)
    
    script = """
import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create animated cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.active_object

# Setup 60-frame animation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 60

# Animate rotation and bounce
for frame in range(1, 61):
    bpy.context.scene.frame_set(frame)
    rotation = (frame / 60) * 2 * math.pi
    cube.rotation_euler.z = rotation
    cube.location.z = 1 + math.sin(rotation) * 0.5
    cube.keyframe_insert(data_path="rotation_euler", index=2)
    cube.keyframe_insert(data_path="location", index=2)

# Add camera and lighting
bpy.ops.object.camera_add(location=(5, -5, 3))
bpy.context.scene.camera = bpy.context.active_object
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))

print("Press SPACEBAR to play animation!")
"""
    
    await executor.execute_script(script, script_name="animated_cube")
    print("Blender GUI is open - press SPACEBAR to play animation!")

asyncio.run(create_animated_cube())
```

## Keyboard Shortcuts in Blender GUI

Once the GUI opens, you can use these shortcuts:

### Animation Control
- **SPACEBAR** - Play/pause animation
- **LEFT/RIGHT ARROW** - Step through frames
- **SHIFT + LEFT/RIGHT ARROW** - Jump to first/last frame
- **ALT + A** - Play animation (alternative)

### Rendering
- **F12** - Render current frame
- **CTRL + F12** - Render animation
- **ESC** - Cancel render
- **F11** - View last render

### Viewport Navigation
- **MIDDLE MOUSE** - Rotate view
- **SHIFT + MIDDLE MOUSE** - Pan view
- **SCROLL WHEEL** - Zoom in/out
- **NUMPAD 0** - Camera view
- **NUMPAD 7** - Top view
- **NUMPAD 1** - Front view
- **NUMPAD 3** - Side view

### Other Useful Shortcuts
- **Z** - Shading menu (Solid, Material Preview, Rendered)
- **N** - Toggle properties panel
- **T** - Toggle tools panel
- **HOME** - Frame all objects
- **NUMPAD .** - Frame selected object

## Configuration Options

### Environment Variable
You can set a default mode via environment variable:

```bash
# Windows
set BLENDER_GUI_MODE=true

# Linux/Mac
export BLENDER_GUI_MODE=true
```

### Code Configuration
```python
# Always use GUI for debugging
import os
os.environ['BLENDER_GUI_MODE'] = 'true'

from blender_mcp.utils.blender_executor import get_blender_executor
executor = get_blender_executor()  # Will use GUI if env var is set
```

## Performance Considerations

### GUI Mode
- **Pros:**
  - Visual feedback
  - Real-time preview
  - Interactive debugging
  - Better for learning

- **Cons:**
  - Slower execution (rendering overhead)
  - Requires display
  - Higher memory usage
  - Not suitable for servers

### Headless Mode
- **Pros:**
  - Faster execution
  - Lower memory usage
  - Works on servers
  - Perfect for automation

- **Cons:**
  - No visual feedback
  - Harder to debug visually
  - Can't preview animations interactively

## Troubleshooting

### Issue: GUI doesn't open
**Solution:** Make sure you're not on a headless server and have a display available.

### Issue: Blender crashes on GUI mode
**Solution:** Check your graphics drivers are up to date.

### Issue: Want to switch between modes
```python
# Reset the singleton to switch modes
from blender_mcp.utils import blender_executor
blender_executor._blender_executor_instance = None

# Now get new executor with different mode
executor = get_blender_executor(headless=False)
```

## Best Practices

1. **Use headless for production:** Always use headless mode in production/server environments
2. **Use GUI for development:** Use GUI mode during development to verify results
3. **Test both modes:** Test your scripts in both modes to ensure compatibility
4. **Close Blender GUI:** Remember to close the Blender window when done in GUI mode
5. **Timeout considerations:** GUI mode may need longer timeouts for interactive work

## Example Scripts

Check out these example scripts:
- `examples/gui_mode_example.py` - Complete GUI mode examples
- `examples/basic_client.py` - Basic usage (headless)

## See Also

- [Main README](../README.md)
- [Tool Reference](TOOL_REFERENCE.md)
- [Examples Directory](../examples/)

