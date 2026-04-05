import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { Monitor, Box, Layers, Play, Settings, Terminal, Activity, MessageSquare, Wand2, LayoutGrid, Package, Database, Puzzle } from 'lucide-react'
import SceneExplorer from './pages/scene-explorer'
import MeshColliderSplat from './pages/mesh-collider-splat'
import AIConstructor from './pages/ai-constructor'
import MaterialStore from './pages/material-store'
import VRPipeline from './pages/vr-pipeline'
import ScriptConsole from './pages/script-console'
import StatusLogs from './pages/status'
import SettingsPage from './pages/settings'
import Chat from './pages/chat'
import Construct from './pages/construct'
import Apps from './pages/apps'
import RepositoryPage from './pages/repository'
import AddonManagerPage from './pages/addon-manager'

function NavItem({ to, icon: Icon, label }: { to: string, icon: any, label: string }) {
    const location = useLocation()
    const isActive = location.pathname === to

    return (
        <Link
            to={to}
            className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${isActive
                ? 'bg-accent text-accent-foreground'
                : 'text-muted-foreground hover:bg-accent/50 hover:text-foreground'
                }`}
        >
            <Icon className="w-5 h-5" />
            <span className="font-medium">{label}</span>
            {isActive && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary" />}
        </Link>
    )
}

function Layout() {
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
                    <div className="px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        Creation
                    </div>
                    <NavItem to="/" icon={Layers} label="Scene Explorer" />
                    <NavItem to="/construct" icon={Wand2} label="Construct" />
                    <NavItem to="/constructor" icon={Box} label="AI Constructor" />
                    <NavItem to="/materials" icon={Monitor} label="Material Store" />
                    <NavItem to="/mesh" icon={Package} label="Mesh / Collider / Splat" />
                    <NavItem to="/repository" icon={Database} label="Repository" />
                    <NavItem to="/addons" icon={Puzzle} label="Addon Manager" />

                    <div className="mt-6 px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        AI Assistant
                    </div>
                    <NavItem to="/chat" icon={MessageSquare} label="Chat" />

                    <div className="mt-6 px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        Pipeline
                    </div>
                    <NavItem to="/vr" icon={Play} label="VR Pipeline" />
                    <NavItem to="/scripts" icon={Terminal} label="Script Console" />

                    <div className="mt-6 px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        System
                    </div>
                    <NavItem to="/status" icon={Activity} label="Status & Logs" />
                    <NavItem to="/apps" icon={LayoutGrid} label="App Hub" />
                    <NavItem to="/settings" icon={Settings} label="Settings" />
                </nav>

                <div className="p-4 border-t border-border bg-muted/20">
                    <div className="flex items-center space-x-3">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="text-sm font-medium text-muted-foreground">System Online</span>
                        <span className="text-xs text-muted-foreground ml-auto">v1.0.0</span>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden bg-background">
                <header className="h-16 border-b border-border flex items-center px-6 bg-card/50 backdrop-blur justify-between">
                    <h2 className="text-lg font-semibold">Active Scene: Untitled.blend</h2>
                    <div className="flex items-center space-x-4">
                        <button className="px-3 py-1.5 text-sm font-medium bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors">
                            Refresh Data
                        </button>
                        <button className="px-3 py-1.5 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
                            Sync to Blender
                        </button>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto">
                    <Routes>
                        <Route path="/" element={<SceneExplorer />} />
                        <Route path="/construct" element={<Construct />} />
                        <Route path="/constructor" element={<AIConstructor />} />
                        <Route path="/materials" element={<MaterialStore />} />
                        <Route path="/mesh" element={<MeshColliderSplat />} />
                        <Route path="/repository" element={<RepositoryPage />} />
                        <Route path="/addons" element={<AddonManagerPage />} />
                        <Route path="/chat" element={<Chat />} />
                        <Route path="/vr" element={<VRPipeline />} />
                        <Route path="/scripts" element={<ScriptConsole />} />
                        <Route path="/status" element={<StatusLogs />} />
                        <Route path="/apps" element={<Apps />} />
                        <Route path="/settings" element={<SettingsPage />} />
                        <Route path="*" element={<div className="p-6">Select a tool from the sidebar</div>} />
                    </Routes>
                </main>
            </div>
        </div>
    )
}

function App() {
    return (
        <Router>
            <Layout />
        </Router>
    )
}

export default App
