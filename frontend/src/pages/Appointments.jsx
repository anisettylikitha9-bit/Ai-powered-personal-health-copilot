import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import { Calendar, Plus, Trash2, MapPin, Phone } from 'lucide-react';

export default function Appointments() {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [doctor, setDoctor] = useState('');
  const [specialty, setSpecialty] = useState('General Physician');
  const [hospital, setHospital] = useState('');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('10:00 AM');
  const [reason, setReason] = useState('');
  const [phone, setPhone] = useState('');

  const fetchApts = () => {
    if (user?.id) {
      api.getAppointments(user.id).then(res => setAppointments(res.appointments || []));
    }
  };

  useEffect(() => { fetchApts(); }, [user]);

  const handleBook = async (e) => {
    e.preventDefault();
    await api.bookAppointment({
      user_id: user.id,
      doctor_name: doctor,
      specialty,
      clinic_hospital: hospital,
      appointment_date: date,
      appointment_time: time,
      reason,
      phone
    });
    setDoctor('');
    setHospital('');
    setReason('');
    setPhone('');
    fetchApts();
  };

  const handleDelete = async (id) => {
    if (window.confirm('Cancel this appointment?')) {
      await api.deleteAppointment(id, user.id);
      fetchApts();
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-3xl p-6 text-white shadow-xl">
        <h1 className="text-2xl font-black">Doctor Appointments & Consultations</h1>
        <p className="text-xs text-blue-100 mt-1">
          Schedule and manage clinic visits, specialist consultations, and hospital checkups.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm">
          <h2 className="font-extrabold text-sm text-slate-800 mb-4 flex items-center gap-2">
            <Plus className="w-4 h-4 text-blue-600" /> Book Consultation Visit
          </h2>
          <form onSubmit={handleBook} className="space-y-3.5">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Doctor Name *</label>
              <input type="text" value={doctor} onChange={(e) => setDoctor(e.target.value)} placeholder="e.g. Dr. Ananya Sharma" className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" required />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Specialty</label>
                <select value={specialty} onChange={(e) => setSpecialty(e.target.value)} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none">
                  <option value="General Physician">General Physician</option>
                  <option value="Cardiologist">Cardiologist</option>
                  <option value="Dermatologist">Dermatologist</option>
                  <option value="Orthopedic">Orthopedic</option>
                  <option value="Pediatrician">Pediatrician</option>
                  <option value="ENT Specialist">ENT Specialist</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Clinic / Hospital</label>
                <input type="text" value={hospital} onChange={(e) => setHospital(e.target.value)} placeholder="e.g. Apollo Hospital" className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Date *</label>
                <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" required />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Time</label>
                <input type="text" value={time} onChange={(e) => setTime(e.target.value)} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" />
              </div>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Reason for Visit</label>
              <input type="text" value={reason} onChange={(e) => setReason(e.target.value)} placeholder="e.g. Routine annual health checkup" className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none" />
            </div>
            <button type="submit" className="w-full py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 text-white font-bold rounded-xl text-xs shadow-md transition">
              Confirm Appointment
            </button>
          </form>
        </div>

        <div className="lg:col-span-7 space-y-3">
          <h2 className="font-extrabold text-sm text-slate-800 mb-2">Upcoming Consultations ({appointments.length})</h2>
          {appointments.length === 0 ? (
            <div className="bg-white rounded-3xl p-10 text-center border border-dashed border-slate-300 text-xs text-slate-400">
              No appointments scheduled.
            </div>
          ) : (
            appointments.map(a => (
              <div key={a.id} className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
                    <Calendar className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm text-slate-800">{a.doctor_name}</h3>
                    <div className="text-xs text-slate-500 mt-0.5">
                      <span>{a.specialty}</span> • <span>{a.appointment_date} at {a.appointment_time}</span>
                    </div>
                    {a.clinic_hospital && (
                      <div className="text-[11px] text-slate-400 flex items-center gap-1 mt-1">
                        <MapPin className="w-3 h-3" /> {a.clinic_hospital}
                      </div>
                    )}
                  </div>
                </div>
                <button onClick={() => handleDelete(a.id)} className="p-1.5 text-slate-400 hover:text-rose-500 rounded-lg transition">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
