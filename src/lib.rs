use zed_extension_api as zed;

struct BlenderMcpExtension;

impl BlenderMcpExtension {
    fn new() -> Self {
        Self
    }
}

impl zed::Extension for BlenderMcpExtension {
    fn new() -> Self {
        Self::new()
    }

    fn context_server_command(
        &mut self,
        _id: &zed::ContextServerId,
        _project: &zed::Project,
    ) -> zed::Result<zed::Command> {
        Ok(zed::Command {
            command: "uv".to_string(),
            args: vec![
                "run".to_string(),
                "--project".to_string(),
                ".".to_string(),
                "--mcp".to_string(),
            ],
            env: Default::default(),
        })
    }
}

zed::register_extension!(BlenderMcpExtension);
