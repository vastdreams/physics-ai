/**
 * PATH: frontend/src/components/layout/Layout.jsx
 * PURPOSE: Main layout wrapper with sidebar and header
 */

import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { clsx } from 'clsx';

const pageTitles = {
  '/': { title: 'Dashboard', subtitle: 'System overview and quick actions' },
  '/chat': { title: 'AI Chat', subtitle: 'Conversational physics interface' },
  '/simulations': { title: 'Simulations', subtitle: 'Run and visualize physics simulations' },
  '/equations': { title: 'Equations', subtitle: 'Symbolic equation solver' },
  '/models': { title: 'Physics Models', subtitle: 'Available simulation models' },
  '/rules': { title: 'Rule Engine', subtitle: 'Manage inference rules' },
  '/evolution': { title: 'Evolution', subtitle: 'Self-evolution and code analysis' },
  '/reasoning': { title: 'Reasoning', subtitle: 'Logical reasoning types' },
  '/logs': { title: 'System Logs', subtitle: 'Chain-of-thought and activity logs' },
  '/metrics': { title: 'Metrics', subtitle: 'Performance and usage metrics' },
  '/settings': { title: 'Settings', subtitle: 'System configuration' },
};

export default function Layout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();
  
  const pageInfo = pageTitles[location.pathname] || { title: 'Physics AI', subtitle: '' };

  return (
    <div className="min-h-screen bg-dark-950">
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} 
      />
      
      <main className={clsx(
        'transition-all duration-300',
        sidebarCollapsed ? 'ml-16' : 'ml-64'
      )}>
        <Header 
          sidebarCollapsed={sidebarCollapsed}
          onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
          title={pageInfo.title}
          subtitle={pageInfo.subtitle}
        />
        
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
