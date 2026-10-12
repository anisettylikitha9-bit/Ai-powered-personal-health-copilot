import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api';
import ThreeHeartCanvas from '../components/ThreeHeartCanvas';
import ThreeBioHologram from '../components/ThreeBioHologram';
import { 
  HeartPulse, Activity, Pill, Calendar, FileText, 
  TrendingUp, AlertCircle, AlertTriangle, PhoneCall, Sparkles, CheckCircle2 
} from 'lucide-react';

export default function Dashboard({ setCurrentTab }) {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.id) {
      api.getDashboardStats(user.id)
        .then(setData)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-cyan-600"></div>
      </div>
    );
  }

  const habit = data?.habit_score || { habit_score: 88, status_label: 'Optimal Lifestyle' };
  const currentHr = data?.latest_vital?.heart_rate || 68;
  const currentSys = data?.latest_vital?.systolic_bp || 118;
  const currentDia = data?.latest_vital?.diastolic_bp || 76;
  const currentGluc = data?.latest_vital?.blood_glucose_mg_dl || 89;

  return (
    <div className="space-y-4">
      {/* 🚨 Medical Emergency Warning (India) Banner matching screenshot */}
      <div className="bg-gradient-to-r from-red-500 via-rose-500 to-rose-600 rounded-3xl p-4 sm:p-4.5 text-white shadow-lg shadow-rose-900/10 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center shrink-0 border border-white/30 text-white">
            <AlertTriangle className="w-5 h-5 text-amber-200" />
          </div>
          <div>
            <h2 className="text-xs sm:text-sm font-black tracking-tight flex items-center gap-1.5">
              <span>🚨 Medical Emergency Warning (India)</span>
            </h2>
            <p className="text-[11px] sm:text-xs text-rose-100 font-medium leading-relaxed max-w-2xl mt-0.5">
              If you or someone around you is experiencing severe symptoms (chest pain, severe shortness of breath, sudden numbness, or loss of consciousness), call emergency services immediately.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2.5 shrink-0">
          <a 
            href="tel:112"
            className="bg-white hover:bg-rose-50 text-slate-800 font-black px-4 py-2 rounded-full text-xs shadow-md transition hover:scale-105 flex items-center gap-1.5 cursor-pointer"
          >
            <PhoneCall className="w-3.5 h-3.5 text-rose-600" />
            <span>Call 112 (India)</span>
          </a>
          <a 
            href="tel:108"
            className="bg-rose-700/90 hover:bg-rose-800 text-white font-black px-4 py-2 rounded-full text-xs border border-white/20 shadow-md transition hover:scale-105 cursor-pointer"
          >
            Ambulance: 108
          </a>
        </div>
      </div>

      {/* 🟠 Personalized Healthcare Hub Banner matching screenshot */}
      <div className="bg-gradient-to-r from-[#00838f] via-[#0097a7] to-[#00838f] rounded-3xl p-5 sm:p-6 text-white shadow-xl shadow-cyan-900/10 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-1.5 text-amber-200 text-[11px] font-black uppercase tracking-wider mb-1">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
            <span>PERSONALIZED HEALTHCARE HUB</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black tracking-tight">
            Welcome back, {user?.full_name || 'Demo Health User'}!
          </h1>
          <p className="text-xs text-cyan-50 mt-1 max-w-xl font-medium leading-relaxed">
            Track daily vitals, monitor medication compliance, evaluate symptoms safely, and store diagnostic PDF records in your private health locker.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setCurrentTab('vitals')}
            className="bg-[#fff9db] hover:bg-amber-100 text-teal-900 font-black px-4 py-2 rounded-full text-xs shadow-md transition hover:scale-105 cursor-pointer"
          >
            + Log Vitals
          </button>
          <button 
            onClick={() => setCurrentTab('reports')}
            className="bg-white/20 hover:bg-white/30 text-amber-100 font-black px-4 py-2 rounded-full text-xs backdrop-blur-xs border border-white/30 transition hover:scale-105 cursor-pointer flex items-center gap-1.5"
          >
            📁 Reports & PDFs
          </button>
        </div>
      </div>

      {/* 🌟 3D INTERACTIVE ANATOMICAL VISUALIZATION SUITE */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <div className="lg:col-span-8">
          <ThreeHeartCanvas bpm={currentHr} height="360px" />
        </div>
        <div className="lg:col-span-4 flex flex-col justify-between">
          <ThreeBioHologram 
            heartRate={currentHr} 
            systolic={currentSys} 
            diastolic={currentDia} 
            glucose={currentGluc} 
            temperature={data?.latest_vital?.temperature_f || 98.6}
          />
        </div>
      </div>

      {/* Top 5 Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Habit Score */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm hover:shadow-md transition">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">Habit Score</span>
            <Sparkles className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-800">
            {habit.habit_score}<span className="text-xs text-slate-400 font-normal">/100</span>
          </div>
          <div className="text-[11px] font-semibold text-emerald-600 mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            {habit.status_label}
          </div>
        </div>

        {/* Vitals Logged */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm hover:shadow-md transition">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">Vitals Records</span>
            <Activity className="w-4 h-4 text-cyan-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-800">
            {data?.vitals_count || 0}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {data?.anomalies_count ? `${data.anomalies_count} anomalies detected` : 'All readings normal'}
          </div>
        </div>

        {/* Active Prescriptions */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm hover:shadow-md transition">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">Prescriptions</span>
            <Pill className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-800">
            {data?.active_medicines_count || 0}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Active daily reminders</div>
        </div>

        {/* Appointments */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm hover:shadow-md transition">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">Appointments</span>
            <Calendar className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-800">
            {data?.appointments_count || 0}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Scheduled clinic visits</div>
        </div>

        {/* Stored Reports & PDFs */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm hover:shadow-md transition">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold">Stored PDFs</span>
            <FileText className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-800">
            {data?.documents_count || 0}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Medical document vault</div>
        </div>
      </div>

      {/* Smart Insights & Telemetry Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Latest Vital Reading */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm">
          <h2 className="font-extrabold text-sm text-slate-800 mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-600" />
            Latest Vitals Telemetry
          </h2>
          {data?.latest_vital ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                <span className="text-xs text-slate-500 font-medium">Blood Pressure</span>
                <span className="font-bold text-sm text-slate-800">
                  {data.latest_vital.systolic_bp || '--'} / {data.latest_vital.diastolic_bp || '--'} mmHg
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                <span className="text-xs text-slate-500 font-medium">Heart Rate</span>
                <span className="font-bold text-sm text-slate-800">
                  {data.latest_vital.heart_rate || '--'} BPM
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                <span className="text-xs text-slate-500 font-medium">Blood Glucose</span>
                <span className="font-bold text-sm text-slate-800">
                  {data.latest_vital.blood_glucose_mg_dl || '--'} mg/dL ({data.latest_vital.glucose_context || 'N/A'})
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                <span className="text-xs text-slate-500 font-medium">Body Temp</span>
                <span className="font-bold text-sm text-slate-800">
                  {data.latest_vital.temperature_f ? `${data.latest_vital.temperature_f} °F` : '--'}
                </span>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400 text-xs">
              No vitals logged yet. Click "+ Log Vitals" to get started.
            </div>
          )}
        </div>

        {/* AI Smart Insights */}
        <div className="lg:col-span-2 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm">
          <h2 className="font-extrabold text-sm text-slate-800 mb-4 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-500" />
            Rule-Based Clinical & Wellness Insights
          </h2>
          {data?.smart_insights && data.smart_insights.length > 0 ? (
            <div className="space-y-3">
              {data.smart_insights.map((ins, idx) => {
                const isObj = typeof ins === 'object' && ins !== null;
                const title = isObj ? (ins.title || ins.category || 'Health Insight') : `Insight #${idx + 1}`;
                const desc = isObj ? ins.description : String(ins);
                const icon = isObj ? (ins.icon || '💡') : '💡';
                const rule = isObj ? ins.rule_explained : null;

                return (
                  <div key={idx} className="p-4 bg-gradient-to-r from-sky-50/70 to-teal-50/70 border border-sky-100 rounded-2xl flex items-start gap-3">
                    <div className="text-xl flex-shrink-0 mt-0.5">
                      {icon}
                    </div>
                    <div className="flex-1">
                      <h4 className="text-xs font-bold text-slate-800 mb-0.5">
                        {title}
                      </h4>
                      <p className="text-xs text-slate-600 leading-relaxed font-medium">
                        {desc}
                      </p>
                      {rule && (
                        <p className="text-[11px] text-cyan-700 mt-2 bg-white/70 p-2 rounded-xl border border-cyan-200/50 font-normal">
                          ℹ️ {rule}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400 text-xs">
              Insights will automatically generate as you log your daily habits and vitals.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
