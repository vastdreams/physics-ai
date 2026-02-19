/**
 * PATH: frontend/src/contexts/AuthContext.jsx
 * PURPOSE: Authentication state management with JWT tokens
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { API_BASE } from '../config';

const AuthContext = createContext(null);

const TOKEN_KEY = 'beyondfrontier_access_token';
const REFRESH_KEY = 'beyondfrontier_refresh_token';
const USER_KEY = 'beyondfrontier_user';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem(USER_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch { return null; }
  });
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const isAuthenticated = !!token && !!user;

  /** Login with email + password */
  const login = useCallback(async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Login failed');
      }

      localStorage.setItem(TOKEN_KEY, data.access_token);
      localStorage.setItem(REFRESH_KEY, data.refresh_token);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));
      setToken(data.access_token);
      setUser(data.user);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  /** Register a new account and auto-login */
  const register = useCallback(async (name, email, password) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password }),
      });
      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Registration failed');
      }

      // Auto-login after registration
      return await login(email, password);
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, [login]);

  /** Logout */
  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
  }, []);

  /** Verify token on mount */
  useEffect(() => {
    if (!token) return;
    fetch(`${API_BASE}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(data => {
        if (data.success && data.user) {
          setUser(data.user);
          localStorage.setItem(USER_KEY, JSON.stringify(data.user));
        } else {
          logout();
        }
      })
      .catch(() => {
        // Token might be expired -- try refresh
        const refreshToken = localStorage.getItem(REFRESH_KEY);
        if (refreshToken) {
          fetch(`${API_BASE}/api/v1/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
          })
            .then(r => r.ok ? r.json() : Promise.reject())
            .then(data => {
              if (data.success && data.access_token) {
                localStorage.setItem(TOKEN_KEY, data.access_token);
                setToken(data.access_token);
              } else {
                logout();
              }
            })
            .catch(() => logout());
        }
        // Don't logout immediately -- backend might just be offline
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, loading, error, login, register, logout, setError }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
