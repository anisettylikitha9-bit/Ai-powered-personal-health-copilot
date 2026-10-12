import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('health_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      localStorage.setItem('health_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('health_user');
    }
  }, [user]);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const res = await api.login(username, password);
      setUser(res.user);
      return res.user;
    } finally {
      setLoading(false);
    }
  };

  const register = async (username, password, fullName, email) => {
    setLoading(true);
    try {
      const res = await api.register(username, password, fullName, email);
      setUser(res.user);
      return res.user;
    } finally {
      setLoading(false);
    }
  };

  const demoLogin = async () => {
    setLoading(true);
    try {
      const res = await api.demoLogin();
      setUser(res.user);
      return res.user;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, demoLogin, loginDemo: demoLogin, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
