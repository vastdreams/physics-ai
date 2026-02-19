/**
 * PATH: frontend/src/pages/Documentation.jsx
 * PURPOSE: Comprehensive documentation page — getting started, API reference,
 *          architecture, physics models, and more. Publicly accessible.
 */

import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  Book,
  Code2,
  Terminal,
  Atom,
  Brain,
  GitBranch,
  Database,
  Cpu,
  Shield,
  Zap,
  Search,
  ChevronRight,
  ExternalLink,
  Copy,
  Check,
  ArrowRight,
  Layers,
  BookOpen,
  Workflow,
  Globe,
  Key,
  Server,
  FileJson,
} from 'lucide-react';

/* ── Code block with copy button ─────────────────────────────── */
function CodeBlock({ code, language = 'bash', title }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <div className="rounded-xl border border-slate-200 overflow-hidden my-4 bg-slate-50">
      {title && (
        <div className="flex items-center justify-between px-4 py-2 bg-slate-100/80 border-b border-slate-200">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
          <span className="text-[10px] text-slate-400 font-mono">{language}</span>
        </div>
      )}
      <div className="relative">
        <pre className="p-4 overflow-x-auto text-sm leading-relaxed">
          <code className="text-slate-700 font-mono">{code}</code>
        </pre>
        <button
          onClick={handleCopy}
          className="absolute top-3 right-3 p-1.5 rounded-lg bg-white border border-slate-200 text-slate-400 hover:text-slate-600 hover:border-slate-300 transition-all"
        >
          {copied ? <Check size={14} className="text-emerald-500" /> : <Copy size={14} />}
        </button>
      </div>
    </div>
  );
}

/* ── Endpoint card ───────────────────────────────────────────── */
function Endpoint({ method, path, description, body, response }) {
  const [open, setOpen] = useState(false);
  const methodColor = {
    GET: 'bg-emerald-50 text-emerald-600 border-emerald-200',
    POST: 'bg-blue-50 text-blue-600 border-blue-200',
    PUT: 'bg-amber-50 text-amber-600 border-amber-200',
    DELETE: 'bg-red-50 text-red-600 border-red-200',
  };
  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden mb-3">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-50 transition-colors text-left"
      >
        <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-md border ${methodColor[method] || 'bg-slate-50 text-slate-600 border-slate-200'}`}>
          {method}
        </span>
        <code className="text-sm font-mono text-slate-700 flex-1">{path}</code>
        <span className="text-xs text-slate-400 hidden sm:inline">{description}</span>
        <ChevronRight size={14} className={`text-slate-400 transition-transform ${open ? 'rotate-90' : ''}`} />
      </button>
      {open && (
        <div className="px-4 pb-4 border-t border-slate-100 bg-slate-50/50">
          <p className="text-sm text-slate-600 mt-3 mb-3">{description}</p>
          {body && <CodeBlock code={body} language="json" title="Request Body" />}
          {response && <CodeBlock code={response} language="json" title="Response" />}
        </div>
      )}
    </div>
  );
}

/* ── Sidebar table of contents ───────────────────────────────── */
const sections = [
  { id: 'getting-started', label: 'Getting Started', icon: Zap },
  { id: 'installation', label: 'Installation', icon: Terminal },
  { id: 'quick-start', label: 'Quick Start', icon: Code2 },
  { id: 'architecture', label: 'Architecture', icon: Layers },
  { id: 'physics-engine', label: 'Physics Engine', icon: Atom },
  { id: 'reasoning', label: 'Reasoning Engine', icon: Brain },
  { id: 'rule-engine', label: 'Rule Engine', icon: Database },
  { id: 'self-evolution', label: 'Self-Evolution', icon: GitBranch },
  { id: 'knowledge-graph', label: 'Knowledge Graph', icon: Globe },
  { id: 'api-reference', label: 'API Reference', icon: FileJson },
  { id: 'authentication', label: 'Authentication', icon: Key },
  { id: 'websockets', label: 'WebSockets', icon: Workflow },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'deployment', label: 'Deployment', icon: Server },
  { id: 'contributing', label: 'Contributing', icon: BookOpen },
];

function TableOfContents({ activeSection }) {
  return (
    <nav className="space-y-0.5">
      {sections.map((s) => {
        const Icon = s.icon;
        const isActive = activeSection === s.id;
        return (
          <a
            key={s.id}
            href={`#${s.id}`}
            className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-all ${
              isActive
                ? 'bg-indigo-50 text-indigo-600 font-semibold'
                : 'text-slate-500 hover:text-slate-800 hover:bg-slate-50'
            }`}
          >
            <Icon size={14} className={isActive ? 'text-indigo-500' : 'text-slate-400'} />
            {s.label}
          </a>
        );
      })}
    </nav>
  );
}

/* ── Section heading ─────────────────────────────────────────── */
function SectionHeading({ id, icon: Icon, children }) {
  return (
    <h2 id={id} className="flex items-center gap-3 text-2xl font-black text-slate-900 mt-16 mb-6 scroll-mt-24">
      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center flex-shrink-0">
        <Icon size={18} className="text-white" />
      </div>
      {children}
    </h2>
  );
}

function SubHeading({ children }) {
  return <h3 className="text-lg font-bold text-slate-800 mt-8 mb-3">{children}</h3>;
}

function P({ children }) {
  return <p className="text-slate-600 leading-relaxed mb-4">{children}</p>;
}

function InfoCard({ title, children, gradient = 'from-indigo-500 to-violet-600' }) {
  return (
    <div className="card-glass p-5 mb-4">
      <div className={`text-sm font-bold text-transparent bg-clip-text bg-gradient-to-r ${gradient} mb-2`}>{title}</div>
      <div className="text-sm text-slate-600 leading-relaxed">{children}</div>
    </div>
  );
}

/* ================================================================== */
/*  Documentation Page                                                  */
/* ================================================================== */
export default function Documentation() {
  const [activeSection, setActiveSection] = useState('getting-started');
  const [searchQuery, setSearchQuery] = useState('');

  // Track active section on scroll
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        }
      },
      { rootMargin: '-20% 0px -70% 0px' }
    );
    sections.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  return (
    <div className="min-h-screen bg-white">
      {/* ── Top navigation ─────────────────────────────────────── */}
      <nav className="fixed top-0 inset-x-0 z-50 flex items-center justify-between px-8 py-4 glass-nav">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md">
            <Sparkles size={20} className="text-white" />
          </div>
          <span className="font-bold text-slate-900 text-lg tracking-tight">Beyond Frontier</span>
        </Link>
        <div className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-500">
          <Link to="/" className="hover:text-slate-900 transition-colors">Home</Link>
          <span className="text-indigo-600 font-semibold">Docs</span>
          <a href="https://github.com/vastdreams/physics-ai" target="_blank" rel="noopener noreferrer" className="hover:text-slate-900 transition-colors flex items-center gap-1">
            GitHub <ExternalLink size={12} />
          </a>
          <Link to="/signup" className="btn-fancy text-sm px-5 py-2">
            Get Started
          </Link>
        </div>
      </nav>

      {/* ── Hero ───────────────────────────────────────────────── */}
      <div className="pt-28 pb-12 px-6 text-center relative overflow-hidden">
        <div className="mesh-bg absolute inset-0 -z-10 opacity-50" />
        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-indigo-50 text-indigo-600 rounded-full text-sm font-semibold mb-6">
          <Book size={14} />
          v2.0.0 Documentation
        </div>
        <h1 className="text-4xl md:text-5xl font-black text-slate-900 mb-4">
          Beyond Frontier <span className="gradient-text-animated">Documentation</span>
        </h1>
        <p className="text-lg text-slate-500 max-w-2xl mx-auto mb-8">
          Everything you need to get started with the neurosymbolic physics engine —
          from installation to advanced API usage.
        </p>
        {/* Search */}
        <div className="max-w-md mx-auto relative">
          <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documentation..."
            className="w-full pl-11 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-700 placeholder-slate-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all shadow-sm"
          />
        </div>
      </div>

      {/* ── Main content with sidebar ──────────────────────────── */}
      <div className="max-w-7xl mx-auto px-6 pb-24 flex gap-10">
        {/* Sticky sidebar TOC */}
        <aside className="hidden lg:block w-56 flex-shrink-0">
          <div className="sticky top-24">
            <p className="text-[10px] uppercase tracking-widest font-bold text-slate-400 mb-3 px-3">On this page</p>
            <TableOfContents activeSection={activeSection} />
          </div>
        </aside>

        {/* Content */}
        <main className="flex-1 min-w-0 max-w-3xl">

          {/* ── GETTING STARTED ─────────────────────────────────── */}
          <SectionHeading id="getting-started" icon={Zap}>Getting Started</SectionHeading>
          <P>
            Beyond Frontier is a self-evolving neurosymbolic physics engine. It combines neural pattern
            recognition with symbolic reasoning to solve physics problems, run simulations, manage
            knowledge, and even improve its own code.
          </P>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <InfoCard title="Free & Open Source" gradient="from-emerald-500 to-teal-600">
              MIT licensed. No API keys or credit cards needed. Fork it, extend it, use it.
            </InfoCard>
            <InfoCard title="Full-Stack" gradient="from-indigo-500 to-violet-600">
              Python backend with Flask, React frontend, WebSocket real-time updates, 41+ REST endpoints.
            </InfoCard>
            <InfoCard title="Self-Evolving" gradient="from-amber-500 to-orange-600">
              The AI can analyze and improve its own code through evolutionary optimization with safety rails.
            </InfoCard>
          </div>

          <SubHeading>Prerequisites</SubHeading>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
            {[
              { name: 'Python 3.10+', note: '3.11 recommended' },
              { name: 'Node.js 18+', note: 'For the frontend' },
              { name: 'Git', note: 'For version control' },
            ].map((p) => (
              <div key={p.name} className="flex items-center gap-2 px-4 py-3 bg-slate-50 rounded-xl border border-slate-200">
                <Check size={14} className="text-emerald-500" />
                <div>
                  <span className="text-sm font-semibold text-slate-700">{p.name}</span>
                  <span className="text-xs text-slate-400 ml-1">({p.note})</span>
                </div>
              </div>
            ))}
          </div>

          {/* ── INSTALLATION ────────────────────────────────────── */}
          <SectionHeading id="installation" icon={Terminal}>Installation</SectionHeading>

          <SubHeading>1. Clone & Setup</SubHeading>
          <CodeBlock title="Terminal" language="bash" code={`# Clone the repository
git clone https://github.com/vastdreams/physics-ai.git
cd physics-ai

# Create Python virtual environment
python -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\\Scripts\\activate    # Windows

# Install Python dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env`} />

          <SubHeading>2. Frontend Setup</SubHeading>
          <CodeBlock title="Terminal" language="bash" code={`cd frontend
npm install
npm run dev      # Development server at http://localhost:3000`} />

          <SubHeading>3. Start the Backend</SubHeading>
          <CodeBlock title="Terminal" language="bash" code={`# From the project root
python -m api.app

# API available at http://localhost:5002
# Health check: curl http://localhost:5002/health
# API docs:     http://localhost:5002/api/docs`} />

          <SubHeading>Environment Variables</SubHeading>
          <P>Copy <code className="text-sm bg-slate-100 px-1.5 py-0.5 rounded font-mono text-indigo-600">.env.example</code> to <code className="text-sm bg-slate-100 px-1.5 py-0.5 rounded font-mono text-indigo-600">.env</code> and configure:</P>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-slate-200 rounded-xl overflow-hidden mb-4">
              <thead>
                <tr className="bg-slate-50">
                  <th className="text-left px-4 py-2 font-semibold text-slate-700">Variable</th>
                  <th className="text-left px-4 py-2 font-semibold text-slate-700">Description</th>
                  <th className="text-left px-4 py-2 font-semibold text-slate-700">Default</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  ['SECRET_KEY', 'JWT signing key', 'Auto-generated'],
                  ['ADMIN_EMAIL', 'Default admin email', 'admin@beyondfrontier.local'],
                  ['ADMIN_PASSWORD', 'Default admin password', 'change-me-in-production'],
                  ['REDIS_URL', 'Redis cache URL', 'redis://localhost:6379/0'],
                  ['DEEPSEEK_API_KEY', 'DeepSeek API key for AI features', '(optional)'],
                  ['CORS_ORIGINS', 'Allowed CORS origins', '* (all)'],
                  ['PORT', 'Backend port', '5002'],
                ].map(([k, d, v]) => (
                  <tr key={k} className="hover:bg-slate-50">
                    <td className="px-4 py-2 font-mono text-xs text-indigo-600">{k}</td>
                    <td className="px-4 py-2 text-slate-600">{d}</td>
                    <td className="px-4 py-2 text-slate-400 font-mono text-xs">{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* ── QUICK START ─────────────────────────────────────── */}
          <SectionHeading id="quick-start" icon={Code2}>Quick Start</SectionHeading>

          <SubHeading>Solve Equations</SubHeading>
          <CodeBlock title="Python" language="python" code={`from physics.equations import EquationSolver

solver = EquationSolver()

# Solve F = ma for acceleration
result = solver.solve(
    equation="F = m * a",
    variables={'F': 100, 'm': 10},
    solve_for='a'
)
print(result.solutions)  # [10.0]`} />

          <SubHeading>Run Simulations</SubHeading>
          <CodeBlock title="Python" language="python" code={`from physics.models import HarmonicOscillator

oscillator = HarmonicOscillator(mass=1.0, spring_constant=4.0)
result = oscillator.simulate(
    initial_conditions={'x': 1.0, 'v': 0.0},
    t_end=10.0,
    dt=0.01
)

# Energy is automatically validated for conservation
print(f"Energy conserved: {len(result.conservation_violations) == 0}")`} />

          <SubHeading>Use Reasoning</SubHeading>
          <CodeBlock title="Python" language="python" code={`from core.reasoning import ReasoningEngineImpl, ReasoningType

reasoner = ReasoningEngineImpl(ReasoningType.DEDUCTIVE)
result = reasoner.reason([
    "is_particle -> has_mass",
    "electron -> is_particle",
    "electron"
])
# Concludes: electron has_mass`} />

          <SubHeading>Call the API</SubHeading>
          <CodeBlock title="cURL" language="bash" code={`# Run a simulation
curl -X POST http://localhost:5002/api/v1/simulate \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "harmonic_oscillator",
    "parameters": {"mass": 1.0, "spring_constant": 4.0},
    "initial_conditions": {"x": 1.0, "v": 0.0},
    "t_end": 10.0
  }'

# Add a rule
curl -X POST http://localhost:5002/api/v1/rules \\
  -H "Content-Type: application/json" \\
  -d '{"name": "test_rule", "condition": {}, "action": {"$return": "success"}}'`} />

          {/* ── ARCHITECTURE ────────────────────────────────────── */}
          <SectionHeading id="architecture" icon={Layers}>Architecture</SectionHeading>
          <P>
            Beyond Frontier uses a layered architecture where each layer can be used independently or
            composed together. Higher layers build on lower layers.
          </P>
          <div className="font-mono text-sm bg-slate-50 border border-slate-200 rounded-xl p-6 mb-6 leading-relaxed overflow-x-auto">
            <div className="text-indigo-600 font-bold">DISCOVERY    </div>
            <div className="text-slate-400 text-xs mb-1 ml-4">Theory proposal, gap analysis, anomaly detection</div>
            <div className="text-violet-600 font-bold">RESEARCH     </div>
            <div className="text-slate-400 text-xs mb-1 ml-4">Validation, calculations, paper analysis</div>
            <div className="text-blue-600 font-bold">REASONING    </div>
            <div className="text-slate-400 text-xs mb-1 ml-4">Neural + Symbolic + Self-Evolution</div>
            <div className="text-emerald-600 font-bold">KNOWLEDGE    </div>
            <div className="text-slate-400 text-xs mb-1 ml-4">Unified physics graph, equations, constants</div>
            <div className="text-amber-600 font-bold">COMPUTATION  </div>
            <div className="text-slate-400 text-xs ml-4">Symbolic solvers, numerical integration, RK4</div>
          </div>

          <SubHeading>Core Components</SubHeading>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            {[
              { name: 'Neurosymbolic Engine', path: 'core/', desc: 'Neural-symbolic hybrid integration, decision making, knowledge synthesis' },
              { name: 'Rule System', path: 'rules/', desc: 'Dynamic rule storage, execution, conflict resolution, pattern matching' },
              { name: 'Evolution Module', path: 'evolution/', desc: 'Code analysis, safe self-modification, performance selection' },
              { name: 'Physics Integration', path: 'physics/', desc: 'Domain models, equation solving, conservation validation' },
              { name: 'VECTOR Framework', path: 'utilities/', desc: 'Variance throttling, Bayesian updates, attention, overlay validation' },
              { name: 'REST API', path: 'api/', desc: '41+ endpoints across 11 categories with WebSocket support' },
            ].map((c) => (
              <div key={c.name} className="card-glass p-4">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold text-slate-800">{c.name}</span>
                  <code className="text-[10px] text-indigo-400 bg-indigo-50 px-1.5 py-0.5 rounded">{c.path}</code>
                </div>
                <p className="text-xs text-slate-500">{c.desc}</p>
              </div>
            ))}
          </div>

          <SubHeading>Directory Structure</SubHeading>
          <CodeBlock title="Project Layout" language="text" code={`physics-ai/
├── api/                  # Flask REST API + WebSocket handlers
│   ├── v1/              # Versioned endpoints
│   └── middleware/      # Auth, rate limiting, security, validation
├── core/                 # Neurosymbolic reasoning engine
├── physics/              # Physics models, solvers, domains
│   ├── domains/         # Classical, quantum, fields, statistical
│   ├── solvers/         # Symbolic, numerical, perturbation
│   └── foundations/     # Conservation laws, symmetries
├── rules/                # Rule engine with pattern matching
├── evolution/            # Self-evolution + code generation
├── ai/                   # LLM integration, agents, rubric
├── frontend/             # React + Vite frontend
│   └── src/
│       ├── pages/       # Dashboard, Chat, Simulations, Docs...
│       ├── components/  # Reusable UI components
│       └── hooks/       # Custom React hooks
├── tests/                # Comprehensive test suite
├── docs/                 # Architecture & reference docs
└── data/                 # User data, knowledge store`} />

          {/* ── PHYSICS ENGINE ──────────────────────────────────── */}
          <SectionHeading id="physics-engine" icon={Atom}>Physics Engine</SectionHeading>
          <P>
            The physics engine provides simulation models with automatic conservation law validation,
            multiple integration methods, and domain-specific solvers.
          </P>

          <SubHeading>Available Models</SubHeading>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-slate-200 rounded-xl overflow-hidden mb-6">
              <thead>
                <tr className="bg-slate-50">
                  <th className="text-left px-4 py-2 font-semibold text-slate-700">Model</th>
                  <th className="text-left px-4 py-2 font-semibold text-slate-700">Description</th>
                  <th className="text-left px-4 py-2 font-semibold text-slate-700">Parameters</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  ['harmonic_oscillator', 'Simple/damped harmonic oscillator', 'mass, spring_constant, damping'],
                  ['pendulum', 'Simple pendulum (small & large angle)', 'length, gravity, damping'],
                  ['two_body_gravity', 'Two-body gravitational system', 'masses, positions, velocities'],
                  ['projectile_motion', 'Projectile with optional drag', 'velocity, angle, drag_coefficient'],
                ].map(([m, d, p]) => (
                  <tr key={m} className="hover:bg-slate-50">
                    <td className="px-4 py-2 font-mono text-xs text-indigo-600">{m}</td>
                    <td className="px-4 py-2 text-slate-600">{d}</td>
                    <td className="px-4 py-2 text-slate-400 text-xs">{p}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <SubHeading>Integration Methods</SubHeading>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
            {[
              { name: 'Euler', code: 'euler', desc: 'Fast, less accurate. Good for quick estimates.' },
              { name: 'RK4', code: 'rk4', desc: 'Recommended. 4th-order Runge-Kutta. Best balance of speed and accuracy.' },
              { name: 'RK45 (Adaptive)', code: 'rk45', desc: 'Adaptive step size via scipy. Best for stiff problems.' },
            ].map((m) => (
              <div key={m.code} className="card-glass p-4">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold text-slate-800">{m.name}</span>
                  <code className="text-[10px] text-indigo-400 bg-indigo-50 px-1.5 py-0.5 rounded">{m.code}</code>
                </div>
                <p className="text-xs text-slate-500">{m.desc}</p>
              </div>
            ))}
          </div>

          <SubHeading>Physics Domains</SubHeading>
          <P>561+ equations across 19 domains, connected by derivation chains, constants, and validity conditions:</P>
          <div className="flex flex-wrap gap-2 mb-6">
            {[
              'Classical Mechanics', 'Quantum Mechanics', 'Electromagnetism', 'General Relativity',
              'Thermodynamics', 'Fluid Dynamics', 'Optics', 'Nuclear Physics',
              'Condensed Matter', 'Astrophysics', 'Plasma / MHD', 'Acoustics',
              'Lagrangian Mechanics', 'Hamiltonian Mechanics', 'Gauge Theory',
              'Path Integrals', 'Phase Transitions', 'Perturbation Theory',
              'Statistical Mechanics',
            ].map((d) => (
              <span key={d} className="px-3 py-1 bg-indigo-50 text-indigo-600 rounded-full text-xs font-semibold">
                {d}
              </span>
            ))}
          </div>

          {/* ── REASONING ───────────────────────────────────────── */}
          <SectionHeading id="reasoning" icon={Brain}>Reasoning Engine</SectionHeading>
          <P>
            Four complementary reasoning types that can be composed for complex physics problems:
          </P>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-slate-200 rounded-xl overflow-hidden mb-6">
              <thead>
                <tr className="bg-slate-50">
                  <th className="text-left px-4 py-2 font-semibold text-slate-700">Type</th>
                  <th className="text-left px-4 py-2 font-semibold text-slate-700">Method</th>
                  <th className="text-left px-4 py-2 font-semibold text-slate-700">Use Case</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  ['Deductive', 'Modus ponens, syllogisms', 'Deriving conclusions from known laws'],
                  ['Inductive', 'Pattern generalization', 'Discovering new relationships from data'],
                  ['Abductive', 'Best explanation inference', 'Hypothesis generation from observations'],
                  ['Analogical', 'Structure mapping', 'Cross-domain knowledge transfer'],
                ].map(([t, m, u]) => (
                  <tr key={t} className="hover:bg-slate-50">
                    <td className="px-4 py-2 font-semibold text-slate-700">{t}</td>
                    <td className="px-4 py-2 text-slate-600">{m}</td>
                    <td className="px-4 py-2 text-slate-500">{u}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* ── RULE ENGINE ─────────────────────────────────────── */}
          <SectionHeading id="rule-engine" icon={Database}>Rule Engine</SectionHeading>
          <P>
            A dynamic rule engine with pattern matching, conflict resolution, and physics-aware constraints.
          </P>

          <SubHeading>Condition Operators</SubHeading>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
            {[
              ['$gt / $gte', 'Greater than'], ['$lt / $lte', 'Less than'],
              ['$eq / $ne', 'Equality'], ['$in / $nin', 'Set membership'],
              ['$exists', 'Field exists'], ['$and / $or', 'Logical ops'],
              ['$not', 'Negation'], ['$regex', 'Pattern match'],
            ].map(([op, desc]) => (
              <div key={op} className="px-3 py-2 bg-slate-50 rounded-lg border border-slate-200">
                <code className="text-xs text-indigo-600 font-mono">{op}</code>
                <p className="text-[10px] text-slate-400 mt-0.5">{desc}</p>
              </div>
            ))}
          </div>

          <SubHeading>Action Types</SubHeading>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 mb-6">
            {[
              ['$set', 'Set values'], ['$compute', 'Evaluate expression'], ['$call', 'Call function'],
              ['$remove', 'Remove keys'], ['$return', 'Return value'],
            ].map(([op, desc]) => (
              <div key={op} className="px-3 py-2 bg-slate-50 rounded-lg border border-slate-200">
                <code className="text-xs text-indigo-600 font-mono">{op}</code>
                <p className="text-[10px] text-slate-400 mt-0.5">{desc}</p>
              </div>
            ))}
          </div>

          <CodeBlock title="Example: Kinetic Energy Rule" language="json" code={`{
  "name": "kinetic_energy_rule",
  "condition": {
    "mass": { "$gt": 0 },
    "velocity": { "$exists": true }
  },
  "action": {
    "$compute": {
      "expression": "0.5 * mass * velocity ** 2",
      "target": "kinetic_energy"
    }
  },
  "priority": 10
}`} />

          {/* ── SELF EVOLUTION ──────────────────────────────────── */}
          <SectionHeading id="self-evolution" icon={GitBranch}>Self-Evolution</SectionHeading>
          <P>
            The system can analyze and improve its own code through evolutionary optimization with
            safety guardrails:
          </P>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            {[
              { title: 'Code Analysis', desc: 'AST-based understanding of codebase structure, dependencies, and complexity metrics' },
              { title: 'Safe Modification', desc: 'Validated code generation with automatic rollback on failure or regression' },
              { title: 'Performance Selection', desc: 'Evolutionary improvement based on execution time, accuracy, and resource metrics' },
              { title: 'Dangerous Pattern Detection', desc: 'AST validation prevents injection, infinite loops, and unsafe operations' },
            ].map((f) => (
              <InfoCard key={f.title} title={f.title}>{f.desc}</InfoCard>
            ))}
          </div>

          {/* ── KNOWLEDGE GRAPH ─────────────────────────────────── */}
          <SectionHeading id="knowledge-graph" icon={Globe}>Knowledge Graph</SectionHeading>
          <P>
            A unified physics knowledge graph with 561+ equations, physical constants, derivation
            chains, and cross-domain relationships.
          </P>
          <CodeBlock title="API: Query the Knowledge Graph" language="bash" code={`# Get knowledge graph statistics
curl http://localhost:5002/api/v1/knowledge/statistics

# Search for equations
curl "http://localhost:5002/api/v1/knowledge/search?q=energy&domain=classical"

# Get specific equation details
curl http://localhost:5002/api/v1/knowledge/equations/kinetic_energy`} />

          {/* ── API REFERENCE ───────────────────────────────────── */}
          <SectionHeading id="api-reference" icon={FileJson}>API Reference</SectionHeading>
          <P>
            Full REST API with 41+ endpoints. All endpoints return JSON. Interactive docs available at{' '}
            <code className="text-sm bg-slate-100 px-1.5 py-0.5 rounded font-mono text-indigo-600">/api/docs</code>.
          </P>

          <SubHeading>Simulation</SubHeading>
          <Endpoint method="POST" path="/api/v1/simulate" description="Run a physics simulation"
            body={`{
  "model": "harmonic_oscillator",
  "parameters": { "mass": 1.0, "spring_constant": 4.0 },
  "initial_conditions": { "x": 1.0, "v": 0.0 },
  "t_end": 10.0, "dt": 0.01, "method": "rk4"
}`}
            response={`{
  "success": true,
  "states": [...],
  "times": [...],
  "conservation_violations": []
}`} />

          <SubHeading>Rules</SubHeading>
          <Endpoint method="GET" path="/api/v1/rules" description="List all rules" />
          <Endpoint method="POST" path="/api/v1/rules" description="Create a new rule"
            body={`{
  "name": "my_rule",
  "condition": { "mass": { "$gt": 0 } },
  "action": { "$compute": { "expression": "0.5 * mass * v**2", "target": "KE" } },
  "priority": 10
}`} />
          <Endpoint method="POST" path="/api/v1/rules/execute" description="Execute rules on a context"
            body={`{ "context": { "mass": 10, "v": 5 } }`} />

          <SubHeading>Evolution</SubHeading>
          <Endpoint method="POST" path="/api/v1/evolution/analyze" description="Analyze codebase for improvements"
            body={`{ "directory": "core/", "include_metrics": true }`} />
          <Endpoint method="POST" path="/api/v1/evolution/evolve" description="Evolve a specific function"
            body={`{
  "file_path": "core/engine.py",
  "function_name": "process",
  "improvement_spec": { "type": "optimize", "target": "performance" }
}`} />
          <Endpoint method="GET" path="/api/v1/evolution/history" description="Get evolution history" />

          <SubHeading>Knowledge</SubHeading>
          <Endpoint method="GET" path="/api/v1/knowledge/statistics" description="Get knowledge graph statistics" />
          <Endpoint method="GET" path="/api/v1/knowledge/search?q=energy" description="Search the knowledge base" />
          <Endpoint method="GET" path="/api/v1/knowledge/constants" description="List physical constants" />
          <Endpoint method="GET" path="/api/v1/knowledge/equations" description="List all equations" />

          <SubHeading>Reasoning</SubHeading>
          <Endpoint method="POST" path="/api/v1/reasoning/query" description="Run a reasoning query"
            body={`{ "query": "What is the kinetic energy of a 10kg object at 5 m/s?", "type": "deductive" }`} />

          <SubHeading>Chain-of-Thought</SubHeading>
          <Endpoint method="GET" path="/api/v1/cot/tree" description="Get reasoning tree" />
          <Endpoint method="GET" path="/api/v1/cot/logs?limit=20" description="Get recent CoT logs" />
          <Endpoint method="POST" path="/api/v1/cot/export" description="Export reasoning logs"
            body={`{ "format": "json" }`} />

          <SubHeading>VECTOR Framework</SubHeading>
          <Endpoint method="POST" path="/api/v1/vector/bayesian-update" description="Bayesian parameter update"
            body={`{
  "prior_mean": 1.0,
  "prior_variance": 0.1,
  "observation": 1.05,
  "observation_variance": 0.02
}`} />
          <Endpoint method="POST" path="/api/v1/vector/throttle" description="Apply variance throttling"
            body={`{ "variance": 0.1, "max_variance": 0.5 }`} />

          <SubHeading>Changelog</SubHeading>
          <Endpoint method="GET" path="/api/v1/changelog/latest" description="Latest release notes + commits" />
          <Endpoint method="GET" path="/api/v1/changelog/commits?limit=20" description="Recent git commits" />
          <Endpoint method="POST" path="/api/v1/changelog/generate" description="Generate AI release notes (requires auth)" />

          <SubHeading>System</SubHeading>
          <Endpoint method="GET" path="/health" description="Health check" />
          <Endpoint method="GET" path="/api/v1/system/stats" description="Platform statistics" />
          <Endpoint method="GET" path="/metrics" description="Prometheus metrics" />

          {/* ── AUTHENTICATION ──────────────────────────────────── */}
          <SectionHeading id="authentication" icon={Key}>Authentication</SectionHeading>
          <P>
            JWT-based authentication with access and refresh tokens. No API keys needed — just register
            with email and password.
          </P>
          <Endpoint method="POST" path="/api/v1/auth/register" description="Register a new account"
            body={`{ "name": "Jane Doe", "email": "jane@example.com", "password": "SecurePass123" }`}
            response={`{ "success": true, "message": "User registered successfully", "user": { "id": "...", "email": "jane@example.com", "role": "user" } }`} />
          <Endpoint method="POST" path="/api/v1/auth/login" description="Login and get tokens"
            body={`{ "email": "jane@example.com", "password": "SecurePass123" }`}
            response={`{ "success": true, "access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "Bearer", "expires_in": 3600 }`} />
          <Endpoint method="POST" path="/api/v1/auth/refresh" description="Refresh access token"
            body={`{ "refresh_token": "eyJ..." }`} />
          <Endpoint method="GET" path="/api/v1/auth/me" description="Get current user (requires Bearer token)" />

          <P>
            Include the token in the <code className="text-sm bg-slate-100 px-1.5 py-0.5 rounded font-mono text-indigo-600">Authorization</code> header:
          </P>
          <CodeBlock title="Authenticated Request" language="bash" code={`curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  http://localhost:5002/api/v1/auth/me`} />

          {/* ── WEBSOCKETS ──────────────────────────────────────── */}
          <SectionHeading id="websockets" icon={Workflow}>WebSockets</SectionHeading>
          <P>
            Real-time updates via Socket.IO at <code className="text-sm bg-slate-100 px-1.5 py-0.5 rounded font-mono text-indigo-600">ws://localhost:5002/socket.io/</code>
          </P>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-slate-200 rounded-xl overflow-hidden mb-6">
              <thead>
                <tr className="bg-slate-50">
                  <th className="text-left px-4 py-2 font-semibold text-slate-700">Event</th>
                  <th className="text-left px-4 py-2 font-semibold text-slate-700">Direction</th>
                  <th className="text-left px-4 py-2 font-semibold text-slate-700">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  ['connect', 'Server → Client', 'Connection established'],
                  ['simulation_update', 'Server → Client', 'Real-time simulation progress'],
                  ['evolution_status', 'Server → Client', 'Evolution cycle progress'],
                  ['module_reloaded', 'Server → Client', 'Hot-reloaded module notification'],
                  ['rule_fired', 'Server → Client', 'Rule execution notification'],
                  ['error', 'Server → Client', 'Error notification'],
                ].map(([e, d, desc]) => (
                  <tr key={e} className="hover:bg-slate-50">
                    <td className="px-4 py-2 font-mono text-xs text-indigo-600">{e}</td>
                    <td className="px-4 py-2 text-slate-500 text-xs">{d}</td>
                    <td className="px-4 py-2 text-slate-600">{desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* ── SECURITY ────────────────────────────────────────── */}
          <SectionHeading id="security" icon={Shield}>Security</SectionHeading>
          <P>
            Beyond Frontier includes defense-in-depth security protections:
          </P>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
            {[
              { title: 'Account Lockout', desc: '5 failed login attempts → 15-minute lock per IP and email' },
              { title: 'Rate Limiting', desc: 'Token bucket with 120 req/min global, 10 req/min on auth endpoints' },
              { title: 'Security Headers', desc: 'X-Frame-Options, HSTS, CSP, X-XSS-Protection, Referrer-Policy' },
              { title: 'Input Sanitization', desc: 'HTML stripping, null byte removal, SQL/XSS/command injection detection' },
              { title: 'Password Strength', desc: 'Min 8 chars, uppercase, number required; common passwords blocked' },
              { title: 'Auto IP Ban', desc: '50+ suspicious requests in 5 min → 30-minute IP block' },
              { title: 'Proxy-Aware', desc: 'Uses X-Forwarded-For for real client IP behind Nginx/load balancer' },
              { title: 'Scanner Blocking', desc: 'Auto-blocks probes for .env, wp-admin, phpinfo, path traversal' },
            ].map((s) => (
              <div key={s.title} className="flex items-start gap-3 px-4 py-3 bg-slate-50 rounded-xl border border-slate-200">
                <Shield size={14} className="text-indigo-500 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="text-sm font-semibold text-slate-700">{s.title}</span>
                  <p className="text-xs text-slate-500 mt-0.5">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* ── DEPLOYMENT ──────────────────────────────────────── */}
          <SectionHeading id="deployment" icon={Server}>Deployment</SectionHeading>
          <P>Beyond Frontier runs on any server with Python 3.10+ and Node.js 18+.</P>

          <SubHeading>Production Build</SubHeading>
          <CodeBlock title="Terminal" language="bash" code={`# Build the frontend
cd frontend && npm run build

# The dist/ folder is served by Nginx or Flask
# Set environment variables for production:
export SECRET_KEY="your-secure-random-key"
export ADMIN_PASSWORD="strong-admin-password"
export CORS_ORIGINS="https://yourdomain.com"

# Run with gunicorn (recommended)
gunicorn -w 4 -b 0.0.0.0:5002 "api.app:create_app()"`} />

          <SubHeading>Nginx Configuration</SubHeading>
          <CodeBlock title="nginx.conf" language="nginx" code={`server {
    listen 80;
    server_name yourdomain.com;

    # Frontend (React SPA)
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5002;
    }
}`} />

          {/* ── CONTRIBUTING ────────────────────────────────────── */}
          <SectionHeading id="contributing" icon={BookOpen}>Contributing</SectionHeading>
          <P>
            Beyond Frontier is open source under the MIT License. Contributions are welcome.
          </P>
          <CodeBlock title="Terminal" language="bash" code={`# Fork the repo, then:
git clone https://github.com/YOUR_USERNAME/physics-ai.git
cd physics-ai
git checkout -b feature/your-feature

# Make changes, then:
git add .
git commit -m "Add your feature"
git push origin feature/your-feature

# Open a Pull Request on GitHub`} />

          <SubHeading>Development Guidelines</SubHeading>
          <div className="space-y-2 mb-6">
            {[
              'Code style: Black formatter for Python, Prettier for JS/JSX',
              'All physics models must include conservation law validation',
              'New API endpoints need tests in tests/',
              'Self-evolution changes require AST validation to pass',
              'Security-sensitive changes need manual review',
            ].map((g, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-slate-600">
                <Check size={14} className="text-emerald-500 mt-0.5 flex-shrink-0" />
                {g}
              </div>
            ))}
          </div>

          {/* ── Footer ─────────────────────────────────────────── */}
          <div className="mt-16 pt-8 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-slate-400">
              Beyond Frontier Documentation · v2.0.0 · MIT License
            </p>
            <div className="flex items-center gap-4 text-sm text-slate-500">
              <a href="https://github.com/vastdreams/physics-ai" target="_blank" rel="noopener noreferrer" className="hover:text-slate-800 transition-colors flex items-center gap-1">
                GitHub <ExternalLink size={12} />
              </a>
              <Link to="/signup" className="text-indigo-500 font-semibold hover:text-indigo-600 transition-colors flex items-center gap-1">
                Get Started <ArrowRight size={14} />
              </Link>
            </div>
          </div>

        </main>
      </div>
    </div>
  );
}
