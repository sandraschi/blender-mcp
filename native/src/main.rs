#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::Mutex;
use tauri::{Emitter, Manager};
use tauri_plugin_shell::ShellExt;

struct BackendProcess(Mutex<Option<tauri_plugin_shell::process::CommandChild>>);

#[tauri::command]
async fn start_backend(app: tauri::AppHandle, state: tauri::State<'_, BackendProcess>) -> Result<String, String> {
    let cmd = app.shell()
        .sidecar("blender-mcp-backend")
        .map_err(|e| format!("Sidecar error: {}", e))?
        .args(["--http", "--port", "10849"]);

    let (_, child) = cmd.spawn().map_err(|e| format!("Failed: {}", e))?;
    *state.0.lock().unwrap() = Some(child);
    Ok("Backend starting".into())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_process::init())
        .manage(BackendProcess(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![start_backend])
        .setup(|app| {
            let handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                match start_backend(handle.clone(), handle.state::<BackendProcess>()).await {
                    Ok(_) => {}
                    Err(e) => {
                        eprintln!("Backend error: {}", e);
                        let _ = handle.emit("backend-status", format!("error: {}", e));
                    }
                }
            });
            #[cfg(debug_assertions)]
            if let Some(window) = app.get_webview_window("main") {
                window.open_devtools();
            }
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error building tauri application")
        .run(|app, event| {
            if let tauri::RunEvent::Exit = event {
                if let Some(child) = app.state::<BackendProcess>().0.lock().unwrap().take() {
                    let _ = child.kill();
                }
            }
        });
}
