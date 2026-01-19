"""Blender MCP Help System.

This module provides a comprehensive help system that documents all available
operations in the Blender MCP server. It's designed to be used by both users
and AI assistants to understand the available functionality.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from blender_mcp.compat import *

from ..compat import *


@dataclass
class ParameterInfo:
    """Information about a function parameter."""

    name: str
    type: str
    default: Any = ""
    description: str = ""
    required: bool = False


@dataclass
class FunctionInfo:
    """Information about an available function."""

    name: str
    description: str
    parameters: List[ParameterInfo] = field(default_factory=list)
    returns: str = ""
    example: str = ""
    category: str = "General"


class HelpSystem:
    """Help system for the Blender MCP server."""

    def __init__(self):
        self.functions: Dict[str, FunctionInfo] = {}
        self._initialize_help()

    def _initialize_help(self):
        """Initialize the help system with all available functions."""
        # Mesh Handler Functions
        self._add_function(
            FunctionInfo(
                name="create_vanity_table",
                category="Mesh Creation",
                description="Create a vanity table with mirror, drawers, and legs.",
                parameters=[
                    ParameterInfo("name", "str", "'VanityTable'", "Name of the object"),
                    ParameterInfo("x", "float", "0.0", "X position"),
                    ParameterInfo("y", "float", "0.0", "Y position"),
                    ParameterInfo("z", "float", "0.0", "Z position"),
                    ParameterInfo(
                        "style", "str", "'art_deco'", "Style: 'art_deco', 'victorian', 'modern'"
                    ),
                ],
                returns="str: Name of the created object",
                example="create_vanity_table('MyTable', 0, 0, 0, 'modern')",
            )
        )

        self._add_function(
            FunctionInfo(
                name="create_candle_set",
                category="Mesh Creation",
                description="Create a set of candles with holders and optional flames.",
                parameters=[
                    ParameterInfo("name", "str", "'CandleSet'", "Name of the object"),
                    ParameterInfo("x", "float", "0.0", "X position"),
                    ParameterInfo("y", "float", "0.0", "Y position"),
                    ParameterInfo("z", "float", "0.0", "Z position"),
                    ParameterInfo("count", "int", "3", "Number of candles"),
                    ParameterInfo(
                        "style", "str", "'elegant'", "Style: 'elegant', 'romantic', 'minimal'"
                    ),
                ],
                returns="str: Name of the created object collection",
            )
        )

        self._add_function(
            FunctionInfo(
                name="create_ornate_mirror",
                category="Mesh Creation",
                description="Create an ornate mirror with decorative frame.",
                parameters=[
                    ParameterInfo("name", "str", "'OrnateMirror'", "Name of the object"),
                    ParameterInfo("x", "float", "0.0", "X position"),
                    ParameterInfo("y", "float", "0.0", "Y position"),
                    ParameterInfo("z", "float", "0.0", "Z position"),
                    ParameterInfo(
                        "style", "str", "'baroque'", "Style: 'baroque', 'art_nouveau', 'modern'"
                    ),
                ],
                returns="str: Name of the created object",
            )
        )

        self._add_function(
            FunctionInfo(
                name="create_feather_duster",
                category="Mesh Creation",
                description="Create a feather duster with realistic feathers.",
                parameters=[
                    ParameterInfo("name", "str", "'FeatherDuster'", "Name of the object"),
                    ParameterInfo("x", "float", "0.0", "X position"),
                    ParameterInfo("y", "float", "0.0", "Y position"),
                    ParameterInfo("z", "float", "0.0", "Z position"),
                    ParameterInfo(
                        "style", "str", "'classic'", "Style: 'classic', 'fluffy', 'exotic'"
                    ),
                ],
                returns="str: Name of the created object",
            )
        )

        # Material Handler Functions
        self._add_function(
            FunctionInfo(
                name="create_fabric_material",
                category="Material Creation",
                description="Create a fabric material with various presets.",
                parameters=[
                    ParameterInfo("name", "str", "'FabricMaterial'", "Name of the material"),
                    ParameterInfo(
                        "fabric_type",
                        "str",
                        "'cotton'",
                        "Type: 'cotton', 'silk', 'velvet', 'wool', 'leather', 'denim'",
                    ),
                    ParameterInfo(
                        "color", "tuple[float, float, float]", "(0.8, 0.1, 0.3)", "RGB color (0-1)"
                    ),
                    ParameterInfo("roughness", "float", "0.7", "Surface roughness (0-1)"),
                ],
                returns="str: Name of the created material",
            )
        )

        self._add_function(
            FunctionInfo(
                name="create_metal_material",
                category="Material Creation",
                description="Create a metal material with various presets.",
                parameters=[
                    ParameterInfo("name", "str", "'MetalMaterial'", "Name of the material"),
                    ParameterInfo(
                        "metal_type",
                        "str",
                        "'gold'",
                        "Type: 'gold', 'silver', 'copper', 'iron', 'aluminum', 'titanium', 'platinum', 'brass', 'bronze', 'chrome', 'steel', 'tungsten'",
                    ),
                    ParameterInfo("roughness", "float", "0.1", "Surface roughness (0-1)"),
                    ParameterInfo("anisotropic", "float", "0.0", "Anisotropic effect (0-1)"),
                ],
                returns="str: Name of the created material",
            )
        )

        self._add_function(
            FunctionInfo(
                name="create_wood_material",
                category="Material Creation",
                description="Create a wood material with realistic grain.",
                parameters=[
                    ParameterInfo("name", "str", "'WoodMaterial'", "Name of the material"),
                    ParameterInfo(
                        "wood_type",
                        "str",
                        "'oak'",
                        "Type: 'oak', 'mahogany', 'pine', 'walnut', 'cherry', 'maple'",
                    ),
                    ParameterInfo("grain_scale", "float", "5.0", "Scale of wood grain (0.1-20.0)"),
                    ParameterInfo("roughness", "float", "0.7", "Surface roughness (0-1)"),
                    ParameterInfo("bump_strength", "float", "0.1", "Bump strength (0-1)"),
                ],
                returns="str: Name of the created material",
            )
        )

        # Export Handler Functions
        self._add_function(
            FunctionInfo(
                name="export_for_unity",
                category="Export",
                description="Export the current scene for Unity3D.",
                parameters=[
                    ParameterInfo(
                        "output_path", "str", required=True, description="Path to save the FBX file"
                    ),
                    ParameterInfo("scale", "float", "1.0", "Scale factor for the exported model"),
                    ParameterInfo(
                        "apply_modifiers",
                        "bool",
                        "True",
                        "Whether to apply modifiers before export",
                    ),
                    ParameterInfo(
                        "optimize_materials",
                        "bool",
                        "True",
                        "Whether to optimize materials for Unity",
                    ),
                    ParameterInfo("bake_textures", "bool", "False", "Whether to bake textures"),
                    ParameterInfo(
                        "lod_levels", "int", "0", "Number of LOD levels to generate (0 = no LOD)"
                    ),
                ],
                returns="str: Success message with export details",
            )
        )

        self._add_function(
            FunctionInfo(
                name="export_for_vrchat",
                category="Export",
                description="Export the current scene for VRChat with performance limits.",
                parameters=[
                    ParameterInfo(
                        "output_path", "str", required=True, description="Path to save the VRM file"
                    ),
                    ParameterInfo("polygon_limit", "int", "20000", "Maximum allowed polygons"),
                    ParameterInfo("material_limit", "int", "8", "Maximum allowed materials"),
                    ParameterInfo(
                        "texture_size_limit", "int", "1024", "Maximum texture size in pixels"
                    ),
                    ParameterInfo("performance_rank", "str", "'Good'", "Target performance rank"),
                ],
                returns="str: Success message with export details",
            )
        )

        # Render Handler Functions
        self._add_function(
            FunctionInfo(
                name="render_preview",
                category="Rendering",
                description="Render a high-quality preview of the current scene.",
                parameters=[
                    ParameterInfo(
                        "output_path",
                        "str",
                        required=True,
                        description="Path to save the rendered image",
                    ),
                    ParameterInfo("resolution_x", "int", "1920", "Horizontal resolution in pixels"),
                    ParameterInfo("resolution_y", "int", "1080", "Vertical resolution in pixels"),
                    ParameterInfo("samples", "int", "256", "Number of samples per pixel"),
                    ParameterInfo("use_denoising", "bool", "True", "Whether to use AI denoising"),
                    ParameterInfo("format", "str", "'PNG'", "Output image format"),
                    ParameterInfo("quality", "int", "90", "Output quality (1-100)"),
                ],
                returns="str: Success message with render details",
            )
        )

        self._add_function(
            FunctionInfo(
                name="render_turntable",
                category="Rendering",
                description="Render a 360-degree turntable animation of the current scene.",
                parameters=[
                    ParameterInfo(
                        "output_dir",
                        "str",
                        required=True,
                        description="Directory to save rendered frames",
                    ),
                    ParameterInfo("frames", "int", "60", "Number of frames for the animation"),
                    ParameterInfo("resolution_x", "int", "1280", "Horizontal resolution in pixels"),
                    ParameterInfo("resolution_y", "int", "720", "Vertical resolution in pixels"),
                    ParameterInfo("format", "str", "'PNG'", "Output image format"),
                ],
                returns="str: Success message with render details",
            )
        )

        # Help and Status Tools
        self._add_function(
            FunctionInfo(
                name="blender_help",
                category="Help & Documentation",
                description="Get comprehensive help for Blender MCP tools and functions.",
                parameters=[
                    ParameterInfo(
                        "function_name",
                        "Optional[str]",
                        "None",
                        "Name of specific function to get help for",
                    ),
                    ParameterInfo(
                        "category", "Optional[str]", "None", "Category to filter help by"
                    ),
                ],
                returns="str: Formatted help text with function signatures and examples",
                example="blender_help('create_cube') or blender_help(category='Mesh Creation')",
            )
        )

        self._add_function(
            FunctionInfo(
                name="blender_list_tools",
                category="Help & Documentation",
                description="List all available Blender MCP tools with descriptions.",
                parameters=[
                    ParameterInfo(
                        "category", "Optional[str]", "None", "Category to filter tools by"
                    )
                ],
                returns="Dict: Tools organized by categories with descriptions",
                example="blender_list_tools('Mesh Creation')",
            )
        )

        self._add_function(
            FunctionInfo(
                name="blender_search_tools",
                category="Help & Documentation",
                description="Search for Blender MCP tools by name or description.",
                parameters=[
                    ParameterInfo(
                        "query",
                        "str",
                        required=True,
                        description="Search term to match against tool names and descriptions",
                    )
                ],
                returns="Dict: Matching tools grouped by relevance (exact, name, description)",
                example="blender_search_tools('cube')",
            )
        )

        self._add_function(
            FunctionInfo(
                name="blender_tool_info",
                category="Help & Documentation",
                description="Get detailed information about a specific Blender MCP tool.",
                parameters=[
                    ParameterInfo(
                        "tool_name",
                        "str",
                        required=True,
                        description="Name of the tool to get information about",
                    )
                ],
                returns="Dict: Comprehensive tool information including parameters and usage",
                example="blender_tool_info('create_cube')",
            )
        )

        self._add_function(
            FunctionInfo(
                name="blender_categories",
                category="Help & Documentation",
                description="Get information about all available tool categories.",
                parameters=[],
                returns="Dict: All categories with tool counts and examples",
                example="blender_categories()",
            )
        )

        self._add_function(
            FunctionInfo(
                name="blender_status",
                category="System Status",
                description="Get comprehensive system status and health information.",
                parameters=[
                    ParameterInfo(
                        "include_blender_info",
                        "bool",
                        "True",
                        "Include Blender-specific information",
                    ),
                    ParameterInfo(
                        "include_system_info", "bool", "True", "Include general system information"
                    ),
                    ParameterInfo(
                        "include_performance", "bool", "True", "Include performance metrics"
                    ),
                ],
                returns="Dict: Complete system status including MCP server, Blender, and performance data",
                example="blender_status()",
            )
        )

        self._add_function(
            FunctionInfo(
                name="blender_system_info",
                category="System Status",
                description="Get detailed system and environment information.",
                parameters=[],
                returns="Dict: Detailed system information including Python packages and configuration",
                example="blender_system_info()",
            )
        )

        self._add_function(
            FunctionInfo(
                name="blender_health_check",
                category="System Status",
                description="Perform a comprehensive health check of the Blender MCP system.",
                parameters=[],
                returns="Dict: Health check results with status indicators for all components",
                example="blender_health_check()",
            )
        )

        self._add_function(
            FunctionInfo(
                name="blender_performance_monitor",
                category="System Status",
                description="Monitor system performance over a specified duration.",
                parameters=[
                    ParameterInfo(
                        "duration_seconds", "int", "10", "How long to monitor (max 60 seconds)"
                    )
                ],
                returns="Dict: Performance monitoring results with samples and summary statistics",
                example="blender_performance_monitor(30)",
            )
        )

        # Object Repository Tools
        self._add_function(
            FunctionInfo(
                name="manage_object_repo",
                category="Object Repository",
                description="Complete object repository management with save, load, search, and versioning capabilities.",
                parameters=[
                    ParameterInfo(
                        "operation", "str", "list_objects", "Operation to perform (save/load/search/list_objects)"
                    ),
                    ParameterInfo(
                        "object_name", "str", "", "Blender object name (for save)"
                    ),
                    ParameterInfo(
                        "object_name_display", "str", "", "Display name for saved objects"
                    ),
                    ParameterInfo(
                        "object_id", "str", "", "Repository ID (for load)"
                    ),
                    ParameterInfo(
                        "query", "str | None", "None", "Search query"
                    ),
                    ParameterInfo(
                        "category", "str", "'general'", "Object category"
                    ),
                    ParameterInfo(
                        "limit", "int", "20", "Maximum results"
                    ),
                    ParameterInfo(
                        "description", "str", "", "Detailed description of the model"
                    ),
                    ParameterInfo(
                        "tags", "List[str]", "[]", "Tags for categorization and search"
                    ),
                    ParameterInfo(
                        "category", "str", "'general'", "Organizational category"
                    ),
                    ParameterInfo(
                        "construction_script", "str | None", "None", "Original construction script"
                    ),
                    ParameterInfo(
                        "quality_rating", "int", "5", "Quality rating 1-10"
                    ),
                    ParameterInfo(
                        "public", "bool", "False", "Make model publicly available"
                    ),
                ],
                returns="Dict: Repository operation results with appropriate data",
                example="manage_object_repo('save', object_name='Robot', object_name_display='Robbie Robot', quality_rating=9)",
            )
        )


        # AI Construction Tools
        self._add_function(
            FunctionInfo(
                name="manage_object_construction",
                category="AI Construction",
                description="AI-powered object construction and modification using natural language and LLM-generated Blender scripts.",
                parameters=[
                    ParameterInfo(
                        "operation", "str", "construct", "Operation to perform (construct/modify)"
                    ),
                    ParameterInfo(
                        "description", "str", "", "Natural language description (for construct)"
                    ),
                    ParameterInfo(
                        "object_name", "str", "", "Existing object name (for modify)"
                    ),
                    ParameterInfo(
                        "modification_description", "str", "", "Modification description (for modify)"
                    ),
                    ParameterInfo(
                        "complexity", "str", "'standard'", "Complexity level"
                    ),
                    ParameterInfo(
                        "max_iterations", "int", "3", "Maximum refinement iterations"
                    ),
                ],
                returns="Dict: Construction/modification results with object info and next steps",
                example="manage_object_construction('construct', description='a robot like Robbie from Forbidden Planet')",
            )
        )

        # Object Repository Tools
        self._add_function(
            FunctionInfo(
                name="construct_object",
                category="AI Construction",
                description="Universal 3D object construction using natural language and LLM-generated Blender scripts.",
                parameters=[
                    ParameterInfo(
                        "description",
                        "str",
                        required=True,
                        description="Natural language description of the object to create"
                    ),
                    ParameterInfo(
                        "name", "str", "'ConstructedObject'", "Name for the created object in Blender scene"
                    ),
                    ParameterInfo(
                        "complexity", "str", "'standard'", "Complexity level (simple/standard/complex)"
                    ),
                    ParameterInfo(
                        "style_preset", "Optional[str]", "None", "Style preset (realistic/stylized/lowpoly/scifi)"
                    ),
                    ParameterInfo(
                        "reference_objects", "Optional[List[str]]", "None", "Existing objects to use as reference"
                    ),
                    ParameterInfo(
                        "allow_modifications", "bool", "True", "Whether LLM can modify existing objects"
                    ),
                    ParameterInfo(
                        "max_iterations", "int", "3", "Maximum refinement iterations"
                    ),
                ],
                returns="Dict: Construction results with success status, object info, and next steps",
                example="construct_object('a robot like Robbie from Forbidden Planet', complexity='complex')",
            )
        )

        # Cross-MCP Export Tools
        self._add_function(
            FunctionInfo(
                name="export_for_mcp_handoff",
                description="Export Blender assets with platform-specific optimizations for seamless cross-MCP handoff",
                category="Repository & Export",
                parameters=[
                    ParameterInfo(
                        "asset_id", "str", required=True, description="ID of asset to export from repository"
                    ),
                    ParameterInfo(
                        "target_mcp", "str", required=True, description="Target MCP server (vrchat, resonite, unity, unreal)"
                    ),
                    ParameterInfo(
                        "optimization_preset", "str", "'automatic'", "Optimization approach (automatic/conservative/aggressive)"
                    ),
                    ParameterInfo(
                        "quality_level", "str", "'high'", "Quality vs speed (draft/standard/high/ultra)"
                    ),
                    ParameterInfo(
                        "include_metadata", "bool", "True", "Include integration metadata for target MCP"
                    ),
                ],
                returns="Dict: Export results with file paths, integration commands, and platform metadata",
                example="export_for_mcp_handoff('robot_001', 'vrchat', optimization_preset='automatic', quality_level='high')",
            )
        )

    def _add_function(self, func_info: FunctionInfo):
        """Add a function to the help system."""
        self.functions[func_info.name] = func_info

    def get_function(self, name: str) -> Optional[FunctionInfo]:
        """Get information about a specific function."""
        return self.functions.get(name)

    def list_functions(self, category: Optional[str] = None) -> List[FunctionInfo]:
        """List all available functions, optionally filtered by category."""
        if category:
            return [f for f in self.functions.values() if f.category == category]
        return list(self.functions.values())

    def get_categories(self) -> List[str]:
        """Get a list of all available categories."""
        return sorted({f.category for f in self.functions.values()})

    def format_function_help(self, name: str) -> str:
        """Format help for a specific function as a string."""
        func = self.get_function(name)
        if not func:
            return f"No help found for function: {name}"

        # Format parameters
        params = []
        for param in func.parameters:
            param_str = f"  {param.name}: {param.type}"
            if param.default:
                param_str += f" = {param.default}"
            if not param.required:
                param_str += " (optional)"
            if param.description:
                param_str += f" - {param.description}"
            params.append(param_str)

        # Build help string
        help_str = f"""{name}
{"=" * len(name)}
{func.description}

Parameters:
"""
        help_str += "\n".join(params) + "\n"

        if func.returns:
            help_str += f"\nReturns:\n  {func.returns}\n"

        if func.example:
            help_str += f"\nExample:\n  {func.example}\n"

        return help_str

    def format_category_help(self, category: str) -> str:
        """Format help for all functions in a category."""
        funcs = [f for f in self.functions.values() if f.category == category]
        if not funcs:
            return f"No functions found in category: {category}"

        help_str = f"{category} Functions\n{'=' * (len(category) + 10)}\n\n"

        for func in sorted(funcs, key=lambda x: x.name):
            help_str += f"{func.name}: {func.description}\n"
            help_str += "  " + ", ".join([f"{p.name}: {p.type}" for p in func.parameters[:3]])
            if len(func.parameters) > 3:
                help_str += f"... (+{len(func.parameters) - 3} more)"
            help_str += "\n\n"

        return help_str

    def format_all_help(self) -> str:
        """Format help for all functions, grouped by category."""
        help_str = """Blender MCP Server Help
======================

Available Commands:
"""

        for category in self.get_categories():
            help_str += f"\n{category}:\n"
            help_str += "-" * (len(category) + 1) + "\n"

            funcs = [f for f in self.functions.values() if f.category == category]
            for func in sorted(funcs, key=lambda x: x.name):
                help_str += f"  {func.name}: {func.description}\n"

        help_str += """

For detailed help on a specific function, use: help('function_name')
For functions in a specific category, use: help_category('category_name')
"""
        return help_str


# Create a singleton instance
help_system = HelpSystem()


def get_help(
    function_name: Optional[str] = None,
    category: Optional[str] = None,
    detail_level: str = "normal",
) -> str:
    """Get help for a specific function or list all available functions.

    Args:
        function_name: Name of the function to get help for
        category: If provided, list all functions in this category
        detail_level: Level of detail ("brief", "normal", "detailed")

    Returns:
        str: Formatted help text
    """
    if function_name:
        if detail_level == "brief":
            func_info = help_system.get_function(function_name)
            if func_info:
                return f"{func_info.name}: {func_info.description}"
            else:
                return f"Function '{function_name}' not found."
        else:
            return help_system.format_function_help(function_name)
    elif category:
        if detail_level == "brief":
            tools = help_system.list_functions(category)
            tool_names = [t.name for t in tools]
            return f"{category}: {len(tools)} tools - {', '.join(tool_names[:5])}{'...' if len(tools) > 5 else ''}"
        else:
            return help_system.format_category_help(category)
    else:
        if detail_level == "brief":
            categories = help_system.get_categories()
            category_counts = {}
            for cat in categories:
                category_counts[cat] = len(help_system.list_functions(cat))
            total_tools = sum(category_counts.values())
            return (
                f"Blender MCP: {total_tools} tools across {len(categories)} categories\n"
                + "\n".join([f"• {cat}: {count} tools" for cat, count in category_counts.items()])
            )
        elif detail_level == "detailed":
            return (
                help_system.format_all_help()
                + "\n\nDetailed parameter information available for each tool."
            )
        else:
            return help_system.format_all_help()


def list_categories() -> List[str]:
    """List all available categories."""
    return help_system.get_categories()


def list_functions(category: Optional[str] = None) -> List[str]:
    """List all available functions, optionally filtered by category."""
    return [f.name for f in help_system.list_functions(category)]
