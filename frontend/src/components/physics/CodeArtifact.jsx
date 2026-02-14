/**
 * PATH: frontend/src/components/physics/CodeArtifact.jsx
 * PURPOSE: Jupyter-like code artifact with execution and output display
 * 
 * FEATURES:
 * - Syntax highlighted code blocks via Shiki
 * - Execute Python/JavaScript code (via Pyodide)
 * - Display outputs (text, plots, data)
 * - Collapsible cells
 * - Copy/Download functionality
 */

import { useState, useCallback, useEffect } from 'react';
import {
  Play,
  Copy,
  Check,
  Download,
  ChevronDown,
  ChevronRight,
  Terminal,
  Code,
  FileCode,
  Loader2,
  AlertCircle,
  CheckCircle2,
  X,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { clsx } from 'clsx';
import { useShiki } from '../../hooks/useShiki';

const languageConfig = {
  python: {
    name: 'Python',
    icon: '🐍',
    color: 'from-blue-500 to-yellow-500',
  },
  javascript: {
    name: 'JavaScript',
    icon: '📜',
    color: 'from-yellow-400 to-yellow-600',
  },
  typescript: {
    name: 'TypeScript',
    icon: '📘',
    color: 'from-blue-500 to-blue-700',
  },
  latex: {
    name: 'LaTeX',
    icon: '📐',
    color: 'from-green-500 to-teal-500',
  },
  sympy: {
    name: 'SymPy',
    icon: '∫',
    color: 'from-purple-500 to-pink-500',
  },
  bash: {
    name: 'Bash',
    icon: '💻',
    color: 'from-gray-600 to-gray-800',
  },
  json: {
    name: 'JSON',
    icon: '{}',
    color: 'from-orange-400 to-orange-600',
  },
  markdown: {
    name: 'Markdown',
    icon: '📝',
    color: 'from-slate-500 to-slate-700',
  },
  sql: {
    name: 'SQL',
    icon: '🗃️',
    color: 'from-cyan-500 to-cyan-700',
  },
};

function CodeCell({ 
  code, 
  language = 'python', 
  executionCount = null,
  output = null,
  error = null,
  onExecute,
  onCopy,
  editable = false,
  onChange
}) {
  const [isRunning, setIsRunning] = useState(false);
  const [copied, setCopied] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [highlightedCode, setHighlightedCode] = useState('');
  
  const { highlight, isReady: shikiReady } = useShiki();
  const config = languageConfig[language] || languageConfig.python;
  
  // Update highlighted code when Shiki is ready or code changes
  useEffect(() => {
    if (shikiReady && code) {
      const html = highlight(code, language, 'dark');
      setHighlightedCode(html);
    }
  }, [code, language, shikiReady, highlight]);
  
  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    onCopy?.();
  };
  
  const handleExecute = async () => {
    if (isRunning || !onExecute) return;
    setIsRunning(true);
    try {
      await onExecute(code, language);
    } finally {
      setIsRunning(false);
    }
  };
  
  const handleDownload = () => {
    const ext = language === 'python' ? 'py' : language === 'javascript' ? 'js' : 'txt';
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `code.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={clsx(
      'code-artifact rounded-xl overflow-hidden border shadow-sm transition-all',
      error ? 'border-red-300 bg-red-50/30' : 'border-slate-200 bg-white'
    )}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1 hover:bg-slate-200 rounded transition-colors"
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronDown size={16} />}
          </button>
          
          <div className={clsx(
            'w-6 h-6 rounded flex items-center justify-center text-xs bg-gradient-to-br text-white',
            config.color
          )}>
            {config.icon}
          </div>
          
          <span className="text-sm font-medium text-slate-700">{config.name}</span>
          
          {executionCount !== null && (
            <span className="text-xs text-slate-400 font-mono">
              In [{executionCount}]
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-1">
          {onExecute && (
            <button
              onClick={handleExecute}
              disabled={isRunning}
              className={clsx(
                'p-1.5 rounded transition-colors',
                isRunning 
                  ? 'bg-amber-100 text-amber-600' 
                  : 'hover:bg-green-100 text-green-600'
              )}
              title="Run code"
            >
              {isRunning ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Play size={16} />
              )}
            </button>
          )}
          
          <button
            onClick={handleCopy}
            className="p-1.5 hover:bg-slate-200 rounded transition-colors"
            title="Copy code"
          >
            {copied ? (
              <Check size={16} className="text-green-500" />
            ) : (
              <Copy size={16} className="text-slate-500" />
            )}
          </button>
          
          <button
            onClick={handleDownload}
            className="p-1.5 hover:bg-slate-200 rounded transition-colors"
            title="Download"
          >
            <Download size={16} className="text-slate-500" />
          </button>
          
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1.5 hover:bg-slate-200 rounded transition-colors"
            title={expanded ? 'Minimize' : 'Expand'}
          >
            {expanded ? (
              <Minimize2 size={16} className="text-slate-500" />
            ) : (
              <Maximize2 size={16} className="text-slate-500" />
            )}
          </button>
        </div>
      </div>
      
      {/* Code */}
      {!collapsed && (
        <div className={clsx(
          'overflow-x-auto shiki-container',
          expanded ? 'max-h-none' : 'max-h-96'
        )}>
          {highlightedCode ? (
            // Shiki-highlighted code
            <div 
              className="shiki-code text-sm leading-relaxed"
              dangerouslySetInnerHTML={{ __html: highlightedCode }} 
            />
          ) : (
            // Fallback while Shiki loads
            <pre className="p-4 text-sm font-mono leading-relaxed bg-slate-900 text-slate-100 overflow-x-auto">
              <code>{code}</code>
            </pre>
          )}
        </div>
      )}
      
      {/* Output */}
      {!collapsed && (output || error) && (
        <div className="border-t border-slate-200">
          {executionCount !== null && (
            <div className="px-4 py-1 bg-slate-50 text-xs text-slate-400 font-mono">
              Out [{executionCount}]
            </div>
          )}
          
          {error ? (
            <div className="p-4 bg-red-50">
              <div className="flex items-center gap-2 text-red-700 mb-2">
                <AlertCircle size={16} />
                <span className="font-medium">Error</span>
              </div>
              <pre className="text-sm text-red-600 font-mono whitespace-pre-wrap">
                {error}
              </pre>
            </div>
          ) : output ? (
            <div className="p-4 bg-slate-50">
              {typeof output === 'string' ? (
                <pre className="text-sm font-mono text-slate-700 whitespace-pre-wrap">
                  {output}
                </pre>
              ) : output.type === 'rich' ? (
                /* Rich output: text + matplotlib plots */
                <div className="space-y-4">
                  {output.text && (
                    <pre className="text-sm font-mono text-slate-700 whitespace-pre-wrap">
                      {output.text}
                    </pre>
                  )}
                  {output.plots && output.plots.map((plotSrc, i) => (
                    <div key={i} className="flex justify-center">
                      <img 
                        src={plotSrc} 
                        alt={`Plot ${i + 1}`} 
                        className="max-w-full rounded-lg border border-slate-200 shadow-sm"
                      />
                    </div>
                  ))}
                </div>
              ) : output.type === 'plot' ? (
                <div className="flex justify-center">
                  <img 
                    src={output.data} 
                    alt="Plot output" 
                    className="max-w-full rounded-lg border border-slate-200"
                  />
                </div>
              ) : output.type === 'table' ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="bg-slate-100">
                        {output.headers.map((h, i) => (
                          <th key={i} className="px-4 py-2 text-left font-medium text-slate-700">
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200">
                      {output.rows.map((row, i) => (
                        <tr key={i}>
                          {row.map((cell, j) => (
                            <td key={j} className="px-4 py-2 text-slate-600 font-mono">
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-slate-600">{JSON.stringify(output, null, 2)}</div>
              )}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}

// Notebook-style container
function NotebookContainer({ cells, onExecute, onAddCell }) {
  return (
    <div className="notebook-container space-y-4">
      {cells.map((cell, index) => (
        <CodeCell
          key={cell.id || index}
          code={cell.code}
          language={cell.language}
          executionCount={cell.executionCount}
          output={cell.output}
          error={cell.error}
          onExecute={onExecute ? (code, lang) => onExecute(index, code, lang) : undefined}
        />
      ))}
      
      {onAddCell && (
        <button
          onClick={onAddCell}
          className="w-full py-3 border-2 border-dashed border-slate-300 rounded-xl text-slate-500 hover:border-accent-primary hover:text-accent-primary transition-colors flex items-center justify-center gap-2"
        >
          <Code size={18} />
          Add Code Cell
        </button>
      )}
    </div>
  );
}

export default CodeCell;
export { NotebookContainer };
