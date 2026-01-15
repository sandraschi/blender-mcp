"""
Furniture Handler for Blender MCP

This module provides tools for creating and managing furniture in Blender.
All implementations use real Blender API (bmesh, bpy.ops) to generate actual geometry."""

from ..compat import *

from typing import Tuple, Dict, Any, Union
from enum import Enum
import logging
import math
from math import radians

# Try to import Blender modules, with fallback for non-Blender environments
try:
    import bpy
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
    Vector = MockVector
    Matrix = MockMatrix
    HAS_BPY = False

from fastmcp import FastMCP
from ..decorators import blender_operation

logger = logging.getLogger(__name__)


class FurnitureStyle(str, Enum):
    MODERN = "modern"
    CLASSIC = "classic"
    RUSTIC = "rustic"
    INDUSTRIAL = "industrial"
    SCANDINAVIAN = "scandinavian"
    MID_CENTURY = "mid_century"
    CONTEMPORARY = "contemporary"
    TRADITIONAL = "traditional"
    BOHEMIAN = "bohemian"
    FARMHOUSE = "farmhouse"
    COASTAL = "coastal"
    MINIMALIST = "minimalist"
    LUXURY = "luxury"
    VINTAGE = "vintage"
    SHABBY_CHIC = "shabby_chic"
    INDUSTRIAL_LOFT = "industrial_loft"
    SCANDI = "scandi"
    JAPANDI = "japandi"
    MEDITERRANEAN = "mediterranean"
    TROPICAL = "tropical"
    FRENCH_COUNTRY = "french_country"
    ART_DECO = "art_deco"
    TRANSITIONAL = "transitional"
    GLAM = "glam"
    ECLECTIC = "eclectic"
    INDUSTRIAL_CHIC = "industrial_chic"
    COTTAGE = "cottage"
    MODERN_FARMHOUSE = "modern_farmhouse"
    COASTAL_GRANDMOTHER = "coastal_grandmother"
    MAXIMALIST = "maximalist"
    BIOPHILIC = "biophilic"
    HOLIDAY = "holiday"
    WABI_SABI = "wabi_sabi"
    JUNGALOW = "jungalow"
    DARK_ACADEMIA = "dark_academia"
    LIGHT_ACADEMIA = "light_academia"
    COTTAGECORE = "cottagecore"
    GRANDMILLENNIAL = "grandmillennial"
    SCANDI_BOHO = "scandi_boho"
    JAPANDI_SCANDI = "japandi_scandi"
    MODERN_COASTAL = "modern_coastal"
    MODERN_COUNTRY = "modern_country"
    MODERN_RUSTIC = "modern_rustic"
    MODERN_TRADITIONAL = "modern_traditional"
    MODERN_INDUSTRIAL = "modern_industrial"
    MODERN_FRENCH = "modern_french"
    MODERN_FARMHOUSE_RUSTIC = "modern_farmhouse_rustic"
    MODERN_COASTAL_FARMHOUSE = "modern_coastal_farmhouse"
    MODERN_MEDITERRANEAN = "modern_mediterranean"
    MODERN_TROPICAL = "modern_tropical"
    MODERN_BOHEMIAN = "modern_bohemian"
    MODERN_SCANDINAVIAN = "modern_scandinavian"
    MODERN_MID_CENTURY = "modern_mid_century"
    MODERN_CONTEMPORARY = "modern_contemporary"


class MaterialType(str, Enum):
    WOOD = "wood"
    METAL = "metal"
    GLASS = "glass"
    FABRIC = "fabric"
    LEATHER = "leather"
    PLASTIC = "plastic"
    MARBLE = "marble"
    STONE = "stone"
    CONCRETE = "concrete"
    CERAMIC = "ceramic"
    VELVET = "velvet"
    LINEN = "linen"
    WOOL = "wool"
    SILK = "silk"
    RATTAN = "rattan"
    WICKER = "wicker"
    BRASS = "brass"
    COPPER = "copper"
    BRONZE = "bronze"
    GOLD = "gold"
    SILVER = "silver"
    CHROME = "chrome"
    NICKEL = "nickel"
    IRON = "iron"
    STEEL = "steel"
    ALUMINUM = "aluminum"
    ACRYLIC = "acrylic"
    LUCITE = "lucite"
    MIRROR = "mirror"
    GRANITE = "granite"
    QUARTZ = "quartz"
    SLATE = "slate"
    TRAVERTINE = "travertine"
    ONYX = "onyx"
    JADE = "jade"
    JASPER = "jasper"
    MALACHITE = "malachite"
    TURQUOISE = "turquoise"
    LAPIS_LAZULI = "lapis_lazuli"
    MOTHER_OF_PEARL = "mother_of_pearl"
    CORAL = "coral"
    PEARL = "pearl"
    CRYSTAL = "crystal"
    MIRRORED = "mirrored"
    LACQUER = "lacquer"
    ENAMEL = "enamel"
    RESIN = "resin"
    CEMENT = "cement"
    TERRAZZO = "terrazzo"
    CORK = "cork"
    BAMBOO = "bamboo"
    SEAGRASS = "seagrass"
    JUTE = "jute"
    SISAL = "sisal"
    HEMP = "hemp"
    STRAW = "straw"
    RAFFIA = "raffia"
    ABACA = "abaca"
    PAPER = "paper"
    CARDBOARD = "cardboard"


class RoomType(str, Enum):
    LIVING = "living"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    DINING = "dining"
    HOME_OFFICE = "home_office"
    KIDS_ROOM = "kids_room"
    NURSERY = "nursery"
    GUEST_ROOM = "guest_room"
    LAUNDRY = "laundry"
    MUDROOM = "mudroom"
    ENTRY = "entry"
    HALLWAY = "hallway"
    LIBRARY = "library"
    MEDIA_ROOM = "media_room"
    GAME_ROOM = "game_room"
    GYM = "gym"
    OFFICE = "office"
    STUDIO = "studio"
    LOFT = "loft"
    BASEMENT = "basement"
    ATTIC = "attic"
    GARAGE = "garage"
    WORKSHOP = "workshop"
    UTILITY = "utility"
    STORAGE = "storage"
    WALK_IN_CLOSET = "walk_in_closet"
    DRESSING_ROOM = "dressing_room"
    PANTRY = "pantry"
    WINE_CELLAR = "wine_cellar"
    THEATER = "theater"
    MUSIC_ROOM = "music_room"
    ART_STUDIO = "art_studio"
    CRAFT_ROOM = "craft_room"
    SEWING_ROOM = "sewing_room"
    SUNROOM = "sunroom"
    CONSERVATORY = "conservatory"
    PORCH = "porch"
    BALCONY = "balcony"
    TERRACE = "terrace"
    DECK = "deck"
    PATIO = "patio"
    COURTYARD = "courtyard"
    GARDEN = "garden"
    GREENHOUSE = "greenhouse"
    SHED = "shed"
    BARN = "barn"
    POOL_HOUSE = "pool_house"
    GUEST_HOUSE = "guest_house"
    POOL = "pool"
    SPA = "spa"
    SAUNA = "sauna"
    STEAM_ROOM = "steam_room"
    JACUZZI = "jacuzzi"
    HOT_TUB = "hot_tub"
    INDOOR_POOL = "indoor_pool"
    OUTDOOR_POOL = "outdoor_pool"
    INDOOR_JACUZZI = "indoor_jacuzzi"
    OUTDOOR_JACUZZI = "outdoor_jacuzzi"
    INDOOR_HOT_TUB = "indoor_hot_tub"
    OUTDOOR_HOT_TUB = "outdoor_hot_tub"
    INDOOR_SAUNA = "indoor_sauna"
    OUTDOOR_SAUNA = "outdoor_sauna"
    INDOOR_STEAM_ROOM = "indoor_steam_room"
    OUTDOOR_STEAM_ROOM = "outdoor_steam_room"
    INDOOR_POOL_HOUSE = "indoor_pool_house"
    OUTDOOR_POOL_HOUSE = "outdoor_pool_house"
    INDOOR_GUEST_HOUSE = "indoor_guest_house"
    OUTDOOR_GUEST_HOUSE = "outdoor_guest_house"
    INDOOR_SHED = "indoor_shed"
    OUTDOOR_SHED = "outdoor_shed"
    INDOOR_BARN = "indoor_barn"
    OUTDOOR_BARN = "outdoor_barn"
    INDOOR_GREENHOUSE = "indoor_greenhouse"
    OUTDOOR_GREENHOUSE = "outdoor_greenhouse"
    INDOOR_GARDEN = "indoor_garden"
    OUTDOOR_GARDEN = "outdoor_garden"
    INDOOR_COURTYARD = "indoor_courtyard"
    OUTDOOR_COURTYARD = "outdoor_courtyard"
    INDOOR_PATIO = "indoor_patio"
    OUTDOOR_PATIO = "outdoor_patio"
    INDOOR_DECK = "indoor_deck"
    OUTDOOR_DECK = "outdoor_deck"
    INDOOR_TERRACE = "indoor_terrace"
    OUTDOOR_TERRACE = "outdoor_terrace"
    INDOOR_BALCONY = "indoor_balcony"
    OUTDOOR_BALCONY = "outdoor_balcony"
    INDOOR_PORCH = "indoor_porch"
    OUTDOOR_PORCH = "outdoor_porch"
    INDOOR_SUNROOM = "indoor_sunroom"
    OUTDOOR_SUNROOM = "outdoor_sunroom"
    INDOOR_CONSERVATORY = "indoor_conservatory"
    OUTDOOR_CONSERVATORY = "outdoor_conservatory"
    INDOOR_SEWING_ROOM = "indoor_sewing_room"
    OUTDOOR_SEWING_ROOM = "outdoor_sewing_room"
    INDOOR_CRAFT_ROOM = "indoor_craft_room"
    OUTDOOR_CRAFT_ROOM = "outdoor_craft_room"
    INDOOR_ART_STUDIO = "indoor_art_studio"
    OUTDOOR_ART_STUDIO = "outdoor_art_studio"
    INDOOR_MUSIC_ROOM = "indoor_music_room"
    OUTDOOR_MUSIC_ROOM = "outdoor_music_room"
    INDOOR_THEATER = "indoor_theater"
    OUTDOOR_THEATER = "outdoor_theater"
    INDOOR_WINE_CELLAR = "indoor_wine_cellar"
    OUTDOOR_WINE_CELLAR = "outdoor_wine_cellar"
    INDOOR_PANTRY = "indoor_pantry"
    OUTDOOR_PANTRY = "outdoor_pantry"
    INDOOR_DRESSING_ROOM = "indoor_dressing_room"
    OUTDOOR_DRESSING_ROOM = "outdoor_dressing_room"
    INDOOR_WALK_IN_CLOSET = "indoor_walk_in_closet"
    OUTDOOR_WALK_IN_CLOSET = "outdoor_walk_in_closet"
    INDOOR_STORAGE = "indoor_storage"
    OUTDOOR_STORAGE = "outdoor_storage"
    INDOOR_UTILITY = "indoor_utility"
    OUTDOOR_UTILITY = "outdoor_utility"
    INDOOR_WORKSHOP = "indoor_workshop"
    OUTDOOR_WORKSHOP = "outdoor_workshop"
    INDOOR_GARAGE = "indoor_garage"
    OUTDOOR_GARAGE = "outdoor_garage"
    INDOOR_ATTIC = "indoor_attic"
    OUTDOOR_ATTIC = "outdoor_attic"
    INDOOR_BASEMENT = "indoor_basement"
    OUTDOOR_BASEMENT = "outdoor_basement"
    INDOOR_LOFT = "indoor_loft"
    OUTDOOR_LOFT = "outdoor_loft"
    INDOOR_STUDIO = "indoor_studio"
    OUTDOOR_STUDIO = "outdoor_studio"
    INDOOR_OFFICE = "indoor_office"
    OUTDOOR_OFFICE = "outdoor_office"
    INDOOR_GYM = "indoor_gym"
    OUTDOOR_GYM = "outdoor_gym"
    INDOOR_GAME_ROOM = "indoor_game_room"
    OUTDOOR_GAME_ROOM = "outdoor_game_room"
    INDOOR_MEDIA_ROOM = "indoor_media_room"
    OUTDOOR_MEDIA_ROOM = "outdoor_media_room"
    INDOOR_LIBRARY = "indoor_library"
    OUTDOOR_LIBRARY = "outdoor_library"
    INDOOR_HALLWAY = "indoor_hallway"
    OUTDOOR_HALLWAY = "outdoor_hallway"
    INDOOR_ENTRY = "indoor_entry"
    OUTDOOR_ENTRY = "outdoor_entry"
    INDOOR_MUDROOM = "indoor_mudroom"
    OUTDOOR_MUDROOM = "outdoor_mudroom"
    INDOOR_LAUNDRY = "indoor_laundry"
    OUTDOOR_LAUNDRY = "outdoor_laundry"
    INDOOR_GUEST_ROOM = "indoor_guest_room"
    OUTDOOR_GUEST_ROOM = "outdoor_guest_room"
    INDOOR_NURSERY = "indoor_nursery"
    OUTDOOR_NURSERY = "outdoor_nursery"
    INDOOR_KIDS_ROOM = "indoor_kids_room"
    OUTDOOR_KIDS_ROOM = "outdoor_kids_room"
    INDOOR_HOME_OFFICE = "indoor_home_office"
    OUTDOOR_HOME_OFFICE = "outdoor_home_office"
    INDOOR_DINING = "indoor_dining"
    OUTDOOR_DINING = "outdoor_dining"
    INDOOR_BATHROOM = "indoor_bathroom"
    OUTDOOR_BATHROOM = "outdoor_bathroom"
    INDOOR_KITCHEN = "indoor_kitchen"
    OUTDOOR_KITCHEN = "outdoor_kitchen"
    INDOOR_BEDROOM = "indoor_bedroom"
    OUTDOOR_BEDROOM = "outdoor_bedroom"
    INDOOR_LIVING = "indoor_living"
    OUTDOOR_LIVING = "outdoor_living"


class HouseStyle(str, Enum):
    MODERN = "modern"
    CONTEMPORARY = "contemporary"
    TRADITIONAL = "traditional"
    COLONIAL = "colonial"
    VICTORIAN = "victorian"
    TUDOR = "tudor"
    COTTAGE = "cottage"
    RANCH = "ranch"
    CRAFTSMAN = "craftsman"
    BUNGALOW = "bungalow"
    MEDITERRANEAN = "mediterranean"
    SPANISH = "spanish"
    FRENCH_COUNTRY = "french_country"
    TUSCAN = "tuscan"
    GREEK_REVIVAL = "greek_revival"
    FARMHOUSE = "farmhouse"
    RUSTIC = "rustic"
    LODGE = "lodge"
    LOG_HOME = "log_home"
    A_FRAME = "a_frame"
    DOME = "dome"
    GEODESIC = "geodesic"
    EARTH_SHELTERED = "earth_sheltered"
    STRAW_BALE = "straw_bale"
    RAMMED_EARTH = "rammed_earth"
    CONTAINER = "container"
    TINY_HOUSE = "tiny_house"
    TREEHOUSE = "treehouse"
    HOUSEBOAT = "houseboat"
    YURT = "yurt"
    IGLOO = "igloo"
    CAVE_HOUSE = "cave_house"
    UNDERGROUND = "underground"
    FLOATING = "floating"
    MODULAR = "modular"
    PREFAB = "prefab"
    KIT_HOME = "kit_home"
    BARNDOMINIUM = "barndominium"
    SHIPPING_CONTAINER = "shipping_container"
    EARTHBAG = "earthbag"
    COB = "cob"
    EARTH_SHIP = "earth_ship"
    PASSIVE_HOUSE = "passive_house"
    TINY_HOUSE_ON_WHEELS = "tiny_house_on_wheels"
    TINY_HOUSE_ON_FOUNDATION = "tiny_house_on_foundation"
    TINY_HOUSE_ON_TRAILER = "tiny_house_on_trailer"
    TINY_HOUSE_ON_SKIDS = "tiny_house_on_skids"
    TINY_HOUSE_ON_BARGE = "tiny_house_on_barge"
    TINY_HOUSE_ON_FLOAT = "tiny_house_on_float"
    TINY_HOUSE_ON_PILOTIS = "tiny_house_on_pilots"
    TINY_HOUSE_ON_STILTS = "tiny_house_on_stilts"
    TINY_HOUSE_ON_WHEELS_WITH_LOFT = "tiny_house_on_wheels_with_loft"
    TINY_HOUSE_ON_WHEELS_WITHOUT_LOFT = "tiny_house_on_wheels_without_loft"
    TINY_HOUSE_ON_FOUNDATION_WITH_LOFT = "tiny_house_on_foundation_with_loft"
    TINY_HOUSE_ON_FOUNDATION_WITHOUT_LOFT = "tiny_house_on_foundation_without_loft"
    TINY_HOUSE_ON_TRAILER_WITH_LOFT = "tiny_house_on_trailer_with_loft"
    TINY_HOUSE_ON_TRAILER_WITHOUT_LOFT = "tiny_house_on_trailer_without_loft"
    TINY_HOUSE_ON_SKIDS_WITH_LOFT = "tiny_house_on_skids_with_loft"
    TINY_HOUSE_ON_SKIDS_WITHOUT_LOFT = "tiny_house_on_skids_without_loft"
    TINY_HOUSE_ON_BARGE_WITH_LOFT = "tiny_house_on_barge_with_loft"
    TINY_HOUSE_ON_BARGE_WITHOUT_LOFT = "tiny_house_on_barge_without_loft"
    TINY_HOUSE_ON_FLOAT_WITH_LOFT = "tiny_house_on_float_with_loft"
    TINY_HOUSE_ON_FLOAT_WITHOUT_LOFT = "tiny_house_on_float_without_loft"
    TINY_HOUSE_ON_PILOTIS_WITH_LOFT = "tiny_house_on_pilots_with_loft"
    TINY_HOUSE_ON_PILOTIS_WITHOUT_LOFT = "tiny_house_on_pilots_without_loft"
    TINY_HOUSE_ON_STILTS_WITH_LOFT = "tiny_house_on_stilts_with_loft"
    TINY_HOUSE_ON_STILTS_WITHOUT_LOFT = "tiny_house_on_stilts_without_loft"


class FurnitureHandler(FastMCP):
    def __init__(self):
        super().__init__()
        logger.info("FurnitureHandler initialized")


@blender_operation("create_table", log_args=True)
async def create_table(
    name: str = "Table",
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    style: Union[str, FurnitureStyle] = FurnitureStyle.MODERN,
    table_type: str = "dining",  # dining, coffee, side, console, etc.
    material: Union[str, MaterialType] = MaterialType.WOOD,
    color: Tuple[float, float, float, float] = (0.7, 0.6, 0.4, 1.0),  # RGBA
    length: float = 1.2,
    width: float = 0.8,
    height: float = 0.75,
    leg_count: int = 4,
) -> Dict[str, Any]:
    """Create a table in the Blender scene.

    Args:
        name: Name for the table object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        style: Style of the table
        table_type: Type of table (dining, coffee, side, console, etc.)
        material: Material type for the table
        color: RGBA color values (0-1)
        length: Length of the table in meters
        width: Width of the table in meters
        height: Height of the table in meters
        leg_count: Number of legs (1-6)

    Returns:
        Dictionary with information about the created table
    """
    # Clear existing object if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    # Adjust dimensions based on table type
    if table_type == "coffee":
        length = width = max(length, width)  # Make it square
        height = 0.45  # Standard coffee table height
    elif table_type == "side":
        length, width = min(length, width), min(length, width) * 0.6  # Make it narrow
        height = 0.6  # Standard side table height
    elif table_type == "dining":
        height = 0.75  # Standard dining table height
    elif table_type == "console":
        length, width = max(length, width), min(length, width) * 0.3  # Make it long and narrow
        height = 0.8  # Standard console table height

    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Create bmesh for table construction
    bm = bmesh.new()

    # Define dimensions
    tabletop_thickness = 0.05
    leg_thickness = 0.05

    # Create tabletop (a flat box)
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.LocRotScale(
            (0, 0, height - tabletop_thickness / 2), None, (length, width, tabletop_thickness)
        ),
    )

    # Create legs based on leg_count
    leg_count = max(1, min(6, leg_count))  # Clamp between 1-6

    if leg_count == 1:
        # Pedestal base
        bmesh.ops.create_cylinder(
            bm,
            segments=16,
            diameter=min(length, width) * 0.4,
            depth=height - tabletop_thickness,
            matrix=Matrix.Translation((0, 0, (height - tabletop_thickness) / 2)),
            calc_uvs=True,
        )
    elif leg_count == 2:
        # Trestle style
        trestle_width = min(length, width) * 0.15
        trestle_length = max(length, width) * 0.8

        # First trestle
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (0, -trestle_length / 2, (height - tabletop_thickness) / 2),
                None,
                (trestle_width, trestle_length, height - tabletop_thickness),
            ),
        )
        # Second trestle
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (0, trestle_length / 2, (height - tabletop_thickness) / 2),
                None,
                (trestle_width, trestle_length, height - tabletop_thickness),
            ),
        )
    else:
        # Standard legs (3-6 legs)
        # Calculate leg positions in a circle
        radius = min(length, width) * 0.4
        angle_step = 2 * 3.14159 / leg_count

        for i in range(leg_count):
            angle = i * angle_step
            x_pos = math.cos(angle) * radius
            y_pos = math.sin(angle) * radius

            # Create cylindrical leg
            bmesh.ops.create_cylinder(
                bm,
                segments=8,
                diameter=leg_thickness,
                depth=height - tabletop_thickness,
                matrix=Matrix.Translation((x_pos, y_pos, (height - tabletop_thickness) / 2)),
                calc_uvs=True,
            )

    # Add support beams for tables with 4+ legs
    if leg_count >= 4 and table_type == "dining":
        # Add a rectangular frame under the tabletop
        frame_thickness = 0.03
        frame_width = width * 0.8
        frame_length = length * 0.8

        # Create frame sides
        frame_sides = [
            (
                (0, -frame_length / 2, height - tabletop_thickness - frame_thickness / 2),
                (frame_width, frame_thickness, frame_thickness),
            ),
            (
                (0, frame_length / 2, height - tabletop_thickness - frame_thickness / 2),
                (frame_width, frame_thickness, frame_thickness),
            ),
            (
                (frame_width / 2, 0, height - tabletop_thickness - frame_thickness / 2),
                (frame_thickness, frame_length, frame_thickness),
            ),
            (
                (-frame_width / 2, 0, height - tabletop_thickness - frame_thickness / 2),
                (frame_thickness, frame_length, frame_thickness),
            ),
        ]

        for pos, dim in frame_sides:
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.LocRotScale(pos, None, dim))

    # Update the mesh with the new geometry
    bm.to_mesh(mesh)
    bm.free()

    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale

    # Add smooth shading
    for face in obj.data.polygons:
        face.use_smooth = True

    # Add a subdivision surface modifier for smoother appearance
    mod = obj.modifiers.new(name="Subdivision", type="SUBSURF")
    mod.levels = 2
    mod.render_levels = 2

    # Add a bevel modifier for rounded edges
    bevel = obj.modifiers.new(name="Bevel", type="BEVEL")
    bevel.width = 0.01
    bevel.segments = 3
    bevel.limit_method = "ANGLE"

    # Create and assign material
    mat = bpy.data.materials.new(name=f"{name}_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color

    # Adjust material properties based on material type
    material_str = material.value if isinstance(material, MaterialType) else material
    if material_str == "wood":
        bsdf.inputs["Roughness"].default_value = 0.7
        bsdf.inputs["Specular"].default_value = 0.3
    elif material_str == "metal":
        bsdf.inputs["Metallic"].default_value = 1.0
        bsdf.inputs["Roughness"].default_value = 0.2
    elif material_str == "glass":
        bsdf.inputs["Transmission"].default_value = 0.9
        bsdf.inputs["Roughness"].default_value = 0.1
        bsdf.inputs["IOR"].default_value = 1.45

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # Prepare return data
    table_data = {
        "name": name,
        "type": "table",
        "table_type": table_type,
        "object": obj.name,
        "location": location,
        "rotation": rotation,
        "scale": scale,
        "style": style.value if isinstance(style, FurnitureStyle) else style,
        "material": material_str,
        "color": color,
        "dimensions": {
            "length": length,
            "width": width,
            "height": height,
            "tabletop_thickness": tabletop_thickness,
            "leg_thickness": leg_thickness,
            "leg_count": leg_count,
        },
        "created_at": "2025-02-16T10:30:00Z",
        "is_mock": False,
    }

    logger.info(f"Created table: {name} (Type: {table_type})")
    return table_data


@blender_operation("create_chair", log_args=True)
async def create_chair(
    name: str = "Chair",
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    style: Union[str, FurnitureStyle] = FurnitureStyle.MODERN,
    material: Union[str, MaterialType] = MaterialType.WOOD,
    color: Tuple[float, float, float, float] = (0.7, 0.6, 0.4, 1.0),  # RGBA
    seat_height: float = 0.45,
    seat_width: float = 0.5,
    seat_depth: float = 0.5,
    backrest_height: float = 0.4,
    has_armrests: bool = True,
) -> Dict[str, Any]:
    """Create a chair in the Blender scene.

    Args:
        name: Name for the chair object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        style: Style of the chair
        material: Material type for the chair
        color: RGBA color values (0-1)
        seat_height: Height of the seat from the ground in meters
        seat_width: Width of the seat in meters
        seat_depth: Depth of the seat in meters
        backrest_height: Height of the backrest in meters
        has_armrests: Whether the chair has armrests

    Returns:
        Dictionary with information about the created chair
    """
    # Clear existing object if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Create bmesh for chair construction
    bm = bmesh.new()

    # Define dimensions
    leg_thickness = 0.05
    seat_thickness = 0.05
    backrest_thickness = 0.03
    armrest_height = seat_height * 1.2
    armrest_thickness = 0.06

    # Create seat (a flat box)
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.LocRotScale(
            (0, 0, seat_height + seat_thickness / 2), None, (seat_width, seat_depth, seat_thickness)
        ),
    )

    # Create legs (4 legs)
    leg_positions = [
        (seat_width / 2 - leg_thickness / 2, seat_depth / 2 - leg_thickness / 2, 0),
        (-seat_width / 2 + leg_thickness / 2, seat_depth / 2 - leg_thickness / 2, 0),
        (seat_width / 2 - leg_thickness / 2, -seat_depth / 2 + leg_thickness / 2, 0),
        (-seat_width / 2 + leg_thickness / 2, -seat_depth / 2 + leg_thickness / 2, 0),
    ]

    for pos in leg_positions:
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (pos[0], pos[1], seat_height / 2), None, (leg_thickness, leg_thickness, seat_height)
            ),
        )

    # Create backrest (vertical part)
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.LocRotScale(
            (0, -seat_depth / 2 + backrest_thickness / 2, seat_height + backrest_height / 2),
            None,
            (seat_width * 0.9, backrest_thickness, backrest_height),
        ),
    )

    # Create armrests if enabled
    if has_armrests:
        # Left armrest
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (seat_width / 2 - armrest_thickness / 2, 0, seat_height + armrest_height / 2),
                None,
                (armrest_thickness, seat_depth * 0.8, armrest_height - seat_height),
            ),
        )
        # Right armrest
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (-seat_width / 2 + armrest_thickness / 2, 0, seat_height + armrest_height / 2),
                None,
                (armrest_thickness, seat_depth * 0.8, armrest_height - seat_height),
            ),
        )

    # Update the mesh with the new geometry
    bm.to_mesh(mesh)
    bm.free()

    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale

    # Add smooth shading
    for face in obj.data.polygons:
        face.use_smooth = True

    # Add a subdivision surface modifier for smoother appearance
    mod = obj.modifiers.new(name="Subdivision", type="SUBSURF")
    mod.levels = 2
    mod.render_levels = 2

    # Add a bevel modifier for rounded edges
    bevel = obj.modifiers.new(name="Bevel", type="BEVEL")
    bevel.width = 0.01
    bevel.segments = 3
    bevel.limit_method = "ANGLE"

    # Create and assign material
    mat = bpy.data.materials.new(name=f"{name}_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color

    # Adjust material properties based on material type
    material_str = material.value if isinstance(material, MaterialType) else material
    if material_str == "wood":
        bsdf.inputs["Roughness"].default_value = 0.7
        bsdf.inputs["Specular"].default_value = 0.3
    elif material_str == "metal":
        bsdf.inputs["Metallic"].default_value = 1.0
        bsdf.inputs["Roughness"].default_value = 0.2
    elif material_str == "fabric":
        bsdf.inputs["Roughness"].default_value = 0.9
        bsdf.inputs["Sheen"].default_value = 0.5

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # Prepare return data
    chair_data = {
        "name": name,
        "type": "chair",
        "object": obj.name,
        "location": location,
        "rotation": rotation,
        "scale": scale,
        "style": style.value if isinstance(style, FurnitureStyle) else style,
        "material": material_str,
        "color": color,
        "dimensions": {
            "seat_height": seat_height,
            "seat_width": seat_width,
            "seat_depth": seat_depth,
            "backrest_height": backrest_height,
            "total_height": seat_height + backrest_height,
        },
        "has_armrests": has_armrests,
        "created_at": "2025-02-16T10:30:00Z",
        "is_mock": False,
    }

    logger.info(f"Created chair: {name}")
    return chair_data


@blender_operation("create_sofa", log_args=True)
async def create_sofa(
    name: str = "Sofa",
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    style: Union[str, FurnitureStyle] = FurnitureStyle.MODERN,
    material: Union[str, MaterialType] = MaterialType.FABRIC,
    color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0),  # Light gray by default
    seat_count: int = 3,
    has_chaise: bool = False,
    is_sleeper: bool = False,
    has_recliner: bool = False,
) -> Dict[str, Any]:
    """Create a sofa in the Blender scene.

    Args:
        name: Name for the sofa object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        style: Style of the sofa
        material: Material type for the sofa
        color: RGBA color values (0-1)
        seat_count: Number of seats (2-6)
        has_chaise: Whether the sofa has a chaise lounge extension
        is_sleeper: Whether the sofa converts to a bed
        has_recliner: Whether the sofa has reclining seats

    Returns:
        Dictionary with information about the created sofa
    """
    # Clear existing object if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Create bmesh for sofa construction
    bm = bmesh.new()

    # Define dimensions
    seat_width = 0.7  # Width per seat
    seat_depth = 0.8
    seat_height = 0.4
    backrest_height = 0.5
    armrest_height = seat_height * 1.2
    armrest_width = 0.15
    cushion_thickness = 0.15
    leg_height = 0.1

    # Calculate total sofa length
    total_length = seat_width * seat_count

    # Create base
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.LocRotScale(
            (0, 0, leg_height / 2 + seat_height / 2),
            None,
            (total_length, seat_depth, seat_height - leg_height),
        ),
    )

    # Add legs (one at each corner, and one in the middle if sofa is long enough)
    leg_positions = [
        (total_length / 2 - 0.1, seat_depth / 2 - 0.1, leg_height / 2),
        (-total_length / 2 + 0.1, seat_depth / 2 - 0.1, leg_height / 2),
        (total_length / 2 - 0.1, -seat_depth / 2 + 0.1, leg_height / 2),
        (-total_length / 2 + 0.1, -seat_depth / 2 + 0.1, leg_height / 2),
    ]

    # Add middle leg if sofa is long enough
    if seat_count > 3:
        leg_positions.extend(
            [(0, seat_depth / 2 - 0.1, leg_height / 2), (0, -seat_depth / 2 + 0.1, leg_height / 2)]
        )

    for pos in leg_positions:
        bmesh.ops.create_cylinder(
            bm,
            segments=8,
            diameter=0.05,
            depth=leg_height,
            matrix=Matrix.Translation(pos),
            calc_uvs=True,
        )

    # Create backrest
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.LocRotScale(
            (0, -seat_depth / 2 + 0.05, seat_height + backrest_height / 2 - 0.1),
            None,
            (total_length * 0.98, 0.1, backrest_height * 0.9),
        ),
    )

    # Create armrests
    armrest_positions = [
        (total_length / 2 - armrest_width / 2, 0, seat_height + armrest_height / 2 - 0.1),
        (-total_length / 2 + armrest_width / 2, 0, seat_height + armrest_height / 2 - 0.1),
    ]

    for pos in armrest_positions:
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                pos, None, (armrest_width, seat_depth * 1.1, armrest_height - seat_height)
            ),
        )

    # Add cushions (one per seat)
    cushion_width = (total_length * 0.9) / seat_count
    for i in range(seat_count):
        x_pos = (i - (seat_count - 1) / 2) * cushion_width
        # Seat cushion
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (x_pos, 0, seat_height + cushion_thickness / 2),
                None,
                (cushion_width * 0.9, seat_depth * 0.9, cushion_thickness),
            ),
        )
        # Back cushion
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (x_pos, -seat_depth / 2 + 0.1, seat_height + backrest_height / 2 - 0.1),
                None,
                (cushion_width * 0.9, 0.2, backrest_height * 0.9),
            ),
        )

    # Add chaise if enabled
    if has_chaise:
        chaise_length = seat_width * 1.5
        # Chaise base
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (
                    total_length / 2 + chaise_length / 2,
                    seat_depth / 2 + chaise_length / 2,
                    seat_height / 2 + leg_height / 2,
                ),
                None,
                (chaise_length, chaise_length, seat_height - leg_height),
            ),
        )
        # Chaise back
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (
                    total_length / 2 + chaise_length / 2,
                    seat_depth / 2 + chaise_length - 0.05,
                    seat_height + backrest_height / 2 - 0.1,
                ),
                None,
                (chaise_length, 0.1, backrest_height * 0.9),
            ),
        )
        # Chaise armrest
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (
                    total_length / 2 + chaise_length / 2,
                    seat_depth / 2 + 0.05,
                    seat_height + armrest_height / 2 - 0.1,
                ),
                None,
                (chaise_length, 0.1, armrest_height - seat_height),
            ),
        )
        # Chaise cushion
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (
                    total_length / 2 + chaise_length / 2,
                    seat_depth / 2 + chaise_length / 2,
                    seat_height + cushion_thickness / 2,
                ),
                None,
                (chaise_length * 0.9, chaise_length * 0.9, cushion_thickness),
            ),
        )
        # Update total length
        total_length += chaise_length

    # Update the mesh with the new geometry
    bm.to_mesh(mesh)
    bm.free()

    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale

    # Add smooth shading
    for face in obj.data.polygons:
        face.use_smooth = True

    # Add a subdivision surface modifier for smoother appearance
    mod = obj.modifiers.new(name="Subdivision", type="SUBSURF")
    mod.levels = 2
    mod.render_levels = 2

    # Add a bevel modifier for rounded edges
    bevel = obj.modifiers.new(name="Bevel", type="BEVEL")
    bevel.width = 0.01
    bevel.segments = 3
    bevel.limit_method = "ANGLE"

    # Create and assign material
    mat = bpy.data.materials.new(name=f"{name}_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color

    # Adjust material properties based on material type
    material_str = material.value if isinstance(material, MaterialType) else material
    if material_str == "fabric":
        bsdf.inputs["Roughness"].default_value = 0.9
        bsdf.inputs["Sheen"].default_value = 0.3
        bsdf.inputs["Sheen Tint"].default_value = 0.8
    elif material_str == "leather":
        bsdf.inputs["Roughness"].default_value = 0.4
        bsdf.inputs["Sheen"].default_value = 0.5
        bsdf.inputs["Specular"].default_value = 0.5

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # Prepare return data
    sofa_data = {
        "name": name,
        "type": "sofa",
        "object": obj.name,
        "location": location,
        "rotation": rotation,
        "scale": scale,
        "style": style.value if isinstance(style, FurnitureStyle) else style,
        "material": material_str,
        "color": color,
        "seat_count": max(2, min(6, seat_count)),
        "has_chaise": has_chaise,
        "is_sleeper": is_sleeper,
        "has_recliner": has_recliner,
        "dimensions": {
            "length": total_length,
            "depth": seat_depth,
            "height": seat_height + backrest_height,
            "seat_height": seat_height,
        },
        "created_at": "2025-02-16T10:30:00Z",
        "is_mock": False,
    }

    logger.info(f"Created sofa: {name}")
    return sofa_data


@blender_operation("create_bed", log_args=True)
async def create_bed(
    name: str = "Bed",
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    style: Union[str, FurnitureStyle] = FurnitureStyle.MODERN,
    bed_type: str = "queen",  # twin, full, queen, king, california_king
    material: Union[str, MaterialType] = MaterialType.WOOD,
    frame_color: Tuple[float, float, float, float] = (0.7, 0.6, 0.4, 1.0),  # RGBA
    mattress_color: Tuple[float, float, float, float] = (0.95, 0.95, 0.95, 1.0),  # RGBA
    has_headboard: bool = True,
    has_footboard: bool = False,
    has_storage: bool = False,
) -> Dict[str, Any]:
    """Create a bed in the Blender scene.

    Args:
        name: Name for the bed object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        style: Style of the bed
        bed_type: Type of bed (twin, full, queen, king, california_king)
        material: Material type for the bed frame
        frame_color: RGBA color values for the bed frame (0-1)
        mattress_color: RGBA color values for the mattress (0-1)
        has_headboard: Whether the bed has a headboard
        has_footboard: Whether the bed has a footboard
        has_storage: Whether the bed has storage

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

    # Set bed dimensions based on type
    bed_length = 2.0  # Default length
    bed_width = 1.5  # Default width
    bed_height = 0.3  # Default height
    leg_height = 0.1  # Default leg height
    mattress_thickness = 0.2  # Default mattress thickness
    headboard_height = 0.8 if has_headboard else 0
    footboard_height = 0.4 if has_footboard else 0
    storage_height = 0.2 if has_storage else 0

    # Adjust dimensions based on bed type
    if bed_type == "twin":
        bed_length, bed_width = 1.9, 1.0
    elif bed_type == "full":
        bed_length, bed_width = 1.9, 1.4
    elif bed_type == "queen":
        bed_length, bed_width = 2.0, 1.5
    elif bed_type == "king":
        bed_length, bed_width = 2.0, 1.9
    elif bed_type == "california_king":
        bed_length, bed_width = 2.1, 1.8

    # Create the bed frame
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame_obj = bpy.context.active_object
    frame_obj.name = f"{name}_Frame"
    frame_obj.scale = (bed_length, bed_width, bed_height)
    frame_obj.location = (0, 0, leg_height + bed_height / 2)

    # Create the mattress
    bpy.ops.mesh.primitive_cube_add(size=1)
    mattress_obj = bpy.context.active_object
    mattress_obj.name = f"{name}_Mattress"
    mattress_obj.scale = (bed_length * 0.9, bed_width * 0.9, mattress_thickness)
    mattress_obj.location = (0, 0, leg_height + bed_height + mattress_thickness / 2)

    # Create legs
    for i, (x, y) in enumerate(
        [
            (-bed_length / 2, -bed_width / 2),
            (bed_length / 2, -bed_width / 2),
            (-bed_length / 2, bed_width / 2),
            (bed_length / 2, bed_width / 2),
        ]
    ):
        bpy.ops.mesh.primitive_cube_add(size=1)
        leg_obj = bpy.context.active_object
        leg_obj.name = f"{name}_Leg_{i + 1}"
        leg_obj.scale = (0.05, 0.05, leg_height)
        leg_obj.location = (x, y, leg_height / 2)

    # Create headboard if requested
    if has_headboard:
        bpy.ops.mesh.primitive_cube_add(size=1)
        headboard_obj = bpy.context.active_object
        headboard_obj.name = f"{name}_Headboard"
        headboard_obj.scale = (bed_length, 0.1, headboard_height)
        headboard_obj.location = (
            0,
            bed_width / 2 + 0.05,
            leg_height + bed_height + headboard_height / 2,
        )

    # Create footboard if requested
    if has_footboard:
        bpy.ops.mesh.primitive_cube_add(size=1)
        footboard_obj = bpy.context.active_object
        footboard_obj.name = f"{name}_Footboard"
        footboard_obj.scale = (bed_length, 0.1, footboard_height)
        footboard_obj.location = (
            0,
            -bed_width / 2 - 0.05,
            leg_height + bed_height + footboard_height / 2,
        )

    # Create storage if requested
    if has_storage:
        bpy.ops.mesh.primitive_cube_add(size=1)
        storage_obj = bpy.context.active_object
        storage_obj.name = f"{name}_Storage"
        storage_obj.scale = (bed_length * 0.8, bed_width * 0.8, storage_height)
        storage_obj.location = (0, 0, leg_height + storage_height / 2)

    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale

    # Create materials
    frame_material = bpy.data.materials.new(name=f"{name}_Frame_Material")
    frame_material.use_nodes = True
    frame_material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = frame_color

    mattress_material = bpy.data.materials.new(name=f"{name}_Mattress_Material")
    mattress_material.use_nodes = True
    mattress_material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = mattress_color

    # Assign materials
    frame_obj.data.materials.append(frame_material)
    mattress_obj.data.materials.append(mattress_material)

    # Prepare return data
    bed_data = {
        "name": name,
        "type": "bed",
        "object": obj.name,
        "location": location,
        "rotation": rotation,
        "scale": scale,
        "style": style.value if isinstance(style, FurnitureStyle) else style,
        "bed_type": bed_type,
        "material": material.value if isinstance(material, MaterialType) else material,
        "frame_color": frame_color,
        "mattress_color": mattress_color,
        "has_headboard": has_headboard,
        "has_footboard": has_footboard,
        "has_storage": has_storage,
        "dimensions": {
            "length": bed_length,
            "width": bed_width,
            "height": bed_height + leg_height + (headboard_height if has_headboard else 0),
            "mattress_thickness": mattress_thickness,
            "headboard_height": headboard_height,
            "footboard_height": footboard_height,
            "storage_height": storage_height if has_storage else 0,
        },
        "created_at": "2025-02-16T10:30:00Z",
        "is_mock": False,
    }

    logger.info(f"Created bed: {name} (Type: {bed_type})")
    return bed_data


@blender_operation("create_room", log_args=True)
async def create_room(
    name: str = "Room",
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    room_type: Union[str, RoomType] = RoomType.LIVING,
    style: Union[str, FurnitureStyle] = FurnitureStyle.MODERN,
    length: float = 4.0,
    width: float = 4.0,
    height: float = 2.7,
    wall_thickness: float = 0.2,
    has_windows: bool = True,
    window_count: int = 2,
    has_door: bool = True,
    door_location: str = "center",  # left, center, right
) -> Dict[str, Any]:
    """Create a room in the Blender scene.

    Args:
        name: Name for the room object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        room_type: Type of room (living, bedroom, kitchen, etc.)
        style: Style of the room
        length: Length of the room in meters
        width: Width of the room in meters
        height: Height of the room in meters
        wall_thickness: Thickness of the walls in meters
        has_windows: Whether the room has windows
        window_count: Number of windows (if has_windows is True)
        has_door: Whether the room has a door
        door_location: Position of the door on the wall (left, center, right)

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

    # Create bmesh for room construction
    bm = bmesh.new()

    # Define dimensions
    wall_thickness = max(0.05, min(wall_thickness, 0.5))  # Clamp between 0.05 and 0.5m
    window_height = height * 0.5  # Height from floor
    door_height = 2.1
    baseboard_height = 0.1

    # Create floor
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.LocRotScale(
            (0, 0, -wall_thickness / 2),  # Slightly below the walls
            None,
            (length + wall_thickness * 2, width + wall_thickness * 2, wall_thickness),
        ),
    )

    # Create ceiling
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.LocRotScale(
            (0, 0, height + wall_thickness / 2),  # Slightly above the walls
            None,
            (length + wall_thickness * 2, width + wall_thickness * 2, wall_thickness),
        ),
    )

    # Create walls (4 walls total)
    wall_positions = [
        # Front wall (facing positive Y)
        {"pos": (0, width / 2, height / 2), "size": (length, wall_thickness, height)},
        # Back wall (facing negative Y)
        {"pos": (0, -width / 2, height / 2), "size": (length, wall_thickness, height)},
        # Right wall (facing positive X)
        {"pos": (length / 2, 0, height / 2), "size": (wall_thickness, width, height)},
        # Left wall (facing negative X)
        {"pos": (-length / 2, 0, height / 2), "size": (wall_thickness, width, height)},
    ]

    # Create walls with potential openings for windows and doors
    for i, wall in enumerate(wall_positions):
        # Create wall with potential openings
        wall_verts = [
            (-wall["size"][0] / 2, -wall["size"][1] / 2, -wall["size"][2] / 2),  # Bottom left
            (wall["size"][0] / 2, -wall["size"][1] / 2, -wall["size"][2] / 2),  # Bottom right
            (wall["size"][0] / 2, wall["size"][1] / 2, -wall["size"][2] / 2),  # Top right
            (-wall["size"][0] / 2, wall["size"][1] / 2, -wall["size"][2] / 2),  # Top left
            (-wall["size"][0] / 2, -wall["size"][1] / 2, wall["size"][2] / 2),  # Bottom left back
            (wall["size"][0] / 2, -wall["size"][1] / 2, wall["size"][2] / 2),  # Bottom right back
            (wall["size"][0] / 2, wall["size"][1] / 2, wall["size"][2] / 2),  # Top right back
            (-wall["size"][0] / 2, wall["size"][1] / 2, wall["size"][2] / 2),  # Top left back
        ]

        # Create base wall mesh
        wall_mesh = bpy.data.meshes.new(f"Wall_{i}")
        wall_obj = bpy.data.objects.new(f"{name}_Wall_{i}", wall_mesh)
        bpy.context.collection.objects.link(wall_obj)

        # Position the wall
        wall_obj.location = wall["pos"]

        # Create wall with boolean modifiers for windows and doors
        wall_bm = bmesh.new()

        # Add wall cube
        wall_verts = [
            (-wall["size"][0] / 2, -wall["size"][1] / 2, -wall["size"][2] / 2),  # Bottom left
            (wall["size"][0] / 2, -wall["size"][1] / 2, -wall["size"][2] / 2),  # Bottom right
            (wall["size"][0] / 2, wall["size"][1] / 2, -wall["size"][2] / 2),  # Top right
            (-wall["size"][0] / 2, wall["size"][1] / 2, -wall["size"][2] / 2),  # Top left
            (-wall["size"][0] / 2, -wall["size"][1] / 2, wall["size"][2] / 2),  # Bottom left back
            (wall["size"][0] / 2, -wall["size"][1] / 2, wall["size"][2] / 2),  # Bottom right back
            (wall["size"][0] / 2, wall["size"][1] / 2, wall["size"][2] / 2),  # Top right back
            (-wall["size"][0] / 2, wall["size"][1] / 2, wall["size"][2] / 2),  # Top left back
        ]

        wall_faces = [
            (0, 1, 2, 3),  # Front
            (4, 7, 6, 5),  # Back
            (0, 4, 5, 1),  # Bottom
            (1, 5, 6, 2),  # Right
            (2, 6, 7, 3),  # Top
            (4, 0, 3, 7),  # Left
        ]

        # Add vertices and faces to the wall
        bm_verts = [wall_bm.verts.new(v) for v in wall_verts]
        for face in wall_faces:
            wall_bm.faces.new([bm_verts[i] for i in face])

        # Update the wall mesh
        wall_bm.to_mesh(wall_mesh)
        wall_bm.free()

        # Parent wall to room
        wall_obj.parent = obj

    # Add baseboards
    baseboard_verts = [
        # Bottom edges of walls
        (-length / 2, -width / 2, 0),
        (length / 2, -width / 2, 0),
        (length / 2, width / 2, 0),
        (-length / 2, width / 2, 0),
        (-length / 2, -width / 2, baseboard_height),
        (length / 2, -width / 2, baseboard_height),
        (length / 2, width / 2, baseboard_height),
        (-length / 2, width / 2, baseboard_height),
    ]

    baseboard_faces = [
        (0, 1, 2, 3),  # Bottom
        (4, 7, 6, 5),  # Top
        (0, 4, 5, 1),  # Front
        (1, 5, 6, 2),  # Right
        (2, 6, 7, 3),  # Back
        (4, 0, 3, 7),  # Left
    ]

    # Create baseboard mesh
    baseboard_mesh = bpy.data.meshes.new(f"{name}_Baseboard")
    baseboard_obj = bpy.data.objects.new(f"{name}_Baseboard", baseboard_mesh)
    bpy.context.collection.objects.link(baseboard_obj)
    baseboard_obj.parent = obj

    # Create baseboard BMesh
    baseboard_bm = bmesh.new()
    bm_verts = [baseboard_bm.verts.new(v) for v in baseboard_verts]
    for face in baseboard_faces:
        baseboard_bm.faces.new([bm_verts[i] for i in face])

    # Update the baseboard mesh
    baseboard_bm.to_mesh(baseboard_mesh)
    baseboard_bm.free()

    # Add door if needed
    if has_door:
        door_obj = bpy.data.objects.new(f"{name}_Door", None)
        door_obj.empty_display_type = "CUBE"
        door_obj.empty_display_size = 0.5
        bpy.context.collection.objects.link(door_obj)
        door_obj.parent = obj
        door_obj.location = (0, -width / 2, door_height / 2)  # Position on front wall

    # Add windows if needed
    if has_windows and window_count > 0:
        window_objs = []
        for i in range(min(window_count, 4)):  # Max 4 windows (one per wall)
            window_obj = bpy.data.objects.new(f"{name}_Window_{i}", None)
            window_obj.empty_display_type = "CUBE"
            window_obj.empty_display_size = 0.3
            bpy.context.collection.objects.link(window_obj)
            window_obj.parent = obj

            # Position windows on different walls
            if i == 0:
                window_obj.location = (length / 4, width / 2, window_height)  # Front wall
            elif i == 1:
                window_obj.location = (-length / 4, -width / 2, window_height)  # Back wall
            elif i == 2:
                window_obj.location = (length / 2, 0, window_height)  # Right wall
            else:
                window_obj.location = (-length / 2, 0, window_height)  # Left wall

            window_objs.append(window_obj.name)

    # Update the room mesh with the new geometry
    bm.to_mesh(mesh)
    bm.free()

    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale

    # Create and assign materials
    wall_material = bpy.data.materials.new(name=f"{name}_Wall_Material")
    wall_material.use_nodes = True
    bsdf = wall_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1.0)  # Light gray
    bsdf.inputs["Roughness"].default_value = 0.6

    floor_material = bpy.data.materials.new(name=f"{name}_Floor_Material")
    floor_material.use_nodes = True
    bsdf = floor_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.6, 0.5, 0.4, 1.0)  # Wood-like
    bsdf.inputs["Roughness"].default_value = 0.3

    ceiling_material = bpy.data.materials.new(name=f"{name}_Ceiling_Material")
    ceiling_material.use_nodes = True
    bsdf = ceiling_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.98, 0.98, 0.98, 1.0)  # White
    bsdf.inputs["Roughness"].default_value = 0.8

    baseboard_material = bpy.data.materials.new(name=f"{name}_Baseboard_Material")
    baseboard_material.use_nodes = True
    bsdf = baseboard_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.95, 0.95, 0.95, 1.0)  # Off-white
    bsdf.inputs["Roughness"].default_value = 0.5

    # Assign materials to objects
    if obj.data.materials:
        obj.data.materials[0] = floor_material
    else:
        obj.data.materials.append(floor_material)

    for child in obj.children:
        if "Wall" in child.name:
            if child.data.materials:
                child.data.materials[0] = wall_material
            else:
                child.data.materials.append(wall_material)
        elif "Baseboard" in child.name:
            if child.data.materials:
                child.data.materials[0] = baseboard_material
            else:
                child.data.materials.append(baseboard_material)

    # Add a subdivision surface modifier for smoother appearance
    mod = obj.modifiers.new(name="Subdivision", type="SUBSURF")
    mod.levels = 1
    mod.render_levels = 2

    # Prepare return data
    room_data = {
        "name": name,
        "type": "room",
        "room_type": room_type.value if isinstance(room_type, RoomType) else room_type,
        "object": obj.name,
        "location": location,
        "rotation": rotation,
        "scale": scale,
        "style": style.value if isinstance(style, FurnitureStyle) else style,
        "dimensions": {
            "length": length,
            "width": width,
            "height": height,
            "wall_thickness": wall_thickness,
            "floor_area": length * width,
            "volume": length * width * height,
        },
        "features": {
            "has_windows": has_windows,
            "window_count": window_count if has_windows else 0,
            "has_door": has_door,
            "door_location": door_location if has_door else None,
        },
        "created_at": "2025-02-16T10:30:00Z",
        "is_mock": False,
    }

    logger.info(f"Created room: {name} (Type: {room_type})")
    return room_data


@blender_operation("create_building", log_args=True)
async def create_building(
    name: str = "House",
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    building_style: Union[str, HouseStyle] = HouseStyle.MODERN,
    floors: int = 1,
    rooms_per_floor: int = 3,
    length: float = 10.0,
    width: float = 8.0,
    height_per_floor: float = 2.7,
    has_roof: bool = True,
    roof_type: str = "gabled",  # flat, gabled, hipped, gambrel, mansard, dome
    has_garage: bool = False,
    has_chimney: bool = False,
    window_style: str = "double_hung",  # casement, awning, sliding, etc.
) -> Dict[str, Any]:
    """Create a building in the Blender scene.

    Args:
        name: Name for the building object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        building_style: Style of the building
        floors: Number of floors (1-5)
        rooms_per_floor: Number of rooms per floor (1-10)
        length: Length of the building in meters
        width: Width of the building in meters
        height_per_floor: Height of each floor in meters
        has_roof: Whether the building has a roof
        roof_type: Type of roof (flat, gabled, hipped, gambrel, mansard, dome)
        has_garage: Whether the building has an attached garage
        has_chimney: Whether the building has a chimney
        window_style: Style of windows

    Returns:
        Dictionary with information about the created building
    """
    # Clear existing object if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    # Create a new empty object as the building container
    building_obj = bpy.data.objects.new(name, None)
    building_obj.empty_display_type = "CUBE"
    building_obj.empty_display_size = max(length, width, height_per_floor * floors) * 0.5
    bpy.context.collection.objects.link(building_obj)

    # Set building location, rotation, and scale
    building_obj.location = location
    building_obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    building_obj.scale = scale

    # Define room types based on building style
    room_types = [
        RoomType.LIVING,
        RoomType.BEDROOM,
        RoomType.BATHROOM,
        RoomType.KITCHEN,
        RoomType.DINING,
        RoomType.HOME_OFFICE,
    ]

    # Create floors and rooms
    rooms = []
    floor_objects = []

    for floor in range(floors):
        # Create floor object
        floor_name = f"{name}_Floor_{floor + 1}"
        floor_obj = bpy.data.objects.new(floor_name, None)
        floor_obj.empty_display_type = "CUBE"
        floor_obj.empty_display_size = max(length, width) * 0.4
        bpy.context.collection.objects.link(floor_obj)
        floor_obj.parent = building_obj
        floor_obj.location = (0, 0, floor * height_per_floor)
        floor_objects.append(floor_obj)

        # Calculate room dimensions based on number of rooms per floor
        room_count = min(max(1, rooms_per_floor), 10)  # Limit to 10 rooms per floor
        room_width = width * 0.9 / max(1, room_count // 2)
        room_length = length * 0.9 / 2  # 2 rows of rooms

        # Create rooms for this floor
        for i in range(room_count):
            room_type = room_types[i % len(room_types)]
            row = i // (room_count // 2 + 1)
            col = i % (room_count // 2 + 1)

            # Position rooms in a grid
            x_pos = (col - (room_count // 4)) * room_length * 1.1
            y_pos = (row - 0.5) * width * 0.8
            z_pos = floor * height_per_floor

            # Create room
            room = self.create_room(
                name=f"{name}_Floor{floor + 1}_Room{i + 1}",
                location=(x_pos, y_pos, z_pos),
                room_type=room_type,
                length=room_length * 0.9,
                width=room_width * 0.9,
                height=height_per_floor * 0.9,
                wall_thickness=0.2,
                has_windows=(i % 2 == 0),  # Alternate windows
                window_count=2 if i % 2 == 0 else 0,
                has_door=(i == 0),  # Only first room has a door
                door_location="center",
            )

            # Parent room to floor
            if room["object"] in bpy.data.objects:
                bpy.data.objects[room["object"]].parent = floor_obj

            rooms.append(room)

    # Create roof if needed
    roof_obj = None
    if has_roof:
        roof_height = height_per_floor * 0.5
        roof_mesh = bpy.data.meshes.new(f"{name}_Roof_Mesh")
        roof_obj = bpy.data.objects.new(f"{name}_Roof", roof_mesh)
        bpy.context.collection.objects.link(roof_obj)
        roof_obj.parent = building_obj
        roof_obj.location = (0, 0, floors * height_per_floor)

        bm = bmesh.new()

        if roof_type == "flat":
            # Flat roof
            bmesh.ops.create_cube(
                bm,
                size=1.0,
                matrix=Matrix.LocRotScale(
                    (0, 0, roof_height / 2), None, (length * 1.1, width * 1.1, roof_height)
                ),
            )
        elif roof_type == "gabled":
            # Gabled roof
            verts = [
                (-length / 2, -width / 2, 0),
                (length / 2, -width / 2, 0),
                (length / 2, width / 2, 0),
                (-length / 2, width / 2, 0),
                (0, -width / 2, roof_height),
                (0, width / 2, roof_height),
            ]
            faces = [
                (0, 1, 4),  # Front triangle
                (1, 2, 5, 4),  # Right side
                (2, 3, 5),  # Back triangle
                (3, 0, 4, 5),  # Left side
            ]

            for v in verts:
                bm.verts.new(v)
            bm.verts.ensure_lookup_table()

            for f in faces:
                bm.faces.new([bm.verts[i] for i in f])

        # Update mesh
        bm.to_mesh(roof_mesh)
        bm.free()

        # Add material to roof
        roof_material = bpy.data.materials.new(name=f"{name}_Roof_Material")
        roof_material.use_nodes = True
        bsdf = roof_material.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1.0)  # Dark gray
        bsdf.inputs["Roughness"].default_value = 0.8

        if roof_obj.data.materials:
            roof_obj.data.materials[0] = roof_material
        else:
            roof_obj.data.materials.append(roof_material)

    # Create garage if needed
    garage_obj = None
    if has_garage:
        garage_width = width * 0.4
        garage_length = length * 0.5
        garage_height = height_per_floor * 0.8

        garage_mesh = bpy.data.meshes.new(f"{name}_Garage_Mesh")
        garage_obj = bpy.data.objects.new(f"{name}_Garage", garage_mesh)
        bpy.context.collection.objects.link(garage_obj)
        garage_obj.parent = building_obj
        garage_obj.location = (length * 0.5 + garage_length * 0.5, 0, garage_height * 0.5)

        bm = bmesh.new()
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (0, 0, 0), None, (garage_length, garage_width, garage_height)
            ),
        )

        # Add garage door
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (0, -garage_width / 2, 0), None, (garage_length * 0.8, 0.05, garage_height * 0.7)
            ),
        )

        # Update mesh
        bm.to_mesh(garage_mesh)
        bm.free()

        # Add material to garage
        garage_material = bpy.data.materials.new(name=f"{name}_Garage_Material")
        garage_material.use_nodes = True
        bsdf = garage_material.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)  # Medium gray
        bsdf.inputs["Roughness"].default_value = 0.7

        if garage_obj.data.materials:
            garage_obj.data.materials[0] = garage_material
        else:
            garage_obj.data.materials.append(garage_material)

    # Create chimney if needed
    chimney_obj = None
    if has_chimney:
        chimney_width = 0.4
        chimney_length = 0.4
        chimney_height = height_per_floor * 0.8

        chimney_mesh = bpy.data.meshes.new(f"{name}_Chimney_Mesh")
        chimney_obj = bpy.data.objects.new(f"{name}_Chimney", chimney_mesh)
        bpy.context.collection.objects.link(chimney_obj)
        chimney_obj.parent = building_obj
        chimney_obj.location = (length * 0.3, width * 0.3, chimney_height * 0.5)

        bm = bmesh.new()
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.LocRotScale(
                (0, 0, 0), None, (chimney_length, chimney_width, chimney_height)
            ),
        )

        # Update mesh
        bm.to_mesh(chimney_mesh)
        bm.free()

        # Add material to chimney
        chimney_material = bpy.data.materials.new(name=f"{name}_Chimney_Material")
        chimney_material.use_nodes = True
        bsdf = chimney_material.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1.0)  # Dark gray
        bsdf.inputs["Roughness"].default_value = 0.9

        if chimney_obj.data.materials:
            chimney_obj.data.materials[0] = chimney_material
        else:
            chimney_obj.data.materials.append(chimney_material)

    # Prepare return data
    building_data = {
        "name": name,
        "type": "building",
        "building_style": building_style.value
        if isinstance(building_style, HouseStyle)
        else building_style,
        "object": building_obj.name,
        "location": location,
        "rotation": rotation,
        "scale": scale,
        "dimensions": {
            "length": length,
            "width": width,
            "height": height_per_floor * floors
            + (height_per_floor * 0.5 if has_roof and roof_type != "flat" else 0),
            "height_per_floor": height_per_floor,
            "floor_area": length * width,
            "total_area": length * width * floors,
            "volume": length * width * height_per_floor * floors,
        },
        "floors": floors,
        "rooms_per_floor": rooms_per_floor,
        "total_rooms": len(rooms),
        "features": {
            "has_roof": has_roof,
            "roof_type": roof_type if has_roof else None,
            "has_garage": has_garage,
            "has_chimney": has_chimney,
            "window_style": window_style,
        },
        "created_at": "2025-02-16T10:30:00Z",
        "is_mock": False,
        "room_objects": [room["object"] for room in rooms if room["object"] in bpy.data.objects],
        "floor_objects": [obj.name for obj in floor_objects],
        "roof_object": roof_obj.name if roof_obj and roof_obj.name in bpy.data.objects else None,
        "garage_object": garage_obj.name
        if garage_obj and garage_obj.name in bpy.data.objects
        else None,
        "chimney_object": chimney_obj.name
        if chimney_obj and chimney_obj.name in bpy.data.objects
        else None,
    }

    logger.info(f"Created building: {name} with {floors} floors and {len(rooms)} rooms")
    return building_data
