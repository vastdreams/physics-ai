import { resolve } from 'path';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { execSync } from 'child_process';

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const DEFAULT_PORT = 3000;
const DEFAULT_BACKEND_URL = 'http://localhost:5002';

/* ── Shared build metadata ──────────────────────────────────────
 * A single hash used by BOTH `define` (compiled into JS) and
 * the `version.json` manifest written to dist/.
 * This ensures the auto-update check compares apples-to-apples.
 */
function getBuildMeta() {
  // Try to use the real git SHA — deterministic and meaningful
  let commit = process.env.COMMIT_SHA || '';
  if (!commit) {
    try { commit = execSync('git rev-parse --short HEAD', { encoding: 'utf-8' }).trim(); }
    catch { commit = ''; }
  }
  const hash = commit || Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
  const version = process.env.npm_package_version || '2.0.0';
  const time = new Date().toISOString();
  return { hash, version, time, commit: commit || 'local' };
}

const buildMeta = getBuildMeta();

/**
 * Vite plugin that writes a version.json manifest into the build output.
 * The frontend polls this file to detect when a new build is deployed,
 * then shows an "Update available" banner.
 *
 * Also reads CHANGELOG.md and embeds the latest release notes so the
 * frontend can show "What's New" without an API call.
 */
function versionManifestPlugin() {
  return {
    name: 'version-manifest',
    closeBundle() {
      // Parse latest release notes from CHANGELOG.md
      let releaseNotes = [];
      try {
        const changelogPath = resolve(__dirname, '..', 'CHANGELOG.md');
        if (existsSync(changelogPath)) {
          const raw = readFileSync(changelogPath, 'utf-8');
          // Extract sections between ## headers
          const sections = raw.split(/^## /m).slice(1); // skip preamble
          for (const section of sections.slice(0, 3)) { // latest 3 releases
            const lines = section.split('\n');
            const titleLine = lines[0].trim();
            const match = titleLine.match(/\[(.+?)\](?:\s*-\s*(.+))?/);
            const version = match ? match[1] : titleLine;
            const date = match && match[2] ? match[2].trim() : '';
            const body = lines.slice(1).join('\n').trim();
            // Parse changes into structured items
            const changes = [];
            let currentCategory = '';
            for (const line of body.split('\n')) {
              const catMatch = line.match(/^### (.+)/);
              if (catMatch) { currentCategory = catMatch[1]; continue; }
              const itemMatch = line.match(/^- (.+)/);
              if (itemMatch) {
                changes.push({ category: currentCategory, text: itemMatch[1] });
              }
            }
            if (version !== 'Unreleased' || changes.length > 0) {
              releaseNotes.push({ version, date, changes });
            }
          }
        }
      } catch { /* non-fatal */ }

      const manifest = {
        version: buildMeta.version,
        buildHash: buildMeta.hash,
        buildTime: buildMeta.time,
        commit: buildMeta.commit,
        releaseNotes,
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
    __BUILD_HASH__: JSON.stringify(buildMeta.hash),
    __BUILD_TIME__: JSON.stringify(buildMeta.time),
    __APP_VERSION__: JSON.stringify(buildMeta.version),
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
