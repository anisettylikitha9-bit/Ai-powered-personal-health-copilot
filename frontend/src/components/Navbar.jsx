import React from 'react';
import { 
  Menu, X, PhoneCall, Globe, Shield, Sparkles, 
  LogOut, User, Bell, HeartPulse, ShieldAlert
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

export default function Navbar({ currentTab, setCurrentTab, isMobileMenuOpen, setIsMobileMenuOpen }) {
  const { user, logout } = useAuth();
  const { lang, setLang, t } = useLanguage();

  const tabTitles = {
    landing: 'Overview & Features',
    dashboard: t('nav_dashboard') || 'Health Dashboard',
    assistant: t('nav_assistant') || 'AI Health Assistant',
    triage: 'Emergency 3-Tier Triage',
    wellness: t('nav_wellness') || 'Wellness Tracker',
    analytics: 'Insights & Analytics',
    history: 'Chat History',
    vitals: t('nav_vitals') || 'Vitals & Biometrics',
    medicines: t('nav_medicines') || 'Prescription Reminders',
    appointments: t('nav_appointments') || 'Appointments',
    reports: t('nav_reports') || 'Medical Vault & PDFs',
    profile: t('nav_profile') || 'Profile & Privacy',
    symptoms: t('nav_symptoms') || 'Symptom Checker'
  };

  const currentTitle = tabTitles[currentTab] || 'Health Dashboard';

  return (
    <header className="lg:hidden bg-white/95 backdrop-blur-md border-b border-slate-200 sticky top-0 z-30 px-4 py-3 transition-all shadow-xs">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
        {/* Left: Mobile Toggle + Breadcrumbs */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition cursor-pointer"
            aria-label="Toggle Navigation Menu"
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500">
              <Shield className="w-3.5 h-3.5 text-teal-600" />
              <span>HealthSaathi AI</span>
              <span className="text-slate-300">/</span>
            </span>
            <h1 className="text-sm sm:text-base font-black text-slate-900 tracking-tight flex items-center gap-2">
              <span>{currentTitle}</span>
              {currentTab === 'triage' && (
                <span className="bg-rose-100 text-rose-700 text-[10px] font-black uppercase px-2 py-0.5 rounded-full ring-1 ring-rose-300">
                  Tier 1-3
                </span>
              )}
              {currentTab === 'assistant' && (
                <span className="bg-sky-100 text-sky-700 text-[10px] font-black uppercase px-2 py-0.5 rounded-full ring-1 ring-sky-300">
                  Voice + Rules
                </span>
              )}
            </h1>
          </div>
        </div>

        {/* Right: Emergency 112, Language Selector, User Profile */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Emergency 112 India Pill */}
          <a
            href="tel:112"
            title="Medical Emergency: Call India 112"
            className="hidden md:flex items-center gap-1.5 bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-700 hover:to-rose-600 text-white px-3 py-1.5 rounded-full text-xs font-black shadow-sm transition hover:scale-105"
          >
            <PhoneCall className="w-3.5 h-3.5 animate-pulse" />
            <span>Call 112</span>
          </a>

          {/* Language Selector */}
          <div className="flex items-center bg-slate-100 border border-slate-200/80 rounded-xl p-1 text-xs">
            <Globe className="w-3.5 h-3.5 text-teal-600 ml-1.5 mr-1" />
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              className="bg-transparent text-slate-800 font-bold text-xs outline-none cursor-pointer pr-1"
              aria-label="Select Language"
            >
              <option value="en">English</option>
              <option value="te">తెలుగు</option>
              <option value="te-roman">Roman Telugu</option>
            </select>
          </div>

          {/* User Profile Pill & Logout */}
          {user && (
            <div className="flex items-center gap-2 pl-1 border-l border-slate-200">
              <button
                onClick={() => setCurrentTab('profile')}
                className="flex items-center gap-2 p-1.5 sm:px-3 sm:py-1.5 rounded-xl hover:bg-slate-100 transition cursor-pointer text-left"
                title="Go to Profile & Privacy Settings"
              >
                <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-sky-600 to-teal-500 text-white font-black text-xs flex items-center justify-center shadow-xs">
                  {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                </div>
                <div className="hidden lg:block">
                  <div className="text-xs font-bold text-slate-800 leading-tight">
                    {user.full_name}
                  </div>
                  <div className="text-[10px] text-teal-600 font-semibold leading-tight">
                    ● Local SQLite
                  </div>
                </div>
              </button>

              <button
                onClick={logout}
                title="Sign out"
                className="p-2 rounded-xl text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition cursor-pointer"
                aria-label="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
