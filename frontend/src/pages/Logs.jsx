/**
 * PATH: frontend/src/pages/Logs.jsx
 * PURPOSE: Real-time system logs with WebSocket streaming
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Terminal,
  Filter,
  Search,
  Download,
  Trash2,
  RefreshCw,
  ChevronDown,
  AlertCircle,
  Info,
  AlertTriangle,
  Bug,
  Wifi,
  WifiOff,
  Pause,
  Play
} from 'lucide-react';
import { clsx } from 'clsx';
import { io } from 'socket.io-client';
import { API_BASE } from '../config';

const logLevels = {
  debug: { icon: Bug, color: 'text-gray-500', bg: 'bg-gray-50', border: 'border-gray-300' },
  info: { icon: Info, color: 'text-blue-500', bg: 'bg-blue-50', border: 'border-blue-400' },
  warn: { icon: AlertTriangle, color: 'text-yellow-500', bg: 'bg-yellow-50', border: 'border-yellow-400' },
  error: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-50', border: 'border-red-400' },
};

function LogEntry({ log }) {
  const [expanded, setExpanded] = useState(false);
  const level = logLevels[log.level] || logLevels.info;
  const Icon = level.icon;

  return (
    <div 
      className={clsx(
        'border-l-2 pl-4 py-2 hover:bg-light-100 cursor-pointer transition-colors',
        level.border
      )}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start gap-3">
        <div className={clsx('w-6 h-6 rounded flex items-center justify-center flex-shrink-0', level.bg)}>
          <Icon size={14} className={level.color} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5 flex-wrap">
            <span className="text-xs text-light-400 font-mono">{log.timestamp}</span>
            <span className={clsx('text-xs font-medium px-1.5 py-0.5 rounded', level.bg, level.color)}>
              {log.level.toUpperCase()}
            </span>
            <span className="text-xs text-light-500 font-medium">{log.source}</span>
          </div>
          <p className="text-sm text-light-700 font-mono break-words">{log.message}</p>
          {expanded && log.details && (
            <pre className="mt-2 p-3 bg-light-900 text-light-100 rounded-lg text-xs overflow-x-auto">
              {JSON.stringify(log.details, null, 2)}
            </pre>
          )}
        </div>
        {log.details && (
          <ChevronDown 
            size={14} 
            className={clsx(
              'text-light-400 transition-transform flex-shrink-0',
              expanded && 'rotate-180'
            )} 
          />
        )}
      </div>
    </div>
  );
}

export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isStreaming, setIsStreaming] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [stats, setStats] = useState({ total: 0, by_level: {} });
  
  const socketRef = useRef(null);
  const logsEndRef = useRef(null);

  // Fetch initial logs
  const fetchLogs = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/logs?limit=200`);
      const data = await res.json();
      if (data.success) {
        setLogs(data.logs.reverse()); // Oldest first for display
      }
    } catch (err) {
      console.error('Failed to fetch logs:', err);
    }
  }, []);

  // Fetch stats
  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/logs/stats`);
      const data = await res.json();
      if (data.success) {
        setStats(data.stats);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  }, []);

  // Use ref for isStreaming so socket handler doesn't need it as a dependency
  const isStreamingRef = useRef(isStreaming);
  useEffect(() => { isStreamingRef.current = isStreaming; }, [isStreaming]);

  // Setup WebSocket connection — only if backend is reachable
  useEffect(() => {
    let cancelled = false;
    fetchLogs();
    fetchStats();

    async function connectSocket() {
      // Probe backend before creating socket
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 3000);
        const res = await fetch(`${API_BASE}/health`, { signal: controller.signal });
        clearTimeout(timeout);
        if (!res.ok || cancelled) return;
      } catch {
        return; // Backend not reachable — skip socket entirely
      }

      const socket = io(API_BASE, {
        transports: ['websocket'],
        reconnectionAttempts: 3,
        reconnectionDelay: 3000,
        reconnectionDelayMax: 10000,
        timeout: 5000,
      });

      socket.on('connect', () => {
        setIsConnected(true);
      });

      socket.on('disconnect', () => {
        setIsConnected(false);
      });

      socket.on('log_entry', (entry) => {
        if (isStreamingRef.current) {
          setLogs((prev) => [...prev.slice(-499), entry]);
          setStats((prev) => ({
            ...prev,
            total: prev.total + 1,
            by_level: {
              ...prev.by_level,
              [entry.level]: (prev.by_level[entry.level] || 0) + 1,
            },
          }));
        }
      });

      socketRef.current = socket;
    }

    connectSocket();

    return () => {
      cancelled = true;
      if (socketRef.current) {
        socketRef.current.disconnect();
        socketRef.current = null;
      }
    };
  }, [fetchLogs, fetchStats]);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (isStreaming && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, isStreaming]);

  // Filter logs
  const filteredLogs = logs.filter((log) => {
    if (filter !== 'all' && log.level !== filter) return false;
    if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const handleClear = async () => {
    try {
      await fetch(`${API_BASE}/api/v1/logs/clear`, { method: 'POST' });
      setLogs([]);
      setStats({ total: 0, by_level: {} });
    } catch (err) {
      console.error('Failed to clear logs:', err);
    }
  };

  const handleExport = () => {
    const data = JSON.stringify(logs, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `beyondfrontier-logs-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
  };

  const handleRefresh = () => {
    fetchLogs();
    fetchStats();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-xl font-semibold text-light-900 flex items-center gap-2">
            <Terminal size={24} className="text-accent-primary" />
            System Logs
          </h1>
          <p className="text-light-500 text-sm">
            {stats.total} total entries | {filteredLogs.length} showing
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {/* Connection Status */}
          <div className={clsx(
            'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm',
            isConnected ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'
          )}>
            {isConnected ? <Wifi size={14} /> : <WifiOff size={14} />}
            <span className="text-xs font-medium">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* Stream Toggle */}
          <button 
            onClick={() => setIsStreaming(!isStreaming)}
            className={clsx(
              'btn-secondary flex items-center gap-2',
              isStreaming && 'border-green-400 bg-green-50'
            )}
          >
            {isStreaming ? <Pause size={14} /> : <Play size={14} />}
            <div className={clsx(
              'w-2 h-2 rounded-full',
              isStreaming ? 'bg-green-400 animate-pulse' : 'bg-light-400'
            )} />
            {isStreaming ? 'Live' : 'Paused'}
          </button>

          <button onClick={handleRefresh} className="btn-secondary flex items-center gap-2">
            <RefreshCw size={16} />
            Refresh
          </button>
          <button onClick={handleExport} className="btn-secondary flex items-center gap-2">
            <Download size={16} />
            Export
          </button>
          <button 
            onClick={handleClear} 
            className="btn-secondary flex items-center gap-2 text-red-500 hover:text-red-600 hover:border-red-300"
          >
            <Trash2 size={16} />
            Clear
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="card py-3">
          <p className="text-2xl font-bold text-light-800">{stats.total}</p>
          <p className="text-xs text-light-500">Total</p>
        </div>
        {['debug', 'info', 'warn', 'error'].map((level) => {
          const config = logLevels[level];
          const Icon = config.icon;
          return (
            <div key={level} className={clsx('card py-3', config.bg)}>
              <div className="flex items-center gap-2">
                <Icon size={16} className={config.color} />
                <p className={clsx('text-2xl font-bold', config.color)}>
                  {stats.by_level?.[level] || 0}
                </p>
              </div>
              <p className="text-xs text-light-500 capitalize">{level}</p>
            </div>
          );
        })}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-light-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search logs..."
            className="input pl-10"
          />
        </div>
        <div className="flex items-center gap-1 p-1 bg-light-200 rounded-lg">
          {['all', 'debug', 'info', 'warn', 'error'].map((level) => (
            <button
              key={level}
              onClick={() => setFilter(level)}
              className={clsx(
                'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                filter === level
                  ? 'bg-white text-light-800 shadow-sm'
                  : 'text-light-500 hover:text-light-700'
              )}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Logs */}
      <div className="card p-0 overflow-hidden">
        <div className="bg-light-100 px-4 py-2 border-b border-light-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal size={16} className="text-light-500" />
            <span className="text-sm text-light-500">Log Stream</span>
          </div>
          {isStreaming && (
            <span className="flex items-center gap-1 text-xs text-green-600">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
              Streaming
            </span>
          )}
        </div>
        <div className="max-h-[600px] overflow-y-auto divide-y divide-light-100">
          {filteredLogs.map((log) => (
            <LogEntry key={log.id} log={log} />
          ))}
          <div ref={logsEndRef} />
          {filteredLogs.length === 0 && (
            <div className="py-12 text-center text-light-400">
              <Terminal size={48} className="mx-auto mb-3 opacity-50" />
              <p>No logs to display</p>
              <p className="text-sm mt-1">Logs will appear here in real-time</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
