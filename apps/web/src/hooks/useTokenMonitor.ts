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

// Exponential backoff configuration
const INITIAL_BACKOFF_MS = 1000; // 1 second
const MAX_BACKOFF_MS = 60000; // 1 minute
const MAX_RETRIES = 5;

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
  const failedAttemptsRef = useRef(0);
  const backoffTimeoutRef = useRef<number | null>(null);

  /**
   * Calculate backoff delay with exponential increase
   */
  const getBackoffDelay = useCallback((attempts: number): number => {
    const delay = INITIAL_BACKOFF_MS * Math.pow(2, attempts);
    return Math.min(delay, MAX_BACKOFF_MS);
  }, []);

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
        // Reset failed attempts on success
        failedAttemptsRef.current = 0;
        console.log('[Auth] Token refreshed proactively by background monitor');
        return true;
      }

      return false;
    } catch (error) {
      console.error('[Auth] Proactive token refresh failed:', error);
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
        console.log('[Auth] Token expired, attempting refresh');
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
        console.log(
          `[Auth] Token expires in ${Math.round(timeUntilExpiry)}s, refreshing proactively`
        );
        isRefreshingRef.current = true;

        const success = await refreshToken();

        if (!success) {
          failedAttemptsRef.current++;

          if (failedAttemptsRef.current >= MAX_RETRIES) {
            console.error(`[Auth] Proactive refresh failed after ${MAX_RETRIES} attempts`);
            // Don't logout on proactive failures - let the API client handle it
          } else {
            const backoffDelay = getBackoffDelay(failedAttemptsRef.current);
            console.warn(
              `[Auth] Proactive refresh failed (attempt ${failedAttemptsRef.current}/${MAX_RETRIES}), ` +
                `will retry in ${backoffDelay / 1000}s`
            );

            // Schedule a retry with backoff
            if (backoffTimeoutRef.current) {
              clearTimeout(backoffTimeoutRef.current);
            }
            backoffTimeoutRef.current = window.setTimeout(() => {
              backoffTimeoutRef.current = null;
              checkToken();
            }, backoffDelay);
          }
        } else {
          // Reset on success
          failedAttemptsRef.current = 0;
        }

        isRefreshingRef.current = false;
      }
    } catch (error) {
      // Invalid token format - likely corrupted
      console.error('[Auth] Token decode error:', error);
      clearTokens();
      onLogout();
    }
  }, [onLogout, refreshToken, getBackoffDelay]);

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
      if (backoffTimeoutRef.current !== null) {
        clearTimeout(backoffTimeoutRef.current);
        backoffTimeoutRef.current = null;
      }
    };
  }, [checkToken, enabled]);
}
