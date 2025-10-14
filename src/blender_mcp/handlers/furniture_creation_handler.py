"""
Furniture and Structure Creation Handler for Blender MCP

This module provides tools for creating various furniture and structural elements in Blender.
All implementations are marked as MOCK for now.
"""

from typing import Optional, Tuple, Dict, Any, Union, List
from enum import Enum, auto
import logging
from datetime import datetime
import math
from math import radians

# Try to import Blender modules, with fallback for non-Blender environments
try:
    import bpy
    import bmesh
    from mathutils import Vector, Matrix
    HAS_BPY = True
except ImportError:
    # Create mock objects for when not running inside Blender
    class MockBpy:
        pass
    
    class MockVector:
        def __init__(self, *args):
            pass
    
    class MockMatrix:
        def __init__(self, *args):
            pass
    
    bpy = MockBpy()
    bmesh = MockBpy()
    Vector = MockVector
    Matrix = MockMatrix
    HAS_BPY = False

from fastmcp import FastMCP
from blender_mcp.decorators import blender_operation

# Initialize logger
logger = logging.getLogger(__name__)

# Create FastMCP instance
app = FastMCP("blender-mcp-furniture-creation")

class BedType(Enum):
    """Available bed types."""
    SINGLE = "single"
    DOUBLE = "double"
    KING = "king"
    QUEEN = "queen"
    BUNK = "bunk"
    LOFT = "loft"
    FOUR_POSTER = "four_poster"
    CANOPY = "canopy"
    MURPHY = "murphy"
    FUTON = "futon"
    WATER = "water"
    HAMMOCK = "hammock"
    ROUND = "round"

class BuildingType(Enum):
    """Available building types."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    SKYSCRAPER = "skyscraper"
    COTTAGE = "cottage"
    CASTLE = "castle"
    WAREHOUSE = "warehouse"
    CHURCH = "church"
    MODERN_HOUSE = "modern_house"
    APARTMENT = "apartment"
    OFFICE = "office"
    MALL = "mall"

class WeaponType(Enum):
    """Available weapon types."""
    SWORD = "sword"
    DAGGER = "dagger"
    AXE = "axe"
    MACE = "mace"
    BOW = "bow"
    CROSSBOW = "crossbow"
    STAFF = "staff"
    WAND = "wand"
    GUN = "gun"
    RIFLE = "rifle"
    SHOTGUN = "shotgun"
    PISTOL = "pistol"
    MACHINE_GUN = "machine_gun"
    SNIPER = "sniper"
    ROCKET_LAUNCHER = "rocket_launcher"
    GRENADE = "grenade"
    SHIELD = "shield"

class OrnamentType(Enum):
    """Available ornament types."""
    VASE = "vase"
    STATUE = "statue"
    CANDELABRA = "candelabra"
    CLOCK = "clock"
    MIRROR = "mirror"
    PICTURE_FRAME = "picture_frame"
    TROPHY = "trophy"
    BOOK = "book"
    GLOBE = "globe"
    PLANT = "plant"
    SCULPTURE = "sculpture"
    LAMP = "lamp"

class RoomType(Enum):
    """Available room types."""
    LIVING = "living"
    BEDROOM = "bedroom"
    BATHROOM = "bathroom"
    KITCHEN = "kitchen"
    DINING = "dining"
    OFFICE = "office"
    LIBRARY = "library"
    GARAGE = "garage"
    BASEMENT = "basement"
    ATTIC = "attic"
    HALLWAY = "hallway"
    STAIRCASE = "staircase"
    GYM = "gym"
    THEATER = "theater"
    NURSERY = "nursery"
    LAUNDRY = "laundry"
    CLOSET = "closet"
    BALCONY = "balcony"
    PATIO = "patio"
    POOL = "pool"

class Material(Enum):
    """Available materials for objects."""
    WOOD = "wood"
    METAL = "metal"
    GLASS = "glass"
    STONE = "stone"
    FABRIC = "fabric"
    LEATHER = "leather"
    PLASTIC = "plastic"
    CONCRETE = "concrete"
    BRICK = "brick"
    MARBLE = "marble"
    CERAMIC = "ceramic"
    CRYSTAL = "crystal"
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    COPPER = "copper"
    IRON = "iron"
    STEEL = "steel"
    PAINT = "paint"

class Style(Enum):
    """Available styles for objects."""
    MODERN = "modern"
    CLASSIC = "classic"
    RUSTIC = "rustic"
    INDUSTRIAL = "industrial"
    SCANDINAVIAN = "scandinavian"
    MID_CENTURY = "mid_century"
    VICTORIAN = "victorian"
    CONTEMPORARY = "contemporary"
    FANTASY = "fantasy"
    SCI_FI = "sci_fi"
    STEAMPUNK = "steampunk"
    GOTHIC = "gothic"
    BAROQUE = "baroque"
    ART_DECO = "art_deco"
    MINIMALIST = "minimalist"
    BOHEMIAN = "bohemian"
    COASTAL = "coastal"
    FARMHOUSE = "farmhouse"
    MEDITERRANEAN = "mediterranean"
    TROPICAL = "tropical"
    JAPANESE = "japanese"
    CHINESE = "chinese"
    INDIAN = "indian"
    AFRICAN = "african"
    MIDDLE_EASTERN = "middle_eastern"
    SOUTH_AMERICAN = "south_american"
    NATIVE_AMERICAN = "native_american"
    TRIBAL = "tribal"
    FUTURISTIC = "futuristic"
    POST_APOCALYPTIC = "post_apocalyptic"
    CYBERPUNK = "cyberpunk"
    DIESELPUNK = "dieselpunk"
    ATOMIC = "atomic"
    SPACE_AGE = "space_age"
    URBAN = "urban"
    SUBURBAN = "suburban"
    RURAL = "rural"
    MOUNTAIN = "mountain"
    BEACH = "beach"
    DESERT = "desert"
    FOREST = "forest"
    JUNGLE = "jungle"
    ARCTIC = "arctic"
    UNDERWATER = "underwater"
    UNDERGROUND = "underground"
    SPACE = "space"
    HEAVENLY = "heavenly"
    HELLISH = "hellish"
    MAGICAL = "magical"
    MYSTICAL = "mystical"
    ENCHANTED = "enchanted"
    CURSED = "cursed"
    HAUNTED = "haunted"
    ABANDONED = "abandoned"
    RUINED = "ruined"
    DESTROYED = "destroyed"
    CONSTRUCTED = "constructed"
    DECONSTRUCTED = "deconstructed"
    ABSTRACT = "abstract"
    SURREAL = "surreal"
    CUBIST = "cubist"
    IMPRESSIONIST = "impressionist"
    EXPRESSIONIST = "expressionist"
    SURREALIST = "surrealist"
    REALIST = "realist"
    HYPERREALIST = "hyperrealist"
    CARTOON = "cartoon"
    ANIME = "anime"
    PIXEL = "pixel"
    LOW_POLY = "low_poly"
    HIGH_POLY = "high_poly"
    STYLIZED = "stylized"
    PHOTOREALISTIC = "photorealistic"
    HAND_PAINTED = "hand_painted"
    WATERCOLOR = "watercolor"
    OIL_PAINTING = "oil_painting"
    PENCIL_SKETCH = "pencil_sketch"
    INK = "ink"
    CHARCOAL = "charcoal"
    CHALK = "chalk"
    PASTEL = "pastel"
    AIRBRUSH = "airbrush"
    VECTOR = "vector"
    PIXEL_ART = "pixel_art"
    VOXEL = "voxel"
    LEGO = "lego"
    PAPER_CRAFT = "paper_craft"
    ORIGAMI = "origami"
    CLAY = "clay"
    WOODEN = "wooden"
    METAL_WORK = "metal_work"
    GLASS_WORK = "glass_work"
    STONE_CARVING = "stone_carving"
    JEWELRY = "jewelry"
    TEXTILE = "textile"
    EMBROIDERY = "embroidery"
    KNITTING = "knitting"
    CROCHET = "crochet"
    QUILTING = "quilting"
    WEAVING = "weaving"
    MACRAME = "macrame"
    TATTING = "tatting"
    LACE_MAKING = "lace_making"
    FELTING = "felting"
    SPINNING = "spinning"
    DYEING = "dyeing"
    PRINTING = "printing"
    EMBOSSING = "embossing"
    ENGRAVING = "engraving"
    ETCHING = "etching"
    LASER_CUTTING = "laser_cutting"
    WATER_JET_CUTTING = "water_jet_cutting"
    PLASMA_CUTTING = "plasma_cutting"
    CNC_MILLING = "cnc_milling"
    THREE_D_PRINTING = "3d_printing"
    LASER_SINTERING = "laser_sintering"
    STEREO_LITHOGRAPHY = "stereo_lithography"
    FUSED_DEPOSITION_MODELING = "fused_deposition_modeling"
    SELECTIVE_LASER_SINTERING = "selective_laser_sintering"
    DIRECT_METAL_LASER_SINTERING = "direct_metal_laser_sintering"
    ELECTRON_BEAM_MELTING = "electron_beam_melting"
    BINDER_JETTING = "binder_jetting"
    MATERIAL_JETTING = "material_jetting"
def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()

# Bed Creation

@blender_operation("create_bed", log_args=True)
async def create_bed(
    name: str = "Bed",
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    bed_type: Union[str, BedType] = BedType.DOUBLE,
    style: Union[str, Style] = Style.MODERN,
    material: Union[str, Material] = Material.WOOD,
    color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0),
    has_headboard: bool = True,
    has_footboard: bool = True,
    has_posts: bool = False,
    has_canopy: bool = False,
    has_storage: bool = False,
    is_murphy: bool = False,
    is_loft: bool = False,
    is_bunk: bool = False,
    is_water: bool = False,
    is_hammock: bool = False,
    is_round: bool = False,
    is_futon: bool = False,
) -> Dict[str, Any]:
    """Create a bed in the Blender scene.
    
    Args:
        name: Name for the bed object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        bed_type: Type of bed (single, double, king, queen, etc.)
        style: Style of the bed
        material: Material type for the bed
        color: RGBA color values (0-1)
        has_headboard: Whether the bed has a headboard
        has_footboard: Whether the bed has a footboard
        has_posts: Whether the bed has posts
        has_canopy: Whether the bed has a canopy
        has_storage: Whether the bed has storage
        is_murphy: Whether the bed is a murphy bed
        is_loft: Whether the bed is a loft bed
        is_bunk: Whether the bed is a bunk bed
        is_water: Whether the bed is a water bed
        is_hammock: Whether the bed is a hammock
        is_round: Whether the bed is round
        is_futon: Whether the bed is a futon
        
    Returns:
        Dictionary with information about the created bed
    """
    # Clear existing object if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    
    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh for bed construction
    bm = bmesh.new()
    
    # Define bed dimensions based on type
    bed_length = 2.0  # Default length
    bed_width = 1.5   # Default width
    bed_height = 0.3  # Default height
    leg_height = 0.1  # Default leg height
    mattress_thickness = 0.2  # Default mattress thickness
    headboard_height = 0.8 if has_headboard else 0
    footboard_height = 0.4 if has_footboard else 0
    storage_height = 0.2 if has_storage else 0
    
    # Adjust dimensions based on bed type
    bed_type_str = bed_type.value if isinstance(bed_type, BedType) else bed_type
    if bed_type_str == "single":
        bed_length, bed_width = 1.9, 1.0
    elif bed_type_str == "double":
        bed_length, bed_width = 1.9, 1.4
    elif bed_type_str == "queen":
        bed_length, bed_width = 2.0, 1.5
    elif bed_type_str == "king":
        bed_length, bed_width = 2.0, 1.9
    elif bed_type_str == "california_king":
        bed_length, bed_width = 2.1, 1.8
    
    # Create the bed frame
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame_obj = bpy.context.active_object
    frame_obj.name = f"{name}_Frame"
    frame_obj.scale = (bed_length, bed_width, bed_height)
    frame_obj.location = (0, 0, leg_height + bed_height/2)
    
    # Create the mattress
    bpy.ops.mesh.primitive_cube_add(size=1)
    mattress_obj = bpy.context.active_object
    mattress_obj.name = f"{name}_Mattress"
    mattress_obj.scale = (bed_length * 0.9, bed_width * 0.9, mattress_thickness)
    mattress_obj.location = (0, 0, leg_height + bed_height + mattress_thickness/2)
    
    # Create legs
    for i, (x, y) in enumerate([(-bed_length/2, -bed_width/2), (bed_length/2, -bed_width/2), 
                                (-bed_length/2, bed_width/2), (bed_length/2, bed_width/2)]):
        bpy.ops.mesh.primitive_cube_add(size=1)
        leg_obj = bpy.context.active_object
        leg_obj.name = f"{name}_Leg_{i+1}"
        leg_obj.scale = (0.05, 0.05, leg_height)
        leg_obj.location = (x, y, leg_height/2)
    
    # Create headboard if requested
    if has_headboard:
        bpy.ops.mesh.primitive_cube_add(size=1)
        headboard_obj = bpy.context.active_object
        headboard_obj.name = f"{name}_Headboard"
        headboard_obj.scale = (bed_length, 0.1, headboard_height)
        headboard_obj.location = (0, bed_width/2 + 0.05, leg_height + bed_height + headboard_height/2)
    
    # Create footboard if requested
    if has_footboard:
        bpy.ops.mesh.primitive_cube_add(size=1)
        footboard_obj = bpy.context.active_object
        footboard_obj.name = f"{name}_Footboard"
        footboard_obj.scale = (bed_length, 0.1, footboard_height)
        footboard_obj.location = (0, -bed_width/2 - 0.05, leg_height + bed_height + footboard_height/2)
    
    # Create storage if requested
    if has_storage:
        bpy.ops.mesh.primitive_cube_add(size=1)
        storage_obj = bpy.context.active_object
        storage_obj.name = f"{name}_Storage"
        storage_obj.scale = (bed_length * 0.8, bed_width * 0.8, storage_height)
        storage_obj.location = (0, 0, leg_height + storage_height/2)
    
    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale
    
    # Create materials
    material_str = material.value if isinstance(material, Material) else material
    frame_material = bpy.data.materials.new(name=f"{name}_Frame_Material")
    frame_material.use_nodes = True
    bsdf = frame_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = color
    
    # Set material properties based on type
    if material_str == "wood":
        bsdf.inputs["Roughness"].default_value = 0.7
        bsdf.inputs["Specular"].default_value = 0.3
    elif material_str == "metal":
        bsdf.inputs["Metallic"].default_value = 1.0
        bsdf.inputs["Roughness"].default_value = 0.2
    elif material_str == "fabric":
        bsdf.inputs["Roughness"].default_value = 0.9
        bsdf.inputs["Specular"].default_value = 0.2
    
    mattress_material = bpy.data.materials.new(name=f"{name}_Mattress_Material")
    mattress_material.use_nodes = True
    mattress_material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.95, 0.95, 0.95, 1.0)
    
    # Assign materials
    frame_obj.data.materials.append(frame_material)
    mattress_obj.data.materials.append(mattress_material)
    
    # Prepare return data
    bed_data = {
        "name": name,
        "type": f"bed_{bed_type_str}",
        "location": location,
        "rotation": rotation,
        "scale": scale,
        "style": style.value if isinstance(style, Style) else style,
        "material": material_str,
        "color": color,
        "has_headboard": has_headboard,
        "has_footboard": has_footboard,
        "has_posts": has_posts,
        "has_canopy": has_canopy,
        "has_storage": has_storage,
        "is_murphy": is_murphy,
        "is_loft": is_loft,
        "is_bunk": is_bunk,
        "is_water": is_water,
        "is_hammock": is_hammock,
        "is_round": is_round,
        "is_futon": is_futon,
        "dimensions": {
            "length": bed_length,
            "width": bed_width,
            "height": bed_height + leg_height + (headboard_height if has_headboard else 0),
            "mattress_thickness": mattress_thickness,
            "headboard_height": headboard_height,
            "footboard_height": footboard_height,
            "storage_height": storage_height if has_storage else 0
        },
        "created_at": get_timestamp(),
        "is_mock": False
    }
    
    logger.info(f"Created bed: {name}")
    return bed_data

# Building Creation

@blender_operation("create_building", log_args=True)
async def create_building(
    name: str = "Building",
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    building_type: Union[str, BuildingType] = BuildingType.RESIDENTIAL,
    style: Union[str, Style] = Style.MODERN,
    material: Union[str, Material] = Material.CONCRETE,
    color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0),
    floors: int = 1,
    width: float = 10.0,
    depth: float = 15.0,
    height: float = 3.0,
    has_roof: bool = True,
    has_balcony: bool = False,
    has_garage: bool = False,
    has_pool: bool = False,
    has_garden: bool = False,
    has_fence: bool = False,
    has_chimney: bool = False,
    has_porch: bool = False,
    has_basement: bool = False,
    has_attic: bool = False,
) -> Dict[str, Any]:
    """Create a building in the Blender scene.
    
    Args:
        name: Name for the building object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        building_type: Type of building (residential, commercial, etc.)
        style: Style of the building
        material: Material type for the building
        color: RGBA color values (0-1)
        floors: Number of floors
        width: Width of the building in meters
        depth: Depth of the building in meters
        height: Height of each floor in meters
        has_roof: Whether the building has a roof
        has_balcony: Whether the building has a balcony
        has_garage: Whether the building has a garage
        has_pool: Whether the building has a pool
        has_garden: Whether the building has a garden
        has_fence: Whether the building has a fence
        has_chimney: Whether the building has a chimney
        has_porch: Whether the building has a porch
        has_basement: Whether the building has a basement
        has_attic: Whether the building has an attic
        
    Returns:
        Dictionary with information about the created building
    """
    # Clear existing object if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    
    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh for building construction
    bm = bmesh.new()
    
    # Define building dimensions
    floor_height = height / floors if floors > 0 else height
    wall_thickness = 0.2
    
    # Create main building structure
    bpy.ops.mesh.primitive_cube_add(size=1)
    building_obj = bpy.context.active_object
    building_obj.name = f"{name}_Main"
    building_obj.scale = (width, depth, height)
    building_obj.location = (0, 0, height/2)
    
    # Create floors
    for floor in range(floors):
        floor_y = floor * floor_height
        bpy.ops.mesh.primitive_cube_add(size=1)
        floor_obj = bpy.context.active_object
        floor_obj.name = f"{name}_Floor_{floor+1}"
        floor_obj.scale = (width * 0.9, depth * 0.9, 0.1)
        floor_obj.location = (0, 0, floor_y + 0.05)
    
    # Create roof if requested
    if has_roof:
        bpy.ops.mesh.primitive_cube_add(size=1)
        roof_obj = bpy.context.active_object
        roof_obj.name = f"{name}_Roof"
        roof_obj.scale = (width * 1.1, depth * 1.1, 0.2)
        roof_obj.location = (0, 0, height + 0.1)
    
    # Create garage if requested
    if has_garage:
        bpy.ops.mesh.primitive_cube_add(size=1)
        garage_obj = bpy.context.active_object
        garage_obj.name = f"{name}_Garage"
        garage_obj.scale = (width * 0.3, depth * 0.4, height * 0.6)
        garage_obj.location = (width * 0.6, depth * 0.6, height * 0.3)
    
    # Create chimney if requested
    if has_chimney:
        bpy.ops.mesh.primitive_cube_add(size=1)
        chimney_obj = bpy.context.active_object
        chimney_obj.name = f"{name}_Chimney"
        chimney_obj.scale = (0.3, 0.3, height * 0.3)
        chimney_obj.location = (width * 0.3, depth * 0.3, height + height * 0.15)
    
    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale
    
    # Create materials
    material_str = material.value if isinstance(material, Material) else material
    building_material = bpy.data.materials.new(name=f"{name}_Material")
    building_material.use_nodes = True
    bsdf = building_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = color
    
    # Set material properties based on type
    if material_str == "concrete":
        bsdf.inputs["Roughness"].default_value = 0.8
        bsdf.inputs["Specular"].default_value = 0.1
    elif material_str == "brick":
        bsdf.inputs["Roughness"].default_value = 0.7
        bsdf.inputs["Specular"].default_value = 0.2
    elif material_str == "wood":
        bsdf.inputs["Roughness"].default_value = 0.6
        bsdf.inputs["Specular"].default_value = 0.3
    
    # Assign materials
    building_obj.data.materials.append(building_material)
    
    # Prepare return data
    building_data = {
        "name": name,
        "type": f"building_{building_type.value if isinstance(building_type, BuildingType) else building_type}",
        "location": location,
        "rotation": rotation,
        "scale": scale,
        "style": style.value if isinstance(style, Style) else style,
        "material": material_str,
        "color": color,
        "floors": floors,
        "dimensions": {"width": width, "depth": depth, "height": height},
        "has_roof": has_roof,
        "has_balcony": has_balcony,
        "has_garage": has_garage,
        "has_pool": has_pool,
        "has_garden": has_garden,
        "has_fence": has_fence,
        "has_chimney": has_chimney,
        "has_porch": has_porch,
        "has_basement": has_basement,
        "has_attic": has_attic,
        "created_at": get_timestamp(),
        "is_mock": False
    }
    
    logger.info(f"Created building: {name}")
    return building_data

# Weapon Creation

@blender_operation("create_weapon", log_args=True)
async def create_weapon(
    name: str = "Weapon",
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    weapon_type: Union[str, WeaponType] = WeaponType.SWORD,
    style: Union[str, Style] = Style.FANTASY,
    material: Union[str, Material] = Material.METAL,
    color: Tuple[float, float, float, float] = (0.5, 0.5, 0.5, 1.0),
    length: float = 1.0,
    width: float = 0.1,
    height: float = 0.1,
    damage: int = 10,
    range_: float = 1.0,
    attack_speed: float = 1.0,
    durability: int = 100,
    is_magical: bool = False,
    is_poisoned: bool = False,
    is_cursed: bool = False,
    is_enchanted: bool = False,
    is_legendary: bool = False,
) -> Dict[str, Any]:
    """Create a weapon in the Blender scene.
    
    Args:
        name: Name for the weapon object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        weapon_type: Type of weapon (sword, axe, bow, etc.)
        style: Style of the weapon
        material: Material type for the weapon
        color: RGBA color values (0-1)
        length: Length of the weapon in meters
        width: Width of the weapon in meters
        height: Height of the weapon in meters
        damage: Base damage of the weapon
        range_: Attack range of the weapon in meters
        attack_speed: Attack speed of the weapon
        durability: Durability of the weapon
        is_magical: Whether the weapon is magical
        is_poisoned: Whether the weapon is poisoned
        is_cursed: Whether the weapon is cursed
        is_enchanted: Whether the weapon is enchanted
        is_legendary: Whether the weapon is legendary
        
    Returns:
        Dictionary with information about the created weapon
    """
    logger.warning("MOCK IMPLEMENTATION: create_weapon is not actually creating geometry in Blender")
    
    weapon_data = {
        "name": name,
        "type": f"weapon_{weapon_type.value if isinstance(weapon_type, WeaponType) else weapon_type}",
        "location": location,
        "rotation": rotation,
        "scale": scale,
        "style": style.value if isinstance(style, Style) else style,
        "material": material.value if isinstance(material, Material) else material,
        "color": color,
        "dimensions": {"length": length, "width": width, "height": height},
        "stats": {
            "damage": damage,
            "range": range_,
            "attack_speed": attack_speed,
            "durability": durability
        },
        "properties": {
            "is_magical": is_magical,
            "is_poisoned": is_poisoned,
            "is_cursed": is_cursed,
            "is_enchanted": is_enchanted,
            "is_legendary": is_legendary
        },
        "created_at": get_timestamp(),
        "is_mock": True
    }
    
    logger.info(f"Created MOCK weapon: {name}")
    return weapon_data

# Ornament Creation

@blender_operation("create_ornament", log_args=True)
async def create_ornament(
    name: str = "Ornament",
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    ornament_type: Union[str, OrnamentType] = OrnamentType.VASE,
    style: Union[str, Style] = Style.CLASSIC,
    material: Union[str, Material] = Material.GLASS,
    color: Tuple[float, float, float, float] = (0.9, 0.9, 0.9, 1.0),
    height: float = 0.3,
    width: float = 0.2,
    depth: float = 0.2,
    is_fragile: bool = True,
    is_breakable: bool = True,
    is_valuable: bool = False,
    is_antique: bool = False,
) -> Dict[str, Any]:
    """Create an ornament in the Blender scene.
    
    Args:
        name: Name for the ornament object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        ornament_type: Type of ornament (vase, statue, etc.)
        style: Style of the ornament
        material: Material type for the ornament
        color: RGBA color values (0-1)
        height: Height of the ornament in meters
        width: Width of the ornament in meters
        depth: Depth of the ornament in meters
        is_fragile: Whether the ornament is fragile
        is_breakable: Whether the ornament can be broken
        is_valuable: Whether the ornament is valuable
        is_antique: Whether the ornament is an antique
        
    Returns:
        Dictionary with information about the created ornament
    """
    logger.warning("MOCK IMPLEMENTATION: create_ornament is not actually creating geometry in Blender")
    
    ornament_data = {
        "name": name,
        "type": f"ornament_{ornament_type.value if isinstance(ornament_type, OrnamentType) else ornament_type}",
        "location": location,
        "rotation": rotation,
        "scale": scale,
        "style": style.value if isinstance(style, Style) else style,
        "material": material.value if isinstance(material, Material) else material,
        "color": color,
        "dimensions": {"height": height, "width": width, "depth": depth},
        "properties": {
            "is_fragile": is_fragile,
            "is_breakable": is_breakable,
            "is_valuable": is_valuable,
            "is_antique": is_antique
        },
        "created_at": get_timestamp(),
        "is_mock": True
    }
    
    logger.info(f"Created MOCK ornament: {name}")
    return ornament_data

# Room Creation

@blender_operation("create_room", log_args=True)
async def create_room(
    name: str = "Room",
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    room_type: Union[str, RoomType] = RoomType.LIVING,
    style: Union[str, Style] = Style.MODERN,
    wall_material: Union[str, Material] = Material.PAINT,
    floor_material: Union[str, Material] = Material.WOOD,
    ceiling_material: Union[str, Material] = Material.PAINT,
    wall_color: Tuple[float, float, float, float] = (0.95, 0.95, 0.95, 1.0),
    floor_color: Tuple[float, float, float, float] = (0.5, 0.4, 0.3, 1.0),
    ceiling_color: Tuple[float, float, float, float] = (0.98, 0.98, 0.98, 1.0),
    length: float = 5.0,
    width: float = 4.0,
    height: float = 2.7,
    has_windows: bool = True,
    window_count: int = 2,
    has_doors: bool = True,
    door_count: int = 1,
    has_lighting: bool = True,
    has_furniture: bool = False,
    has_decoration: bool = False,
) -> Dict[str, Any]:
    """Create a room in the Blender scene.
    
    Args:
        name: Name for the room object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        room_type: Type of room (living, bedroom, kitchen, etc.)
        style: Style of the room
        wall_material: Material type for the walls
        floor_material: Material type for the floor
        ceiling_material: Material type for the ceiling
        wall_color: RGBA color values for walls (0-1)
        floor_color: RGBA color values for floor (0-1)
        ceiling_color: RGBA color values for ceiling (0-1)
        length: Length of the room in meters
        width: Width of the room in meters
        height: Height of the room in meters
        has_windows: Whether the room has windows
        window_count: Number of windows
        has_doors: Whether the room has doors
        door_count: Number of doors
        has_lighting: Whether the room has lighting
        has_furniture: Whether to add furniture to the room
        has_decoration: Whether to add decoration to the room
        
    Returns:
        Dictionary with information about the created room
    """
    # Clear existing object if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    
    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create room structure
    wall_thickness = 0.2
    
    # Create floor
    bpy.ops.mesh.primitive_cube_add(size=1)
    floor_obj = bpy.context.active_object
    floor_obj.name = f"{name}_Floor"
    floor_obj.scale = (length, width, 0.1)
    floor_obj.location = (0, 0, 0.05)
    
    # Create walls
    wall_positions = [
        (0, width/2 + wall_thickness/2, height/2),  # Front wall
        (0, -width/2 - wall_thickness/2, height/2), # Back wall
        (length/2 + wall_thickness/2, 0, height/2), # Right wall
        (-length/2 - wall_thickness/2, 0, height/2)  # Left wall
    ]
    
    for i, (x, y, z) in enumerate(wall_positions):
        bpy.ops.mesh.primitive_cube_add(size=1)
        wall_obj = bpy.context.active_object
        wall_obj.name = f"{name}_Wall_{i+1}"
        if i < 2:  # Front/back walls
            wall_obj.scale = (length + 2*wall_thickness, wall_thickness, height)
        else:  # Left/right walls
            wall_obj.scale = (wall_thickness, width, height)
        wall_obj.location = (x, y, z)
    
    # Create ceiling
    bpy.ops.mesh.primitive_cube_add(size=1)
    ceiling_obj = bpy.context.active_object
    ceiling_obj.name = f"{name}_Ceiling"
    ceiling_obj.scale = (length, width, 0.1)
    ceiling_obj.location = (0, 0, height - 0.05)
    
    # Create windows if requested
    if has_windows and window_count > 0:
        for i in range(min(window_count, 4)):  # Max 4 windows
            bpy.ops.mesh.primitive_cube_add(size=1)
            window_obj = bpy.context.active_object
            window_obj.name = f"{name}_Window_{i+1}"
            window_obj.scale = (0.8, 0.1, 0.6)
            window_obj.location = (0, width/2 + 0.1, height * 0.6)
    
    # Create doors if requested
    if has_doors and door_count > 0:
        for i in range(min(door_count, 2)):  # Max 2 doors
            bpy.ops.mesh.primitive_cube_add(size=1)
            door_obj = bpy.context.active_object
            door_obj.name = f"{name}_Door_{i+1}"
            door_obj.scale = (0.1, 0.1, height * 0.8)
            door_obj.location = (length/4 if i == 0 else -length/4, width/2 + 0.1, height * 0.4)
    
    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale
    
    # Create materials
    wall_material_str = wall_material.value if isinstance(wall_material, Material) else wall_material
    floor_material_str = floor_material.value if isinstance(floor_material, Material) else floor_material
    ceiling_material_str = ceiling_material.value if isinstance(ceiling_material, Material) else ceiling_material
    
    # Create wall material
    wall_mat = bpy.data.materials.new(name=f"{name}_Wall_Material")
    wall_mat.use_nodes = True
    wall_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = wall_color
    
    # Create floor material
    floor_mat = bpy.data.materials.new(name=f"{name}_Floor_Material")
    floor_mat.use_nodes = True
    floor_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = floor_color
    
    # Create ceiling material
    ceiling_mat = bpy.data.materials.new(name=f"{name}_Ceiling_Material")
    ceiling_mat.use_nodes = True
    ceiling_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = ceiling_color
    
    # Assign materials
    floor_obj.data.materials.append(floor_mat)
    ceiling_obj.data.materials.append(ceiling_mat)
    
    # Prepare return data
    room_data = {
        "name": name,
        "type": f"room_{room_type.value if isinstance(room_type, RoomType) else room_type}",
        "location": location,
        "rotation": rotation,
        "scale": scale,
        "style": style.value if isinstance(style, Style) else style,
        "materials": {
            "wall": wall_material_str,
            "floor": floor_material_str,
            "ceiling": ceiling_material_str
        },
        "colors": {
            "wall": wall_color,
            "floor": floor_color,
            "ceiling": ceiling_color
        },
        "dimensions": {"length": length, "width": width, "height": height},
        "features": {
            "has_windows": has_windows,
            "window_count": window_count if has_windows else 0,
            "has_doors": has_doors,
            "door_count": door_count if has_doors else 0,
            "has_lighting": has_lighting,
            "has_furniture": has_furniture,
            "has_decoration": has_decoration
        },
        "created_at": get_timestamp(),
        "is_mock": False
    }
    
    logger.info(f"Created room: {name}")
    return room_data
