from ..compat import *

"""Command Line Interface for Blender MCP.

This module provides a command-line interface to interact with the Blender MCP server,
including accessing the help system and executing commands.
"""
import argparse
import sys
from typing import List, Optional

from .help import get_help, list_categories, list_functions


def print_banner():
    """Print the Blender MCP banner."""
    banner = """
    ____  _            __        __  ___  ____  
   / __ )(_)___  ___  / /__     /  |/  / / __ \ 
  / __  / / __ \/ _ \/ //_/    / /|_/ / / /_/ / 
 / /_/ / / / / /  __/ ,<      / /  / / / ____/  
/_____/_/_/ /_/\___/_/|_|    /_/  /_/ /_/     
                                             
    Model Creation Pipeline - Help System
    """
    print(banner)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="Blender MCP - Model Creation Pipeline Help System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Help command
    help_parser = subparsers.add_parser("help", help="Show help for commands")
    help_parser.add_argument(
        "function_or_category", nargs="?", help="Function or category to get help for"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List available items")
    list_parser.add_argument(
        "type", choices=["categories", "functions"], help="Type of items to list", nargs="?"
    )
    list_parser.add_argument("--category", help="Filter functions by category", default=None)

    # Version command
    subparsers.add_parser("version", help="Show version information")

    # Parse arguments
    if args is None:
        args = sys.argv[1:]

    # If no arguments, show help
    if not args:
        parser.print_help()
        return 0

    args = parser.parse_args(args)

    # Handle commands
    if args.command == "help":
        if args.function_or_category:
            # Check if it's a category
            categories = list_categories()
            if args.function_or_category.lower() in [c.lower() for c in categories]:
                print(get_help(category=args.function_or_category))
            else:
                print(get_help(function_name=args.function_or_category))
        else:
            print_banner()
            print("\n" + get_help())

    elif args.command == "list":
        if not args.type or args.type == "categories":
            print("\nAvailable Categories:")
            print("-" * 40)
            for category in sorted(list_categories()):
                print(f"- {category}")

        if not args.type or args.type == "functions":
            print("\nAvailable Functions:")
            print("-" * 40)
            if args.category:
                funcs = list_functions(args.category)
                if not funcs:
                    print(f"No functions found in category: {args.category}")
                else:
                    for func in sorted(funcs):
                        print(f"- {func}")
            else:
                for category in sorted(list_categories()):
                    print(f"\n{category}:")
                    for func in sorted(list_functions(category)):
                        print(f"  - {func}")

    elif args.command == "version":
        from . import __version__

        print(f"Blender MCP Version: {__version__}")

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
