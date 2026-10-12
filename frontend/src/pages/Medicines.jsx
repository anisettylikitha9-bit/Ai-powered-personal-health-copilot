import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import { Pill, Plus, CheckCircle2, Trash2, Clock } from 'lucide-react';

export default function Medicines() {
  const { user } = useAuth();
  const [medicines, setMedicines] = useState([]);
  const [name, setName] = useState('');
  const [dosage, setDosage] = useState('');
  const [timing, setTiming] = useState('After Meals');
  const [timeStr, setTimeStr] = useState('09:00 AM');
  const [instructions, setInstructions] = useState('');

  const fetchMeds = () => {
    if (user?.id) {
      api.getMedicines(user.id).then(res => setMedicines(res.medicines || []));
    }
  };

  useEffect(() => { fetchMeds(); }, [user]);

  const handleAdd = async (e) => {
    e.preventDefault();
    await api.addMedicine({
      user_id: user.id,
      medicine_name: name,
      dosage,
      schedule_timing: timing,
      time_str: timeStr,
      instructions
    });
    setName('');
    setDosage('');
    setInstructions('');
    fetchMeds();
  };

  const handleToggle = async (id) => {
    await api.toggleMedicine(id, user.id);
    fetchMeds();
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this medicine reminder?')) {
      await api.deleteMedicine(id, user.id);
      fetchMeds();
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-3xl p-6 text-white shadow-xl">
        <h1 className="text-2xl font-black">Prescription & Medication Reminders</h1>
        <p className="text-xs text-purple-100 mt-1">
          Keep track of ongoing prescriptions, dose timings, instructions, and daily adherence.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm">
          <h2 className="font-extrabold text-sm text-slate-800 mb-4 flex items-center gap-2">
            <Plus className="w-4 h-4 text-purple-600" /> Add Prescription Reminder
          </h2>
          <form onSubmit={handleAdd} className="space-y-3.5">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Medicine Name *</label>
              <input 
                type="text" 
                value={name} 
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Metformin / Paracetamol"
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Dosage</label>
                <input 
                  type="text" 
                  value={dosage} 
                  onChange={(e) => setDosage(e.target.value)}
                  placeholder="e.g. 500mg (1 Tab)"
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Time</label>
                <input 
                  type="text" 
                  value={timeStr} 
                  onChange={(e) => setTimeStr(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Timing Context</label>
              <select 
                value={timing} 
                onChange={(e) => setTiming(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none"
              >
                <option value="Before Meals">Before Meals</option>
                <option value="After Meals">After Meals</option>
                <option value="With Food">With Food</option>
                <option value="Bedtime">Bedtime</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Physician Instructions</label>
              <input 
                type="text" 
                value={instructions} 
                onChange={(e) => setInstructions(e.target.value)}
                placeholder="e.g. Take with warm water"
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none"
              />
            </div>
            <button
              type="submit"
              className="w-full py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 text-white font-bold rounded-xl text-xs shadow-md transition"
            >
              Add Medicine Reminder
            </button>
          </form>
        </div>

        <div className="lg:col-span-7 space-y-3">
          <h2 className="font-extrabold text-sm text-slate-800 mb-2">Active Prescriptions ({medicines.length})</h2>
          {medicines.length === 0 ? (
            <div className="bg-white rounded-3xl p-10 text-center border border-dashed border-slate-300 text-xs text-slate-400">
              No prescriptions registered.
            </div>
          ) : (
            medicines.map((m) => (
              <div key={m.id} className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-purple-50 text-purple-600 rounded-xl">
                    <Pill className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm text-slate-800">{m.medicine_name}</h3>
                    <div className="text-xs text-slate-500 flex items-center gap-2 mt-0.5">
                      <span>{m.dosage}</span>
                      <span>•</span>
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {m.time_str} ({m.schedule_timing})</span>
                    </div>
                    {m.instructions && <p className="text-[11px] text-slate-400 mt-1">{m.instructions}</p>}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleToggle(m.id)}
                    className="px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-bold rounded-xl transition flex items-center gap-1"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" /> Mark Taken Today
                  </button>
                  <button
                    onClick={() => handleDelete(m.id)}
                    className="p-1.5 text-slate-400 hover:text-rose-500 rounded-lg transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
