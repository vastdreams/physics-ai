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
          Open Source Project
        </div>
        <h1 className="text-4xl font-bold text-light-900 mb-4">
          Building AI to Explore the<br />
          <span className="bg-gradient-to-r from-accent-primary to-accent-purple bg-clip-text text-transparent">
            Frontiers of Physics
          </span>
        </h1>
        <p className="text-xl text-light-500 max-w-2xl mx-auto mb-8">
          Physics AI is a self-evolving neurosymbolic intelligence designed to explore, 
          unify, and expand humanity's understanding of the physical universe.
        </p>
        <blockquote className="italic text-light-600 border-l-4 border-accent-primary pl-4 inline-block text-left">
          "The most incomprehensible thing about the universe is that it is comprehensible."
          <footer className="text-sm text-light-400 mt-1">— Albert Einstein</footer>
        </blockquote>
      </section>

      {/* The Problem */}
      <section className="card">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-red-50 flex items-center justify-center">
            <Target size={20} className="text-red-500" />
          </div>
          <h2 className="text-2xl font-semibold text-light-900">The Problem</h2>
        </div>
        
        <p className="text-light-600 mb-6">
          Physics has a unification problem. For a century, we've had two incompatible 
          frameworks describing reality:
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

        <p className="text-light-600">
          Despite the efforts of brilliant minds—Einstein, Hawking, Witten—we haven't reconciled them. 
          String theory remains unverified. Loop quantum gravity is incomplete. The Standard Model 
          has 19 free parameters we can't derive from first principles.
        </p>

        <div className="mt-6 p-4 rounded-xl bg-amber-50 border border-amber-200">
          <h4 className="font-medium text-amber-800 mb-2">Why hasn't AI helped?</h4>
          <ul className="text-sm text-amber-700 space-y-1">
            <li>• <strong>Neural networks</strong> recognize patterns but can't derive equations</li>
            <li>• <strong>Symbolic systems</strong> manipulate symbols but can't discover patterns</li>
            <li>• <strong>Neither</strong> can improve themselves based on physics constraints</li>
          </ul>
        </div>
      </section>

      {/* Our Approach */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
            <Lightbulb size={20} className="text-accent-primary" />
          </div>
          <h2 className="text-2xl font-semibold text-light-900">Our Approach</h2>
        </div>

        <p className="text-light-600 mb-8">
          Physics AI combines three capabilities no existing system has together:
        </p>

        <div className="grid md:grid-cols-2 gap-6">
          <CapabilityCard
            icon={Brain}
            title="Neurosymbolic Reasoning"
            description="Fuses neural pattern recognition with symbolic equation manipulation. The AI sees patterns like a neural network but reasons like a mathematician."
            color="blue"
          />
          <CapabilityCard
            icon={Network}
            title="Unified Physics Graph"
            description="Connects classical, quantum, relativistic, and statistical physics through symmetries, correspondences, and limiting cases."
            color="purple"
          />
          <CapabilityCard
            icon={GitBranch}
            title="Self-Evolution"
            description="Analyzes and improves its own code within physics-constrained boundaries. Safe, validated modifications with human oversight."
            color="green"
          />
          <CapabilityCard
            icon={Users}
            title="Human-AI Collaboration"
            description="Augments physicists rather than replacing them. The best discoveries will come from humans and AI working together."
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
                <th className="text-center py-3 px-4 text-light-500 font-medium">Physics AI</th>
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
            description="Physics AI is a tool for physicists, not a replacement. The best discoveries will come from working together."
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
              'Neurosymbolic engine with hybrid reasoning',
              'Four reasoning types (deductive, inductive, abductive, analogical)',
              'Physics equation solver with SymPy integration',
              'Simulation models with conservation validation',
              'REST API (41 endpoints) + WebSocket',
              'Modern web dashboard'
            ]}
          />
          <RoadmapPhase
            phase={2}
            title="Enhancement"
            status="progress"
            items={[
              'Cross-domain reasoning (connect QM ↔ GR)',
              'Hypothesis generation from knowledge gaps',
              'arXiv paper ingestion pipeline',
              'Uncertainty quantification (VECTOR framework)',
              'Transformer-based physics embeddings'
            ]}
          />
          <RoadmapPhase
            phase={3}
            title="Synthesis"
            status="planned"
            items={[
              'Theory unification proposals',
              'Anomaly detection in physical theories',
              'Experimental guidance suggestions',
              'Multi-agent physics debate system'
            ]}
          />
          <RoadmapPhase
            phase={4}
            title="Discovery"
            status="vision"
            items={[
              'Novel prediction generation',
              'Mathematical structure discovery',
              'Autonomous research assistance',
              'Physics breakthrough collaboration'
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
          Physics isn't just an academic pursuit. Understanding fundamental laws has given us:
        </p>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center p-3">
            <div className="text-2xl mb-1">⚡</div>
            <div className="text-sm text-light-700">Electronics</div>
            <div className="text-xs text-light-400">Quantum mechanics</div>
          </div>
          <div className="text-center p-3">
            <div className="text-2xl mb-1">📡</div>
            <div className="text-sm text-light-700">GPS</div>
            <div className="text-xs text-light-400">Relativity corrections</div>
          </div>
          <div className="text-center p-3">
            <div className="text-2xl mb-1">⚛️</div>
            <div className="text-sm text-light-700">Nuclear Energy</div>
            <div className="text-xs text-light-400">E=mc²</div>
          </div>
          <div className="text-center p-3">
            <div className="text-2xl mb-1">🏥</div>
            <div className="text-sm text-light-700">MRI</div>
            <div className="text-xs text-light-400">Quantum spin</div>
          </div>
        </div>

        <p className="text-light-700 font-medium text-center">
          The next breakthrough—whether it's quantum gravity, dark matter, or something we haven't 
          imagined—could transform civilization. We're building the AI to help find it.
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
            href="https://github.com/vastdreams/physics-ai"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary flex items-center gap-2"
          >
            <Code2 size={18} />
            View on GitHub
            <ExternalLink size={14} />
          </a>
          <a
            href="https://github.com/vastdreams/physics-ai/blob/main/CONTRIBUTING.md"
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
