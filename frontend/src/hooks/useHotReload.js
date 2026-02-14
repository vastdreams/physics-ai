/**
 * PATH: frontend/src/hooks/useHotReload.js
 * PURPOSE: React hook for monitoring backend hot reload status
 *
 * WHY: Provides real-time updates when backend modules are reloaded,
 *      enabling automatic UI refresh without manual page reload.
 *      Only connects WebSocket when backend is confirmed reachable.
 */

import { useState, useEffect, useCallback, useRef } from 'react';

import { io } from 'socket.io-client';

import { API_BASE } from '../config';

/**
 * Probe the backend with a lightweight fetch. Returns true if reachable.
 */
async function isBackendReachable() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);
    const res = await fetch(`${API_BASE}/health`, { signal: controller.signal });
    clearTimeout(timeout);
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * Hook for monitoring and controlling hot reload.
 * WebSocket is only created after confirming the backend is reachable.
 */
export function useHotReload() {
  const [status, setStatus] = useState({
    enabled: false,
    running: false,
    watchedFiles: 0,
    totalReloads: 0,
    failedReloads: 0,
    uptime: 0,
  });
  
  const [recentReloads, setRecentReloads] = useState([]);
  const socketRef = useRef(null);

  // Fetch initial status
  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/hot-reload/status`);
      const data = await res.json();
      setStatus({
        enabled: data.enabled,
        running: data.running,
        watchedFiles: data.watched_files || 0,
        totalReloads: data.total_reloads || 0,
        failedReloads: data.failed_reloads || 0,
        uptime: data.uptime_seconds || 0,
        autoReload: data.auto_reload !== false,
      });
    } catch {
      // Backend not available — silently ignore
    }
  }, []);

  // Only connect WebSocket if backend is reachable
  useEffect(() => {
    let cancelled = false;

    async function connect() {
      const reachable = await isBackendReachable();
      if (cancelled || !reachable) return;

      const ws = io(API_BASE, {
        transports: ['websocket'],
        reconnectionAttempts: 3,
        reconnectionDelay: 3000,
        reconnectionDelayMax: 15000,
        timeout: 5000,
      });

      ws.on('module_reloaded', (data) => {
        setRecentReloads((prev) => [
          {
            module: data.module,
            timestamp: new Date(data.timestamp),
            success: true,
            reloadTime: data.reload_time_ms,
          },
          ...prev.slice(0, 9),
        ]);

        setStatus((prev) => ({
          ...prev,
          totalReloads: prev.totalReloads + 1,
        }));

        window.dispatchEvent(new CustomEvent('beyondfrontier:module-reload', { 
          detail: data 
        }));
      });

      ws.on('module_reload_failed', (data) => {
        setRecentReloads((prev) => [
          {
            module: data.module,
            timestamp: new Date(),
            success: false,
            error: data.error,
          },
          ...prev.slice(0, 9),
        ]);

        setStatus((prev) => ({
          ...prev,
          failedReloads: prev.failedReloads + 1,
        }));
      });

      socketRef.current = ws;
      fetchStatus();
    }

    connect();

    return () => {
      cancelled = true;
      if (socketRef.current) {
        socketRef.current.disconnect();
        socketRef.current = null;
      }
    };
  }, [fetchStatus]);

  // Trigger manual reload
  const triggerReload = useCallback(async (moduleName = null) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/hot-reload/reload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(moduleName ? { module: moduleName } : {}),
      });
      const data = await res.json();
      
      if (data.success) {
        fetchStatus();
      }
      
      return data;
    } catch (err) {
      return { success: false, error: err.message };
    }
  }, [fetchStatus]);

  // Toggle auto-reload
  const toggleAutoReload = useCallback(async (enabled) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/hot-reload/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled }),
      });
      const data = await res.json();
      
      if (data.success) {
        setStatus((prev) => ({ ...prev, autoReload: data.auto_reload }));
      }
      
      return data;
    } catch (err) {
      return { success: false, error: err.message };
    }
  }, []);

  return {
    status,
    recentReloads,
    triggerReload,
    toggleAutoReload,
    refetch: fetchStatus,
  };
}

/**
 * Hook for auto-refreshing data when relevant modules reload.
 * @param {string[]} modules - Module prefixes to watch
 * @param {Function} onRefresh - Callback invoked when a matching module reloads
 */
export function useAutoRefresh(modules, onRefresh) {
  useEffect(() => {
    const handleReload = (event) => {
      const { module } = event.detail;
      
      const isRelevant = modules.some((m) => 
        module.startsWith(m) || module.includes(m)
      );
      
      if (isRelevant && onRefresh) {
        onRefresh();
      }
    };

    window.addEventListener('beyondfrontier:module-reload', handleReload);
    
    return () => {
      window.removeEventListener('beyondfrontier:module-reload', handleReload);
    };
  }, [modules, onRefresh]);
}

export default useHotReload;
