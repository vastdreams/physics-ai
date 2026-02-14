import { resolve } from 'path';
import { writeFileSync } from 'fs';

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const DEFAULT_PORT = 3000;
const DEFAULT_BACKEND_URL = 'http://localhost:5002';

/**
 * Vite plugin that writes a version.json manifest into the build output.
 * The frontend polls this file to detect when a new build is deployed,
 * then shows an "Update available" banner.
 */
function versionManifestPlugin() {
  let buildHash = '';
  return {
    name: 'version-manifest',
    buildStart() {
      // Generate a unique build hash from the current timestamp + random suffix
      buildHash = Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
    },
    closeBundle() {
      const manifest = {
        version: process.env.npm_package_version || '0.0.0',
        buildHash,
        buildTime: new Date().toISOString(),
        commit: process.env.COMMIT_SHA || 'local',
      };
      writeFileSync(
        resolve(__dirname, 'dist', 'version.json'),
        JSON.stringify(manifest, null, 2),
      );
    },
  };
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), versionManifestPlugin()],
  define: {
    __BUILD_HASH__: JSON.stringify(
      process.env.COMMIT_SHA ||
        Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
    ),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
  server: {
    port: parseInt(process.env.VITE_PORT || String(DEFAULT_PORT), 10),
    open: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || DEFAULT_BACKEND_URL,
        changeOrigin: true,
      },
      '/socket.io': {
        target: process.env.VITE_API_URL || DEFAULT_BACKEND_URL,
        changeOrigin: true,
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
