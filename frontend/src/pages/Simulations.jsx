/**
 * PATH: frontend/src/pages/Simulations.jsx
 * PURPOSE: Physics simulation interface with parameter controls and visualization
 */

import { useState } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  Download,
  Settings,
  Atom,
  Activity,
  Zap,
  ChevronDown,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { clsx } from 'clsx';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const models = [
  { 
    id: 'harmonic_oscillator', 
    name: 'Harmonic Oscillator', 
    icon: Activity,
    description: 'Simple/damped harmonic motion',
    params: [
      { name: 'mass', label: 'Mass (kg)', default: 1.0, min: 0.1, max: 100 },
      { name: 'spring_constant', label: 'Spring Constant (N/m)', default: 4.0, min: 0.1, max: 100 },
      { name: 'damping', label: 'Damping Coefficient', default: 0.0, min: 0, max: 10 },
    ],
    initial: [
      { name: 'x', label: 'Initial Position (m)', default: 1.0 },
      { name: 'v', label: 'Initial Velocity (m/s)', default: 0.0 },
    ]
  },
  { 
    id: 'pendulum', 
    name: 'Pendulum', 
    icon: Atom,
    description: 'Simple pendulum motion',
    params: [
      { name: 'length', label: 'Length (m)', default: 1.0, min: 0.1, max: 10 },
      { name: 'mass', label: 'Mass (kg)', default: 1.0, min: 0.1, max: 100 },
      { name: 'gravity', label: 'Gravity (m/s²)', default: 9.81, min: 1, max: 20 },
    ],
    initial: [
      { name: 'theta', label: 'Initial Angle (rad)', default: 0.5 },
      { name: 'omega', label: 'Initial Angular Velocity', default: 0.0 },
    ]
  },
  { 
    id: 'projectile_motion', 
    name: 'Projectile Motion', 
    icon: Zap,
    description: 'Projectile with optional drag',
    params: [
      { name: 'mass', label: 'Mass (kg)', default: 1.0, min: 0.1, max: 100 },
      { name: 'drag_coefficient', label: 'Drag Coefficient', default: 0.0, min: 0, max: 1 },
      { name: 'gravity', label: 'Gravity (m/s²)', default: 9.81, min: 1, max: 20 },
    ],
    initial: [
      { name: 'x', label: 'Initial X (m)', default: 0.0 },
      { name: 'y', label: 'Initial Y (m)', default: 0.0 },
      { name: 'vx', label: 'Initial Vx (m/s)', default: 10.0 },
      { name: 'vy', label: 'Initial Vy (m/s)', default: 10.0 },
    ]
  },
];

function ParameterInput({ param, value, onChange }) {
  return (
    <div className="space-y-1">
      <label className="text-sm text-light-600">{param.label}</label>
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(param.name, parseFloat(e.target.value) || 0)}
        step={0.1}
        min={param.min}
        max={param.max}
        className="input text-sm py-2"
      />
    </div>
  );
}

export default function Simulations() {
  const [selectedModel, setSelectedModel] = useState(models[0]);
  const [params, setParams] = useState(() => {
    const initial = {};
    models[0].params.forEach(p => initial[p.name] = p.default);
    return initial;
  });
  const [initialConditions, setInitialConditions] = useState(() => {
    const initial = {};
    models[0].initial.forEach(p => initial[p.name] = p.default);
    return initial;
  });
  const [duration, setDuration] = useState(10);
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleModelChange = (model) => {
    setSelectedModel(model);
    const newParams = {};
    model.params.forEach(p => newParams[p.name] = p.default);
    setParams(newParams);
    const newInitial = {};
    model.initial.forEach(p => newInitial[p.name] = p.default);
    setInitialConditions(newInitial);
    setResults(null);
    setError(null);
  };

  const handleParamChange = (name, value) => {
    setParams(prev => ({ ...prev, [name]: value }));
  };

  const handleInitialChange = (name, value) => {
    setInitialConditions(prev => ({ ...prev, [name]: value }));
  };

  const runSimulation = async () => {
    setIsRunning(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5002/api/v1/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: selectedModel.id,
          parameters: params,
          initial_conditions: initialConditions,
          t_end: duration,
          dt: 0.01,
          method: 'rk4'
        }),
      });

      if (!response.ok) {
        throw new Error('Simulation failed');
      }

      const data = await response.json();
      
      // Transform data for chart
      const chartData = data.times?.map((t, i) => ({
        time: t,
        ...Object.fromEntries(
          Object.keys(data.states?.[i] || {}).map(key => [key, data.states[i][key]])
        )
      })) || [];

      setResults({
        data: chartData,
        conservation: data.conservation_violations || [],
        metadata: data.metadata || {}
      });
    } catch (err) {
      setError('Failed to run simulation. Make sure the API server is running.');
      
      // Generate mock data for demo
      const mockData = [];
      for (let t = 0; t <= duration; t += 0.1) {
        if (selectedModel.id === 'harmonic_oscillator') {
          const omega = Math.sqrt(params.spring_constant / params.mass);
          mockData.push({
            time: t,
            x: initialConditions.x * Math.cos(omega * t),
            v: -initialConditions.x * omega * Math.sin(omega * t)
          });
        } else if (selectedModel.id === 'pendulum') {
          const omega = Math.sqrt(params.gravity / params.length);
          mockData.push({
            time: t,
            theta: initialConditions.theta * Math.cos(omega * t),
            omega: -initialConditions.theta * omega * Math.sin(omega * t)
          });
        } else {
          mockData.push({
            time: t,
            x: initialConditions.x + initialConditions.vx * t,
            y: initialConditions.y + initialConditions.vy * t - 0.5 * params.gravity * t * t
          });
        }
      }
      setResults({ data: mockData, conservation: [], metadata: { demo: true } });
    } finally {
      setIsRunning(false);
    }
  };

  const resetSimulation = () => {
    setResults(null);
    setError(null);
    handleModelChange(selectedModel);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-light-900">Physics Simulations</h1>
          <p className="text-light-500 text-sm">Run and visualize physics models with real-time data</p>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={resetSimulation}
            className="btn-secondary flex items-center gap-2"
          >
            <RotateCcw size={16} />
            Reset
          </button>
          <button 
            onClick={runSimulation}
            disabled={isRunning}
            className={clsx(
              'btn-primary flex items-center gap-2',
              isRunning && 'opacity-50 cursor-not-allowed'
            )}
          >
            {isRunning ? <Pause size={16} /> : <Play size={16} />}
            {isRunning ? 'Running...' : 'Run Simulation'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel - Model Selection & Parameters */}
        <div className="space-y-4">
          {/* Model Selection */}
          <div className="card">
            <h3 className="font-medium text-light-800 mb-3">Select Model</h3>
            <div className="space-y-2">
              {models.map((model) => (
                <button
                  key={model.id}
                  onClick={() => handleModelChange(model)}
                  className={clsx(
                    'w-full flex items-center gap-3 p-3 rounded-lg border transition-all text-left',
                    selectedModel.id === model.id
                      ? 'border-accent-primary bg-accent-primary/5'
                      : 'border-light-300 hover:border-light-400 hover:bg-light-100'
                  )}
                >
                  <div className={clsx(
                    'w-10 h-10 rounded-lg flex items-center justify-center',
                    selectedModel.id === model.id
                      ? 'bg-accent-primary text-white'
                      : 'bg-light-200 text-light-500'
                  )}>
                    <model.icon size={20} />
                  </div>
                  <div>
                    <p className={clsx(
                      'font-medium text-sm',
                      selectedModel.id === model.id ? 'text-accent-primary' : 'text-light-700'
                    )}>
                      {model.name}
                    </p>
                    <p className="text-xs text-light-500">{model.description}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Parameters */}
          <div className="card">
            <h3 className="font-medium text-light-800 mb-3">Parameters</h3>
            <div className="space-y-3">
              {selectedModel.params.map((param) => (
                <ParameterInput
                  key={param.name}
                  param={param}
                  value={params[param.name]}
                  onChange={handleParamChange}
                />
              ))}
            </div>
          </div>

          {/* Initial Conditions */}
          <div className="card">
            <h3 className="font-medium text-light-800 mb-3">Initial Conditions</h3>
            <div className="space-y-3">
              {selectedModel.initial.map((param) => (
                <ParameterInput
                  key={param.name}
                  param={param}
                  value={initialConditions[param.name]}
                  onChange={handleInitialChange}
                />
              ))}
              <div className="space-y-1">
                <label className="text-sm text-light-600">Duration (s)</label>
                <input
                  type="number"
                  value={duration}
                  onChange={(e) => setDuration(parseFloat(e.target.value) || 10)}
                  step={1}
                  min={1}
                  max={100}
                  className="input text-sm py-2"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Visualization */}
        <div className="lg:col-span-2 space-y-4">
          {/* Chart */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-light-800">Simulation Results</h3>
              {results && (
                <div className="flex items-center gap-2">
                  {results.conservation?.length === 0 ? (
                    <span className="badge-green flex items-center gap-1">
                      <CheckCircle2 size={12} />
                      Energy Conserved
                    </span>
                  ) : (
                    <span className="badge-yellow flex items-center gap-1">
                      <AlertTriangle size={12} />
                      Conservation Violations
                    </span>
                  )}
                </div>
              )}
            </div>

            {error && (
              <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700 text-sm">
                {error}
              </div>
            )}

            {results ? (
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={results.data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                    <XAxis 
                      dataKey="time" 
                      stroke="#737373"
                      fontSize={12}
                      tickFormatter={(v) => v.toFixed(1)}
                    />
                    <YAxis stroke="#737373" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#ffffff', 
                        border: '1px solid #e5e5e5',
                        borderRadius: '8px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                      }}
                      labelStyle={{ color: '#262626' }}
                    />
                    <Legend />
                    {Object.keys(results.data[0] || {}).filter(k => k !== 'time').map((key, i) => (
                      <Line
                        key={key}
                        type="monotone"
                        dataKey={key}
                        stroke={['#10a37f', '#5436da', '#ec4899', '#f59e0b'][i % 4]}
                        strokeWidth={2}
                        dot={false}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-80 flex items-center justify-center text-light-400">
                <div className="text-center">
                  <Atom size={48} className="mx-auto mb-3 text-light-300" />
                  <p>Run a simulation to see results</p>
                </div>
              </div>
            )}
          </div>

          {/* Metadata */}
          {results && (
            <div className="card">
              <h3 className="font-medium text-light-800 mb-3">Simulation Metadata</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-light-500">Model</p>
                  <p className="text-sm text-light-700">{selectedModel.name}</p>
                </div>
                <div>
                  <p className="text-xs text-light-500">Data Points</p>
                  <p className="text-sm text-light-700">{results.data.length}</p>
                </div>
                <div>
                  <p className="text-xs text-light-500">Duration</p>
                  <p className="text-sm text-light-700">{duration}s</p>
                </div>
                <div>
                  <p className="text-xs text-light-500">Method</p>
                  <p className="text-sm text-light-700">{results.metadata?.demo ? 'Demo' : 'RK4'}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
