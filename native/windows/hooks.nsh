; Kill UI + backend before install/uninstall (backend locks resources/*.exe).
!macro KillBlenderFleetProcesses
  DetailPrint "Stopping Blender MCP processes..."
  ExecWait 'taskkill /F /IM blender-mcp-backend.exe /T' $0
  ExecWait 'taskkill /F /IM blender_mcp_native.exe /T' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "blender-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "blender_mcp_native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "blender-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "blender_mcp_native.exe"
    Pop $0
  !endif
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillBlenderFleetProcesses
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillBlenderFleetProcesses
!macroend
