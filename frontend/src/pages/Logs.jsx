/**
 * PATH: frontend/src/pages/Logs.jsx
 * PURPOSE: System logs and chain-of-thought visualization
 */

import { useState, useEffect } from 'react';
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
  Clock
} from 'lucide-react';
import { clsx } from 'clsx';

const logLevels = {
  debug: { icon: Bug, color: 'text-gray-400', bg: 'bg-gray-500/10' },
  info: { icon: Info, color: 'text-blue-400', bg: 'bg-blue-500/10' },
  warn: { icon: AlertTriangle, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
  error: { icon: AlertCircle, color: 'text-red-400', bg: 'bg-red-500/10' },
};

function LogEntry({ log }) {
  const [expanded, setExpanded] = useState(false);
  const level = logLevels[log.level] || logLevels.info;
  const Icon = level.icon;

  return (
    <div 
      className={clsx(
        'border-l-2 pl-4 py-2 hover:bg-dark-800/50 cursor-pointer transition-colors',
        log.level === 'error' && 'border-red-500',
        log.level === 'warn' && 'border-yellow-500',
        log.level === 'info' && 'border-blue-500',
        log.level === 'debug' && 'border-gray-500',
      )}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start gap-3">
        <div className={clsx('w-6 h-6 rounded flex items-center justify-center flex-shrink-0', level.bg)}>
          <Icon size={14} className={level.color} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-xs text-dark-500 font-mono">{log.timestamp}</span>
            <span className={clsx('text-xs font-medium', level.color)}>[{log.level.toUpperCase()}]</span>
            <span className="text-xs text-dark-500">{log.source}</span>
          </div>
          <p className="text-sm text-dark-200 font-mono">{log.message}</p>
          {expanded && log.details && (
            <pre className="mt-2 p-2 bg-dark-900 rounded text-xs text-dark-400 overflow-x-auto">
              {JSON.stringify(log.details, null, 2)}
            </pre>
          )}
        </div>
        {log.details && (
          <ChevronDown 
            size={14} 
            className={clsx(
              'text-dark-500 transition-transform flex-shrink-0',
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

  useEffect(() => {
    // Mock logs
    const mockLogs = [
      { id: 1, timestamp: '2026-02-02 10:30:15', level: 'info', source: 'NeurosymboticEngine', message: 'Processing input with hybrid mode', details: { mode: 'hybrid', confidence: 0.85 } },
      { id: 2, timestamp: '2026-02-02 10:30:14', level: 'debug', source: 'RuleEngine', message: 'Rule "kinetic_energy" matched successfully' },
      { id: 3, timestamp: '2026-02-02 10:30:12', level: 'info', source: 'Simulation', message: 'Harmonic oscillator simulation completed', details: { duration: '0.45s', steps: 1001 } },
      { id: 4, timestamp: '2026-02-02 10:30:10', level: 'warn', source: 'Evolution', message: 'Code modification requires approval', details: { file: 'core/engine.py', change_type: 'optimization' } },
      { id: 5, timestamp: '2026-02-02 10:30:08', level: 'error', source: 'API', message: 'WebSocket connection failed', details: { error: 'ECONNREFUSED', retry: true } },
      { id: 6, timestamp: '2026-02-02 10:30:05', level: 'info', source: 'EquationSolver', message: 'Solved F = ma symbolically', details: { solution: 'a = F/m' } },
      { id: 7, timestamp: '2026-02-02 10:30:00', level: 'debug', source: 'NeuralComponent', message: 'Pattern stored with similarity 0.92' },
    ];
    setLogs(mockLogs);
  }, []);

  const filteredLogs = logs.filter(log => {
    if (filter !== 'all' && log.level !== filter) return false;
    if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const handleClear = () => {
    setLogs([]);
  };

  const handleExport = () => {
    const data = JSON.stringify(logs, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'physics-ai-logs.json';
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-dark-100">System Logs</h1>
          <p className="text-dark-400 text-sm">{filteredLogs.length} log entries</p>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={() => setIsStreaming(!isStreaming)}
            className={clsx(
              'btn-secondary flex items-center gap-2',
              isStreaming && 'border-green-500/50'
            )}
          >
            <div className={clsx(
              'w-2 h-2 rounded-full',
              isStreaming ? 'bg-green-400 animate-pulse' : 'bg-dark-500'
            )} />
            {isStreaming ? 'Live' : 'Paused'}
          </button>
          <button onClick={handleExport} className="btn-secondary flex items-center gap-2">
            <Download size={16} />
            Export
          </button>
          <button onClick={handleClear} className="btn-secondary flex items-center gap-2 text-red-400 hover:text-red-300">
            <Trash2 size={16} />
            Clear
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-dark-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search logs..."
            className="input pl-10"
          />
        </div>
        <div className="flex items-center gap-1 p-1 bg-dark-800 rounded-lg">
          {['all', 'debug', 'info', 'warn', 'error'].map((level) => (
            <button
              key={level}
              onClick={() => setFilter(level)}
              className={clsx(
                'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                filter === level
                  ? 'bg-dark-700 text-dark-100'
                  : 'text-dark-400 hover:text-dark-200'
              )}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Logs */}
      <div className="card p-0 overflow-hidden">
        <div className="bg-dark-850 px-4 py-2 border-b border-dark-700 flex items-center gap-2">
          <Terminal size={16} className="text-dark-400" />
          <span className="text-sm text-dark-400">Log Stream</span>
        </div>
        <div className="max-h-[600px] overflow-y-auto divide-y divide-dark-800">
          {filteredLogs.map((log) => (
            <LogEntry key={log.id} log={log} />
          ))}
          {filteredLogs.length === 0 && (
            <div className="py-12 text-center text-dark-500">
              <Terminal size={48} className="mx-auto mb-3 opacity-50" />
              <p>No logs to display</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
