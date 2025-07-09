import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      // proxy API requests to FastAPI backend
      '/tasks': 'http://localhost:8000',
      '/memory': 'http://localhost:8000'
    }
  }
});
