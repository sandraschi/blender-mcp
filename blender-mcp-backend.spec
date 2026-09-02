import sys, os
site_pkgs = os.path.abspath('.venv/Lib/site-packages')
if site_pkgs not in sys.path:
    sys.path.insert(0, site_pkgs)
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

a = Analysis(
    ['run_server.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src/blender_mcp', 'blender_mcp')],
    hiddenimports=[
        '_datetime', '_strptime',
        'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.asyncio',
        'uvicorn.protocols', 'uvicorn.protocols.http',
        'uvicorn.protocols.http.httptools_impl', 'uvicorn.protocols.http.h11_impl',
        'uvicorn.lifespan', 'uvicorn.lifespan.on',
    ] + collect_submodules('fastmcp')
    + [m for m in collect_submodules('blender_mcp') if 'validation_handler' not in m]
    + ['mcp', 'mcp.types', 'mcp.shared'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'setuptools', 'pip', 'wheel', 'test', 'tests', 'unittest',
              'blender_mcp.handlers.validation_handler'],
    noarchive=True,
    optimize=0,
)
# Strip .dist-info from all TOC lists (AV locks). Keep packages that need metadata.
_keep_dist = ['mcp-', 'opentelemetry-', 'opentelemetry_api', 'opentelemetry-api', 'email_validator-']
_saved = [e for e in a.datas if isinstance(e, tuple) and any(k in str(e[0]) for k in _keep_dist) and '.dist-info' in str(e[0])]
for _list in [a.datas, a.binaries, a.zipfiles, a.scripts]:
    _list[:] = [e for e in _list if not (isinstance(e, tuple) and '.dist-info' in str(e[0]))]
a.datas.extend(_saved)
SKIP = ['torch', 'playwright', 'bitsandbytes', 'llvmlite', 'pyarrow', 'pymupdf', 'grpc',
        'numba', 'Cython', 'google', 'azure', 'boto3', 'botocore', 'matplotlib', 'PIL',
        'pandas', 'scipy', 'sklearn', 'onnxruntime']
a.binaries = [b for b in a.binaries if not any(s in b[0].lower() for s in SKIP)]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='blender-mcp-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

