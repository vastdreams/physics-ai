/**
 * PATH: frontend/src/components/chat/QualityBadge.jsx
 * PURPOSE: Display rubric quality gate results as visual badges and detailed breakdown
 * 
 * WHY: Users need to see at a glance how trustworthy an AI response is.
 * The quality badge provides immediate feedback via a letter grade,
 * and expands to show per-dimension rubric scores. This builds trust
 * and transparency into the AI system.
 * 
 * FEATURES:
 * - Compact letter grade badge (A/B/C/D/F)
 * - Expandable dimension breakdown with progress bars
 * - Gate pass/fail indicators
 * - Strengths and weaknesses summary
 * - Improvement suggestions
 */

import { useState } from 'react';
import {
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Lightbulb,
  Info,
  Zap,
  BookOpen,
  Calculator,
  FileCode,
  GraduationCap,
  Link,
  Copy,
  Check
} from 'lucide-react';
import { clsx } from 'clsx';

// Grade color mapping
const GRADE_COLORS = {
  A: { bg: 'bg-emerald-100', text: 'text-emerald-700', border: 'border-emerald-300', bar: 'bg-emerald-500' },
  B: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300', bar: 'bg-blue-500' },
  C: { bg: 'bg-amber-100', text: 'text-amber-700', border: 'border-amber-300', bar: 'bg-amber-500' },
  D: { bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-300', bar: 'bg-orange-500' },
  F: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300', bar: 'bg-red-500' },
};

// Dimension icons and labels
const DIMENSION_CONFIG = {
  physics_accuracy: { icon: Zap, label: 'Physics Accuracy', description: 'Correctness of physics laws and principles' },
  mathematical_rigor: { icon: Calculator, label: 'Mathematical Rigor', description: 'Derivation validity and notation' },
  explanation_clarity: { icon: BookOpen, label: 'Explanation Clarity', description: 'First principles and plain language' },
  provenance_completeness: { icon: Link, label: 'Provenance', description: 'Source references and artefact coverage' },
  code_quality: { icon: FileCode, label: 'Code Quality', description: 'Correctness, safety, and readability' },
  pedagogical_value: { icon: GraduationCap, label: 'Pedagogical Value', description: 'Physical insight and connections' },
};

/**
 * Compact quality badge (shows just the grade)
 */
function GradeBadge({ grade, score, onClick, compact = false }) {
  const colors = GRADE_COLORS[grade] || GRADE_COLORS.C;
  
  const ShieldIcon = grade === 'A' || grade === 'B' 
    ? ShieldCheck 
    : grade === 'C' 
      ? ShieldAlert 
      : ShieldX;
  
  if (compact) {
    return (
      <button
        onClick={onClick}
        className={clsx(
          'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold transition-all hover:shadow-sm',
          colors.bg, colors.text, 'border', colors.border
        )}
        title={`Quality: ${grade} (${Math.round(score * 100)}%)`}
      >
        <ShieldIcon size={12} />
        {grade}
      </button>
    );
  }
  
  return (
    <button
      onClick={onClick}
      className={clsx(
        'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-semibold transition-all hover:shadow-md cursor-pointer',
        colors.bg, colors.text, 'border', colors.border
      )}
      title="Click to see quality details"
    >
      <ShieldIcon size={16} />
      <span>Quality: {grade}</span>
      <span className="text-xs opacity-70">({Math.round(score * 100)}%)</span>
    </button>
  );
}

/**
 * Progress bar for a dimension score
 */
function ScoreBar({ score, grade, passed }) {
  const colors = GRADE_COLORS[grade] || GRADE_COLORS.C;
  const percentage = Math.round(score * 100);
  
  return (
    <div className="flex items-center gap-2 w-full">
      <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all duration-500', colors.bar)}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className={clsx('text-xs font-mono w-10 text-right', colors.text)}>
        {percentage}%
      </span>
      {passed ? (
        <CheckCircle2 size={12} className="text-green-500 flex-shrink-0" />
      ) : (
        <XCircle size={12} className="text-red-400 flex-shrink-0" />
      )}
    </div>
  );
}

/**
 * Single dimension detail row
 */
function DimensionRow({ dimensionKey, data, expanded, onToggle }) {
  const config = DIMENSION_CONFIG[dimensionKey] || {
    icon: Info,
    label: dimensionKey.replace(/_/g, ' '),
    description: '',
  };
  const Icon = config.icon;
  
  return (
    <div className="border-b border-slate-100 last:border-b-0">
      {/* Summary row */}
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-slate-50 transition-colors"
      >
        <Icon size={14} className="text-slate-500 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-700">{config.label}</span>
            <span className={clsx(
              'text-xs font-bold px-1.5 py-0.5 rounded',
              GRADE_COLORS[data.grade]?.bg,
              GRADE_COLORS[data.grade]?.text
            )}>
              {data.grade}
            </span>
          </div>
          <ScoreBar score={data.score} grade={data.grade} passed={data.passed} />
        </div>
        {expanded ? (
          <ChevronDown size={14} className="text-slate-400 flex-shrink-0" />
        ) : (
          <ChevronRight size={14} className="text-slate-400 flex-shrink-0" />
        )}
      </button>
      
      {/* Expanded question details */}
      {expanded && data.questions && (
        <div className="px-3 pb-3 pl-10 space-y-2">
          <p className="text-xs text-slate-500 mb-2">{config.description}</p>
          {data.questions.map((q, i) => (
            <div key={q.question_id || i} className="flex items-start gap-2 text-xs">
              <div className={clsx(
                'w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0',
                q.score >= 0.75 ? 'bg-green-400' :
                q.score >= 0.5 ? 'bg-amber-400' : 'bg-red-400'
              )} />
              <div className="flex-1">
                <p className="text-slate-600">{q.question}</p>
                <p className="text-slate-400 mt-0.5">
                  {q.level} ({Math.round(q.score * 100)}%) - {q.explanation}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Full quality report panel
 */
export function QualityReport({ quality, onClose }) {
  const [expandedDims, setExpandedDims] = useState(new Set());
  
  if (!quality || !quality.report) return null;
  
  const report = quality.report;
  const verdict = quality.verdict;
  const colors = GRADE_COLORS[report.overall_grade] || GRADE_COLORS.C;
  
  const toggleDimension = (dim) => {
    setExpandedDims(prev => {
      const next = new Set(prev);
      if (next.has(dim)) next.delete(dim);
      else next.add(dim);
      return next;
    });
  };
  
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-lg overflow-hidden">
      {/* Header */}
      <div className={clsx('px-4 py-3 border-b', colors.bg)}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={clsx(
              'w-12 h-12 rounded-xl flex items-center justify-center font-bold text-2xl',
              colors.bg, colors.text, 'border-2', colors.border
            )}>
              {report.overall_grade}
            </div>
            <div>
              <h3 className="font-semibold text-slate-800">Quality Assessment</h3>
              <p className="text-sm text-slate-600">
                {report.rubric} - {Math.round(report.overall_score * 100)}% overall
              </p>
            </div>
          </div>
          
          {/* Verdict badge */}
          <div className={clsx(
            'px-3 py-1 rounded-full text-xs font-semibold',
            verdict === 'pass' ? 'bg-green-100 text-green-700' :
            verdict === 'improve' ? 'bg-amber-100 text-amber-700' :
            verdict === 'escalate' ? 'bg-red-100 text-red-700' :
            'bg-slate-100 text-slate-600'
          )}>
            {verdict === 'pass' ? 'PASSED' :
             verdict === 'improve' ? 'NEEDS IMPROVEMENT' :
             verdict === 'escalate' ? 'ESCALATED' : verdict?.toUpperCase()}
          </div>
        </div>
      </div>
      
      {/* Dimensions */}
      <div className="divide-y divide-slate-100">
        {report.dimensions && Object.entries(report.dimensions).map(([key, dim]) => (
          <DimensionRow
            key={key}
            dimensionKey={key}
            data={dim}
            expanded={expandedDims.has(key)}
            onToggle={() => toggleDimension(key)}
          />
        ))}
      </div>
      
      {/* Insights */}
      {(report.strengths?.length > 0 || report.weaknesses?.length > 0 || report.suggestions?.length > 0) && (
        <div className="px-4 py-3 bg-slate-50 border-t border-slate-200 space-y-3">
          {/* Strengths */}
          {report.strengths?.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-green-700 flex items-center gap-1 mb-1">
                <TrendingUp size={12} />
                Strengths
              </h4>
              <ul className="space-y-0.5">
                {report.strengths.map((s, i) => (
                  <li key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                    <CheckCircle2 size={10} className="text-green-500 mt-0.5 flex-shrink-0" />
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Weaknesses */}
          {report.weaknesses?.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-red-700 flex items-center gap-1 mb-1">
                <TrendingDown size={12} />
                Areas for Improvement
              </h4>
              <ul className="space-y-0.5">
                {report.weaknesses.map((w, i) => (
                  <li key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                    <AlertTriangle size={10} className="text-amber-500 mt-0.5 flex-shrink-0" />
                    {w}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Suggestions */}
          {report.suggestions?.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-blue-700 flex items-center gap-1 mb-1">
                <Lightbulb size={12} />
                Suggestions
              </h4>
              <ul className="space-y-0.5">
                {report.suggestions.map((s, i) => (
                  <li key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                    <Lightbulb size={10} className="text-blue-500 mt-0.5 flex-shrink-0" />
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      {/* Footer */}
      <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-400">
        <span>Evaluated in {report.evaluation_time_ms?.toFixed(0)}ms</span>
        <span>Rubric Quality Gate v1.0</span>
      </div>
    </div>
  );
}

/**
 * Main export: compact badge + expandable report
 */
export default function QualityBadge({ quality, compact = false }) {
  const [showReport, setShowReport] = useState(false);
  
  if (!quality || quality.error || !quality.report) {
    return null;
  }
  
  const report = quality.report;
  
  return (
    <div className="relative">
      <GradeBadge
        grade={report.overall_grade}
        score={report.overall_score}
        onClick={() => setShowReport(!showReport)}
        compact={compact}
      />
      
      {showReport && (
        <div className="absolute right-0 top-full mt-2 z-50 w-96 max-w-[calc(100vw-2rem)]">
          <QualityReport
            quality={quality}
            onClose={() => setShowReport(false)}
          />
          {/* Click outside to close */}
          <div
            className="fixed inset-0 -z-10"
            onClick={() => setShowReport(false)}
          />
        </div>
      )}
    </div>
  );
}
