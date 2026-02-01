/**
 * PATH: frontend/src/components/layout/Header.jsx
 * PURPOSE: Top header bar with breadcrumbs, status indicators, and actions
 */

import { useState } from 'react';
import { 
  PanelLeftClose, 
  PanelLeft,
  Bell,
  Wifi,
  WifiOff,
  Activity,
  Moon,
  Sun,
  RefreshCw
} from 'lucide-react';
import { clsx } from 'clsx';

export default function Header({ sidebarCollapsed, onToggleSidebar, title, subtitle }) {
  const [isConnected, setIsConnected] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <header className="h-14 bg-dark-900/80 backdrop-blur-xl border-b border-dark-800 flex items-center justify-between px-4 sticky top-0 z-40">
      {/* Left Section */}
      <div className="flex items-center gap-4">
        <button 
          onClick={onToggleSidebar}
          className="p-2 hover:bg-dark-800 rounded-lg transition-colors text-dark-400 hover:text-dark-200"
        >
          {sidebarCollapsed ? <PanelLeft size={20} /> : <PanelLeftClose size={20} />}
        </button>
        
        <div>
          <h2 className="font-semibold text-dark-100">{title || 'Dashboard'}</h2>
          {subtitle && (
            <p className="text-xs text-dark-500">{subtitle}</p>
          )}
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-2">
        {/* Status Indicator */}
        <div className={clsx(
          'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm',
          isConnected ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
        )}>
          {isConnected ? <Wifi size={14} /> : <WifiOff size={14} />}
          <span className="text-xs font-medium">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        {/* Activity */}
        <button className="p-2 hover:bg-dark-800 rounded-lg transition-colors text-dark-400 hover:text-dark-200 relative">
          <Activity size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-accent-primary rounded-full animate-pulse" />
        </button>

        {/* Refresh */}
        <button 
          onClick={handleRefresh}
          className="p-2 hover:bg-dark-800 rounded-lg transition-colors text-dark-400 hover:text-dark-200"
        >
          <RefreshCw size={18} className={clsx(isRefreshing && 'animate-spin')} />
        </button>

        {/* Notifications */}
        <button className="p-2 hover:bg-dark-800 rounded-lg transition-colors text-dark-400 hover:text-dark-200 relative">
          <Bell size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-accent-purple rounded-full" />
        </button>
      </div>
    </header>
  );
}
