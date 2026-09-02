import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    "import.meta.env.VITE_API_BASE": JSON.stringify(process.env.VITE_API_BASE || ""),
  },
  build: {
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ["react", "react-dom", "react-router-dom"],
          vendor: ["framer-motion", "zustand", "lucide-react"],
        },
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: "0.0.0.0",
    allowedHosts: ["goliath"],
    port: 10848,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:10849",
        changeOrigin: true,
      },
      "/mcp": {
        target: "http://127.0.0.1:10849",
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path.replace(/^\/mcp/, ""),
      },
    },
  },
});
