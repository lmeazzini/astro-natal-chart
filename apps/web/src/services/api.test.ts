/**
 * Tests for API client with automatic token refresh
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  getToken,
  setToken,
  getRefreshToken,
  setRefreshToken,
  clearTokens,
  authEvents,
  apiClient,
} from './api';

// Mock fetch globally
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

// Mock i18n
vi.mock('../i18n', () => ({
  default: {
    language: 'en',
  },
}));

describe('Token Management Utilities', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('getToken / setToken', () => {
    it('should return null when no token stored', () => {
      expect(getToken()).toBeNull();
    });

    it('should store and retrieve token', () => {
      setToken('test-token');
      expect(getToken()).toBe('test-token');
    });

    it('should use correct storage key', () => {
      setToken('my-token');
      expect(localStorage.getItem('astro_access_token')).toBe('my-token');
    });
  });

  describe('getRefreshToken / setRefreshToken', () => {
    it('should return null when no refresh token stored', () => {
      expect(getRefreshToken()).toBeNull();
    });

    it('should store and retrieve refresh token', () => {
      setRefreshToken('test-refresh-token');
      expect(getRefreshToken()).toBe('test-refresh-token');
    });

    it('should use correct storage key', () => {
      setRefreshToken('my-refresh');
      expect(localStorage.getItem('astro_refresh_token')).toBe('my-refresh');
    });
  });

  describe('clearTokens', () => {
    it('should clear both tokens', () => {
      setToken('access');
      setRefreshToken('refresh');

      clearTokens();

      expect(getToken()).toBeNull();
      expect(getRefreshToken()).toBeNull();
    });
  });
});

describe('authEvents', () => {
  it('should allow subscribing to logout events', () => {
    const callback = vi.fn();

    authEvents.subscribe(callback);
    authEvents.notifyLogout();

    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('should allow unsubscribing', () => {
    const callback = vi.fn();

    const unsubscribe = authEvents.subscribe(callback);
    unsubscribe();
    authEvents.notifyLogout();

    expect(callback).not.toHaveBeenCalled();
  });

  it('should notify multiple subscribers', () => {
    const callback1 = vi.fn();
    const callback2 = vi.fn();

    authEvents.subscribe(callback1);
    authEvents.subscribe(callback2);
    authEvents.notifyLogout();

    expect(callback1).toHaveBeenCalled();
    expect(callback2).toHaveBeenCalled();
  });

  afterEach(() => {
    // Clear listeners
    authEvents.listeners.clear();
  });
});

describe('ApiClient', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    authEvents.listeners.clear();
  });

  describe('Basic Requests', () => {
    it('should make GET request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: () => Promise.resolve({ data: 'test' }),
      });

      const result = await apiClient.get('/test');

      expect(result).toEqual({ data: 'test' });
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({ method: 'GET' })
      );
    });

    it('should make POST request with body', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: () => Promise.resolve({ success: true }),
      });

      const result = await apiClient.post('/test', { name: 'test' });

      expect(result).toEqual({ success: true });
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ name: 'test' }),
        })
      );
    });

    it('should include Authorization header when token exists', async () => {
      setToken('my-access-token');

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: () => Promise.resolve({}),
      });

      await apiClient.get('/protected');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer my-access-token',
          }),
        })
      );
    });

    it('should handle 204 No Content', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
        headers: new Headers(),
      });

      const result = await apiClient.delete('/item/123');

      expect(result).toBeUndefined();
    });
  });

  describe('Auto-Refresh from Header', () => {
    it('should update token when X-New-Access-Token header present', async () => {
      setToken('old-token');

      const headers = new Headers();
      headers.set('X-New-Access-Token', 'new-token-from-middleware');

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers,
        json: () => Promise.resolve({ data: 'test' }),
      });

      await apiClient.get('/test');

      expect(getToken()).toBe('new-token-from-middleware');
    });

    it('should not change token when header absent', async () => {
      setToken('original-token');

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: () => Promise.resolve({ data: 'test' }),
      });

      await apiClient.get('/test');

      expect(getToken()).toBe('original-token');
    });
  });

  describe('401 Handling and Token Refresh', () => {
    it('should attempt refresh on 401 response', async () => {
      setToken('expired-token');
      setRefreshToken('valid-refresh');

      // First call returns 401
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        headers: new Headers(),
        json: () => Promise.resolve({ detail: 'Token expired' }),
      });

      // Refresh call succeeds
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: () =>
          Promise.resolve({
            access_token: 'new-access-token',
            refresh_token: 'new-refresh-token',
          }),
      });

      // Retry succeeds
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: () => Promise.resolve({ data: 'success' }),
      });

      const result = await apiClient.get('/protected');

      expect(result).toEqual({ data: 'success' });
      expect(getToken()).toBe('new-access-token');
      expect(getRefreshToken()).toBe('new-refresh-token');
    });

    it('should logout when refresh fails', async () => {
      setToken('expired-token');
      setRefreshToken('invalid-refresh');

      const logoutCallback = vi.fn();
      authEvents.subscribe(logoutCallback);

      // First call returns 401
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        headers: new Headers(),
        json: () => Promise.resolve({ detail: 'Token expired' }),
      });

      // Refresh call fails
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        headers: new Headers(),
        json: () => Promise.resolve({ detail: 'Invalid refresh token' }),
      });

      await expect(apiClient.get('/protected')).rejects.toThrow();

      expect(getToken()).toBeNull();
      expect(getRefreshToken()).toBeNull();
      expect(logoutCallback).toHaveBeenCalled();
    });

    it('should not attempt refresh when no token exists', async () => {
      // No token set

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        headers: new Headers(),
        json: () => Promise.resolve({ detail: 'Not authenticated' }),
      });

      await expect(apiClient.get('/protected')).rejects.toThrow();

      // Should only have made one call (no refresh attempt)
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    it('should not attempt refresh when no refresh token exists', async () => {
      setToken('expired-token');
      // No refresh token

      const logoutCallback = vi.fn();
      authEvents.subscribe(logoutCallback);

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        headers: new Headers(),
        json: () => Promise.resolve({ detail: 'Token expired' }),
      });

      await expect(apiClient.get('/protected')).rejects.toThrow();

      expect(logoutCallback).toHaveBeenCalled();
    });

    it('should queue concurrent requests during refresh', async () => {
      setToken('expired-token');
      setRefreshToken('valid-refresh');

      // First call returns 401
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        headers: new Headers(),
        json: () => Promise.resolve({ detail: 'Token expired' }),
      });

      // Refresh succeeds
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: () =>
          Promise.resolve({
            access_token: 'new-token',
            refresh_token: 'new-refresh',
          }),
      });

      // Retry succeeds
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: () => Promise.resolve({ data: 'success' }),
      });

      // Make request that triggers refresh
      const result = await apiClient.get('/resource');

      expect(result).toEqual({ data: 'success' });

      // Verify refresh was called
      const refreshCalls = mockFetch.mock.calls.filter((call) => call[0].includes('/auth/refresh'));
      expect(refreshCalls.length).toBe(1);
    });
  });

  describe('Error Handling', () => {
    it('should throw error with detail message', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        headers: new Headers(),
        json: () => Promise.resolve({ detail: 'Bad request' }),
      });

      await expect(apiClient.post('/test')).rejects.toThrow('Bad request');
    });

    it('should handle validation error array', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        headers: new Headers(),
        json: () =>
          Promise.resolve({
            detail: [{ msg: 'Field required', type: 'missing' }],
          }),
      });

      await expect(apiClient.post('/test')).rejects.toThrow('Field required');
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiClient.get('/test')).rejects.toThrow('Network error');
    });
  });

  describe('HTTP Methods', () => {
    it('should make PUT request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: () => Promise.resolve({ updated: true }),
      });

      await apiClient.put('/item/1', { name: 'updated' });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/item/1'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ name: 'updated' }),
        })
      );
    });

    it('should make PATCH request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: () => Promise.resolve({ patched: true }),
      });

      await apiClient.patch('/item/1', { field: 'value' });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/item/1'),
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify({ field: 'value' }),
        })
      );
    });

    it('should make DELETE request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: () => Promise.resolve({ deleted: true }),
      });

      await apiClient.delete('/item/1');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/item/1'),
        expect.objectContaining({ method: 'DELETE' })
      );
    });
  });
});
