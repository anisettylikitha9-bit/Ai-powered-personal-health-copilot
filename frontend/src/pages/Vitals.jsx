import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import ThreeBioHologram from '../components/ThreeBioHologram';
import { Activity, Plus, Trash2, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function Vitals() {
  const { user } = useAuth();
  const [vitals, setVitals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [systolic, setSystolic] = useState('');
  const [diastolic, setDiastolic] = useState('');
  const [heartRate, setHeartRate] = useState('');
  const [temp, setTemp] = useState('');
  const [glucose, setGlucose] = useState('');
  const [glucoseCtx, setGlucoseCtx] = useState('Fasting');
  const [weight, setWeight] = useState('');
  const [notes, setNotes] = useState('');
  const [valMsg, setValMsg] = useState(null);

  const fetchVitals = () => {
    if (user?.id) {
      setLoading(true);
      api.getVitals(user.id)
        .then(res => setVitals(res.vitals || []))
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  };

  useEffect(() => {
    fetchVitals();
  }, [user]);

  const handleLog = async (e) => {
    e.preventDefault();
    setValMsg(null);
    try {
      const res = await api.logVitals({
        user_id: user.id,
        systolic_bp: systolic ? parseInt(systolic) : null,
        diastolic_bp: diastolic ? parseInt(diastolic) : null,
        heart_rate: heartRate ? parseInt(heartRate) : null,
        temperature_f: temp ? parseFloat(temp) : null,
        blood_glucose_mg_dl: glucose ? parseInt(glucose) : null,
        glucose_context: glucoseCtx,
        weight_kg: weight ? parseFloat(weight) : null,
        notes
      });
      setValMsg(res.validation);
      setSystolic('');
      setDiastolic('');
      setHeartRate('');
      setTemp('');
      setGlucose('');
      setWeight('');
      setNotes('');
      fetchVitals();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this vital reading?')) {
      await api.deleteVital(id, user.id);
      fetchVitals();
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-cyan-600 to-sky-600 rounded-3xl p-6 text-white shadow-xl">
        <h1 className="text-2xl font-black">Vitals & Physiological Tracker</h1>
        <p className="text-xs text-cyan-100 mt-1">
          Record blood pressure, heart rate, blood glucose, and body temperature with automated medical anomaly alerts.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Log Form */}
        <div className="lg:col-span-5 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm">
          <h2 className="font-extrabold text-sm text-slate-800 mb-4 flex items-center gap-2">
            <Plus className="w-4 h-4 text-cyan-600" /> Log New Physiological Reading
          </h2>

          {valMsg && valMsg.flags && valMsg.flags.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 text-amber-800 text-xs p-3 rounded-xl mb-4">
              <div className="font-bold flex items-center gap-1.5 mb-1">
                <AlertTriangle className="w-4 h-4 text-amber-600" /> Anomaly Flag Detected:
              </div>
              <ul className="list-disc pl-5 space-y-0.5">
                {valMsg.flags.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </div>
          )}

          <form onSubmit={handleLog} className="space-y-3.5">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Systolic BP (mmHg)</label>
                <input 
                  type="number" 
                  value={systolic} 
                  onChange={(e) => setSystolic(e.target.value)}
                  placeholder="e.g. 120"
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-cyan-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Diastolic BP (mmHg)</label>
                <input 
                  type="number" 
                  value={diastolic} 
                  onChange={(e) => setDiastolic(e.target.value)}
                  placeholder="e.g. 80"
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-cyan-500 outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Heart Rate (BPM)</label>
                <input 
                  type="number" 
                  value={heartRate} 
                  onChange={(e) => setHeartRate(e.target.value)}
                  placeholder="e.g. 72"
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-cyan-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Body Temp (°F)</label>
                <input 
                  type="number" 
                  step="0.1" 
                  value={temp} 
                  onChange={(e) => setTemp(e.target.value)}
                  placeholder="e.g. 98.6"
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-cyan-500 outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Glucose (mg/dL)</label>
                <input 
                  type="number" 
                  value={glucose} 
                  onChange={(e) => setGlucose(e.target.value)}
                  placeholder="e.g. 95"
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-cyan-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Glucose Context</label>
                <select 
                  value={glucoseCtx} 
                  onChange={(e) => setGlucoseCtx(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-cyan-500 outline-none"
                >
                  <option value="Fasting">Fasting</option>
                  <option value="Post-Prandial">Post-Meal (2h)</option>
                  <option value="Random">Random</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Notes / Context</label>
              <input 
                type="text" 
                value={notes} 
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g. Morning reading before breakfast"
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-cyan-500 outline-none"
              />
            </div>

            <button
              type="submit"
              className="w-full py-3 bg-gradient-to-r from-cyan-600 to-sky-600 hover:from-cyan-700 hover:to-sky-700 text-white font-bold rounded-xl text-xs shadow-md transition"
            >
              Record Vitals
            </button>
          </form>
        </div>

        {/* Right Column: 3D Hologram & History Table */}
        <div className="lg:col-span-7 space-y-6">
          <ThreeBioHologram 
            heartRate={vitals[0]?.heart_rate || 72} 
            systolic={vitals[0]?.systolic_bp || 120} 
            diastolic={vitals[0]?.diastolic_bp || 80} 
            glucose={vitals[0]?.blood_glucose_mg_dl || 95} 
            temperature={vitals[0]?.temperature_f || 98.6}
          />

          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm overflow-x-auto">
            <h2 className="font-extrabold text-sm text-slate-800 mb-4">Historical Readings Log</h2>
          {loading ? (
            <div className="text-center py-10 text-xs text-slate-400">Loading vitals...</div>
          ) : vitals.length === 0 ? (
            <div className="text-center py-10 text-xs text-slate-400">No vitals recorded yet.</div>
          ) : (
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400">
                  <th className="pb-3 font-semibold">Date & Time</th>
                  <th className="pb-3 font-semibold">BP</th>
                  <th className="pb-3 font-semibold">HR</th>
                  <th className="pb-3 font-semibold">Glucose</th>
                  <th className="pb-3 font-semibold">Status</th>
                  <th className="pb-3 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {vitals.map(v => (
                  <tr key={v.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 text-slate-700">{v.recorded_at}</td>
                    <td className="py-3 font-bold text-slate-800">
                      {v.systolic_bp && v.diastolic_bp ? `${v.systolic_bp}/${v.diastolic_bp}` : '--'}
                    </td>
                    <td className="py-3 text-slate-700">{v.heart_rate ? `${v.heart_rate} bpm` : '--'}</td>
                    <td className="py-3 text-slate-700">{v.blood_glucose_mg_dl ? `${v.blood_glucose_mg_dl} mg/dL` : '--'}</td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        v.flag_status === 'Critical' ? 'bg-rose-100 text-rose-700' :
                        v.flag_status === 'Warning' ? 'bg-amber-100 text-amber-700' :
                        'bg-emerald-100 text-emerald-700'
                      }`}>
                        {v.flag_status || 'Normal'}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <button 
                        onClick={() => handleDelete(v.id)}
                        className="text-slate-400 hover:text-rose-500 p-1 rounded transition"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
      </div>
    </div>
  );
}
