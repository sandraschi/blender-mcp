"""Unit tests for Poly Haven URL resolution helpers (no network)."""

from __future__ import annotations

from blender_mcp.services.polyhaven_api import (
    _pick_resolution,
    collect_bundle_entries,
    resolve_hdri_url,
    resolve_model_import_bundle,
    resolve_texture_blend_bundle,
)


def test_pick_resolution_exact() -> None:
    assert _pick_resolution("4k", ["1k", "2k", "4k"]) == "4k"


def test_pick_resolution_fallback() -> None:
    assert _pick_resolution("16k", ["1k", "2k", "4k"]) == "4k"


def test_resolve_hdri_url() -> None:
    files = {
        "hdri": {
            "4k": {
                "hdr": {"url": "https://cdn.example.com/foo.hdr"},
                "exr": {"url": "https://cdn.example.com/foo.exr"},
            }
        }
    }
    u = resolve_hdri_url(files, "4k", "hdr")
    assert u == "https://cdn.example.com/foo.hdr"
    assert resolve_hdri_url(files, "4k", "exr") == "https://cdn.example.com/foo.exr"


def test_collect_bundle_entries() -> None:
    node = {
        "url": "https://cdn.example.com/scene.gltf",
        "include": {"textures/a.png": {"url": "https://cdn.example.com/textures/a.png"}},
    }
    entries = collect_bundle_entries(node)
    assert len(entries) == 2
    assert entries[0][0].endswith("scene.gltf")


def test_resolve_texture_blend_bundle() -> None:
    files = {
        "blend": {
            "2k": {
                "blend": {
                    "url": "https://cdn.example.com/mat.blend",
                    "include": {"foo.png": {"url": "https://cdn.example.com/foo.png"}},
                }
            }
        }
    }
    entries, primary = resolve_texture_blend_bundle(files, "2k")
    assert primary == "https://cdn.example.com/mat.blend"
    assert any("mat.blend" in e[0] for e in entries)


def test_resolve_model_import_bundle_gltf() -> None:
    files = {
        "gltf": {
            "4k": {
                "gltf": {
                    "url": "https://cdn.example.com/m.gltf",
                    "include": {"m.bin": {"url": "https://cdn.example.com/m.bin"}},
                }
            }
        }
    }
    entries, primary = resolve_model_import_bundle(files, "4k", "gltf")
    assert primary == "https://cdn.example.com/m.gltf"
    assert len(entries) >= 1
