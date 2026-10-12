import React, { useState } from 'react';
import { 
  AlertTriangle, PhoneCall, ShieldAlert, HeartPulse, CheckCircle2, 
  HelpCircle, ArrowRight, Activity, Clock, ShieldCheck, Stethoscope
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api';

const RED_FLAGS = [
  { id: 'chest_pain', label_en: 'Severe or crushing chest pain / pressure', label_te: 'తీవ్రమైన ఛాతీ నొప్పి లేదా గుండెపోటు సంకేతాలు', label_roman: 'Severe chest pain / chati noppi' },
  { id: 'breathing', label_en: 'Severe shortness of breath or cannot breathe', label_te: 'తీవ్రమైన శ్వాసకోశ ఇబ్బంది లేదా గాలి ఆడకపోవడం', label_roman: 'Cannot breathe / oopiri aadatledu' },
  { id: 'stroke', label_en: 'Facial drooping, arm weakness, or slurred speech (F.A.S.T.)', label_te: 'ముఖం వంకరపోవడం, ఒక వైపు బలహీనత, మాట తడబడటం (పక్షవాతం)', label_roman: 'Face droop, slurred speech / mata thadabadatam' },
  { id: 'unconscious', label_en: 'Loss of consciousness, fainting with trauma, or unresponsive', label_te: 'స్పృహ తప్పడం లేదా స్పృహ కోల్పోవడం', label_roman: 'Passed out / spruha thappindi' },
  { id: 'bleeding', label_en: 'Severe uncontrolled bleeding or coughing/vomiting blood', label_te: 'తీవ్రమైన రక్తస్రావం లేదా వాంతి/దగ్గులో రక్తం', label_roman: 'Severe bleeding / raktham kaaruthondi' },
  { id: 'anaphylaxis', label_en: 'Severe allergic reaction with swelling of tongue/throat', label_te: 'తీవ్రమైన అలెర్జీ, నాలుక లేదా గొంతు వాపు', label_roman: 'Swelling of throat / gonthu vaapu' },
];

const COMMON_SYMPTOMS = [
  'Headache', 'Fever', 'Cough', 'Sore Throat', 'Runny Nose', 
  'Stomach Pain', 'Dizziness', 'Body Pain', 'Nausea / Vomiting', 'Diarrhea'
];

export default function EmergencyTriage() {
  const { user } = useAuth();
  const { lang } = useLanguage();

  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [selectedRedFlags, setSelectedRedFlags] = useState([]);
  const [freeformText, setFreeformText] = useState('');
  const [severity, setSeverity] = useState('Moderate');
  const [duration, setDuration] = useState('1 to 3 days');
  const [loading, setLoading] = useState(false);
  const [triageResult, setTriageResult] = useState(null);

  const toggleRedFlag = (id) => {
    setSelectedRedFlags(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const toggleSymptom = (symp) => {
    setSelectedSymptoms(prev => 
      prev.includes(symp) ? prev.filter(x => x !== symp) : [...prev, symp]
    );
  };

  const handleEvaluate = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);

    try {
      // Collect red-flag texts if checked
      const redFlagDescriptions = selectedRedFlags.map(rfId => {
        const item = RED_FLAGS.find(r => r.id === rfId);
        return item ? item.label_en : rfId;
      });

      const combinedSymptoms = [...selectedSymptoms, ...redFlagDescriptions];
      const payload = {
        user_id: user?.id,
        symptoms: combinedSymptoms,
        text_input: freeformText,
        severity: severity,
        duration: duration,
        lang: lang || 'en'
      };

      const res = await api.triage(payload);
      setTriageResult(res);
    } catch (err) {
      console.error('Triage assessment failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedSymptoms([]);
    setSelectedRedFlags([]);
    setFreeformText('');
    setSeverity('Moderate');
    setDuration('1 to 3 days');
    setTriageResult(null);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* 🚨 Prominent India Emergency Hotline Banner */}
      <div className="bg-gradient-to-r from-rose-700 via-rose-600 to-amber-600 rounded-3xl p-6 text-white shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1 max-w-2xl">
          <div className="flex items-center gap-2 text-rose-200 text-xs font-black uppercase tracking-wider">
            <ShieldAlert className="w-4 h-4 text-amber-300 animate-pulse" />
            <span>High-Priority Emergency Medical Protocol (India)</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Emergency Triage Assessment
          </h1>
          <p className="text-xs text-rose-100 leading-relaxed">
            If you or someone around you is in severe danger, <strong>do NOT wait for a chatbot response</strong>. Immediately call <strong>112</strong> or <strong>108</strong>.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href="tel:112"
            className="flex items-center gap-2 bg-white text-rose-700 px-5 py-3 rounded-2xl font-black text-sm hover:bg-rose-50 shadow-lg shadow-rose-900/30 transition-transform hover:scale-105"
          >
            <PhoneCall className="w-4 h-4 text-rose-600 animate-bounce" />
            <span>Call 112 (Police / Emergency)</span>
          </a>
          <a
            href="tel:108"
            className="hidden sm:flex items-center gap-2 bg-rose-800/80 border border-white/20 text-white px-4 py-3 rounded-2xl font-bold text-sm hover:bg-rose-800 transition"
          >
            <span>Call 108 (Ambulance)</span>
          </a>
        </div>
      </div>

      {/* 3 Urgency Levels Legend */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-rose-50/70 border border-rose-200 rounded-2xl p-4 space-y-1">
          <div className="flex items-center gap-2 text-rose-700 font-black text-xs uppercase tracking-wider">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-600" />
            <span>Tier 1: Emergency Care Now</span>
          </div>
          <p className="text-[11px] text-slate-600 leading-snug">
            Severe breathing difficulty, stroke signs, unconsciousness, severe chest pain, or massive bleeding. Immediate 112 routing.
          </p>
        </div>

        <div className="bg-amber-50/70 border border-amber-200 rounded-2xl p-4 space-y-1">
          <div className="flex items-center gap-2 text-amber-700 font-black text-xs uppercase tracking-wider">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-600" />
            <span>Tier 2: Prompt Medical Consultation</span>
          </div>
          <p className="text-[11px] text-slate-600 leading-snug">
            Persistent symptoms (&gt;3 days), severe intensity, or co-occurring issues requiring physician exam within 24–48 hours.
          </p>
        </div>

        <div className="bg-emerald-50/70 border border-emerald-200 rounded-2xl p-4 space-y-1">
          <div className="flex items-center gap-2 text-emerald-700 font-black text-xs uppercase tracking-wider">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-600" />
            <span>Tier 3: General Self-Care Guidance</span>
          </div>
          <p className="text-[11px] text-slate-600 leading-snug">
            Low-risk, mild, or early-stage concerns without detected red flags. Home hydration, rest, and careful monitoring.
          </p>
        </div>
      </div>

      {/* 🩺 Interactive Triage Input Panel */}
      <div className="grid lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-6">
          <div className="border-b border-slate-100 pb-4">
            <h2 className="text-lg font-black text-slate-900 flex items-center gap-2">
              <Activity className="w-5 h-5 text-sky-600" />
              <span>Step 1: Check Acute Red-Flag Indicators</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Select any of the following life-threatening symptoms if currently present.
            </p>
          </div>

          {/* Red Flag Checkboxes */}
          <div className="space-y-2.5">
            {RED_FLAGS.map((rf) => {
              const isChecked = selectedRedFlags.includes(rf.id);
              const label = lang === 'te' ? rf.label_te : lang === 'te-roman' ? rf.label_roman : rf.label_en;
              return (
                <label
                  key={rf.id}
                  className={`flex items-start gap-3 p-3 rounded-2xl border transition-all cursor-pointer ${
                    isChecked
                      ? 'bg-rose-50 border-rose-400 text-rose-950 ring-2 ring-rose-300/30'
                      : 'bg-slate-50/60 border-slate-200/80 hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => toggleRedFlag(rf.id)}
                    className="mt-0.5 w-4 h-4 rounded text-rose-600 focus:ring-rose-500 border-slate-300"
                  />
                  <div className="text-xs font-semibold leading-relaxed">
                    {label}
                  </div>
                </label>
              );
            })}
          </div>

          {/* Common Symptoms Selector */}
          <div className="space-y-3 pt-2">
            <h3 className="text-xs font-black text-slate-800 uppercase tracking-wider">
              Step 2: Select Other General Symptoms
            </h3>
            <div className="flex flex-wrap gap-2">
              {COMMON_SYMPTOMS.map((s) => {
                const isSelected = selectedSymptoms.includes(s);
                return (
                  <button
                    key={s}
                    type="button"
                    onClick={() => toggleSymptom(s)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-sky-600 text-white shadow-xs'
                        : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                    }`}
                  >
                    {s}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Freeform Description Input */}
          <div className="space-y-2 pt-2">
            <h3 className="text-xs font-black text-slate-800 uppercase tracking-wider">
              Step 3: Describe in Your Own Words (English, తెలుగు, or Roman Telugu)
            </h3>
            <textarea
              rows={3}
              value={freeformText}
              onChange={(e) => setFreeformText(e.target.value)}
              placeholder="e.g. 'Naaku jwaram ga undi 2 days nunchi' or 'Persistent stomach cramps since morning'..."
              className="w-full text-xs p-3.5 rounded-2xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500 bg-slate-50/50"
            />
          </div>

          {/* Severity & Duration Selectors */}
          <div className="grid sm:grid-cols-2 gap-4 pt-2">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700">Severity Intensity</label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-sky-500 font-medium"
              >
                <option value="Mild">Mild (Noticeable but does not stop routines)</option>
                <option value="Moderate">Moderate (Uncomfortable, slowing activities)</option>
                <option value="Severe">Severe (Incapacitating, severe pain/distress)</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700">Symptom Duration</label>
              <select
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-sky-500 font-medium"
              >
                <option value="Just started today">Just started today (&lt; 24 hours)</option>
                <option value="1 to 3 days">1 to 3 days</option>
                <option value="4 to 7 days">4 to 7 days</option>
                <option value="More than 1 week">More than 1 week</option>
                <option value="More than 2 weeks">More than 2 weeks</option>
              </select>
            </div>
          </div>

          {/* Submit Actions */}
          <div className="flex items-center gap-3 pt-3">
            <button
              onClick={handleEvaluate}
              disabled={loading}
              className="flex-1 py-3.5 bg-gradient-to-r from-sky-600 to-teal-600 hover:from-sky-700 hover:to-teal-700 text-white rounded-2xl font-black text-xs sm:text-sm shadow-md transition-all hover:scale-[1.02] flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {loading ? (
                <span>Evaluating Urgency Rules...</span>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  <span>Run 3-Tier Clinical Assessment</span>
                </>
              )}
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="px-4 py-3.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-2xl transition cursor-pointer"
            >
              Reset
            </button>
          </div>
        </div>

        {/* 📋 Result Card Panel */}
        <div className="lg:col-span-5 space-y-4">
          {triageResult ? (
            <div className={`rounded-3xl p-6 border shadow-lg space-y-5 transition-all ${
              triageResult.tier_level === 1
                ? 'bg-rose-50/90 border-rose-300 text-rose-950 ring-4 ring-rose-400/20'
                : triageResult.tier_level === 2
                  ? 'bg-amber-50/90 border-amber-300 text-amber-950 ring-4 ring-amber-400/20'
                  : 'bg-emerald-50/90 border-emerald-300 text-emerald-950 ring-4 ring-emerald-400/20'
            }`}>
              {/* Badge & Urgency Title */}
              <div className="space-y-2">
                <span className={`inline-block px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${
                  triageResult.tier_level === 1
                    ? 'bg-rose-600 text-white animate-pulse'
                    : triageResult.tier_level === 2
                      ? 'bg-amber-600 text-white'
                      : 'bg-emerald-600 text-white'
                }`}>
                  Urgency Tier {triageResult.tier_level}: {triageResult.tier}
                </span>
                <h3 className="text-xl font-black leading-tight">
                  {triageResult.headline}
                </h3>
                <div className="text-xs font-bold opacity-90">
                  {triageResult.call_to_action}
                </div>
              </div>

              {/* Emergency Call Button if Tier 1 */}
              {triageResult.tier_level === 1 && (
                <a
                  href="tel:112"
                  className="w-full py-3.5 bg-rose-600 hover:bg-rose-700 text-white rounded-2xl font-black text-sm flex items-center justify-center gap-2 shadow-lg shadow-rose-600/30 transition-transform hover:scale-105"
                >
                  <PhoneCall className="w-4 h-4 animate-bounce" />
                  <span>Call 112 Immediately</span>
                </a>
              )}

              {/* Reasons */}
              {triageResult.reasons && triageResult.reasons.length > 0 && (
                <div className="space-y-1.5 text-xs">
                  <div className="font-bold uppercase tracking-wider text-[10px] opacity-75">
                    Trigger Rationale:
                  </div>
                  <ul className="space-y-1">
                    {triageResult.reasons.map((r, i) => (
                      <li key={i} className="flex items-start gap-1.5 leading-relaxed">
                        <span className="font-bold">•</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Steps */}
              {triageResult.urgent_actions && (
                <div className="space-y-2 pt-2 border-t border-slate-200/60">
                  <div className="font-bold uppercase tracking-wider text-[10px] opacity-75">
                    Recommended Immediate Steps:
                  </div>
                  <div className="space-y-1.5 text-xs">
                    {triageResult.urgent_actions.map((act, i) => (
                      <div key={i} className="flex items-start gap-2 bg-white/70 p-2 rounded-xl">
                        <CheckCircle2 className="w-3.5 h-3.5 mt-0.5 text-sky-600 shrink-0" />
                        <span className="leading-snug">{act}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Limitation Notice */}
              <div className="pt-2 text-[10px] opacity-75 italic leading-relaxed border-t border-slate-200/60">
                {triageResult.limitation}
              </div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-3xl p-8 text-center space-y-4 shadow-sm">
              <div className="w-16 h-16 rounded-3xl bg-sky-50 text-sky-600 flex items-center justify-center mx-auto">
                <Stethoscope className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-base font-black text-slate-800">
                  Awaiting Triage Inputs
                </h3>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  Select your symptoms, check red-flag indicators, or type your concern in English/Telugu. Our verified 3-tier rules engine will assess urgency without delay.
                </p>
              </div>

              <div className="bg-slate-50 border border-slate-100 rounded-2xl p-3 text-left text-[11px] text-slate-600 space-y-1">
                <div className="font-bold text-slate-800">Conservative Safety Standards:</div>
                <div>• Never treats lack of keywords as proof of safety.</div>
                <div>• Direct India 112/108 routing for cardiac, stroke, and airway red flags.</div>
                <div>• 100% Non-diagnostic transparent classification.</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
