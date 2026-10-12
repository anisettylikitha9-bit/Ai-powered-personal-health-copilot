import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import { User, Heart, Shield, CheckCircle2 } from 'lucide-react';

export default function Profile() {
  const { user } = useAuth();
  const [age, setAge] = useState(30);
  const [gender, setGender] = useState('Male');
  const [height, setHeight] = useState(175);
  const [weight, setWeight] = useState(72);
  const [bloodGroup, setBloodGroup] = useState('O+');
  const [allergies, setAllergies] = useState('');
  const [conditions, setConditions] = useState('');
  const [contactName, setContactName] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [bmi, setBmi] = useState(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (user?.id) {
      api.getProfile(user.id).then(res => {
        if (res.profile) {
          const p = res.profile;
          if (p.age) setAge(p.age);
          if (p.gender) setGender(p.gender);
          if (p.height_cm) setHeight(p.height_cm);
          if (p.weight_kg) setWeight(p.weight_kg);
          if (p.blood_group) setBloodGroup(p.blood_group);
          if (p.allergies) setAllergies(p.allergies);
          if (p.chronic_conditions) setConditions(p.chronic_conditions);
          if (p.emergency_contact_name) setContactName(p.emergency_contact_name);
          if (p.emergency_contact_phone) setContactPhone(p.emergency_contact_phone);
        }
        setBmi(res.bmi);
      });
    }
  }, [user]);

  const handleSave = async (e) => {
    e.preventDefault();
    const res = await api.saveProfile({
      user_id: user.id,
      age: parseInt(age),
      gender,
      height_cm: parseFloat(height),
      weight_kg: parseFloat(weight),
      blood_group: bloodGroup,
      allergies,
      chronic_conditions: conditions,
      emergency_contact_name: contactName,
      emergency_contact_phone: contactPhone
    });
    setBmi(res.bmi);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-sky-600 to-indigo-600 rounded-3xl p-6 text-white shadow-xl">
        <h1 className="text-2xl font-black">Personal Health Profile</h1>
        <p className="text-xs text-sky-100 mt-1">
          Demographics, physiological metrics, allergies, and emergency medical contacts.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <form onSubmit={handleSave} className="lg:col-span-8 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <h2 className="font-extrabold text-sm text-slate-800">Biometric & Medical Information</h2>
            {saved && (
              <span className="text-xs font-bold text-emerald-600 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Profile saved!
              </span>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Age (Years)</label>
              <input type="number" value={age} onChange={(e) => setAge(e.target.value)} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Gender</label>
              <select value={gender} onChange={(e) => setGender(e.target.value)} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none">
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Height (cm)</label>
              <input type="number" step="0.1" value={height} onChange={(e) => setHeight(e.target.value)} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Weight (kg)</label>
              <input type="number" step="0.1" value={weight} onChange={(e) => setWeight(e.target.value)} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Blood Group</label>
              <input type="text" value={bloodGroup} onChange={(e) => setBloodGroup(e.target.value)} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Allergies</label>
              <input type="text" value={allergies} onChange={(e) => setAllergies(e.target.value)} placeholder="e.g. Penicillin, Pollen" className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Chronic Conditions / History</label>
            <input type="text" value={conditions} onChange={(e) => setConditions(e.target.value)} placeholder="e.g. Mild Hypertension, Asthma" className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" />
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-100">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Emergency Contact Name</label>
              <input type="text" value={contactName} onChange={(e) => setContactName(e.target.value)} placeholder="e.g. Ravi Kumar" className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Emergency Phone</label>
              <input type="text" value={contactPhone} onChange={(e) => setContactPhone(e.target.value)} placeholder="+91 98765 43210" className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" />
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100">
            <label className="block text-xs font-bold text-slate-700 mb-2">Preferred Application Language</label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setLang('en')}
                className={`flex-1 py-2 rounded-xl text-xs font-bold border transition cursor-pointer ${
                  lang === 'en' ? 'bg-sky-600 text-white border-sky-600 shadow-xs' : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                English
              </button>
              <button
                type="button"
                onClick={() => setLang('te')}
                className={`flex-1 py-2 rounded-xl text-xs font-bold border transition cursor-pointer ${
                  lang === 'te' ? 'bg-sky-600 text-white border-sky-600 shadow-xs' : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                తెలుగు
              </button>
              <button
                type="button"
                onClick={() => setLang('te-roman')}
                className={`flex-1 py-2 rounded-xl text-xs font-bold border transition cursor-pointer ${
                  lang === 'te-roman' ? 'bg-sky-600 text-white border-sky-600 shadow-xs' : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                Roman Telugu
              </button>
            </div>
          </div>

          <button type="submit" className="w-full py-3 bg-gradient-to-r from-sky-600 to-teal-600 hover:from-sky-700 text-white font-bold rounded-xl text-xs shadow-md transition cursor-pointer">
            Save Profile & Preferences
          </button>
        </form>

        {/* Right Column: BMI Gauge & Privacy Settings */}
        <div className="lg:col-span-4 space-y-6">
          {/* BMI Gauge card */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <h2 className="font-extrabold text-sm text-slate-800 flex items-center gap-2">
              <Heart className="w-4 h-4 text-rose-500" /> BMI & WHO Classification
            </h2>
            {bmi ? (
              <div className="p-4 bg-slate-50 rounded-2xl text-center space-y-2">
                <div className="text-4xl font-black text-slate-800">{bmi.bmi}</div>
                <div className="text-xs font-bold px-3 py-1 rounded-full inline-block bg-emerald-100 text-emerald-700">
                  {bmi.category}
                </div>
                <p className="text-[11px] text-slate-500 leading-snug">
                  Height: {height} cm • Weight: {weight} kg
                </p>
              </div>
            ) : (
              <div className="text-center py-6 text-xs text-slate-400">
                Enter your height and weight to calculate WHO BMI.
              </div>
            )}
          </div>

          {/* 🔒 Privacy & Data Rights Card */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <h2 className="font-extrabold text-sm text-slate-800 flex items-center gap-2">
              <Shield className="w-4 h-4 text-sky-600" /> Privacy & Data Rights
            </h2>
            <p className="text-xs text-slate-500 leading-relaxed">
              Your health data is stored strictly in your local SQLite database with parameterized SQLAlchemy isolation. No third-party data broker sharing.
            </p>

            <div className="pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={async () => {
                  if (window.confirm('⚠️ WARNING: This will permanently delete ALL your vitals, wellness logs, appointments, prescriptions, and chat history. This cannot be undone.\n\nAre you sure you want to proceed?')) {
                    try {
                      await api.wipeUserData(user.id);
                      alert('All personal health records have been permanently erased from the database.');
                      window.location.reload();
                    } catch (err) {
                      alert('Failed to erase data: ' + err.message);
                    }
                  }
                }}
                className="w-full py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <span>Permanently Erase All My Data</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
