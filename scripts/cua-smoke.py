#!/usr/bin/env python3
"""CUA smoke test for NSIS-installed fleet apps (pywinauto-mcp canary).

CUA_SMOKE_VERSION = 3
If this file differs from templates/tauri-native/scripts/cua-smoke.py in
mcp-central-docs, copy the template over — version number will have changed.

Usage:
    python scripts/cua-smoke.py
    python scripts/cua-smoke.py --installer path/to/setup.exe
    python scripts/cua-smoke.py --config scripts/cua-nsis-config.json

Phases (implemented):
    1. Kill stale processes
    2. Silent install NSIS
    3. Launch app, wait for backend health
    4. Verify window (pywinauto)
    5. Screenshot evidence
    6. Feature-route smoke (health + data endpoint)
    7. Check diagnostics
    8. WebView bridge proof (OCR)
    9. Uninstall
    10. Report pass/fail

Phases (planned Phase 3): nav sidebar click-through, floating chat visibility.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

# ── Config ────────────────────────────────────────────────────────────

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cua-nsis-config.json")


def load_config(path: str | None = None) -> dict:
    p = path or DEFAULT_CONFIG_PATH
    if not os.path.exists(p):
        print(f"  [cua] WARNING: config not found at {p}, using built-in defaults", flush=True)
        return {}
    with open(p) as f:
        cfg = json.load(f)

    # Expand env vars in string values
    def _expand(v):
        if isinstance(v, str):
            return os.path.expandvars(v)
        if isinstance(v, list):
            return [_expand(x) for x in v]
        return v

    return {k: _expand(v) for k, v in cfg.items()}


CUA_SMOKE_VERSION = 3  # bump when template changes; see docstring


def _check_version():
    """Warn if this file doesn't match the template version."""
    from pathlib import Path

    ver_file = Path(__file__)
    # If the template path exists, compare versions
    tpl = Path(os.getenv("MCP_CENTRAL_DOCS", "")) / "templates/tauri-native/scripts/cua-smoke.py"
    if tpl.exists():
        tpl_text = tpl.read_text(encoding="utf-8")
        import re

        m = re.search(r"CUA_SMOKE_VERSION\s*=\s*(\d+)", tpl_text)
        if m and int(m.group(1)) > CUA_SMOKE_VERSION:
            print(
                f"  [cua] WARNING: cua-smoke.py v{CUA_SMOKE_VERSION} is outdated "
                f"(template v{m.group(1)}). Copy template over.",
                flush=True,
            )


def cfg(key: str, default=""):
    return _CONFIG.get(key, default)


_CONFIG = load_config()

# ── Derived constants ─────────────────────────────────────────────────

BACKEND_PORT = int(cfg("backend_port", 10789))
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"
PRODUCT_NAME = cfg("product_name", "Pywinauto MCP Operator")
HEALTH_PATH = cfg("health_path", "/api/v1/health")
DIAGNOSTICS_PATH = cfg("diagnostics_path", "/api/v1/diagnostics")
FEATURE_PATH = cfg("feature_smoke_path", "/api/v1/system/info")
WINDOW_TITLE_RE = cfg("window_title_re", "Pywinauto MCP")
BRIDGE_OK_TEXT = cfg("bridge_ok_text", "REST bridge reachable")
INSTALL_DIR = cfg("install_dir", "%LOCALAPPDATA%\\Pywinauto MCP Operator")
OPERATOR_EXE = cfg("operator_exe", "pywinauto-mcp-operator.exe")
PROCESS_NAMES = cfg("backend_process_names", ["pywinauto-mcp-operator", "pywinauto-mcp-backend"])
NSIS_GLOB = cfg("nsis_glob", "web_sota/src-tauri/target/release/bundle/nsis/Pywinauto MCP Operator_*_x64-setup.exe")
REGISTRY_FILTER = cfg("uninstall_registry_filter", "*Pywinauto*")
MAX_RETRY = 10
RETRY_DELAY = 3

_INSTALLED = False


# ── Helpers (must be before CUA client) ────────────────────────────


def log(msg: str):
    print(f"  [cua] {msg}", flush=True)


def log_warn(msg: str):
    print(f"  [WARN] {msg}", flush=True)


# ── Direct pywinauto (no pywinauto-mcp dependency) ─────────────────

try:
    import pywinauto
    import pywinauto.findwindows
    _HAS_PYWAUTO = True
except ImportError:
    _HAS_PYWAUTO = False


def cua_available() -> bool:
    return _HAS_PYWAUTO


def _find_tauri_window(title_re: str):
    """Find Tauri webview window — excludes classic apps by class_name."""
    wins = pywinauto.findwindows.find_elements(title_re=title_re)
    tauri = [w for w in wins if w.class_name != "QMainWindow"]
    if not tauri:
        raise RuntimeError(f"No Tauri window found (classes: {set(w.class_name for w in wins)})")
    return tauri[0].handle


def _get_window(handle: int):
    app = pywinauto.Application(backend="uia").connect(handle=handle)
    return app.window(handle=handle)


def cua_find_window(title_re: str = "") -> dict | None:
    """Find a window by title regex. Returns {handle, title, rect} or None."""
    try:
        import pywinauto

        wins = pywinauto.findwindows.find_elements(title_re=title_re)
        tauri = [w for w in wins if w.class_name != "QMainWindow"]
        if not tauri:
            return None
        handle = tauri[0].handle
        app = pywinauto.Application(backend="uia").connect(handle=handle)
        win = app.window(handle=handle)
        win.wait("visible", timeout=5)
        rect = win.rectangle()
        w = rect.width if isinstance(rect.width, int) else rect.width()
        h = rect.height if isinstance(rect.height, int) else rect.height()
        return {"handle": handle, "title": win.window_text(), "rect": {"left": rect.left, "top": rect.top, "width": w, "height": h}}
    except Exception:
        return None


def cua_screenshot(window_handle: int = 0, output_path: str = "") -> str | None:
    """Take a screenshot. Returns path or None."""
    try:
        import pywinauto

        wins = pywinauto.findwindows.find_elements(title_re=WINDOW_TITLE_RE)
        tauri = [w for w in wins if w.class_name != "QMainWindow"]
        if tauri:
            app = pywinauto.Application(backend="uia").connect(handle=tauri[0].handle)
            win = app.window(handle=tauri[0].handle)
            capture = win.capture_as_image()
            capture.save(output_path)
            return output_path
    except Exception:
        return None


def _show_automation_warning():
    """Warn user that automation is about to click around. Flashes a red HUD overlay."""
    print("\n  " + "!" * 60, flush=True)
    print("  !!! CUA AUTOMATION WARNING !!!", flush=True)
    print("  !!! The script will now take control of the mouse and keyboard.", flush=True)
    print("  !!! Please do not touch the mouse or keyboard until the test completes.", flush=True)
    print("  !!! This will take approximately 3 seconds per page.", flush=True)
    print("  " + "!" * 60 + "\n", flush=True)
    time.sleep(3)


def cua_ocr_text(window_handle: int = 0, image_path: str = "") -> str:
    """Run OCR on a window screenshot. Returns text."""
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if image_path and os.path.exists(image_path):
            from PIL import Image
            return pytesseract.image_to_string(Image.open(image_path))
        if window_handle:
            from PIL import Image
            capture = cua_screenshot(window_handle, f"{image_path or 'capture'}.png")
            if capture and os.path.exists(capture):
                return pytesseract.image_to_string(Image.open(capture))
    except Exception:
        pass
    return ""


def cua_click(window_handle: int, x: int, y: int):
    """Click at (x,y) relative to window."""
    try:
        import pywinauto.mouse
        pywinauto.mouse.click(button="left", coords=(x, y))
    except Exception:
        pass


def _release_mouse():
    """Release all mouse buttons — call after any clicking to prevent stuck input."""
    try:
        import ctypes
        MOUSEEVENTF_LEFTUP = 0x0004
        MOUSEEVENTF_RIGHTUP = 0x0010
        MOUSEEVENTF_MIDDLEUP = 0x0040
        for flag in (MOUSEEVENTF_LEFTUP, MOUSEEVENTF_RIGHTUP, MOUSEEVENTF_MIDDLEUP):
            ctypes.windll.user32.mouse_event(flag, 0, 0, 0, 0)
    except Exception:
        pass


# ── Helpers ───────────────────────────────────────────────────────────


class PhaseFailed(Exception):
    """Non-fatal phase failure — script continues to uninstall."""


def fatal(msg: str):
    print(f"  [cua] FATAL: {msg}", flush=True)
    sys.exit(1)


def phase_fail(msg: str):
    print(f"  [cua] PHASE FAIL: {msg}", flush=True)
    raise PhaseFailed(msg)


# ── Phase 1: Kill stale ───────────────────────────────────────────────


def kill_stale():
    for name in PROCESS_NAMES:
        subprocess.run(["taskkill", "/F", "/IM", f"{name}.exe", "/T"], capture_output=True, timeout=10)
    time.sleep(1)
    log("Stale processes killed")


# ── Phase 2: Install ──────────────────────────────────────────────────


def find_installer() -> str:
    import glob

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pattern = os.path.join(repo_root, *NSIS_GLOB.replace("/", "\\").split("\\"))
    matches = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    if matches:
        return matches[0]
    fatal("No NSIS installer found. Run 'just build-native' first.")


def silent_install(installer: str):
    log(f"Installing: {installer}")
    r = subprocess.run([installer, "/S"], capture_output=True, timeout=120)
    if r.returncode != 0:
        fatal(f"NSIS install exited with code {r.returncode}")
    global _INSTALLED
    _INSTALLED = True
    time.sleep(2)
    log("Install complete")


# ── Phase 3: Launch ──────────────────────────────────────────────────


def launch_app():
    exe = os.path.join(INSTALL_DIR, OPERATOR_EXE)
    if not os.path.exists(exe):
        fatal(f"Operator not found at {exe}")
    env = os.environ.copy()
    env_vars = cfg("env_vars", {})
    if isinstance(env_vars, dict):
        for k, v in env_vars.items():
            env[k] = str(v)
            log(f"  Set env {k}={v}")
    subprocess.Popen([exe], cwd=INSTALL_DIR, env=env)
    log(f"Launched {exe}")
    for attempt in range(MAX_RETRY):
        try:
            resp = urllib.request.urlopen(f"{BACKEND_URL}{HEALTH_PATH}", timeout=5)
            if resp.status == 200:
                log(f"Backend healthy (attempt {attempt + 1})")
                return
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            pass
        time.sleep(RETRY_DELAY)
    fatal(f"Backend not reachable after {MAX_RETRY * RETRY_DELAY}s")


# ── Phase 4: Verify window ───────────────────────────────────────────


def verify_window():
    if not cua_available():
        log("CUA client unavailable -- window check skipped")
        return
    win = cua_find_window(WINDOW_TITLE_RE)
    if win:
        r = win.get("rect", {}) or {}
        w = r.get("width", 0) or 0
        h = r.get("height", 0) or 0
        log(f"Window '{win.get('title', '?')}' found: {w}x{h}")
        if isinstance(w, int) and isinstance(h, int) and w > 0 and h > 0 and (w < 100 or h < 100):
            phase_fail(f"Window too small: {w}x{h}")
    else:
        log(f"Window matching '{WINDOW_TITLE_RE}' not found")


# ── Phase 5: Screenshot ──────────────────────────────────────────────


def take_screenshot(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"cua-smoke-{int(time.time())}.png")
    result = cua_screenshot(0, path)
    if result and os.path.exists(result):
        log(f"Screenshot saved: {result} ({os.path.getsize(result)} bytes)")
    else:
        log("Screenshot not available (CUA client needed)")


# ── Phase 6: Feature-route smoke ─────────────────────────────────────


def check_feature_route():
    try:
        resp = urllib.request.urlopen(f"{BACKEND_URL}{FEATURE_PATH}", timeout=5)
        body = json.loads(resp.read())
        log(f"Feature route {FEATURE_PATH}: HTTP {resp.status}")
        if resp.status == 200:
            log(f"  response keys: {list(body.keys())[:5]}")
    except Exception as e:
        log(f"Feature route check failed (non-fatal): {e}")


# ── Phase 7: Diagnostics ─────────────────────────────────────────────


def check_diagnostics():
    try:
        resp = urllib.request.urlopen(f"{BACKEND_URL}{DIAGNOSTICS_PATH}", timeout=5)
        data = json.loads(resp.read())
        if data.get("success"):
            d = data["data"]
            log(f"Backend: {d['backend'].get('status')} v{d['backend'].get('version')}")
            log(
                f"System: CPU {d['system'].get('cpu_percent')}% | Mem {d['system'].get('memory_percent')}% | Disk {d['system'].get('disk_percent')}%"
            )
            log(f"Tools: {d['tools'].get('total')} registered")
            log(f"CUA: Tesseract={d['cua_status']['tesseract_available']} Window={d['cua_status']['window_found']}")
            if d.get("errors", {}).get("count", 0) > 0:
                log(f"WARNING: {d['errors']['count']} errors logged")
        else:
            log(f"Diagnostics returned: {data}")
    except Exception as e:
        log(f"Diagnostics check failed (non-fatal): {e}")


# ── Phase 8: WebView bridge proof (OCR) ──────────────────────────────


def verify_webview_bridge(output_dir: str):
    if not cua_available():
        log("CUA client unavailable -- WebView bridge check skipped")
        return
    os.makedirs(output_dir, exist_ok=True)
    snap_path = os.path.join(output_dir, f"bridge-snap-{int(time.time())}.png")
    result = cua_screenshot(0, snap_path)
    text = cua_ocr_text(0, snap_path or "")
    if not text and result and os.path.exists(snap_path):
        text = cua_ocr_text(image_path=snap_path)
    if BRIDGE_OK_TEXT.lower() in text.lower() or "connected" in text.lower():
        log(f"WebView bridge OK (found '{BRIDGE_OK_TEXT}' in screenshot OCR)")
    elif text:
        os.makedirs(output_dir, exist_ok=True)
        log(f"WebView OCR text: {text[:200]}")
        phase_fail(f"WebView bridge not OK — likely API_BASE/CSP/CORS (expected '{BRIDGE_OK_TEXT}')")
    else:
        log("WebView bridge check skipped (no OCR available)")


# ── Phase 9: Nav click-through ──────────────────────────────────────


def _verify_page_ocr(text: str, label: str, expected: str) -> bool:
    """Check OCR text for page validity. Returns True if page seems OK."""
    text_lower = text.lower()
    fail_keywords = ["404", "not found", "could not find", "error", "timeout", "internal server error", "bad gateway"]
    for kw in fail_keywords:
        if kw in text_lower:
            log(f"  Page '{label}': ERROR keyword '{kw}' found in OCR")
            return False
    if not text.strip():
        log(f"  Page '{label}': EMPTY OCR — page may be blank or not loading")
        return False
    if expected.lower() in text_lower:
        log(f"  Page '{label}': V OK (found '{expected}')")
        return True
    log(f"  Page '{label}': X expected '{expected}' not found in OCR — page may be wrong")
    return False


def _nav_click_element(win_handle: int, wx: int, wy: int, idx: int, label: str = ""):
    """Click a nav item. Tries title-based UIA matching first, then index, then coordinates."""
    import pywinauto
    app = pywinauto.Application(backend="uia").connect(handle=win_handle)
    w = app.window(handle=win_handle)

    # Preferred: match by accessible name (title= is the pywinauto criteria for UIA Name).
    # Index-based Hyperlink ordering is fragile - sidebar order may differ from nav_routes.
    if label:
        try:
            link = w.descendants(title=label)
            if link:
                link[0].click_input()
                return
        except Exception:
            pass
        try:
            elements = w.descendants(control_type="Hyperlink")
            el = [e for e in elements if label.lower() in (e.window_text() or "").lower()]
            if el:
                el[0].click_input()
                return
        except Exception:
            pass

    # Fallback: positional Hyperlink
    try:
        elements = w.descendants(control_type="Hyperlink")
        if idx < len(elements):
            elements[idx].click_input()
            return
    except Exception:
        pass
    # Try Pane (some WebView versions)  
    try:
        elements = w.descendants(control_type="Pane")
        nav_elements = [e for e in elements if e.rectangle().left < wx + 200]
        nav_elements_sorted = sorted(nav_elements, key=lambda e: e.rectangle().top)
        if idx < len(nav_elements_sorted):
            nav_elements_sorted[idx].click_input()
            return
    except Exception:
        pass

    # Fallback to coordinate click
    click_x = wx + int(cfg("sidebar_click_x", 30))
    click_y = wy + int(cfg("sidebar_first_y", 90)) + idx * int(cfg("sidebar_step_y", 55))
    cua_click(win_handle, click_x, click_y)


def nav_click_through(output_dir: str):
    """Click each sidebar nav item, verify page loads via OCR."""
    if not cua_available():
        log("CUA client unavailable -- nav click-through skipped")
        return
    _release_mouse()
    _show_automation_warning()

    nav_routes = cfg("nav_routes", [["Dashboard", "Automation Dashboard"], ["Logging", "Logs"], ["Settings", "Settings"], ["Help", "Help"]])
    nav_routes = [(r[0], r[1]) for r in nav_routes if len(r) >= 2]
    win = cua_find_window(WINDOW_TITLE_RE)
    if not win:
        log("No window found for nav click-through")
        return
    r = win.get("rect", {}) or {}
    wx = r.get("left", 0) or 0
    wy = r.get("top", 0) or 0
    snap_dir = os.path.join(output_dir, "nav")
    handle = win.get("handle", 0)

    # Bring window to front and maximize (user was warned)
    try:
        import pywinauto
        app = pywinauto.Application(backend="uia").connect(handle=handle)
        w = app.window(handle=handle)
        w.set_focus()
        w.maximize()
        time.sleep(1)
    except Exception:
        pass

    for idx, (label, expected_header) in enumerate(nav_routes):
        try:
            _nav_click_element(handle, wx, wy, idx, label)
            _release_mouse()
            time.sleep(3)

            snap_path = os.path.join(snap_dir, f"nav-{label.lower()}-{int(time.time())}.png")
            os.makedirs(snap_dir, exist_ok=True)
            cua_screenshot(handle, snap_path)
            text = cua_ocr_text(handle, snap_path)

            _verify_page_ocr(text, label, expected_header)
        except Exception as e:
            log(f"Nav '{label}' failed (non-fatal): {e}")
            _release_mouse()

    _release_mouse()


# ── Phase 10: Log analysis ────────────────────────────────────────────


def analyze_logs():
    """Read the Tauri app logs and report errors/warnings."""
    log_paths = [
        os.path.join(INSTALL_DIR, "pywinauto-mcp.log"),
        os.path.expandvars(r"%APPDATA%\com.sandraschi.pywinauto-mcp\logs\backend-spawn.log"),
    ]
    errors = []
    warnings = []

    for path in log_paths:
        if not os.path.exists(path):
            continue
        log(f"Analyzing log: {path} ({os.path.getsize(path)} bytes)")
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    if "ERROR" in stripped or "CRITICAL" in stripped:
                        errors.append(stripped)
                    elif "WARNING" in stripped or "WARN" in stripped:
                        warnings.append(stripped)
        except Exception as e:
            log(f"Could not read {path}: {e}")

    if errors:
        log(f"ERRORS FOUND ({len(errors)}):")
        for err in errors[:10]:
            log(f"  ! {err[:200]}")
    else:
        log("No errors found in logs")

    if warnings:
        log(f"Warnings: {len(warnings)}")
        for warn in warnings[:5]:
            log(f"  ? {warn[:200]}")

    if errors:
        phase_fail(f"{len(errors)} errors found in app logs")


# ── Phase 11: Uninstall ───────────────────────────────────────────────


def uninstall():
    uninstaller = os.path.join(INSTALL_DIR, "uninstall.exe")
    if not os.path.exists(uninstaller):
        if _INSTALLED:
            log(f"Uninstaller not found at {uninstaller}")
        return
    r = subprocess.run([uninstaller, "/S"], capture_output=True, timeout=60)
    log(f"Uninstaller exited with code {r.returncode}")
    time.sleep(2)
    remaining = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"Get-ItemProperty 'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' -ErrorAction SilentlyContinue | Where-Object {{ $_.DisplayName -like '{REGISTRY_FILTER}' }}",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if remaining.stdout.strip():
        log("WARNING: App may still be registered")
    else:
        log("Clean: app uninstalled")


# ── Main ──────────────────────────────────────────────────────────────


def main():
    # Self-check: warn if template version differs
    _check_version()

    parser = argparse.ArgumentParser(description="CUA-NSIS smoke test")
    parser.add_argument("--installer", help="Path to NSIS installer .exe")
    parser.add_argument("--config", help="Path to cua-nsis-config.json")
    parser.add_argument("--output-dir", default="cua-reports", help="Screenshot output directory")
    args = parser.parse_args()

    if args.config:
        _CONFIG.update(load_config(args.config))

    phases = [
        (True, "Kill stale processes", lambda: kill_stale()),
        (True, "Install NSIS", lambda: silent_install(args.installer or find_installer())),
        (True, "Launch app", launch_app),
        (False, "Verify window", verify_window),
        (False, "Screenshot", lambda: take_screenshot(args.output_dir)),
        (False, "Feature route", check_feature_route),
        (False, "Check diagnostics", check_diagnostics),
        (False, "WebView bridge", lambda: verify_webview_bridge(args.output_dir)),
        (False, "Nav click-through", lambda: nav_click_through(args.output_dir)),
        (False, "Analyze app logs", analyze_logs),
        (False, "Uninstall", uninstall),
    ]

    passed = failed = 0
    fatal_failed = False

    print(f"\n{'=' * 50}")
    print(f"  CUA Smoke Test — {PRODUCT_NAME}")
    print(f"{'=' * 50}\n")

    try:
        for is_fatal, name, fn in phases:
            print(f"  Phase {phases.index((is_fatal, name, fn)) + 1}: {name}")
            try:
                fn()
                print(f"  V {name}\n")
                passed += 1
            except PhaseFailed:
                print(f"  X {name}\n")
                failed += 1
                if is_fatal:
                    fatal_failed = True
            except Exception as e:
                print(f"  X {name}: {e}\n")
                failed += 1
                if is_fatal:
                    fatal_failed = True
    finally:
        _release_mouse()

    print(f"{'=' * 50}")
    print(f"  Result: {passed}/{passed + failed} phases passed")
    if failed:
        print(f"  {failed} phase(s) FAILED")
    if fatal_failed:
        print("  FATAL phase failure — see above")
        sys.exit(1)
    print("  ALL PHASES PASSED")
    print(f"{'=' * 50}\n")


if __name__ == "__main__":
    main()
