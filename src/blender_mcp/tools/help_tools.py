"""
Help and documentation tools for Blender MCP.

Provides comprehensive help system, tool discovery, and documentation
for all available Blender MCP functionality.
"""

from loguru import logger


# Import app lazily to avoid circular imports
def get_app():
    from blender_mcp.app import app

    return app


def _register_help_tools():
    """Register help tools with the app."""
    app = get_app()

    @app.tool
    async def blender_help(
        function_name: str = None, category: str = None, detail_level: str = "normal"
    ) -> str:
        """
        Get comprehensive help for Blender MCP tools and functions.

        Returns detailed help information for specific functions, categories,
        or a complete overview of all available tools.

        Args:
            function_name: Name of specific function to get detailed help for
            category: Category to filter help by
            detail_level: Level of detail ("brief", "normal", "detailed")

        Returns:
            Formatted help text with function signatures, parameters, and examples

        Examples:
            - blender_help() - Show all available tools
            - blender_help("create_cube") - Help for specific function
            - blender_help(category="Mesh Creation") - All mesh tools
            - blender_help(detail_level="brief") - Brief overview
        """
        logger.info(
            f"Getting help - function: {function_name}, category: {category}, detail_level: {detail_level}"
        )
        from blender_mcp.help import get_help as _get_help

        return _get_help(function_name, category, detail_level)

    @app.tool
    async def blender_list_tools(category: str = None) -> str:
        """
        List all available Blender MCP tools with descriptions.

        Returns a comprehensive list of all tools, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            Formatted string with tools organized by categories

        Examples:
            - blender_list_tools() - All tools
        """
        logger.info(f"Listing tools - category: {category}")
        from blender_mcp.help import list_functions, list_categories

        categories = list_categories()

        result = f"Available Blender MCP Tools\n{'=' * 30}\n\n"

        if category:
            # Specific category
            if category in categories:
                tools = list_functions(category)
                result += f"{category} Tools ({len(tools)}):\n{'-' * (len(category) + 7)}\n"
                for tool in tools:
                    result += f"  • {tool}\n"
                result += f"\nTotal: {len(tools)} tools in {category} category"
            else:
                result += f"Category '{category}' not found.\n\nAvailable categories:\n"
                for cat in categories:
                    result += f"  • {cat}\n"
        else:
            # All categories
            total_tools = 0
            for cat in categories:
                tools = list_functions(cat)
                result += f"{cat} ({len(tools)}):\n{'-' * (len(cat) + 3)}\n"
                for tool in tools[:5]:  # Show first 5 tools per category
                    result += f"  • {tool}\n"
                if len(tools) > 5:
                    result += f"  ... and {len(tools) - 5} more\n"
                result += "\n"
                total_tools += len(tools)

            result += f"Total: {total_tools} tools across {len(categories)} categories"

        return result

    @app.tool
    async def blender_search_tools(query: str) -> str:
        """
        Search for Blender MCP tools by name or description.

        Performs case-insensitive search across all tool names and descriptions.

        Args:
            query: Search term to match against tool names and descriptions

        Returns:
            Formatted string with matching tools grouped by relevance

        Examples:
            - blender_search_tools("cube") - Find cube-related tools
        """
        logger.info(f"Searching tools for query: '{query}'")
        from blender_mcp.help import help_system

        query_lower = query.lower()

        exact_matches = []
        name_matches = []
        description_matches = []

        for func in help_system.list_functions():
            func_name_lower = func.name.lower()
            desc_lower = func.description.lower()

            # Exact name match
            if func_name_lower == query_lower:
                exact_matches.append(func)
            # Name contains query
            elif query_lower in func_name_lower:
                name_matches.append(func)
            # Description contains query
            elif query_lower in desc_lower:
                description_matches.append(func)

        result = f"Search Results for '{query}'\n{'=' * (20 + len(query))}\n\n"

        if exact_matches:
            result += f"Exact Matches ({len(exact_matches)}):\n{'-' * 15}\n"
            for func in exact_matches:
                result += f"  • {func.name}: {func.description}\n"
            result += "\n"

        if name_matches:
            result += f"Name Matches ({len(name_matches)}):\n{'-' * 13}\n"
            for func in name_matches:
                result += f"  • {func.name}: {func.description}\n"
            result += "\n"

        if description_matches:
            result += f"Description Matches ({len(description_matches)}):\n{'-' * 20}\n"
            for func in description_matches:
                result += f"  • {func.name}: {func.description}\n"
            result += "\n"

        total_matches = len(exact_matches) + len(name_matches) + len(description_matches)
        result += f"Total matches: {total_matches}"

        if total_matches == 0:
            result += "\n\nNo tools found matching your search. Try a different query or use blender_list_tools() to see all available tools."

        return result

    @app.tool
    async def blender_tool_info(tool_name: str) -> str:
        """
        Get detailed information about a specific Blender MCP tool.

        Returns comprehensive information including parameters, return types,
        examples, and usage notes for the specified tool.

        Args:
            tool_name: Name of the tool to get information about

        Returns:
            Detailed tool information with parameters and usage examples

        Examples:
            - blender_tool_info("blender_mesh") - Info about mesh tools
        """
        logger.info(f"Getting info for tool: '{tool_name}'")
        from blender_mcp.help import help_system

        func_info = help_system.get_function(tool_name)
        if not func_info:
            from blender_mcp.help import list_functions

            available_tools = list_functions()
            return f"""Tool '{tool_name}' not found.

Available tools: {", ".join(available_tools[:10])}{"..." if len(available_tools) > 10 else ""}

Try:
• blender_search_tools('{tool_name}') to search for similar tools
• blender_list_tools() to see all available tools"""

        # Format the response
        result = f"""Tool: {func_info.name}
{"=" * (6 + len(func_info.name))}

Category: {func_info.category}

Description:
{func_info.description}

"""

        if func_info.parameters:
            result += "Parameters:\n"
            for param in func_info.parameters:
                required_str = "" if param.required else " (optional)"
                default_str = f" = {param.default}" if param.default else ""
                result += f"  • {param.name}: {param.type}{default_str}{required_str}\n"
                if param.description:
                    result += f"    {param.description}\n"
            result += "\n"

        if func_info.returns:
            result += f"Returns: {func_info.returns}\n\n"

        if func_info.example:
            result += f"Example: {func_info.example}\n"

        return result

    @app.tool
    async def blender_categories() -> str:
        """
        Get information about all available tool categories.

        Returns a list of all categories with tool counts and descriptions.

        Returns:
            Formatted string with all categories and their tool counts

        Examples:
            - blender_categories() - List all categories
        """
        logger.info("Listing all tool categories")
        from blender_mcp.help import list_categories, list_functions

        categories = list_categories()

        result = f"Blender MCP Tool Categories ({len(categories)} total)\n{'=' * 40}\n\n"

        for category in categories:
            tools = list_functions(category)
            result += f"{category}\n{'-' * len(category)}\n"
            result += f"  {len(tools)} tools available\n"

            # Show a few example tools
            if tools:
                result += "  Examples: " + ", ".join(tools[:3])
                if len(tools) > 3:
                    result += f" (+{len(tools) - 3} more)"
                result += "\n"

            result += "\n"

        return result


# Register the tools when this module is imported
_register_help_tools()
