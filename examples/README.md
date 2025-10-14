# Blender-MCP Examples

This directory contains example code demonstrating how to use the Blender-MCP server.

## Basic Client Example

The `basic_client.py` script shows how to connect to a Blender-MCP server and interact with various tools.

### Prerequisites

- Python 3.8+
- Required packages (install with `pip install -r requirements.txt`):
  - aiohttp
  - asyncio

### Running the Example

1. Start the Blender-MCP server in Blender
2. Run the example client:
   ```bash
   python examples/basic_client.py
   ```

### What the Example Does

The example demonstrates:

1. Connecting to the MCP server
2. Getting scene information
3. Creating a cube
4. Enabling physics on the cube
5. Baking a physics simulation
6. Setting up a simple render

### Output

The script will log its progress to the console. You should see output like:

```
2023-04-01 12:00:00,000 - __main__ - INFO - === Example 1: Get Scene Information ===
2023-04-01 12:00:00,100 - __main__ - INFO - Scene Info: {...}
2023-04-01 12:00:00,200 - __main__ - INFO - === Example 2: Create a Cube ===
...
```

## Extending the Example

You can modify the `main()` function in `basic_client.py` to call different tools or pass different parameters. Refer to the Blender-MCP documentation for a complete list of available tools and their parameters.

## Download Tools Example

The `download_example.py` script demonstrates how to use the download tools to fetch assets from URLs and import them into Blender scenes.

### Prerequisites

- Same prerequisites as basic client
- Internet connection for downloading files

### Running the Download Example

```bash
python examples/download_example.py
```

### What the Download Example Shows

The example demonstrates:

1. **Supported file formats** for download and import
2. **Example commands** for different file types
3. **Advanced usage** with custom filenames and timeouts
4. **Katana-specific examples** for downloading 3D assets

### Download Tool Capabilities

The `blender_download` tool can:

- Download files from HTTP/HTTPS URLs
- Automatically detect file types (.obj, .fbx, .png, etc.)
- Import 3D models, textures, and other assets into Blender
- Handle large files with progress indication
- Provide flexible import options

### Example Usage

```python
# Download and import a Katana model
await blender_download("https://example.com/katana.fbx")

# Download texture without importing
await blender_download("https://example.com/texture.png", import_into_scene=False)
```

## Error Handling

The example includes basic error handling. If a tool call fails, the error will be logged to the console.
