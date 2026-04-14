import {
  BookOpen,
  Box,
  Mic,
  MonitorSmartphone,
  Music,
  ShieldCheck,
  TrainFront,
  User,
  UserCircle,
  Video,
  Waves,
} from "lucide-react";
import type React from "react";

export interface FleetMember {
  id: string;
  name: string;
  description: string;
  port: number;
  repo_path: string;
  icon: React.ElementType;
  category: "Transit" | "Media" | "Infra" | "Control" | "Creative" | "Knowledge" | "Core";
}

export const FLEET_REGISTRY: FleetMember[] = [
  {
    id: "blender-mcp",
    name: "Blender Control",
    description: "3D visualization and geometry orchestration.",
    port: 10848,
    repo_path: "D:/Dev/repos/blender-mcp",
    icon: Box,
    category: "Creative",
  },
  {
    id: "avatar-mcp",
    name: "Avatar Control",
    description: "VRM avatar management and animation orchestration.",
    port: 10792,
    repo_path: "D:/Dev/repos/avatar-mcp",
    icon: UserCircle,
    category: "Creative",
  },
  {
    id: "alexa-mcp",
    name: "Alexa Control",
    description: "Acoustic bridge and voice command orchestration.",
    port: 10800,
    repo_path: "D:/Dev/repos/alexa-mcp",
    icon: Mic,
    category: "Control",
  },
  {
    id: "vienna-live-mcp",
    name: "Vienna Live MCP",
    description: "Transit and location-aware services in Vienna.",
    port: 10878,
    repo_path: "D:/Dev/repos/vienna-live-mcp",
    icon: TrainFront,
    category: "Transit",
  },
  {
    id: "handbrake-mcp",
    name: "Handbrake MCP",
    description: "Automated media transcoding and pipeline management.",
    port: 10874,
    repo_path: "D:/Dev/repos/handbrake-mcp",
    icon: Video,
    category: "Media",
  },
  {
    id: "virtualdj-mcp",
    name: "VirtualDJ MCP",
    description: "SOTA VJing and audio orchestration.",
    port: 10876,
    repo_path: "D:/Dev/repos/virtualdj-mcp",
    icon: Music,
    category: "Media",
  },
  {
    id: "openfang",
    name: "OpenFang",
    description: "Fleet supervisor and modular agentic node controller.",
    port: 10870,
    repo_path: "D:/Dev/repos/openfang",
    icon: ShieldCheck,
    category: "Infra",
  },
  {
    id: "osc-mcp",
    name: "OSC MCP",
    description: "Real-time control protocol bridge for high-end audio/visual gear.",
    port: 10766,
    repo_path: "D:/Dev/repos/osc-mcp",
    icon: Waves,
    category: "Control",
  },
  {
    id: "rustdesk-mcp",
    name: "RustDesk MCP",
    description: "Secure remote access and fleet management.",
    port: 10804,
    repo_path: "D:/Dev/repos/rustdesk-mcp",
    icon: MonitorSmartphone,
    category: "Infra",
  },
  {
    id: "vroidstudio-mcp",
    name: "VroidStudio MCP",
    description: "Avatar creation and VR character pipeline.",
    port: 10880,
    repo_path: "D:/Dev/repos/vroidstudio-mcp",
    icon: User,
    category: "Creative",
  },
  {
    id: "obsidian-mcp",
    name: "Obsidian MCP",
    description: "Knowledge graph and second brain integration.",
    port: 10704,
    repo_path: "D:/Dev/repos/obsidian-mcp",
    icon: BookOpen,
    category: "Knowledge",
  },
  {
    id: "mcp-central-docs",
    name: "Docs MCP",
    description: "Standardized MCP documentation and fleet registry.",
    port: 10720,
    repo_path: "D:/Dev/repos/mcp-central-docs",
    icon: BookOpen,
    category: "Knowledge",
  },
  {
    id: "mywienerlinien",
    name: "My Wiener Linien",
    description: "Advanced transit tracking for the city of Vienna.",
    port: 10872,
    repo_path: "D:/Dev/repos/mywienerlinien",
    icon: TrainFront,
    category: "Transit",
  },
  {
    id: "nest-protect-mcp",
    name: "Nest Protect MCP",
    description: "Smart safety monitoring and emergency orchestration.",
    port: 10768,
    repo_path: "D:/Dev/repos/nest-protect-mcp",
    icon: ShieldCheck,
    category: "Control",
  },
];
