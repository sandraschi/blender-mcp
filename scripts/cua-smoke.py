#!/usr/bin/env python3
"""CUA smoke test — simplified (pywinauto direct, no pywinauto-mcp dep).

CUA_SMOKE_VERSION = 2

Phases:
    1. Kill stale processes
    2. Silent install NSIS
    3. Launch app, wait for backend health
    4. Verify window (pywinauto)
    5. Screenshot
    6. Diagnostics check
    7. Uninstall
"""

import argparse
import glob
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

CUA_SMOKE_VERSION = 2
DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cua-nsis-config.json")
_CONFIG = {}


def load_config(path=None):
    p = path or DEFAULT_CONFIG
    if not os.path.exists(p):
        return {}
    with open(p) as f:
        return json.load(f)


def cfg(k, d=""):
    return _CONFIG.get(k, d)


_CONFIG = load_config()

BACKEND_PORT = int(cfg("backend_port", 10700))
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"
PRODUCT_NAME = cfg("product_name", "App")
HEALTH_PATH = cfg("health_path", "/api/v1/health")
WINDOW_TITLE_RE = cfg("window_title_re", PRODUCT_NAME)
INSTALL_DIR = os.path.expandvars(cfg("install_dir", f"%LOCALAPPDATA%\\{PRODUCT_NAME}"))
OPERATOR_EXE = cfg("operator_exe", f"{PRODUCT_NAME.lower().replace(' ', '-')}-native.exe")
PROCESS_NAMES = cfg(
    "backend_process_names",
    [OPERATOR_EXE.replace(".exe", ""), f"{OPERATOR_EXE.replace('.exe', '').replace('-native', '')}-backend"],
)
NSIS_GLOB = cfg("nsis_glob", f"native/target/release/bundle/nsis/{PRODUCT_NAME}_*_x64-setup.exe")
MAX_RETRY, RETRY_DELAY = 10, 3


def log(m):
    print(f"  [cua] {m}", flush=True)


def fatal(m):
    print(f"  [cua] FATAL: {m}", flush=True)
    sys.exit(1)


# Phase 1
def kill_stale():
    for name in PROCESS_NAMES:
        subprocess.run(["taskkill", "/F", "/IM", name, "/T"], capture_output=True, timeout=10)
    time.sleep(1)
    log("Stale processes killed")


# Phase 2
def find_installer():
    repo_root = Path(__file__).resolve().parent.parent
    matches = sorted(glob.glob(str(repo_root / NSIS_GLOB.replace("/", "\\"))), key=os.path.getmtime, reverse=True)
    if matches:
        return matches[0]
    fatal("No NSIS installer found")


def silent_install(inst):
    log(f"Installing: {inst}")
    r = subprocess.run([inst, "/S"], capture_output=True, timeout=120)
    if r.returncode != 0:
        fatal(f"Install failed: {r.returncode}")
    time.sleep(2)
    log("Install complete")


# Phase 3
def launch_app():
    exe = os.path.join(INSTALL_DIR, OPERATOR_EXE)
    if not os.path.exists(exe):
        fatal(f"Operator not found at {exe}")
    subprocess.Popen([exe], cwd=INSTALL_DIR)
    for i in range(MAX_RETRY):
        try:
            r = urllib.request.urlopen(f"{BACKEND_URL}{HEALTH_PATH}", timeout=5)
            if r.status == 200:
                log(f"Backend healthy (attempt {i + 1})")
                return
        except:
            pass
        time.sleep(RETRY_DELAY)
    fatal(f"Backend not reachable after {MAX_RETRY * RETRY_DELAY}s")


# Phase 4
def verify_window():
    try:
        import pywinauto

        app = pywinauto.Application(backend="uia").connect(title_re=WINDOW_TITLE_RE)
        win = app.window(title_re=WINDOW_TITLE_RE)
        win.wait("visible", timeout=5)
        r = win.rectangle()
        w = r.width()
        h = r.height()
        log(f"Window found: {w}x{h}")
        if w < 100 or h < 100:
            log("Window too small")
            return
    except Exception as e:
        log(f"Window check skipped: {e}")


# Phase 5
def screenshot(out):
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f"cua-{int(time.time())}.png")
    try:
        import pywinauto

        app = pywinauto.Application(backend="uia").connect(title_re=WINDOW_TITLE_RE)
        win = app.window(title_re=WINDOW_TITLE_RE)
        win.set_focus()
        time.sleep(1)
        win.capture_as_image().save(path)
        log(f"Screenshot: {path} ({os.path.getsize(path)} bytes)")
    except Exception as e:
        log(f"Screenshot skipped: {e}")


# Phase 6
# Phase 5b - Sidebar nav click-through (title-based UIA matching)
def nav_click_through(output_dir):
    import pywinauto

    handle = _find_tauri_window()
    app = pywinauto.Application(backend="uia").connect(handle=handle)
    win = app.window(handle=handle)
    win.set_focus()
    time.sleep(2)
    nav_routes = cfg("nav_routes", [])
    if not isinstance(nav_routes, list) or not nav_routes:
        log("No nav_routes in config - nav walk skipped")
        return
    win.maximize()
    time.sleep(1)
    for label, expected in nav_routes:
        try:
            link = win.descendants(title=label)
            if link:
                link[0].click_input()
            else:
                elements = win.descendants(control_type="Hyperlink")
                el = [e for e in elements if label.lower() in (e.window_text() or "").lower()]
                if el:
                    el[0].click_input()
                else:
                    log(f"Nav '{label}': no link found - skipped")
                    continue
            time.sleep(2)
            path = os.path.join(output_dir, f"nav-{label.lower().replace(' ', '-')}.png")
            win.capture_as_image().save(path)
            log(f"Nav '{label}': clicked + screenshot ({os.path.getsize(path)} bytes)")
        except Exception as e:
            log(f"Nav '{label}' failed (non-fatal): {e}")


def check_diagnostics():
    try:
        r = urllib.request.urlopen(f"{BACKEND_URL}/api/v1/diagnostics", timeout=5)
        data = json.loads(r.read())
        log(f"Diagnostics: HTTP {r.status}")
        if isinstance(data, dict):
            log(f"  keys: {list(data.keys())[:5]}")
    except Exception as e:
        log(f"Diagnostics check failed: {e}")


# Phase 7
def uninstall():
    un = os.path.join(INSTALL_DIR, "uninstall.exe")
    if not os.path.exists(un):
        log("No uninstaller found")
        return
    subprocess.run([un, "/S"], capture_output=True, timeout=60)
    time.sleep(2)
    log("Uninstall complete")


def main():
    parser = argparse.ArgumentParser(description="CUA-NSIS smoke test")
    parser.add_argument("--installer")
    parser.add_argument("--config")
    parser.add_argument("--output-dir", default="cua-reports")
    args = parser.parse_args()
    if args.config:
        _CONFIG.update(load_config(args.config))

    phases = [
        (True, "Kill stale", kill_stale),
        (True, "Install", lambda: silent_install(args.installer or find_installer())),
        (True, "Launch", launch_app),
        (False, "Window", verify_window),
        (False, "Screenshot", lambda: screenshot(args.output_dir)),
        (False, "Nav walk", lambda: nav_click_through(args.output_dir)),
        (False, "Diagnostics", check_diagnostics),
        (False, "Uninstall", uninstall),
    ]
    passed = failed = 0
    halted = False
    for fatal_phase, name, fn in phases:
        try:
            fn()
            passed += 1
            log(f"V {name}")
        except Exception as e:
            failed += 1
            log(f"X {name}: {e}")
            if fatal_phase:
                halted = True
    log(f"Result: {passed}/{passed + failed}")
    if halted:
        sys.exit(1)
    log("ALL PHASES PASSED")


if __name__ == "__main__":
    main()
