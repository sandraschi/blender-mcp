import { useCallback, useRef } from "react";

let fileInputCounter = 0;

/** True when running inside the Tauri 2.0 WebView (NSIS installer). */
export function isTauri(): boolean {
  return typeof window !== "undefined" && "__TAURI_INTERNALS__" in window;
}

/** Result of opening a file. `path` is available in Tauri; `data` in browser. */
export type OpenFileResult = {
  name: string;
  /** File bytes (both Tauri and browser). */
  data: ArrayBuffer;
  /** Filesystem path (Tauri only — backend can read directly). */
  path?: string;
};

/** Options for saving a file. */
export type SaveFileOptions = {
  filename?: string;
  content: string | Blob;
  mimeType?: string;
};

/**
 * Centralized hook for all @tauri-apps/api operations.
 * Every method has a browser-native fallback — pages call these methods
 * unconditionally and get the right behavior in both Tauri and dev browser.
 */
export function useTauri() {
  const tauri = isTauri();
  const tauriRef = useRef(tauri);
  tauriRef.current = tauri;

  /** Call a Tauri Rust command. Returns null in dev browser. */
  const invoke = useCallback(async <T>(cmd: string, args?: Record<string, unknown>): Promise<T | null> => {
    if (!tauriRef.current) return null;
    try {
      const m = await import("@tauri-apps/api/core");
      return await m.invoke<T>(cmd, args);
    } catch {
      return null;
    }
  }, []);

  /**
   * Listen for a Tauri event.
   * In Tauri 2, the callback receives `Event<T>` where `event.payload` is T.
   * Returns null in dev browser.
   */
  const listen = useCallback(async <T>(event: string, handler: (payload: T) => void): Promise<(() => void) | null> => {
    if (!tauriRef.current) return null;
    try {
      const m = await import("@tauri-apps/api/event");
      return await m.listen<T>(event, (e) => handler(e.payload));
    } catch {
      return null;
    }
  }, []);

  /** Open a native file picker. Falls back to `<input type="file">` in browser. */
  const openFile = useCallback(async (extensions?: string[]): Promise<OpenFileResult | null> => {
    if (tauriRef.current) {
      try {
        const { open } = await import("@tauri-apps/plugin-dialog");
        const r = await open({
          multiple: false,
          filters: extensions ? [{ name: "Files", extensions }] : undefined,
        });
        if (!r) return null;
        const name = r.split(/[/\\]/).pop() || r;
        const { readFile } = await import("@tauri-apps/plugin-fs");
        const uint8 = await readFile(r);
        return {
          name,
          data: uint8.buffer.slice(uint8.byteOffset, uint8.byteOffset + uint8.byteLength),
          path: r,
        };
      } catch {
        return null;
      }
    }
    return new Promise((resolve) => {
      const id = `tauri-file-input-${++fileInputCounter}`;
      const input = document.createElement("input");
      input.id = id;
      input.type = "file";
      input.style.display = "none";
      if (extensions) input.accept = extensions.map((e) => `.${e}`).join(",");
      input.onchange = async () => {
        const file = input.files?.[0];
        if (!file) {
          resolve(null);
          return;
        }
        resolve({ name: file.name, data: await file.arrayBuffer() });
        input.remove();
      };
      document.body.appendChild(input);
      input.click();
    });
  }, []);

  /** Save content to a file. Falls back to browser download in dev. */
  const saveFile = useCallback(async (opts: SaveFileOptions): Promise<string | null> => {
    const filename = opts.filename || "download";
    if (tauriRef.current) {
      try {
        const { save } = await import("@tauri-apps/plugin-dialog");
        const path = await save({ defaultPath: filename });
        if (!path) return null;
        const fs = await import("@tauri-apps/plugin-fs");
        if (typeof opts.content === "string") {
          await fs.writeTextFile(path, opts.content);
        } else {
          const buf = await opts.content.arrayBuffer();
          await fs.writeFile(path, new Uint8Array(buf));
        }
        return path;
      } catch {
        return null;
      }
    }
    const blob =
      typeof opts.content === "string"
        ? new Blob([opts.content], { type: opts.mimeType || "text/plain" })
        : opts.content;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.style.display = "none";
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      URL.revokeObjectURL(url);
      a.remove();
    }, 1000);
    return filename;
  }, []);

  /** OS toast notification. Falls back to Web Notification API in browser. */
  const notify = useCallback(
    async (title: string, body?: string) => {
      if (!tauri) {
        try {
          new Notification(title, { body });
        } catch {}
        return;
      }
      try {
        const m = await import("@tauri-apps/plugin-notification");
        await m.sendNotification({ title, body });
      } catch {
        try {
          new Notification(title, { body });
        } catch {}
      }
    },
    [tauri],
  );

  /** Native confirm dialog. Falls back to window.confirm in browser. */
  const confirmAction = useCallback(
    async (msg: string): Promise<boolean> => {
      if (!tauri) return window.confirm(msg);
      try {
        const m = await import("@tauri-apps/plugin-dialog");
        return await m.ask(msg);
      } catch {
        return window.confirm(msg);
      }
    },
    [tauri],
  );

  /** Native message dialog. Falls back to alert in browser. */
  const showMessage = useCallback(
    async (msg: string) => {
      if (!tauri) {
        alert(msg);
        return;
      }
      try {
        const m = await import("@tauri-apps/plugin-dialog");
        await m.message(msg);
      } catch {
        alert(msg);
      }
    },
    [tauri],
  );

  /** Open URL in default browser. Falls back to window.open in browser. */
  const openUrl = useCallback(
    async (url: string) => {
      if (!tauri) {
        window.open(url, "_blank");
        return;
      }
      try {
        const m = await import("@tauri-apps/plugin-shell");
        await m.open(url);
      } catch {
        window.open(url, "_blank");
      }
    },
    [tauri],
  );

  /** Set window titlebar text. Always updates document.title as fallback. */
  const setWindowTitle = useCallback(
    async (title: string) => {
      document.title = title;
      if (!tauri) return;
      try {
        const m = await import("@tauri-apps/api/window");
        await m.getCurrentWindow().setTitle(title);
      } catch {}
    },
    [tauri],
  );

  /** Copy text to system clipboard. Falls back to navigator.clipboard. */
  const copyToClipboard = useCallback(
    async (text: string) => {
      if (!tauri) {
        try {
          await navigator.clipboard.writeText(text);
        } catch {}
        return;
      }
      try {
        const m = await import("@tauri-apps/plugin-clipboard-manager");
        await m.writeText(text);
      } catch {
        try {
          await navigator.clipboard.writeText(text);
        } catch {}
      }
    },
    [tauri],
  );

  const readSettings = useCallback(
    async <T>(key: string): Promise<T | null> => {
      if (!tauri) {
        try {
          return JSON.parse(localStorage.getItem(key) ?? "null");
        } catch {
          return null;
        }
      }
      try {
        const { readTextFile } = await import("@tauri-apps/plugin-fs");
        return JSON.parse(await readTextFile(`${key}.json`));
      } catch {
        return null;
      }
    },
    [tauri],
  );

  const writeSettings = useCallback(
    async (key: string, data: unknown) => {
      if (!tauri) {
        localStorage.setItem(key, JSON.stringify(data));
        return;
      }
      try {
        const { writeTextFile } = await import("@tauri-apps/plugin-fs");
        await writeTextFile(`${key}.json`, JSON.stringify(data, null, 2));
      } catch {}
    },
    [tauri],
  );

  return {
    isTauri: tauri,
    invoke,
    listen,
    openFile,
    saveFile,
    notify,
    confirmAction,
    showMessage,
    openUrl,
    setWindowTitle,
    copyToClipboard,
    readSettings,
    writeSettings,
  };
}
