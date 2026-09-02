#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod backend;
use backend::{spawn_backend, BackendProcess};
use std::sync::Mutex;
use tauri::{Emitter, Manager};

#[tauri::command]
async fn start_backend(app: tauri::AppHandle, state: tauri::State<'_, BackendProcess>) -> Result<String, String> {
    spawn_backend(app, &state)
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
            // Gate G: spawn off setup thread so UI shows instantly and the async runtime/event loop
            // is never blocked by the backend cold start. backend.rs handles free_port + health poll + logs.
            let handle2 = handle.clone();
            std::thread::spawn(move || {
                let state = handle2.state::<BackendProcess>();
                match spawn_backend(handle2.clone(), &state) {
                    Ok(msg) => {
                        let _ = handle2.emit("backend-status", msg);
                    }
                    Err(e) => {
                        eprintln!("Backend error: {}", e);
                        let _ = handle2.emit("backend-status", format!("error: {}", e));
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
                // Gate G: kill + wait to release exe lock before NSIS uninstall
                if let Some(mut child) = app.state::<BackendProcess>().0.lock().unwrap().take() {
                    let _ = child.kill();
                    let _ = child.wait();
                }
            }
        });
}
