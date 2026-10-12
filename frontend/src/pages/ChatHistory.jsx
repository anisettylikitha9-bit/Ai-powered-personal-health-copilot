import React, { useState, useEffect } from 'react';
import { 
  Bot, User, Trash2, Search, Calendar, MessageSquare, 
  ArrowRight, AlertTriangle, ShieldCheck, RefreshCw
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';

export default function ChatHistory({ setCurrentTab }) {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);

  const fetchHistory = async () => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const res = await api.getChatHistory(user.id, 60);
      setHistory(res.history || []);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [user]);

  const handleClear = async () => {
    if (!window.confirm('Are you sure you want to delete your entire conversation history? This cannot be undone.')) {
      return;
    }
    setClearing(true);
    try {
      await api.clearChatHistory(user.id);
      setHistory([]);
    } catch (err) {
      console.error('Failed to clear chat history:', err);
    } finally {
      setClearing(false);
    }
  };

  const filteredHistory = history.filter(item => 
    item.content.toLowerCase().includes(search.toLowerCase()) ||
    (item.timestamp && item.timestamp.includes(search))
  );

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* 🧭 Header */}
      <div className="bg-gradient-to-r from-sky-600 via-indigo-600 to-purple-600 rounded-3xl p-6 text-white shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-indigo-200 text-xs font-bold uppercase tracking-wider">
            <MessageSquare className="w-3.5 h-3.5 text-cyan-300" />
            <span>HealthSaathi AI Conversation Archives</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Chat & Consultation History
          </h1>
          <p className="text-xs text-indigo-100 max-w-lg leading-relaxed">
            Review past health questions, symptom evaluations, and safety recommendations stored securely in your private database.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurrentTab && setCurrentTab('assistant')}
            className="flex items-center gap-1.5 px-4 py-2.5 bg-white text-indigo-900 rounded-2xl font-bold text-xs shadow-md hover:bg-indigo-50 transition cursor-pointer"
          >
            <span>Open Assistant</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
          {history.length > 0 && (
            <button
              onClick={handleClear}
              disabled={clearing}
              className="flex items-center gap-1.5 px-3.5 py-2.5 bg-rose-500/80 hover:bg-rose-600 text-white rounded-2xl font-bold text-xs shadow-md transition cursor-pointer disabled:opacity-50"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear History</span>
            </button>
          )}
        </div>
      </div>

      {/* 🔍 Search Filter */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search conversations by symptoms, questions, or dates..."
            className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500 bg-slate-50/50"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-slate-500">
            {filteredHistory.length} Exchanges
          </span>
          <button
            onClick={fetchHistory}
            title="Refresh history"
            className="p-2 rounded-xl text-slate-500 hover:bg-slate-100 transition cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* 📜 Message List */}
      {loading ? (
        <div className="bg-white border border-slate-200 rounded-3xl p-12 text-center text-xs font-bold text-slate-500">
          Loading conversation history...
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-3xl p-12 text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center mx-auto">
            <MessageSquare className="w-7 h-7" />
          </div>
          <h3 className="text-base font-black text-slate-800">
            {search ? 'No Matches Found' : 'No Chat History Yet'}
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            {search 
              ? 'Try adjusting your search keyword.' 
              : 'Ask a question in English, Telugu, or Roman Telugu to save your first consultation.'}
          </p>
          <button
            onClick={() => setCurrentTab && setCurrentTab('assistant')}
            className="px-5 py-2.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl font-bold text-xs shadow-md transition"
          >
            Start Conversation Now
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredHistory.map((item, index) => {
            const isUser = item.role === 'user';
            const isEmergency = item.content.includes('🚨') || item.content.includes('EMERGENCY');
            return (
              <div
                key={index}
                className={`rounded-3xl p-5 border shadow-xs transition-all ${
                  isEmergency
                    ? 'bg-rose-50/70 border-rose-300'
                    : isUser
                      ? 'bg-sky-50/50 border-sky-200/80 ml-4 sm:ml-12'
                      : 'bg-white border-slate-200 mr-4 sm:mr-12'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                      isUser ? 'bg-sky-600 text-white' : isEmergency ? 'bg-rose-600 text-white' : 'bg-slate-800 text-white'
                    }`}>
                      {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                    </div>
                    <span className="text-xs font-black text-slate-900">
                      {isUser ? 'You' : 'HealthSaathi AI Copilot'}
                    </span>
                    {isEmergency && (
                      <span className="text-[10px] font-black uppercase bg-rose-600 text-white px-2 py-0.5 rounded-full flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" />
                        <span>Emergency Red Flag</span>
                      </span>
                    )}
                  </div>

                  <span className="text-[10px] font-medium text-slate-400 flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    <span>{item.timestamp ? new Date(item.timestamp).toLocaleString() : 'Recent'}</span>
                  </span>
                </div>

                <div className="text-xs text-slate-700 whitespace-pre-wrap leading-relaxed pl-9">
                  {item.content}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
