import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6 text-white font-sans">
          <div className="max-w-md w-full bg-slate-800 border border-slate-700 rounded-3xl p-8 text-center shadow-2xl">
            <div className="w-14 h-14 bg-rose-500/20 text-rose-400 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-rose-500/30">
              <AlertTriangle className="w-8 h-8" />
            </div>
            <h2 className="text-xl font-black mb-2">Something went wrong</h2>
            <p className="text-xs text-slate-300 mb-4 leading-relaxed">
              {this.state.error?.message || 'An unexpected rendering error occurred in the health dashboard.'}
            </p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => {
                  localStorage.removeItem('health_user');
                  window.location.reload();
                }}
                className="px-4 py-2.5 bg-slate-700 hover:bg-slate-600 rounded-xl text-xs font-bold transition"
              >
                Reset Session
              </button>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2.5 bg-sky-600 hover:bg-sky-500 rounded-xl text-xs font-bold flex items-center gap-1.5 transition shadow-lg shadow-sky-600/30"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
