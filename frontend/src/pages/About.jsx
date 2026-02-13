/**
 * PATH: frontend/src/pages/About.jsx
 * PURPOSE: Vision and about page showcasing the project's mission and future direction
 * 
 * FLOW:
 * ┌───────────┐  ┌──────────────┐  ┌─────────────┐
 * │  Mission  │──│  Approach    │──│  Roadmap    │
 * │  Banner   │  │  Cards       │  │  Timeline   │
 * └───────────┘  └──────────────┘  └─────────────┘
 */

import { useState } from 'react';
import {
  Atom,
  Brain,
  GitBranch,
  Sparkles,
  Target,
  Zap,
  Users,
  Shield,
  BookOpen,
  ExternalLink,
  ChevronRight,
  Check,
  Clock,
  Telescope,
  Lightbulb,
  Network,
  Cpu,
  Code2,
  FlaskConical,
  Infinity
} from 'lucide-react';
import { clsx } from 'clsx';

function CapabilityCard({ icon: Icon, title, description, color }) {
  const colors = {
    blue: 'from-blue-500 to-indigo-600',
    purple: 'from-purple-500 to-violet-600',
    green: 'from-green-500 to-emerald-600',
    orange: 'from-orange-500 to-amber-600',
  };

  return (
    <div className="card group hover:border-light-400 transition-all">
      <div className={clsx(
        'w-14 h-14 rounded-xl bg-gradient-to-br flex items-center justify-center mb-4',
        colors[color]
      )}>
        <Icon size={28} className="text-white" />
      </div>
      <h3 className="text-lg font-semibold text-light-900 mb-2">{title}</h3>
      <p className="text-light-500 text-sm leading-relaxed">{description}</p>
    </div>
  );
}

function PrincipleCard({ icon: Icon, title, description }) {
  return (
    <div className="flex gap-4 p-4 rounded-xl hover:bg-light-100 transition-colors">
      <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center flex-shrink-0">
        <Icon size={20} className="text-accent-primary" />
      </div>
      <div>
        <h4 className="font-medium text-light-800 mb-1">{title}</h4>
        <p className="text-sm text-light-500">{description}</p>
      </div>
    </div>
  );
}

function RoadmapPhase({ phase, title, status, items }) {
  const statusStyles = {
    complete: { bg: 'bg-green-100', text: 'text-green-700', icon: Check },
    progress: { bg: 'bg-blue-100', text: 'text-blue-700', icon: Clock },
    planned: { bg: 'bg-purple-100', text: 'text-purple-700', icon: Target },
    vision: { bg: 'bg-orange-100', text: 'text-orange-700', icon: Telescope },
  };

  const style = statusStyles[status];
  const StatusIcon = style.icon;

  return (
    <div className="relative pl-8 pb-8 border-l-2 border-light-200 last:border-transparent">
      <div className={clsx(
        'absolute left-0 -translate-x-1/2 w-8 h-8 rounded-full flex items-center justify-center',
        style.bg
      )}>
        <StatusIcon size={16} className={style.text} />
      </div>
      <div className="ml-4">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-xs font-medium text-light-400">Phase {phase}</span>
          <span className={clsx('badge', style.bg, style.text)}>{title}</span>
        </div>
        <ul className="space-y-2">
          {items.map((item, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-light-600">
              <ChevronRight size={14} className="text-light-400 mt-0.5 flex-shrink-0" />
              {item}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function ProblemCard({ framework, describes, limitation }) {
  return (
    <div className="p-4 rounded-xl bg-light-100 border border-light-200">
      <h4 className="font-semibold text-light-800 mb-1">{framework}</h4>
      <p className="text-sm text-light-600 mb-2">Describes: {describes}</p>
      <p className="text-xs text-light-500">⚠️ {limitation}</p>
    </div>
  );
}

export default function About() {
  return (
    <div className="max-w-5xl mx-auto space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent-primary/10 text-accent-primary text-sm mb-6">
          <Infinity size={16} />
          Open Source Infrastructure
        </div>
        <h1 className="text-4xl font-bold text-light-900 mb-4">
          The Operating System for<br />
          <span className="bg-gradient-to-r from-accent-primary to-accent-purple bg-clip-text text-transparent">
            Physics Research
          </span>
        </h1>
        <p className="text-xl text-light-500 max-w-2xl mx-auto mb-8">
          Beyond Frontier is unified open-source infrastructure that accelerates discovery, 
          validates experiments, proposes theories, and finds the unknown.
        </p>
        <div className="flex flex-wrap justify-center gap-4 text-sm text-light-600">
          <span className="flex items-center gap-1"><Zap size={14} className="text-yellow-500" /> Accelerate</span>
          <span className="flex items-center gap-1"><Check size={14} className="text-green-500" /> Validate</span>
          <span className="flex items-center gap-1"><Lightbulb size={14} className="text-purple-500" /> Propose</span>
          <span className="flex items-center gap-1"><Telescope size={14} className="text-blue-500" /> Discover</span>
        </div>
      </section>

      {/* The Problem */}
      <section className="card">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-red-50 flex items-center justify-center">
            <Target size={20} className="text-red-500" />
          </div>
          <h2 className="text-2xl font-semibold text-light-900">The Problem</h2>
        </div>
        
        <h3 className="font-medium text-light-800 mb-3">Physics Has No Unified Infrastructure</h3>
        <p className="text-light-600 mb-4">
          Every physicist reinvents the wheel. Calculations scatter across tools. Knowledge lives 
          in papers and minds. Discovery is bottlenecked by human bandwidth.
        </p>

        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <ProblemCard 
            framework="Quantum Mechanics"
            describes="The very small (atoms, particles)"
            limitation="Breaks down at large scales"
          />
          <ProblemCard 
            framework="General Relativity"
            describes="The very large (gravity, spacetime)"
            limitation="Breaks down at small scales"
          />
        </div>

        <p className="text-light-600 mb-4">
          For a century, we've had incompatible frameworks. String theory is unverified. 
          The Standard Model has 19 unexplained parameters.
        </p>

        <div className="mt-4 p-4 rounded-xl bg-amber-50 border border-amber-200">
          <h4 className="font-medium text-amber-800 mb-2">Current tools can't help</h4>
          <div className="grid grid-cols-2 gap-2 text-sm text-amber-700">
            <div>• <strong>Mathematica</strong>: No physics reasoning</div>
            <div>• <strong>ChatGPT</strong>: No rigorous derivation</div>
            <div>• <strong>COMSOL</strong>: No theoretical connection</div>
            <div>• <strong>arXiv</strong>: Can't compute or validate</div>
          </div>
        </div>
      </section>

      {/* Our Approach */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
            <Lightbulb size={20} className="text-accent-primary" />
          </div>
          <h2 className="text-2xl font-semibold text-light-900">Layered Infrastructure</h2>
        </div>

        <p className="text-light-600 mb-6">
          Beyond Frontier is built as layered infrastructure. Use it at any level:
        </p>

        {/* Infrastructure Layers */}
        <div className="space-y-3 mb-8">
          <div className="p-4 rounded-xl bg-gradient-to-r from-orange-50 to-orange-100 border border-orange-200">
            <div className="flex items-center gap-3 mb-2">
              <Telescope size={20} className="text-orange-600" />
              <h4 className="font-medium text-orange-800">Discovery Layer</h4>
            </div>
            <p className="text-sm text-orange-700">Theory proposal • Gap analysis • Anomaly detection • Finding the unknown</p>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200">
            <div className="flex items-center gap-3 mb-2">
              <FlaskConical size={20} className="text-purple-600" />
              <h4 className="font-medium text-purple-800">Research Layer</h4>
            </div>
            <p className="text-sm text-purple-700">Experiment validation • Calculation engine • Paper analysis • Research production</p>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200">
            <div className="flex items-center gap-3 mb-2">
              <Brain size={20} className="text-blue-600" />
              <h4 className="font-medium text-blue-800">Reasoning Layer</h4>
            </div>
            <p className="text-sm text-blue-700">Neural patterns + Symbolic proofs + Self-evolution • Thinks like a physicist</p>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-r from-green-50 to-green-100 border border-green-200">
            <div className="flex items-center gap-3 mb-2">
              <Network size={20} className="text-green-600" />
              <h4 className="font-medium text-green-800">Knowledge Layer</h4>
            </div>
            <p className="text-sm text-green-700">Unified physics graph • Equations • Constants • Experimental results</p>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-200">
            <div className="flex items-center gap-3 mb-2">
              <Cpu size={20} className="text-gray-600" />
              <h4 className="font-medium text-gray-800">Computation Layer</h4>
            </div>
            <p className="text-sm text-gray-700">Symbolic solvers • Numerical integration • Perturbation methods • Validation</p>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <CapabilityCard
            icon={GitBranch}
            title="Self-Evolving"
            description="The system improves its own capabilities within physics-constrained boundaries. Safe, validated, human-overseen evolution."
            color="green"
          />
          <CapabilityCard
            icon={Users}
            title="Human-AI Symbiosis"
            description="AI handles computation and pattern-finding. Humans provide intuition and interpretation. Together, we go further."
            color="orange"
          />
        </div>
      </section>

      {/* What Makes Us Different */}
      <section className="card bg-gradient-to-br from-light-50 to-light-100">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
            <Sparkles size={20} className="text-purple-500" />
          </div>
          <h2 className="text-2xl font-semibold text-light-900">What Makes Us Different</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-light-200">
                <th className="text-left py-3 px-4 text-light-500 font-medium">Capability</th>
                <th className="text-center py-3 px-4 text-light-500 font-medium">ChatGPT</th>
                <th className="text-center py-3 px-4 text-light-500 font-medium">Wolfram</th>
                <th className="text-center py-3 px-4 text-light-500 font-medium">Beyond Frontier</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-light-100">
                <td className="py-3 px-4 text-light-700">Pattern Recognition</td>
                <td className="py-3 px-4 text-center text-green-500">✓</td>
                <td className="py-3 px-4 text-center text-red-400">✗</td>
                <td className="py-3 px-4 text-center text-green-500">✓</td>
              </tr>
              <tr className="border-b border-light-100">
                <td className="py-3 px-4 text-light-700">Symbolic Math</td>
                <td className="py-3 px-4 text-center text-red-400">✗</td>
                <td className="py-3 px-4 text-center text-green-500">✓</td>
                <td className="py-3 px-4 text-center text-green-500">✓</td>
              </tr>
              <tr className="border-b border-light-100">
                <td className="py-3 px-4 text-light-700">Physics Constraints</td>
                <td className="py-3 px-4 text-center text-red-400">✗</td>
                <td className="py-3 px-4 text-center text-yellow-500">~</td>
                <td className="py-3 px-4 text-center text-green-500">✓</td>
              </tr>
              <tr className="border-b border-light-100">
                <td className="py-3 px-4 text-light-700">Self-Evolution</td>
                <td className="py-3 px-4 text-center text-red-400">✗</td>
                <td className="py-3 px-4 text-center text-red-400">✗</td>
                <td className="py-3 px-4 text-center text-green-500">✓</td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-light-700">Chain-of-Thought Transparency</td>
                <td className="py-3 px-4 text-center text-yellow-500">~</td>
                <td className="py-3 px-4 text-center text-green-500">✓</td>
                <td className="py-3 px-4 text-center text-green-500">✓</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Principles */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
            <Shield size={20} className="text-blue-500" />
          </div>
          <h2 className="text-2xl font-semibold text-light-900">Guiding Principles</h2>
        </div>

        <div className="grid md:grid-cols-2 gap-2">
          <PrincipleCard
            icon={FlaskConical}
            title="Physics First"
            description="Every capability is grounded in physical constraints. Equations must satisfy conservation laws, dimensional analysis, and known limits."
          />
          <PrincipleCard
            icon={BookOpen}
            title="Transparent Reasoning"
            description="No black boxes. Every conclusion has a chain-of-thought explanation that physicists can verify and critique."
          />
          <PrincipleCard
            icon={Users}
            title="Human-AI Collaboration"
            description="Beyond Frontier is a tool for physicists, not a replacement. The best discoveries will come from working together."
          />
          <PrincipleCard
            icon={Shield}
            title="Safe Evolution"
            description="Self-modification is validated, tested, and reversible. Human oversight at every step."
          />
          <PrincipleCard
            icon={Code2}
            title="Open Science"
            description="MIT-licensed open source. The future of physics shouldn't be locked in a corporate lab."
          />
          <PrincipleCard
            icon={Zap}
            title="First Principles"
            description="Built from mathematical foundations, not heuristics. Every component is traceable to fundamental physics."
          />
        </div>
      </section>

      {/* Roadmap */}
      <section>
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center">
            <Target size={20} className="text-green-500" />
          </div>
          <h2 className="text-2xl font-semibold text-light-900">Roadmap</h2>
        </div>

        <div className="ml-4">
          <RoadmapPhase
            phase={1}
            title="Foundation"
            status="complete"
            items={[
              'Core computation infrastructure (symbolic + numerical)',
              'Basic physics knowledge graph (classical, quantum)',
              'Neurosymbolic reasoning engine',
              'REST API (41 endpoints) + Web dashboard'
            ]}
          />
          <RoadmapPhase
            phase={2}
            title="Knowledge Expansion"
            status="progress"
            items={[
              'Complete Standard Model encoding',
              'General Relativity framework',
              'arXiv paper ingestion pipeline',
              'Experiment database integration',
              'Cross-domain inference (QM ↔ GR connections)'
            ]}
          />
          <RoadmapPhase
            phase={3}
            title="Research Production"
            status="planned"
            items={[
              'Calculation workflows for researchers',
              'Experiment validation tools',
              'Paper analysis and knowledge extraction',
              'Collaboration features'
            ]}
          />
          <RoadmapPhase
            phase={4}
            title="Discovery Infrastructure"
            status="vision"
            items={[
              'Theory proposal generation',
              'Automated gap analysis',
              'Multi-agent theory debate',
              'Novel prediction generation',
              'Experimental guidance for decisive tests'
            ]}
          />
        </div>
      </section>

      {/* Why This Matters */}
      <section className="card bg-gradient-to-br from-accent-primary/5 to-accent-purple/5 border-accent-primary/20">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
            <Infinity size={20} className="text-accent-primary" />
          </div>
          <h2 className="text-2xl font-semibold text-light-900">Why This Matters</h2>
        </div>
        
        <p className="text-light-600 mb-4">
          Every physics breakthrough has transformed civilization:
        </p>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <div className="text-center p-3">
            <div className="text-2xl mb-1">⚡</div>
            <div className="text-sm text-light-700">Electronics</div>
            <div className="text-xs text-light-400">$3T industry</div>
          </div>
          <div className="text-center p-3">
            <div className="text-2xl mb-1">📡</div>
            <div className="text-sm text-light-700">GPS</div>
            <div className="text-xs text-light-400">Global navigation</div>
          </div>
          <div className="text-center p-3">
            <div className="text-2xl mb-1">⚛️</div>
            <div className="text-sm text-light-700">Nuclear</div>
            <div className="text-xs text-light-400">10% of electricity</div>
          </div>
          <div className="text-center p-3">
            <div className="text-2xl mb-1">🏥</div>
            <div className="text-sm text-light-700">MRI</div>
            <div className="text-xs text-light-400">Medical imaging</div>
          </div>
          <div className="text-center p-3">
            <div className="text-2xl mb-1">💡</div>
            <div className="text-sm text-light-700">Lasers</div>
            <div className="text-xs text-light-400">Communication</div>
          </div>
        </div>

        <div className="bg-light-50 rounded-xl p-4 mb-4">
          <h4 className="font-medium text-light-800 mb-2">The bottleneck is discovery speed</h4>
          <p className="text-sm text-light-600">
            Humanity produces more physics papers than any person can read. Calculations that could 
            reveal insights go uncomputed. Connections between fields go unnoticed.
          </p>
        </div>

        <p className="text-light-700 font-medium text-center">
          Beyond Frontier is infrastructure to remove that bottleneck.<br />
          exploring physics at the speed of silicon, not the speed of grad students.
        </p>
      </section>

      {/* Call to Action */}
      <section className="text-center py-8">
        <h2 className="text-2xl font-semibold text-light-900 mb-4">
          The universe is comprehensible.<br />
          Let's comprehend it together.
        </h2>
        <div className="flex items-center justify-center gap-4">
          <a
            href="https://github.com/beyondfrontier/beyondfrontier"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary flex items-center gap-2"
          >
            <Code2 size={18} />
            View on GitHub
            <ExternalLink size={14} />
          </a>
          <a
            href="https://github.com/beyondfrontier/beyondfrontier/blob/main/CONTRIBUTING.md"
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 rounded-lg border border-light-300 text-light-700 hover:bg-light-100 transition-colors flex items-center gap-2"
          >
            <Users size={18} />
            Contribute
          </a>
        </div>
      </section>
    </div>
  );
}
