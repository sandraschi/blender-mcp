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

## Error Handling

The example includes basic error handling. If a tool call fails, the error will be logged to the console.
