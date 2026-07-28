import { Bot, Download, Eraser, MessageSquare, Send, Sparkles, User } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { sendChatMessage } from "../api/mcp";

const STORAGE_KEY = "blender-mcp-chat-history";
const PERSONALITY_KEY = "blender-mcp-chat-personality";
const MAX_MESSAGES = 100;

const PERSONALITIES: Record<string, { label: string; prompt: string }> = {
  "blender-expert": {
    label: "Blender Expert",
    prompt:
      "You are a Blender expert assistant. You have access to the full blender-mcp toolset. Respond conversationally and suggest specific tools when the user asks about Blender tasks. Keep responses technical and concise.",
  },
  "research-assistant": {
    label: "Research Assistant",
    prompt:
      "You are a thorough research assistant specializing in 3D graphics and Blender. Provide detailed explanations, cite techniques, and suggest learning resources. Break down complex concepts step by step.",
  },
  "quick-summarizer": {
    label: "Quick Summarizer",
    prompt:
      "You are a concise assistant. Provide brief, direct answers. Use bullet points where possible. Do not elaborate unless asked. Focus on actionable steps.",
  },
  "creative-advisor": {
    label: "Creative Advisor",
    prompt:
      "You are a creative 3D design advisor. Suggest artistic approaches, composition tips, and visual storytelling techniques. Be inspiring and offer multiple creative directions for the user's projects.",
  },
};

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  ts?: string;
}

function loadHistory(): Message[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw).slice(0, MAX_MESSAGES);
  } catch {
    /* ignore */
  }
  return [];
}

function saveHistory(messages: Message[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-MAX_MESSAGES)));
  } catch {
    /* ignore */
  }
}

function loadPersonality(): string {
  try {
    return localStorage.getItem(PERSONALITY_KEY) || "blender-expert";
  } catch {
    return "blender-expert";
  }
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>(() => {
    const saved = loadHistory();
    if (saved.length > 0) return saved;
    return [
      {
        id: "welcome",
        role: "assistant",
        content:
          "Hello! I'm your Blender MCP assistant. I can help you create objects, modify scenes, apply materials, and more. What would you like to do?",
        ts: new Date().toISOString(),
      },
    ];
  });
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [personalityId, setPersonalityId] = useState(loadPersonality);
  const [skillName, setSkillName] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    saveHistory(messages);
  }, [messages]);
  useEffect(() => {
    localStorage.setItem(PERSONALITY_KEY, personalityId);
  }, [personalityId]);

  useEffect(() => {
    (async () => {
      try {
        const base = import.meta.env.DEV ? "/mcp" : "http://127.0.0.1:10849";
        const r = await fetch(`${base}/api/skills`);
        if (r.ok) {
          const data = await r.json();
          if (data.skills?.length > 0) setSkillName(data.skills[0].name || "blender-expert");
        }
      } catch {
        /* ignore */
      }
    })();
  }, []);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const buildPrompt = useCallback(() => {
    const personality = PERSONALITIES[personalityId];
    const role = personality ? personality.prompt : PERSONALITIES["blender-expert"].prompt;
    const skill = skillName ? `Active skill: ${skillName}. ` : "";
    return `${skill}${role}`;
  }, [personalityId, skillName]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      ts: new Date().toISOString(),
    };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setIsLoading(true);
    try {
      const fullPrompt = buildPrompt();
      const messageWithContext = `${fullPrompt}\n\nUser: ${userMsg.content}`;
      const response = await sendChatMessage(messageWithContext);
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          response.success && response.data
            ? (response.data as { response?: string }).response || "I processed your request."
            : "I'm having trouble connecting to the AI backend. The tools in the sidebar are still available for direct use.",
        ts: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Connection issue: ${err instanceof Error ? err.message : "Unknown error"}. Try using the sidebar tools directly.`,
          ts: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleExport = () => {
    const lines = messages.map((m) => `[${m.ts ? new Date(m.ts).toISOString() : ""}] ${m.role}: ${m.content}`);
    const blob = new Blob([lines.join("\n\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `blender-mcp-chat-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleClear = () => {
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content: "Conversation cleared. How can I help you?",
        ts: new Date().toISOString(),
      },
    ]);
    localStorage.removeItem(STORAGE_KEY);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]" data-testid="chat-page">
      <div
        className="flex items-center justify-between px-6 py-4 border-b border-border bg-card/50"
        data-testid="chat-controls"
      >
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-primary" />
          <h1 className="font-semibold">AI Chat</h1>
          {skillName && <span className="text-sm text-muted-foreground ml-2">skill:{skillName}</span>}
        </div>
        <div className="flex items-center gap-3">
          <select
            value={personalityId}
            onChange={(e) => setPersonalityId(e.target.value)}
            className="bg-zinc-800 text-zinc-100 border border-zinc-600 rounded px-2 py-1 text-sm"
            data-testid="personality-select"
          >
            {Object.entries(PERSONALITIES).map(([id, p]) => (
              <option key={id} value={id}>
                {p.label}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={handleExport}
            disabled={messages.length === 0}
            className="p-1.5 text-muted-foreground hover:text-foreground transition-colors disabled:opacity-30"
            title="Export chat"
            data-testid="chat-export"
          >
            <Download className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={handleClear}
            disabled={messages.length <= 1}
            className="p-1.5 text-muted-foreground hover:text-foreground transition-colors disabled:opacity-30"
            title="Clear conversation"
            data-testid="chat-clear"
          >
            <Eraser className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4" data-testid="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
            {message.role === "assistant" && (
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-primary-foreground" />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"}`}
            >
              <div className="text-sm whitespace-pre-wrap">{message.content}</div>
              {message.ts && (
                <div
                  className={`text-sm mt-1 ${message.role === "user" ? "text-primary-foreground/70" : "text-muted-foreground"}`}
                >
                  {new Date(message.ts).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              )}
            </div>
            {message.role === "user" && (
              <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-primary-foreground" />
            </div>
            <div className="bg-muted rounded-lg px-4 py-3 flex items-center gap-2">
              <div className="w-2 h-2 bg-current rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:0.2s]" />
              <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:0.4s]" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="px-6 py-2 border-t border-border bg-card/30" data-testid="example-prompts">
        <div className="flex items-center gap-2 overflow-x-auto">
          <span className="text-sm text-muted-foreground whitespace-nowrap">Quick commands:</span>
          {["Create a cube", "Add lighting", "Apply material", "Render scene", "Export to FBX"].map((cmd) => (
            <button
              key={cmd}
              type="button"
              onClick={() => setInput(cmd)}
              className="text-sm px-3 py-1 bg-secondary text-secondary-foreground rounded-full hover:bg-secondary/80 transition-colors whitespace-nowrap flex items-center gap-1"
            >
              <Sparkles className="w-3 h-3" />
              {cmd}
            </button>
          ))}
        </div>
      </div>

      <div className="px-6 py-4 border-t border-border bg-card/50">
        <div className="flex items-end gap-2 bg-background border border-input rounded-lg p-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me to create objects, modify scenes, or help with Blender..."
            className="flex-1 bg-transparent resize-none outline-none min-h-[44px] max-h-[120px] py-2 px-1"
            rows={1}
            style={{ height: "auto" }}
            data-testid="chat-input"
          />
          <button
            type="button"
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="p-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            data-testid="chat-send"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
