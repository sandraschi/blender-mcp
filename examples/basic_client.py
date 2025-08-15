"""
Basic MCP Client Example for Blender-MCP

This script demonstrates how to connect to a Blender-MCP server and use various tools.
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BlenderMCPClient:
    """A simple client for interacting with the Blender MCP server."""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        """Initialize the MCP client.
        
        Args:
            host: Hostname or IP of the MCP server
            port: Port of the MCP server
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        import aiohttp
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters to pass to the tool
            
        Returns:
            The tool's response as a dictionary
        """
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async with statement.")
            
        url = f"{self.base_url}/tools/{tool_name}"
        
        logger.info(f"Calling tool: {tool_name}")
        logger.debug(f"Parameters: {json.dumps(params, indent=2)}")
        
        try:
            async with self.session.post(url, json=params) as response:
                response_data = await response.json()
                
                if response.status != 200:
                    error_msg = response_data.get('detail', 'Unknown error')
                    logger.error(f"Tool call failed: {error_msg}")
                    return {
                        'status': 'error',
                        'error': error_msg,
                        'status_code': response.status
                    }
                
                logger.debug(f"Response: {json.dumps(response_data, indent=2)}")
                return response_data
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

async def main():
    """Main function to demonstrate MCP client usage."""
    # Create a client instance
    async with BlenderMCPClient() as client:
        # Example 1: Get scene information
        logger.info("\n=== Example 1: Get Scene Information ===")
        result = await client.call_tool("get_scene_info", {})
        logger.info(f"Scene Info: {json.dumps(result, indent=2)}")
        
        # Example 2: Create a cube
        logger.info("\n=== Example 2: Create a Cube ===")
        cube_params = {
            "name": "MyCube",
            "location": [0, 0, 0],
            "size": 2.0
        }
        result = await client.call_tool("create_cube", cube_params)
        logger.info(f"Created cube: {result}")
        
        # Example 3: Enable physics on the cube
        logger.info("\n=== Example 3: Enable Physics on Cube ===")
        physics_params = {
            "object_name": "MyCube",
            "physics_type": "RIGID_BODY",
            "mass": 1.0,
            "friction": 0.5,
            "bounciness": 0.3,
            "collision_shape": "BOX"
        }
        result = await client.call_tool("enable_physics", physics_params)
        logger.info(f"Physics enabled: {result}")
        
        # Example 4: Bake physics simulation
        logger.info("\n=== Example 4: Bake Physics Simulation ===")
        bake_params = {
            "frame_start": 1,
            "frame_end": 50,
            "step": 1,
            "only_selected": False,
            "clear_cached": True
        }
        result = await client.call_tool("bake_physics_simulation", bake_params)
        logger.info(f"Bake result: {result}")
        
        # Example 5: Set up a simple render
        logger.info("\n=== Example 5: Set Up Render ===")
        render_params = {
            "resolution_x": 1920,
            "resolution_y": 1080,
            "resolution_percentage": 100,
            "engine": "CYCLES",
            "samples": 128,
            "use_denoising": True
        }
        result = await client.call_tool("setup_render", render_params)
        logger.info(f"Render setup: {result}")

if __name__ == "__main__":
    asyncio.run(main())
