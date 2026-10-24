import { defineConfig } from 'astro/config';

export default defineConfig({
  build: {
    format: 'file'
  },
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:3000',
          changeOrigin: true
        }
      }
    }
  }
});
