import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
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
