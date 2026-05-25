"""Batch-fix remaining lint errors in blender-mcp."""
import pathlib, re

root = pathlib.Path("src")

# 1. E741 ambiguous `l` -> `_line`
for pyfile in root.rglob("*.py"):
    text = pyfile.read_text(encoding="utf-8")
    original = text
    text = text.replace("for l in ", "for _line in ")
    text = text.replace("for l.", "for _line.")
    text = text.replace("(l for ", "(_line for ")
    text = text.replace("for l,", "for _line,")
    text = text.replace("'l'", "'_line'")
    if text != original:
        pyfile.write_text(text, encoding="utf-8")
        print(f"  E741: {pyfile.name}")

# 2. E722 bare except
for pyfile in root.rglob("*.py"):
    text = pyfile.read_text(encoding="utf-8")
    original = text
    text = re.sub(r"^(\s*)except:\s*$", r"\1except Exception:", text, flags=re.MULTILINE)
    if text != original:
        pyfile.write_text(text, encoding="utf-8")
        print(f"  E722: {pyfile.name}")

# 3. RUF001 ambiguous unicode in status_icons
for pyfile in root.rglob("*.py"):
    text = pyfile.read_text(encoding="utf-8")
    if '"info": "ℹ️"' in text or "'info': 'ℹ️'" in text:
        text = text.replace('"info": "ℹ️"', '"info": "(i)"')
        text = text.replace("'info': 'ℹ️'", "'info': '(i)'")
        pyfile.write_text(text, encoding="utf-8")
        print(f"  RUF001: {pyfile.name}")

# 4. RUF002 en-dash to hyphen
for pyfile in root.rglob("*.py"):
    text = pyfile.read_text(encoding="utf-8")
    if "\u2013" in text:
        text = text.replace("\u2013", "-")
        pyfile.write_text(text, encoding="utf-8")
        print(f"  RUF002: {pyfile.name}")

# 5. RUF012 ClassVar
valfile = root / "blender_mcp/utils/validation.py"
if valfile.exists():
    text = valfile.read_text(encoding="utf-8")
    text = text.replace("            objects = {}", "            objects: ClassVar[dict] = {}")
    valfile.write_text(text, encoding="utf-8")
    print(f"  RUF012: validation.py")

# 6. B006 mutable defaults in grease_pencil_tools.py
gpfile = root / "blender_mcp/tools/grease_pencil_tools.py"
if gpfile.exists():
    text = gpfile.read_text(encoding="utf-8")
    text = text.replace("points: list = [],", "points: list | None = None,")
    text = text.replace("color: list = [0.0, 0.0, 0.0, 1.0],", "color: list | None = None,")
    text = text.replace("location: list = [0.0, 0.0, 0.0],", "location: list | None = None,")
    text = text.replace("fill_color: list = [0.0, 0.0, 0.0, 0.0],", "fill_color: list | None = None,")
    gpfile.write_text(text, encoding="utf-8")
    print(f"  B006: grease_pencil_tools.py")

# 7. E402 import logger dance in selection_tools.py, splatting_tools.py
for fname in ["selection_tools.py", "splatting_tools.py"]:
    fp = root / f"blender_mcp/tools/{fname}"
    if fp.exists():
        text = fp.read_text(encoding="utf-8")
        # Move logger= line to after imports
        text = re.sub(r"(logger = logging\.getLogger\([^)]+\)\s*\n+)(from )", r"\2\1", text)
        fp.write_text(text, encoding="utf-8")
        print(f"  E402: {fname}")

print("\nDone!")
