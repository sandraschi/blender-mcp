import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    server: {
        port: 10848,
        strictPort: true,
        proxy: {
            '/mcp': {
                target: 'http://localhost:10849',
                changeOrigin: true,
                ws: true,
                rewrite: (path) => path.replace(/^\/mcp/, '')
            }
        }
    }
})
