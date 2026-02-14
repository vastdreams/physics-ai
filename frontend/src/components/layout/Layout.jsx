/**
 * PATH: frontend/src/components/layout/Layout.jsx
 * PURPOSE: Main layout with premium light design and resizable panels
 */

import { useState, useCallback } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
import { MessageSquare, Terminal, PanelRight } from 'lucide-react';

import Sidebar from './Sidebar';
import Header from './Header';
import ResizablePanel from '../panels/ResizablePanel';
import RightDrawer from '../panels/RightDrawer';
import BottomPanel from '../panels/BottomPanel';

const pageTitles = {
  '/dashboard': { title: 'Dashboard', subtitle: 'System overview and quick actions' },
  '/chat': { title: 'AI Chat', subtitle: 'Conversational physics interface' },
  '/simulations': { title: 'Simulations', subtitle: 'Run and visualize physics simulations' },
  '/equations': { title: 'Equations', subtitle: 'Symbolic equation solver' },
  '/knowledge': { title: 'Knowledge', subtitle: 'Unified physics knowledge base' },
  '/models': { title: 'Physics Models', subtitle: 'Available simulation models' },
  '/rules': { title: 'Rule Engine', subtitle: 'Manage inference rules' },
  '/evolution': { title: 'Evolution', subtitle: 'Self-evolution and code analysis' },
  '/reasoning': { title: 'Reasoning', subtitle: 'Logical reasoning types' },
  '/logs': { title: 'System Logs', subtitle: 'Chain-of-thought and activity logs' },
  '/metrics': { title: 'Metrics', subtitle: 'Performance and usage metrics' },
  '/settings': { title: 'Settings', subtitle: 'System configuration' },
  '/about': { title: 'About', subtitle: 'Vision and mission' },
};

/** Main layout — sidebar, header, content area, and resizable panels. */
export default function Layout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rightDrawerOpen, setRightDrawerOpen] = useState(false);
  const [bottomPanelOpen, setBottomPanelOpen] = useState(false);
  const [rightDrawerMaximized, setRightDrawerMaximized] = useState(false);
  const [bottomPanelMaximized, setBottomPanelMaximized] = useState(false);
  const [rightDrawerSize, setRightDrawerSize] = useState(380);
  const [bottomPanelSize, setBottomPanelSize] = useState(250);

  const location = useLocation();
  const pageInfo = pageTitles[location.pathname] || { title: 'Beyond Frontier', subtitle: '' };

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
    <div className="h-screen flex overflow-hidden bg-slate-50">
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main */}
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
                  'p-2 rounded-xl transition-colors',
                  bottomPanelOpen
                    ? 'bg-indigo-50 text-indigo-500'
                    : 'text-slate-400 hover:bg-slate-100 hover:text-slate-600'
                )}
                title="Toggle Console"
              >
                <Terminal size={18} />
              </button>
              <button
                onClick={toggleRightDrawer}
                className={clsx(
                  'p-2 rounded-xl transition-colors',
                  rightDrawerOpen
                    ? 'bg-indigo-50 text-indigo-500'
                    : 'text-slate-400 hover:bg-slate-100 hover:text-slate-600'
                )}
                title="Toggle AI Chat"
              >
                <MessageSquare size={18} />
              </button>
            </div>
          }
        />

        {/* Content + Panels */}
        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Content */}
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
                className="border-t border-slate-200"
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
              className="border-l border-slate-200"
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

      {/* Edge panel toggles */}
      {!rightDrawerOpen && (
        <div className="fixed right-0 top-1/2 -translate-y-1/2 z-40">
          <button
            onClick={toggleRightDrawer}
            className="p-2 bg-white/80 backdrop-blur-sm hover:bg-white border border-slate-200 border-r-0 rounded-l-xl shadow-soft transition-all group"
            title="Open AI Chat"
          >
            <PanelRight size={16} className="text-slate-400 group-hover:text-indigo-500 transition-colors" />
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
            className="px-4 py-1.5 bg-white/80 backdrop-blur-sm hover:bg-white border border-slate-200 border-b-0 rounded-t-xl shadow-soft transition-all group flex items-center gap-2"
            title="Open Console"
          >
            <Terminal size={14} className="text-slate-400 group-hover:text-indigo-500 transition-colors" />
            <span className="text-xs text-slate-400 group-hover:text-slate-600 font-medium">Console</span>
          </button>
        </div>
      )}
    </div>
  );
}
