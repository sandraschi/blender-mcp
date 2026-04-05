"""
Blender MCP Megatest Suite
===========================

Comprehensive, Production-Safe Testing Framework

TEST LEVELS:
===========

Level 1: SMOKE (2 minutes)
- Basic server startup
- Simple tool calls
- Essential functionality

Level 2: STANDARD (10 minutes)
- Core Blender operations
- Scene management
- Basic object creation

Level 3: ADVANCED (20 minutes)
- Complex operations
- Material systems
- Animation basics

Level 4: INTEGRATION (45 minutes)
- Multi-tool workflows
- Export/import cycles
- Performance testing

Level 5: FULL BLAST (90 minutes)
- Complete feature coverage
- Stress testing
- Real-world scenarios

USAGE:
======

# Quick smoke test
pytest tests/megatest/ -m megatest_smoke -v

# Standard validation
pytest tests/megatest/ -m megatest_standard -v

# Advanced features
pytest tests/megatest/ -m megatest_advanced -v

# Integration testing
pytest tests/megatest/ -m megatest_integration -v

# Complete validation
pytest tests/megatest/ -m megatest_full -v

SAFETY:
=======

- NEVER touches production data
- Isolated test environment
- Multiple safety validations
- Automatic cleanup options

CONFIGURATION:
==============

Environment Variables:
- MEGATEST_LOCATION: local|temp|hidden|<custom_path>
- MEGATEST_CLEANUP: immediate|on_success|preserve
- MEGATEST_LEVEL: smoke|standard|advanced|integration|full

Files:
- tests/megatest/conftest.py: Safety fixtures and configuration
- tests/megatest/level*/: Test implementations by level
- tests/megatest/shared/: Shared utilities and fixtures
"""

__version__ = "1.0.0"
__description__ = "Blender MCP Comprehensive Testing Framework"
