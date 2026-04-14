import {
  AlertCircle,
  Bell,
  Brain,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Cloud,
  Cpu,
  Key,
  Palette,
  RefreshCw,
  RotateCcw,
  Save,
  Server,
  Settings as SettingsIcon,
  Shield,
} from "lucide-react";
import { useEffect, useState } from "react";
import { getConfig, listLocalModels, updateConfig } from "../api/mcp";

type LLMProvider = "ollama" | "lmstudio" | "cloud";

interface ModelInfo {
  id: string;
  name: string;
  size?: string;
  loaded?: boolean;
}

interface LLMConfig {
  provider: LLMProvider;
  ollama_url: string;
  lmstudio_url: string;
  openai_api_key: string;
  openai_model: string;
  selected_model: string;
}

export default function Settings() {
  const [serverHost, setServerHost] = useState("localhost");
  const [serverPort, setServerPort] = useState(9876);
  const [theme, setTheme] = useState("dark");
  const [autoSync, setAutoSync] = useState(true);
  const [notifications, setNotifications] = useState(true);

  const [llmConfig, setLLMConfig] = useState<LLMConfig>({
    provider: "ollama",
    ollama_url: "http://localhost:11434",
    lmstudio_url: "http://localhost:1234",
    openai_api_key: "",
    openai_model: "gpt-4",
    selected_model: "",
  });

  const [availableModels, setAvailableModels] = useState<ModelInfo[]>([]);
  const [loadingModels, setLoadingModels] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [saving, setSaving] = useState(false);
  const [providerError, setProviderError] = useState<string | null>(null);
  const [expandedSection, setExpandedSection] = useState<string>("llm");

  useEffect(() => {
    loadConfig();
  }, []);

  useEffect(() => {
    fetchModels();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await getConfig();
      if (response.success && response.data) {
        const data = response.data as Record<string, unknown>;
        if (data.server_host) setServerHost(data.server_host as string);
        if (data.server_port) setServerPort(data.server_port as number);
        if (data.theme) setTheme(data.theme as string);
        if (data.auto_sync !== undefined) setAutoSync(data.auto_sync as boolean);
        if (data.notifications !== undefined) setNotifications(data.notifications as boolean);
        if (data.llm) setLLMConfig((prev) => ({ ...prev, ...(data.llm as LLMConfig) }));
      }
    } catch (err) {
      console.error("Failed to load config:", err);
    }
  };

  const fetchModels = async () => {
    setLoadingModels(true);
    setProviderError(null);
    try {
      const response = await listLocalModels();
      if (!response.success || !response.data) {
        setProviderError(response.error ?? "Failed to discover models");
        setAvailableModels([]);
        return;
      }
      const { ollama, lm_studio, errors } = response.data;
      if (errors?.length) setProviderError(errors.join("; "));
      const ollamaModels = (ollama ?? []).map((name: string) => ({
        id: name,
        name,
        loaded: false,
      }));
      const lmStudioModels = (lm_studio ?? []).map((id: string) => ({
        id,
        name: id,
        loaded: true,
      }));
      if (llmConfig.provider === "ollama") setAvailableModels(ollamaModels);
      else if (llmConfig.provider === "lmstudio") setAvailableModels(lmStudioModels);
    } catch (err) {
      setProviderError("Backend unreachable. Start the webapp backend (webapp\\start.ps1).");
      setAvailableModels([]);
    } finally {
      setLoadingModels(false);
    }
  };

  const loadOllamaModel = async (modelName: string) => {
    try {
      await fetch(`${llmConfig.ollama_url}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: modelName, prompt: "" }),
      });
      setLLMConfig((prev) => ({ ...prev, selected_model: modelName }));
      fetchModels();
      setHasChanges(true);
    } catch (err) {
      console.error("Failed to load model:", err);
    }
  };

  const updateLLMProvider = (provider: LLMProvider) => {
    setLLMConfig((prev) => ({ ...prev, provider }));
    setHasChanges(true);
  };

  const updateLLMField = (field: keyof LLMConfig, value: string) => {
    setLLMConfig((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      const fullConfig = {
        server_host: serverHost,
        server_port: serverPort,
        theme,
        auto_sync: autoSync,
        notifications,
        llm: llmConfig,
      };
      const response = await updateConfig(fullConfig);
      if (response.success) {
        setHasChanges(false);
      }
    } catch (err) {
      console.error("Failed to save settings:", err);
    } finally {
      setSaving(false);
    }
  };

  const resetSettings = () => {
    loadConfig();
    setHasChanges(false);
  };

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? "" : section);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight mb-1 flex items-center gap-2">
            <SettingsIcon className="w-6 h-6" />
            Settings
          </h1>
          <p className="text-muted-foreground">
            Configure Blender MCP, LLM providers, and preferences.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {hasChanges && (
            <button
              type="button"
              onClick={resetSettings}
              title="Reset all settings to default"
              aria-label="Reset settings"
              className="flex items-center space-x-2 px-4 py-2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reset</span>
            </button>
          )}
          <button
            type="button"
            onClick={saveSettings}
            disabled={!hasChanges || saving}
            className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            <Save className={`w-4 h-4 ${saving ? "animate-spin" : ""}`} />
            <span>{saving ? "Saving..." : "Save Changes"}</span>
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {/* LLM Provider Settings */}
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <button
            type="button"
            onClick={() => toggleSection("llm")}
            className="w-full p-4 flex items-center justify-between hover:bg-accent/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-400" />
              <h2 className="font-semibold">LLM Provider</h2>
              <span className="text-xs text-muted-foreground ml-2">({llmConfig.provider})</span>
            </div>
            {expandedSection === "llm" ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>

          {expandedSection === "llm" && (
            <div className="p-4 pt-0 space-y-6">
              {/* Provider Selection */}
              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => updateLLMProvider("ollama")}
                  className={`p-3 rounded-lg border text-left transition-colors ${
                    llmConfig.provider === "ollama"
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Cpu
                      className={`w-4 h-4 ${llmConfig.provider === "ollama" ? "text-primary" : "text-muted-foreground"}`}
                    />
                    <span className="font-medium">Ollama</span>
                  </div>
                  <p className="text-xs text-muted-foreground">Local models</p>
                </button>

                <button
                  type="button"
                  onClick={() => updateLLMProvider("lmstudio")}
                  className={`p-3 rounded-lg border text-left transition-colors ${
                    llmConfig.provider === "lmstudio"
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Server
                      className={`w-4 h-4 ${llmConfig.provider === "lmstudio" ? "text-primary" : "text-muted-foreground"}`}
                    />
                    <span className="font-medium">LM Studio</span>
                  </div>
                  <p className="text-xs text-muted-foreground">Local server</p>
                </button>

                <button
                  type="button"
                  onClick={() => updateLLMProvider("cloud")}
                  className={`p-3 rounded-lg border text-left transition-colors ${
                    llmConfig.provider === "cloud"
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Cloud
                      className={`w-4 h-4 ${llmConfig.provider === "cloud" ? "text-primary" : "text-muted-foreground"}`}
                    />
                    <span className="font-medium">Cloud (OpenAI)</span>
                  </div>
                  <p className="text-xs text-muted-foreground">API key required</p>
                </button>
              </div>

              {/* Ollama Settings */}
              {llmConfig.provider === "ollama" && (
                <div className="space-y-4">
                  <div>
                    <label htmlFor="ollama-url" className="text-sm font-medium mb-1 block">
                      Ollama URL
                    </label>
                    <input
                      id="ollama-url"
                      type="text"
                      title="Ollama Server URL"
                      placeholder="http://localhost:11434"
                      value={llmConfig.ollama_url}
                      onChange={(e) => updateLLMField("ollama_url", e.target.value)}
                      className="w-full bg-background border border-input rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Default: http://localhost:11434
                    </p>
                  </div>

                  {providerError && (
                    <div className="flex items-center gap-2 text-red-500 text-sm">
                      <AlertCircle className="w-4 h-4" />
                      {providerError}
                    </div>
                  )}

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label htmlFor="available-models" className="text-sm font-medium">
                        Available Models
                      </label>
                      <button
                        type="button"
                        onClick={fetchModels}
                        disabled={loadingModels}
                        className="flex items-center gap-1 text-xs text-primary hover:underline"
                      >
                        <RefreshCw className={`w-3 h-3 ${loadingModels ? "animate-spin" : ""}`} />
                        Refresh
                      </button>
                    </div>

                    <div className="border border-border rounded-md divide-y divide-border max-h-48 overflow-y-auto">
                      {loadingModels ? (
                        <div className="p-4 text-center text-muted-foreground text-sm">
                          Loading models...
                        </div>
                      ) : availableModels.length === 0 ? (
                        <div className="p-4 text-center text-muted-foreground text-sm">
                          No models found
                        </div>
                      ) : (
                        availableModels.map((model) => (
                          <div
                            key={model.id}
                            className={`p-3 flex items-center justify-between hover:bg-accent/50 cursor-pointer ${
                              llmConfig.selected_model === model.id ? "bg-primary/10" : ""
                            }`}
                          >
                            <div>
                              <div className="font-medium text-sm">{model.name}</div>
                              {model.size && (
                                <div className="text-xs text-muted-foreground">{model.size}</div>
                              )}
                            </div>
                            <div className="flex items-center gap-2">
                              {llmConfig.selected_model === model.id && (
                                <CheckCircle className="w-4 h-4 text-green-500" />
                              )}
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  loadOllamaModel(model.id);
                                }}
                                className="text-xs px-2 py-1 bg-primary text-primary-foreground rounded hover:bg-primary/90"
                              >
                                Load
                              </button>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* LM Studio Settings */}
              {llmConfig.provider === "lmstudio" && (
                <div className="space-y-4">
                  <div>
                    <label htmlFor="lmstudio-url" className="text-sm font-medium mb-1 block">
                      LM Studio URL
                    </label>
                    <input
                      id="lmstudio-url"
                      type="text"
                      title="LM Studio Server URL"
                      placeholder="http://localhost:1234"
                      value={llmConfig.lmstudio_url}
                      onChange={(e) => updateLLMField("lmstudio_url", e.target.value)}
                      className="w-full bg-background border border-input rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Default: http://localhost:1234
                    </p>
                  </div>

                  {providerError && (
                    <div className="flex items-center gap-2 text-red-500 text-sm">
                      <AlertCircle className="w-4 h-4" />
                      {providerError}
                    </div>
                  )}

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Connected Models</span>
                      <button
                        type="button"
                        onClick={fetchModels}
                        disabled={loadingModels}
                        className="flex items-center gap-1 text-xs text-primary hover:underline"
                      >
                        <RefreshCw className={`w-3 h-3 ${loadingModels ? "animate-spin" : ""}`} />
                        Refresh
                      </button>
                    </div>
                    {availableModels.map((model: ModelInfo) => (
                      <div
                        key={model.id}
                        className="flex items-center justify-between p-2 bg-muted/50 rounded mb-1"
                      >
                        <span className="text-sm">{model.name}</span>
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Cloud/OpenAI Settings */}
              {llmConfig.provider === "cloud" && (
                <div className="space-y-4">
                  <div>
                    <label
                      htmlFor="openai-key"
                      className="text-sm font-medium mb-1 flex items-center gap-2"
                    >
                      <Key className="w-4 h-4" />
                      OpenAI API Key
                    </label>
                    <input
                      id="openai-key"
                      type="password"
                      title="OpenAI API Key"
                      value={llmConfig.openai_api_key}
                      onChange={(e) => updateLLMField("openai_api_key", e.target.value)}
                      className="w-full bg-background border border-input rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
                      placeholder="sk-..."
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Your API key is stored locally and never shared.
                    </p>
                  </div>

                  <div>
                    <label htmlFor="openai-model" className="text-sm font-medium mb-1 block">
                      Model
                    </label>
                    <select
                      id="openai-model"
                      title="Select OpenAI Model"
                      value={llmConfig.openai_model}
                      onChange={(e) => updateLLMField("openai_model", e.target.value)}
                      className="w-full bg-background border border-input rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
                    >
                      <option value="gpt-4">GPT-4</option>
                      <option value="gpt-4-turbo">GPT-4 Turbo</option>
                      <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    </select>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Blender Connection */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Server className="w-5 h-5 text-blue-400" />
            <h2 className="font-semibold">Blender Connection</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="server-host" className="text-sm font-medium mb-1 block">
                Server Host
              </label>
              <input
                type="text"
                id="server-host"
                title="Server Hostname"
                placeholder="localhost"
                value={serverHost}
                onChange={(e) => {
                  setServerHost(e.target.value);
                  setHasChanges(true);
                }}
                className="w-full bg-background border border-input rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <div>
              <label htmlFor="server-port" className="text-sm font-medium mb-1 block">
                Server Port
              </label>
              <input
                type="number"
                id="server-port"
                title="Server Port Number"
                value={serverPort}
                onChange={(e) => {
                  setServerPort(Number.parseInt(e.target.value));
                  setHasChanges(true);
                }}
                className="w-full bg-background border border-input rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
          </div>
        </div>

        {/* Appearance */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Palette className="w-5 h-5 text-purple-400" />
            <h2 className="font-semibold">Appearance</h2>
          </div>
          <div>
            <label htmlFor="theme" className="text-sm font-medium mb-1 block">
              Theme
            </label>
            <select
              id="theme"
              title="Select Appearance Theme"
              value={theme}
              onChange={(e) => {
                setTheme(e.target.value);
                setHasChanges(true);
              }}
              className="w-full bg-background border border-input rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="system">System</option>
            </select>
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Bell className="w-5 h-5 text-yellow-400" />
            <h2 className="font-semibold">Notifications</h2>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">Auto Sync</div>
                <p className="text-xs text-muted-foreground">
                  Automatically sync changes to Blender
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  setAutoSync(!autoSync);
                  setHasChanges(true);
                }}
                title={autoSync ? "Disable Auto Sync" : "Enable Auto Sync"}
                aria-label="Toggle Auto Sync"
                className={`w-12 h-6 rounded-full transition-colors ${autoSync ? "bg-primary" : "bg-muted"}`}
              >
                <div
                  className={`w-5 h-5 rounded-full bg-background transition-transform ${autoSync ? "translate-x-6" : "translate-x-0.5"}`}
                />
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">Notifications</div>
                <p className="text-xs text-muted-foreground">Show toast notifications</p>
              </div>
              <button
                type="button"
                onClick={() => {
                  setNotifications(!notifications);
                  setHasChanges(true);
                }}
                title={notifications ? "Disable Notifications" : "Enable Notifications"}
                aria-label="Toggle Notifications"
                className={`w-12 h-6 rounded-full transition-colors ${notifications ? "bg-primary" : "bg-muted"}`}
              >
                <div
                  className={`w-5 h-5 rounded-full bg-background transition-transform ${notifications ? "translate-x-6" : "translate-x-0.5"}`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Security */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-green-400" />
            <h2 className="font-semibold">Security</h2>
          </div>
          <p className="text-sm text-muted-foreground">
            API keys and authentication tokens are stored locally in your browser and never shared
            with third parties.
          </p>
        </div>
      </div>
    </div>
  );
}
