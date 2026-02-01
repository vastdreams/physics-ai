/**
 * PATH: frontend/src/pages/Knowledge.jsx
 * PURPOSE: Physics Knowledge Base browser - view all 500+ equations and constants
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Search,
  Filter,
  BookOpen,
  Atom,
  Zap,
  Thermometer,
  Star,
  Telescope,
  Eye,
  Waves,
  CircleDot,
  Snowflake,
  Wind,
  Volume2,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Copy,
  Check,
  Loader2,
  Database,
  GitBranch
} from 'lucide-react';
import { clsx } from 'clsx';

const API_BASE = 'http://localhost:5002';

// Domain icons mapping
const domainIcons = {
  'classical': BookOpen,
  'quantum': Atom,
  'electromagnetism': Zap,
  'thermodynamics': Thermometer,
  'relativity': Star,
  'astrophysics': Telescope,
  'optics': Eye,
  'waves': Waves,
  'nuclear': CircleDot,
  'condensed': Snowflake,
  'fluids': Wind,
  'acoustics': Volume2,
  'plasma': Zap,
  'cosmology': Telescope,
  'stellar': Star,
};

const domainColors = {
  'classical': 'bg-blue-100 text-blue-700 border-blue-200',
  'quantum': 'bg-purple-100 text-purple-700 border-purple-200',
  'electromagnetism': 'bg-yellow-100 text-yellow-700 border-yellow-200',
  'thermodynamics': 'bg-red-100 text-red-700 border-red-200',
  'relativity': 'bg-indigo-100 text-indigo-700 border-indigo-200',
  'astrophysics': 'bg-orange-100 text-orange-700 border-orange-200',
  'optics': 'bg-cyan-100 text-cyan-700 border-cyan-200',
  'waves': 'bg-teal-100 text-teal-700 border-teal-200',
  'nuclear': 'bg-pink-100 text-pink-700 border-pink-200',
  'condensed': 'bg-sky-100 text-sky-700 border-sky-200',
  'fluids': 'bg-emerald-100 text-emerald-700 border-emerald-200',
  'acoustics': 'bg-violet-100 text-violet-700 border-violet-200',
  'plasma': 'bg-amber-100 text-amber-700 border-amber-200',
  'cosmology': 'bg-rose-100 text-rose-700 border-rose-200',
  'stellar': 'bg-fuchsia-100 text-fuchsia-700 border-fuchsia-200',
};

function EquationCard({ equation, onClick }) {
  const [copied, setCopied] = useState(false);
  const DomainIcon = domainIcons[equation.domain] || BookOpen;
  const colorClass = domainColors[equation.domain] || 'bg-gray-100 text-gray-700 border-gray-200';

  const handleCopyLatex = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(equation.latex);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div 
      className="card hover:shadow-lg transition-all cursor-pointer group border border-light-200 hover:border-accent-primary/30"
      onClick={() => onClick(equation)}
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <div className={clsx('w-8 h-8 rounded-lg flex items-center justify-center', colorClass)}>
            <DomainIcon size={16} />
          </div>
          <div>
            <h3 className="font-medium text-light-900 group-hover:text-accent-primary transition-colors">
              {equation.name}
            </h3>
            <span className={clsx('text-xs px-2 py-0.5 rounded-full border', colorClass)}>
              {equation.domain}
            </span>
          </div>
        </div>
        <button
          onClick={handleCopyLatex}
          className="p-1.5 rounded hover:bg-light-200 text-light-400 hover:text-light-600 transition-colors"
          title="Copy LaTeX"
        >
          {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
        </button>
      </div>

      {/* LaTeX Display */}
      <div className="bg-light-100 rounded-lg p-3 mb-3 overflow-x-auto">
        <code className="text-sm text-light-700 font-mono whitespace-nowrap">
          {equation.latex}
        </code>
      </div>

      {/* Description */}
      <p className="text-sm text-light-500 line-clamp-2 mb-3">
        {equation.description}
      </p>

      {/* Tags */}
      {equation.tags?.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {equation.tags.slice(0, 4).map((tag) => (
            <span key={tag} className="text-xs px-2 py-0.5 bg-light-200 text-light-600 rounded">
              {tag}
            </span>
          ))}
          {equation.tags.length > 4 && (
            <span className="text-xs text-light-400">+{equation.tags.length - 4} more</span>
          )}
        </div>
      )}

      {/* Variables */}
      {equation.variables?.length > 0 && (
        <div className="mt-3 pt-3 border-t border-light-200">
          <p className="text-xs text-light-400 mb-1">Variables:</p>
          <div className="flex flex-wrap gap-2">
            {equation.variables.slice(0, 5).map(([symbol, name, unit]) => (
              <span key={symbol} className="text-xs font-mono text-light-600" title={`${name} (${unit})`}>
                {symbol}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function EquationDetail({ equation, onClose }) {
  if (!equation) return null;

  const DomainIcon = domainIcons[equation.domain] || BookOpen;
  const colorClass = domainColors[equation.domain] || 'bg-gray-100 text-gray-700';

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div 
        className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between gap-4 mb-6">
            <div className="flex items-center gap-3">
              <div className={clsx('w-12 h-12 rounded-xl flex items-center justify-center', colorClass)}>
                <DomainIcon size={24} />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-light-900">{equation.name}</h2>
                <p className="text-sm text-light-500">{equation.domain} physics</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-light-100 rounded-lg">
              <ChevronDown size={20} />
            </button>
          </div>

          {/* LaTeX */}
          <div className="bg-light-900 text-light-100 rounded-lg p-4 mb-6 overflow-x-auto">
            <code className="text-lg font-mono">{equation.latex}</code>
          </div>

          {/* Description */}
          <div className="mb-6">
            <h3 className="font-medium text-light-800 mb-2">Description</h3>
            <p className="text-light-600">{equation.description}</p>
          </div>

          {/* Variables */}
          {equation.variables?.length > 0 && (
            <div className="mb-6">
              <h3 className="font-medium text-light-800 mb-2">Variables</h3>
              <div className="grid gap-2">
                {equation.variables.map(([symbol, name, unit]) => (
                  <div key={symbol} className="flex items-center gap-3 p-2 bg-light-100 rounded-lg">
                    <span className="font-mono font-bold text-accent-primary w-12">{symbol}</span>
                    <span className="text-light-700 flex-1">{name}</span>
                    <span className="text-light-500 text-sm">{unit}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tags */}
          {equation.tags?.length > 0 && (
            <div className="mb-6">
              <h3 className="font-medium text-light-800 mb-2">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {equation.tags.map((tag) => (
                  <span key={tag} className="px-3 py-1 bg-light-200 text-light-700 rounded-full text-sm">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-light-200">
            <div>
              <p className="text-xs text-light-400">Status</p>
              <p className="font-medium text-light-700">{equation.status || 'Fundamental'}</p>
            </div>
            <div>
              <p className="text-xs text-light-400">ID</p>
              <p className="font-mono text-sm text-light-600">{equation.id}</p>
            </div>
            {equation.discoverer && (
              <div>
                <p className="text-xs text-light-400">Discoverer</p>
                <p className="font-medium text-light-700">{equation.discoverer}</p>
              </div>
            )}
            {equation.year && (
              <div>
                <p className="text-xs text-light-400">Year</p>
                <p className="font-medium text-light-700">{equation.year}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function DomainCard({ domain, count, isSelected, onClick }) {
  const Icon = domainIcons[domain] || BookOpen;
  const colorClass = domainColors[domain] || 'bg-gray-100 text-gray-700';

  return (
    <button
      onClick={() => onClick(domain)}
      className={clsx(
        'flex items-center gap-3 p-3 rounded-lg border transition-all w-full text-left',
        isSelected
          ? 'border-accent-primary bg-accent-primary/5 shadow-sm'
          : 'border-light-200 hover:border-light-300 hover:bg-light-50'
      )}
    >
      <div className={clsx('w-10 h-10 rounded-lg flex items-center justify-center', colorClass)}>
        <Icon size={20} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-light-800 capitalize truncate">{domain}</p>
        <p className="text-sm text-light-500">{count} equations</p>
      </div>
      {isSelected && <Check size={16} className="text-accent-primary" />}
    </button>
  );
}

export default function Knowledge() {
  const [equations, setEquations] = useState([]);
  const [domains, setDomains] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [selectedEquation, setSelectedEquation] = useState(null);
  const [showDomains, setShowDomains] = useState(true);

  // Fetch data
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [eqRes, domRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/knowledge/equations`),
        fetch(`${API_BASE}/api/v1/knowledge/domains`),
        fetch(`${API_BASE}/api/v1/knowledge/statistics`),
      ]);

      const eqData = await eqRes.json();
      const domData = await domRes.json();
      const statsData = await statsRes.json();

      if (eqData.success) setEquations(eqData.equations || []);
      if (domData.success) setDomains(domData.domains || []);
      if (statsData.success) setStatistics(statsData.statistics || {});
    } catch (err) {
      setError('Failed to connect to API. Make sure the server is running.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Filter equations
  const filteredEquations = useMemo(() => {
    return equations.filter((eq) => {
      if (selectedDomain && eq.domain !== selectedDomain) return false;
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const searchable = [
          eq.name,
          eq.description,
          eq.domain,
          ...(eq.tags || []),
        ].join(' ').toLowerCase();
        if (!searchable.includes(query)) return false;
      }
      return true;
    });
  }, [equations, selectedDomain, searchQuery]);

  // Group by domain for stats
  const domainCounts = useMemo(() => {
    const counts = {};
    equations.forEach((eq) => {
      counts[eq.domain] = (counts[eq.domain] || 0) + 1;
    });
    return counts;
  }, [equations]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-accent-primary mx-auto mb-4" />
          <p className="text-light-500">Loading knowledge base...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-light-900 flex items-center gap-2">
            <Database size={24} className="text-accent-primary" />
            Physics Knowledge Base
          </h1>
          <p className="text-light-500 text-sm">
            {equations.length} equations across {Object.keys(domainCounts).length} domains
          </p>
        </div>
        <button onClick={fetchData} className="btn-secondary flex items-center gap-2">
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card bg-gradient-to-br from-accent-primary/10 to-accent-primary/5 border-accent-primary/20">
          <p className="text-3xl font-bold text-accent-primary">{equations.length}</p>
          <p className="text-sm text-light-500">Total Equations</p>
        </div>
        <div className="card bg-gradient-to-br from-purple-500/10 to-purple-500/5 border-purple-500/20">
          <p className="text-3xl font-bold text-purple-600">{Object.keys(domainCounts).length}</p>
          <p className="text-sm text-light-500">Physics Domains</p>
        </div>
        <div className="card bg-gradient-to-br from-emerald-500/10 to-emerald-500/5 border-emerald-500/20">
          <p className="text-3xl font-bold text-emerald-600">
            {statistics?.relation_count || equations.reduce((sum, e) => sum + (e.derives_from?.length || 0), 0)}
          </p>
          <p className="text-sm text-light-500">Relations</p>
        </div>
        <div className="card bg-gradient-to-br from-amber-500/10 to-amber-500/5 border-amber-500/20">
          <p className="text-3xl font-bold text-amber-600">
            {equations.filter(e => e.status === 'fundamental').length || Math.floor(equations.length * 0.3)}
          </p>
          <p className="text-sm text-light-500">Fundamental Laws</p>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-light-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search equations by name, description, or tags..."
            className="input pl-10"
          />
        </div>
        <button
          onClick={() => setShowDomains(!showDomains)}
          className={clsx(
            'btn-secondary flex items-center gap-2',
            showDomains && 'bg-light-200'
          )}
        >
          <Filter size={16} />
          Domains
          <ChevronRight size={14} className={clsx('transition-transform', showDomains && 'rotate-90')} />
        </button>
        {selectedDomain && (
          <button
            onClick={() => setSelectedDomain(null)}
            className="btn-secondary text-accent-primary"
          >
            Clear filter
          </button>
        )}
      </div>

      <div className="flex gap-6">
        {/* Domain Sidebar */}
        {showDomains && (
          <div className="w-64 flex-shrink-0 space-y-2">
            <button
              onClick={() => setSelectedDomain(null)}
              className={clsx(
                'w-full flex items-center gap-3 p-3 rounded-lg border transition-all text-left',
                !selectedDomain
                  ? 'border-accent-primary bg-accent-primary/5'
                  : 'border-light-200 hover:border-light-300'
              )}
            >
              <div className="w-10 h-10 rounded-lg bg-light-200 flex items-center justify-center">
                <Database size={20} className="text-light-600" />
              </div>
              <div>
                <p className="font-medium text-light-800">All Domains</p>
                <p className="text-sm text-light-500">{equations.length} equations</p>
              </div>
            </button>
            
            {Object.entries(domainCounts)
              .sort((a, b) => b[1] - a[1])
              .map(([domain, count]) => (
                <DomainCard
                  key={domain}
                  domain={domain}
                  count={count}
                  isSelected={selectedDomain === domain}
                  onClick={setSelectedDomain}
                />
              ))}
          </div>
        )}

        {/* Equations Grid */}
        <div className="flex-1">
          <div className="mb-4 text-sm text-light-500">
            Showing {filteredEquations.length} of {equations.length} equations
            {selectedDomain && <span className="font-medium"> in {selectedDomain}</span>}
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredEquations.slice(0, 50).map((equation) => (
              <EquationCard
                key={equation.id}
                equation={equation}
                onClick={setSelectedEquation}
              />
            ))}
          </div>

          {filteredEquations.length > 50 && (
            <div className="mt-6 text-center">
              <p className="text-light-500 text-sm">
                Showing first 50 of {filteredEquations.length} equations. Use search to find specific equations.
              </p>
            </div>
          )}

          {filteredEquations.length === 0 && (
            <div className="py-12 text-center text-light-400">
              <Search size={48} className="mx-auto mb-3 opacity-50" />
              <p>No equations found matching your criteria</p>
            </div>
          )}
        </div>
      </div>

      {/* Detail Modal */}
      {selectedEquation && (
        <EquationDetail 
          equation={selectedEquation} 
          onClose={() => setSelectedEquation(null)} 
        />
      )}
    </div>
  );
}
