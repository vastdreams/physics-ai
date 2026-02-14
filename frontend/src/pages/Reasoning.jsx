/**
 * PATH: frontend/src/pages/Reasoning.jsx
 * PURPOSE: Reasoning engine interface showing different reasoning types
 */

import { useState } from 'react';
import {
  Brain,
  GitMerge,
  Lightbulb,
  Shuffle,
  ArrowRight,
  Play,
  ChevronRight,
  AlertCircle
} from 'lucide-react';
import { clsx } from 'clsx';
import { API_BASE } from '../config';

const reasoningTypes = [
  {
    id: 'deductive',
    name: 'Deductive Reasoning',
    icon: Brain,
    color: 'from-blue-500 to-indigo-600',
    description: 'Derives conclusions from established premises using logical rules like modus ponens.',
    example: {
      premises: ['All electrons are particles', 'All particles have mass'],
      conclusion: 'Therefore, all electrons have mass'
    }
  },
  {
    id: 'inductive',
    name: 'Inductive Reasoning',
    icon: GitMerge,
    color: 'from-purple-500 to-violet-600',
    description: 'Generalizes patterns from specific observations to form broader conclusions.',
    example: {
      observations: ['Object A falls at 9.8 m/s²', 'Object B falls at 9.8 m/s²', 'Object C falls at 9.8 m/s²'],
      generalization: 'All objects fall at 9.8 m/s² near Earth\'s surface'
    }
  },
  {
    id: 'abductive',
    name: 'Abductive Reasoning',
    icon: Lightbulb,
    color: 'from-yellow-500 to-orange-600',
    description: 'Infers the best explanation for observed phenomena or evidence.',
    example: {
      observation: 'Light bends when passing through a prism',
      hypothesis: 'White light is composed of multiple wavelengths with different refraction indices'
    }
  },
  {
    id: 'analogical',
    name: 'Analogical Reasoning',
    icon: Shuffle,
    color: 'from-green-500 to-emerald-600',
    description: 'Transfers knowledge from one domain to another based on structural similarities.',
    example: {
      source: 'Electric current flows like water through pipes',
      target: 'Resistance is like friction in pipes, voltage is like water pressure'
    }
  },
];

function ReasoningTypeCard({ type, isSelected, onSelect }) {
  const Icon = type.icon;

  return (
    <button
      onClick={() => onSelect(type)}
      className={clsx(
        'card text-left transition-all',
        isSelected ? 'border-accent-primary ring-2 ring-accent-primary/20' : 'hover:border-light-400'
      )}
    >
      <div className="flex items-start gap-4">
        <div className={clsx(
          'w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center flex-shrink-0',
          type.color
        )}>
          <Icon size={24} className="text-white" />
        </div>
        <div className="flex-1">
          <h3 className="font-medium text-light-800 mb-1">{type.name}</h3>
          <p className="text-sm text-light-500">{type.description}</p>
        </div>
        <ChevronRight size={18} className={clsx(
          'text-light-400 transition-colors',
          isSelected && 'text-accent-primary'
        )} />
      </div>
    </button>
  );
}

function ReasoningDemo({ type }) {
  const [result, setResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [demoFallback, setDemoFallback] = useState(false);

  const mockSteps = {
    deductive: ['Applied modus ponens', 'Chained syllogisms', 'Derived conclusion'],
    inductive: ['Collected observations', 'Identified pattern', 'Formed generalization'],
    abductive: ['Analyzed observation', 'Generated hypotheses', 'Selected best explanation'],
    analogical: ['Identified source domain', 'Mapped structure', 'Transferred knowledge'],
  };

  const handleRun = async () => {
    setIsProcessing(true);
    setDemoFallback(false);
    try {
      const question = type.id === 'deductive' ? type.example.premises.join('; ')
        : type.id === 'inductive' ? type.example.observations.join('; ')
        : type.id === 'abductive' ? type.example.observation
        : type.example.source;

      const res = await fetch(`${API_BASE}/api/v1/agents/reason`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, type: type.id }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult({
          success: true,
          confidence: data.confidence ?? 0.92,
          steps: data.steps || mockSteps[type.id],
        });
      } else { throw new Error(); }
    } catch {
      setDemoFallback(true);
      setResult({ success: true, confidence: 0.92, steps: mockSteps[type.id] });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-light-800">Demo: {type.name}</h3>
        <button 
          onClick={handleRun}
          disabled={isProcessing}
          className="btn-primary flex items-center gap-2"
        >
          {isProcessing ? (
            <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
          ) : (
            <Play size={16} />
          )}
          Run Demo
        </button>
      </div>

      {/* Input */}
      <div className="space-y-4 mb-6">
        {type.id === 'deductive' && (
          <div>
            <p className="text-sm text-light-500 mb-2">Premises</p>
            <div className="space-y-2">
              {type.example.premises.map((p, i) => (
                <div key={i} className="p-3 bg-light-100 rounded-lg text-light-700 text-sm">
                  {i + 1}. {p}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {type.id === 'inductive' && (
          <div>
            <p className="text-sm text-light-500 mb-2">Observations</p>
            <div className="space-y-2">
              {type.example.observations.map((o, i) => (
                <div key={i} className="p-3 bg-light-100 rounded-lg text-light-700 text-sm">
                  {o}
                </div>
              ))}
            </div>
          </div>
        )}

        {type.id === 'abductive' && (
          <div>
            <p className="text-sm text-light-500 mb-2">Observation</p>
            <div className="p-3 bg-light-100 rounded-lg text-light-700 text-sm">
              {type.example.observation}
            </div>
          </div>
        )}

        {type.id === 'analogical' && (
          <div>
            <p className="text-sm text-light-500 mb-2">Source Analogy</p>
            <div className="p-3 bg-light-100 rounded-lg text-light-700 text-sm">
              {type.example.source}
            </div>
          </div>
        )}
      </div>

      {/* Result */}
      {result && (
        <div className="border-t border-light-200 pt-4">
          {demoFallback && (
            <div className="mb-3 p-2 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-xs flex items-center gap-1">
              <AlertCircle size={12} />
              Demo mode — start the backend for real reasoning
            </div>
          )}
          <div className="flex items-center gap-2 mb-3">
            <ArrowRight size={16} className="text-accent-primary" />
            <span className="text-sm font-medium text-light-700">Result</span>
            <span className="badge-green text-[10px]">
              Confidence: {(result.confidence * 100).toFixed(0)}%
            </span>
          </div>
          
          <div className="p-4 bg-accent-primary/5 border border-accent-primary/20 rounded-lg mb-4">
            <p className="text-light-800">
              {type.id === 'deductive' && type.example.conclusion}
              {type.id === 'inductive' && type.example.generalization}
              {type.id === 'abductive' && type.example.hypothesis}
              {type.id === 'analogical' && type.example.target}
            </p>
          </div>

          <div>
            <p className="text-xs text-light-400 mb-2">Reasoning Steps</p>
            <div className="flex items-center gap-2">
              {result.steps.map((step, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-light-200 rounded text-xs text-light-600">
                    {step}
                  </span>
                  {i < result.steps.length - 1 && (
                    <ArrowRight size={12} className="text-light-300" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function Reasoning() {
  const [selectedType, setSelectedType] = useState(reasoningTypes[0]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-light-900">Reasoning Engine</h1>
        <p className="text-light-500 text-sm">Four types of logical reasoning for physics analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Type Selection */}
        <div className="space-y-3">
          <h2 className="text-sm font-medium text-light-500">Select Reasoning Type</h2>
          {reasoningTypes.map((type) => (
            <ReasoningTypeCard
              key={type.id}
              type={type}
              isSelected={selectedType.id === type.id}
              onSelect={setSelectedType}
            />
          ))}
        </div>

        {/* Demo */}
        <div>
          <ReasoningDemo type={selectedType} />
        </div>
      </div>
    </div>
  );
}
