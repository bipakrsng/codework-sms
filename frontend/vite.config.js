import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  base: './',
  plugins: [
    vue(),
    vueDevTools(),
  ],
  server: {
    host:'0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://10.24.133.91:5000',
        changeOrigin: true,
        // No rewrite needed since Flask already expects /api prefix
      },
      '/socket.io': {
        target: 'http://10.24.133.91:5000',
        ws: true, // <-- IMPORTANT for WebSockets
      },
    },
    hmr: {
      protocol: 'ws',
      host: '10.24.133.91',
      port: 5173,
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
