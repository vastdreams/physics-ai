/**
 * PATH: frontend/src/pages/Models.jsx
 * PURPOSE: Browse available physics models
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Atom,
  Activity,
  Zap,
  Orbit,
  Waves,
  Thermometer,
  ArrowRight,
  Search,
  Filter
} from 'lucide-react';
import { clsx } from 'clsx';

const models = [
  {
    id: 'harmonic_oscillator',
    name: 'Harmonic Oscillator',
    icon: Activity,
    category: 'Classical',
    description: 'Simple and damped harmonic motion. Models springs, pendulums (small angle), and LC circuits.',
    equations: ['F = -kx', 'x(t) = A cos(ωt + φ)'],
    parameters: ['mass', 'spring_constant', 'damping'],
    color: 'from-blue-500 to-indigo-600'
  },
  {
    id: 'pendulum',
    name: 'Pendulum',
    icon: Atom,
    category: 'Classical',
    description: 'Simple pendulum supporting both small and large angle approximations.',
    equations: ['θ̈ = -(g/L)sin(θ)', 'T = 2π√(L/g)'],
    parameters: ['length', 'mass', 'gravity'],
    color: 'from-purple-500 to-violet-600'
  },
  {
    id: 'two_body_gravity',
    name: 'Two-Body Gravity',
    icon: Orbit,
    category: 'Classical',
    description: 'Gravitational interaction between two massive bodies. Includes orbital mechanics.',
    equations: ['F = Gm₁m₂/r²', 'E = -Gm₁m₂/r + ½μv²'],
    parameters: ['mass1', 'mass2', 'G'],
    color: 'from-orange-500 to-amber-600'
  },
  {
    id: 'projectile_motion',
    name: 'Projectile Motion',
    icon: Zap,
    category: 'Classical',
    description: 'Projectile trajectory with optional air resistance (drag).',
    equations: ['x = v₀t cos(θ)', 'y = v₀t sin(θ) - ½gt²'],
    parameters: ['mass', 'drag_coefficient', 'gravity'],
    color: 'from-green-500 to-emerald-600'
  },
  {
    id: 'wave_equation',
    name: 'Wave Equation',
    icon: Waves,
    category: 'Fields',
    description: 'One-dimensional wave propagation. Models strings, sound, and electromagnetic waves.',
    equations: ['∂²u/∂t² = c²∂²u/∂x²'],
    parameters: ['wave_speed', 'tension', 'density'],
    color: 'from-cyan-500 to-teal-600'
  },
  {
    id: 'heat_diffusion',
    name: 'Heat Diffusion',
    icon: Thermometer,
    category: 'Statistical',
    description: 'Heat conduction in materials following Fourier\'s law.',
    equations: ['∂T/∂t = α∇²T'],
    parameters: ['thermal_diffusivity', 'initial_temp', 'boundary_temp'],
    color: 'from-red-500 to-pink-600'
  },
];

function ModelCard({ model }) {
  const Icon = model.icon;

  return (
    <Link 
      to={`/simulations?model=${model.id}`}
      className="card group hover:border-light-400 transition-all"
    >
      <div className="flex items-start gap-4">
        <div className={clsx(
          'w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-110',
          model.color
        )}>
          <Icon size={24} className="text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-medium text-light-800 group-hover:text-light-900 transition-colors">
              {model.name}
            </h3>
            <span className="badge-blue text-[10px]">{model.category}</span>
          </div>
          <p className="text-sm text-light-500 mb-3 line-clamp-2">{model.description}</p>
          
          <div className="space-y-2">
            <div>
              <p className="text-xs text-light-400 mb-1">Key Equations</p>
              <div className="flex flex-wrap gap-1">
                {model.equations.map((eq, i) => (
                  <code key={i} className="px-2 py-0.5 bg-light-200 rounded text-xs text-light-700 font-mono">
                    {eq}
                  </code>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs text-light-400 mb-1">Parameters</p>
              <div className="flex flex-wrap gap-1">
                {model.parameters.map((param, i) => (
                  <span key={i} className="px-2 py-0.5 bg-light-100 rounded text-xs text-light-500">
                    {param}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
        <ArrowRight size={18} className="text-light-400 group-hover:text-light-600 group-hover:translate-x-1 transition-all flex-shrink-0" />
      </div>
    </Link>
  );
}

export default function Models() {
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  const categories = ['all', ...new Set(models.map(m => m.category))];

  const filteredModels = models.filter(model => {
    if (categoryFilter !== 'all' && model.category !== categoryFilter) return false;
    if (searchQuery && !model.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-light-900">Physics Models</h1>
        <p className="text-light-500 text-sm">Browse and explore available simulation models</p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-light-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search models..."
            className="input pl-10"
          />
        </div>
        <div className="flex items-center gap-1 p-1 bg-light-200 rounded-lg">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={clsx(
                'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                categoryFilter === cat
                  ? 'bg-white text-light-800 shadow-sm'
                  : 'text-light-500 hover:text-light-700'
              )}
            >
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredModels.map((model) => (
          <ModelCard key={model.id} model={model} />
        ))}
      </div>

      {filteredModels.length === 0 && (
        <div className="card text-center py-12">
          <Atom size={48} className="mx-auto mb-3 text-light-300" />
          <p className="text-light-400">No models found</p>
        </div>
      )}
    </div>
  );
}
