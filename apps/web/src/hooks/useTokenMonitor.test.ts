/**
 * Tests for useTokenMonitor hook
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useTokenMonitor } from './useTokenMonitor';
import * as api from '../services/api';

// Mock jwt-decode
vi.mock('jwt-decode', () => ({
  jwtDecode: vi.fn(),
}));

// Import after mocking
import { jwtDecode } from 'jwt-decode';

// Mock fetch
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

describe('useTokenMonitor', () => {
  const mockOnLogout = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    // Default: no token stored
    vi.spyOn(api, 'getToken').mockReturnValue(null);
    vi.spyOn(api, 'getRefreshToken').mockReturnValue(null);
    vi.spyOn(api, 'setToken').mockImplementation(() => {});
    vi.spyOn(api, 'setRefreshToken').mockImplementation(() => {});
    vi.spyOn(api, 'clearTokens').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should not do anything when disabled', () => {
    vi.spyOn(api, 'getToken').mockReturnValue('valid-token');

    renderHook(() =>
      useTokenMonitor({
        onLogout: mockOnLogout,
        enabled: false,
      })
    );

    // Advance time - should not trigger any checks
    act(() => {
      vi.advanceTimersByTime(120000);
    });

    expect(mockOnLogout).not.toHaveBeenCalled();
  });

  it('should not check when no token exists', () => {
    vi.spyOn(api, 'getToken').mockReturnValue(null);

    renderHook(() =>
      useTokenMonitor({
        onLogout: mockOnLogout,
        enabled: true,
      })
    );

    // Check should happen but not call jwtDecode since no token
    expect(jwtDecode).not.toHaveBeenCalled();
  });

  it('should check token immediately on mount', () => {
    const futureExp = Math.floor(Date.now() / 1000) + 600; // 10 min from now
    vi.spyOn(api, 'getToken').mockReturnValue('valid-token');
    vi.mocked(jwtDecode).mockReturnValue({ exp: futureExp, sub: 'user-123', iat: 0 });

    renderHook(() =>
      useTokenMonitor({
        onLogout: mockOnLogout,
        enabled: true,
      })
    );

    // Should have decoded token
    expect(jwtDecode).toHaveBeenCalledWith('valid-token');
  });

  it('should not refresh token with plenty of time remaining', () => {
    const futureExp = Math.floor(Date.now() / 1000) + 600; // 10 min from now
    vi.spyOn(api, 'getToken').mockReturnValue('valid-token');
    vi.mocked(jwtDecode).mockReturnValue({ exp: futureExp, sub: 'user-123', iat: 0 });

    renderHook(() =>
      useTokenMonitor({
        onLogout: mockOnLogout,
        enabled: true,
      })
    );

    // Should not call refresh endpoint
    expect(mockFetch).not.toHaveBeenCalled();
    expect(mockOnLogout).not.toHaveBeenCalled();
  });

  it('should check periodically at interval', async () => {
    const futureExp = Math.floor(Date.now() / 1000) + 600;
    vi.spyOn(api, 'getToken').mockReturnValue('valid-token');
    vi.mocked(jwtDecode).mockReturnValue({ exp: futureExp, sub: 'user-123', iat: 0 });

    renderHook(() =>
      useTokenMonitor({
        onLogout: mockOnLogout,
        enabled: true,
      })
    );

    // Initial check
    expect(jwtDecode).toHaveBeenCalledTimes(1);

    // Advance by check interval (60 seconds)
    act(() => {
      vi.advanceTimersByTime(60000);
    });

    // Should have checked again
    expect(jwtDecode).toHaveBeenCalledTimes(2);

    // Advance again
    act(() => {
      vi.advanceTimersByTime(60000);
    });

    expect(jwtDecode).toHaveBeenCalledTimes(3);
  });

  it('should cleanup interval on unmount', () => {
    const futureExp = Math.floor(Date.now() / 1000) + 600;
    vi.spyOn(api, 'getToken').mockReturnValue('valid-token');
    vi.mocked(jwtDecode).mockReturnValue({ exp: futureExp, sub: 'user-123', iat: 0 });

    const { unmount } = renderHook(() =>
      useTokenMonitor({
        onLogout: mockOnLogout,
        enabled: true,
      })
    );

    // Initial check
    expect(jwtDecode).toHaveBeenCalledTimes(1);

    // Unmount
    unmount();

    // Advance time - should not trigger more checks
    act(() => {
      vi.advanceTimersByTime(120000);
    });

    // Should still be 1 (no new checks after unmount)
    expect(jwtDecode).toHaveBeenCalledTimes(1);
  });

  // Async tests with real timers and longer timeout
  describe('async operations', () => {
    beforeEach(() => {
      vi.useRealTimers();
    });

    it('should proactively refresh token expiring within threshold', async () => {
      const nearExp = Math.floor(Date.now() / 1000) + 60; // 1 min from now (< 2 min threshold)
      vi.spyOn(api, 'getToken').mockReturnValue('expiring-token');
      vi.spyOn(api, 'getRefreshToken').mockReturnValue('valid-refresh-token');
      vi.mocked(jwtDecode).mockReturnValue({ exp: nearExp, sub: 'user-123', iat: 0 });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            access_token: 'new-access-token',
            refresh_token: 'new-refresh-token',
          }),
      });

      renderHook(() =>
        useTokenMonitor({
          onLogout: mockOnLogout,
          enabled: true,
        })
      );

      // Wait for async operations with waitFor
      await waitFor(
        () => {
          expect(mockFetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/v1/auth/refresh'),
            expect.objectContaining({
              method: 'POST',
            })
          );
        },
        { timeout: 2000 }
      );

      await waitFor(() => {
        expect(api.setToken).toHaveBeenCalledWith('new-access-token');
      });
      expect(mockOnLogout).not.toHaveBeenCalled();
    }, 10000);

    it('should logout when token is expired and refresh fails', async () => {
      const expiredExp = Math.floor(Date.now() / 1000) - 60; // 1 min ago
      vi.spyOn(api, 'getToken').mockReturnValue('expired-token');
      vi.spyOn(api, 'getRefreshToken').mockReturnValue('invalid-refresh');
      vi.mocked(jwtDecode).mockReturnValue({ exp: expiredExp, sub: 'user-123', iat: 0 });

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      renderHook(() =>
        useTokenMonitor({
          onLogout: mockOnLogout,
          enabled: true,
        })
      );

      // Wait for logout to be called
      await waitFor(
        () => {
          expect(mockOnLogout).toHaveBeenCalled();
        },
        { timeout: 2000 }
      );

      expect(api.clearTokens).toHaveBeenCalled();
    }, 10000);

    it('should logout on invalid token decode error', async () => {
      vi.spyOn(api, 'getToken').mockReturnValue('malformed-token');
      vi.mocked(jwtDecode).mockImplementation(() => {
        throw new Error('Invalid token');
      });

      renderHook(() =>
        useTokenMonitor({
          onLogout: mockOnLogout,
          enabled: true,
        })
      );

      // Wait for logout to be called
      await waitFor(
        () => {
          expect(mockOnLogout).toHaveBeenCalled();
        },
        { timeout: 2000 }
      );

      expect(api.clearTokens).toHaveBeenCalled();
    }, 10000);

    it('should not logout on refresh failure when token not expired', async () => {
      const nearExp = Math.floor(Date.now() / 1000) + 60; // 1 min from now
      vi.spyOn(api, 'getToken').mockReturnValue('near-expiry-token');
      vi.spyOn(api, 'getRefreshToken').mockReturnValue('refresh-token');
      vi.mocked(jwtDecode).mockReturnValue({ exp: nearExp, sub: 'user-123', iat: 0 });

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500, // Server error, not auth error
      });

      renderHook(() =>
        useTokenMonitor({
          onLogout: mockOnLogout,
          enabled: true,
        })
      );

      // Wait for fetch to be called
      await waitFor(
        () => {
          expect(mockFetch).toHaveBeenCalled();
        },
        { timeout: 2000 }
      );

      // Give time for any potential logout call
      await new Promise((r) => setTimeout(r, 200));

      // Should NOT logout on proactive refresh failure (token still valid)
      expect(mockOnLogout).not.toHaveBeenCalled();
      expect(api.clearTokens).not.toHaveBeenCalled();
    }, 10000);
  });
});
