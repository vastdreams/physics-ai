/**
 * PATH: frontend/src/components/layout/Sidebar.jsx
 * PURPOSE: Premium sidebar navigation with gradient accents
 */

import { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
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
  Terminal,
  Info,
} from 'lucide-react';

import { API_BASE } from '../../config';

const buildNavigationSections = (knowledgeCount) => [
  {
    title: 'Main',
    items: [
      { name: 'Dashboard', path: '/dashboard', icon: Home },
      { name: 'Chat', path: '/chat', icon: MessageSquare, badge: 'AI' },
    ]
  },
  {
    title: 'Physics',
    items: [
      { name: 'Knowledge Base', path: '/knowledge', icon: Database, badge: knowledgeCount != null ? String(knowledgeCount) : null },
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
      { name: 'About', path: '/about', icon: Info },
    ]
  }
];

/** Single navigation link with gradient active indicator. */
function NavItem({ item, collapsed }) {
  const location = useLocation();
  const isActive = location.pathname === item.path;
  const Icon = item.icon;

  return (
    <NavLink
      to={item.path}
      className={clsx(
        'flex items-center gap-3 px-3 py-2 rounded-xl transition-all duration-200 relative',
        isActive
          ? 'bg-gradient-to-r from-indigo-50 to-violet-50 text-indigo-600 font-semibold'
          : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'
      )}
    >
      {/* Active gradient bar */}
      {isActive && (
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-full bg-gradient-to-b from-indigo-500 to-violet-500" />
      )}
      <Icon size={18} className={clsx(isActive ? 'text-indigo-500' : 'text-slate-400')} />
      {!collapsed && (
        <>
          <span className="flex-1 text-sm">{item.name}</span>
          {item.badge && (
            <span className={clsx(
              'text-[10px] px-1.5 py-0.5 rounded-full font-semibold',
              isActive
                ? 'bg-indigo-100 text-indigo-600'
                : 'bg-emerald-50 text-emerald-600'
            )}>
              {item.badge}
            </span>
          )}
        </>
      )}
    </NavLink>
  );
}

/** Collapsible navigation section. */
function NavSection({ section, collapsed, defaultOpen = true }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="mb-3">
      {!collapsed && (
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 px-3 py-1.5 w-full text-slate-400 hover:text-slate-600 transition-colors"
        >
          {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          <span className="text-[11px] font-bold uppercase tracking-widest">
            {section.title}
          </span>
        </button>
      )}
      {(isOpen || collapsed) && (
        <div className="mt-0.5 space-y-0.5">
          {section.items.map((item) => (
            <NavItem key={item.path} item={item} collapsed={collapsed} />
          ))}
        </div>
      )}
    </div>
  );
}

/** Premium sidebar with frosted glass effect. */
export default function Sidebar({ collapsed, onToggle }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [knowledgeCount, setKnowledgeCount] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/v1/knowledge/statistics`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(d => setKnowledgeCount(d.statistics?.total_nodes ?? d.statistics?.total ?? null))
      .catch(() => setKnowledgeCount(null));
  }, []);

  const navigationSections = buildNavigationSections(knowledgeCount);

  return (
    <aside
      className={clsx(
        'fixed left-0 top-0 h-screen bg-white/80 backdrop-blur-xl border-r border-slate-200/60 flex flex-col z-50 transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Brand */}
      <div className="p-4 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md shadow-indigo-200/50">
            <Sparkles size={18} className="text-white" />
          </div>
          {!collapsed && (
            <div>
              <h1 className="font-bold text-slate-900 tracking-tight">Beyond Frontier</h1>
              <p className="text-[11px] text-slate-400 font-medium">Physics Engine</p>
            </div>
          )}
        </div>
      </div>

      {/* Search */}
      {!collapsed && (
        <div className="p-3">
          <div className="relative">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 transition-all"
            />
            <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-slate-400 bg-white border border-slate-200 px-1.5 py-0.5 rounded font-mono">
              /
            </kbd>
          </div>
        </div>
      )}

      {/* Quick Action */}
      {!collapsed && (
        <div className="px-3 pb-2">
          <button className="w-full flex items-center gap-2 px-3 py-2.5 bg-gradient-to-r from-indigo-50 to-violet-50 hover:from-indigo-100 hover:to-violet-100 border border-indigo-100 rounded-xl text-sm text-indigo-600 font-medium transition-all">
            <Plus size={16} />
            <span>New Simulation</span>
          </button>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-0.5">
        {navigationSections.map((section) => (
          <NavSection
            key={section.title}
            section={section}
            collapsed={collapsed}
          />
        ))}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-slate-100">
        {!collapsed ? (
          <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-slate-50">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-white text-sm font-bold shadow-sm">
              A
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-800 truncate">Abhishek</p>
              <p className="text-[11px] text-slate-400">Administrator</p>
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-white text-sm font-bold">
              A
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
