/**
 * PATH: frontend/src/components/layout/Layout.jsx
 * PURPOSE: Main layout wrapper with Cursor-style resizable panels
 * 
 * LAYOUT:
 * ┌──────────┬────────────────────────────┬──────────┐
 * │          │                            │  Right   │
 * │ Sidebar  │      Main Content          │  Drawer  │
 * │          │                            │  (Chat)  │
 * │          ├────────────────────────────┤          │
 * │          │      Bottom Panel          │          │
 * │          │   (Console/Terminal)       │          │
 * └──────────┴────────────────────────────┴──────────┘
 */

import { useState, useCallback } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import ResizablePanel from '../panels/ResizablePanel';
import RightDrawer from '../panels/RightDrawer';
import BottomPanel from '../panels/BottomPanel';
import { clsx } from 'clsx';
import { MessageSquare, Terminal, PanelRight, PanelBottom } from 'lucide-react';

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
  '/about': { title: 'About', subtitle: 'Vision and mission' },
};

export default function Layout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rightDrawerOpen, setRightDrawerOpen] = useState(false);
  const [bottomPanelOpen, setBottomPanelOpen] = useState(false);
  const [rightDrawerMaximized, setRightDrawerMaximized] = useState(false);
  const [bottomPanelMaximized, setBottomPanelMaximized] = useState(false);
  
  // Panel sizes
  const [rightDrawerSize, setRightDrawerSize] = useState(380);
  const [bottomPanelSize, setBottomPanelSize] = useState(250);
  
  const location = useLocation();
  const pageInfo = pageTitles[location.pathname] || { title: 'Physics AI', subtitle: '' };

  const toggleRightDrawer = useCallback(() => {
    setRightDrawerOpen(prev => !prev);
    if (rightDrawerMaximized) setRightDrawerMaximized(false);
  }, [rightDrawerMaximized]);

  const toggleBottomPanel = useCallback(() => {
    setBottomPanelOpen(prev => !prev);
    if (bottomPanelMaximized) setBottomPanelMaximized(false);
  }, [bottomPanelMaximized]);

  const toggleRightDrawerMaximize = useCallback(() => {
    setRightDrawerMaximized(prev => !prev);
  }, []);

  const toggleBottomPanelMaximize = useCallback(() => {
    setBottomPanelMaximized(prev => !prev);
  }, []);

  return (
    <div className="h-screen flex overflow-hidden bg-light-100">
      {/* Sidebar */}
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} 
      />
      
      {/* Main Area (Content + Bottom Panel) */}
      <div className={clsx(
        'flex-1 flex flex-col transition-all duration-300 overflow-hidden',
        sidebarCollapsed ? 'ml-16' : 'ml-64'
      )}>
        {/* Header */}
        <Header 
          sidebarCollapsed={sidebarCollapsed}
          onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
          title={pageInfo.title}
          subtitle={pageInfo.subtitle}
          rightActions={
            <div className="flex items-center gap-1">
              <button
                onClick={toggleBottomPanel}
                className={clsx(
                  'p-2 rounded-lg transition-colors',
                  bottomPanelOpen
                    ? 'bg-accent-primary/10 text-accent-primary'
                    : 'text-light-500 hover:bg-light-200 hover:text-light-700'
                )}
                title="Toggle Console (Ctrl+`)"
              >
                <Terminal size={18} />
              </button>
              <button
                onClick={toggleRightDrawer}
                className={clsx(
                  'p-2 rounded-lg transition-colors',
                  rightDrawerOpen
                    ? 'bg-accent-primary/10 text-accent-primary'
                    : 'text-light-500 hover:bg-light-200 hover:text-light-700'
                )}
                title="Toggle AI Chat (Ctrl+Shift+A)"
              >
                <MessageSquare size={18} />
              </button>
            </div>
          }
        />
        
        {/* Content Area with Right Drawer */}
        <div className="flex-1 flex overflow-hidden">
          {/* Main Content + Bottom Panel */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Main Content */}
            <div className={clsx(
              'flex-1 overflow-auto p-6',
              bottomPanelMaximized && 'hidden'
            )}>
              <Outlet />
            </div>
            
            {/* Bottom Panel */}
            {bottomPanelOpen && (
              <ResizablePanel
                direction="vertical"
                position="start"
                defaultSize={bottomPanelMaximized ? window.innerHeight - 64 : bottomPanelSize}
                minSize={150}
                maxSize={bottomPanelMaximized ? window.innerHeight - 64 : 500}
                className="border-t border-light-200"
              >
                <BottomPanel
                  onClose={toggleBottomPanel}
                  onMaximize={toggleBottomPanelMaximize}
                  isMaximized={bottomPanelMaximized}
                />
              </ResizablePanel>
            )}
          </div>
          
          {/* Right Drawer */}
          {rightDrawerOpen && (
            <ResizablePanel
              direction="horizontal"
              position="start"
              defaultSize={rightDrawerMaximized ? 600 : rightDrawerSize}
              minSize={280}
              maxSize={rightDrawerMaximized ? 800 : 500}
              className="border-l border-light-200"
            >
              <RightDrawer
                onClose={toggleRightDrawer}
                onMaximize={toggleRightDrawerMaximize}
                isMaximized={rightDrawerMaximized}
              />
            </ResizablePanel>
          )}
        </div>
      </div>

      {/* Panel Toggle Bar (always visible at edges) */}
      {!rightDrawerOpen && (
        <div className="fixed right-0 top-1/2 -translate-y-1/2 z-40">
          <button
            onClick={toggleRightDrawer}
            className="p-2 bg-light-100 hover:bg-light-200 border border-light-300 border-r-0 rounded-l-lg shadow-sm transition-colors group"
            title="Open AI Chat"
          >
            <PanelRight size={16} className="text-light-500 group-hover:text-accent-primary transition-colors" />
          </button>
        </div>
      )}
      
      {!bottomPanelOpen && (
        <div className={clsx(
          'fixed bottom-0 left-1/2 -translate-x-1/2 z-40',
          sidebarCollapsed ? 'ml-8' : 'ml-32'
        )}>
          <button
            onClick={toggleBottomPanel}
            className="px-3 py-1.5 bg-light-100 hover:bg-light-200 border border-light-300 border-b-0 rounded-t-lg shadow-sm transition-colors group flex items-center gap-2"
            title="Open Console"
          >
            <Terminal size={14} className="text-light-500 group-hover:text-accent-primary transition-colors" />
            <span className="text-xs text-light-500 group-hover:text-light-700">Console</span>
          </button>
        </div>
      )}
    </div>
  );
}
