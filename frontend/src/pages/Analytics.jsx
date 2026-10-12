import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, LineChart, Line, AreaChart, Area, XAxis, YAxis, 
  CartesianGrid, Tooltip, ResponsiveContainer, Legend 
} from 'recharts';
import { 
  Sparkles, Activity, Droplets, Moon, Dumbbell, 
  AlertCircle, CheckCircle2, Info, ArrowUpRight, ShieldCheck, Flame, RefreshCw
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';

export default function Analytics({ setCurrentTab }) {
  const { user } = useAuth();
  const [wellnessLogs, setWellnessLogs] = useState([]);
  const [goals, setGoals] = useState(null);
  const [insights, setInsights] = useState([]);
  const [timeframe, setTimeframe] = useState('7'); // 7 or 30 days
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const [wRes, inRes] = await Promise.all([
        api.getWellness(user.id, parseInt(timeframe, 10)),
        api.getInsights(user.id)
      ]);
      setWellnessLogs(wRes.logs || []);
      setGoals(wRes.goals || null);
      setInsights(inRes.insights || []);
    } catch (err) {
      console.error('Failed to load analytics data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [user, timeframe]);

  // Format logs for Recharts chronologically
  const chartData = [...wellnessLogs].reverse().map(log => {
    const d = new Date(log.log_date);
    const shortDay = d.toLocaleDateString('en-US', { weekday: 'short', month: 'numeric', day: 'numeric' });
    return {
      date: shortDay,
      rawDate: log.log_date,
      water: log.water_ml || 0,
      sleep: log.sleep_hours || 0,
      exercise: log.exercise_mins || 0,
      isActive: (log.exercise_mins || 0) > 0 ? 1 : 0,
      waterGoal: goals?.target_water_ml || 2500,
      sleepGoal: goals?.target_sleep_hours || 8.0,
      exerciseGoal: goals?.target_exercise_mins || 30,
    };
  });

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* 🌟 Header & Filter */}
      <div className="bg-gradient-to-r from-sky-600 via-teal-600 to-indigo-600 rounded-3xl p-6 text-white shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-sky-200 text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-pulse" />
            <span>Explainable Wellness Intelligence & Visual Trends</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Health Insights & Trends
          </h1>
          <p className="text-xs text-sky-100 max-w-xl leading-relaxed">
            Every insight provides its exact <strong>Data used</strong>, <strong>Rule applied</strong>, <strong>Result</strong>, and <strong>Clinical limitation</strong>. Never synthetic or invented.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-white/15 p-1 rounded-2xl border border-white/20 backdrop-blur-sm">
          <button
            onClick={() => setTimeframe('7')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              timeframe === '7' ? 'bg-white text-slate-900 shadow-sm' : 'text-white hover:bg-white/10'
            }`}
          >
            Past 7 Days
          </button>
          <button
            onClick={() => setTimeframe('30')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              timeframe === '30' ? 'bg-white text-slate-900 shadow-sm' : 'text-white hover:bg-white/10'
            }`}
          >
            Past 30 Days
          </button>
          <button
            onClick={fetchData}
            title="Refresh trends"
            className="p-1.5 rounded-xl hover:bg-white/10 text-white transition cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* 🧠 4-Part Explainable Intelligence Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-black text-slate-900 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-teal-600" />
            <span>Explainable Wellness Intelligence</span>
          </h2>
          <span className="text-xs font-bold text-slate-500">
            {insights.length} Verified Heuristic Patterns
          </span>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          {insights.map((item, idx) => (
            <div
              key={idx}
              className={`rounded-3xl p-5 border shadow-sm space-y-3 transition-all ${
                item.type === 'positive'
                  ? 'bg-teal-50/70 border-teal-200 text-teal-950'
                  : item.type === 'warning'
                    ? 'bg-rose-50/70 border-rose-200 text-rose-950'
                    : item.type === 'opportunity'
                      ? 'bg-amber-50/70 border-amber-200 text-amber-950'
                      : 'bg-slate-50/90 border-slate-200 text-slate-900'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className={`text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                  item.type === 'positive'
                    ? 'bg-teal-600 text-white'
                    : item.type === 'warning'
                      ? 'bg-rose-600 text-white'
                      : item.type === 'opportunity'
                        ? 'bg-amber-600 text-white'
                        : 'bg-slate-700 text-white'
                }`}>
                  {item.category}
                </span>
                <span className="text-[10px] font-bold opacity-60">Rule-Verified</span>
              </div>

              <h3 className="text-base font-black leading-snug">
                {item.title}
              </h3>

              {/* 4-Part Structure */}
              <div className="space-y-2 text-xs pt-1 border-t border-slate-200/60">
                <div className="bg-white/80 rounded-xl p-2.5 space-y-1">
                  <div className="text-[10px] font-black uppercase tracking-wider text-slate-500">
                    📊 Data Used:
                  </div>
                  <div className="font-semibold text-slate-800">{item.data_used}</div>
                </div>

                <div className="bg-white/80 rounded-xl p-2.5 space-y-1">
                  <div className="text-[10px] font-black uppercase tracking-wider text-slate-500">
                    ⚙️ Rule Applied:
                  </div>
                  <div className="font-semibold text-slate-800">{item.rule_applied}</div>
                </div>

                <div className="bg-white/80 rounded-xl p-2.5 space-y-1">
                  <div className="text-[10px] font-black uppercase tracking-wider text-teal-700">
                    🎯 Result:
                  </div>
                  <div className="font-bold text-slate-900">{item.result}</div>
                </div>

                <div className="bg-white/50 rounded-xl p-2.5 space-y-1">
                  <div className="text-[10px] font-black uppercase tracking-wider text-slate-400">
                    ⚠️ Limitation & Clinical Caveat:
                  </div>
                  <div className="text-[11px] text-slate-600 italic">{item.limitation}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 📊 Recharts Trend Visualizations */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-black text-slate-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-sky-600" />
            <span>Habit Tracking Trends</span>
          </h2>
          {wellnessLogs.length === 0 && (
            <span className="text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-lg">
              No recorded entries yet
            </span>
          )}
        </div>

        {wellnessLogs.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-3xl p-12 text-center space-y-4">
            <div className="w-16 h-16 rounded-3xl bg-sky-50 text-sky-600 flex items-center justify-center mx-auto">
              <Activity className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-base font-black text-slate-900">No Recorded Wellness Logs</h3>
              <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                Recharts visualizes weekly and monthly trends only from real saved data. Add your first day in the Wellness Tracker or load demo data.
              </p>
            </div>
            <button
              onClick={() => setCurrentTab && setCurrentTab('wellness')}
              className="px-5 py-2.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl font-bold text-xs shadow-md transition"
            >
              Open Wellness Tracker
            </button>
          </div>
        ) : (
          <div className="grid lg:grid-cols-2 gap-6">
            {/* 💧 Hydration Chart */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-black text-slate-800 flex items-center gap-2">
                    <Droplets className="w-4 h-4 text-sky-600" />
                    <span>Daily Water Intake (ml)</span>
                  </h3>
                  <div className="text-[11px] text-slate-500">Target: {goals?.target_water_ml || 2500} ml/day</div>
                </div>
                <span className="text-xs font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded-lg">
                  Recharts Area
                </span>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="waterGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#0284c7" stopOpacity={0.4}/>
                        <stop offset="95%" stopColor="#0284c7" stopOpacity={0.0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                      formatter={(val) => [`${val} ml`, 'Water Intake']}
                    />
                    <Area type="monotone" dataKey="water" stroke="#0284c7" strokeWidth={3} fillOpacity={1} fill="url(#waterGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 🌙 Sleep Duration Chart */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-black text-slate-800 flex items-center gap-2">
                    <Moon className="w-4 h-4 text-indigo-600" />
                    <span>Nightly Sleep Duration (Hours)</span>
                  </h3>
                  <div className="text-[11px] text-slate-500">Benchmark: 7.0 - 9.0 hrs/night</div>
                </div>
                <span className="text-xs font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-lg">
                  Recharts Line
                </span>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <YAxis domain={[0, 12]} tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                      formatter={(val) => [`${val} hrs`, 'Sleep Duration']}
                    />
                    <Line type="monotone" dataKey="sleep" stroke="#6366f1" strokeWidth={3} dot={{ r: 4, fill: '#6366f1' }} activeDot={{ r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 🏃 Exercise Minutes Bar Chart */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-4 lg:col-span-2">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-black text-slate-800 flex items-center gap-2">
                    <Dumbbell className="w-4 h-4 text-teal-600" />
                    <span>Physical Activity & Active Days (Minutes)</span>
                  </h3>
                  <div className="text-[11px] text-slate-500">Daily target: {goals?.target_exercise_mins || 30} mins • WHO weekly goal: 150+ mins</div>
                </div>
                <span className="text-xs font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-lg">
                  Recharts Bar
                </span>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                      formatter={(val) => [`${val} mins`, 'Active Exercise']}
                    />
                    <Bar dataKey="exercise" fill="#0d9488" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
