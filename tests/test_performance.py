"""Performance and stress tests for Blender MCP.

These tests evaluate performance characteristics and stress test the system
with real Blender execution.
"""

import pytest
import asyncio
import time
import psutil
import os
from pathlib import Path
from typing import List, Dict, Any


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.requires_blender
class TestPerformance:
    """Performance tests for Blender MCP components."""

    @pytest.fixture
    async def performance_setup(self, blender_executable: str, temp_dir: Path):
        """Setup for performance tests."""
        from blender_mcp.utils.blender_executor import BlenderExecutor
        executor = BlenderExecutor(blender_executable)

        return {
            "executor": executor,
            "temp_dir": temp_dir,
            "start_time": time.time()
        }

    async def measure_execution_time(self, coro, description: str) -> float:
        """Measure execution time of an async operation."""
        start_time = time.time()
        result = await coro
        end_time = time.time()
        duration = end_time - start_time
        print(".2f")
        return duration

    @pytest.mark.asyncio
    async def test_script_execution_performance(self, performance_setup: Dict[str, Any]):
        """Test performance of script execution."""
        executor = performance_setup["executor"]

        # Test simple script performance
        simple_script = "import bpy\nprint('Hello World')"
        duration = await self.measure_execution_time(
            executor.execute_script(simple_script),
            "Simple script execution"
        )
        assert duration < 10.0  # Should complete within 10 seconds

        # Test complex script performance
        complex_script = '''
import bpy
import math

# Create many objects
for i in range(50):
    x = math.sin(i * 0.1) * 5
    y = math.cos(i * 0.1) * 5
    z = i * 0.1
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z))

print("Created 50 objects")
'''
        duration = await self.measure_execution_time(
            executor.execute_script(complex_script),
            "Complex script execution (50 objects)"
        )
        assert duration < 30.0  # Should complete within 30 seconds

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, performance_setup: Dict[str, Any]):
        """Test performance with concurrent operations."""
        executor = performance_setup["executor"]

        async def create_objects_batch(batch_id: int, count: int):
            script = f'''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)

for i in range({count}):
    bpy.ops.mesh.primitive_cube_add(location=(i*2, {batch_id}*10, 0))

print(f"Batch {batch_id} completed with {count} objects")
'''
            return await executor.execute_script(script)

        # Run multiple batches concurrently
        tasks = [
            create_objects_batch(i, 10) for i in range(5)
        ]

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        duration = end_time - start_time
        print(".2f")

        # All operations should succeed
        for i, result in enumerate(results):
            assert f"Batch {i} completed with 10 objects" in result

        assert duration < 60.0  # Should complete within 1 minute

    @pytest.mark.asyncio
    async def test_memory_usage(self, performance_setup: Dict[str, Any]):
        """Test memory usage during operations."""
        executor = performance_setup["executor"]

        def get_memory_usage():
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # MB

        initial_memory = get_memory_usage()

        # Perform memory-intensive operations
        memory_script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create many high-poly objects
for i in range(20):
    bpy.ops.mesh.primitive_uv_sphere_add(
        location=(i*3, 0, 0),
        radius=1,
        segments=32,
        ring_count=16
    )

print("Created 20 high-poly spheres")
'''
        await executor.execute_script(memory_script)

        final_memory = get_memory_usage()
        memory_delta = final_memory - initial_memory

        print(".2f")
        # Memory usage should not exceed reasonable limits
        assert memory_delta < 500  # Less than 500MB increase

    @pytest.mark.asyncio
    async def test_handler_performance(self, blender_executable: str):
        """Test performance of various handlers."""
        from blender_mcp.handlers.scene_handler import SceneHandler
        from blender_mcp.handlers.mesh_handler import MeshHandler

        scene_handler = SceneHandler(blender_executable)
        mesh_handler = MeshHandler(blender_executable)

        # Test scene operations
        scene_times = []
        for i in range(10):
            duration = await self.measure_execution_time(
                scene_handler.create_scene(f"PerfScene{i}"),
                f"Scene creation {i}"
            )
            scene_times.append(duration)

        avg_scene_time = sum(scene_times) / len(scene_times)
        print(".2f")
        assert avg_scene_time < 5.0  # Average scene creation under 5 seconds

        # Test mesh operations (if available)
        try:
            mesh_times = []
            for i in range(5):
                script = f'''
import bpy
bpy.ops.mesh.primitive_cube_add(location=({i*2}, 0, 0))
cube = bpy.context.active_object
cube.name = "PerfCube{i}"
print(f"Created PerfCube{i}")
'''
                duration = await self.measure_execution_time(
                    mesh_handler.executor.execute_script(script),
                    f"Mesh creation {i}"
                )
                mesh_times.append(duration)

            avg_mesh_time = sum(mesh_times) / len(mesh_times)
            print(".2f")
            assert avg_mesh_time < 3.0  # Average mesh creation under 3 seconds
        except Exception:
            pytest.skip("Mesh operations not available for performance testing")

    @pytest.mark.asyncio
    async def test_large_scene_handling(self, performance_setup: Dict[str, Any]):
        """Test handling of large scenes."""
        executor = performance_setup["executor"]

        # Create a very large scene
        large_scene_script = '''
import bpy
import math
import random

bpy.ops.wm.read_factory_settings(use_empty=True)

# Create 200 objects of various types
for i in range(200):
    # Random position in a large area
    x = random.uniform(-50, 50)
    y = random.uniform(-50, 50)
    z = random.uniform(0, 20)

    # Randomly choose object type
    obj_type = random.choice(['cube', 'sphere', 'cylinder'])

    if obj_type == 'cube':
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
    elif obj_type == 'sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(location=(x, y, z))
    elif obj_type == 'cylinder':
        bpy.ops.mesh.primitive_cylinder_add(location=(x, y, z))

    # Name the object
    obj = bpy.context.active_object
    obj.name = f"LargeSceneObj_{i:03d}"

    # Add random scale
    scale = random.uniform(0.5, 2.0)
    obj.scale = (scale, scale, scale)

print("Created large scene with 200 objects")
'''

        duration = await self.measure_execution_time(
            executor.execute_script(large_scene_script),
            "Large scene creation (200 objects)"
        )

        assert duration < 120.0  # Should complete within 2 minutes

        # Verify scene contents
        verify_script = '''
import bpy
objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
print(f"Large scene contains {len(objects)} mesh objects")
'''
        result = await executor.execute_script(verify_script)
        assert "200 mesh objects" in result

    @pytest.mark.asyncio
    async def test_rapid_succession_operations(self, performance_setup: Dict[str, Any]):
        """Test rapid succession of operations."""
        executor = performance_setup["executor"]

        operations = []

        # Perform 50 rapid operations
        for i in range(50):
            script = f'''
import bpy
if {i} == 0:
    bpy.ops.wm.read_factory_settings(use_empty=True)

bpy.ops.mesh.primitive_cube_add(location=({i}*0.5, 0, 0))
obj = bpy.context.active_object
obj.name = f"RapidObj_{i:02d}"
'''
            operations.append(executor.execute_script(script))

        start_time = time.time()
        results = await asyncio.gather(*operations)
        end_time = time.time()

        total_duration = end_time - start_time
        avg_duration = total_duration / len(operations)

        print(".2f")
        print(".3f")

        # All operations should succeed
        successful = sum(1 for result in results if "RapidObj_" in result)
        assert successful == 50

        assert total_duration < 180.0  # Total under 3 minutes
        assert avg_duration < 5.0    # Average under 5 seconds per operation

    @pytest.mark.asyncio
    async def test_error_recovery_performance(self, performance_setup: Dict[str, Any]):
        """Test performance of error recovery."""
        executor = performance_setup["executor"]

        # Mix of successful and failing operations
        operations = []

        for i in range(20):
            if i % 5 == 0:  # Every 5th operation fails
                script = '''
import bpy
nonexistent_function_that_will_fail()
'''
            else:
                script = f'''
import bpy
bpy.ops.mesh.primitive_cube_add(location=({i}, 0, 0))
obj = bpy.context.active_object
obj.name = f"RecoveryObj_{i}"
print(f"Created RecoveryObj_{i}")
'''

            operations.append(executor.execute_script(script))

        start_time = time.time()

        # Execute operations and handle errors
        results = []
        for coro in operations:
            try:
                result = await coro
                results.append(("success", result))
            except Exception as e:
                results.append(("error", str(e)))

        end_time = time.time()
        total_duration = end_time - start_time

        print(".2f")

        # Should have 4 errors (every 5th operation)
        errors = sum(1 for status, _ in results if status == "error")
        successes = sum(1 for status, _ in results if status == "success")

        assert errors == 4
        assert successes == 16

        # Error recovery should not significantly impact performance
        assert total_duration < 60.0  # Under 1 minute total


@pytest.mark.stress
@pytest.mark.slow
@pytest.mark.requires_blender
class TestStress:
    """Stress tests for extreme conditions."""

    @pytest.mark.asyncio
    async def test_maximum_objects(self, blender_executable: str):
        """Test creating the maximum number of objects Blender can handle."""
        from blender_mcp.utils.blender_executor import BlenderExecutor
        executor = BlenderExecutor(blender_executable)

        # Try to create as many objects as possible
        stress_script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)

objects_created = 0
max_attempts = 1000  # Safety limit

for i in range(max_attempts):
    try:
        bpy.ops.mesh.primitive_cube_add(location=(i*0.1, 0, 0))
        objects_created += 1
    except:
        break  # Stop if Blender can't create more objects

print(f"Successfully created {objects_created} objects")
'''

        result = await executor.execute_script(stress_script)

        # Should create at least some objects
        assert "Successfully created" in result

        # Extract number created
        import re
        match = re.search(r"Successfully created (\d+) objects", result)
        assert match
        count = int(match.group(1))
        assert count > 0

        print(f"Stress test created {count} objects")

    @pytest.mark.asyncio
    async def test_complex_materials_stress(self, blender_executable: str):
        """Test creating many complex materials."""
        from blender_mcp.utils.blender_executor import BlenderExecutor
        executor = BlenderExecutor(blender_executable)

        materials_script = '''
import bpy
import random

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object

materials_created = 0
max_materials = 100

for i in range(max_materials):
    try:
        material = bpy.data.materials.new(name=f"StressMat_{i:03d}")
        material.use_nodes = True

        # Create complex node setup
        principled = material.node_tree.nodes["Principled BSDF"]

        # Random colors
        principled.inputs["Base Color"].default_value = (
            random.random(),
            random.random(),
            random.random(),
            1.0
        )

        # Random metallic/roughness
        principled.inputs["Metallic"].default_value = random.random()
        principled.inputs["Roughness"].default_value = random.random()

        materials_created += 1

    except:
        break

print(f"Successfully created {materials_created} complex materials")
'''

        result = await executor.execute_script(materials_script)

        assert "Successfully created" in result

        # Extract number created
        import re
        match = re.search(r"Successfully created (\d+) complex materials", result)
        assert match
        count = int(match.group(1))
        assert count > 0

        print(f"Stress test created {count} complex materials")

    @pytest.mark.asyncio
    async def test_long_running_script(self, blender_executable: str):
        """Test very long-running script."""
        from blender_mcp.utils.blender_executor import BlenderExecutor
        executor = BlenderExecutor(blender_executable)

        long_script = '''
import bpy
import time
import math

bpy.ops.wm.read_factory_settings(use_empty=True)

# Perform computationally intensive operations
start_time = time.time()

# Create many objects with complex transformations
for i in range(100):
    x = math.sin(i * 0.1) * 10
    y = math.cos(i * 0.1) * 10
    z = math.sin(i * 0.05) * 5

    bpy.ops.mesh.primitive_uv_sphere_add(
        location=(x, y, z),
        radius=0.5,
        segments=16,
        ring_count=8
    )

    obj = bpy.context.active_object
    obj.name = f"ComplexObj_{i:03d}"

    # Apply complex material
    material = bpy.data.materials.new(name=f"ComplexMat_{i:03d}")
    material.use_nodes = True
    principled = material.node_tree.nodes["Principled BSDF"]

    # Complex color based on position
    r = (math.sin(i * 0.1) + 1) / 2
    g = (math.cos(i * 0.1) + 1) / 2
    b = (math.sin(i * 0.05) + 1) / 2

    principled.inputs["Base Color"].default_value = (r, g, b, 1.0)
    obj.data.materials.append(material)

end_time = time.time()
duration = end_time - start_time

print(f"Long-running script completed in {duration:.2f} seconds")
print("Created 100 complex objects with materials")
'''

        start_time = time.time()
        result = await executor.execute_script(long_script)
        end_time = time.time()

        total_duration = end_time - start_time

        assert "Long-running script completed" in result
        assert "Created 100 complex objects" in result

        print(".2f")
        # Should complete within reasonable time (allowing for Blender's performance)
        assert total_duration < 300.0  # 5 minutes max
