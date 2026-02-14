/**
 * PATH: frontend/src/pages/Evolution.jsx
 * PURPOSE: Self-evolution tracking and management interface
 */

import { useState, useEffect } from 'react';
import {
  GitBranch,
  GitCommit,
  Play,
  Pause,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Clock,
  Code,
  TrendingUp,
  Zap
} from 'lucide-react';
import { clsx } from 'clsx';
import { API_BASE } from '../config';

function EvolutionCard({ evolution }) {
  return (
    <div className="card">
      <div className="flex items-start gap-4">
        <div className={clsx(
          'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0',
          evolution.status === 'completed' && 'bg-green-50 text-green-500',
          evolution.status === 'running' && 'bg-blue-50 text-blue-500',
          evolution.status === 'failed' && 'bg-red-50 text-red-500',
          evolution.status === 'pending' && 'bg-yellow-50 text-yellow-500'
        )}>
          {evolution.status === 'completed' && <CheckCircle2 size={20} />}
          {evolution.status === 'running' && <GitBranch size={20} className="animate-pulse" />}
          {evolution.status === 'failed' && <AlertCircle size={20} />}
          {evolution.status === 'pending' && <Clock size={20} />}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-medium text-light-800">{evolution.name}</h3>
            <span className={clsx(
              'badge text-[10px]',
              evolution.status === 'completed' && 'badge-green',
              evolution.status === 'running' && 'badge-blue',
              evolution.status === 'failed' && 'bg-red-100 text-red-600',
              evolution.status === 'pending' && 'badge-yellow'
            )}>
              {evolution.status}
            </span>
          </div>
          <p className="text-sm text-light-500 mb-2">{evolution.description}</p>
          <div className="flex items-center gap-4 text-xs text-light-400">
            <span className="flex items-center gap-1">
              <Code size={12} />
              {evolution.file}
            </span>
            <span className="flex items-center gap-1">
              <Clock size={12} />
              {evolution.timestamp}
            </span>
            {evolution.improvement && (
              <span className="flex items-center gap-1 text-green-500">
                <TrendingUp size={12} />
                +{evolution.improvement}%
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Evolution() {
  const [evolutions, setEvolutions] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [demoMode, setDemoMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalCycles: 0,
    successRate: 0,
    avgImprovement: 0,
    lastRun: '--'
  });

  const mockEvolutions = [
    { id: 1, name: 'Optimize RuleEngine.match()', description: 'Improved pattern matching algorithm with early termination', file: 'rules/rule_engine.py', status: 'completed', timestamp: '2 hours ago', improvement: 15 },
    { id: 2, name: 'Enhance EquationSolver caching', description: 'Added memoization for repeated equation solutions', file: 'physics/equations.py', status: 'completed', timestamp: '5 hours ago', improvement: 23 },
    { id: 3, name: 'Refactor NeuralComponent.embed()', description: 'Optimizing embedding generation for better performance', file: 'core/engine.py', status: 'running', timestamp: 'In progress' },
    { id: 4, name: 'Add parallel processing to simulations', description: 'Pending review for multi-threaded simulation support', file: 'physics/models.py', status: 'pending', timestamp: 'Queued' },
  ];

  useEffect(() => {
    const fetchEvolution = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/evolution/history`);
        if (res.ok) {
          const data = await res.json();
          const list = data.history || data.evolutions || [];
          setEvolutions(list);
          const completed = list.filter(e => e.status === 'completed');
          setStats({
            totalCycles: list.length,
            successRate: list.length ? Math.round((completed.length / list.length) * 100 * 10) / 10 : 0,
            avgImprovement: completed.length
              ? Math.round(completed.reduce((s, e) => s + (e.improvement || 0), 0) / completed.length * 10) / 10
              : 0,
            lastRun: list.length ? (list[0].timestamp || '--') : '--',
          });
        } else { throw new Error(); }
      } catch {
        setDemoMode(true);
        setEvolutions(mockEvolutions);
        setStats({ totalCycles: 8, successRate: 87.5, avgImprovement: 12.3, lastRun: '2 hours ago' });
      } finally {
        setLoading(false);
      }
    };
    fetchEvolution();
  }, []);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/evolution/analyze`, { method: 'POST' });
      if (res.ok) { /* refresh */ }
    } catch { /* ok */ }
    setTimeout(() => setIsAnalyzing(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-light-900">Self-Evolution</h1>
          <p className="text-light-500 text-sm">AI-driven code improvement and optimization</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn-secondary flex items-center gap-2">
            <RotateCcw size={16} />
            View History
          </button>
          <button 
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="btn-primary flex items-center gap-2"
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                Analyzing...
              </>
            ) : (
              <>
                <Zap size={16} />
                Run Analysis
              </>
            )}
          </button>
        </div>
      </div>

      {demoMode && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-sm flex items-center gap-2">
          <AlertCircle size={16} />
          Running in demo mode — start the backend for live data
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-sm text-light-500 mb-1">Total Cycles</p>
          <p className="text-2xl font-semibold text-light-900">{stats.totalCycles}</p>
        </div>
        <div className="card">
          <p className="text-sm text-light-500 mb-1">Success Rate</p>
          <p className="text-2xl font-semibold text-green-500">{stats.successRate}%</p>
        </div>
        <div className="card">
          <p className="text-sm text-light-500 mb-1">Avg Improvement</p>
          <p className="text-2xl font-semibold text-accent-primary">+{stats.avgImprovement}%</p>
        </div>
        <div className="card">
          <p className="text-sm text-light-500 mb-1">Last Run</p>
          <p className="text-2xl font-semibold text-light-800">{stats.lastRun}</p>
        </div>
      </div>

      {/* Evolution List */}
      <div className="space-y-3">
        <h2 className="text-lg font-medium text-light-800">Recent Evolutions</h2>
        {evolutions.map((evolution) => (
          <EvolutionCard key={evolution.id} evolution={evolution} />
        ))}
      </div>
    </div>
  );
}
