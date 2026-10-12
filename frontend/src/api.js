// frontend/src/api.js - Central API Client
const API_BASE = '/api';

export async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, options);
  if (!res.ok) {
    let errorDetail = 'API request failed';
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || errorDetail;
    } catch (e) {}
    throw new Error(errorDetail);
  }
  return res.json();
}

export const api = {
  // System & Translations
  getTranslations: () => request('/translations'),
  
  // Auth
  login: (username, password) => request('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  }),
  register: (username, password, full_name, email) => request('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, full_name, email })
  }),
  demoLogin: () => request('/auth/demo', { method: 'POST' }),

  // Dashboard
  getDashboardStats: (userId) => request(`/dashboard/stats?user_id=${userId}`),

  // Profile
  getProfile: (userId) => request(`/profile?user_id=${userId}`),
  saveProfile: (data) => request('/profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),

  // Vitals
  getVitals: (userId) => request(`/vitals?user_id=${userId}`),
  logVitals: (data) => request('/vitals', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),
  deleteVital: (vitalId, userId) => request(`/vitals/${vitalId}?user_id=${userId}`, {
    method: 'DELETE'
  }),

  // AI Assistant & Chat
  chat: (userId, message, lang) => request('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, message, lang })
  }),
  chatWithAssistant: (userId, message, lang) => request('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, message, lang })
  }),
  getChatHistory: (userId, limit = 50) => request(`/chat/history?user_id=${userId}&limit=${limit}`),
  clearChatHistory: (userId) => request(`/chat/history?user_id=${userId}`, {
    method: 'DELETE'
  }),

  // Emergency Triage & Symptoms
  triage: (data) => request('/triage', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),
  getSymptomReference: () => request('/symptoms/reference'),
  assessSymptoms: (data) => request('/symptoms/assess', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),

  // Medicines
  getMedicines: (userId) => request(`/medicines?user_id=${userId}`),
  addMedicine: (data) => request('/medicines', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),
  toggleMedicine: (medId, userId) => request(`/medicines/${medId}/toggle?user_id=${userId}`, {
    method: 'POST'
  }),
  deleteMedicine: (medId, userId) => request(`/medicines/${medId}?user_id=${userId}`, {
    method: 'DELETE'
  }),

  // Appointments
  getAppointments: (userId) => request(`/appointments?user_id=${userId}`),
  bookAppointment: (data) => request('/appointments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),
  deleteAppointment: (aptId, userId) => request(`/appointments/${aptId}?user_id=${userId}`, {
    method: 'DELETE'
  }),

  // Wellness & Explainable Insights
  getWellness: (userId, days = 30) => request(`/wellness?user_id=${userId}&days=${days}`),
  logWellness: (data) => request('/wellness', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),
  updateWellness: (recordId, data) => request(`/wellness/${recordId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),
  deleteWellness: (recordId, userId) => request(`/wellness/${recordId}?user_id=${userId}`, {
    method: 'DELETE'
  }),
  saveWellnessGoals: (data) => request('/wellness/goals', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),
  getInsights: (userId) => request(`/insights?user_id=${userId}`),
  wipeUserData: (userId) => request('/privacy/wipe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId })
  }),

  // Medical Documents & PDFs
  getDocuments: (userId, category) => {
    const q = category ? `&category=${encodeURIComponent(category)}` : '';
    return request(`/documents?user_id=${userId}${q}`);
  },
  uploadDocument: (formData) => fetch('/api/documents/upload', {
    method: 'POST',
    body: formData
  }).then(r => {
    if (!r.ok) throw new Error('Upload failed');
    return r.json();
  }),
  deleteDocument: (docId, userId) => request(`/documents/${docId}?user_id=${userId}`, {
    method: 'DELETE'
  }),
  getDocumentDownloadUrl: (docId, userId) => `/api/documents/${docId}/download?user_id=${userId}`,
  getPdfReportUrl: (userId) => `/api/reports/summary-pdf?user_id=${userId}`,
  getCsvReportUrl: (type, userId) => `/api/reports/csv/${type}?user_id=${userId}`,
};
