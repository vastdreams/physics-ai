/**
 * PATH: frontend/src/components/panels/BottomPanel.jsx
 * PURPOSE: Bottom panel with tabs for Console, Terminal, Logs, Problems (Cursor-style)
 * 
 * FEATURES:
 * - Multiple tabs (Console, Output, Logs, Problems)
 * - Real-time log streaming
 * - Command input
 * - Filterable output
 */

import { useState, useRef, useEffect } from 'react';
import {
  Terminal,
  FileText,
  AlertTriangle,
  Play,
  Trash2,
  X,
  ChevronUp,
  ChevronDown,
  Filter,
  Search,
  Copy,
  Check,
  Loader2,
  Info,
  AlertCircle,
  Bug,
  Zap
} from 'lucide-react';
import { clsx } from 'clsx';

const tabs = [
  { id: 'console', label: 'Console', icon: Terminal },
  { id: 'output', label: 'Output', icon: FileText },
  { id: 'logs', label: 'Logs', icon: Info },
  { id: 'problems', label: 'Problems', icon: AlertTriangle },
];

const logLevels = {
  info: { icon: Info, color: 'text-blue-500', bg: 'bg-blue-50' },
  warning: { icon: AlertTriangle, color: 'text-yellow-500', bg: 'bg-yellow-50' },
  error: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-50' },
  debug: { icon: Bug, color: 'text-purple-500', bg: 'bg-purple-50' },
  success: { icon: Zap, color: 'text-green-500', bg: 'bg-green-50' },
};

function ConsoleTab({ onCommand }) {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState([
    { type: 'system', content: 'Physics AI Console v1.0.0' },
    { type: 'system', content: 'Type "help" for available commands' },
  ]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [commandHistory, setCommandHistory] = useState([]);
  const inputRef = useRef(null);
  const outputRef = useRef(null);

  useEffect(() => {
    outputRef.current?.scrollTo(0, outputRef.current.scrollHeight);
  }, [history]);

  const executeCommand = async (cmd) => {
    const trimmed = cmd.trim();
    if (!trimmed) return;

    setHistory(prev => [...prev, { type: 'input', content: `> ${trimmed}` }]);
    setCommandHistory(prev => [...prev, trimmed]);
    setHistoryIndex(-1);
    setInput('');

    // Built-in commands
    if (trimmed === 'help') {
      setHistory(prev => [...prev, {
        type: 'output',
        content: `Available commands:
  help          - Show this help message
  clear         - Clear console
  constants     - List physical constants
  equations     - List available equations
  simulate      - Run a simulation
  status        - System status
  version       - Show version info`
      }]);
      return;
    }

    if (trimmed === 'clear') {
      setHistory([]);
      return;
    }

    if (trimmed === 'version') {
      setHistory(prev => [...prev, { type: 'output', content: 'Physics AI v1.0.0 - Neurosymbolic Engine' }]);
      return;
    }

    // API commands
    try {
      setHistory(prev => [...prev, { type: 'loading', content: 'Executing...' }]);
      
      let endpoint = '/api/v1/knowledge/statistics';
      if (trimmed === 'constants') endpoint = '/api/v1/knowledge/constants';
      else if (trimmed === 'equations') endpoint = '/api/v1/knowledge/equations?limit=10';
      else if (trimmed === 'status') endpoint = '/health';
      
      const response = await fetch(`http://localhost:5002${endpoint}`);
      const data = await response.json();
      
      setHistory(prev => [
        ...prev.slice(0, -1),
        { type: 'output', content: JSON.stringify(data, null, 2) }
      ]);
    } catch (error) {
      setHistory(prev => [
        ...prev.slice(0, -1),
        { type: 'error', content: `Error: ${error.message}` }
      ]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      executeCommand(input);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        const newIndex = historyIndex < commandHistory.length - 1 ? historyIndex + 1 : historyIndex;
        setHistoryIndex(newIndex);
        setInput(commandHistory[commandHistory.length - 1 - newIndex] || '');
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setInput(commandHistory[commandHistory.length - 1 - newIndex] || '');
      } else {
        setHistoryIndex(-1);
        setInput('');
      }
    }
  };

  return (
    <div className="h-full flex flex-col bg-light-900 font-mono text-sm">
      <div ref={outputRef} className="flex-1 overflow-y-auto p-2 space-y-1">
        {history.map((item, i) => (
          <div
            key={i}
            className={clsx(
              'whitespace-pre-wrap',
              item.type === 'input' && 'text-accent-primary',
              item.type === 'output' && 'text-light-300',
              item.type === 'error' && 'text-red-400',
              item.type === 'system' && 'text-light-500 italic',
              item.type === 'loading' && 'text-yellow-400'
            )}
          >
            {item.type === 'loading' && <Loader2 size={12} className="inline animate-spin mr-2" />}
            {item.content}
          </div>
        ))}
      </div>
      <div className="flex items-center gap-2 p-2 border-t border-light-700">
        <span className="text-accent-primary">{'>'}</span>
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter command..."
          className="flex-1 bg-transparent text-light-200 placeholder-light-600 outline-none"
          autoFocus
        />
      </div>
    </div>
  );
}

function OutputTab() {
  const [output, setOutput] = useState([
    { time: '10:23:45', message: 'Physics AI initialized', level: 'info' },
    { time: '10:23:46', message: 'Loaded 122 equations', level: 'success' },
    { time: '10:23:46', message: 'Loaded 45 physical constants', level: 'success' },
    { time: '10:23:47', message: 'API server ready on port 5002', level: 'info' },
  ]);

  return (
    <div className="h-full overflow-y-auto p-2 bg-light-50 font-mono text-xs">
      {output.map((item, i) => {
        const level = logLevels[item.level] || logLevels.info;
        const Icon = level.icon;
        return (
          <div key={i} className="flex items-start gap-2 py-1 hover:bg-light-100 px-1 rounded">
            <span className="text-light-400 flex-shrink-0">{item.time}</span>
            <Icon size={12} className={clsx('flex-shrink-0 mt-0.5', level.color)} />
            <span className="text-light-700">{item.message}</span>
          </div>
        );
      })}
    </div>
  );
}

function LogsTab() {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    // Fetch logs from API
    const fetchLogs = async () => {
      try {
        const response = await fetch('http://localhost:5002/api/v1/cot/logs');
        if (response.ok) {
          const data = await response.json();
          setLogs(data.logs || []);
        }
      } catch (error) {
        setLogs([
          { timestamp: new Date().toISOString(), level: 'info', message: 'Waiting for API connection...' }
        ]);
      }
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  const filteredLogs = filter === 'all' ? logs : logs.filter(l => l.level === filter);

  return (
    <div className="h-full flex flex-col bg-light-50">
      <div className="flex items-center gap-2 px-2 py-1 border-b border-light-200">
        <Filter size={12} className="text-light-400" />
        {['all', 'info', 'warning', 'error'].map(level => (
          <button
            key={level}
            onClick={() => setFilter(level)}
            className={clsx(
              'px-2 py-0.5 text-xs rounded transition-colors',
              filter === level
                ? 'bg-accent-primary text-white'
                : 'text-light-600 hover:bg-light-200'
            )}
          >
            {level}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto p-2 font-mono text-xs">
        {filteredLogs.length === 0 ? (
          <div className="text-light-500 text-center py-4">No logs to display</div>
        ) : (
          filteredLogs.map((log, i) => {
            const level = logLevels[log.level] || logLevels.info;
            const Icon = level.icon;
            return (
              <div key={i} className="flex items-start gap-2 py-1 hover:bg-light-100 px-1 rounded">
                <span className="text-light-400 flex-shrink-0">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <Icon size={12} className={clsx('flex-shrink-0 mt-0.5', level.color)} />
                <span className="text-light-700">{log.message}</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

function ProblemsTab() {
  const [problems, setProblems] = useState([
    { type: 'warning', file: 'physics/equations.py', line: 42, message: 'Unused import: numpy' },
    { type: 'info', file: 'core/engine.py', line: 156, message: 'Consider adding type hints' },
  ]);

  return (
    <div className="h-full overflow-y-auto bg-light-50">
      {problems.length === 0 ? (
        <div className="text-light-500 text-center py-4 text-sm">No problems detected</div>
      ) : (
        <div className="divide-y divide-light-200">
          {problems.map((problem, i) => {
            const level = logLevels[problem.type] || logLevels.info;
            const Icon = level.icon;
            return (
              <div key={i} className="flex items-start gap-2 p-2 hover:bg-light-100 cursor-pointer">
                <Icon size={14} className={clsx('flex-shrink-0 mt-0.5', level.color)} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-light-800">{problem.message}</div>
                  <div className="text-xs text-light-500">
                    {problem.file}:{problem.line}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function BottomPanel({ onClose, onMaximize, isMaximized }) {
  const [activeTab, setActiveTab] = useState('console');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'console': return <ConsoleTab />;
      case 'output': return <OutputTab />;
      case 'logs': return <LogsTab />;
      case 'problems': return <ProblemsTab />;
      default: return null;
    }
  };

  return (
    <div className="h-full flex flex-col bg-white border-t border-light-200">
      {/* Tab Header */}
      <div className="flex items-center justify-between px-2 bg-light-50 border-b border-light-200">
        <div className="flex items-center">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'flex items-center gap-1.5 px-3 py-2 text-xs font-medium border-b-2 transition-colors',
                activeTab === tab.id
                  ? 'text-accent-primary border-accent-primary'
                  : 'text-light-500 border-transparent hover:text-light-700'
              )}
            >
              <tab.icon size={12} />
              {tab.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={onMaximize}
            className="p-1.5 hover:bg-light-200 rounded transition-colors"
            title={isMaximized ? 'Restore' : 'Maximize'}
          >
            {isMaximized ? <ChevronDown size={14} className="text-light-500" /> : <ChevronUp size={14} className="text-light-500" />}
          </button>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-light-200 rounded transition-colors"
            title="Close"
          >
            <X size={14} className="text-light-500" />
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {renderTabContent()}
      </div>
    </div>
  );
}
