
import sys
sys.path.insert(0, 'D:/Dev/repos/blender-mcp/src')

try:
    import blender_mcp
    print("✅ blender_mcp module imported successfully")
    
    try:
        from blender_mcp.app import app
        print("✅ app imported successfully")
        
        try:
            from blender_mcp.server import main
            print("✅ server main imported successfully")
            
            print("✅ All imports successful - should work")
        except Exception as e:
            print(f"❌ Server import failed: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"❌ App import failed: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Module import failed: {e}")
    import traceback
    traceback.print_exc()
