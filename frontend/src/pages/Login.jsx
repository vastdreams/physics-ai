/**
 * PATH: frontend/src/pages/Login.jsx
 * PURPOSE: Beautiful login page with animated gradient background
 */

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { login, loading, error, setError } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Email and password are required');
      return;
    }
    const success = await login(email, password);
    if (success) {
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen flex relative overflow-hidden">
      {/* Animated mesh background */}
      <div className="mesh-bg absolute inset-0 -z-10" />
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      {/* Left panel -- branding */}
      <div className="hidden lg:flex lg:w-1/2 items-center justify-center p-16 relative">
        <div className="max-w-md">
          <div className="flex items-center gap-3 mb-10">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-200/50">
              <Sparkles size={24} className="text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-black text-slate-900 tracking-tight">Beyond Frontier</h2>
              <p className="text-sm text-slate-500 font-medium">Physics Engine</p>
            </div>
          </div>

          <h1 className="text-4xl font-black text-slate-900 leading-tight mb-4">
            Pushing physics
            <br />
            <span className="gradient-text-animated">past the known</span>
          </h1>

          <p className="text-lg text-slate-500 leading-relaxed">
            A self-evolving engine that accelerates discovery, validates experiments,
            proposes theories, and finds the unknown.
          </p>

          <div className="mt-10 grid grid-cols-2 gap-4">
            {[
              { number: '50+', label: 'Physics Models' },
              { number: '12', label: 'Solver Engines' },
              { number: '5', label: 'AI Modes' },
              { number: '100%', label: 'Open Source' },
            ].map((stat) => (
              <div key={stat.label} className="card-glass p-4">
                <div className="text-2xl font-black gradient-text">{stat.number}</div>
                <p className="text-xs text-slate-500 font-medium mt-0.5">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel -- login form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile brand */}
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md">
              <Sparkles size={20} className="text-white" />
            </div>
            <span className="text-xl font-black text-slate-900 tracking-tight">Beyond Frontier</span>
          </div>

          <div className="card-glass p-8">
            <div className="mb-8">
              <h2 className="text-2xl font-black text-slate-900 mb-1">Welcome back</h2>
              <p className="text-slate-500">Sign in to continue to your dashboard</p>
            </div>

            {error && (
              <div className="mb-6 p-3 bg-red-50 border border-red-100 rounded-xl flex items-center gap-2 text-red-600 text-sm font-medium">
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@beyondfrontier.local"
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all"
                  autoComplete="email"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full px-4 py-3 pr-12 bg-white border border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all"
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-fancy w-full py-3.5 justify-center text-base disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Signing in...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    Sign In
                    <ArrowRight size={18} />
                  </span>
                )}
              </button>
            </form>

            <div className="mt-6 text-center text-sm text-slate-500">
              <p>
                Default credentials:{' '}
                <code className="text-xs bg-slate-100 px-1.5 py-0.5 rounded font-mono text-indigo-600">
                  admin@beyondfrontier.local
                </code>
              </p>
            </div>
          </div>

          <p className="mt-6 text-center text-sm text-slate-400">
            <Link to="/" className="hover:text-slate-600 transition-colors">
              Back to home
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
