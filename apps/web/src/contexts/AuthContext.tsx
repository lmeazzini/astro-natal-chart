/**
 * Authentication context for managing user state with automatic token refresh
 */

/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { authService, User } from '../services/auth';
import { getToken, setToken, setRefreshToken, clearTokens, authEvents } from '../services/api';
import { useLocaleSync } from '../hooks/useLocaleSync';
import { useTokenMonitor } from '../hooks/useTokenMonitor';

interface AuthContextData {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, fullName: string, password: string, passwordConfirm: string, acceptTerms?: boolean) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
  /** Refresh user data from API (e.g., after email verification in another tab) */
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Sync i18n with user's locale preference when user changes
  useLocaleSync(user);

  const logout = useCallback(() => {
    const token = getToken();

    if (token) {
      authService.logout(token).catch(console.error);
    }

    clearTokens();
    setUser(null);
  }, []);

  // Monitor token expiration and refresh proactively
  useTokenMonitor({
    onLogout: logout,
    enabled: !!user,
  });

  // Subscribe to auth events (e.g., logout triggered by API client)
  useEffect(() => {
    const unsubscribe = authEvents.subscribe(() => {
      setUser(null);
    });

    return unsubscribe;
  }, []);

  useEffect(() => {
    loadStoredUser();
  }, []);

  async function loadStoredUser() {
    try {
      const token = getToken();

      if (token) {
        const userData = await authService.getCurrentUser(token);
        setUser(userData);
      }
    } catch (error) {
      console.error('Failed to load user:', error);
      clearTokens();
    } finally {
      setIsLoading(false);
    }
  }

  async function login(email: string, password: string) {
    try {
      const tokens = await authService.login({ email, password });

      setToken(tokens.access_token);
      if (tokens.refresh_token) {
        setRefreshToken(tokens.refresh_token);
      }

      const userData = await authService.getCurrentUser(tokens.access_token);
      setUser(userData);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  async function register(
    email: string,
    fullName: string,
    password: string,
    passwordConfirm: string,
    acceptTerms?: boolean
  ) {
    try {
      await authService.register({
        email,
        full_name: fullName,
        password,
        password_confirm: passwordConfirm,
        accept_terms: acceptTerms,
      });

      // Auto-login after registration
      await login(email, password);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  /**
   * Refresh user data from API.
   * Useful when user verifies email in another tab/window.
   */
  async function refreshUser() {
    try {
      const token = getToken();
      if (token) {
        const userData = await authService.getCurrentUser(token);
        setUser(userData);
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        setUser,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
