import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import { 
  HeartPulse, Droplets, Moon, Dumbbell, Sparkles, CheckCircle2, 
  Trash2, Edit3, Plus, X, Calendar, Smile, FileText, CheckSquare
} from 'lucide-react';

export default function Wellness() {
  const { user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [goals, setGoals] = useState(null);
  const [habitScore, setHabitScore] = useState(null);
  const [loading, setLoading] = useState(true);

  // Form Modal State (Add or Edit)
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    log_date: new Date().toISOString().split('T')[0],
    water_ml: 2500,
    sleep_hours: 7.5,
    exercise_mins: 30,
    exercise_type: 'Brisk Walking',
    mood: 'Energetic',
    notes: '',
    meal_notes: ''
  });

  const fetchLogs = async () => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const res = await api.getWellness(user.id, 30);
      setLogs(res.logs || []);
      setGoals(res.goals || null);
    } catch (err) {
      console.error('Failed to load wellness logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [user]);

  const handleOpenAdd = () => {
    setEditingId(null);
    setFormData({
      log_date: new Date().toISOString().split('T')[0],
      water_ml: 2500,
      sleep_hours: 7.5,
      exercise_mins: 30,
      exercise_type: 'Brisk Walking',
      mood: 'Energetic',
      notes: '',
      meal_notes: ''
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (log) => {
    setEditingId(log.id);
    setFormData({
      log_date: log.log_date,
      water_ml: log.water_ml || 0,
      sleep_hours: log.sleep_hours || 0,
      exercise_mins: log.exercise_mins || 0,
      exercise_type: log.exercise_type || 'Brisk Walking',
      mood: log.mood || 'Neutral',
      notes: log.notes || '',
      meal_notes: log.meal_notes || ''
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (logId) => {
    if (!window.confirm('Are you sure you want to delete this wellness record?')) return;
    try {
      await api.deleteWellness(logId, user.id);
      fetchLogs();
    } catch (err) {
      alert('Could not delete record: ' + err.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        // Edit existing log
        const res = await api.updateWellness(editingId, {
          user_id: user.id,
          water_ml: parseInt(formData.water_ml, 10),
          sleep_hours: parseFloat(formData.sleep_hours),
          exercise_mins: parseInt(formData.exercise_mins, 10),
          exercise_type: formData.exercise_type,
          mood: formData.mood,
          meal_notes: formData.meal_notes,
          notes: formData.notes
        });
        if (res.habit_score) setHabitScore(res.habit_score);
      } else {
        // Add new log
        const res = await api.logWellness({
          user_id: user.id,
          log_date: formData.log_date,
          water_ml: parseInt(formData.water_ml, 10),
          sleep_hours: parseFloat(formData.sleep_hours),
          exercise_mins: parseInt(formData.exercise_mins, 10),
          exercise_type: formData.exercise_type,
          mood: formData.mood,
          meal_notes: formData.meal_notes,
          notes: formData.notes
        });
        if (res.habit_score) setHabitScore(res.habit_score);
      }
      setIsModalOpen(false);
      fetchLogs();
    } catch (err) {
      alert('Failed to save wellness record: ' + err.message);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* 🌟 Header */}
      <div className="bg-gradient-to-r from-teal-600 via-sky-600 to-indigo-600 rounded-3xl p-6 text-white shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-teal-200 text-xs font-bold uppercase tracking-wider">
            <HeartPulse className="w-3.5 h-3.5 text-amber-300" />
            <span>Daily Health Habits & CRUD Logging</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Wellness Tracker
          </h1>
          <p className="text-xs text-teal-100 max-w-lg leading-relaxed">
            Record daily water, sleep hours, exercise minutes, active days, and general notes. Edit or delete past entries anytime.
          </p>
        </div>

        <button
          onClick={handleOpenAdd}
          className="flex items-center gap-2 px-5 py-3 bg-white text-teal-900 rounded-2xl font-black text-xs sm:text-sm shadow-md hover:bg-teal-50 transition-all hover:scale-105 cursor-pointer"
        >
          <Plus className="w-4 h-4 text-teal-600" />
          <span>Add New Wellness Entry</span>
        </button>
      </div>

      {/* Habit Score Card if recently computed */}
      {habitScore && (
        <div className="bg-gradient-to-r from-teal-50 to-sky-50 border border-teal-200 rounded-3xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-teal-600 text-white flex flex-col items-center justify-center font-black">
              <span className="text-xl leading-none">{habitScore.total_score || habitScore.habit_score || 80}</span>
              <span className="text-[9px] uppercase tracking-wider opacity-80">/ 100</span>
            </div>
            <div>
              <div className="text-xs font-black uppercase text-teal-700 tracking-wider">
                Lifestyle Habit Consistency
              </div>
              <div className="text-base font-extrabold text-slate-800">
                {habitScore.score_grade || habitScore.status_label || 'Healthy Habit Pace'}
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                {habitScore.disclaimer || 'Calculated transparently across hydration, sleep, exercise, and vitals consistency.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 📋 Log Entries List */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-base font-black text-slate-900">Recorded Wellness Entries</h2>
            <p className="text-xs text-slate-500">Full CRUD: Add, inspect, modify, or remove recorded days</p>
          </div>
          <span className="text-xs font-bold text-slate-500 bg-slate-100 px-3 py-1 rounded-xl">
            {logs.length} Total Logs
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs font-bold text-slate-400">
            Loading wellness records...
          </div>
        ) : logs.length === 0 ? (
          <div className="p-12 text-center space-y-4">
            <div className="w-16 h-16 rounded-3xl bg-teal-50 text-teal-600 flex items-center justify-center mx-auto">
              <HeartPulse className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-base font-black text-slate-800">No Wellness Records Found</h3>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                You haven't logged any wellness entries yet. Click "Add New Wellness Entry" to record today's hydration and sleep.
              </p>
            </div>
            <button
              onClick={handleOpenAdd}
              className="px-5 py-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-bold text-xs shadow-md transition cursor-pointer"
            >
              Add First Entry
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider text-[10px] border-b border-slate-100">
                <tr>
                  <th className="py-3 px-6">Date</th>
                  <th className="py-3 px-4">Water Intake</th>
                  <th className="py-3 px-4">Sleep</th>
                  <th className="py-3 px-4">Active Exercise</th>
                  <th className="py-3 px-4">Mood</th>
                  <th className="py-3 px-4">Notes</th>
                  <th className="py-3 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700 font-medium">
                {logs.map((log) => {
                  const isActiveDay = (log.exercise_mins || 0) > 0;
                  return (
                    <tr key={log.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-6 font-bold text-slate-900 flex items-center gap-2">
                        <Calendar className="w-3.5 h-3.5 text-teal-600" />
                        <span>{log.log_date}</span>
                      </td>
                      <td className="py-3.5 px-4 font-semibold text-cyan-700">
                        {log.water_ml} ml
                      </td>
                      <td className="py-3.5 px-4 font-semibold text-indigo-700">
                        {log.sleep_hours} hrs
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-1.5 font-semibold text-teal-700">
                          <span>{log.exercise_mins} mins</span>
                          {isActiveDay && (
                            <span className="text-[9px] bg-teal-100 text-teal-800 px-1.5 py-0.5 rounded-full font-bold">
                              Active
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-slate-400 font-normal">
                          {log.exercise_type || 'Exercise'}
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="inline-block bg-slate-100 px-2.5 py-0.5 rounded-full text-[11px] font-bold text-slate-700">
                          {log.mood || 'Neutral'}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-500 max-w-xs truncate">
                        {log.notes || log.meal_notes || '—'}
                      </td>
                      <td className="py-3.5 px-6 text-right space-x-2">
                        <button
                          onClick={() => handleOpenEdit(log)}
                          title="Edit this entry"
                          className="p-1.5 rounded-lg text-sky-600 hover:bg-sky-50 transition cursor-pointer"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(log.id)}
                          title="Delete this entry"
                          className="p-1.5 rounded-lg text-rose-500 hover:bg-rose-50 transition cursor-pointer"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 📝 Add/Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-950/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-5 animate-scale-up">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-black text-slate-900">
                {editingId ? 'Edit Wellness Record' : 'Record Daily Wellness'}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">Date</label>
                <input
                  type="date"
                  value={formData.log_date}
                  onChange={(e) => setFormData({ ...formData, log_date: e.target.value })}
                  disabled={!!editingId}
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-slate-50/50 font-medium"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-bold text-slate-700 block mb-1">Water Intake (ml)</label>
                  <input
                    type="number"
                    min="0"
                    max="10000"
                    step="50"
                    value={formData.water_ml}
                    onChange={(e) => setFormData({ ...formData, water_ml: e.target.value })}
                    className="w-full text-xs p-2.5 rounded-xl border border-slate-200"
                    required
                  />
                </div>

                <div>
                  <label className="text-xs font-bold text-slate-700 block mb-1">Sleep Duration (Hours)</label>
                  <input
                    type="number"
                    min="0"
                    max="24"
                    step="0.5"
                    value={formData.sleep_hours}
                    onChange={(e) => setFormData({ ...formData, sleep_hours: e.target.value })}
                    className="w-full text-xs p-2.5 rounded-xl border border-slate-200"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-bold text-slate-700 block mb-1">Exercise (Minutes)</label>
                  <input
                    type="number"
                    min="0"
                    max="600"
                    value={formData.exercise_mins}
                    onChange={(e) => setFormData({ ...formData, exercise_mins: e.target.value })}
                    className="w-full text-xs p-2.5 rounded-xl border border-slate-200"
                    required
                  />
                </div>

                <div>
                  <label className="text-xs font-bold text-slate-700 block mb-1">Exercise Type</label>
                  <input
                    type="text"
                    value={formData.exercise_type}
                    onChange={(e) => setFormData({ ...formData, exercise_type: e.target.value })}
                    placeholder="e.g. Brisk Walking, Yoga"
                    className="w-full text-xs p-2.5 rounded-xl border border-slate-200"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-bold text-slate-700 block mb-1">Mood</label>
                  <select
                    value={formData.mood}
                    onChange={(e) => setFormData({ ...formData, mood: e.target.value })}
                    className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-white"
                  >
                    <option value="Energetic">Energetic</option>
                    <option value="Calm">Calm</option>
                    <option value="Neutral">Neutral</option>
                    <option value="Tired">Tired</option>
                    <option value="Stressed">Stressed</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-bold text-slate-700 block mb-1">Meals / Nutrition</label>
                  <input
                    type="text"
                    value={formData.meal_notes}
                    onChange={(e) => setFormData({ ...formData, meal_notes: e.target.value })}
                    placeholder="e.g. Balanced home-cooked meals"
                    className="w-full text-xs p-2.5 rounded-xl border border-slate-200"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">General Wellness Notes</label>
                <textarea
                  rows={2}
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Any feelings, hydration notes, or lifestyle observations..."
                  className="w-full text-xs p-2.5 rounded-xl border border-slate-200"
                />
              </div>

              <div className="flex items-center gap-3 pt-2">
                <button
                  type="submit"
                  className="flex-1 py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-bold text-xs shadow-md transition cursor-pointer"
                >
                  {editingId ? 'Update Record' : 'Save Wellness Record'}
                </button>
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-bold text-xs transition cursor-pointer"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
