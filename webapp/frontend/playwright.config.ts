import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  timeout: 60000,
  retries: 1,
  use: { baseURL: "http://localhost:10848", headless: true, screenshot: "only-on-failure" },
  webServer: [
    {
      // Backend API (uvicorn serves the FastMCP ASGI app directly)
      command: "uv run uvicorn blender_mcp.server:asgi_app --host 127.0.0.1 --port 10849",
      url: "http://127.0.0.1:10849/api/v1/health",
      timeout: 120000,
      reuseExistingServer: true,
      cwd: "../..",
    },
    {
      // Frontend dev server (same-origin /api + /mcp proxy, see vite.config.ts)
      command: "npm run dev -- --port 10848 --host",
      url: "http://127.0.0.1:10848",
      timeout: 120000,
      reuseExistingServer: true,
    },
  ],
});
