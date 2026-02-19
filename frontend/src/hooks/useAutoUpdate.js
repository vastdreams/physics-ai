/**
 * PATH: frontend/src/hooks/useAutoUpdate.js
 * PURPOSE: Poll /version.json to detect new builds + expose release notes.
 *
 * The build hash is shared between the Vite `define` and the version.json
 * manifest, so a mismatch genuinely means a new deployment happened.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

/* Globals injected by vite.config.js — same hash written to version.json */
const CURRENT_BUILD = typeof __BUILD_HASH__ !== 'undefined' ? __BUILD_HASH__ : null;
const CURRENT_VERSION = typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : '';

/** Poll interval: 60s in prod, disabled in dev */
const POLL_INTERVAL = import.meta.env.PROD ? 60_000 : 0;

/**
 * @returns {{
 *   updateAvailable: boolean,
 *   latestVersion: string|null,
 *   currentVersion: string,
 *   releaseNotes: Array<{version:string, date:string, changes:Array}>,
 *   reload: () => void,
 *   dismiss: () => void,
 * }}
 */
export default function useAutoUpdate() {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [latestVersion, setLatestVersion] = useState(null);
  const [releaseNotes, setReleaseNotes] = useState([]);
  const timerRef = useRef(null);

  const check = useCallback(async () => {
    if (!CURRENT_BUILD) return;

    try {
      const res = await fetch(`/version.json?_=${Date.now()}`, {
        cache: 'no-store',
        headers: { 'Cache-Control': 'no-cache' },
      });
      if (!res.ok) return;

      const data = await res.json();

      // Always grab release notes (useful for "What's New" even if no update)
      if (data.releaseNotes?.length) {
        setReleaseNotes(data.releaseNotes);
      }

      if (data.buildHash && data.buildHash !== CURRENT_BUILD) {
        setUpdateAvailable(true);
        setLatestVersion(data.version || null);
      }
    } catch {
      // Network error — silent retry next interval
    }
  }, []);

  useEffect(() => {
    // Always do an initial fetch for release notes (even in dev)
    const initialDelay = setTimeout(check, 2_000);

    if (POLL_INTERVAL) {
      timerRef.current = setInterval(check, POLL_INTERVAL);
    }

    return () => {
      clearTimeout(initialDelay);
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [check]);

  /** Hard reload — bust the service worker & browser cache */
  const reload = useCallback(() => {
    // Unregister any service workers that might cache the old build
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistrations().then((regs) => {
        regs.forEach((r) => r.unregister());
      });
    }
    // Cache-busting reload
    window.location.href = window.location.pathname + '?v=' + Date.now();
  }, []);

  const dismiss = useCallback(() => {
    setUpdateAvailable(false);
  }, []);

  return {
    updateAvailable,
    latestVersion,
    currentVersion: CURRENT_VERSION,
    releaseNotes,
    reload,
    dismiss,
  };
}
