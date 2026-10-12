import React, { useState, useEffect } from 'react';
import { HashRouter as Router, Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import ErrorBoundary from './components/ErrorBoundary';

// 9 Core HealthSaathi AI Pages + Clinical Modules
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Assistant from './pages/Assistant';
import EmergencyTriage from './pages/EmergencyTriage';
import Wellness from './pages/Wellness';
import Analytics from './pages/Analytics';
import ChatHistory from './pages/ChatHistory';
import Profile from './pages/Profile';
import Vitals from './pages/Vitals';
import Medicines from './pages/Medicines';
import Appointments from './pages/Appointments';
import Reports from './pages/Reports';
import SymptomChecker from './pages/SymptomChecker';

function AppLayout() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Derive currentTab from URL path
  const currentPath = location.pathname.replace('/', '') || (user ? 'dashboard' : 'landing');
  const [currentTab, setCurrentTabState] = useState(currentPath);

  useEffect(() => {
    const path = location.pathname.replace('/', '') || (user ? 'dashboard' : 'landing');
    setCurrentTabState(path);
  }, [location.pathname, user]);

  const handleTabChange = (tab) => {
    setCurrentTabState(tab);
    navigate(`/${tab}`);
  };

  // If unauthenticated:
  if (!user) {
    if (location.pathname === '/login') {
      return <Login onBackToLanding={() => navigate('/')} />;
    }
    return (
      <LandingPage 
        setCurrentTab={handleTabChange} 
        onOpenLogin={() => navigate('/login')} 
      />
    );
  }

  return (
    <div className="flex bg-slate-50 min-h-screen">
      {/* Responsive Sidebar */}
      <Sidebar 
        currentTab={currentTab} 
        setCurrentTab={handleTabChange} 
        isMobileMenuOpen={isMobileMenuOpen}
        setIsMobileMenuOpen={setIsMobileMenuOpen}
      />

      {/* Main View Area */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        {/* Top Navigation Bar */}
        <Navbar 
          currentTab={currentTab} 
          setCurrentTab={handleTabChange} 
          isMobileMenuOpen={isMobileMenuOpen}
          setIsMobileMenuOpen={setIsMobileMenuOpen}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto overflow-y-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/landing" element={<LandingPage setCurrentTab={handleTabChange} onOpenLogin={() => {}} />} />
            <Route path="/dashboard" element={<Dashboard setCurrentTab={handleTabChange} />} />
            <Route path="/assistant" element={<Assistant />} />
            <Route path="/triage" element={<EmergencyTriage />} />
            <Route path="/wellness" element={<Wellness />} />
            <Route path="/analytics" element={<Analytics setCurrentTab={handleTabChange} />} />
            <Route path="/history" element={<ChatHistory setCurrentTab={handleTabChange} />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/vitals" element={<Vitals />} />
            <Route path="/medicines" element={<Medicines />} />
            <Route path="/appointments" element={<Appointments />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/symptoms" element={<SymptomChecker />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <LanguageProvider>
        <AuthProvider>
          <Router>
            <AppLayout />
          </Router>
        </AuthProvider>
      </LanguageProvider>
    </ErrorBoundary>
  );
}
