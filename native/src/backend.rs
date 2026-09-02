use std::fs::{self, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::net::{SocketAddr, TcpStream};
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::str::FromStr;
use std::sync::Mutex;
use std::thread;
use std::time::Duration;

use tauri::path::BaseDirectory;
use tauri::{AppHandle, Emitter, Manager};

pub struct BackendProcess(pub Mutex<Option<Child>>);

const BACKEND_NAME: &str = "blender-mcp-backend.exe";
const BACKEND_PORT: u16 = 10849;
const BACKEND_TAG: &str = "blender-mcp-backend-x86_64-pc-windows-msvc.exe";
const ENV_PORT: &str = "MCP_PORT";
const ENV_HOST: &str = "MCP_HOST";
const ENV_TAURI: &str = "BLENDER_TAURI";

fn dev_backend_path() -> Option<PathBuf> {
    if !cfg!(debug_assertions) { return None; }
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("binaries")
        .join(BACKEND_TAG);
    path.exists().then_some(path)
}

fn log_line(app: &AppHandle, message: &str) {
    eprintln!("[backend] {message}");
    if let Ok(dir) = app.path().app_log_dir() {
        let _ = fs::create_dir_all(&dir);
        let log_path = dir.join("backend-spawn.log");
        if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(log_path) {
            let _ = writeln!(file, "{message}");
        }
    }
}

fn resolve_bundled_backend(app: &AppHandle) -> Result<PathBuf, String> {
    let mut tried = Vec::new();
    if let Ok(path) = app.path().resolve(BACKEND_NAME, BaseDirectory::Resource) {
        tried.push(path.display().to_string());
        if path.exists() { return Ok(path); }
    }
    let resources_path = format!("resources/{BACKEND_NAME}");
    if let Ok(path) = app.path().resolve(&resources_path, BaseDirectory::Resource) {
        tried.push(path.display().to_string());
        if path.exists() { return Ok(path); }
    }
    Err(format!("bundled backend missing (tried: {})", tried.join("; ")))
}

pub fn materialize_backend(app: &AppHandle) -> Result<PathBuf, String> {
    if let Some(dev_path) = dev_backend_path() {
        log_line(app, &format!("using dev backend: {}", dev_path.display()));
        return Ok(dev_path);
    }
    let bundled = resolve_bundled_backend(app)?;
    log_line(app, &format!("using bundled backend: {}", bundled.display()));
    // Strip Windows extended-length path prefix (\\?\) which Command::spawn() rejects.
    let s = bundled.to_string_lossy().to_string();
    let clean = if let Some(rest) = s.strip_prefix(r"\\?\") { PathBuf::from(rest) } else { bundled.clone() };
    Ok(clean)
}

fn free_port(_port: u16) -> bool {
    #[cfg(windows)]
    {
        let img_kill = "Stop-Process -Name 'blender-mcp-backend' -Force -ErrorAction SilentlyContinue; Stop-Process -Name 'blender_mcp_native' -Force -ErrorAction SilentlyContinue; taskkill /F /IM blender-mcp-backend.exe /T 2>$null; taskkill /F /IM blender_mcp_native.exe /T 2>$null";
        let _ = Command::new("powershell.exe").args(["-NoProfile", "-Command", img_kill]).stdout(Stdio::null()).stderr(Stdio::null()).status();
        thread::sleep(Duration::from_millis(500));
    }
    true
}

fn stop_managed_child(state: &BackendProcess) {
    if let Some(mut child) = state.0.lock().unwrap().take() {
        let _ = child.kill();
        let _ = child.wait();
    }
}

fn watch_stream<R: std::io::Read + Send + 'static>(stream: R, app: AppHandle) {
    let reader = BufReader::new(stream);
    let mut ready = false;
    for line in reader.lines().map_while(Result::ok) {
        log_line(&app, &line);
        if !ready && (line.contains("Uvicorn running") || line.contains("Application startup complete")) {
            ready = true;
            let _ = app.emit("backend-status", "ready");
        }
    }
}

pub fn spawn_backend(app: AppHandle, state: &BackendProcess) -> Result<String, String> {
    stop_managed_child(state);
    if !free_port(BACKEND_PORT) {
        let msg = format!("Could not free port {BACKEND_PORT} after 240s -- TIME_WAIT not cleared");
        log_line(&app, &msg);
        return Err(msg);
    }

    let backend_path = materialize_backend(&app)?;
    log_line(&app, &format!("spawning {} on port {}", backend_path.display(), BACKEND_PORT));

    let mut cmd = Command::new(&backend_path);
    cmd
        .env(ENV_PORT, BACKEND_PORT.to_string())
        .env(ENV_HOST, "127.0.0.1")
        .env(ENV_TAURI, "1")
        .env("MCP_TRANSPORT", "http")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    let mut child = cmd.spawn().map_err(|e| format!("spawn failed: {e}"))?;

    let stdout = child.stdout.take();
    let stderr = child.stderr.take();
    state.0.lock().unwrap().replace(child);

    if let Some(out) = stdout {
        let handle = app.clone();
        thread::spawn(move || watch_stream(out, handle));
    }
    if let Some(err) = stderr {
        let handle = app.clone();
        thread::spawn(move || watch_stream(err, handle));
    }

    let addr = SocketAddr::from_str(&format!("127.0.0.1:{BACKEND_PORT}")).unwrap();
    let app_health = app.clone();
    thread::spawn(move || {
        for attempt in 0..30 {
            thread::sleep(Duration::from_secs(2));
            match TcpStream::connect_timeout(&addr, Duration::from_secs(2)) {
                Ok(_) => {
                    log_line(&app_health, &format!("Backend health check PASSED on port {BACKEND_PORT} (attempt {})", attempt + 1));
                    let _ = app_health.emit("backend-status", "ready");
                    return;
                }
                Err(e) => {
                    log_line(&app_health, &format!("Backend health check: {e} (attempt {})", attempt + 1));
                }
            }
        }
        log_line(&app_health, &format!("Backend health check FAILED -- not listening on port {BACKEND_PORT} after 30 attempts"));
        let _ = app_health.emit("backend-status", "error: backend not reachable");
    });

    Ok(format!("Backend starting on port {BACKEND_PORT}"))
}
