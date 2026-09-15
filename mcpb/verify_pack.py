"""Required checks before `mcpb pack`, per MCPB_PACKAGING_STANDARDS.md section 2.5.

Stdlib only -- must run before any packaged dependency is guaranteed installed.

Usage:
    uv run python mcpb/verify_pack.py import <mcpb_src_dir> <entry_module>
    uv run python mcpb/verify_pack.py ast <entry_point_file>
    uv run python mcpb/verify_pack.py pollution <mcpb_dir>

Exits 0 and prints "OK ..." on pass; exits 1 and prints "FAIL ..." on failure.
"""

from __future__ import annotations

import ast
import builtins
import importlib
import sys
from pathlib import Path


def check_import(stage_dir: str, entry_module: str) -> None:
    """Resolve entry_module with stage_dir inserted at the front of sys.path;
    assert it actually loaded from there and not from some other installed
    copy (site-packages, an editable install, a stale twin)."""
    stage = Path(stage_dir).resolve()
    sys.path.insert(0, str(stage))
    mod = importlib.import_module(entry_module)
    origin = Path(mod.__file__).resolve()
    if stage not in origin.parents:
        raise SystemExit(f"FAIL import: {entry_module} resolved to {origin}, not under {stage}")
    print(f"OK import: {entry_module} -> {origin}")


def _target_names(node: ast.AST) -> set[str]:
    """Names bound by an assignment-like target (Name / Tuple / List / Starred)."""
    names: set[str] = set()
    if isinstance(node, ast.Name):
        names.add(node.id)
    elif isinstance(node, (ast.Tuple, ast.List)):
        for elt in node.elts:
            names |= _target_names(elt)
    elif isinstance(node, ast.Starred):
        names |= _target_names(node.value)
    return names


def check_ast(entry_file: str) -> None:
    """Flag `name.attr(...)` call sites where `name` is never bound anywhere in
    the module -- catches the "uvicorn.run() with no import uvicorn" class of
    bug. Deliberately conservative: only single-level attribute calls on a bare
    Name are checked; chained/nested expressions are skipped rather than risk
    a false positive.
    """
    src = Path(entry_file).read_text(encoding="utf-8")
    tree = ast.parse(src, filename=entry_file)

    bound: set[str] = set(dir(builtins)) | {"self", "cls", "__class__"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                bound.add(alias.asname or alias.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
        elif isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                bound |= _target_names(t)
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
            bound |= _target_names(node.target)
        elif isinstance(node, ast.NamedExpr):
            bound |= _target_names(node.target)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            bound |= _target_names(node.target)
        elif isinstance(node, ast.comprehension):
            bound |= _target_names(node.target)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars is not None:
                    bound |= _target_names(item.optional_vars)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            bound.update(node.names)

    missing: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            base = node.func.value
            if isinstance(base, ast.Name) and base.id not in bound:
                missing.append(f"{base.id}.{node.func.attr}() at line {node.lineno}")

    if missing:
        raise SystemExit("FAIL ast: unbound name(s) at call sites:\n  " + "\n  ".join(missing))
    print(f"OK ast: {entry_file} -- no unbound call-site names")


def check_pollution(mcpb_dir: str) -> None:
    root = Path(mcpb_dir)
    bad: list[Path] = []
    for pattern in ("__pycache__", "*.pyc", "*.bak", "*.bak.*", "*.bak-*", "*.orig", "*.rej"):
        bad.extend(root.rglob(pattern))
    if bad:
        listing = "\n  ".join(str(p) for p in bad[:20])
        raise SystemExit(f"FAIL pollution: {len(bad)} disallowed path(s) under {mcpb_dir}:\n  {listing}")
    print(f"OK pollution: {mcpb_dir} is clean")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    checks = {"import": check_import, "ast": check_ast, "pollution": check_pollution}
    fn = checks.get(cmd)
    if fn is None:
        raise SystemExit(f"unknown check {cmd!r}; expected one of {sorted(checks)}")
    fn(*args)


if __name__ == "__main__":
    main()
