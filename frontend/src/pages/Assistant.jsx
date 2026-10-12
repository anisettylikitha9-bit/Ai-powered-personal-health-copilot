import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api';
import { 
  Bot, Send, AlertTriangle, Sparkles, User, 
  Mic, MicOff, Volume2, VolumeX, Radio, Play, Square,
  Activity, CheckCircle2, RotateCcw, Globe, Stethoscope
} from 'lucide-react';

export default function Assistant() {
  const { user } = useAuth();
  const { lang, setLang, t } = useLanguage();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: lang === 'te' 
        ? 'నమస్కారం! నేను మీ AI వ్యక్తిగత ఆరోగ్య మరియు వాయిస్ సహాయకుడిని. మైక్రోఫోన్ ఉపయోగించి మాట్లాడవచ్చు లేదా టైప్ చేయవచ్చు.'
        : 'Hello! I am your AI Voice & Clinical Health Assistant. You can speak into your microphone or type your symptoms anytime (e.g. "I have a severe headache", "fever since yesterday").'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // --- Voice Assistant State ---
  const [isListening, setIsListening] = useState(false);
  const [listeningInterim, setListeningInterim] = useState('');
  const [speakingIndex, setSpeakingIndex] = useState(null);
  const [autoSpeak, setAutoSpeak] = useState(true);
  const [speechSupported, setSpeechSupported] = useState(true);

  const recognitionRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Scroll to bottom on new messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, listeningInterim]);

  // Clean Markdown for Natural Clinical Speech Synthesis
  const cleanTextForSpeech = (markdown) => {
    if (!markdown) return '';
    return markdown
      .replace(/###|\*\*|\*|__|`|--|•|🚨|💧|🌙|⚕️|ℹ️|\[.*?\]\(.*?\)/g, ' ')
      .replace(/\n+/g, '. ')
      .replace(/\s+/g, ' ')
      .trim();
  };

  // Text-To-Speech (Assistant Voice Read-Aloud)
  const speakText = (text, index) => {
    if (!('speechSynthesis' in window)) return;

    // If currently speaking this message, toggle stop
    if (speakingIndex === index) {
      window.speechSynthesis.cancel();
      setSpeakingIndex(null);
      return;
    }

    window.speechSynthesis.cancel();
    const cleanStr = cleanTextForSpeech(text);
    if (!cleanStr) return;

    const utterance = new SpeechSynthesisUtterance(cleanStr);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.lang = lang === 'te' ? 'te-IN' : 'en-US';

    // Try finding natural voices
    const voices = window.speechSynthesis.getVoices();
    if (voices && voices.length > 0) {
      const preferredVoice = voices.find(v => 
        (lang === 'te' && v.lang.includes('te')) ||
        (lang !== 'te' && (v.name.includes('Natural') || v.name.includes('Google') || v.lang.includes('en')))
      );
      if (preferredVoice) utterance.voice = preferredVoice;
    }

    utterance.onstart = () => setSpeakingIndex(index);
    utterance.onend = () => setSpeakingIndex(null);
    utterance.onerror = () => setSpeakingIndex(null);

    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setSpeakingIndex(null);
  };

  // Speech-To-Text (Microphone Dictation Setup)
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSpeechSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = lang === 'te' ? 'te-IN' : 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      setListeningInterim('');
      stopSpeaking(); // Stop talking while listening to user
    };

    recognition.onresult = (event) => {
      let interim = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }

      if (interim) {
        setListeningInterim(interim);
      }

      if (finalTranscript) {
        const fullText = (input + ' ' + finalTranscript).trim();
        setInput(fullText);
        setListeningInterim('');
        setIsListening(false);
        // Auto-send voice query immediately
        handleSend(fullText);
      }
    };

    recognition.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      setIsListening(false);
      setListeningInterim('');
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch (e) {}
      }
      stopSpeaking();
    };
  }, [lang, input]);

  // Toggle Microphone
  const toggleListening = () => {
    if (!speechSupported) {
      alert('Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.');
      return;
    }

    if (isListening) {
      try {
        recognitionRef.current?.stop();
      } catch (e) {}
      setIsListening(false);
    } else {
      try {
        recognitionRef.current?.start();
      } catch (e) {
        console.error('Failed to start speech recognition:', e);
      }
    }
  };

  // Send Message & Handle Response
  const handleSend = async (textToSend) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    stopSpeaking();
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const res = await api.chatWithAssistant(user?.id, text, lang);
      const newAssistantMsg = {
        role: 'assistant',
        content: res.content,
        isEmergency: res.is_emergency,
        matchedRule: res.matched_rule,
        symptoms: res.matched_symptoms,
        follow_ups: res.follow_ups || []
      };

      setMessages(prev => {
        const nextMsgs = [...prev, newAssistantMsg];
        // If autoSpeak is enabled, speak the answer
        if (autoSpeak) {
          setTimeout(() => {
            speakText(res.content, nextMsgs.length - 1);
          }, 300);
        }
        return nextMsgs;
      });
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I encountered an error analyzing your inquiry. Please try again or consult a doctor.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const samplePrompts = [
    "Naaku jwaram ga undi.",
    "I have a headache.",
    "Explain dehydration in Telugu.",
    "How can I improve my sleep?",
    "What are normal blood pressure ranges?",
    "Healthy plate nutrition tips"
  ];

  return (
    <div className="space-y-6">
      {/* 🌟 Futuristic Voice & Clinical Header */}
      <div className="relative overflow-hidden bg-gradient-to-r from-sky-600 via-indigo-600 to-purple-600 rounded-3xl p-6 text-white shadow-xl flex flex-wrap items-center justify-between gap-4">
        {/* Ambient Glow */}
        <div className="absolute top-0 right-1/4 w-64 h-64 bg-cyan-400/20 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-xl">
          <div className="flex items-center gap-2 text-indigo-200 text-xs font-bold uppercase tracking-wider mb-1">
            <Radio className="w-3.5 h-3.5 text-cyan-300 animate-pulse" />
            <span>AI Voice & Clinical Symptom Copilot</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            AI Health Voice Assistant
          </h1>
          <p className="text-xs text-indigo-100 mt-1 leading-relaxed">
            Hands-free voice recognition, real-time medical speech synthesis, red-flag triage filters, and non-prescriptive home guidance.
          </p>
        </div>

        {/* 3D Holographic Interactive Voice Orb */}
        <div className="relative z-10 flex items-center gap-3">
          <button
            onClick={toggleListening}
            className={`relative p-3.5 rounded-2xl backdrop-blur-md border transition-all duration-300 flex items-center gap-3 shadow-lg ${
              isListening 
                ? 'bg-rose-500/90 border-rose-300 text-white shadow-rose-500/50 scale-105 ring-4 ring-rose-400/30' 
                : speakingIndex !== null
                  ? 'bg-cyan-500/90 border-cyan-300 text-slate-950 shadow-cyan-500/40 ring-4 ring-cyan-400/30'
                  : 'bg-white/15 border-white/25 hover:bg-white/25 text-white'
            }`}
            title={isListening ? "Listening... Tap to stop" : "Tap to speak with Voice Assistant"}
          >
            {/* Visualizer Waves */}
            <div className="flex items-center gap-0.5 h-6">
              {[1, 2, 3, 4, 5].map((bar) => (
                <span
                  key={bar}
                  className={`w-1 rounded-full transition-all duration-200 ${
                    isListening
                      ? 'bg-white animate-bounce'
                      : speakingIndex !== null
                        ? 'bg-slate-950 animate-pulse'
                        : 'bg-white/60 h-2'
                  }`}
                  style={{
                    height: isListening ? `${(bar % 3 + 1) * 7}px` : speakingIndex !== null ? `${(bar * 4)}px` : '8px',
                    animationDelay: `${bar * 0.1}s`
                  }}
                />
              ))}
            </div>

            <div className="text-left">
              <div className="text-[10px] font-semibold opacity-80 uppercase tracking-wider">
                {isListening ? 'Listening...' : speakingIndex !== null ? 'Speaking...' : 'Voice Orb'}
              </div>
              <div className="text-xs font-black">
                {isListening ? 'Speak Now' : speakingIndex !== null ? 'Tap to Mute' : 'Tap to Talk'}
              </div>
            </div>

            <div className={`p-2 rounded-xl ${isListening ? 'bg-rose-700/60' : 'bg-white/20'}`}>
              {isListening ? <Mic className="w-5 h-5 text-white animate-pulse" /> : <Mic className="w-5 h-5" />}
            </div>
          </button>

          {/* Auto-Speak Toggle */}
          <button
            onClick={() => {
              if (speakingIndex !== null) stopSpeaking();
              setAutoSpeak(!autoSpeak);
            }}
            className={`px-3 py-3 rounded-2xl backdrop-blur-md border text-xs font-bold transition flex items-center gap-1.5 shadow-md ${
              autoSpeak 
                ? 'bg-emerald-500/30 border-emerald-400/50 text-emerald-200' 
                : 'bg-white/10 border-white/20 text-slate-300 hover:text-white'
            }`}
            title="Toggle automatic speech response"
          >
            {autoSpeak ? <Volume2 className="w-4 h-4 text-emerald-300" /> : <VolumeX className="w-4 h-4 text-slate-400" />}
            <span className="hidden sm:inline">{autoSpeak ? 'Audio ON' : 'Audio OFF'}</span>
          </button>
        </div>
      </div>

      {/* 🌐 Interactive Language Selector */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white border border-slate-200/80 rounded-2xl p-3 shadow-xs">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
          <Globe className="w-4 h-4 text-sky-600" />
          <span>Assistant Language / భాష:</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs font-bold">
          <button
            type="button"
            onClick={() => setLang('en')}
            className={`px-3 py-1.5 rounded-xl transition cursor-pointer ${
              lang === 'en' ? 'bg-sky-600 text-white shadow-xs' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
            }`}
          >
            English
          </button>
          <button
            type="button"
            onClick={() => setLang('te')}
            className={`px-3 py-1.5 rounded-xl transition cursor-pointer ${
              lang === 'te' ? 'bg-sky-600 text-white shadow-xs' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
            }`}
          >
            తెలుగు (Telugu)
          </button>
          <button
            type="button"
            onClick={() => setLang('te-roman')}
            className={`px-3 py-1.5 rounded-xl transition cursor-pointer ${
              lang === 'te-roman' ? 'bg-sky-600 text-white shadow-xs' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
            }`}
          >
            Roman Telugu
          </button>
        </div>
      </div>

      {/* Suggested prompts */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        <span className="text-slate-400 font-semibold whitespace-nowrap flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-amber-500" />
          <span>Quick Prompts:</span>
        </span>
        {samplePrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(p)}
            className="px-3 py-1.5 bg-white border border-slate-200 hover:border-indigo-400 text-slate-700 hover:text-indigo-700 font-medium rounded-xl whitespace-nowrap shadow-sm transition hover:scale-[1.02] cursor-pointer"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Chat Container */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm flex flex-col h-[530px] overflow-hidden">
        {/* Messages list */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((m, idx) => (
            <div key={idx} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {m.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-sky-600 to-indigo-600 text-white flex items-center justify-center flex-shrink-0 text-xs font-bold shadow-sm mt-1">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div className={`max-w-xl rounded-2xl p-4 text-xs leading-relaxed relative group ${
                m.role === 'user'
                  ? 'bg-sky-600 text-white font-medium rounded-tr-none shadow-md'
                  : m.isEmergency 
                    ? 'bg-rose-50 border-2 border-rose-400 text-rose-900 rounded-tl-none font-medium'
                    : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-tl-none font-normal'
              }`}>
                {m.isEmergency && (
                  <div className="flex items-center gap-2 text-rose-700 font-bold mb-2 pb-2 border-b border-rose-200">
                    <AlertTriangle className="w-4 h-4" />
                    <span>EMERGENCY ALERT: Call India 112 Immediately</span>
                  </div>
                )}

                <div className="whitespace-pre-wrap">{m.content}</div>

                {/* Clickable Follow-up questions */}
                {m.follow_ups && m.follow_ups.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-slate-200/60 space-y-1.5">
                    <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                      <Sparkles className="w-3 h-3 text-amber-500" />
                      <span>Relevant Follow-Up Questions:</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {m.follow_ups.map((q, qIdx) => (
                        <button
                          key={qIdx}
                          type="button"
                          onClick={() => handleSend(q)}
                          className="text-[11px] bg-white border border-sky-200 hover:border-sky-400 text-sky-800 font-semibold px-2.5 py-1 rounded-xl shadow-2xs hover:bg-sky-50 transition cursor-pointer text-left"
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Speaker button on Assistant responses */}
                {m.role === 'assistant' && (
                  <div className="mt-3 pt-2.5 border-t border-slate-200/60 flex items-center justify-between text-[11px]">
                    <button
                      onClick={() => speakText(m.content, idx)}
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg font-bold transition cursor-pointer ${
                        speakingIndex === idx
                          ? 'bg-cyan-500 text-slate-950 shadow-sm animate-pulse'
                          : 'bg-slate-200/70 hover:bg-slate-200 text-slate-700'
                      }`}
                    >
                      {speakingIndex === idx ? (
                        <>
                          <Square className="w-3 h-3 fill-current" />
                          <span>Stop Reading</span>
                        </>
                      ) : (
                        <>
                          <Volume2 className="w-3 h-3 text-cyan-600" />
                          <span>Listen Out Loud</span>
                        </>
                      )}
                    </button>

                    {m.matchedRule && (
                      <span className="text-[10px] text-slate-400 font-semibold truncate max-w-[220px]">
                        {m.matchedRule}
                      </span>
                    )}
                  </div>
                )}
              </div>

              {m.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-slate-800 text-white flex items-center justify-center flex-shrink-0 text-xs font-bold mt-1 shadow-sm">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {/* AI Loading State */}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-sm">
                <Bot className="w-4 h-4 animate-spin" />
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 text-xs text-slate-600 rounded-tl-none flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping"></span>
                <span>AI Voice Copilot is evaluating your symptoms and checking medical red flags...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Live Microphone Interim Feedback Banner */}
        {isListening && (
          <div className="bg-gradient-to-r from-rose-50 to-pink-50 border-t border-rose-200 px-6 py-2.5 flex items-center justify-between text-xs animate-pulse">
            <div className="flex items-center gap-2 text-rose-700 font-bold">
              <Mic className="w-4 h-4 text-rose-600 animate-ping" />
              <span>Listening to your voice... Speak your symptoms clearly:</span>
              <span className="font-medium text-slate-700 italic ml-1">
                "{listeningInterim || 'Listening...'}"
              </span>
            </div>
            <button 
              onClick={toggleListening}
              className="text-[11px] font-bold text-rose-700 hover:text-rose-900 underline"
            >
              Cancel
            </button>
          </div>
        )}

        {/* Input Bar with Voice Mic Button */}
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSend(); }} 
          className="p-4 border-t border-slate-100 flex items-center gap-2.5 bg-slate-50/50"
        >
          {/* Microphone Dictation Trigger */}
          <button
            type="button"
            onClick={toggleListening}
            className={`p-3 rounded-2xl font-bold text-xs transition shadow-md flex items-center justify-center ${
              isListening
                ? 'bg-rose-600 text-white ring-4 ring-rose-400/40 animate-pulse shadow-rose-600/30'
                : 'bg-white hover:bg-slate-100 border border-slate-200 text-indigo-600 hover:text-indigo-700 shadow-sm'
            }`}
            title={isListening ? "Listening... Tap to stop" : "Tap to speak with voice"}
          >
            {isListening ? <MicOff className="w-5 h-5 text-white" /> : <Mic className="w-5 h-5" />}
          </button>

          {/* Text Input Field */}
          <input 
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? "Listening to your voice..." : "Type or speak your symptoms (e.g. 'I have a high fever and sore throat')..."}
            className="flex-1 px-4 py-3 bg-white border border-slate-200 rounded-2xl text-xs font-medium focus:ring-2 focus:ring-indigo-500 outline-none shadow-inner"
          />

          {/* Send Button */}
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-5 py-3 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-700 hover:to-indigo-700 text-white font-bold rounded-2xl text-xs shadow-md shadow-indigo-500/20 transition flex items-center gap-2 disabled:opacity-40 hover:scale-[1.02] cursor-pointer"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>

        {/* ⚕️ Transparent Clinical Safety Disclaimer */}
        <div className="px-4 py-2 bg-slate-50 border-t border-slate-100 text-[10px] text-slate-500 text-center flex items-center justify-center gap-1.5">
          <Stethoscope className="w-3.5 h-3.5 text-sky-600 shrink-0" />
          <span>HealthSaathi AI is an educational wellness copilot and not a doctor. It cannot diagnose diseases, prescribe medication, or replace professional consultation.</span>
        </div>
      </div>
    </div>
  );
}
