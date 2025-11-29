import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { existsSync } from 'fs';

// Detect Docker (/app/package.json exists) vs local dev
const root = existsSync('/app/package.json') ? '/app' : __dirname;
const src = resolve(root, 'src');

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': src,
      '~components': resolve(src, 'components'),
      '~contexts': resolve(src, 'contexts'),
      '~features': resolve(src, 'features'),
      '~services': resolve(src, 'services'),
      '~types': resolve(src, 'types'),
      '~hooks': resolve(src, 'hooks'),
      '~config': resolve(src, 'config'),
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
