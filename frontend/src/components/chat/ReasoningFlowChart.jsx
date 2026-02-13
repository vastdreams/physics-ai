/**
 * PATH: frontend/src/components/chat/ReasoningFlowChart.jsx
 * PURPOSE: Display Chain of Thought reasoning as an interactive flowchart
 * 
 * WHY: Users need to understand the AI's reasoning process
 * to validate results and build trust. This component provides:
 * - Visual flowchart of reasoning steps
 * - First principles explanations
 * - Plain language interpretations
 * - Validation checkpoints
 * 
 * FLOW:
 * ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
 * │   Parse     │───▶│   Render     │───▶│  Interact   │
 * │   CoT Data  │    │   Flowchart  │    │  Expand     │
 * └─────────────┘    └──────────────┘    └─────────────┘
 */

import { useState } from 'react';
import {
  ChevronDown,
  ChevronRight,
  Check,
  AlertCircle,
  Lightbulb,
  Target,
  ArrowDown,
  ArrowRight,
  Brain,
  Zap,
  BookOpen,
  Calculator,
  GitBranch,
  Copy,
  CheckCircle2
} from 'lucide-react';
import { clsx } from 'clsx';
import MarkdownRenderer from './MarkdownRenderer';

// Step type configurations
const STEP_TYPES = {
  understanding: {
    icon: BookOpen,
    color: 'blue',
    label: 'Understanding',
    bgClass: 'bg-blue-50 border-blue-200',
    iconClass: 'bg-blue-100 text-blue-600',
  },
  analysis: {
    icon: Brain,
    color: 'purple',
    label: 'Analysis',
    bgClass: 'bg-purple-50 border-purple-200',
    iconClass: 'bg-purple-100 text-purple-600',
  },
  derivation: {
    icon: Calculator,
    color: 'orange',
    label: 'Derivation',
    bgClass: 'bg-orange-50 border-orange-200',
    iconClass: 'bg-orange-100 text-orange-600',
  },
  validation: {
    icon: Check,
    color: 'green',
    label: 'Validation',
    bgClass: 'bg-green-50 border-green-200',
    iconClass: 'bg-green-100 text-green-600',
  },
  conclusion: {
    icon: Target,
    color: 'emerald',
    label: 'Conclusion',
    bgClass: 'bg-emerald-50 border-emerald-200',
    iconClass: 'bg-emerald-100 text-emerald-600',
  },
  assumption: {
    icon: AlertCircle,
    color: 'amber',
    label: 'Assumption',
    bgClass: 'bg-amber-50 border-amber-200',
    iconClass: 'bg-amber-100 text-amber-600',
  },
  insight: {
    icon: Lightbulb,
    color: 'yellow',
    label: 'Insight',
    bgClass: 'bg-yellow-50 border-yellow-200',
    iconClass: 'bg-yellow-100 text-yellow-600',
  },
  branch: {
    icon: GitBranch,
    color: 'slate',
    label: 'Decision',
    bgClass: 'bg-slate-50 border-slate-200',
    iconClass: 'bg-slate-100 text-slate-600',
  },
};

/**
 * Parse reasoning text into structured steps
 */
function parseReasoningSteps(reasoning) {
  if (!reasoning) return [];
  
  // Handle array of steps
  if (Array.isArray(reasoning)) {
    return reasoning.map((step, i) => ({
      id: i + 1,
      type: step.type || detectStepType(step.content || step),
      title: step.title || `Step ${i + 1}`,
      content: step.content || step,
      plainLanguage: step.plain_language || step.plainLanguage || null,
      validation: step.validation || null,
      confidence: step.confidence || null,
    }));
  }
  
  // Handle string - split into steps
  if (typeof reasoning === 'string') {
    // Try to detect numbered steps
    const stepPatterns = [
      /(?:^|\n)(?:Step\s*)?(\d+)[.:]\s*([^\n]+(?:\n(?!\d+[.:])[^\n]+)*)/gi,
      /(?:^|\n)[-•]\s*([^\n]+(?:\n(?![-•])[^\n]+)*)/gi,
    ];
    
    const steps = [];
    let match;
    
    // Try numbered steps first
    const numberedRegex = /(?:^|\n)(?:Step\s*)?(\d+)[.):]\s*([\s\S]*?)(?=(?:\n(?:Step\s*)?\d+[.):])|\n\n|$)/gi;
    while ((match = numberedRegex.exec(reasoning)) !== null) {
      steps.push({
        id: parseInt(match[1]),
        type: detectStepType(match[2]),
        title: `Step ${match[1]}`,
        content: match[2].trim(),
        plainLanguage: null,
        validation: null,
        confidence: null,
      });
    }
    
    if (steps.length > 0) return steps;
    
    // Fall back to splitting by paragraphs
    const paragraphs = reasoning.split(/\n\n+/).filter(p => p.trim());
    return paragraphs.map((p, i) => ({
      id: i + 1,
      type: detectStepType(p),
      title: `Step ${i + 1}`,
      content: p.trim(),
      plainLanguage: null,
      validation: null,
      confidence: null,
    }));
  }
  
  return [];
}

/**
 * Detect step type based on content
 */
function detectStepType(content) {
  if (!content) return 'analysis';
  const lower = content.toLowerCase();
  
  if (/understand|given|problem|question|ask/i.test(lower)) return 'understanding';
  if (/analy[sz]|examin|consider|look at/i.test(lower)) return 'analysis';
  if (/deriv|calculat|comput|solv|substitut|apply|using/i.test(lower)) return 'derivation';
  if (/verif|check|validat|confirm|test/i.test(lower)) return 'validation';
  if (/therefore|thus|conclude|result|answer|final/i.test(lower)) return 'conclusion';
  if (/assum|suppos|let|given that/i.test(lower)) return 'assumption';
  if (/insight|notice|observ|key point|important/i.test(lower)) return 'insight';
  if (/if|case|branch|depend|either|or/i.test(lower)) return 'branch';
  
  return 'analysis';
}

/**
 * Single reasoning step component
 */
function ReasoningStep({ step, isLast, isExpanded, onToggle }) {
  const [copied, setCopied] = useState(false);
  const config = STEP_TYPES[step.type] || STEP_TYPES.analysis;
  const Icon = config.icon;
  
  const handleCopy = () => {
    navigator.clipboard.writeText(step.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  
  return (
    <div className="reasoning-step relative">
      {/* Connector line */}
      {!isLast && (
        <div className="absolute left-5 top-12 bottom-0 w-0.5 bg-slate-200" />
      )}
      
      {/* Step card */}
      <div className={clsx(
        'relative rounded-lg border p-4 transition-all',
        config.bgClass,
        isExpanded && 'shadow-md'
      )}>
        {/* Header */}
        <div 
          className="flex items-start gap-3 cursor-pointer"
          onClick={onToggle}
        >
          {/* Step number with icon */}
          <div className={clsx(
            'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0',
            config.iconClass
          )}>
            <Icon size={18} />
          </div>
          
          {/* Title and type */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className={clsx(
                'text-xs font-semibold uppercase tracking-wider',
                `text-${config.color}-600`
              )}>
                {config.label}
              </span>
              {step.confidence && (
                <span className="text-xs text-slate-400">
                  {Math.round(step.confidence * 100)}% confident
                </span>
              )}
            </div>
            <h4 className="font-medium text-slate-800 mt-0.5">
              {step.title}
            </h4>
          </div>
          
          {/* Expand/collapse */}
          <button className="p-1 hover:bg-white/50 rounded">
            {isExpanded ? (
              <ChevronDown size={16} className="text-slate-400" />
            ) : (
              <ChevronRight size={16} className="text-slate-400" />
            )}
          </button>
        </div>
        
        {/* Expanded content */}
        {isExpanded && (
          <div className="mt-4 space-y-3">
            {/* Main content */}
            <div className="text-sm text-slate-700 pl-13">
              <MarkdownRenderer content={step.content} copyable={false} />
            </div>
            
            {/* Plain language explanation */}
            {step.plainLanguage && (
              <div className="pl-13 pt-3 border-t border-slate-200/50">
                <div className="flex items-center gap-2 text-xs font-medium text-slate-500 mb-2">
                  <Lightbulb size={12} />
                  In plain terms
                </div>
                <p className="text-sm text-slate-600 italic">
                  {step.plainLanguage}
                </p>
              </div>
            )}
            
            {/* Validation status */}
            {step.validation && (
              <div className="pl-13 flex items-center gap-2 text-xs">
                {step.validation.valid ? (
                  <>
                    <CheckCircle2 size={12} className="text-green-500" />
                    <span className="text-green-600">Validated: {step.validation.message}</span>
                  </>
                ) : (
                  <>
                    <AlertCircle size={12} className="text-amber-500" />
                    <span className="text-amber-600">Check: {step.validation.message}</span>
                  </>
                )}
              </div>
            )}
            
            {/* Copy button */}
            <div className="pl-13">
              <button
                onClick={handleCopy}
                className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1"
              >
                {copied ? <Check size={10} /> : <Copy size={10} />}
                {copied ? 'Copied' : 'Copy step'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Main ReasoningFlowChart component
 */
export default function ReasoningFlowChart({ 
  reasoning, 
  title = "Chain of Thought",
  expandAll = false,
  className 
}) {
  const [expandedSteps, setExpandedSteps] = useState(
    expandAll ? new Set() : new Set([0]) // Expand first by default
  );
  const [allExpanded, setAllExpanded] = useState(expandAll);
  
  const steps = parseReasoningSteps(reasoning);
  
  if (!steps || steps.length === 0) {
    return null;
  }
  
  const toggleStep = (index) => {
    setExpandedSteps(prev => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };
  
  const toggleAll = () => {
    if (allExpanded) {
      setExpandedSteps(new Set());
    } else {
      setExpandedSteps(new Set(steps.map((_, i) => i)));
    }
    setAllExpanded(!allExpanded);
  };
  
  return (
    <div className={clsx('reasoning-flowchart', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
            <Brain size={16} className="text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-800">{title}</h3>
            <p className="text-xs text-slate-500">{steps.length} reasoning steps</p>
          </div>
        </div>
        
        <button
          onClick={toggleAll}
          className="text-xs text-slate-500 hover:text-slate-700 px-2 py-1 hover:bg-slate-100 rounded"
        >
          {allExpanded ? 'Collapse all' : 'Expand all'}
        </button>
      </div>
      
      {/* Steps */}
      <div className="space-y-3">
        {steps.map((step, index) => (
          <ReasoningStep
            key={step.id || index}
            step={step}
            isLast={index === steps.length - 1}
            isExpanded={expandedSteps.has(index) || allExpanded}
            onToggle={() => toggleStep(index)}
          />
        ))}
      </div>
      
      {/* Summary */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <div className="flex items-center gap-4 text-xs text-slate-500">
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-blue-400" />
            Understanding: {steps.filter(s => s.type === 'understanding').length}
          </span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-orange-400" />
            Derivation: {steps.filter(s => s.type === 'derivation').length}
          </span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-green-400" />
            Validated: {steps.filter(s => s.type === 'validation').length}
          </span>
        </div>
      </div>
    </div>
  );
}

// Export parser for use elsewhere
export { parseReasoningSteps, STEP_TYPES };
