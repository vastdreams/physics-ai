/**
 * PATH: frontend/src/pages/LandingPage.jsx
 * PURPOSE: Stunning public landing page for Beyond Frontier
 */

import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Brain,
  Atom,
  BookOpen,
  GitBranch,
  MessageSquare,
  Sparkles,
  ArrowRight,
  ChevronDown,
  Check,
  X,
  Zap,
  Network,
  FlaskConical,
  Search,
  Layers,
  Telescope,
} from 'lucide-react';

/* ------------------------------------------------------------------ */
/*  Scroll-triggered animation hook                                    */
/* ------------------------------------------------------------------ */
function useScrollReveal() {
  const ref = useRef(null);
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );
    const el = ref.current;
    if (el) {
      el.querySelectorAll('.reveal').forEach((child) => observer.observe(child));
    }
    return () => observer.disconnect();
  }, []);
  return ref;
}

/* ------------------------------------------------------------------ */
/*  Animated counter                                                   */
/* ------------------------------------------------------------------ */
function Counter({ end, suffix = '', duration = 2000 }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const started = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started.current) {
          started.current = true;
          const startTime = performance.now();
          const animate = (now) => {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            setCount(Math.round(eased * end));
            if (progress < 1) requestAnimationFrame(animate);
          };
          requestAnimationFrame(animate);
        }
      },
      { threshold: 0.5 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [end, duration]);

  return <span ref={ref} className="tabular-nums">{count}{suffix}</span>;
}

/* ------------------------------------------------------------------ */
/*  Feature card with 3D tilt                                          */
/* ------------------------------------------------------------------ */
function FeatureCard({ icon: Icon, title, description, gradient, delay }) {
  const cardRef = useRef(null);

  const handleMouseMove = (e) => {
    const card = cardRef.current;
    if (!card) return;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = ((y - centerY) / centerY) * -8;
    const rotateY = ((x - centerX) / centerX) * 8;
    card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
  };

  const handleMouseLeave = () => {
    if (cardRef.current) {
      cardRef.current.style.transform = 'perspective(800px) rotateX(0) rotateY(0) scale(1)';
    }
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="reveal card-glass group cursor-default"
      style={{ transitionDelay: `${delay}ms`, transition: 'transform 0.15s ease-out, opacity 0.6s ease-out, translate 0.6s ease-out' }}
    >
      <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${gradient} flex items-center justify-center mb-5 shadow-lg group-hover:shadow-xl transition-shadow`}>
        <Icon size={28} className="text-white" />
      </div>
      <h3 className="text-xl font-bold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-500 leading-relaxed">{description}</p>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Architecture layer                                                 */
/* ------------------------------------------------------------------ */
function ArchLayer({ label, description, icon: Icon, gradient, index }) {
  const isEven = index % 2 === 0;
  return (
    <div
      className={`reveal flex items-center gap-6 ${isEven ? 'reveal-left' : 'reveal-right'}`}
      style={{ transitionDelay: `${index * 120}ms` }}
    >
      <div className={`flex-shrink-0 w-16 h-16 rounded-2xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg`}>
        <Icon size={28} className="text-white" />
      </div>
      <div className="flex-1">
        <h4 className="font-bold text-slate-900 text-lg">{label}</h4>
        <p className="text-slate-500 text-sm mt-0.5">{description}</p>
      </div>
      <div className={`hidden md:block h-0.5 w-24 bg-gradient-to-r ${gradient} rounded-full opacity-40`} />
    </div>
  );
}

/* ================================================================== */
/*  Main Landing Page                                                  */
/* ================================================================== */
export default function LandingPage() {
  const containerRef = useScrollReveal();

  return (
    <div ref={containerRef} className="min-h-screen bg-white overflow-x-hidden">
      {/* ── Floating nav ──────────────────────────────────────── */}
      <nav className="fixed top-0 inset-x-0 z-50 flex items-center justify-between px-8 py-4 glass-nav">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md">
            <Sparkles size={20} className="text-white" />
          </div>
          <span className="font-bold text-slate-900 text-lg tracking-tight">Beyond Frontier</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-500">
          <a href="#features" className="hover:text-slate-900 transition-colors">Features</a>
          <a href="#architecture" className="hover:text-slate-900 transition-colors">Architecture</a>
          <a href="#compare" className="hover:text-slate-900 transition-colors">Compare</a>
          <Link to="/docs" className="hover:text-slate-900 transition-colors">Docs</Link>
          <Link to="/signup" className="btn-fancy text-sm px-5 py-2">
            Get Started
          </Link>
        </div>
      </nav>

      {/* ── Hero ──────────────────────────────────────────────── */}
      <section className="relative min-h-screen flex items-center justify-center px-6 pt-24 pb-16">
        {/* Mesh gradient background */}
        <div className="mesh-bg absolute inset-0 -z-10" />
        {/* Floating orbs */}
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="reveal inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-600 text-sm font-medium mb-8">
            <Zap size={14} />
            Open-source physics infrastructure
          </div>

          <h1 className="reveal text-6xl md:text-8xl font-black tracking-tight leading-[0.95] mb-6">
            <span className="gradient-text-animated">Beyond</span>
            <br />
            <span className="gradient-text-animated" style={{ animationDelay: '0.5s' }}>Frontier</span>
          </h1>

          <p className="reveal text-xl md:text-2xl text-slate-500 max-w-2xl mx-auto mb-10 leading-relaxed font-light">
            Pushing physics past the known. A self-evolving engine that accelerates
            discovery, validates experiments, and finds the unknown.
          </p>

          <div className="reveal flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/signup" className="btn-fancy text-lg px-8 py-3.5 shadow-xl shadow-indigo-200/50">
              Get Started Free
              <ArrowRight size={20} className="inline ml-2" />
            </Link>
            <a href="#features" className="btn-ghost-fancy text-lg px-8 py-3.5">
              Explore Features
            </a>
          </div>
        </div>

        {/* Scroll hint */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce text-slate-300">
          <ChevronDown size={28} />
        </div>
      </section>

      {/* ── Trust strip ───────────────────────────────────────── */}
      <section className="py-12 border-y border-slate-100 bg-slate-50/60">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            { end: 50, suffix: '+', label: 'Physics Models' },
            { end: 12, suffix: '', label: 'Solver Engines' },
            { end: 100, suffix: '%', label: 'Open Source' },
            { end: 5, suffix: '', label: 'AI Reasoning Modes' },
          ].map((item) => (
            <div key={item.label}>
              <div className="text-4xl font-black gradient-text-animated">
                <Counter end={item.end} suffix={item.suffix} />
              </div>
              <p className="text-sm text-slate-500 mt-1 font-medium">{item.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Problem ───────────────────────────────────────────── */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="reveal text-4xl md:text-5xl font-black text-slate-900 mb-4">
              Physics has no unified infrastructure
            </h2>
            <p className="reveal text-lg text-slate-500 max-w-2xl mx-auto">
              Calculations scatter across tools. Knowledge lives in papers. Discovery is bottlenecked by human bandwidth.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { name: 'Mathematica', does: 'Symbolic math', cant: 'Reason about physics', color: 'red' },
              { name: 'ChatGPT', does: 'Natural language', cant: 'Rigorous derivation', color: 'green' },
              { name: 'COMSOL', does: 'Simulation', cant: 'Connect to theory', color: 'blue' },
              { name: 'arXiv', does: 'Store papers', cant: 'Compute or validate', color: 'orange' },
            ].map((tool, i) => (
              <div key={tool.name} className="reveal card-glass text-center" style={{ transitionDelay: `${i * 100}ms` }}>
                <h4 className="font-bold text-slate-900 text-lg mb-3">{tool.name}</h4>
                <div className="flex items-center gap-2 justify-center text-sm text-emerald-600 mb-2">
                  <Check size={14} /> {tool.does}
                </div>
                <div className="flex items-center gap-2 justify-center text-sm text-slate-400 line-through">
                  <X size={14} /> {tool.cant}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────── */}
      <section id="features" className="py-24 px-6 bg-slate-50/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="reveal text-4xl md:text-5xl font-black text-slate-900 mb-4">
              Everything you need, unified
            </h2>
            <p className="reveal text-lg text-slate-500 max-w-2xl mx-auto">
              Six pillars of physics infrastructure, working together.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={Brain}
              title="Neurosymbolic Engine"
              description="Neural + symbolic processing with confidence-weighted hybrid integration for physics reasoning."
              gradient="from-violet-500 to-purple-600"
              delay={0}
            />
            <FeatureCard
              icon={BookOpen}
              title="Equation Solver"
              description="Symbolic equation solving with SymPy, step-by-step derivations, and numeric evaluation."
              gradient="from-blue-500 to-indigo-600"
              delay={80}
            />
            <FeatureCard
              icon={Atom}
              title="Live Simulations"
              description="Real-time physics simulations — pendulum, spring-mass, projectile — with Matter.js visualization."
              gradient="from-cyan-500 to-blue-600"
              delay={160}
            />
            <FeatureCard
              icon={Network}
              title="Knowledge Graph"
              description="Unified physics knowledge base connecting concepts, equations, models, and experimental data."
              gradient="from-emerald-500 to-teal-600"
              delay={240}
            />
            <FeatureCard
              icon={GitBranch}
              title="Self-Evolution"
              description="The engine evolves its own code — proposing improvements, validating, and auto-applying changes."
              gradient="from-pink-500 to-rose-600"
              delay={320}
            />
            <FeatureCard
              icon={MessageSquare}
              title="AI Chat Interface"
              description="Conversational physics assistant with Wolfram-style output, proof display, and executable code."
              gradient="from-amber-500 to-orange-600"
              delay={400}
            />
          </div>
        </div>
      </section>

      {/* ── Architecture ──────────────────────────────────────── */}
      <section id="architecture" className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="reveal text-4xl md:text-5xl font-black text-slate-900 mb-4">
              Layered infrastructure
            </h2>
            <p className="reveal text-lg text-slate-500 max-w-xl mx-auto">
              Use it at any layer. Build on top. Accelerate physics at the speed of silicon.
            </p>
          </div>

          <div className="space-y-6">
            <ArchLayer icon={Telescope} label="Discovery" description="Theory proposal, gap analysis, anomaly detection" gradient="from-violet-500 to-purple-600" index={0} />
            <ArchLayer icon={FlaskConical} label="Research" description="Validation, calculations, paper analysis" gradient="from-indigo-500 to-blue-600" index={1} />
            <ArchLayer icon={Brain} label="Reasoning" description="Neural + Symbolic + Self-Evolution" gradient="from-blue-500 to-cyan-600" index={2} />
            <ArchLayer icon={Search} label="Knowledge" description="Unified physics graph, equations, data" gradient="from-cyan-500 to-teal-600" index={3} />
            <ArchLayer icon={Layers} label="Computation" description="Symbolic solvers, numerical integration" gradient="from-emerald-500 to-green-600" index={4} />
          </div>
        </div>
      </section>

      {/* ── Comparison ────────────────────────────────────────── */}
      <section id="compare" className="py-24 px-6 bg-slate-50/50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="reveal text-4xl md:text-5xl font-black text-slate-900 mb-4">
              How we compare
            </h2>
          </div>

          <div className="reveal card-glass overflow-hidden p-0">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="text-left p-4 font-medium text-slate-500">Capability</th>
                  <th className="p-4 font-bold text-center">
                    <span className="gradient-text-animated">Beyond Frontier</span>
                  </th>
                  <th className="p-4 font-medium text-center text-slate-500">ChatGPT</th>
                  <th className="p-4 font-medium text-center text-slate-500">Wolfram</th>
                  <th className="p-4 font-medium text-center text-slate-500">COMSOL</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['Symbolic Solving', true, false, true, false],
                  ['Physics Reasoning', true, 'partial', false, false],
                  ['Live Simulations', true, false, true, true],
                  ['Knowledge Graph', true, false, 'partial', false],
                  ['Self-Evolution', true, false, false, false],
                  ['Natural Language', true, true, false, false],
                  ['Open Source', true, false, false, false],
                  ['Theory Proposal', true, false, false, false],
                ].map(([cap, bf, gpt, wolf, com], i) => (
                  <tr key={cap} className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                    <td className="p-4 text-slate-700 font-medium">{cap}</td>
                    {[bf, gpt, wolf, com].map((val, j) => (
                      <td key={j} className="p-4 text-center">
                        {val === true ? (
                          <span className="inline-flex w-6 h-6 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 items-center justify-center">
                            <Check size={14} className="text-white" />
                          </span>
                        ) : val === 'partial' ? (
                          <span className="text-amber-400 font-bold">~</span>
                        ) : (
                          <span className="text-slate-200"><X size={16} /></span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ── Final CTA ─────────────────────────────────────────── */}
      <section className="py-32 px-6 relative overflow-hidden">
        <div className="mesh-bg-cta absolute inset-0 -z-10" />
        <div className="max-w-3xl mx-auto text-center relative z-10">
          <h2 className="reveal text-4xl md:text-6xl font-black text-slate-900 mb-6 leading-tight">
            Start exploring physics
            <br />
            <span className="gradient-text-animated">at the speed of silicon</span>
          </h2>
          <p className="reveal text-lg text-slate-500 mb-10">
            Open-source. Self-evolving. Built for the future of discovery.
          </p>
          <div className="reveal">
            <Link to="/signup" className="btn-fancy text-lg px-10 py-4 shadow-2xl shadow-indigo-200/60">
              Get Started Free
              <ArrowRight size={22} className="inline ml-2" />
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────── */}
      <footer className="py-12 px-6 border-t border-slate-100 bg-white">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
              <Sparkles size={16} className="text-white" />
            </div>
            <span className="font-bold text-slate-900">Beyond Frontier</span>
          </div>
          <p className="text-sm text-slate-400">
            Pushing physics past the known. Open source under MIT License.
          </p>
          <div className="flex items-center gap-6 text-sm text-slate-500">
            <Link to="/docs" className="hover:text-slate-900 transition-colors">Documentation</Link>
            <a href="https://github.com/vastdreams/physics-ai" target="_blank" rel="noopener noreferrer" className="hover:text-slate-900 transition-colors">
              GitHub
            </a>
            <Link to="/about" className="hover:text-slate-900 transition-colors">About</Link>
            <Link to="/login" className="hover:text-slate-900 transition-colors">Sign In</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
