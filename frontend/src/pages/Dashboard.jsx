/**
 * PATH: frontend/src/pages/Dashboard.jsx
 * PURPOSE: Premium dashboard with animated stats, gradient cards, and glow effects
 */

import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  Atom,
  Brain,
  GitBranch,
  GitCommit,
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
  Play,
  Rocket,
  Shield,
  Wrench,
  Star,
  ChevronRight,
} from 'lucide-react';
import { clsx } from 'clsx';
import { API_BASE } from '../config';

/* ------------------------------------------------------------------ */
/*  Animated counter hook                                              */
/* ------------------------------------------------------------------ */
function useAnimatedCount(target, duration = 1200) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const started = useRef(false);

  useEffect(() => {
    if (target === 0 || started.current) return;
    if (typeof target === 'string') { setCount(target); return; }
    started.current = true;
    const startTime = performance.now();
    const animate = (now) => {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [target, duration]);

  return count;
}

/* ------------------------------------------------------------------ */
/*  Stat card with gradient accent bar                                 */
/* ------------------------------------------------------------------ */
function StatCard({ title, value, change, icon: Icon, gradient, borderColor }) {
  const animatedValue = useAnimatedCount(typeof value === 'number' ? value : 0);

  return (
    <div className="card group relative overflow-hidden">
      {/* Top accent bar */}
      <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${gradient} opacity-80 group-hover:opacity-100 transition-opacity`} />
      <div className="flex items-start justify-between pt-2">
        <div>
          <p className="text-sm text-slate-500 font-medium mb-1">{title}</p>
          <p className="text-3xl font-black text-slate-900 tabular-nums">
            {typeof value === 'number' ? animatedValue : value}
          </p>
          {change && (
            <div className="flex items-center gap-1 mt-2">
              <TrendingUp size={13} className="text-emerald-500" />
              <span className="text-xs text-emerald-600 font-semibold">{change}</span>
            </div>
          )}
        </div>
        <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg`}>
          <Icon size={22} className="text-white" />
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Quick action with hover glow                                       */
/* ------------------------------------------------------------------ */
function QuickAction({ title, description, icon: Icon, to, gradient }) {
  return (
    <Link
      to={to}
      className="card-hover group flex items-center gap-4"
    >
      <div className={clsx(
        'w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-300 group-hover:scale-110 group-hover:shadow-lg bg-gradient-to-br',
        gradient
      )}>
        <Icon size={22} className="text-white" />
      </div>
      <div className="flex-1">
        <h3 className="font-semibold text-slate-800 group-hover:text-slate-900 transition-colors">
          {title}
        </h3>
        <p className="text-sm text-slate-400">{description}</p>
      </div>
      <ArrowRight size={18} className="text-slate-300 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all" />
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/*  Activity timeline                                                  */
/* ------------------------------------------------------------------ */
function RecentActivity({ activities }) {
  const typeConfig = {
    simulation: { icon: Atom, bg: 'bg-blue-50', text: 'text-blue-500', dot: 'bg-blue-400' },
    rule: { icon: Database, bg: 'bg-violet-50', text: 'text-violet-500', dot: 'bg-violet-400' },
    evolution: { icon: GitBranch, bg: 'bg-emerald-50', text: 'text-emerald-500', dot: 'bg-emerald-400' },
    error: { icon: AlertCircle, bg: 'bg-red-50', text: 'text-red-500', dot: 'bg-red-400' },
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-slate-800">Recent Activity</h3>
        <Link to="/logs" className="text-sm text-indigo-500 hover:text-indigo-600 font-medium transition-colors">
          View all
        </Link>
      </div>
      <div className="space-y-1">
        {activities.map((activity, i) => {
          const config = typeConfig[activity.type] || typeConfig.simulation;
          const TypeIcon = config.icon;
          return (
            <div key={i} className="flex items-start gap-3 py-2.5 relative">
              {/* Timeline line */}
              {i < activities.length - 1 && (
                <div className="absolute left-[15px] top-10 bottom-0 w-px bg-slate-100" />
              )}
              <div className={clsx('w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 relative z-10', config.bg, config.text)}>
                <TypeIcon size={15} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-slate-600 truncate">{activity.message}</p>
                <p className="text-xs text-slate-400 mt-0.5">{activity.time}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  System status                                                      */
/* ------------------------------------------------------------------ */
function SystemStatus({ status }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-slate-800">System Status</h3>
        <span className={clsx(
          'px-3 py-1 rounded-full text-xs font-bold',
          status.overall === 'healthy'
            ? 'bg-emerald-50 text-emerald-600'
            : 'bg-amber-50 text-amber-600'
        )}>
          {status.overall === 'healthy' ? 'All Operational' : 'Degraded'}
        </span>
      </div>
      <div className="space-y-2">
        {status.components.map((component, i) => (
          <div key={i} className="flex items-center justify-between py-2.5 border-b border-slate-50 last:border-0">
            <div className="flex items-center gap-3">
              <component.icon size={16} className="text-slate-400" />
              <span className="text-sm text-slate-600 font-medium">{component.name}</span>
            </div>
            <div className="flex items-center gap-3">
              {component.status === 'operational' ? (
                <CheckCircle2 size={14} className="text-emerald-500" />
              ) : (
                <AlertCircle size={14} className="text-amber-500" />
              )}
              <span className="text-xs text-slate-400 font-mono tabular-nums">{component.latency}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  What's New — changelog + commits from API                          */
/* ------------------------------------------------------------------ */
const categoryIcon = {
  Features: Rocket,
  Added: Rocket,
  Improvements: Star,
  Changed: Star,
  Fixes: Wrench,
  Fixed: Wrench,
  Security: Shield,
  default: ChevronRight,
};
const categoryColor = {
  Features: 'text-indigo-500 bg-indigo-50',
  Added: 'text-indigo-500 bg-indigo-50',
  Improvements: 'text-amber-500 bg-amber-50',
  Changed: 'text-amber-500 bg-amber-50',
  Fixes: 'text-emerald-500 bg-emerald-50',
  Fixed: 'text-emerald-500 bg-emerald-50',
  Security: 'text-red-500 bg-red-50',
  default: 'text-slate-500 bg-slate-50',
};

function WhatsNew({ changelog, commits, loading }) {
  const [tab, setTab] = useState('notes');

  // Combine changelog changes + generated notes for display
  const changes = [];
  if (changelog?.latest_release?.changes) {
    changes.push(...changelog.latest_release.changes);
  }
  if (changelog?.generated_notes?.[0]?.changes) {
    changes.push(...changelog.generated_notes[0].changes);
  }
  // Deduplicate by text
  const seen = new Set();
  const uniqueChanges = changes.filter(c => {
    const key = c.text?.toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  const recentCommits = (changelog?.recent_commits || commits || []).slice(0, 8);
  const version = changelog?.latest_release?.version || '';
  const releaseDate = changelog?.latest_release?.date || '';

  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-5 bg-slate-100 rounded w-32 mb-4" />
        <div className="space-y-3">
          <div className="h-4 bg-slate-50 rounded w-full" />
          <div className="h-4 bg-slate-50 rounded w-3/4" />
          <div className="h-4 bg-slate-50 rounded w-5/6" />
        </div>
      </div>
    );
  }

  if (!uniqueChanges.length && !recentCommits.length) return null;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
            <Sparkles size={14} className="text-white" />
          </div>
          <div>
            <h3 className="font-bold text-slate-800">What&apos;s New</h3>
            {version && (
              <p className="text-[10px] text-slate-400 font-medium">
                v{version}{releaseDate ? ` · ${releaseDate}` : ''}
              </p>
            )}
          </div>
        </div>
        <div className="flex rounded-lg bg-slate-100 p-0.5">
          {['notes', 'commits'].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={clsx(
                'px-3 py-1 rounded-md text-xs font-semibold transition-all',
                tab === t
                  ? 'bg-white text-slate-800 shadow-sm'
                  : 'text-slate-400 hover:text-slate-600'
              )}
            >
              {t === 'notes' ? 'Release Notes' : 'Commits'}
            </button>
          ))}
        </div>
      </div>

      {tab === 'notes' && uniqueChanges.length > 0 && (
        <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
          {uniqueChanges.slice(0, 12).map((item, i) => {
            const Icon = categoryIcon[item.category] || categoryIcon.default;
            const color = categoryColor[item.category] || categoryColor.default;
            return (
              <div key={i} className="flex items-start gap-2.5 py-1.5">
                <div className={clsx('w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5', color)}>
                  <Icon size={12} />
                </div>
                <div className="flex-1 min-w-0">
                  {item.category && (
                    <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mr-2">
                      {item.category}
                    </span>
                  )}
                  <p className="text-sm text-slate-600 leading-relaxed">{item.text}</p>
                </div>
              </div>
            );
          })}
          {uniqueChanges.length > 12 && (
            <p className="text-xs text-slate-400 text-center pt-1">
              +{uniqueChanges.length - 12} more changes
            </p>
          )}
        </div>
      )}

      {tab === 'notes' && uniqueChanges.length === 0 && (
        <p className="text-sm text-slate-400 text-center py-6">
          No release notes yet — check the commits tab
        </p>
      )}

      {tab === 'commits' && recentCommits.length > 0 && (
        <div className="space-y-1 max-h-64 overflow-y-auto pr-1">
          {recentCommits.map((c, i) => (
            <div key={c.sha || i} className="flex items-start gap-2.5 py-2 group">
              <div className="w-6 h-6 rounded-lg bg-slate-50 flex items-center justify-center flex-shrink-0 mt-0.5 text-slate-400 group-hover:text-slate-600">
                <GitCommit size={12} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-slate-600 truncate">{c.message}</p>
                <div className="flex items-center gap-2 mt-0.5">
                  <code className="text-[10px] font-mono text-indigo-400 bg-indigo-50 px-1.5 py-0.5 rounded">
                    {c.short_sha}
                  </code>
                  <span className="text-[10px] text-slate-400">
                    {c.author}{c.date ? ` · ${c.date.slice(0, 10)}` : ''}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === 'commits' && recentCommits.length === 0 && (
        <p className="text-sm text-slate-400 text-center py-6">
          No recent commits found
        </p>
      )}
    </div>
  );
}

/* ================================================================== */
/*  Dashboard                                                          */
/* ================================================================== */
export default function Dashboard() {
  const [stats, setStats] = useState({ simulations: 0, rules: 0, evolutions: 0, uptime: '0h' });
  const [activities, setActivities] = useState([]);
  const [systemStatus, setSystemStatus] = useState({
    overall: 'unknown',
    components: [
      { name: 'Neurosymbolic Engine', icon: Brain, status: 'checking', latency: '--' },
      { name: 'Rule Engine', icon: Database, status: 'checking', latency: '--' },
      { name: 'Physics Solver', icon: Atom, status: 'checking', latency: '--' },
      { name: 'Evolution Module', icon: GitBranch, status: 'checking', latency: '--' },
    ]
  });
  const [demoMode, setDemoMode] = useState(false);
  const [changelog, setChangelog] = useState(null);
  const [changelogLoading, setChangelogLoading] = useState(true);

  useEffect(() => {
    let failed = 0;

    // Fetch changelog / What's New data
    const fetchChangelog = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/changelog/latest`);
        if (res.ok) {
          const data = await res.json();
          if (data.success) setChangelog(data);
        }
      } catch { /* non-fatal */ }
      finally { setChangelogLoading(false); }
    };
    fetchChangelog();

    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/system/stats`);
        if (res.ok) {
          const data = await res.json();
          setStats({
            simulations: data.simulations ?? 0,
            rules: data.rules ?? 0,
            evolutions: data.evolutions ?? 0,
            uptime: data.uptime ?? '0h',
          });
        } else { failed++; }
      } catch { failed++; }
    };

    const fetchActivity = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/cot/logs?limit=5`);
        if (res.ok) {
          const data = await res.json();
          if (data.logs?.length) {
            setActivities(data.logs.map(l => ({
              type: l.type || 'simulation',
              message: l.message || l.action || 'Activity',
              time: l.timestamp || '',
            })));
          } else { failed++; }
        } else { failed++; }
      } catch { failed++; }
    };

    const fetchHealth = async () => {
      try {
        const start = Date.now();
        const res = await fetch(`${API_BASE}/health`);
        const latency = Date.now() - start;
        if (res.ok) {
          setSystemStatus({
            overall: 'healthy',
            components: [
              { name: 'Neurosymbolic Engine', icon: Brain, status: 'operational', latency: `${latency}ms` },
              { name: 'Rule Engine', icon: Database, status: 'operational', latency: `${latency}ms` },
              { name: 'Physics Solver', icon: Atom, status: 'operational', latency: `${latency}ms` },
              { name: 'Evolution Module', icon: GitBranch, status: 'operational', latency: `${latency}ms` },
            ]
          });
        } else { failed++; }
      } catch { failed++; }
    };

    Promise.all([fetchStats(), fetchActivity(), fetchHealth()]).then(() => {
      if (failed >= 3) {
        setDemoMode(true);
        setStats({ simulations: 127, rules: 24, evolutions: 8, uptime: '72h 15m' });
        setActivities([
          { type: 'simulation', message: 'Harmonic oscillator simulation completed', time: '2 minutes ago' },
          { type: 'rule', message: 'New rule "kinetic_energy" added', time: '15 minutes ago' },
          { type: 'evolution', message: 'Code evolution cycle completed', time: '1 hour ago' },
          { type: 'simulation', message: 'Pendulum simulation ran for 10s', time: '2 hours ago' },
        ]);
        setSystemStatus({
          overall: 'healthy',
          components: [
            { name: 'Neurosymbolic Engine', icon: Brain, status: 'operational', latency: '12ms' },
            { name: 'Rule Engine', icon: Database, status: 'operational', latency: '8ms' },
            { name: 'Physics Solver', icon: Atom, status: 'operational', latency: '45ms' },
            { name: 'Evolution Module', icon: GitBranch, status: 'operational', latency: '23ms' },
          ]
        });
      }
    });
  }, []);

  return (
    <div className="space-y-6">
      {/* Demo banner */}
      {demoMode && (
        <div className="p-3 bg-amber-50 border border-amber-200/50 rounded-xl text-amber-700 text-sm flex items-center gap-2 font-medium">
          <AlertCircle size={16} />
          Running in demo mode — start the backend for live data
        </div>
      )}

      {/* Welcome banner with mesh gradient */}
      <div className="relative rounded-2xl overflow-hidden p-8">
        <div className="mesh-bg absolute inset-0" />
        <div className="absolute inset-0 bg-gradient-to-r from-white/40 to-transparent" />
        <div className="relative flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-black text-slate-900 mb-1">
              Welcome to Beyond Frontier
            </h1>
            <p className="text-slate-500 font-medium">
              Your neurosymbolic engine is ready for exploration
            </p>
          </div>
          <Link
            to="/chat"
            className="btn-fancy px-6 py-3"
          >
            <Sparkles size={18} />
            Start Chat
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Simulations"
          value={stats.simulations}
          change="+12% this week"
          icon={Atom}
          gradient="from-blue-500 to-indigo-600"
        />
        <StatCard
          title="Active Rules"
          value={stats.rules}
          change="+3 new rules"
          icon={Database}
          gradient="from-violet-500 to-purple-600"
        />
        <StatCard
          title="Evolution Cycles"
          value={stats.evolutions}
          icon={GitBranch}
          gradient="from-emerald-500 to-teal-600"
        />
        <StatCard
          title="System Uptime"
          value={stats.uptime}
          icon={Activity}
          gradient="from-amber-500 to-orange-600"
        />
      </div>

      {/* Quick Actions + Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-3">
          <h2 className="text-lg font-bold text-slate-800">Quick Actions</h2>
          <QuickAction
            title="Run Simulation"
            description="Real-time physics visualization"
            icon={Play}
            to="/simulations"
            gradient="from-blue-500 to-indigo-600"
          />
          <QuickAction
            title="Chat with AI"
            description="Natural language physics interface"
            icon={MessageSquare}
            to="/chat"
            gradient="from-indigo-500 to-violet-600"
          />
          <QuickAction
            title="Solve Equations"
            description="Symbolic solver with derivations"
            icon={BookOpen}
            to="/equations"
            gradient="from-violet-500 to-purple-600"
          />
          <QuickAction
            title="Manage Rules"
            description="Create and edit inference rules"
            icon={Database}
            to="/rules"
            gradient="from-amber-500 to-orange-600"
          />
        </div>

        <div className="space-y-4">
          <WhatsNew changelog={changelog} loading={changelogLoading} />
          <RecentActivity activities={activities} />
          <SystemStatus status={systemStatus} />
        </div>
      </div>
    </div>
  );
}
