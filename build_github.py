# Build script for GitHub Actions and local development
import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        print(f"✅ {cmd}")
        return True
    except Exception as e:
        print(f"❌ Exception running {cmd}: {e}")
        return False

def build_dxt():
    """Build DXT extension using official toolchain"""
    repo_root = Path(__file__).parent
    dxt_dir = repo_root / "dxt"
    dist_dir = repo_root / "dist"
    
    # Create dist directory
    dist_dir.mkdir(exist_ok=True)
    
    # Validate manifest
    print("🔍 Validating manifest.json...")
    if not run_command("dxt validate manifest.json", cwd=dxt_dir):
        return False
    
    # Get version from manifest or environment
    version = os.environ.get('VERSION', '1.0.0')
    output_file = dist_dir / f"blender-mcp-{version}.dxt"
    
    # Build DXT package
    print(f"📦 Building DXT package: {output_file}")
    if not run_command(f"dxt pack . {output_file}", cwd=dxt_dir):
        return False
    
    # Optional signing
    signing_key = os.environ.get('DXT_SIGNING_KEY')
    if signing_key:
        print("🔐 Signing DXT package...")
        key_file = repo_root / "temp_signing.key"
        try:
            with open(key_file, 'w') as f:
                f.write(signing_key)
            if not run_command(f"dxt sign {output_file} --key {key_file}"):
                print("⚠️ Signing failed, continuing with unsigned package")
        finally:
            if key_file.exists():
                key_file.unlink()
    
    print(f"🎉 DXT package built successfully: {output_file}")
    return True

if __name__ == "__main__":
    if build_dxt():
        print("✅ Build completed successfully")
        sys.exit(0)
    else:
        print("❌ Build failed")
        sys.exit(1)
