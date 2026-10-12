import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api';
import { Stethoscope, AlertTriangle, ShieldCheck, CheckSquare, Square } from 'lucide-react';

export default function SymptomChecker() {
  const { user } = useAuth();
  const { lang } = useLanguage();
  const [ref, setRef] = useState(null);
  const [selected, setSelected] = useState([]);
  const [severity, setSeverity] = useState('Moderate');
  const [duration, setDuration] = useState('1-3 days');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getSymptomReference().then(setRef);
  }, []);

  const toggleSymptom = (s) => {
    setSelected(prev => 
      prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]
    );
  };

  const handleAssess = async () => {
    if (selected.length === 0) {
      alert('Please select at least one symptom');
      return;
    }
    setLoading(true);
    try {
      const res = await api.assessSymptoms({
        user_id: user?.id,
        symptoms: selected,
        severity,
        duration,
        lang
      });
      setResult(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-teal-600 to-cyan-600 rounded-3xl p-6 text-white shadow-xl">
        <h1 className="text-2xl font-black">Symptom Checker & Triage Engine</h1>
        <p className="text-xs text-teal-100 mt-1">
          Select symptoms for rule-based clinical evaluation, red flag detection, and home care suggestions.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Symptom Checklist */}
        <div className="lg:col-span-6 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
          <h2 className="font-extrabold text-sm text-slate-800">Select Symptoms ({selected.length})</h2>
          
          <div className="grid grid-cols-2 gap-2 max-h-72 overflow-y-auto p-1">
            {ref?.common_symptoms?.map((s, idx) => {
              const active = selected.includes(s);
              return (
                <button
                  key={idx}
                  onClick={() => toggleSymptom(s)}
                  type="button"
                  className={`p-2.5 rounded-xl text-xs font-semibold text-left transition flex items-center gap-2 border ${
                    active ? 'bg-cyan-50 border-cyan-400 text-cyan-800' : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {active ? <CheckSquare className="w-3.5 h-3.5 text-cyan-600" /> : <Square className="w-3.5 h-3.5 text-slate-400" />}
                  <span className="truncate">{s}</span>
                </button>
              );
            })}
          </div>

          <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-100">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Severity</label>
              <select value={severity} onChange={(e) => setSeverity(e.target.value)} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none">
                <option value="Mild">Mild</option>
                <option value="Moderate">Moderate</option>
                <option value="Severe">Severe</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Duration</label>
              <select value={duration} onChange={(e) => setDuration(e.target.value)} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none">
                <option value="Less than 24 hours">Less than 24 hours</option>
                <option value="1-3 days">1-3 days</option>
                <option value="4-7 days">4-7 days</option>
                <option value="More than a week">More than a week</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleAssess}
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-700 text-white font-bold rounded-xl text-xs shadow-md transition"
          >
            {loading ? 'Evaluating Symptoms...' : 'Analyze Symptoms'}
          </button>
        </div>

        {/* Assessment Result */}
        <div className="lg:col-span-6 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm">
          <h2 className="font-extrabold text-sm text-slate-800 mb-4">Triage Evaluation Result</h2>
          {result ? (
            <div className="space-y-4 text-xs">
              {result.is_emergency && (
                <div className="p-3 bg-rose-50 border-2 border-rose-400 text-rose-800 rounded-2xl flex items-center gap-3 font-bold">
                  <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0" />
                  <span>EMERGENCY: Immediate Medical Consultation Required (Call 112)</span>
                </div>
              )}
              <div className="p-4 bg-slate-50 rounded-2xl space-y-2">
                <div className="font-bold text-slate-800">Identified Findings:</div>
                <p className="text-slate-600">{result.clinical_summary || result.analysis}</p>
              </div>
              {result.recommendations && (
                <div className="space-y-1">
                  <div className="font-bold text-slate-800">Next Steps & Home Guidance:</div>
                  <ul className="list-disc pl-5 text-slate-600 space-y-1">
                    {result.recommendations.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-16 text-xs text-slate-400">
              Select your symptoms and click "Analyze Symptoms" to view triage evaluation.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
