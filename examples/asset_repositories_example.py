"""
Example: Using Blender MCP Asset Repositories

This example demonstrates how to download and import free assets from various repositories
including Kenney Assets, Quaternius, Open Game Art, and Poly Haven.
"""

import asyncio

from blender_mcp.handlers.asset_repository_handler import (
    AssetRepository,
    download_and_import_asset,
    list_available_assets,
    search_assets,
)


async def example_kenney_assets():
    """Download and import assets from Kenney.nl."""
    print("🎨 Downloading Kenney Fantasy Town Kit...")

    result = await download_and_import_asset(
        repository=AssetRepository.KENNEY,
        asset_name="fantasy-town-kit",
        import_options={"scale": 1.0, "location": [0, 0, 0]},
    )

    print(f"✅ Result: {result['status']}")
    if result["status"] == "SUCCESS":
        print(f"📦 Downloaded: {result['asset_name']}")
        print(f"📁 Files: {len(result.get('all_downloaded_files', []))}")
    else:
        print(f"❌ Error: {result['error']}")


async def example_quaternius_assets():
    """Download and import assets from Quaternius.com."""
    print("\n🚀 Downloading Quaternius Ultimate Space Kit...")

    result = await download_and_import_asset(
        repository=AssetRepository.QUATERNIUS,
        asset_name="ultimate-space-kit",
        import_options={"scale": 0.5, "location": [10, 0, 0]},
    )

    print(f"✅ Result: {result['status']}")
    if result["status"] == "SUCCESS":
        print(f"📦 Downloaded: {result['asset_name']}")
        print(f"📁 Files: {len(result.get('all_downloaded_files', []))}")
    else:
        print(f"❌ Error: {result['error']}")


async def example_opengameart_assets():
    """Download assets from OpenGameArt.org using direct URLs."""
    print("\n🎮 Downloading from OpenGameArt...")

    # Example URL - replace with actual download link from OpenGameArt
    example_url = "https://opengameart.org/sites/default/files/example_asset.zip"

    result = await download_and_import_asset(
        repository=AssetRepository.OPEN_GAME_ART,
        asset_name="community_asset",
        repository_specific_params={"url": example_url},
        import_options={"scale": 1.0, "location": [0, 10, 0]},
    )

    print(f"✅ Result: {result['status']}")
    if result["status"] == "SUCCESS":
        print("📦 Downloaded from OpenGameArt")
    else:
        print(f"❌ Error: {result['error']}")


async def example_polyhaven_hdri():
    """Download HDRI environment from Poly Haven."""
    print("\n🌅 Downloading HDRI from Poly Haven...")

    result = await download_and_import_asset(
        repository=AssetRepository.POLY_HAVEN,
        asset_name="lebombo",
        repository_specific_params={"type": "hdris"},
        import_options={"format": "hdr"},
    )

    print(f"✅ Result: {result['status']}")
    if result["status"] == "SUCCESS":
        print("📦 Downloaded HDRI: lebombo")
    else:
        print(f"❌ Error: {result['error']}")


async def example_polyhaven_texture():
    """Download PBR texture from Poly Haven."""
    print("\n🧱 Downloading texture from Poly Haven...")

    result = await download_and_import_asset(
        repository=AssetRepository.POLY_HAVEN,
        asset_name="wood_02",
        repository_specific_params={"type": "textures"},
        import_options={"format": "png"},
    )

    print(f"✅ Result: {result['status']}")
    if result["status"] == "SUCCESS":
        print("📦 Downloaded texture: wood_02")
    else:
        print(f"❌ Error: {result['error']}")


async def list_repository_assets():
    """List available assets from repositories."""
    print("\n📋 Listing available Kenney assets...")

    result = await list_available_assets(AssetRepository.KENNEY)
    if result["status"] == "SUCCESS":
        print(f"🏪 Repository: {result['repository']}")
        print(f"📝 Description: {result['description']}")
        print(f"🌐 Website: {result['website']}")
        print("📦 Sample assets:")
        for asset in result.get("sample_assets", []):
            print(f"  • {asset}")
    else:
        print(f"❌ Error: {result['error']}")


async def search_for_assets():
    """Search for assets across repositories."""
    print("\n🔍 Searching for 'fantasy' assets...")

    result = await search_assets(query="fantasy", limit=5)

    if result["status"] == "SUCCESS":
        print(f"📊 Found {result['total_results']} results")
        for asset in result["results"]:
            print(f"  • {asset['asset_name']} ({asset['repository']})")
    else:
        print(f"❌ Error: {result['error']}")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("Blender MCP - Asset Repositories Example")
    print("=" * 60)
    print()
    print("This example demonstrates downloading assets from free repositories.")
    print("Note: Some downloads may fail if assets are moved or renamed.")
    print()

    # List available assets
    await list_repository_assets()

    # Search for assets
    await search_for_assets()

    # Download examples (uncomment to test)
    print("\n💡 Uncomment the following lines to test downloads:")
    print("# await example_kenney_assets()")
    print("# await example_quaternius_assets()")
    print("# await example_polyhaven_hdri()")
    print("# await example_polyhaven_texture()")
    print()
    print("⚠️  Note: OpenGameArt requires specific download URLs")
    print("   Visit https://opengameart.org/ and copy download links")

    print("\n🎉 Asset repository integration is ready!")
    print("   Use the tools to download and import free assets into your scenes.")


if __name__ == "__main__":
    asyncio.run(main())
