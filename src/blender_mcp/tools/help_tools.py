"""
Help and documentation portmanteau for Blender MCP.

Single tool for help, list_tools, search, tool_info, and categories.
"""

import logging
from typing import Literal, Optional

from ..compat import *

logger = logging.getLogger(__name__)


def get_app():
    from blender_mcp.app import app

    return app


def _register_help_tools():
    """Register the blender_help portmanteau tool."""
    app = get_app()

    @app.tool
    async def blender_help(
        operation: Literal["help", "list_tools", "search", "tool_info", "categories"] = "help",
        function_name: Optional[str] = None,
        category: Optional[str] = None,
        detail_level: str = "normal",
        query: Optional[str] = None,
        tool_name: Optional[str] = None,
    ) -> str:
        """
        Get help, list tools, search, tool info, or categories (portmanteau).

        Operations:
        - help: Comprehensive help for tools/functions (use function_name, category, detail_level)
        - list_tools: List all tools, optionally filtered by category
        - search: Search tools by name or description (use query)
        - tool_info: Detailed info for one tool (use tool_name)
        - categories: List all categories with tool counts

        Args:
            operation: One of help, list_tools, search, tool_info, categories
            function_name: For help - specific function name
            category: For help/list_tools - category filter
            detail_level: For help - brief, normal, detailed
            query: For search - search term
            tool_name: For tool_info - tool to describe

        Returns:
            Formatted help/list/search/info/categories text
        """
        from blender_mcp.help import (
            get_help as _get_help,
        )
        from blender_mcp.help import (
            help_system,
            list_categories,
            list_functions,
        )

        if operation == "help":
            logger.info(
                f"Getting help - function: {function_name}, category: {category}, detail_level: {detail_level}"
            )
            return _get_help(function_name, category, detail_level)

        if operation == "list_tools":
            logger.info(f"Listing tools - category: {category}")
            categories = list_categories()
            result = f"Available Blender MCP Tools\n{'=' * 30}\n\n"
            if category:
                if category in categories:
                    tools = list_functions(category)
                    result += f"{category} Tools ({len(tools)}):\n{'-' * (len(category) + 7)}\n"
                    for tool in tools:
                        result += f"  - {tool}\n"
                    result += f"\nTotal: {len(tools)} tools in {category} category"
                else:
                    result += f"Category '{category}' not found.\n\nAvailable categories:\n"
                    for cat in categories:
                        result += f"  - {cat}\n"
            else:
                total_tools = 0
                for cat in categories:
                    tools = list_functions(cat)
                    result += f"{cat} ({len(tools)}):\n{'-' * (len(cat) + 3)}\n"
                    for tool in tools[:5]:
                        result += f"  - {tool}\n"
                    if len(tools) > 5:
                        result += f"  ... and {len(tools) - 5} more\n"
                    result += "\n"
                    total_tools += len(tools)
                result += f"Total: {total_tools} tools across {len(categories)} categories"
            return result

        if operation == "search":
            if not query:
                return "query is required for search operation"
            logger.info(f"Searching tools for query: '{query}'")
            query_lower = query.lower()
            exact_matches = []
            name_matches = []
            description_matches = []
            for func in help_system.list_functions():
                fn_lower = func.name.lower()
                desc_lower = func.description.lower()
                if fn_lower == query_lower:
                    exact_matches.append(func)
                elif query_lower in fn_lower:
                    name_matches.append(func)
                elif query_lower in desc_lower:
                    description_matches.append(func)
            result = f"Search Results for '{query}'\n{'=' * (20 + len(query))}\n\n"
            if exact_matches:
                result += f"Exact Matches ({len(exact_matches)}):\n{'-' * 15}\n"
                for func in exact_matches:
                    result += f"  - {func.name}: {func.description}\n"
                result += "\n"
            if name_matches:
                result += f"Name Matches ({len(name_matches)}):\n{'-' * 13}\n"
                for func in name_matches:
                    result += f"  - {func.name}: {func.description}\n"
                result += "\n"
            if description_matches:
                result += f"Description Matches ({len(description_matches)}):\n{'-' * 20}\n"
                for func in description_matches:
                    result += f"  - {func.name}: {func.description}\n"
                result += "\n"
            total = len(exact_matches) + len(name_matches) + len(description_matches)
            result += f"Total matches: {total}"
            if total == 0:
                result += (
                    "\n\nNo tools found. Try blender_help(operation='list_tools') to see all tools."
                )
            return result

        if operation == "tool_info":
            if not tool_name:
                return "tool_name is required for tool_info operation"
            logger.info(f"Getting info for tool: '{tool_name}'")
            func_info = help_system.get_function(tool_name)
            if not func_info:
                available = list_functions()
                return f"Tool '{tool_name}' not found.\n\nAvailable: {', '.join(available[:10])}{'...' if len(available) > 10 else ''}\n\nTry blender_help(operation='search', query='{tool_name}')."
            result = f"Tool: {func_info.name}\n{'=' * (6 + len(func_info.name))}\n\nCategory: {func_info.category}\n\nDescription:\n{func_info.description}\n\n"
            if func_info.parameters:
                result += "Parameters:\n"
                for param in func_info.parameters:
                    req = "" if param.required else " (optional)"
                    default = f" = {param.default}" if param.default else ""
                    result += f"  - {param.name}: {param.type}{default}{req}\n"
                    if param.description:
                        result += f"    {param.description}\n"
                result += "\n"
            if func_info.returns:
                result += f"Returns: {func_info.returns}\n\n"
            if func_info.example:
                result += f"Example: {func_info.example}\n"
            return result

        if operation == "categories":
            logger.info("Listing all tool categories")
            categories = list_categories()
            result = f"Blender MCP Tool Categories ({len(categories)} total)\n{'=' * 40}\n\n"
            for cat in categories:
                tools = list_functions(cat)
                result += f"{cat}\n{'-' * len(cat)}\n"
                result += f"  {len(tools)} tools available\n"
                if tools:
                    result += "  Examples: " + ", ".join(tools[:3])
                    if len(tools) > 3:
                        result += f" (+{len(tools) - 3} more)"
                    result += "\n"
                result += "\n"
            return result

        return (
            f"Unknown operation: {operation}. Use: help, list_tools, search, tool_info, categories"
        )


_register_help_tools()
