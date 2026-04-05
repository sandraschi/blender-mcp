# Troubleshooting Guide

## Common Issues and Solutions

### Installation Problems

#### "blender-mcp command not found"
**Symptoms:** Command not recognized in terminal
**Solutions:**
```bash
# Check if installed
pip list | grep blender-mcp

# Add to PATH (Linux/Mac)
export PATH="$HOME/.local/bin:$PATH"

# Add to PATH (Windows)
# Add %USERPROFILE%\AppData\Local\Programs\Python\Python3x\Scripts to PATH

# Reinstall
pip uninstall blender-mcp
pip install blender-mcp
```

#### Import Errors on Startup
**Symptoms:** Module import failures during CLI execution
**Error:** `NameError: name 'Context' is not defined`
**Solutions:**
```bash
# Check FastMCP version
pip show fastmcp

# Upgrade to compatible version
pip install --upgrade fastmcp>=2.14.3

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

#### Blender Path Issues
**Symptoms:** "Blender executable not found"
**Error:** `WARNING: Blender executable not found at: C:\Program Files\Blender Foundation\Blender 4.4\blender.exe`
**Solutions:**
```bash
# Set environment variable
export BLENDER_EXECUTABLE=/path/to/blender

# Check Blender installation
/path/to/blender --version

# Add to system PATH
# Windows: Add Blender directory to PATH
# Linux/Mac: ln -s /path/to/blender /usr/local/bin/blender
```

### AI Construction Issues

#### Script Generation Fails
**Symptoms:** AI construction returns validation errors
**Error:** `"Generated script failed validation: {'errors': ['syntax_error'], 'warnings': []}"`
**Solutions:**
```python
# Try simpler description
construct_object("a red cube")

# Use more specific technical terms
construct_object("a parametric cube with rounded edges, 2 meter sides")

# Check complexity level
construct_object("complex building", complexity="simple")  # Start simple
```

#### Validation Security Errors
**Symptoms:** Script rejected for security reasons
**Error:** `"security_score": 25, "issues": ["dangerous_import", "unapproved_operation"]`
**Solutions:**
```python
# Avoid complex file operations
# Use approved Blender operations only
# Check generated script manually
# Report security false positives
```

#### Memory/Resource Issues
**Symptoms:** Blender crashes during complex operations
**Error:** `"RuntimeError: Blender execution failed: out of memory"`
**Solutions:**
```python
# Reduce complexity
construct_object("building", complexity="simple")

# Close other applications
# Increase system memory
# Use smaller texture sizes
# Clear Blender scene between operations
```

### Performance Problems

#### Slow Response Times
**Symptoms:** Operations take longer than expected
**Solutions:**
```python
# Use appropriate complexity levels
construct_object("object", complexity="simple")  # Fastest
construct_object("object", complexity="standard")  # Balanced
construct_object("object", complexity="complex")  # Slowest

# Enable caching
export MCP_CACHE=true

# Check system resources
# Close unnecessary applications
# Monitor memory usage
```

#### High Memory Usage
**Symptoms:** System becomes unresponsive during operations
**Solutions:**
```python
# Monitor Blender memory
blender_system("get_memory_usage")

# Clear caches regularly
blender_system("clear_cache")

# Use smaller texture resolutions
# Reduce scene complexity
# Restart Blender instances periodically
```

### Network and Connectivity Issues

#### MCP Client Connection Problems
**Symptoms:** Claude Desktop can't connect to Blender MCP
**Error:** `Connection refused` or `timeout`
**Solutions:**
```bash
# Check server status
blender-mcp --check-blender

# Restart MCP server
pkill -f blender-mcp
blender-mcp --stdio

# Check Claude Desktop config
# Ensure correct command path
# Verify MCP configuration in Claude settings
```

#### HTTP API Connection Issues
**Symptoms:** Web API calls fail
**Solutions:**
```bash
# Check server status
curl http://localhost:8000/health

# Start HTTP server
blender-mcp --http --port 8000

# Check firewall settings
# Verify port availability
# Test with different ports
```

### Platform-Specific Issues

#### Windows Path Issues
**Symptoms:** File path errors on Windows
**Solutions:**
```powershell
# Use forward slashes in paths
"C:/path/to/file.blend"

# Escape backslashes
"C:\\path\\to\\file.blend"

# Use raw strings for paths
r"C:\path\to\file.blend"
```

#### Linux Permission Issues
**Symptoms:** Access denied errors
**Solutions:**
```bash
# Check file permissions
ls -la /path/to/file

# Fix permissions
chmod 644 /path/to/file
chmod 755 /directory

# Run as appropriate user
# Check SELinux/AppArmor if applicable
```

#### macOS Gatekeeper Issues
**Symptoms:** Blender blocked by security
**Solutions:**
```bash
# Allow Blender in Security & Privacy
# System Preferences → Security & Privacy → General
# Click "Allow Anyway" for Blender

# Or disable Gatekeeper (not recommended)
sudo spctl --master-disable
```

### Tool-Specific Issues

#### Material Application Problems
**Symptoms:** Materials not applying correctly
**Solutions:**
```python
# Check object selection
blender_selection("select_object", object_name="MyObject")

# Verify material exists
blender_materials("list_materials")

# Apply with correct parameters
blender_materials("apply_pbr", object_name="MyObject",
                 base_color=[1.0, 0.0, 0.0], metallic=0.0)
```

#### Animation Keyframe Issues
**Symptoms:** Animation not playing correctly
**Solutions:**
```python
# Check frame range
blender_animation("set_frame_range", start_frame=1, end_frame=120)

# Verify keyframes exist
blender_animation("list_keyframes", object_name="MyObject")

# Set interpolation
blender_animation("set_interpolation", interpolation="bezier")
```

#### Export Format Problems
**Symptoms:** Exported files corrupted or incomplete
**Solutions:**
```python
# Check export settings
blender_export("validate_export", object_names=["MyObject"], format="fbx")

# Use supported formats
# FBX, OBJ, glTF for 3D models
# PNG, JPEG for images

# Verify file permissions on export directory
```

### VR Platform Issues

#### VRChat Upload Failures
**Symptoms:** Exported models rejected by VRChat
**Solutions:**
```python
# Check polygon limits
blender_validation("check_polygons", target_platform="vrchat")

# Validate materials
blender_validation("check_materials", target_platform="vrchat")

# Use VRChat export preset
blender_export_presets("export_vrchat", include_animations=True)
```

#### Unity Import Issues
**Symptoms:** Models don't import correctly in Unity
**Solutions:**
```python
# Use Unity-compatible export
blender_export("export_fbx", object_names=["MyModel"],
              export_settings={"unity_compatible": True})

# Check scale and units
blender_scene("set_units", unit_system="metric")

# Apply transforms
blender_transform("apply_transforms", object_name="MyModel")
```

### Repository Issues

#### Object Save/Load Problems
**Symptoms:** Repository operations fail
**Solutions:**
```python
# Check repository path
blender_system("get_config")

# Verify permissions on repository directory
# Check available disk space
# Validate object exists before operations
```

#### Search Not Working
**Symptoms:** Repository search returns no results
**Solutions:**
```python
# Try simpler queries
manage_object_repo("search", query="robot")

# Check tags and categories
manage_object_repo("list_objects")

# Rebuild search index
blender_system("rebuild_index")
```

### Development and Testing

#### Test Failures
**Symptoms:** Unit tests failing
**Solutions:**
```bash
# Install test dependencies
pip install blender-mcp[dev]

# Run specific tests
pytest tests/test_construction.py -v

# Check Blender availability for integration tests
blender-mcp --check-blender
```

#### Logging Issues
**Symptoms:** No log output or excessive logging
**Solutions:**
```bash
# Enable debug logging
export MCP_DEBUG=true
blender-mcp --debug --stdio

# Check log file location
blender_system("get_log_path")

# Adjust log levels in code
import logging
logging.getLogger('blender_mcp').setLevel(logging.DEBUG)
```

### Getting Help

#### Debug Information Collection
```bash
# System information
blender-mcp --show-config

# Blender status
blender-mcp --check-blender

# Tool list
blender-mcp --list-tools

# Generate debug report
blender_system("generate_debug_report")
```

#### Support Resources
1. **GitHub Issues**: Report bugs with full error logs
2. **Documentation**: Check `docs/` for detailed guides
3. **Community**: Join Discord/server for user support
4. **Logs**: Provide relevant log excerpts when reporting issues

#### Emergency Procedures
```bash
# Force restart Blender instances
blender_system("restart_blender")

# Clear all caches
blender_system("clear_all_caches")

# Reset to default configuration
blender_system("reset_config")

# Emergency shutdown
blender_system("emergency_shutdown")
```

This troubleshooting guide covers the most common issues. For additional help, check the logs, system status, and consider filing a detailed bug report with reproduction steps.
