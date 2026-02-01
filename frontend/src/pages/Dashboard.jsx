/**
 * PATH: frontend/src/pages/Dashboard.jsx
 * PURPOSE: Main dashboard with system overview, quick actions, and stats
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Atom,
  Brain,
  GitBranch,
  Activity,
  Zap,
  BookOpen,
  MessageSquare,
  ArrowRight,
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  Cpu,
  Database,
  Sparkles,
  Play
} from 'lucide-react';
import { clsx } from 'clsx';

function StatCard({ title, value, change, icon: Icon, color }) {
  const colors = {
    green: 'from-green-500 to-emerald-600',
    blue: 'from-blue-500 to-indigo-600',
    purple: 'from-purple-500 to-violet-600',
    orange: 'from-orange-500 to-amber-600',
  };

  return (
    <div className="card group hover:border-dark-600 transition-all">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-dark-400 mb-1">{title}</p>
          <p className="text-2xl font-semibold text-dark-100">{value}</p>
          {change && (
            <div className="flex items-center gap-1 mt-2">
              <TrendingUp size={14} className="text-green-400" />
              <span className="text-xs text-green-400">{change}</span>
            </div>
          )}
        </div>
        <div className={clsx(
          'w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center',
          colors[color]
        )}>
          <Icon size={24} className="text-white" />
        </div>
      </div>
    </div>
  );
}

function QuickAction({ title, description, icon: Icon, to, color }) {
  return (
    <Link
      to={to}
      className="card-hover group flex items-center gap-4"
    >
      <div className={clsx(
        'w-12 h-12 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110',
        color
      )}>
        <Icon size={24} className="text-white" />
      </div>
      <div className="flex-1">
        <h3 className="font-medium text-dark-100 group-hover:text-white transition-colors">
          {title}
        </h3>
        <p className="text-sm text-dark-400">{description}</p>
      </div>
      <ArrowRight size={18} className="text-dark-500 group-hover:text-dark-300 group-hover:translate-x-1 transition-all" />
    </Link>
  );
}

function RecentActivity({ activities }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-dark-100">Recent Activity</h3>
        <Link to="/logs" className="text-sm text-accent-primary hover:underline">
          View all
        </Link>
      </div>
      <div className="space-y-3">
        {activities.map((activity, i) => (
          <div key={i} className="flex items-start gap-3 py-2">
            <div className={clsx(
              'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
              activity.type === 'simulation' && 'bg-blue-500/20 text-blue-400',
              activity.type === 'rule' && 'bg-purple-500/20 text-purple-400',
              activity.type === 'evolution' && 'bg-green-500/20 text-green-400',
              activity.type === 'error' && 'bg-red-500/20 text-red-400',
            )}>
              {activity.type === 'simulation' && <Atom size={16} />}
              {activity.type === 'rule' && <Database size={16} />}
              {activity.type === 'evolution' && <GitBranch size={16} />}
              {activity.type === 'error' && <AlertCircle size={16} />}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-dark-200 truncate">{activity.message}</p>
              <p className="text-xs text-dark-500">{activity.time}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SystemStatus({ status }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-dark-100">System Status</h3>
        <span className={clsx(
          'badge',
          status.overall === 'healthy' ? 'badge-green' : 'badge-yellow'
        )}>
          {status.overall === 'healthy' ? 'All Systems Operational' : 'Degraded'}
        </span>
      </div>
      <div className="space-y-3">
        {status.components.map((component, i) => (
          <div key={i} className="flex items-center justify-between py-2">
            <div className="flex items-center gap-2">
              <component.icon size={16} className="text-dark-400" />
              <span className="text-sm text-dark-300">{component.name}</span>
            </div>
            <div className="flex items-center gap-2">
              {component.status === 'operational' ? (
                <CheckCircle2 size={14} className="text-green-400" />
              ) : (
                <AlertCircle size={14} className="text-yellow-400" />
              )}
              <span className="text-xs text-dark-400">{component.latency}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState({
    simulations: 0,
    rules: 0,
    evolutions: 0,
    uptime: '0h',
  });

  const [activities] = useState([
    { type: 'simulation', message: 'Harmonic oscillator simulation completed', time: '2 minutes ago' },
    { type: 'rule', message: 'New rule "kinetic_energy" added', time: '15 minutes ago' },
    { type: 'evolution', message: 'Code evolution cycle completed', time: '1 hour ago' },
    { type: 'simulation', message: 'Pendulum simulation ran for 10s', time: '2 hours ago' },
  ]);

  const [systemStatus] = useState({
    overall: 'healthy',
    components: [
      { name: 'Neurosymbolic Engine', icon: Brain, status: 'operational', latency: '12ms' },
      { name: 'Rule Engine', icon: Database, status: 'operational', latency: '8ms' },
      { name: 'Physics Solver', icon: Atom, status: 'operational', latency: '45ms' },
      { name: 'Evolution Module', icon: GitBranch, status: 'operational', latency: '23ms' },
    ]
  });

  useEffect(() => {
    // Fetch stats from API
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:5002/api/v1/rules/statistics');
        if (response.ok) {
          const data = await response.json();
          setStats(prev => ({ ...prev, rules: data.total_rules || 0 }));
        }
      } catch (error) {
        console.log('API not available, using mock data');
      }
    };
    fetchStats();

    // Simulate stats loading
    setStats({
      simulations: 127,
      rules: 24,
      evolutions: 8,
      uptime: '72h 15m',
    });
  }, []);

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="card bg-gradient-to-r from-dark-800 to-dark-850 border-dark-700 overflow-hidden relative">
        <div className="absolute inset-0 bg-gradient-to-r from-accent-primary/10 to-accent-purple/10" />
        <div className="relative flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-dark-100 mb-1">
              Welcome back to Physics AI
            </h1>
            <p className="text-dark-400">
              Your neurosymbolic engine is ready for exploration
            </p>
          </div>
          <Link
            to="/chat"
            className="btn-primary flex items-center gap-2"
          >
            <Sparkles size={18} />
            Start Chat
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Simulations"
          value={stats.simulations}
          change="+12% this week"
          icon={Atom}
          color="blue"
        />
        <StatCard
          title="Active Rules"
          value={stats.rules}
          change="+3 new rules"
          icon={Database}
          color="purple"
        />
        <StatCard
          title="Evolution Cycles"
          value={stats.evolutions}
          icon={GitBranch}
          color="green"
        />
        <StatCard
          title="System Uptime"
          value={stats.uptime}
          icon={Activity}
          color="orange"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="space-y-3">
          <h2 className="text-lg font-medium text-dark-100">Quick Actions</h2>
          <QuickAction
            title="Run Simulation"
            description="Execute physics simulations with real-time visualization"
            icon={Play}
            to="/simulations"
            color="bg-gradient-to-br from-blue-500 to-indigo-600"
          />
          <QuickAction
            title="Chat with AI"
            description="Natural language interface for physics queries"
            icon={MessageSquare}
            to="/chat"
            color="bg-gradient-to-br from-accent-primary to-emerald-600"
          />
          <QuickAction
            title="Solve Equations"
            description="Symbolic equation solver with step-by-step solutions"
            icon={BookOpen}
            to="/equations"
            color="bg-gradient-to-br from-purple-500 to-violet-600"
          />
          <QuickAction
            title="Manage Rules"
            description="Create and manage inference rules"
            icon={Database}
            to="/rules"
            color="bg-gradient-to-br from-orange-500 to-amber-600"
          />
        </div>

        <div className="space-y-4">
          <RecentActivity activities={activities} />
          <SystemStatus status={systemStatus} />
        </div>
      </div>
    </div>
  );
}
