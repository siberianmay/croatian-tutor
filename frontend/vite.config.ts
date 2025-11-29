import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '~components': path.resolve(__dirname, 'src/components'),
      '~contexts': path.resolve(__dirname, 'src/contexts'),
      '~features': path.resolve(__dirname, 'src/features'),
      '~services': path.resolve(__dirname, 'src/services'),
      '~types': path.resolve(__dirname, 'src/types/index'),
      '~hooks': path.resolve(__dirname, 'src/hooks'),
      '~config': path.resolve(__dirname, 'src/config'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
});
