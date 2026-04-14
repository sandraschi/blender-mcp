import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, ExternalLink, Loader2, Play } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import type { FleetMember } from "./apps-catalog";

interface FleetCardProps {
  member: FleetMember;
  currentAppId?: string;
}

export function FleetCard({ member, currentAppId }: FleetCardProps) {
  const isCurrent = member.id === currentAppId;
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking");
  const [isLaunching, setIsLaunching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkStatus = useCallback(async () => {
    try {
      const controller = new AbortController();
      const id = setTimeout(() => controller.abort(), 2000);
      const resp = await fetch(`http://localhost:${member.port}/api/v1/health`, {
        signal: controller.signal,
      });
      clearTimeout(id);
      setStatus(resp.ok ? "online" : "offline");
    } catch {
      setStatus("offline");
    }
  }, [member.port]);

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, [checkStatus]);

  const launchApp = async () => {
    setIsLaunching(true);
    setError(null);
    try {
      const resp = await fetch("/api/v1/fleet/launch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_path: member.repo_path,
          port: member.port,
          app_id: member.id,
        }),
      });

      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || "Launch failed");

      // Poll for online status
      let attempts = 0;
      const poll = setInterval(async () => {
        attempts++;
        try {
          const check = await fetch(`http://localhost:${member.port}/api/v1/health`);
          if (check.ok) {
            clearInterval(poll);
            setIsLaunching(false);
            setStatus("online");
            window.location.href = `http://localhost:${member.port}`;
          }
        } catch {
          if (attempts > 30) {
            clearInterval(poll);
            setIsLaunching(false);
            setError("Launch timed out. Start manually.");
          }
        }
      }, 1000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Connect failed");
      setIsLaunching(false);
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`group relative overflow-hidden rounded-xl border p-5 transition-all duration-300 ${
        isCurrent
          ? "border-primary/50 bg-primary/5 shadow-[0_0_20px_rgba(59,130,246,0.1)]"
          : "border-border bg-card/40 hover:border-primary/50 hover:bg-card/60"
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`flex h-10 w-10 items-center justify-center rounded-lg ${
              isCurrent
                ? "bg-primary/20 text-primary"
                : "bg-muted text-muted-foreground group-hover:text-foreground"
            }`}
          >
            <member.icon className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-semibold">{member.name}</h3>
            <p className="text-xs text-muted-foreground">{member.category}</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <div
            className={`h-2 w-2 rounded-full ${
              status === "online"
                ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"
                : status === "offline"
                  ? "bg-muted"
                  : "bg-primary animate-pulse"
            }`}
          />
          <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
            {status}
          </span>
        </div>
      </div>

      <p className="mt-4 text-xs leading-relaxed text-muted-foreground line-clamp-2">
        {member.description}
      </p>

      <div className="mt-6 flex gap-2">
        {status === "online" ? (
          <a
            href={`http://localhost:${member.port}`}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-secondary py-2 text-xs font-medium text-secondary-foreground transition-colors hover:bg-secondary/80 active:scale-95"
          >
            <ExternalLink className="h-3.5 w-3.5" />
            Enter Dashboard
          </a>
        ) : (
          <button
            type="button"
            onClick={launchApp}
            disabled={isLaunching || isCurrent}
            className={`flex flex-1 items-center justify-center gap-2 rounded-lg py-2 text-xs font-medium transition-all active:scale-95 ${
              isLaunching
                ? "bg-primary/20 text-primary cursor-not-allowed"
                : "bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            }`}
          >
            {isLaunching ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Launching...
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5" />
                Start Service
              </>
            )}
          </button>
        )}
      </div>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3 flex items-center gap-2 text-[10px] text-destructive"
          >
            <AlertCircle className="h-3 w-3" />
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {isCurrent && (
        <div className="absolute top-2 right-2">
          <span className="flex items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-[9px] font-bold uppercase text-primary border border-primary/20">
            Current
          </span>
        </div>
      )}
    </motion.div>
  );
}
