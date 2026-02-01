/**
 * PATH: frontend/src/components/layout/Sidebar.jsx
 * PURPOSE: Notion-style sidebar navigation with collapsible sections
 * 
 * FLOW:
 * ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
 * │   Logo &    │───▶│  Navigation  │───▶│   Footer    │
 * │   Search    │    │   Sections   │    │   Actions   │
 * └─────────────┘    └──────────────┘    └─────────────┘
 */

import { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  Home, 
  MessageSquare, 
  Atom, 
  BookOpen, 
  GitBranch, 
  Settings,
  ChevronDown,
  ChevronRight,
  Search,
  Plus,
  Sparkles,
  Cpu,
  Workflow,
  Database,
  LineChart,
  History,
  Terminal,
  Zap
} from 'lucide-react';
import { clsx } from 'clsx';

const navigationSections = [
  {
    title: 'Main',
    items: [
      { name: 'Dashboard', path: '/', icon: Home },
      { name: 'Chat', path: '/chat', icon: MessageSquare, badge: 'AI' },
    ]
  },
  {
    title: 'Physics',
    items: [
      { name: 'Simulations', path: '/simulations', icon: Atom },
      { name: 'Equations', path: '/equations', icon: BookOpen },
      { name: 'Models', path: '/models', icon: Workflow },
    ]
  },
  {
    title: 'AI Engine',
    items: [
      { name: 'Rules', path: '/rules', icon: Database },
      { name: 'Evolution', path: '/evolution', icon: GitBranch },
      { name: 'Reasoning', path: '/reasoning', icon: Cpu },
    ]
  },
  {
    title: 'System',
    items: [
      { name: 'Logs', path: '/logs', icon: Terminal },
      { name: 'Metrics', path: '/metrics', icon: LineChart },
      { name: 'Settings', path: '/settings', icon: Settings },
    ]
  }
];

function NavItem({ item, collapsed }) {
  const location = useLocation();
  const isActive = location.pathname === item.path;
  const Icon = item.icon;

  return (
    <NavLink
      to={item.path}
      className={clsx(
        'flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200',
        isActive 
          ? 'bg-dark-700/80 text-white' 
          : 'text-dark-400 hover:bg-dark-800 hover:text-dark-200'
      )}
    >
      <Icon size={18} className={clsx(isActive && 'text-accent-primary')} />
      {!collapsed && (
        <>
          <span className="flex-1 text-sm font-medium">{item.name}</span>
          {item.badge && (
            <span className="badge-green text-[10px]">{item.badge}</span>
          )}
        </>
      )}
    </NavLink>
  );
}

function NavSection({ section, collapsed, defaultOpen = true }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="mb-2">
      {!collapsed && (
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 px-3 py-1.5 w-full text-dark-500 hover:text-dark-300 transition-colors"
        >
          {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          <span className="text-xs font-semibold uppercase tracking-wider">
            {section.title}
          </span>
        </button>
      )}
      {(isOpen || collapsed) && (
        <div className="mt-1 space-y-0.5">
          {section.items.map((item) => (
            <NavItem key={item.path} item={item} collapsed={collapsed} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function Sidebar({ collapsed, onToggle }) {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <aside 
      className={clsx(
        'fixed left-0 top-0 h-screen bg-dark-900 border-r border-dark-800 flex flex-col z-50 transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-dark-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary to-accent-blue flex items-center justify-center">
            <Sparkles size={18} className="text-white" />
          </div>
          {!collapsed && (
            <div>
              <h1 className="font-semibold text-white">Physics AI</h1>
              <p className="text-xs text-dark-500">Neurosymbolic Engine</p>
            </div>
          )}
        </div>
      </div>

      {/* Search */}
      {!collapsed && (
        <div className="p-3">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-dark-500" />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-dark-800 border border-dark-700 rounded-lg text-sm text-dark-200 placeholder-dark-500 focus:outline-none focus:border-dark-600"
            />
            <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-dark-500 bg-dark-700 px-1.5 py-0.5 rounded">
              ⌘K
            </kbd>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      {!collapsed && (
        <div className="px-3 pb-2">
          <button className="w-full flex items-center gap-2 px-3 py-2 bg-dark-800 hover:bg-dark-700 border border-dark-700 rounded-lg text-sm text-dark-300 transition-colors">
            <Plus size={16} />
            <span>New Simulation</span>
          </button>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {navigationSections.map((section) => (
          <NavSection 
            key={section.title} 
            section={section} 
            collapsed={collapsed}
          />
        ))}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-dark-800">
        {!collapsed ? (
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-dark-800/50">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent-purple to-accent-pink flex items-center justify-center text-white text-sm font-medium">
              A
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-dark-200 truncate">Abhishek</p>
              <p className="text-xs text-dark-500">Administrator</p>
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent-purple to-accent-pink flex items-center justify-center text-white text-sm font-medium">
              A
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
