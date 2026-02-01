/**
 * PATH: frontend/src/hooks/useHotReload.js
 * PURPOSE: React hook for monitoring backend hot reload status
 *
 * WHY: Provides real-time updates when backend modules are reloaded,
 *      enabling automatic UI refresh without manual page reload.
 */

import { useState, useEffect, useCallback } from 'react';
import { io } from 'socket.io-client';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5002';

/**
 * Hook for monitoring and controlling hot reload
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
  const [socket, setSocket] = useState(null);

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
    } catch (err) {
      console.warn('Failed to fetch hot reload status:', err);
    }
  }, []);

  // Setup WebSocket connection for real-time updates
  useEffect(() => {
    const ws = io(API_BASE, {
      transports: ['websocket'],
      autoConnect: true,
    });

    ws.on('connect', () => {
      console.log('Connected to hot reload WebSocket');
    });

    ws.on('module_reloaded', (data) => {
      console.log('Module reloaded:', data.module);
      
      // Add to recent reloads
      setRecentReloads((prev) => [
        {
          module: data.module,
          timestamp: new Date(data.timestamp),
          success: true,
          reloadTime: data.reload_time_ms,
        },
        ...prev.slice(0, 9), // Keep last 10
      ]);

      // Update status
      setStatus((prev) => ({
        ...prev,
        totalReloads: prev.totalReloads + 1,
      }));

      // Trigger custom event for components to handle
      window.dispatchEvent(new CustomEvent('physicsai:module-reload', { 
        detail: data 
      }));
    });

    ws.on('module_reload_failed', (data) => {
      console.error('Module reload failed:', data.module, data.error);
      
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

    setSocket(ws);
    fetchStatus();

    return () => {
      ws.disconnect();
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
      console.error('Failed to trigger reload:', err);
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
      console.error('Failed to toggle auto-reload:', err);
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
 * Hook for auto-refreshing data when relevant modules reload
 */
export function useAutoRefresh(modules, onRefresh) {
  useEffect(() => {
    const handleReload = (event) => {
      const { module } = event.detail;
      
      // Check if the reloaded module is relevant
      const isRelevant = modules.some((m) => 
        module.startsWith(m) || module.includes(m)
      );
      
      if (isRelevant && onRefresh) {
        console.log(`Auto-refreshing due to ${module} reload`);
        onRefresh();
      }
    };

    window.addEventListener('physicsai:module-reload', handleReload);
    
    return () => {
      window.removeEventListener('physicsai:module-reload', handleReload);
    };
  }, [modules, onRefresh]);
}

export default useHotReload;
