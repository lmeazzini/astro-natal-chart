/**
 * Hook for proactive token refresh monitoring
 *
 * This hook runs in the background and checks if the access token is
 * about to expire. If so, it proactively refreshes the token before
 * it expires, ensuring a seamless user experience.
 */

import { useEffect, useCallback, useRef } from 'react';
import { jwtDecode } from 'jwt-decode';
import { getToken, setToken, getRefreshToken, setRefreshToken, clearTokens } from '../services/api';

// Check token every 60 seconds
const CHECK_INTERVAL = 60000;

// Refresh token if it expires in less than 2 minutes
const REFRESH_THRESHOLD = 120;

interface JWTPayload {
  exp: number;
  sub: string;
  iat: number;
}

interface UseTokenMonitorOptions {
  onLogout: () => void;
  enabled?: boolean;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Proactively monitor and refresh the access token before expiration
 */
export function useTokenMonitor({ onLogout, enabled = true }: UseTokenMonitorOptions): void {
  const intervalRef = useRef<number | null>(null);
  const isRefreshingRef = useRef(false);

  const refreshToken = useCallback(async (): Promise<boolean> => {
    const refresh = getRefreshToken();

    if (!refresh) {
      return false;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refresh }),
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json();

      if (data.access_token) {
        setToken(data.access_token);
        if (data.refresh_token) {
          setRefreshToken(data.refresh_token);
        }
        console.log('Token refreshed proactively by monitor');
        return true;
      }

      return false;
    } catch (error) {
      console.error('Proactive token refresh failed:', error);
      return false;
    }
  }, []);

  const checkToken = useCallback(async () => {
    // Skip if already refreshing
    if (isRefreshingRef.current) {
      return;
    }

    const token = getToken();

    if (!token) {
      return;
    }

    try {
      // Decode JWT to check expiration
      const decoded = jwtDecode<JWTPayload>(token);
      const now = Date.now() / 1000;
      const timeUntilExpiry = decoded.exp - now;

      // If token is expired or invalid
      if (timeUntilExpiry <= 0) {
        console.log('Token expired, attempting refresh');
        isRefreshingRef.current = true;

        const success = await refreshToken();

        if (!success) {
          clearTokens();
          onLogout();
        }

        isRefreshingRef.current = false;
        return;
      }

      // If token expires in less than threshold, refresh it proactively
      if (timeUntilExpiry < REFRESH_THRESHOLD) {
        console.log(`Token expires in ${Math.round(timeUntilExpiry)}s, refreshing proactively`);
        isRefreshingRef.current = true;

        const success = await refreshToken();

        if (!success) {
          // Don't logout immediately - let the normal flow handle it
          console.warn('Proactive refresh failed, will retry on next check');
        }

        isRefreshingRef.current = false;
      }
    } catch (error) {
      // Invalid token format - likely corrupted
      console.error('Token decode error:', error);
      clearTokens();
      onLogout();
    }
  }, [onLogout, refreshToken]);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    // Check immediately on mount
    checkToken();

    // Set up interval for periodic checks
    intervalRef.current = window.setInterval(checkToken, CHECK_INTERVAL);

    return () => {
      if (intervalRef.current !== null) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [checkToken, enabled]);
}
