/**
 * PATH: frontend/src/components/physics/ProofDisplay.jsx
 * PURPOSE: Wolfram-style mathematical proof display with theorems, lemmas, and derivations
 * 
 * FEATURES:
 * - Theorem/Lemma/Corollary blocks
 * - Step-by-step derivations
 * - LaTeX rendering
 * - Collapsible proof sections
 * - Citation references
 */

import { useState } from 'react';

import { clsx } from 'clsx';
import {
  ChevronDown,
  ChevronRight,
  BookOpen,
  Lightbulb,
  CheckCircle2,
  ArrowRight,
  Copy,
  Check,
  ExternalLink,
  Sparkles,
} from 'lucide-react';

// Block types with styling
const blockStyles = {
  theorem: {
    label: 'Theorem',
    bg: 'bg-blue-50',
    border: 'border-blue-300',
    accent: 'text-blue-700',
    icon: BookOpen,
  },
  lemma: {
    label: 'Lemma',
    bg: 'bg-purple-50',
    border: 'border-purple-300',
    accent: 'text-purple-700',
    icon: Lightbulb,
  },
  corollary: {
    label: 'Corollary',
    bg: 'bg-green-50',
    border: 'border-green-300',
    accent: 'text-green-700',
    icon: CheckCircle2,
  },
  definition: {
    label: 'Definition',
    bg: 'bg-amber-50',
    border: 'border-amber-300',
    accent: 'text-amber-700',
    icon: BookOpen,
  },
  axiom: {
    label: 'Axiom',
    bg: 'bg-red-50',
    border: 'border-red-300',
    accent: 'text-red-700',
    icon: Sparkles,
  },
};

function MathBlock({ latex, inline = false }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(latex);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={clsx(
      'group relative',
      inline ? 'inline-block' : 'my-4'
    )}>
      <div className={clsx(
        'font-math text-lg',
        inline 
          ? 'px-2 py-1 bg-slate-100 rounded inline-block' 
          : 'p-4 bg-slate-50 border border-slate-200 rounded-lg text-center text-xl'
      )}>
        {/* Simple LaTeX display - in production would use KaTeX/MathJax */}
        <code className="text-slate-800 font-mono">{latex}</code>
      </div>
      {!inline && (
        <button
          onClick={handleCopy}
          className="absolute top-2 right-2 p-1.5 opacity-0 group-hover:opacity-100 bg-white border border-slate-200 rounded transition-all hover:bg-slate-100"
          title="Copy LaTeX"
        >
          {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} className="text-slate-400" />}
        </button>
      )}
    </div>
  );
}

function TheoremBlock({ type = 'theorem', number, title, statement, proof, children }) {
  const [showProof, setShowProof] = useState(false);
  const style = blockStyles[type] || blockStyles.theorem;
  const Icon = style.icon;

  return (
    <div className={clsx('my-6 rounded-lg border-l-4', style.border, style.bg)}>
      {/* Header */}
      <div className="px-4 py-3 flex items-center gap-3">
        <Icon size={20} className={style.accent} />
        <span className={clsx('font-semibold', style.accent)}>
          {style.label} {number && `${number}`}
          {title && ` (${title})`}
        </span>
      </div>
      
      {/* Statement */}
      <div className="px-4 pb-4">
        <div className="text-slate-700 leading-relaxed text-base">
          {statement}
        </div>
        {children}
      </div>
      
      {/* Proof toggle */}
      {proof && (
        <div className="border-t border-slate-200">
          <button
            onClick={() => setShowProof(!showProof)}
            className="w-full px-4 py-2 flex items-center gap-2 text-sm text-slate-600 hover:bg-white/50 transition-colors"
          >
            {showProof ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            <span className="font-medium">{showProof ? 'Hide' : 'Show'} Proof</span>
          </button>
          
          {showProof && (
            <div className="px-4 pb-4 text-slate-600">
              <div className="pl-4 border-l-2 border-slate-300">
                {proof}
              </div>
              <div className="mt-3 text-right text-slate-400 font-serif italic">
                Q.E.D. ∎
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function DerivationStep({ step, number, annotation, isLast }) {
  return (
    <div className="flex items-start gap-4 py-3">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent-primary/10 text-accent-primary flex items-center justify-center text-sm font-medium">
        {number}
      </div>
      <div className="flex-1">
        <MathBlock latex={step} />
        {annotation && (
          <p className="text-sm text-slate-500 mt-1 italic">
            {annotation}
          </p>
        )}
      </div>
      {!isLast && (
        <ArrowRight size={16} className="text-slate-300 mt-3 flex-shrink-0" />
      )}
    </div>
  );
}

function DerivationChain({ title, steps, conclusion }) {
  return (
    <div className="my-6 bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl border border-slate-200 overflow-hidden">
      {/* Header */}
      {title && (
        <div className="px-5 py-3 bg-slate-100 border-b border-slate-200">
          <h3 className="font-semibold text-slate-800">{title}</h3>
        </div>
      )}
      
      {/* Steps */}
      <div className="px-5 py-2 divide-y divide-slate-200">
        {steps.map((step, i) => (
          <DerivationStep
            key={i}
            number={i + 1}
            step={step.expression}
            annotation={step.reason}
            isLast={i === steps.length - 1}
          />
        ))}
      </div>
      
      {/* Conclusion */}
      {conclusion && (
        <div className="px-5 py-4 bg-green-50 border-t border-green-200">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 size={18} className="text-green-600" />
            <span className="font-semibold text-green-800">Conclusion</span>
          </div>
          <MathBlock latex={conclusion} />
        </div>
      )}
    </div>
  );
}

function Reference({ authors, title, year, journal, doi }) {
  return (
    <div className="flex items-start gap-3 py-2 text-sm">
      <BookOpen size={14} className="text-slate-400 mt-1 flex-shrink-0" />
      <div className="text-slate-600">
        <span className="font-medium text-slate-700">{authors}</span>
        {' '}({year}). <em>{title}</em>
        {journal && `. ${journal}`}
        {doi && (
          <a 
            href={`https://doi.org/${doi}`} 
            target="_blank" 
            rel="noopener noreferrer"
            className="ml-2 text-accent-primary hover:underline inline-flex items-center gap-1"
          >
            DOI <ExternalLink size={12} />
          </a>
        )}
      </div>
    </div>
  );
}

/**
 * Main proof display — renders structured proof content in a formal style.
 * @param {Object} props
 * @param {React.ReactNode} props.content - Proof content to render
 */
export default function ProofDisplay({ content }) {
  // Parse structured proof content
  // In production, this would parse from backend response
  
  return (
    <div className="proof-display font-serif">
      {content}
    </div>
  );
}

// Export individual components for use
export { TheoremBlock, DerivationChain, MathBlock, Reference, DerivationStep };
