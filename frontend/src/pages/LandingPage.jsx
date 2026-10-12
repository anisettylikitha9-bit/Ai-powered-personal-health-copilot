import React from 'react';
import { 
  Heart, Shield, Sparkles, PhoneCall, Bot, Activity, 
  BarChart3, CheckCircle, ArrowRight, Stethoscope, AlertTriangle,
  Zap, Lock, Globe, Clock, Flame
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

export default function LandingPage({ setCurrentTab, onOpenLogin }) {
  const { loginDemo } = useAuth();
  const { lang, setLang } = useLanguage();

  const handleLaunchDemo = async () => {
    try {
      await loginDemo();
      if (setCurrentTab) setCurrentTab('dashboard');
    } catch (err) {
      console.error('Demo login failed:', err);
      if (onOpenLogin) onOpenLogin();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-sky-50/40 to-teal-50/30 text-slate-800">
      {/* 🚨 Emergency India Hotline Top Bar */}
      <div className="bg-gradient-to-r from-rose-600 via-rose-500 to-amber-600 text-white text-xs sm:text-sm py-2.5 px-4 shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2 font-bold tracking-wide">
            <AlertTriangle className="w-4 h-4 animate-bounce text-amber-200" />
            <span>MEDICAL EMERGENCY IN INDIA?</span>
            <span className="hidden sm:inline font-normal opacity-90">Call 112 (General) or 108 (Ambulance) immediately.</span>
          </div>
          <div className="flex items-center gap-3">
            <a 
              href="tel:112" 
              className="flex items-center gap-1.5 bg-white text-rose-700 px-3 py-1 rounded-full font-black text-xs hover:bg-rose-50 shadow transition-transform hover:scale-105"
            >
              <PhoneCall className="w-3.5 h-3.5 text-rose-600" />
              <span>Call 112 Now</span>
            </a>
          </div>
        </div>
      </div>

      {/* 🧭 Top Navigation */}
      <nav className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-sky-600 to-teal-500 p-0.5 shadow-lg shadow-sky-500/20">
            <div className="w-full h-full bg-white rounded-[14px] flex items-center justify-center">
              <Heart className="w-6 h-6 text-sky-600 fill-teal-400" />
            </div>
          </div>
          <div>
            <div className="text-xl font-black bg-gradient-to-r from-sky-700 via-teal-700 to-indigo-700 bg-clip-text text-transparent">
              HealthSaathi AI
            </div>
            <div className="text-[10px] font-bold text-slate-700 uppercase tracking-wider">
              Advanced Personal Health Copilot
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Language Switcher */}
          <div className="hidden sm:flex items-center bg-white border border-slate-200 rounded-xl p-1 shadow-sm text-xs font-bold text-slate-700">
            <button 
              onClick={() => setLang('en')}
              className={`px-2.5 py-1 rounded-lg transition-all ${lang === 'en' ? 'bg-sky-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
            >
              English
            </button>
            <button 
              onClick={() => setLang('te')}
              className={`px-2.5 py-1 rounded-lg transition-all ${lang === 'te' ? 'bg-sky-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
            >
              తెలుగు
            </button>
            <button 
              onClick={() => setLang('te-roman')}
              className={`px-2.5 py-1 rounded-lg transition-all ${lang === 'te-roman' ? 'bg-sky-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
            >
              Roman Telugu
            </button>
          </div>

          <button
            onClick={onOpenLogin}
            className="px-4 py-2 text-xs sm:text-sm font-bold text-sky-700 hover:text-sky-900 bg-sky-50/80 hover:bg-sky-100 rounded-xl transition cursor-pointer"
          >
            Sign In
          </button>
          <button
            onClick={handleLaunchDemo}
            className="flex items-center gap-1.5 px-4 py-2 text-xs sm:text-sm font-bold bg-gradient-to-r from-sky-600 to-teal-600 hover:from-sky-700 hover:to-teal-700 text-white rounded-xl shadow-md hover:shadow-sky-500/20 transition-all hover:scale-105 cursor-pointer"
          >
            <Sparkles className="w-4 h-4 text-amber-200" />
            <span>Live Demo</span>
          </button>
        </div>
      </nav>

      {/* 🚀 Hero Section */}
      <section className="max-w-7xl mx-auto px-6 pt-10 pb-16 lg:pt-16 lg:pb-24">
        <div className="grid lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 bg-gradient-to-r from-sky-100 to-teal-100 text-sky-800 px-3.5 py-1.5 rounded-full text-xs font-bold border border-sky-200/60 shadow-sm">
              <Sparkles className="w-3.5 h-3.5 text-teal-600 animate-spin" />
              <span>Offline-First Rule-Based AI • 100% Free • Zero Paid APIs</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-slate-900 leading-tight">
              Your Intelligent <span className="bg-gradient-to-r from-sky-600 via-teal-600 to-indigo-600 bg-clip-text text-transparent">Health Companion</span> for Daily Wellness & Triage.
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-2xl">
              Empowering you with natural voice conversations in <strong>English, తెలుగు, and Roman Telugu</strong>, conservative emergency triage routed to <strong>India 112</strong>, transparent wellness habits, and explainable health intelligence.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                onClick={handleLaunchDemo}
                className="flex items-center gap-2.5 px-6 py-3.5 bg-gradient-to-r from-sky-600 via-teal-600 to-indigo-600 hover:from-sky-700 hover:to-teal-700 text-white rounded-2xl font-black text-sm shadow-xl shadow-sky-600/25 transition-all hover:scale-105 cursor-pointer"
              >
                <Zap className="w-4 h-4 text-amber-300" />
                <span>Launch HealthSaathi Demo</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                onClick={() => {
                  if (setCurrentTab) setCurrentTab('triage');
                  else if (onOpenLogin) onOpenLogin();
                }}
                className="flex items-center gap-2 px-5 py-3.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-2xl font-bold text-sm shadow-sm transition hover:border-rose-300 hover:text-rose-600 cursor-pointer"
              >
                <Shield className="w-4 h-4 text-rose-500" />
                <span>Emergency 3-Tier Triage</span>
              </button>
            </div>

            {/* Quick Proof Badges */}
            <div className="grid grid-cols-3 gap-3 pt-4 max-w-lg">
              <div className="bg-white/80 backdrop-blur-sm border border-slate-200/80 rounded-2xl p-3 text-center shadow-xs">
                <div className="text-lg font-black text-sky-600">3 Tiers</div>
                <div className="text-[11px] font-medium text-slate-500">Clinical Safety Triage</div>
              </div>
              <div className="bg-white/80 backdrop-blur-sm border border-slate-200/80 rounded-2xl p-3 text-center shadow-xs">
                <div className="text-lg font-black text-teal-600">3 Languages</div>
                <div className="text-[11px] font-medium text-slate-500">EN, తెలుగు, Roman TE</div>
              </div>
              <div className="bg-white/80 backdrop-blur-sm border border-slate-200/80 rounded-2xl p-3 text-center shadow-xs">
                <div className="text-lg font-black text-indigo-600">100%</div>
                <div className="text-[11px] font-medium text-slate-500">Explainable Rules</div>
              </div>
            </div>
          </div>

          {/* Interactive Hero Showcase Card */}
          <div className="lg:col-span-5">
            <div className="relative">
              {/* Decorative Glow */}
              <div className="absolute -inset-1.5 bg-gradient-to-r from-sky-500 via-teal-400 to-indigo-500 rounded-3xl blur-xl opacity-30 animate-pulse" />

              <div className="relative bg-white border border-slate-200/80 rounded-3xl p-6 shadow-2xl space-y-5">
                {/* Assistant Chat Preview */}
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div className="flex items-center gap-2.5">
                    <div className="w-9 h-9 rounded-xl bg-sky-50 flex items-center justify-center text-sky-600 border border-sky-100">
                      <Bot className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="text-xs font-black text-slate-800">HealthSaathi Voice Copilot</div>
                      <div className="text-[10px] text-teal-600 font-bold flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-teal-500 animate-ping" />
                        Online • Multi-Language Voice Orb
                      </div>
                    </div>
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-sky-100 text-sky-800">
                    Live Preview
                  </span>
                </div>

                {/* Example Chat Flow */}
                <div className="space-y-3 text-xs">
                  <div className="flex justify-end">
                    <div className="bg-sky-600 text-white rounded-2xl rounded-tr-xs px-3.5 py-2 max-w-[85%] font-medium shadow-xs">
                      "Naaku jwaram ga undi."
                    </div>
                  </div>

                  <div className="flex justify-start">
                    <div className="bg-slate-50 border border-slate-100 text-slate-700 rounded-2xl rounded-tl-xs p-3.5 max-w-[90%] space-y-2 shadow-xs">
                      <div className="font-bold text-sky-700 flex items-center gap-1">
                        <Heart className="w-3.5 h-3.5 text-rose-500" />
                        <span>Jwaram & Chali (Fever Guidance)</span>
                      </div>
                      <p className="text-[11px] text-slate-600 leading-relaxed">
                        • Goruvechani neellu, ORS mariyu kobbari neellu thagandi.<br/>
                        • Prathi 4-6 hours ki thermometer tho temperature check cheyyandi.<br/>
                        • Jwaram 103°F kante ekkuva unna leda 3 days kante ekkuva unna doctor ni kalavandi.
                      </p>
                      <div className="flex flex-wrap gap-1 pt-1">
                        <span className="text-[9px] bg-sky-100 text-sky-800 px-2 py-0.5 rounded-full font-bold">
                          Safe Home Self-Care
                        </span>
                        <span className="text-[9px] bg-teal-100 text-teal-800 px-2 py-0.5 rounded-full font-bold">
                          Non-Diagnostic
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Triage Urgency Preview */}
                <div className="bg-gradient-to-r from-rose-50 to-amber-50 border border-rose-200/80 rounded-2xl p-3.5">
                  <div className="flex items-center justify-between text-xs font-black text-rose-700 mb-1">
                    <span className="flex items-center gap-1.5">
                      <AlertTriangle className="w-4 h-4 text-rose-600" />
                      3-Urgency Tier Triage System
                    </span>
                    <span className="text-[10px] bg-rose-600 text-white px-2 py-0.5 rounded-md">
                      Call 112
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600">
                    Emergency care now • Prompt medical consultation • General self-care guidance
                  </p>
                </div>

                {/* Live Try Button */}
                <button
                  onClick={handleLaunchDemo}
                  className="w-full py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer"
                >
                  <span>Open Full Dashboard & AI Assistant</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 🌟 4 Core Architectural Pillars */}
      <section className="bg-white border-y border-slate-200/70 py-16 px-6">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center max-w-2xl mx-auto space-y-3">
            <div className="text-xs font-black text-sky-600 uppercase tracking-widest">
              Engineered For Safety & Trust
            </div>
            <h2 className="text-3xl font-black text-slate-900">
              Why HealthSaathi AI is Different
            </h2>
            <p className="text-sm text-slate-600">
              Built on verified clinical heuristics, conservative emergency protocols, and fully explainable wellness analytics.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Pillar 1 */}
            <div className="bg-slate-50/80 hover:bg-sky-50/60 border border-slate-200/80 rounded-3xl p-6 space-y-4 transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
              <div className="w-12 h-12 rounded-2xl bg-rose-100 flex items-center justify-center text-rose-600 shadow-xs">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900">
                1. 3-Tier Emergency Triage
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Separates acute red flags (*Emergency care now* with direct India 112 routing) from *Prompt medical consultation* and *General self-care*. Never delays emergency guidance.
              </p>
            </div>

            {/* Pillar 2 */}
            <div className="bg-slate-50/80 hover:bg-teal-50/60 border border-slate-200/80 rounded-3xl p-6 space-y-4 transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
              <div className="w-12 h-12 rounded-2xl bg-teal-100 flex items-center justify-center text-teal-600 shadow-xs">
                <Globe className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900">
                2. Telugu + Roman Telugu Companion
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Native voice and text comprehension for Telugu script (*"నాకు జ్వరంగా ఉంది"*) and Roman Telugu (*"Naaku jwaram ga undi"*), plus English with instant language toggling.
              </p>
            </div>

            {/* Pillar 3 */}
            <div className="bg-slate-50/80 hover:bg-indigo-50/60 border border-slate-200/80 rounded-3xl p-6 space-y-4 transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
              <div className="w-12 h-12 rounded-2xl bg-indigo-100 flex items-center justify-center text-indigo-600 shadow-xs">
                <BarChart3 className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900">
                3. Explainable Wellness Intelligence
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Every insight shows **Data used**, **Rule applied**, **Result**, and **Limitation**. Never invents measurements or generates ungrounded advice.
              </p>
            </div>

            {/* Pillar 4 */}
            <div className="bg-slate-50/80 hover:bg-sky-50/60 border border-slate-200/80 rounded-3xl p-6 space-y-4 transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
              <div className="w-12 h-12 rounded-2xl bg-sky-100 flex items-center justify-center text-sky-600 shadow-xs">
                <Lock className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-slate-900">
                4. Absolute Privacy & Data Rights
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Stored in isolated local SQLite with zero paid cloud trackers. Complete user data wiping functionality allows you to permanently erase all records at any time.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ⚕️ Mandatory Medical Disclaimer */}
      <footer className="max-w-7xl mx-auto px-6 py-12 border-t border-slate-200 text-center space-y-4">
        <div className="flex items-center justify-center gap-2 text-xs font-bold text-slate-500">
          <Stethoscope className="w-4 h-4 text-sky-600" />
          <span>Non-Diagnostic Clinical Safety Policy</span>
        </div>
        <p className="text-xs text-slate-500 max-w-3xl mx-auto leading-relaxed">
          HealthSaathi AI is an educational wellness tracking copilot and emergency triage advisor. It is <strong>NOT a licensed medical practitioner</strong> and does not diagnose illnesses, prescribe medications, or replace direct consultation with a qualified doctor. If you suspect an acute medical emergency, call <strong>112</strong> immediately.
        </p>
        <div className="text-[11px] text-slate-400">
          © {new Date().getFullYear()} HealthSaathi AI • Made with care for personalized healthcare intelligence.
        </div>
      </footer>
    </div>
  );
}
