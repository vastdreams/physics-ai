/**
 * PATH: frontend/src/components/UpdateBanner.jsx
 * PURPOSE: Non-intrusive banner shown when a new build is detected.
 *
 * Slides in from the bottom and lets the user either refresh now or dismiss.
 */

import { RefreshCw, X } from 'lucide-react';
import useAutoUpdate from '../hooks/useAutoUpdate';

export default function UpdateBanner() {
  const { updateAvailable, latestVersion, reload, dismiss } = useAutoUpdate();

  if (!updateAvailable) return null;

  return (
    <div className="fixed bottom-4 left-1/2 z-[9999] -translate-x-1/2 animate-slide-up">
      <div className="flex items-center gap-3 rounded-xl border border-indigo-500/30 bg-indigo-950/90 px-5 py-3 text-sm text-indigo-100 shadow-2xl backdrop-blur-lg">
        <RefreshCw size={16} className="shrink-0 animate-spin-slow text-indigo-400" />
        <span>
          A new version{latestVersion ? ` (${latestVersion})` : ''} is available.
        </span>
        <button
          onClick={reload}
          className="rounded-lg bg-indigo-600 px-3 py-1 text-xs font-semibold text-white transition hover:bg-indigo-500"
        >
          Refresh now
        </button>
        <button
          onClick={dismiss}
          className="ml-1 rounded p-1 text-indigo-400 transition hover:bg-indigo-800 hover:text-indigo-200"
          aria-label="Dismiss"
        >
          <X size={14} />
        </button>
      </div>
    </div>
  );
}
