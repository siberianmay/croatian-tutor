import React, { createContext, useContext, useState, useCallback, useMemo, useEffect } from 'react';
import api from '~services/api';
import type { AuthUser, AuthToken, LoginRequest, RegisterRequest } from '~types';

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token and fetch user on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem(ACCESS_TOKEN_KEY);
      if (token) {
        try {
          const response = await api.get<AuthUser>('/auth/me');
          setUser(response.data);
        } catch {
          // Token invalid, clear storage
          localStorage.removeItem(ACCESS_TOKEN_KEY);
          localStorage.removeItem(REFRESH_TOKEN_KEY);
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = useCallback(async (credentials: LoginRequest) => {
    const response = await api.post<AuthToken>('/auth/login', credentials);
    const { access_token, refresh_token } = response.data;

    localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);

    // Fetch user data
    const userResponse = await api.get<AuthUser>('/auth/me');
    setUser(userResponse.data);
  }, []);

  const register = useCallback(async (data: RegisterRequest) => {
    const response = await api.post<AuthToken>('/auth/register', data);
    const { access_token, refresh_token } = response.data;

    localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);

    // Fetch user data
    const userResponse = await api.get<AuthUser>('/auth/me');
    setUser(userResponse.data);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
  }), [user, isLoading, login, register, logout]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
