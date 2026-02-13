/**
 * PATH: frontend/src/config.js
 * PURPOSE: Centralized configuration — single source of truth for all runtime values.
 *
 * Every component/hook/page should import from here instead of
 * hardcoding URLs, ports, or feature flags.
 *
 * Values are resolved in this order:
 *   1. Vite env vars (VITE_*)  — set in .env or CI
 *   2. Sensible development defaults
 */

/** Base URL for the backend API (no trailing slash). */
export const API_BASE =
  import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:5002' : '');

/**
 * When running in production behind a reverse-proxy the frontend and API
 * share the same origin, so API_BASE is '' (empty string) and all fetch
 * calls become relative (e.g. `/api/v1/...`).
 *
 * During development, Vite's proxy (vite.config.js) forwards /api and
 * /socket.io to the Flask backend at localhost:5002, so we can also use
 * '' in dev if the proxy is active.  The explicit fallback is kept for
 * cases where someone runs the frontend without the proxy.
 */

/** WebSocket URL for Socket.IO connections. */
export const WS_BASE = import.meta.env.VITE_WS_URL || API_BASE;

/** App version (injected at build time by Vite). */
export const BUILD_HASH = typeof __BUILD_HASH__ !== 'undefined' ? __BUILD_HASH__ : 'dev';
export const BUILD_TIME = typeof __BUILD_TIME__ !== 'undefined' ? __BUILD_TIME__ : '';
