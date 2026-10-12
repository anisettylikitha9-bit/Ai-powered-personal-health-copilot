import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import ThreeHeartCanvas from '../components/ThreeHeartCanvas';
import { ShieldCheck, HeartPulse, Sparkles, KeyRound, UserPlus, Lock, Mail, User, CheckCircle2 } from 'lucide-react';

export default function Login({ onBackToLanding }) {
  const { login, register, demoLogin, loading } = useAuth();
  const { t } = useLanguage();
  const [tab, setTab] = useState('login');
  const [username, setUsername] = useState('demouser');
  const [password, setPassword] = useState('Demo@123');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login(username, password);
    } catch (err) {
      setError(err.message || 'Invalid username or password');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await register(username, password, fullName, email);
    } catch (err) {
      setError(err.message || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-sky-950 flex items-center justify-center p-4 lg:p-10">
      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Left Side: 3D Holographic Heart Hero Canvas */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center gap-3">
            {onBackToLanding && (
              <button
                onClick={onBackToLanding}
                className="text-xs font-bold text-cyan-400 hover:text-cyan-300 bg-white/5 border border-white/10 px-3 py-1.5 rounded-full transition cursor-pointer"
              >
                ← Back to Overview
              </button>
            )}
            <div className="inline-flex items-center gap-2 bg-cyan-950/80 border border-cyan-500/40 px-3.5 py-1.5 rounded-full text-cyan-300 text-xs font-bold shadow-lg">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>Interactive 3D Biometric Engine</span>
            </div>
          </div>

          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
            HealthSaathi <span className="bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent">AI Copilot</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-xl leading-relaxed">
            Your private clinical companion. Real-time 3D anatomical cardiovascular telemetry, rule-based symptom assessment, medication compliance reminders, and medical document PDF vault.
          </p>

          {/* Embedded 3D Canvas */}
          <div className="pt-2">
            <ThreeHeartCanvas bpm={72} height="360px" />
          </div>

          <div className="grid grid-cols-3 gap-3 pt-2">
            <div className="bg-slate-900/60 backdrop-blur-md p-3 rounded-2xl border border-white/10 text-center">
              <div className="text-cyan-400 font-extrabold text-sm">Offline First</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Private SQLite & 0 APIs</div>
            </div>
            <div className="bg-slate-900/60 backdrop-blur-md p-3 rounded-2xl border border-white/10 text-center">
              <div className="text-emerald-400 font-extrabold text-sm">3D Telemetry</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Real-time WebGL canvas</div>
            </div>
            <div className="bg-slate-900/60 backdrop-blur-md p-3 rounded-2xl border border-white/10 text-center">
              <div className="text-rose-400 font-extrabold text-sm">India 112 Triage</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Emergency red-flag filter</div>
            </div>
          </div>
        </div>

        {/* Right Side: Authentication Portal Card */}
        <div className="lg:col-span-5 bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl p-7 border border-white/20">
          {/* Brand Header */}
          <div className="text-center mb-5">
            <div className="relative inline-block mb-2.5">
              <img 
                src="/logo.png" 
                alt="Health Copilot Logo" 
                className="w-16 h-16 rounded-2xl object-cover shadow-xl shadow-cyan-500/30 border-2 border-cyan-400 mx-auto"
              />
            </div>
            <h2 className="text-xl font-black text-slate-800 tracking-tight">
              Personal Health Locker
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Sign in to access your vitals and stored medical records
            </p>
          </div>

          {/* Tab Switcher */}
          <div className="flex bg-slate-100 p-1 rounded-xl mb-5">
            <button
              onClick={() => { setTab('login'); setError(''); }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition ${
                tab === 'login' ? 'bg-white text-sky-700 shadow-sm' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setTab('register'); setError(''); }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition ${
                tab === 'register' ? 'bg-white text-sky-700 shadow-sm' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Create Account
            </button>
          </div>

        {error && (
          <div className="bg-rose-50 border border-rose-200 text-rose-700 text-xs p-3 rounded-xl mb-4 font-medium flex items-center gap-2">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {tab === 'login' ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Username</label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input 
                  type="text" 
                  value={username} 
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-sky-500 focus:bg-white outline-none transition" 
                  placeholder="Enter your username"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input 
                  type="password" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-sky-500 focus:bg-white outline-none transition" 
                  placeholder="Enter your password"
                  required
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-sky-600 to-cyan-600 hover:from-sky-700 hover:to-cyan-700 text-white font-bold rounded-xl text-xs shadow-lg shadow-sky-500/25 transition duration-150 disabled:opacity-50"
            >
              {loading ? 'Authenticating...' : 'Sign In to Health Locker'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="space-y-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Full Name</label>
              <input 
                type="text" 
                value={fullName} 
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-sky-500 outline-none" 
                placeholder="e.g. Ramesh Kumar"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Username</label>
              <input 
                type="text" 
                value={username} 
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-sky-500 outline-none" 
                placeholder="Choose username"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Email</label>
              <input 
                type="email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-sky-500 outline-none" 
                placeholder="name@example.com"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Password</label>
              <input 
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-sky-500 outline-none" 
                placeholder="Create password"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold rounded-xl text-xs shadow-lg shadow-teal-500/25 transition duration-150 disabled:opacity-50"
            >
              {loading ? 'Creating Account...' : 'Complete Registration'}
            </button>
          </form>
        )}

        {/* Demo Fast Access Button */}
        <div className="mt-6 pt-5 border-t border-slate-100">
          <button
            onClick={() => demoLogin()}
            disabled={loading}
            className="w-full py-2.5 bg-gradient-to-r from-violet-50 to-indigo-50 hover:from-violet-100 hover:to-indigo-100 text-indigo-700 border border-indigo-200/80 font-bold rounded-xl text-xs flex items-center justify-center gap-2 transition hover:scale-[1.01]"
          >
            <Sparkles className="w-4 h-4 text-indigo-500" />
            Quick Demo Login (Preloaded Data)
          </button>
        </div>

        {/* Footer badges */}
        <div className="mt-6 flex items-center justify-center gap-4 text-[11px] text-slate-400">
          <span className="flex items-center gap-1">🛡️ Private SQLite</span>
          <span>•</span>
          <span className="flex items-center gap-1">⚡ Fast & Local</span>
          <span>•</span>
          <span className="flex items-center gap-1">🇮🇳 India 112 Safety</span>
        </div>
      </div>
    </div>
  </div>
  );
}
