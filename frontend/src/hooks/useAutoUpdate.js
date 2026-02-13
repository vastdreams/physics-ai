/**
 * PATH: frontend/src/hooks/useAutoUpdate.js
 * PURPOSE: Poll /version.json to detect when a new build is deployed.
 *
 * When a mismatch is detected the hook exposes `updateAvailable = true`
 * so the UI can show a non-intrusive refresh banner.
 *
 * The build hash is injected at compile time by Vite via `define`.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

/* globals injected by vite.config.js */
const CURRENT_BUILD = typeof __BUILD_HASH__ !== 'undefined' ? __BUILD_HASH__ : null;

/** How often to poll (ms).  Default: 60 s in production, never in dev. */
const POLL_INTERVAL = import.meta.env.PROD ? 60_000 : 0;

export default function useAutoUpdate() {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [latestVersion, setLatestVersion] = useState(null);
  const timerRef = useRef(null);

  const check = useCallback(async () => {
    // Don't poll during development or if we have no build hash
    if (!CURRENT_BUILD) return;

    try {
      // Cache-bust so CDNs and browsers don't serve the old manifest
      const res = await fetch(`/version.json?_=${Date.now()}`, {
        cache: 'no-store',
      });
      if (!res.ok) return;

      const data = await res.json();
      if (data.buildHash && data.buildHash !== CURRENT_BUILD) {
        setUpdateAvailable(true);
        setLatestVersion(data.version || null);
      }
    } catch {
      // Network error — silent. We'll retry on the next interval.
    }
  }, []);

  useEffect(() => {
    if (!POLL_INTERVAL) return;

    // Initial check after a short delay (let the app settle)
    const initialDelay = setTimeout(check, 5_000);

    // Recurring checks
    timerRef.current = setInterval(check, POLL_INTERVAL);

    return () => {
      clearTimeout(initialDelay);
      clearInterval(timerRef.current);
    };
  }, [check]);

  const reload = useCallback(() => {
    window.location.reload();
  }, []);

  const dismiss = useCallback(() => {
    setUpdateAvailable(false);
  }, []);

  return { updateAvailable, latestVersion, reload, dismiss };
}
