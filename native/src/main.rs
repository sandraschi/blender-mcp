#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod backend;
use backend::{spawn_backend, BackendProcess};
use std::io::Write;
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
            let name = match &event {
                tauri::RunEvent::Exit => "Exit".to_string(),
                tauri::RunEvent::ExitRequested { .. } => "ExitRequested".to_string(),
                tauri::RunEvent::WindowEvent { label, event: we, .. } => {
                    let kind = if matches!(we, tauri::WindowEvent::CloseRequested { .. }) { "CloseRequested" } else if matches!(we, tauri::WindowEvent::Destroyed) { "Destroyed" } else if matches!(we, tauri::WindowEvent::Focused(_)) { "Focused" } else if matches!(we, tauri::WindowEvent::Resized(_)) { "Resized" } else { "OtherWinEvent" };
                    format!("WindowEvent[{label}]={kind}")
                }
                tauri::RunEvent::Ready => "Ready".to_string(),
                tauri::RunEvent::Resumed => "Resumed".to_string(),
                tauri::RunEvent::MainEventsCleared => "MainEventsCleared".to_string(),
                _ => "Other".to_string(),
            };
            let _ = std::fs::OpenOptions::new().create(true).append(true).open("C:\\Temp\\blender-events.log").and_then(|mut f| writeln!(f, "event: {name}"));
            if let tauri::RunEvent::Exit = event {
                let _ = std::fs::OpenOptions::new().create(true).append(true).open("C:\\Temp\\blender-events.log").and_then(|mut f| writeln!(f, "EXIT EVENT fired"));
                if let Some(mut child) = app.state::<BackendProcess>().0.lock().unwrap().take() {
                    let _ = child.kill();
                    let _ = child.wait();
                }
            }
        });
}
