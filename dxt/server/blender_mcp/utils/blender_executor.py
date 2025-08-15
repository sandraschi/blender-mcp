"""Comprehensive Blender script executor with extensive error handling and logging."""

import asyncio
import subprocess
import tempfile
import os
import shutil
import psutil
from pathlib import Path
from typing import Optional, Dict, Any, List, TypeVar
from loguru import logger
import time

from ..exceptions import BlenderNotFoundError, BlenderScriptError
from ..config import BLENDER_EXECUTABLE, validate_blender_executable

# Type variable for the BlenderExecutor class
T = TypeVar('T', bound='BlenderExecutor')

# Global instance of BlenderExecutor
_blender_executor_instance = None

def get_blender_executor(blender_executable: str = None) -> 'BlenderExecutor':
    """Get or create a singleton instance of BlenderExecutor.
    
    Args:
        blender_executable: Path to the Blender executable or command name.
                          If None, uses the configured BLENDER_EXECUTABLE.
        
    Returns:
        BlenderExecutor: The singleton instance of the BlenderExecutor.
    """
    global _blender_executor_instance
    
    if _blender_executor_instance is None:
        # Use the configured path if no explicit path is provided
        executable_to_use = blender_executable or BLENDER_EXECUTABLE
        _blender_executor_instance = BlenderExecutor(executable_to_use)
    
    return _blender_executor_instance


class BlenderExecutor:
    """Comprehensive Blender script executor with robust error handling."""
    
    def __init__(self, blender_executable: str = None):
        # Use the provided executable, or fall back to the one from config
        self.blender_executable = blender_executable or BLENDER_EXECUTABLE
        self.blender_version = None
        self.blender_path = None
        self.temp_dir = None
        self.process_timeout = 300
        self.max_retries = 3
        
        # Validate the Blender executable before initialization
        if not validate_blender_executable():
            raise BlenderNotFoundError(
                f"Blender executable not found at: {self.blender_executable}"
            )
            
        self._initialize_executor()
    
    def _initialize_executor(self) -> None:
        """Initialize executor with comprehensive validation and setup."""
        try:
            logger.info(f"🎨 Initializing Blender executor with executable: {self.blender_executable}")
            
            # Find and validate Blender executable
            self._locate_and_validate_blender()
            
            # Setup temporary directory
            self._setup_temp_directory()
            
            # Test basic Blender functionality
            self._test_blender_functionality()
            
            logger.info(f"✅ Blender executor initialized successfully - Version: {self.blender_version}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Blender executor: {str(e)}")
            raise BlenderNotFoundError(f"Executor initialization failed: {str(e)}")
    
    def _locate_and_validate_blender(self) -> None:
        """Locate and validate the Blender executable."""
        # First, check the explicitly configured path
        if self.blender_executable:
            # Try with .exe extension if not already present on Windows
            if os.name == 'nt' and not self.blender_executable.lower().endswith('.exe'):
                exe_path = f"{self.blender_executable}.exe"
                if os.path.isfile(exe_path):
                    self.blender_path = Path(exe_path).resolve()
                    logger.info(f"✅ Using configured Blender executable: {self.blender_path}")
                    self._validate_blender_version()
                    return
            
            # Try the path as-is
            if os.path.isfile(self.blender_executable):
                self.blender_path = Path(self.blender_executable).resolve()
                logger.info(f"✅ Using configured Blender executable: {self.blender_path}")
                self._validate_blender_version()
                return
            
            # If we have a directory, look for the executable inside it
            if os.path.isdir(self.blender_executable):
                # Check for common executable names in the directory
                for exe_name in ["blender", "blender.exe"]:
                    exe_path = os.path.join(self.blender_executable, exe_name)
                    if os.path.isfile(exe_path):
                        self.blender_path = Path(exe_path).resolve()
                        logger.info(f"✅ Found Blender in configured directory: {self.blender_path}")
                        self._validate_blender_version()
                        return
        
        # If we get here, the configured path didn't work, try other methods
        # Common Blender executable names and paths
        blender_names = ["blender", "blender.exe"]
        
        # Common installation paths - include the configured path in the error message
        common_paths = [
            str(self.blender_executable) if self.blender_executable else "<configured path>",
            "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.1\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe",
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/Applications/Blender.app/Contents/MacOS/Blender"
        ]
        
        # Check if the executable is in PATH
        for name in blender_names:
            try:
                result = subprocess.run(
                    [name, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.blender_path = Path(shutil.which(name)).resolve()
                    logger.info(f"✅ Found Blender in PATH: {self.blender_path}")
                    self._validate_blender_version()
                    return
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
                
        # Check common installation paths
        for path in common_paths:
            if not path or path == "<configured path>":
                continue
                
            # Try with .exe extension if not already present on Windows
            if os.name == 'nt' and not path.lower().endswith('.exe'):
                exe_path = f"{path}.exe"
                if os.path.isfile(exe_path):
                    self.blender_path = Path(exe_path).resolve()
                    logger.info(f"✅ Found Blender at common location: {self.blender_path}")
                    self._validate_blender_version()
                    return
            
            # Try the path as-is
            if os.path.isfile(path):
                self.blender_path = Path(path).resolve()
                logger.info(f"✅ Found Blender at common location: {self.blender_path}")
                self._validate_blender_version()
                return
        
        # If we get here, we couldn't find Blender
        error_msg = "No valid Blender installation found. "
        if self.blender_executable:
            error_msg += f"Configured path: {self.blender_executable} does not exist. "
        error_msg += f"Tried: {[p for p in common_paths if p and p != '<configured path>']}"
        
        raise BlenderNotFoundError(error_msg)
    
    def _validate_blender_version(self) -> None:
        """Validate the Blender version and set the version attribute."""
        try:
            result = subprocess.run(
                [str(self.blender_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "Blender" in result.stdout:
                version_line = result.stdout.split('\n')[0]
                self.blender_version = version_line.strip()
                logger.info(f"✅ Validated Blender version: {self.blender_version}")
            else:
                logger.warning(f"⚠️ Could not determine Blender version: {result.stderr}")
                self.blender_version = "unknown"
                
        except Exception as e:
            logger.error(f"❌ Error validating Blender version: {str(e)}")
            raise BlenderScriptError("", f"Blender version validation failed: {str(e)}")
    
    def _setup_temp_directory(self) -> None:
        """Setup temporary directory for Blender operations."""
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="blender_mcp_")
            logger.debug(f"📁 Created temp directory: {self.temp_dir}")
            
            # Verify temp directory is writable
            test_file = os.path.join(self.temp_dir, "test_write.txt")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            
        except Exception as e:
            logger.error(f"❌ Failed to setup temp directory: {str(e)}")
            raise BlenderScriptError("", f"Temp directory setup failed: {str(e)}")
    
    def _test_blender_functionality(self) -> None:
        """Test basic Blender functionality with a simple script."""
        try:
            test_script = '''
import bpy
import sys

try:
    # Test basic Blender operations
    scene_count = len(bpy.data.scenes)
    object_count = len(bpy.context.scene.objects)
    
    print(f"BLENDER_TEST_SUCCESS: Scenes={scene_count}, Objects={object_count}")
    print(f"BLENDER_PYTHON_VERSION: {sys.version}")
    
except Exception as e:
    print(f"BLENDER_TEST_ERROR: {str(e)}")
    sys.exit(1)
'''
            
            # Create a temporary Python script file to avoid command line length issues
            test_script_path = os.path.join(self.temp_dir, "test_blender_functionality.py")
            with open(test_script_path, 'w', encoding='utf-8') as f:
                f.write(test_script)
            
            # Ensure the Blender executable path is properly quoted for Windows
            blender_cmd = [
                f'"{self.blender_path}"',  # Quote the path to handle spaces
                '--background',
                '--factory-startup',
                '--python', f'"{test_script_path}"',
                '--',  # End of Blender arguments
            ]
            
            # On Windows, we need to use shell=True and join the command parts
            if os.name == 'nt':
                command = ' '.join(blender_cmd)
                logger.debug(f"Running command: {command}")
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                    shell=True
                )
            else:
                # On Unix-like systems, we can pass the command as a list
                logger.debug(f"Running command: {' '.join(blender_cmd)}")
                result = subprocess.run(
                    blender_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False
                )
            
            if result.returncode != 0:
                logger.error(f"❌ Blender functionality test failed: {result.stderr}")
                raise BlenderScriptError(test_script, f"Functionality test failed: {result.stderr}")
            
            # Check for success marker in output
            if "BLENDER_TEST_SUCCESS" not in result.stdout:
                logger.error(f"❌ Blender test script did not complete successfully")
                raise BlenderScriptError(test_script, "Test script did not complete successfully")
            
            logger.debug(f"✅ Blender functionality test passed")
            
        except subprocess.TimeoutExpired as e:
            logger.error(f"❌ Blender functionality test timed out: {str(e)}")
            raise BlenderScriptError(test_script, "Functionality test timed out")
        except Exception as e:
            logger.error(f"❌ Blender functionality test error: {str(e)}")
            raise BlenderScriptError(test_script, f"Functionality test error: {str(e)}")
    
    async def execute_script(
        self, 
        script: str, 
        blend_file: Optional[str] = None,
        timeout: Optional[int] = None,
        retry_count: int = 0,
        script_name: Optional[str] = None
    ) -> str:
        """Execute Python script in Blender with comprehensive error handling."""
        
        if timeout is None:
            timeout = self.process_timeout
        
        script_id = script_name or f"script_{int(time.time() * 1000)}"
        
        try:
            logger.info(f"🎨 Executing Blender script: {script_id} (timeout: {timeout}s)")
            
            # Validate script is not empty
            if not script or not script.strip():
                raise BlenderScriptError(script, "Empty or whitespace-only script provided")
            
            # Create temporary script file with error handling wrapper
            wrapped_script = self._wrap_script_with_error_handling(script, script_id)
            script_path = self._write_temp_script(wrapped_script, script_id)
            
            try:
                # Validate blend file if provided
                if blend_file and not os.path.exists(blend_file):
                    logger.warning(f"⚠️ Blend file not found, using factory startup: {blend_file}")
                    blend_file = None
                
                # Build comprehensive command
                cmd = self._build_blender_command(script_path, blend_file)
                
                # Execute with process monitoring
                stdout, stderr = await self._execute_with_monitoring(cmd, timeout, script_id)
                
                # Process and validate output
                result = self._process_script_output(stdout, stderr, script_id)
                
                logger.info(f"✅ Blender script completed successfully: {script_id}")
                return result
                
            finally:
                # Always clean up temp script file
                self._cleanup_temp_file(script_path)
        
        except BlenderScriptError:
            # Re-raise Blender-specific errors
            raise
        except asyncio.TimeoutError as e:
            error_msg = f"Script execution timed out after {timeout}s"
            logger.error(f"❌ {error_msg}: {script_id}")
            
            # Retry logic for timeout
            if retry_count < self.max_retries:
                logger.warning(f"🔄 Retrying script execution ({retry_count + 1}/{self.max_retries}): {script_id}")
                await asyncio.sleep(2)  # Brief delay before retry
                return await self.execute_script(script, blend_file, timeout, retry_count + 1, script_name)
            
            raise BlenderScriptError(script, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during script execution: {str(e)}"
            logger.error(f"❌ {error_msg}: {script_id}")
            raise BlenderScriptError(script, error_msg)
    
    def _wrap_script_with_error_handling(self, script: str, script_id: str) -> str:
        """Wrap user script with comprehensive error handling."""
        return f'''
import sys
import traceback
import bpy

SCRIPT_ID = "{script_id}"

print(f"BLENDER_SCRIPT_START: {{SCRIPT_ID}}")

try:
    # User script starts here
{self._indent_script(script, 4)}
    
    print(f"BLENDER_SCRIPT_SUCCESS: {{SCRIPT_ID}}")
    
except Exception as user_error:
    print(f"BLENDER_SCRIPT_ERROR: {{SCRIPT_ID}} - {{str(user_error)}}")
    print(f"BLENDER_SCRIPT_TRACEBACK: {{SCRIPT_ID}} - {{traceback.format_exc()}}")
    sys.exit(1)
'''
    
    def _indent_script(self, script: str, spaces: int) -> str:
        """Indent script lines for proper nesting."""
        indent = " " * spaces
        lines = script.split('\n')
        return '\n'.join(f"{indent}{line}" if line.strip() else line for line in lines)
    
    def _write_temp_script(self, script: str, script_id: str) -> str:
        """Write script to temporary file with proper encoding."""
        try:
            script_path = os.path.join(self.temp_dir, f"{script_id}.py")
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script)
            
            logger.debug(f"📝 Written script to: {script_path}")
            return script_path
            
        except Exception as e:
            logger.error(f"❌ Failed to write temp script: {str(e)}")
            raise BlenderScriptError(script, f"Failed to write temp script: {str(e)}")
    
    def _build_blender_command(self, script_path: str, blend_file: Optional[str]) -> List[str]:
        """Build comprehensive Blender command with all necessary flags."""
        cmd = [
            self.blender_executable,
            "--background",           # No GUI
            "--factory-startup",      # Clean startup
            "--enable-autoexec",      # Allow script execution
        ]
        
        if blend_file and os.path.exists(blend_file):
            cmd.append(blend_file)
        
        cmd.extend([
            "--python", script_path,
            "--", # End of Blender args
        ])
        
        logger.debug(f"🔧 Blender command: {' '.join(cmd)}")
        return cmd
    
    async def _execute_with_monitoring(
        self, 
        cmd: List[str], 
        timeout: int, 
        script_id: str
    ) -> tuple[str, str]:
        """Execute command with process monitoring and resource tracking."""
        
        process = None
        try:
            # Create subprocess with proper settings
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir,
                env=os.environ.copy()
            )
            
            logger.debug(f"🚀 Started Blender process PID: {process.pid} for script: {script_id}")
            
            # Monitor process execution
            start_time = time.time()
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                execution_time = time.time() - start_time
                logger.debug(f"⏱️ Script execution completed in {execution_time:.2f}s: {script_id}")
                
            except asyncio.TimeoutError:
                # Kill process on timeout
                logger.error(f"❌ Script execution timed out, killing process {process.pid}: {script_id}")
                
                try:
                    if process.pid:
                        parent = psutil.Process(process.pid)
                        for child in parent.children(recursive=True):
                            logger.debug(f"🔪 Killing child process: {child.pid}")
                            child.kill()
                        parent.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.warning(f"⚠️ Could not kill process cleanly: {str(e)}")
                
                process.kill()
                await process.wait()
                raise asyncio.TimeoutError(f"Process timed out after {timeout}s")
            
            # Check process return code
            if process.returncode != 0:
                stderr_str = stderr.decode('utf-8', errors='replace')
                logger.error(f"❌ Blender process failed with return code {process.returncode}: {script_id}")
                raise BlenderScriptError("", f"Blender process failed (code {process.returncode}): {stderr_str}")
            
            return stdout.decode('utf-8', errors='replace'), stderr.decode('utf-8', errors='replace')
            
        except Exception as e:
            if process and process.returncode is None:
                try:
                    process.kill()
                    await process.wait()
                except Exception as cleanup_error:
                    logger.error(f"❌ Error during process cleanup: {str(cleanup_error)}")
            
            raise e
    
    def _process_script_output(self, stdout: str, stderr: str, script_id: str) -> str:
        """Process and validate script output with comprehensive error checking."""
        
        # Log all output for debugging
        if stdout.strip():
            logger.debug(f"📤 Script stdout: {script_id}")
            for line in stdout.split('\n'):
                if line.strip():
                    logger.debug(f"  {line}")
        
        if stderr.strip():
            logger.debug(f"📤 Script stderr: {script_id}")
            for line in stderr.split('\n'):
                if line.strip():
                    logger.debug(f"  {line}")
        
        # Check for script execution markers
        if f"BLENDER_SCRIPT_START: {script_id}" not in stdout:
            logger.error(f"❌ Script did not start properly: {script_id}")
            raise BlenderScriptError("", f"Script did not start properly: {stderr}")
        
        # Check for errors
        error_lines = []
        traceback_lines = []
        
        for line in stdout.split('\n'):
            if f"BLENDER_SCRIPT_ERROR: {script_id}" in line:
                error_msg = line.split(' - ', 1)[1] if ' - ' in line else "Unknown error"
                error_lines.append(error_msg)
            elif f"BLENDER_SCRIPT_TRACEBACK: {script_id}" in line:
                traceback_msg = line.split(' - ', 1)[1] if ' - ' in line else ""
                traceback_lines.append(traceback_msg)
        
        if error_lines:
            full_error = f"Script errors: {'; '.join(error_lines)}"
            if traceback_lines:
                full_error += f"\nTraceback: {'; '.join(traceback_lines)}"
            logger.error(f"❌ Script execution errors: {script_id} - {full_error}")
            raise BlenderScriptError("", full_error)
        
        # Check for success marker
        if f"BLENDER_SCRIPT_SUCCESS: {script_id}" not in stdout:
            logger.warning(f"⚠️ Script completed without success marker: {script_id}")
            # Don't fail here, as script might have completed successfully without marker
        
        return stdout
    
    def _cleanup_temp_file(self, file_path: str) -> None:
        """Clean up temporary files with error handling."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"🧹 Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"⚠️ Could not clean up temp file {file_path}: {str(e)}")
    
    def cleanup(self) -> None:
        """Clean up executor resources."""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.debug(f"🧹 Cleaned up temp directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"⚠️ Could not clean up temp directory: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass  # Ignore errors in destructor
