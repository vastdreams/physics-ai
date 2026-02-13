/**
 * PATH: frontend/src/pages/Equations.jsx
 * PURPOSE: Symbolic equation solver interface
 */

import { useState } from 'react';
import {
  Calculator,
  Play,
  Copy,
  Check,
  BookOpen,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { clsx } from 'clsx';
import { API_BASE } from '../config';

const exampleEquations = [
  { equation: 'F = m * a', variables: { F: 100, m: 10 }, solveFor: 'a', description: "Newton's Second Law" },
  { equation: 'E = m * c**2', variables: { m: 1 }, solveFor: 'E', description: 'Mass-Energy Equivalence' },
  { equation: 'x**2 - 4 = 0', variables: {}, solveFor: 'x', description: 'Quadratic Equation' },
  { equation: 'v = v0 + a*t', variables: { v0: 0, a: 9.81, t: 2 }, solveFor: 'v', description: 'Kinematic Equation' },
];

export default function Equations() {
  const [equation, setEquation] = useState('F = m * a');
  const [variables, setVariables] = useState('{"F": 100, "m": 10}');
  const [solveFor, setSolveFor] = useState('a');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleSolve = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const varsObj = JSON.parse(variables);
      
      const response = await fetch(`${API_BASE}/api/v1/equations/solve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          equation,
          variables: varsObj,
          solve_for: solveFor,
        }),
      });

      if (!response.ok) {
        throw new Error('Solver request failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      // Generate mock result for demo
      let mockResult;
      if (equation.includes('F = m * a') && solveFor === 'a') {
        const vars = JSON.parse(variables);
        mockResult = {
          solutions: [vars.F / vars.m],
          method: 'symbolic',
          steps: [
            'Starting equation: F = m * a',
            `Substituting F = ${vars.F}, m = ${vars.m}`,
            `${vars.F} = ${vars.m} * a`,
            `a = ${vars.F} / ${vars.m}`,
            `a = ${vars.F / vars.m}`
          ]
        };
      } else if (equation.includes('x**2 - 4 = 0')) {
        mockResult = {
          solutions: [-2, 2],
          method: 'symbolic',
          steps: [
            'Starting equation: x² - 4 = 0',
            'Factor: (x - 2)(x + 2) = 0',
            'Solutions: x = 2 or x = -2'
          ]
        };
      } else {
        mockResult = {
          solutions: ['Demo result'],
          method: 'demo',
          steps: ['API not connected, showing demo result']
        };
      }
      setResult(mockResult);
      setError('Note: Using demo solver. Start the API for full functionality.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExample = (example) => {
    setEquation(example.equation);
    setVariables(JSON.stringify(example.variables, null, 2));
    setSolveFor(example.solveFor);
    setResult(null);
    setError(null);
  };

  const handleCopy = () => {
    if (result) {
      navigator.clipboard.writeText(JSON.stringify(result, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-light-900">Equation Solver</h1>
        <p className="text-light-500 text-sm">Symbolic mathematics with step-by-step solutions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Panel */}
        <div className="lg:col-span-2 space-y-4">
          <div className="card">
            <h3 className="font-medium text-light-800 mb-4">Enter Equation</h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm text-light-600 mb-1 block">Equation</label>
                <input
                  type="text"
                  value={equation}
                  onChange={(e) => setEquation(e.target.value)}
                  placeholder="e.g., F = m * a"
                  className="input font-mono"
                />
                <p className="text-xs text-light-400 mt-1">
                  Use ** for exponents, e.g., x**2 for x²
                </p>
              </div>

              <div>
                <label className="text-sm text-light-600 mb-1 block">Known Variables (JSON)</label>
                <textarea
                  value={variables}
                  onChange={(e) => setVariables(e.target.value)}
                  placeholder='{"F": 100, "m": 10}'
                  rows={3}
                  className="input font-mono text-sm"
                />
              </div>

              <div>
                <label className="text-sm text-light-600 mb-1 block">Solve For</label>
                <input
                  type="text"
                  value={solveFor}
                  onChange={(e) => setSolveFor(e.target.value)}
                  placeholder="e.g., a"
                  className="input font-mono"
                />
              </div>

              <button
                onClick={handleSolve}
                disabled={isLoading}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                ) : (
                  <Calculator size={18} />
                )}
                Solve Equation
              </button>
            </div>
          </div>

          {/* Result */}
          {(result || error) && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-light-800">Solution</h3>
                <button 
                  onClick={handleCopy}
                  className="btn-ghost text-sm"
                >
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700 text-sm">
                  {error}
                </div>
              )}

              {result && (
                <div className="space-y-4">
                  {/* Solutions */}
                  <div className="p-4 bg-accent-primary/5 border border-accent-primary/20 rounded-lg">
                    <p className="text-sm text-light-500 mb-1">Solutions</p>
                    <div className="flex flex-wrap gap-2">
                      {result.solutions?.map((sol, i) => (
                        <span key={i} className="px-3 py-1 bg-white rounded-lg text-lg font-mono text-accent-primary shadow-sm">
                          {solveFor} = {typeof sol === 'number' ? sol.toFixed(4) : sol}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Steps */}
                  {result.steps && (
                    <div>
                      <p className="text-sm text-light-500 mb-2">Solution Steps</p>
                      <div className="space-y-2">
                        {result.steps.map((step, i) => (
                          <div key={i} className="flex items-start gap-3">
                            <span className="w-6 h-6 rounded-full bg-light-200 text-light-600 text-xs flex items-center justify-center flex-shrink-0">
                              {i + 1}
                            </span>
                            <span className="text-light-700 font-mono text-sm">{step}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Method */}
                  <div className="flex items-center gap-2 text-sm text-light-400">
                    <Sparkles size={14} />
                    Solved using {result.method} method
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Examples Panel */}
        <div className="space-y-4">
          <div className="card">
            <h3 className="font-medium text-light-800 mb-3">Example Equations</h3>
            <div className="space-y-2">
              {exampleEquations.map((example, i) => (
                <button
                  key={i}
                  onClick={() => handleExample(example)}
                  className="w-full flex items-center gap-3 p-3 bg-light-100 hover:bg-light-200 rounded-lg text-left transition-colors group"
                >
                  <div className="w-8 h-8 rounded-lg bg-light-200 group-hover:bg-accent-primary/10 flex items-center justify-center transition-colors">
                    <BookOpen size={16} className="text-light-500 group-hover:text-accent-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-mono text-light-700 truncate">{example.equation}</p>
                    <p className="text-xs text-light-400">{example.description}</p>
                  </div>
                  <ChevronRight size={14} className="text-light-400" />
                </button>
              ))}
            </div>
          </div>

          {/* Quick Reference */}
          <div className="card">
            <h3 className="font-medium text-light-800 mb-3">Syntax Reference</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-light-500">Addition</span>
                <code className="text-light-700">a + b</code>
              </div>
              <div className="flex justify-between">
                <span className="text-light-500">Subtraction</span>
                <code className="text-light-700">a - b</code>
              </div>
              <div className="flex justify-between">
                <span className="text-light-500">Multiplication</span>
                <code className="text-light-700">a * b</code>
              </div>
              <div className="flex justify-between">
                <span className="text-light-500">Division</span>
                <code className="text-light-700">a / b</code>
              </div>
              <div className="flex justify-between">
                <span className="text-light-500">Exponent</span>
                <code className="text-light-700">a ** b</code>
              </div>
              <div className="flex justify-between">
                <span className="text-light-500">Square Root</span>
                <code className="text-light-700">sqrt(a)</code>
              </div>
              <div className="flex justify-between">
                <span className="text-light-500">Sine</span>
                <code className="text-light-700">sin(a)</code>
              </div>
              <div className="flex justify-between">
                <span className="text-light-500">Cosine</span>
                <code className="text-light-700">cos(a)</code>
              </div>
            </div>
          </div>

          {/* Constants */}
          <div className="card">
            <h3 className="font-medium text-light-800 mb-3">Physical Constants</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-light-500">Speed of Light</span>
                <code className="text-light-700">c = 299792458</code>
              </div>
              <div className="flex justify-between">
                <span className="text-light-500">Planck's Constant</span>
                <code className="text-light-700">h = 6.626e-34</code>
              </div>
              <div className="flex justify-between">
                <span className="text-light-500">Gravity</span>
                <code className="text-light-700">g = 9.81</code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
