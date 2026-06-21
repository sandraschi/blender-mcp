import { defineConfig } from '@playwright/test';
export default defineConfig({
    testDir: './e2e', timeout: 60000, retries: 1,
    use: { baseURL: 'http://localhost:10848', headless: true, screenshot: 'only-on-failure' },
    webServer: {
        command: 'uv run python -m blender_mcp.server --port 10849',
        port: 10849, timeout: 30000, reuseExistingServer: false
    }
});
