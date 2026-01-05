import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    // Suppress warnings about DOMException polyfills
    // Modern browsers have native DOMException support
    rollupOptions: {
      onwarn(warning, warn) {
        // Suppress DOMException warnings from dependencies
        // This is safe because modern browsers (including those used by Railway deployments)
        // have native DOMException support
        if (
          warning.message &&
          (warning.message.includes('DOMException') ||
           warning.message.includes('Use your platform\'s native DOMException'))
        ) {
          return
        }
        // Show all other warnings
        warn(warning)
      }
    }
  },
  // Optimize dependencies to use native browser APIs
  optimizeDeps: {
    include: ['axios', 'react', 'react-dom', 'react-router-dom']
  }
})

