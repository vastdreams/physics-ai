/**
 * PATH: frontend/src/pages/Signup.jsx
 * PURPOSE: User registration page — no API keys, just name/email/password
 */

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Eye, EyeOff, AlertCircle, Check, X, Shield } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

/** Password strength checker */
function getPasswordStrength(pw) {
  if (!pw) return { score: 0, label: '', color: '' };
  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;

  if (score <= 1) return { score, label: 'Weak', color: 'bg-red-500' };
  if (score <= 2) return { score, label: 'Fair', color: 'bg-amber-500' };
  if (score <= 3) return { score, label: 'Good', color: 'bg-blue-500' };
  return { score, label: 'Strong', color: 'bg-emerald-500' };
}

function PasswordRule({ met, text }) {
  return (
    <div className={`flex items-center gap-2 text-xs ${met ? 'text-emerald-600' : 'text-slate-400'}`}>
      {met ? <Check size={12} /> : <X size={12} />}
      {text}
    </div>
  );
}

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const { register, loading, error, setError } = useAuth();
  const navigate = useNavigate();

  const strength = getPasswordStrength(password);
  const passwordsMatch = password && confirmPassword && password === confirmPassword;
  const hasMinLength = password.length >= 8;
  const hasUppercase = /[A-Z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[^A-Za-z0-9]/.test(password);

  const canSubmit = name.trim() && email.trim() && hasMinLength && passwordsMatch && agreed && !loading;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    const success = await register(name.trim(), email.trim(), password);
    if (success) {
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen flex relative overflow-hidden">
      {/* Background */}
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
            Join the future of
            <br />
            <span className="gradient-text-animated">physics discovery</span>
          </h1>

          <p className="text-lg text-slate-500 leading-relaxed">
            No API keys. No credit card. Just create an account and start exploring
            the most advanced open-source physics engine.
          </p>

          <div className="mt-10 space-y-4">
            {[
              { icon: Shield, text: 'Your data stays private and secure' },
              { icon: Sparkles, text: 'Full access to all physics tools' },
              { icon: Check, text: 'Free forever — 100% open source' },
            ].map((item) => (
              <div key={item.text} className="flex items-center gap-3 text-slate-600">
                <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center">
                  <item.icon size={16} className="text-indigo-500" />
                </div>
                <span className="text-sm font-medium">{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel -- signup form */}
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
            <div className="mb-6">
              <h2 className="text-2xl font-black text-slate-900 mb-1">Create your account</h2>
              <p className="text-slate-500">Free access to the full physics platform</p>
            </div>

            {error && (
              <div className="mb-5 p-3 bg-red-50 border border-red-100 rounded-xl flex items-center gap-2 text-red-600 text-sm font-medium">
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all"
                  autoComplete="name"
                  autoFocus
                  maxLength={100}
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all"
                  autoComplete="email"
                  maxLength={254}
                />
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Min. 8 characters"
                    className="w-full px-4 py-3 pr-12 bg-white border border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all"
                    autoComplete="new-password"
                    maxLength={128}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>

                {/* Strength meter */}
                {password && (
                  <div className="mt-2">
                    <div className="flex gap-1 mb-1.5">
                      {[1, 2, 3, 4, 5].map((i) => (
                        <div
                          key={i}
                          className={`h-1 flex-1 rounded-full transition-colors ${
                            i <= strength.score ? strength.color : 'bg-slate-200'
                          }`}
                        />
                      ))}
                    </div>
                    <div className="grid grid-cols-2 gap-1">
                      <PasswordRule met={hasMinLength} text="8+ characters" />
                      <PasswordRule met={hasUppercase} text="Uppercase letter" />
                      <PasswordRule met={hasNumber} text="Number" />
                      <PasswordRule met={hasSpecial} text="Special character" />
                    </div>
                  </div>
                )}
              </div>

              {/* Confirm Password */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Confirm Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter your password"
                  className={`w-full px-4 py-3 bg-white border rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 transition-all ${
                    confirmPassword
                      ? passwordsMatch
                        ? 'border-emerald-300 focus:border-emerald-400 focus:ring-emerald-100'
                        : 'border-red-300 focus:border-red-400 focus:ring-red-100'
                      : 'border-slate-200 focus:border-indigo-400 focus:ring-indigo-100'
                  }`}
                  autoComplete="new-password"
                  maxLength={128}
                />
                {confirmPassword && !passwordsMatch && (
                  <p className="text-xs text-red-500 mt-1">Passwords do not match</p>
                )}
              </div>

              {/* Terms */}
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={agreed}
                  onChange={(e) => setAgreed(e.target.checked)}
                  className="mt-0.5 w-4 h-4 rounded border-slate-300 text-indigo-500 focus:ring-indigo-200"
                />
                <span className="text-xs text-slate-500 leading-relaxed">
                  I agree to the{' '}
                  <span className="text-indigo-500 font-medium">Terms of Service</span>{' '}
                  and{' '}
                  <span className="text-indigo-500 font-medium">Privacy Policy</span>.
                  My data is processed securely.
                </span>
              </label>

              {/* Submit */}
              <button
                type="submit"
                disabled={!canSubmit}
                className="btn-fancy w-full py-3.5 justify-center text-base disabled:opacity-40 disabled:cursor-not-allowed disabled:transform-none"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Creating account...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    Create Account
                    <ArrowRight size={18} />
                  </span>
                )}
              </button>
            </form>
          </div>

          <p className="mt-6 text-center text-sm text-slate-500">
            Already have an account?{' '}
            <Link to="/login" className="text-indigo-500 font-semibold hover:text-indigo-600 transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
