/**
 * PATH: frontend/src/components/HotReloadIndicator.jsx
 * PURPOSE: Visual indicator for hot reload status
 *
 * WHY: Shows developers when modules are being reloaded and any errors,
 *      providing immediate feedback during development.
 */

import { useState, useEffect } from 'react';
import { RefreshCw, Check, X, Zap } from 'lucide-react';
import { useHotReload } from '../hooks/useHotReload';

export function HotReloadIndicator({ compact = false }) {
  const { status, recentReloads, triggerReload } = useHotReload();
  const [showDetails, setShowDetails] = useState(false);
  const [reloading, setReloading] = useState(false);
  const [lastReload, setLastReload] = useState(null);

  // Flash indicator when reload happens
  useEffect(() => {
    if (recentReloads.length > 0) {
      const latest = recentReloads[0];
      if (!lastReload || latest.timestamp > lastReload.timestamp) {
        setLastReload(latest);
        setReloading(true);
        setTimeout(() => setReloading(false), 1000);
      }
    }
  }, [recentReloads, lastReload]);

  if (!status.enabled) {
    return null; // Don't show if hot reload is disabled
  }

  const handleManualReload = async () => {
    setReloading(true);
    await triggerReload();
    setTimeout(() => setReloading(false), 500);
  };

  if (compact) {
    return (
      <button
        onClick={handleManualReload}
        className={`
          flex items-center gap-1 px-2 py-1 rounded text-xs
          transition-all duration-200
          ${reloading 
            ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' 
            : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
          }
        `}
        title="Hot Reload Active - Click to refresh all modules"
      >
        <Zap className={`w-3 h-3 ${reloading ? 'animate-pulse' : ''}`} />
        <span>HMR</span>
      </button>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setShowDetails(!showDetails)}
        className={`
          flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm
          transition-all duration-200
          ${reloading 
            ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 animate-pulse' 
            : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
          }
        `}
      >
        <Zap className={`w-4 h-4 ${status.running ? 'text-yellow-500' : ''}`} />
        <span>Hot Reload</span>
        {status.totalReloads > 0 && (
          <span className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs">
            {status.totalReloads}
          </span>
        )}
      </button>

      {showDetails && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4 z-50">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-gray-900 dark:text-white">Hot Reload Status</h3>
            <button
              onClick={handleManualReload}
              className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
              title="Reload all modules"
            >
              <RefreshCw className={`w-4 h-4 ${reloading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500 dark:text-gray-400">Watched Files</span>
              <span className="font-mono">{status.watchedFiles}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500 dark:text-gray-400">Total Reloads</span>
              <span className="font-mono text-green-600">{status.totalReloads}</span>
            </div>
            {status.failedReloads > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Failed</span>
                <span className="font-mono text-red-600">{status.failedReloads}</span>
              </div>
            )}
          </div>

          {recentReloads.length > 0 && (
            <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
              <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
                Recent Reloads
              </h4>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {recentReloads.slice(0, 5).map((reload, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 text-xs py-1"
                  >
                    {reload.success ? (
                      <Check className="w-3 h-3 text-green-500" />
                    ) : (
                      <X className="w-3 h-3 text-red-500" />
                    )}
                    <span className="font-mono truncate flex-1" title={reload.module}>
                      {reload.module.split('.').pop()}
                    </span>
                    {reload.reloadTime && (
                      <span className="text-gray-400">
                        {reload.reloadTime.toFixed(0)}ms
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default HotReloadIndicator;
