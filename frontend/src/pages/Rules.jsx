/**
 * PATH: frontend/src/pages/Rules.jsx
 * PURPOSE: Rule engine management interface
 */

import { useState, useEffect } from 'react';
import {
  Plus,
  Search,
  Filter,
  Trash2,
  Edit2,
  Play,
  ChevronRight,
  Database,
  Code,
  CheckCircle2,
  AlertCircle,
  Copy,
  X
} from 'lucide-react';
import { clsx } from 'clsx';

function RuleCard({ rule, onEdit, onDelete, onTest }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card group">
      <div 
        className="flex items-start gap-4 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="w-10 h-10 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center flex-shrink-0">
          <Database size={20} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-medium text-dark-100">{rule.name}</h3>
            <span className={clsx(
              'badge text-[10px]',
              rule.enabled ? 'badge-green' : 'badge-yellow'
            )}>
              {rule.enabled ? 'Active' : 'Disabled'}
            </span>
            {rule.priority && (
              <span className="badge-blue text-[10px]">Priority: {rule.priority}</span>
            )}
          </div>
          <p className="text-sm text-dark-400 truncate">{rule.description || 'No description'}</p>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button 
            onClick={(e) => { e.stopPropagation(); onTest(rule); }}
            className="p-2 hover:bg-dark-700 rounded-lg text-dark-400 hover:text-accent-primary transition-colors"
          >
            <Play size={16} />
          </button>
          <button 
            onClick={(e) => { e.stopPropagation(); onEdit(rule); }}
            className="p-2 hover:bg-dark-700 rounded-lg text-dark-400 hover:text-dark-200 transition-colors"
          >
            <Edit2 size={16} />
          </button>
          <button 
            onClick={(e) => { e.stopPropagation(); onDelete(rule); }}
            className="p-2 hover:bg-dark-700 rounded-lg text-dark-400 hover:text-red-400 transition-colors"
          >
            <Trash2 size={16} />
          </button>
        </div>
        <ChevronRight 
          size={16} 
          className={clsx(
            'text-dark-500 transition-transform',
            expanded && 'rotate-90'
          )} 
        />
      </div>

      {expanded && (
        <div className="mt-4 pt-4 border-t border-dark-700 space-y-3">
          <div>
            <p className="text-xs text-dark-500 mb-1">Condition</p>
            <pre className="code-block text-xs overflow-x-auto">
              {JSON.stringify(rule.condition, null, 2)}
            </pre>
          </div>
          <div>
            <p className="text-xs text-dark-500 mb-1">Action</p>
            <pre className="code-block text-xs overflow-x-auto">
              {JSON.stringify(rule.action, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

function AddRuleModal({ isOpen, onClose, onAdd }) {
  const [name, setName] = useState('');
  const [condition, setCondition] = useState('{}');
  const [action, setAction] = useState('{}');
  const [priority, setPriority] = useState(10);
  const [error, setError] = useState(null);

  const handleSubmit = () => {
    try {
      const conditionObj = JSON.parse(condition);
      const actionObj = JSON.parse(action);
      onAdd({ name, condition: conditionObj, action: actionObj, priority });
      onClose();
      setName('');
      setCondition('{}');
      setAction('{}');
      setPriority(10);
      setError(null);
    } catch (e) {
      setError('Invalid JSON in condition or action');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-dark-800 rounded-xl border border-dark-700 w-full max-w-lg p-6 mx-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-dark-100">Add New Rule</h2>
          <button onClick={onClose} className="p-1 hover:bg-dark-700 rounded">
            <X size={20} className="text-dark-400" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="text-sm text-dark-400 mb-1 block">Rule Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., kinetic_energy_rule"
              className="input"
            />
          </div>

          <div>
            <label className="text-sm text-dark-400 mb-1 block">Priority</label>
            <input
              type="number"
              value={priority}
              onChange={(e) => setPriority(parseInt(e.target.value) || 10)}
              className="input"
            />
          </div>

          <div>
            <label className="text-sm text-dark-400 mb-1 block">Condition (JSON)</label>
            <textarea
              value={condition}
              onChange={(e) => setCondition(e.target.value)}
              placeholder='{"mass": {"$gt": 0}}'
              rows={4}
              className="input font-mono text-sm"
            />
          </div>

          <div>
            <label className="text-sm text-dark-400 mb-1 block">Action (JSON)</label>
            <textarea
              value={action}
              onChange={(e) => setAction(e.target.value)}
              placeholder='{"$set": {"status": "processed"}}'
              rows={4}
              className="input font-mono text-sm"
            />
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button onClick={handleSubmit} className="btn-primary">
            Add Rule
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Rules() {
  const [rules, setRules] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    // Fetch rules from API
    const fetchRules = async () => {
      try {
        const response = await fetch('http://localhost:5002/api/v1/rules');
        if (response.ok) {
          const data = await response.json();
          setRules(data.rules || []);
        }
      } catch (error) {
        console.log('Using mock rules');
        setRules([
          {
            id: 1,
            name: 'kinetic_energy',
            description: 'Calculate kinetic energy from mass and velocity',
            condition: { mass: { $gt: 0 }, velocity: { $exists: true } },
            action: { $compute: { expression: '0.5 * mass * velocity ** 2', target: 'kinetic_energy' } },
            priority: 10,
            enabled: true
          },
          {
            id: 2,
            name: 'momentum',
            description: 'Calculate momentum from mass and velocity',
            condition: { mass: { $gt: 0 }, velocity: { $exists: true } },
            action: { $compute: { expression: 'mass * velocity', target: 'momentum' } },
            priority: 10,
            enabled: true
          },
          {
            id: 3,
            name: 'potential_energy',
            description: 'Calculate gravitational potential energy',
            condition: { mass: { $gt: 0 }, height: { $exists: true } },
            action: { $compute: { expression: 'mass * 9.81 * height', target: 'potential_energy' } },
            priority: 5,
            enabled: false
          },
        ]);
      }
    };
    fetchRules();
  }, []);

  const handleAddRule = async (rule) => {
    try {
      const response = await fetch('http://localhost:5002/api/v1/rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rule),
      });
      if (response.ok) {
        const newRule = await response.json();
        setRules(prev => [...prev, newRule]);
      }
    } catch (error) {
      // Add locally for demo
      setRules(prev => [...prev, { ...rule, id: Date.now(), enabled: true }]);
    }
  };

  const handleDeleteRule = async (rule) => {
    try {
      await fetch(`http://localhost:5002/api/v1/rules/${rule.name}`, {
        method: 'DELETE',
      });
    } catch (error) {
      console.log('Delete failed, removing locally');
    }
    setRules(prev => prev.filter(r => r.id !== rule.id));
  };

  const handleTestRule = async (rule) => {
    setTestResult({ loading: true, rule });
    try {
      const response = await fetch('http://localhost:5002/api/v1/rules/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          context: { mass: 10, velocity: 5, height: 2 }
        }),
      });
      if (response.ok) {
        const result = await response.json();
        setTestResult({ success: true, rule, result });
      }
    } catch (error) {
      setTestResult({ 
        success: true, 
        rule, 
        result: { demo: true, message: 'Rule would match the test context' } 
      });
    }
  };

  const filteredRules = rules.filter(rule => 
    rule.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    rule.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-dark-100">Rule Engine</h1>
          <p className="text-dark-400 text-sm">{rules.length} rules configured</p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={16} />
          Add Rule
        </button>
      </div>

      {/* Search & Filter */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-dark-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search rules..."
            className="input pl-10"
          />
        </div>
        <button className="btn-secondary flex items-center gap-2">
          <Filter size={16} />
          Filter
        </button>
      </div>

      {/* Test Result */}
      {testResult && (
        <div className={clsx(
          'card',
          testResult.success ? 'border-green-500/30' : 'border-dark-700'
        )}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              {testResult.loading ? (
                <div className="animate-spin w-4 h-4 border-2 border-accent-primary border-t-transparent rounded-full" />
              ) : (
                <CheckCircle2 size={16} className="text-green-400" />
              )}
              <span className="font-medium text-dark-200">
                Test Result: {testResult.rule?.name}
              </span>
            </div>
            <button 
              onClick={() => setTestResult(null)}
              className="p-1 hover:bg-dark-700 rounded"
            >
              <X size={16} className="text-dark-400" />
            </button>
          </div>
          {testResult.result && (
            <pre className="code-block text-xs">
              {JSON.stringify(testResult.result, null, 2)}
            </pre>
          )}
        </div>
      )}

      {/* Rules List */}
      <div className="space-y-3">
        {filteredRules.map((rule) => (
          <RuleCard
            key={rule.id}
            rule={rule}
            onEdit={() => {}}
            onDelete={handleDeleteRule}
            onTest={handleTestRule}
          />
        ))}

        {filteredRules.length === 0 && (
          <div className="card text-center py-12">
            <Database size={48} className="mx-auto mb-3 text-dark-600" />
            <p className="text-dark-400">No rules found</p>
            <button 
              onClick={() => setShowAddModal(true)}
              className="btn-primary mt-4"
            >
              Add your first rule
            </button>
          </div>
        )}
      </div>

      <AddRuleModal 
        isOpen={showAddModal} 
        onClose={() => setShowAddModal(false)} 
        onAdd={handleAddRule}
      />
    </div>
  );
}
