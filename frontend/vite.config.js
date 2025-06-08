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
    // Preserve symlinks to fix path resolution issues
    preserveSymlinks: true,
  },
  server: {
    // Handle symlinks properly
    fs: {
      allow: ['..'],
    },
  },
})