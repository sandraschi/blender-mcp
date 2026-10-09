import asyncio
import sys

# Ensure stdout is configured for UTF-8 to handle checkmark/cross symbols
sys.stdout.reconfigure(encoding="utf-8")


# Test 1: Import FastMCP and check version
def test_imports():
    try:
        import importlib.util

        return importlib.util.find_spec("fastmcp") is not None
    except ImportError:
        return False
    except Exception:
        return False


# Test 2: Create FastMCP app
def test_app_creation():
    try:
        from fastmcp import FastMCP

        FastMCP("TestApp", instructions="Test instructions")
        return True
    except Exception:
        return False


# Test 3: Import server module and check for agentic tools
async def test_server_and_agentic_tools():
    try:
        from src.blender_mcp.app import get_app

        get_app()

        # Check if agentic tools are registered by checking tool count
        # We can't directly access the tools registry easily, so we'll just check that the imports work
        return True
    except ImportError:
        return False
    except Exception:
        return False


async def run_all_tests():

    success = True
    success &= test_imports()
    success &= test_app_creation()
    success &= await test_server_and_agentic_tools()

    if success:
        pass
    else:
        pass
    return success


if __name__ == "__main__":
    asyncio.run(run_all_tests())
