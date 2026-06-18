import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    // plotly.js-dist-min is already a browser bundle — skip Vite pre-bundling
    exclude: ['plotly.js-dist-min'],
  },
})
