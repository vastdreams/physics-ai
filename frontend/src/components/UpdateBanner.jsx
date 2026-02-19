/**
 * PATH: frontend/src/components/UpdateBanner.jsx
 * PURPOSE: Non-intrusive banner for new builds + expandable release notes.
 *
 * Light-themed to match the rest of the UI. Shows version number,
 * a "What changed" toggle, and a hard-refresh button.
 */

import { useState } from 'react';
import { RefreshCw, X, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import useAutoUpdate from '../hooks/useAutoUpdate';

export default function UpdateBanner() {
  const { updateAvailable, latestVersion, releaseNotes, reload, dismiss } = useAutoUpdate();
  const [expanded, setExpanded] = useState(false);

  if (!updateAvailable) return null;

  // Show the first release's changes as a compact summary
  const latest = releaseNotes?.[0];
  const summaryItems = latest?.changes?.slice(0, 5) || [];

  return (
    <div className="fixed bottom-4 left-1/2 z-[9999] -translate-x-1/2 w-[min(95vw,460px)] animate-slide-up">
      <div className="rounded-2xl border border-indigo-200/60 bg-white/95 shadow-2xl shadow-indigo-100/50 backdrop-blur-xl overflow-hidden">
        {/* Main row */}
        <div className="flex items-center gap-3 px-5 py-3.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center flex-shrink-0">
            <Sparkles size={14} className="text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-slate-800">
              Version {latestVersion || 'new'} available
            </p>
            <p className="text-xs text-slate-400 truncate">New features and improvements</p>
          </div>
          {summaryItems.length > 0 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              aria-label="Toggle changes"
            >
              {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
          )}
          <button
            onClick={reload}
            className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 px-4 py-2 text-xs font-bold text-white shadow-md shadow-indigo-200/50 transition hover:shadow-lg hover:scale-[1.02]"
          >
            <RefreshCw size={12} />
            Update
          </button>
          <button
            onClick={dismiss}
            className="p-1.5 rounded-lg text-slate-300 hover:text-slate-500 hover:bg-slate-100 transition-colors"
            aria-label="Dismiss"
          >
            <X size={14} />
          </button>
        </div>

        {/* Expandable release notes */}
        {expanded && summaryItems.length > 0 && (
          <div className="px-5 pb-4 pt-1 border-t border-slate-100">
            <p className="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-2">
              What&apos;s new in {latest.version}
            </p>
            <ul className="space-y-1">
              {summaryItems.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-slate-600">
                  <span className="mt-1.5 w-1 h-1 rounded-full bg-indigo-400 flex-shrink-0" />
                  <span>
                    {item.category && (
                      <span className="font-semibold text-indigo-500">{item.category}: </span>
                    )}
                    {item.text}
                  </span>
                </li>
              ))}
              {latest.changes.length > 5 && (
                <li className="text-xs text-slate-400 pl-3">
                  +{latest.changes.length - 5} more changes
                </li>
              )}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
