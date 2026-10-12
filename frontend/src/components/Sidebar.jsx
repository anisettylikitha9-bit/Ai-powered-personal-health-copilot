import React from 'react';
import { 
  LayoutDashboard, User, Activity, Bot, Stethoscope, 
  Pill, Calendar, HeartPulse, FileText, Globe, LogOut, Sparkles,
  ShieldAlert, BarChart3, MessageSquare, Compass, Heart, X
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

export default function Sidebar({ 
  currentTab, 
  setCurrentTab, 
  isMobileMenuOpen, 
  setIsMobileMenuOpen 
}) {
  const { user, logout } = useAuth();
  const { lang, setLang, t } = useLanguage();

  const primaryNavItems = [
    { id: 'dashboard', label: 'Personal Health Dashboard', icon: LayoutDashboard },
    { id: 'profile', label: 'Health Profile', icon: User },
    { id: 'vitals', label: 'Vitals Tracker', icon: Activity },
    { id: 'assistant', label: 'AI Health Assistant', icon: Bot, badge: 'AI' },
    { id: 'symptoms', label: 'Symptom Checker', icon: Stethoscope },
    { id: 'medicines', label: 'Medicine Reminders', icon: Pill },
    { id: 'appointments', label: 'Doctor Appointments', icon: Calendar },
    { id: 'wellness', label: 'Daily Wellness Tracker', icon: HeartPulse },
    { id: 'reports', label: 'Health Reports & Export', icon: FileText, badge: 'NEW' },
  ];

  const secondaryNavItems = [
    { id: 'triage', label: 'Emergency 3-Tier Triage', icon: ShieldAlert, badge: '112' },
    { id: 'analytics', label: 'Insights & Analytics', icon: BarChart3 },
    { id: 'history', label: 'Chat History', icon: MessageSquare },
    { id: 'landing', label: 'Overview & Features', icon: Compass },
  ];

  const handleNavClick = (tabId) => {
    setCurrentTab(tabId);
    if (setIsMobileMenuOpen) {
      setIsMobileMenuOpen(false);
    }
  };

  const sidebarContent = (
    <div className="flex flex-col justify-between h-full p-4 bg-white">
      <div>
        {/* Brand Header matching screenshot */}
        <div 
          onClick={() => handleNavClick('dashboard')}
          className="flex flex-col items-center text-center pb-4 pt-1 border-b border-slate-100 cursor-pointer group"
        >
          <div className="relative mb-2">
            <img 
              src="/logo.png" 
              alt="Health Copilot Logo" 
              className="w-14 h-14 rounded-2xl object-cover shadow-md border border-slate-200 group-hover:scale-105 transition-transform"
            />
            <div className="absolute -bottom-1 -right-1 bg-emerald-500 w-3.5 h-3.5 rounded-full border-2 border-white ring-2 ring-emerald-200"></div>
          </div>
          <h1 className="font-black text-base text-slate-800 tracking-tight flex items-center gap-1.5">
            <span>Health Copilot</span>
            <span className="text-[10px] bg-cyan-100 text-cyan-800 font-bold px-1.5 py-0.5 rounded-md">Ai</span>
          </h1>
          <p className="text-[11px] text-slate-400 font-medium mt-0.5">Personal Healthcare Intelligence</p>
        </div>

        {/* Primary Navigation Items */}
        <nav className="mt-3 space-y-1 overflow-y-auto max-h-[calc(100vh-270px)] pr-1">
          {primaryNavItems.map((item) => {
            const Icon = item.icon;
            const active = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 cursor-pointer ${
                  active 
                    ? 'bg-[#00838f] text-white shadow-md shadow-cyan-900/10' 
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                <div className="flex items-center gap-2.5 truncate">
                  <Icon className={`w-4 h-4 shrink-0 ${active ? 'text-white' : 'text-slate-500'}`} />
                  <span className="truncate">{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[9px] uppercase font-black px-1.5 py-0.5 rounded shrink-0 ${
                    active 
                      ? 'bg-white/20 text-white' 
                      : item.badge === 'AI' || item.badge === 'NEW'
                        ? 'bg-cyan-100 text-cyan-800' 
                        : 'bg-rose-100 text-rose-700'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}

          {/* Secondary Clinical & Tools Section */}
          <div className="pt-2 mt-2 border-t border-slate-100">
            <div className="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Clinical & Analytics
            </div>
            {secondaryNavItems.map((item) => {
              const Icon = item.icon;
              const active = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-150 cursor-pointer ${
                    active 
                      ? 'bg-[#00838f] text-white shadow-md shadow-cyan-900/10' 
                      : 'text-slate-500 hover:bg-slate-100 hover:text-slate-800'
                  }`}
                >
                  <div className="flex items-center gap-2.5 truncate">
                    <Icon className={`w-3.5 h-3.5 shrink-0 ${active ? 'text-white' : 'text-slate-400'}`} />
                    <span className="truncate">{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className={`text-[9px] uppercase font-black px-1.5 py-0.5 rounded shrink-0 ${
                      active ? 'bg-white/20 text-white' : 'bg-rose-100 text-rose-700'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </nav>
      </div>

      {/* Footer Controls: Language, Profile & Logout */}
      <div className="pt-3 border-t border-slate-100 space-y-2.5">
        {/* Language Selector */}
        <div className="flex items-center justify-between bg-slate-50 px-2.5 py-1.5 rounded-xl border border-slate-200 text-xs">
          <div className="flex items-center gap-1.5 text-slate-600 font-medium text-[11px]">
            <Globe className="w-3.5 h-3.5 text-teal-600" />
            <span>Language</span>
          </div>
          <select 
            value={lang} 
            onChange={(e) => setLang(e.target.value)}
            className="bg-white border border-slate-200 text-slate-800 font-bold rounded-lg px-2 py-1 text-[11px] focus:ring-2 focus:ring-sky-500 outline-none cursor-pointer"
          >
            <option value="en">English</option>
            <option value="te">తెలుగు</option>
            <option value="te-roman">Roman Telugu</option>
          </select>
        </div>

        {/* User Account Capsule */}
        {user && (
          <div className="bg-gradient-to-r from-slate-50 to-sky-50/50 p-2.5 rounded-xl border border-slate-200/80 flex items-center justify-between">
            <div className="flex items-center gap-2 truncate">
              <div className="w-7 h-7 rounded-lg bg-sky-600 text-white font-black text-xs flex items-center justify-center shrink-0">
                {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
              </div>
              <div className="truncate">
                <div className="text-xs font-bold text-slate-800 truncate">{user.full_name}</div>
                <div className="text-[10px] text-teal-600 font-medium">● Local SQLite</div>
              </div>
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sticky Sidebar */}
      <aside className="hidden lg:flex w-72 bg-white border-r border-slate-200 min-h-screen flex-col sticky top-0 shadow-sm z-20">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Overlay */}
      {isMobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div 
            className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
            onClick={() => setIsMobileMenuOpen(false)}
          />
          <div className="relative w-72 max-w-[80vw] bg-white h-full shadow-2xl flex flex-col z-10 animate-in slide-in-from-left duration-200">
            <button
              onClick={() => setIsMobileMenuOpen(false)}
              className="absolute top-4 right-4 p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              aria-label="Close Navigation"
            >
              <X className="w-5 h-5" />
            </button>
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
}
