import {
  Activity,
  BookOpen,
  Box,
  Clapperboard,
  Database,
  Layers,
  LayoutGrid,
  MessageSquare,
  Monitor,
  Package,
  Palette,
  Pen,
  Play,
  Puzzle,
  ScanEye,
  Settings,
  Terminal,
  Wand2,
} from "lucide-react";
import { useEffect, useRef } from "react";
import { Link, Route, BrowserRouter as Router, Routes, useLocation } from "react-router-dom";
import { useZoom } from "./hooks/useZoom";
import AddonManagerPage from "./pages/addon-manager";
import AgentToolsPage from "./pages/agent-tools";
import AIConstructor from "./pages/ai-constructor";
import Animation2DPage from "./pages/animation-2d";
import Apps from "./pages/apps";
import Chat from "./pages/chat";
import Construct from "./pages/construct";
import Dashboard from "./pages/dashboard";
import GreasePencilPage from "./pages/grease-pencil";
import HelpPage from "./pages/help";
import LogsPage from "./pages/logs";
import MaterialStore from "./pages/material-store";
import MeshColliderSplat from "./pages/mesh-collider-splat";
import RepositoryPage from "./pages/repository";
import SceneExplorer from "./pages/scene-explorer";
import ScriptConsole from "./pages/script-console";
import SettingsPage from "./pages/settings";
import SkillsPage from "./pages/skills";
import StatusLogs from "./pages/status";
import StoryboardPage from "./pages/storyboard";
import VideoEditor from "./pages/video-editor";
import VRPipeline from "./pages/vr-pipeline";
import { useConnection } from "./store/connection";

function NavItem({ to, icon: Icon, label }: { to: string; icon: React.ElementType; label: string }) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
        isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-accent/50 hover:text-foreground"
      }`}
    >
      <Icon className="w-5 h-5" />
      <span className="font-medium">{label}</span>
      {isActive && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary" />}
    </Link>
  );
}

function ConnectionStatus() {
  const { state, lastError } = useConnection();
  const statusColor = state === "connected" ? "bg-emerald-500" : state === "connecting" ? "bg-amber-500" : "bg-red-500";
  const statusLabel =
    state === "connected"
      ? "System Online"
      : state === "connecting"
        ? "Connecting..."
        : `Offline${lastError ? ` (${lastError.slice(0, 60)})` : ""}`;
  return (
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full ${statusColor} animate-pulse`} data-testid="connection-status" />
      <span className="text-sm font-medium text-muted-foreground truncate" data-testid="connection-label">
        {statusLabel}
      </span>
    </div>
  );
}

const BACKEND_HEALTH_URL = import.meta.env.DEV ? "/api/v1/health" : "http://127.0.0.1:10849/api/v1/health";

const BACKOFF = [1, 2, 4, 8, 16, 30];

function useHealthPoll() {
  const attemptRef = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    let cancelled = false;
    async function tick() {
      try {
        const r = await fetch(BACKEND_HEALTH_URL, { signal: AbortSignal.timeout(5000) });
        if (cancelled) return;
        if (r.ok) {
          useConnection.setState({ state: "connected" });
          attemptRef.current = 0;
        } else useConnection.setState({ state: "offline", lastError: `HTTP ${r.status}` });
      } catch (e) {
        if (cancelled) return;
        useConnection.setState({
          state: "offline",
          lastError: e instanceof Error ? e.message : String(e),
        });
      }
      attemptRef.current = Math.min(++attemptRef.current, BACKOFF.length - 1);
      timerRef.current = setTimeout(tick, BACKOFF[attemptRef.current] * 1000);
    }
    tick();
    return () => {
      cancelled = true;
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);
}

function useTauriConnectionBridge() {
  useEffect(() => {
    let unlisten: (() => void) | undefined;
    (async () => {
      try {
        const { listen } = await import("@tauri-apps/api/event");
        unlisten = await listen<string>("backend-status", (event) => {
          if (event.payload === "ready") useConnection.setState({ state: "connected" });
          else if (event.payload?.startsWith("error:"))
            useConnection.setState({ state: "error", lastError: event.payload });
        });
      } catch {
        /* dev browser -- no-op */
      }
    })();
    return () => {
      if (unlisten) unlisten();
    };
  }, []);
}

function Layout() {
  useZoom();
  useHealthPoll();
  useTauriConnectionBridge();
  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 border-r border-border bg-card flex flex-col">
        <div className="p-6 flex items-center space-x-3 border-b border-border">
          <div className="w-8 h-8 rounded bg-primary flex items-center justify-center">
            <Box className="w-5 h-5 text-primary-foreground" />
          </div>
          <h1 className="font-bold text-xl tracking-tight">Blender MCP</h1>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          <div className="px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Creation</div>
          <NavItem to="/" icon={LayoutGrid} label="Dashboard" />
          <NavItem to="/scene" icon={Layers} label="Scene Explorer" />
          <NavItem to="/construct" icon={Wand2} label="Construct" />
          <NavItem to="/constructor" icon={Box} label="AI Constructor" />
          <NavItem to="/materials" icon={Monitor} label="Material Store" />
          <NavItem to="/mesh" icon={Package} label="Mesh / Collider / Splat" />
          <NavItem to="/repository" icon={Database} label="Repository" />
          <NavItem to="/addons" icon={Puzzle} label="Addon Manager" />

          <div className="mt-6 px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Agent Lab
          </div>
          <NavItem to="/agent-tools" icon={ScanEye} label="Agent Tools" />

          <div className="mt-6 px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            AI Assistant
          </div>
          <NavItem to="/chat" icon={MessageSquare} label="Chat" />

          <div className="mt-6 px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            2D Animation
          </div>
          <NavItem to="/grease-pencil" icon={Pen} label="Grease Pencil" />
          <NavItem to="/animation-2d" icon={Palette} label="2D Animation" />
          <NavItem to="/storyboard" icon={Clapperboard} label="Storyboard" />

          <div className="mt-6 px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Pipeline
          </div>
          <NavItem to="/vr" icon={Play} label="VR Pipeline" />
          <NavItem to="/scripts" icon={Terminal} label="Script Console" />
          <NavItem to="/video" icon={Clapperboard} label="Video Editor" />

          <div className="mt-6 px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            System
          </div>
          <NavItem to="/logs" icon={Terminal} label="Logs" />
          <NavItem to="/help" icon={BookOpen} label="Help & Reference" />
          <NavItem to="/skills" icon={BookOpen} label="Skills" />
          <NavItem to="/status" icon={Activity} label="System Status" />
          <NavItem to="/apps" icon={LayoutGrid} label="App Hub" />
          <NavItem to="/settings" icon={Settings} label="Settings" />
        </nav>

        <div className="p-4 border-t border-border bg-muted/20">
          <ConnectionStatus />
          <div className="text-xs text-muted-foreground text-center mt-1">v0.10.0</div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden bg-background">
        <header className="h-16 border-b border-border flex items-center px-6 bg-card/50 backdrop-blur justify-between">
          <h2 className="text-lg font-semibold">Active Scene: Untitled.blend</h2>
          <div className="flex items-center space-x-4">
            <button
              type="button"
              className="px-3 py-1.5 text-sm font-medium bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
            >
              Refresh Data
            </button>
            <button
              type="button"
              className="px-3 py-1.5 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Sync to Blender
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scene" element={<SceneExplorer />} />
            <Route path="/construct" element={<Construct />} />
            <Route path="/constructor" element={<AIConstructor />} />
            <Route path="/materials" element={<MaterialStore />} />
            <Route path="/mesh" element={<MeshColliderSplat />} />
            <Route path="/agent-tools" element={<AgentToolsPage />} />
            <Route path="/repository" element={<RepositoryPage />} />
            <Route path="/addons" element={<AddonManagerPage />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/grease-pencil" element={<GreasePencilPage />} />
            <Route path="/animation-2d" element={<Animation2DPage />} />
            <Route path="/storyboard" element={<StoryboardPage />} />
            <Route path="/vr" element={<VRPipeline />} />
            <Route path="/scripts" element={<ScriptConsole />} />
            <Route path="/video" element={<VideoEditor />} />
            <Route path="/status" element={<StatusLogs />} />
            <Route path="/logs" element={<LogsPage />} />
            <Route path="/help" element={<HelpPage />} />
            <Route path="/skills" element={<SkillsPage />} />
            <Route path="/apps" element={<Apps />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<div className="p-6">Select a tool from the sidebar</div>} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Layout />
    </Router>
  );
}

export default App;
