/**
 * PATH: frontend/src/pages/Metrics.jsx
 * PURPOSE: Performance and usage metrics dashboard
 */

import { useState, useEffect } from 'react';

import { clsx } from 'clsx';
import {
  Activity,
  Cpu,
  Clock,
  TrendingUp,
  TrendingDown,
  Database,
  AlertCircle,
} from 'lucide-react';
import {
  LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar,
} from 'recharts';

import { API_BASE } from '../config';

/** Shared Recharts tooltip styling used across all chart components. */
const TOOLTIP_STYLE = {
  backgroundColor: '#ffffff',
  border: '1px solid #e5e5e5',
  borderRadius: '8px',
  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
};

// Generate mock data (fallback)
const generateTimeData = () => {
  return Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    requests: Math.floor(Math.random() * 100) + 20,
    latency: Math.floor(Math.random() * 50) + 10,
    errors: Math.floor(Math.random() * 5),
  }));
};

const generateComponentData = () => [
  { name: 'Engine', cpu: 45, memory: 62 },
  { name: 'Rules', cpu: 23, memory: 38 },
  { name: 'Solver', cpu: 67, memory: 45 },
  { name: 'Evolution', cpu: 12, memory: 28 },
  { name: 'API', cpu: 34, memory: 41 },
];

/**
 * @param {Object} props
 * @param {string} props.title - Metric label
 * @param {string|number} props.value - Metric value
 * @param {string} [props.change] - Change description
 * @param {import('lucide-react').LucideIcon} props.icon - Icon component
 * @param {'up'|'down'} [props.trend] - Trend direction
 * @param {string} [props.unit] - Value suffix (e.g. "ms", "%")
 */
function MetricCard({ title, value, change, icon: Icon, trend, unit = '' }) {
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-light-500 mb-1">{title}</p>
          <p className="text-2xl font-semibold text-light-900">
            {value}{unit}
          </p>
          {change && (
            <div className={clsx(
              'flex items-center gap-1 mt-2 text-sm',
              trend === 'up' ? 'text-green-500' : 'text-red-500'
            )}>
              {trend === 'up' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
              {change}
            </div>
          )}
        </div>
        <div className="w-10 h-10 rounded-lg bg-light-200 flex items-center justify-center">
          <Icon size={20} className="text-light-600" />
        </div>
      </div>
    </div>
  );
}

/** System metrics dashboard — charts and stats for performance monitoring. */
export default function Metrics() {
  const [timeData, setTimeData] = useState(generateTimeData);
  const [componentData, setComponentData] = useState(generateComponentData);
  const [timeRange, setTimeRange] = useState('24h');
  const [demoMode, setDemoMode] = useState(false);
  const [liveStats, setLiveStats] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const [healthRes, statsRes] = await Promise.all([
          fetch(`${API_BASE}/health`).catch(() => null),
          fetch(`${API_BASE}/api/v1/system/stats`).catch(() => null),
        ]);
        if (healthRes?.ok) {
          const hData = await healthRes.json();
          setLiveStats(prev => ({ ...prev, version: hData.version, build: hData.build }));
        }
        if (statsRes?.ok) {
          const sData = await statsRes.json();
          setLiveStats(prev => ({ ...prev, rules: sData.rules, uptime: sData.uptime }));
        }
        if (!healthRes?.ok && !statsRes?.ok) setDemoMode(true);
      } catch {
        setDemoMode(true);
      }
    };
    fetchMetrics();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-light-900">System Metrics</h1>
          <p className="text-light-500 text-sm">Performance and usage analytics</p>
        </div>
        <div className="flex items-center gap-1 p-1 bg-light-200 rounded-lg">
          {['1h', '6h', '24h', '7d'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={clsx(
                'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                timeRange === range
                  ? 'bg-white text-light-800 shadow-sm'
                  : 'text-light-500 hover:text-light-700'
              )}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {demoMode && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-sm flex items-center gap-2">
          <AlertCircle size={16} />
          Running in demo mode — start the backend for live metrics
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Avg Response Time"
          value="23"
          unit="ms"
          change="-12% from last hour"
          icon={Clock}
          trend="up"
        />
        <MetricCard
          title="Requests/Min"
          value="156"
          change="+8% from last hour"
          icon={Activity}
          trend="up"
        />
        <MetricCard
          title="CPU Usage"
          value="34"
          unit="%"
          icon={Cpu}
        />
        <MetricCard
          title="Active Rules"
          value="24"
          change="+3 this week"
          icon={Database}
          trend="up"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Request Volume */}
        <div className="card">
          <h3 className="font-medium text-light-800 mb-4">Request Volume</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeData}>
                <defs>
                  <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10a37f" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#10a37f" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                <XAxis dataKey="time" stroke="#737373" fontSize={12} />
                <YAxis stroke="#737373" fontSize={12} />
                <Tooltip contentStyle={TOOLTIP_STYLE} />
                <Area 
                  type="monotone" 
                  dataKey="requests" 
                  stroke="#10a37f" 
                  fillOpacity={1} 
                  fill="url(#colorRequests)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Latency */}
        <div className="card">
          <h3 className="font-medium text-light-800 mb-4">Response Latency (ms)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                <XAxis dataKey="time" stroke="#737373" fontSize={12} />
                <YAxis stroke="#737373" fontSize={12} />
                <Tooltip contentStyle={TOOLTIP_STYLE} />
                <Line 
                  type="monotone" 
                  dataKey="latency" 
                  stroke="#5436da" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Component Usage */}
      <div className="card">
        <h3 className="font-medium text-light-800 mb-4">Component Resource Usage</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={componentData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
              <XAxis type="number" stroke="#737373" fontSize={12} />
              <YAxis dataKey="name" type="category" stroke="#737373" fontSize={12} width={80} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  border: '1px solid #e5e5e5',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                }}
              />
              <Bar dataKey="cpu" fill="#10a37f" name="CPU %" radius={[0, 4, 4, 0]} />
              <Bar dataKey="memory" fill="#5436da" name="Memory %" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
