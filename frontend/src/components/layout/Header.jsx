/**
 * PATH: frontend/src/components/layout/Header.jsx
 * PURPOSE: Premium glass header with status indicators and actions
 */

import { useState } from 'react';
import { clsx } from 'clsx';
import {
  PanelLeftClose,
  PanelLeft,
  Bell,
  Wifi,
  WifiOff,
  Activity,
  RefreshCw,
} from 'lucide-react';

import { HotReloadIndicator } from '../HotReloadIndicator';

/**
 * Top header with frosted glass, gradient accents, and status.
 */
export default function Header({ sidebarCollapsed, onToggleSidebar, title, subtitle, rightActions }) {
  const [isConnected, setIsConnected] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <header className="h-14 bg-white/70 backdrop-blur-xl border-b border-slate-200/50 flex items-center justify-between px-5 sticky top-0 z-40 flex-shrink-0">
      {/* Left */}
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          className="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-400 hover:text-slate-600"
        >
          {sidebarCollapsed ? <PanelLeft size={20} /> : <PanelLeftClose size={20} />}
        </button>

        <div>
          <h2 className="font-bold text-slate-900 tracking-tight">{title || 'Dashboard'}</h2>
          {subtitle && (
            <p className="text-xs text-slate-400">{subtitle}</p>
          )}
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-2">
        {/* Connection status */}
        <div className={clsx(
          'flex items-center gap-2 px-3 py-1.5 rounded-full text-sm transition-colors',
          isConnected ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-500'
        )}>
          {isConnected ? <Wifi size={13} /> : <WifiOff size={13} />}
          <span className="text-xs font-semibold">
            {isConnected ? 'Connected' : 'Offline'}
          </span>
        </div>

        {/* Activity */}
        <button className="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-400 hover:text-slate-600 relative">
          <Activity size={18} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-full animate-pulse" />
        </button>

        {/* Hot Reload */}
        <HotReloadIndicator compact />

        {/* Refresh */}
        <button
          onClick={handleRefresh}
          className="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-400 hover:text-slate-600"
          title="Refresh"
        >
          <RefreshCw size={18} className={clsx(isRefreshing && 'animate-spin')} />
        </button>

        {/* Notifications */}
        <button className="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-400 hover:text-slate-600 relative">
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-gradient-to-br from-violet-500 to-pink-500 rounded-full" />
        </button>

        {/* Divider */}
        {rightActions && (
          <div className="w-px h-6 bg-slate-200 mx-1" />
        )}

        {rightActions}
      </div>
    </header>
  );
}
