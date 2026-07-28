# Per-repo fleet start config for blender-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'blender-mcp'
    BackendPort  = 10849
    FrontendPort = 10848
    HealthPath   = '/api/v1/health'
    WebRoot      = 'D:\Dev\repos\blender-mcp\webapp'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'blender_mcp.server:asgi_app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10849' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
