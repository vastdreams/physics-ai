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

export default function Header({ sidebarCollapsed, onToggleSidebar, title, subtitle, rightActions }) {
  const [isConnected, setIsConnected] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <header className="h-14 bg-light-50/80 backdrop-blur-xl border-b border-light-200 flex items-center justify-between px-4 sticky top-0 z-40 flex-shrink-0">
      {/* Left Section */}
      <div className="flex items-center gap-4">
        <button 
          onClick={onToggleSidebar}
          className="p-2 hover:bg-light-200 rounded-lg transition-colors text-light-500 hover:text-light-700"
        >
          {sidebarCollapsed ? <PanelLeft size={20} /> : <PanelLeftClose size={20} />}
        </button>
        
        <div>
          <h2 className="font-semibold text-light-900">{title || 'Dashboard'}</h2>
          {subtitle && (
            <p className="text-xs text-light-500">{subtitle}</p>
          )}
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-2">
        {/* Status Indicator */}
        <div className={clsx(
          'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm',
          isConnected ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'
        )}>
          {isConnected ? <Wifi size={14} /> : <WifiOff size={14} />}
          <span className="text-xs font-medium">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        {/* Activity */}
        <button className="p-2 hover:bg-light-200 rounded-lg transition-colors text-light-500 hover:text-light-700 relative">
          <Activity size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-accent-primary rounded-full animate-pulse" />
        </button>

        {/* Refresh */}
        <button 
          onClick={handleRefresh}
          className="p-2 hover:bg-light-200 rounded-lg transition-colors text-light-500 hover:text-light-700"
        >
          <RefreshCw size={18} className={clsx(isRefreshing && 'animate-spin')} />
        </button>

        {/* Notifications */}
        <button className="p-2 hover:bg-light-200 rounded-lg transition-colors text-light-500 hover:text-light-700 relative">
          <Bell size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-accent-purple rounded-full" />
        </button>

        {/* Divider */}
        {rightActions && (
          <div className="w-px h-6 bg-light-300 mx-1" />
        )}

        {/* Custom Right Actions */}
        {rightActions}
      </div>
    </header>
  );
}
