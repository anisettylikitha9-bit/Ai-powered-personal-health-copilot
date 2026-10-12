import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api';
import { 
  FileText, Upload, Download, Trash2, Eye, Filter, 
  Search, ShieldAlert, Sparkles, CheckCircle2, AlertTriangle, Plus 
} from 'lucide-react';

export default function Reports() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('vault');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  // Upload Form state
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Lab / Blood Test');
  const [reportDate, setReportDate] = useState(new Date().toISOString().split('T')[0]);
  const [doctorOrLab, setDoctorOrLab] = useState('');
  const [notes, setNotes] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [uploadError, setUploadError] = useState('');

  const fetchDocs = () => {
    if (user?.id) {
      setLoading(true);
      api.getDocuments(user.id, categoryFilter === 'All' ? null : categoryFilter)
        .then(res => setDocuments(res.documents || []))
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  };

  useEffect(() => {
    fetchDocs();
  }, [user, categoryFilter]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setUploadError('Please select a PDF or image file to upload.');
      return;
    }
    if (!title.trim()) {
      setUploadError('Please specify a title for this medical document.');
      return;
    }

    setUploading(true);
    setUploadError('');
    setUploadSuccess('');

    try {
      const formData = new FormData();
      formData.append('user_id', user.id);
      formData.append('title', title);
      formData.append('category', category);
      formData.append('report_date', reportDate);
      formData.append('doctor_or_lab', doctorOrLab);
      formData.append('notes', notes);
      formData.append('file', selectedFile);

      await api.uploadDocument(formData);
      setUploadSuccess('Document uploaded and safely archived in your health vault!');
      setTitle('');
      setDoctorOrLab('');
      setNotes('');
      setSelectedFile(null);
      // Reset file input
      const fileInput = document.getElementById('report_file_input');
      if (fileInput) fileInput.value = '';
      fetchDocs();
    } catch (err) {
      setUploadError(err.message || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId) => {
    if (window.confirm('Are you sure you want to delete this medical report?')) {
      await api.deleteDocument(docId, user.id);
      fetchDocs();
    }
  };

  const filteredDocs = documents.filter(doc => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      doc.title.toLowerCase().includes(q) ||
      (doc.doctor_or_lab && doc.doctor_or_lab.toLowerCase().includes(q)) ||
      (doc.notes && doc.notes.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-teal-600 via-sky-600 to-indigo-600 rounded-3xl p-6 text-white shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-teal-100 text-xs font-bold uppercase tracking-wider mb-1">
            <span>📑 Medical Locker & Export Center</span>
          </div>
          <h1 className="text-2xl font-black tracking-tight">
            Medical Reports & PDF Vault
          </h1>
          <p className="text-xs text-teal-50 mt-1 max-w-lg">
            Privately store your laboratory results, blood tests, radiology scans, and prescriptions. Export consolidated PDF health summaries for physician consultations.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <a
            href={api.getPdfReportUrl(user?.id)}
            target="_blank"
            rel="noreferrer"
            className="bg-white text-teal-700 hover:bg-teal-50 font-bold px-4 py-2.5 rounded-xl text-xs shadow-md transition flex items-center gap-2 hover:scale-105"
          >
            <Download className="w-4 h-4" />
            Consolidated PDF Report
          </a>
        </div>
      </div>

      {/* Main Tabs */}
      <div className="flex bg-slate-100 p-1.5 rounded-2xl max-w-md">
        <button
          onClick={() => setActiveTab('vault')}
          className={`flex-1 py-2 text-xs font-bold rounded-xl transition ${
            activeTab === 'vault' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          📁 Stored Medical PDFs ({documents.length})
        </button>
        <button
          onClick={() => setActiveTab('exports')}
          className={`flex-1 py-2 text-xs font-bold rounded-xl transition ${
            activeTab === 'exports' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          📥 CSV Data Exports
        </button>
      </div>

      {activeTab === 'vault' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Upload Card */}
          <div className="lg:col-span-5 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm">
            <h2 className="font-extrabold text-sm text-slate-800 mb-2 flex items-center gap-2">
              <Upload className="w-4 h-4 text-cyan-600" />
              Upload Medical Report (PDF / Image)
            </h2>
            <p className="text-xs text-slate-400 mb-4">
              Add lab reports, prescriptions, or imaging scans to your private encrypted storage.
            </p>

            {uploadSuccess && (
              <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs p-3 rounded-xl mb-4 font-medium flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>{uploadSuccess}</span>
              </div>
            )}

            {uploadError && (
              <div className="bg-rose-50 border border-rose-200 text-rose-700 text-xs p-3 rounded-xl mb-4 font-medium flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-600" />
                <span>{uploadError}</span>
              </div>
            )}

            <form onSubmit={handleUpload} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Select File (PDF, PNG, JPG) *
                </label>
                <input 
                  id="report_file_input"
                  type="file" 
                  accept=".pdf,.png,.jpg,.jpeg,.txt"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100 cursor-pointer border border-slate-200 rounded-xl p-1 bg-slate-50"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Document Title *</label>
                <input 
                  type="text" 
                  value={title} 
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-sky-500 outline-none" 
                  placeholder="e.g. Complete Blood Count (CBC) & Lipid Panel"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Category</label>
                  <select 
                    value={category} 
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-sky-500 outline-none"
                  >
                    <option value="Lab / Blood Test">Lab / Blood Test</option>
                    <option value="Radiology / Scan (X-Ray, MRI, CT)">Radiology / Scan</option>
                    <option value="Doctor Prescription">Doctor Prescription</option>
                    <option value="Discharge Summary">Discharge Summary</option>
                    <option value="Vaccination Record">Vaccination Record</option>
                    <option value="Other Medical Document">Other Medical Document</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Report Date</label>
                  <input 
                    type="date" 
                    value={reportDate} 
                    onChange={(e) => setReportDate(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-sky-500 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Clinic / Doctor / Lab Name</label>
                <input 
                  type="text" 
                  value={doctorOrLab} 
                  onChange={(e) => setDoctorOrLab(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-sky-500 outline-none" 
                  placeholder="e.g. Apollo Diagnostics / Dr. Ananya Sharma"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Clinical Notes / Key Findings</label>
                <textarea 
                  value={notes} 
                  onChange={(e) => setNotes(e.target.value)}
                  rows="2"
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-sky-500 outline-none resize-none" 
                  placeholder="e.g. Fasting sugar 92 mg/dL, normal hemoglobin level"
                ></textarea>
              </div>

              <button
                type="submit"
                disabled={uploading}
                className="w-full py-3 bg-gradient-to-r from-sky-600 to-teal-600 hover:from-sky-700 hover:to-teal-700 text-white font-bold rounded-xl text-xs shadow-md shadow-sky-500/20 transition flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Upload className="w-4 h-4" />
                {uploading ? 'Archiving Document...' : 'Upload & Save to Vault'}
              </button>
            </form>
          </div>

          {/* Stored Documents List */}
          <div className="lg:col-span-7 space-y-4">
            {/* Filters */}
            <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm flex flex-wrap items-center justify-between gap-3">
              <div className="relative flex-1 min-w-[180px]">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input 
                  type="text" 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search title, lab or notes..."
                  className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium outline-none focus:ring-2 focus:ring-sky-500"
                />
              </div>
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-slate-400" />
                <select 
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-bold text-slate-700 outline-none"
                >
                  <option value="All">All Categories</option>
                  <option value="Lab / Blood Test">Lab / Blood Test</option>
                  <option value="Radiology / Scan (X-Ray, MRI, CT)">Radiology</option>
                  <option value="Doctor Prescription">Prescriptions</option>
                  <option value="Discharge Summary">Discharge</option>
                </select>
              </div>
            </div>

            {/* Document Cards */}
            {loading ? (
              <div className="text-center py-12 text-slate-400 text-xs">Loading vault...</div>
            ) : filteredDocs.length === 0 ? (
              <div className="bg-white rounded-3xl p-10 text-center border border-dashed border-slate-300">
                <FileText className="w-12 h-12 text-slate-300 mx-auto mb-2" />
                <div className="font-bold text-sm text-slate-700">No medical reports found</div>
                <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                  Upload your laboratory results or scan PDFs using the form on the left.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredDocs.map((doc) => (
                  <div key={doc.id} className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm hover:shadow-md transition">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-3">
                        <div className="p-3 bg-gradient-to-br from-sky-50 to-cyan-50 rounded-2xl border border-sky-100 text-sky-600 flex-shrink-0">
                          <FileText className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <h3 className="font-bold text-sm text-slate-800">{doc.title}</h3>
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-100 text-cyan-800">
                              {doc.category}
                            </span>
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                              {doc.file_type || 'PDF'} • {doc.file_size_kb} KB
                            </span>
                          </div>
                          <div className="text-xs text-slate-500 mt-1 flex items-center gap-3">
                            <span>📅 {doc.report_date}</span>
                            {doc.doctor_or_lab && <span>🏥 {doc.doctor_or_lab}</span>}
                          </div>
                          {doc.notes && (
                            <p className="text-xs text-slate-600 mt-2 bg-slate-50 p-2 rounded-xl">
                              {doc.notes}
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <a 
                          href={api.getDocumentDownloadUrl(doc.id, user.id)}
                          download={doc.file_name}
                          className="p-2 text-sky-600 hover:bg-sky-50 rounded-xl transition"
                          title="Download Document"
                        >
                          <Download className="w-4 h-4" />
                        </a>
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="p-2 text-rose-500 hover:bg-rose-50 rounded-xl transition"
                          title="Delete Document"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        /* CSV Exports */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm text-center">
            <h3 className="font-bold text-sm text-slate-800 mb-1">Vitals Data (CSV)</h3>
            <p className="text-xs text-slate-400 mb-4">Export all recorded blood pressure, glucose, and heart rate logs.</p>
            <a 
              href={api.getCsvReportUrl('vitals', user?.id)}
              className="inline-flex items-center gap-2 bg-sky-50 text-sky-700 hover:bg-sky-100 font-bold px-4 py-2 rounded-xl text-xs transition"
            >
              <Download className="w-3.5 h-3.5" /> Download Vitals CSV
            </a>
          </div>

          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm text-center">
            <h3 className="font-bold text-sm text-slate-800 mb-1">Wellness Logs (CSV)</h3>
            <p className="text-xs text-slate-400 mb-4">Export 90 days of daily hydration, sleep, and exercise data.</p>
            <a 
              href={api.getCsvReportUrl('wellness', user?.id)}
              className="inline-flex items-center gap-2 bg-teal-50 text-teal-700 hover:bg-teal-100 font-bold px-4 py-2 rounded-xl text-xs transition"
            >
              <Download className="w-3.5 h-3.5" /> Download Wellness CSV
            </a>
          </div>

          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm text-center">
            <h3 className="font-bold text-sm text-slate-800 mb-1">Prescriptions (CSV)</h3>
            <p className="text-xs text-slate-400 mb-4">Export active and past medication reminder schedules.</p>
            <a 
              href={api.getCsvReportUrl('medicines', user?.id)}
              className="inline-flex items-center gap-2 bg-purple-50 text-purple-700 hover:bg-purple-100 font-bold px-4 py-2 rounded-xl text-xs transition"
            >
              <Download className="w-3.5 h-3.5" /> Download Medicine CSV
            </a>
          </div>

          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm text-center">
            <h3 className="font-bold text-sm text-slate-800 mb-1">Appointments (CSV)</h3>
            <p className="text-xs text-slate-400 mb-4">Export doctor visits, clinic addresses, and consultation history.</p>
            <a 
              href={api.getCsvReportUrl('appointments', user?.id)}
              className="inline-flex items-center gap-2 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 font-bold px-4 py-2 rounded-xl text-xs transition"
            >
              <Download className="w-3.5 h-3.5" /> Download Visits CSV
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
