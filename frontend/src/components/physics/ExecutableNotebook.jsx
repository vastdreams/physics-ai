/**
 * PATH: frontend/src/components/physics/ExecutableNotebook.jsx
 * PURPOSE: Executable Jupyter-like notebook with Pyodide Python support
 * 
 * WHY: Combines CodeArtifact UI with Pyodide execution engine
 * to create a fully interactive Python notebook in the browser.
 * 
 * FLOW:
 * ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
 * │ User types  │───▶│ Click Run    │───▶│ Pyodide     │
 * │ Python code │    │ button       │    │ executes    │
 * └─────────────┘    └──────────────┘    └─────────────┘
 *                                               │
 *                                               ▼
 *                                        ┌─────────────┐
 *                                        │ Display     │
 *                                        │ output      │
 *                                        └─────────────┘
 * 
 * FEATURES:
 * - Live Python execution via Pyodide
 * - Persistent state across cells
 * - Package installation
 * - Loading indicator during Pyodide init
 */

import { useState, useCallback } from 'react';
import { Loader2, Package, AlertCircle, CheckCircle2 } from 'lucide-react';
import { clsx } from 'clsx';
import CodeCell, { NotebookContainer } from './CodeArtifact';
import { usePyodide, formatPythonOutput, formatPythonError } from '../../hooks/usePyodide';

/**
 * ExecutableNotebook - Interactive Python notebook
 */
export function ExecutableNotebook({ initialCells = [], className }) {
  const { runPython, installPackage, isReady, isLoading, loadingMessage, error } = usePyodide();
  const [cells, setCells] = useState(() => 
    initialCells.map((cell, index) => ({
      id: cell.id || `cell-${index}`,
      code: cell.code || '',
      language: cell.language || 'python',
      output: null,
      error: null,
      executionCount: null,
    }))
  );
  const [executionCounter, setExecutionCounter] = useState(1);
  
  /**
   * Execute a cell's code
   */
  const handleExecute = useCallback(async (cellIndex, code, language) => {
    if (language !== 'python' && language !== 'sympy') {
      // For non-Python languages, show a message
      setCells(prev => prev.map((cell, i) => 
        i === cellIndex 
          ? { ...cell, output: `Execution not supported for ${language}`, error: null }
          : cell
      ));
      return;
    }
    
    // Update cell to show running state
    setCells(prev => prev.map((cell, i) => 
      i === cellIndex 
        ? { ...cell, output: null, error: null }
        : cell
    ));
    
    // Execute the code
    const result = await runPython(code);
    const currentCount = executionCounter;
    setExecutionCounter(prev => prev + 1);
    
    // Update cell with result
    setCells(prev => prev.map((cell, i) => {
      if (i !== cellIndex) return cell;
      
      if (result.success) {
        return {
          ...cell,
          output: formatPythonOutput(result),
          error: null,
          executionCount: currentCount,
        };
      } else {
        return {
          ...cell,
          output: null,
          error: formatPythonError(result),
          executionCount: currentCount,
        };
      }
    }));
  }, [runPython, executionCounter]);
  
  /**
   * Add a new cell
   */
  const handleAddCell = useCallback(() => {
    setCells(prev => [
      ...prev,
      {
        id: `cell-${Date.now()}`,
        code: '',
        language: 'python',
        output: null,
        error: null,
        executionCount: null,
      }
    ]);
  }, []);
  
  /**
   * Update cell code
   */
  const handleCellChange = useCallback((cellIndex, newCode) => {
    setCells(prev => prev.map((cell, i) => 
      i === cellIndex ? { ...cell, code: newCode } : cell
    ));
  }, []);
  
  // Show loading state while Pyodide initializes
  if (isLoading) {
    return (
      <div className={clsx('p-6 rounded-xl border border-slate-200 bg-slate-50', className)}>
        <div className="flex items-center gap-3 text-slate-600">
          <Loader2 className="animate-spin" size={20} />
          <div>
            <div className="font-medium">Initializing Python environment...</div>
            <div className="text-sm text-slate-500">{loadingMessage}</div>
          </div>
        </div>
      </div>
    );
  }
  
  // Show error if Pyodide failed to load
  if (error) {
    return (
      <div className={clsx('p-6 rounded-xl border border-red-200 bg-red-50', className)}>
        <div className="flex items-center gap-3 text-red-700">
          <AlertCircle size={20} />
          <div>
            <div className="font-medium">Failed to initialize Python</div>
            <div className="text-sm text-red-600">{error}</div>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className={clsx('executable-notebook', className)}>
      {/* Status indicator */}
      <div className="flex items-center gap-2 mb-4 text-sm">
        <CheckCircle2 size={16} className="text-green-500" />
        <span className="text-slate-600">Python environment ready</span>
      </div>
      
      {/* Notebook cells */}
      <NotebookContainer
        cells={cells}
        onExecute={handleExecute}
        onAddCell={handleAddCell}
      />
    </div>
  );
}

/**
 * Standalone executable code cell
 */
export function ExecutableCodeCell({ 
  code, 
  language = 'python',
  className 
}) {
  const { runPython, isReady, isLoading, error } = usePyodide();
  const [output, setOutput] = useState(null);
  const [cellError, setCellError] = useState(null);
  const [executionCount, setExecutionCount] = useState(null);
  const [counter, setCounter] = useState(1);
  
  const handleExecute = useCallback(async (cellCode, cellLang) => {
    if (cellLang !== 'python' && cellLang !== 'sympy') {
      setOutput(`Execution not supported for ${cellLang}`);
      setCellError(null);
      return;
    }
    
    const result = await runPython(cellCode);
    setExecutionCount(counter);
    setCounter(prev => prev + 1);
    
    if (result.success) {
      setOutput(formatPythonOutput(result));
      setCellError(null);
    } else {
      setOutput(null);
      setCellError(formatPythonError(result));
    }
  }, [runPython, counter]);
  
  return (
    <div className={className}>
      {isLoading && (
        <div className="flex items-center gap-2 mb-2 text-sm text-slate-500">
          <Loader2 className="animate-spin" size={14} />
          <span>Loading Python...</span>
        </div>
      )}
      <CodeCell
        code={code}
        language={language}
        output={output}
        error={cellError}
        executionCount={executionCount}
        onExecute={isReady ? handleExecute : undefined}
      />
    </div>
  );
}

export default ExecutableNotebook;
