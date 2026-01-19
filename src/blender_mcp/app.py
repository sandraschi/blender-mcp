"""FastMCP application instance for Blender MCP server."""

# Import from our compatibility module first
from blender_mcp.compat import *

# Initialize FastMCP application with lazy tool discovery
app = None


def get_app():
    """Get or create the FastMCP application instance with lazy initialization."""

    global app
    if app is None:
        from fastmcp import FastMCP

        app = FastMCP(
            name="blender-mcp",
            version="1.0.0",
            instructions="""You are Blender MCP, a comprehensive FastMCP 2.14.3 server for 3D creation and animation using Blender.

FASTMCP 2.14.3 FEATURES:
- Conversational tool returns for natural AI interaction
- Sampling capabilities for agentic workflows and complex 3D operations
- Portmanteau design preventing tool explosion while maintaining full functionality

CORE CAPABILITIES:
- 3D Modeling: Create, modify, and manipulate 3D objects and meshes
- Animation: Set up keyframes, create motion paths, and manage timelines
- Rendering: Configure render settings, materials, lighting, and output
- Scene Management: Organize objects, collections, and scene hierarchies
- Materials & Textures: Create and apply materials, textures, and shaders
- Import/Export: Work with various 3D file formats and interchange standards

CONVERSATIONAL FEATURES:
- Tools return natural language responses alongside structured data
- Sampling allows autonomous orchestration of complex 3D workflows
- Agentic capabilities for intelligent content creation and management

RESPONSE FORMAT:
- All tools return dictionaries with 'success' boolean and 'message' for conversational responses
- Error responses include 'error' field with descriptive message
- Success responses include relevant data fields and natural language summaries

PORTMANTEAU DESIGN:
Tools are consolidated into logical groups to prevent tool explosion while maintaining full functionality.
Each portmanteau tool handles multiple related operations through an 'operation' parameter.
"""
        )

        # Import handlers to register tools (this will register @app.tool decorated functions)

        # Import here to prevent circular imports
        from blender_mcp.tools import discover_tools

        # Discover and register all tools
        discover_tools()

        # Register agentic workflow tools
        from blender_mcp.agentic import register_agentic_tools
        register_agentic_tools()

        # Register resources
        _register_resources(app)

    return app


def _register_resources(app):
    """Register MCP resources for the Blender server."""

    @app.resource("blender://scripts/{category}")
    async def get_script_collection(category: str) -> str:
        """Get a collection of construction scripts for a specific category."""
        try:
            scripts_data = _load_script_collection(category)
            return json.dumps({
                "category": category,
                "scripts": scripts_data,
                "description": f"Collection of {category} construction scripts for Blender",
                "total_scripts": len(scripts_data)
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "error": f"Failed to load {category} scripts",
                "message": str(e)
            })

    @app.resource("blender://scripts/{category}/{script_name}")
    async def get_specific_script(category: str, script_name: str) -> str:
        """Get a specific construction script."""
        try:
            script_data = _load_specific_script(category, script_name)
            return json.dumps(script_data, indent=2)
        except Exception as e:
            return json.dumps({
                "error": f"Failed to load script {script_name} from {category}",
                "message": str(e)
            })


def _load_script_collection(category: str) -> List[Dict[str, Any]]:
    """Load all scripts for a category."""
    # This would load from a scripts database or file system
    # For now, return mock data based on the MCPB configuration
    mock_collections = {
        "robots": [
            {
                "name": "classic_robot",
                "description": "Classic sci-fi robot like Robbie from Forbidden Planet",
                "complexity": "standard",
                "script": "# Mock Blender script for classic robot\nbpy.ops.mesh.primitive_cube_add()\n# Add robot-specific geometry and materials",
                "tags": ["robot", "scifi", "character"]
            },
            {
                "name": "industrial_robot",
                "description": "Industrial robotic arm with articulated joints",
                "complexity": "complex",
                "script": "# Mock Blender script for industrial robot\n# Complex armature and mechanical parts",
                "tags": ["robot", "industrial", "automation"]
            }
        ],
        "furniture": [
            {
                "name": "modern_chair",
                "description": "Modern ergonomic office chair",
                "complexity": "standard",
                "script": "# Mock Blender script for modern chair\n# Curved surfaces and materials",
                "tags": ["furniture", "chair", "office"]
            }
        ],
        "rooms": [
            {
                "name": "living_room",
                "description": "Cozy living room with sofa, TV, and coffee table",
                "complexity": "complex",
                "script": "# Mock Blender script for living room\n# Multiple furniture pieces and layout",
                "tags": ["room", "living", "interior"]
            }
        ],
        "houses": [
            {
                "name": "modern_house",
                "description": "Contemporary single-family home",
                "complexity": "complex",
                "script": "# Mock Blender script for modern house\n# Architectural modeling and texturing",
                "tags": ["house", "architecture", "modern"]
            }
        ],
        "vehicles": [
            {
                "name": "sports_car",
                "description": "High-performance sports car",
                "complexity": "complex",
                "script": "# Mock Blender script for sports car\n# Aerodynamic body and wheel assemblies",
                "tags": ["vehicle", "car", "sports"]
            }
        ],
        "nature": [
            {
                "name": "forest_clearing",
                "description": "Peaceful forest clearing with trees",
                "complexity": "standard",
                "script": "# Mock Blender script for forest clearing\n# Terrain and vegetation placement",
                "tags": ["nature", "forest", "landscape"]
            }
        ]
    }

    return mock_collections.get(category, [])


def _load_specific_script(category: str, script_name: str) -> Dict[str, Any]:
    """Load a specific script by name."""
    collection = _load_script_collection(category)
    for script in collection:
        if script["name"] == script_name:
            return script

    raise ValueError(f"Script '{script_name}' not found in category '{category}'")


# For backward compatibility
app = get_app()
