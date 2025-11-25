/**
 * Tests for usePermissions hook
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { usePermissions } from './usePermissions';
import type { User } from '../services/auth';

// Mock useAuth hook
vi.mock('../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}));

import { useAuth } from '../contexts/AuthContext';

// Helper to create a mock user with all required fields
const createMockUser = (overrides: Partial<User> = {}): User => ({
  id: 'user-1',
  email: 'test@example.com',
  full_name: 'Test User',
  locale: 'en-US',
  timezone: null,
  avatar_url: null,
  email_verified: true,
  is_active: true,
  is_superuser: false,
  role: 'free',
  bio: null,
  profile_public: false,
  user_type: 'curious',
  website: null,
  instagram: null,
  twitter: null,
  location: null,
  professional_since: null,
  specializations: null,
  allow_email_notifications: true,
  analytics_consent: true,
  last_login_at: null,
  last_activity_at: null,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides,
});

// Helper to create mock auth context
const createMockAuthContext = (user: User | null, isAuthenticated: boolean) => ({
  user,
  isAuthenticated,
  login: vi.fn(),
  logout: vi.fn(),
  register: vi.fn(),
  isLoading: false,
  refreshUser: vi.fn(),
  setUser: vi.fn(),
});

describe('usePermissions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('when user is not authenticated', () => {
    beforeEach(() => {
      vi.mocked(useAuth).mockReturnValue(createMockAuthContext(null, false));
    });

    it('should return isFree as true', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isFree).toBe(true);
    });

    it('should return isPremium as false', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isPremium).toBe(false);
    });

    it('should return isAdmin as false', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isAdmin).toBe(false);
    });

    it('should return role as null', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.role).toBeNull();
    });

    it('should return isAuthenticated as false', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('when user has FREE role', () => {
    beforeEach(() => {
      const user = createMockUser({ role: 'free' });
      vi.mocked(useAuth).mockReturnValue(createMockAuthContext(user, true));
    });

    it('should return isFree as true', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isFree).toBe(true);
    });

    it('should return isPremium as false', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isPremium).toBe(false);
    });

    it('should return isAdmin as false', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isAdmin).toBe(false);
    });

    it('should return role as "free"', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.role).toBe('free');
    });

    it('should return isAuthenticated as true', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isAuthenticated).toBe(true);
    });
  });

  describe('when user has PREMIUM role', () => {
    beforeEach(() => {
      const user = createMockUser({
        email: 'premium@example.com',
        full_name: 'Premium User',
        role: 'premium',
      });
      vi.mocked(useAuth).mockReturnValue(createMockAuthContext(user, true));
    });

    it('should return isFree as false', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isFree).toBe(false);
    });

    it('should return isPremium as true', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isPremium).toBe(true);
    });

    it('should return isAdmin as false', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isAdmin).toBe(false);
    });

    it('should return role as "premium"', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.role).toBe('premium');
    });

    it('should return isAuthenticated as true', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isAuthenticated).toBe(true);
    });
  });

  describe('when user has ADMIN role', () => {
    beforeEach(() => {
      const user = createMockUser({
        email: 'admin@realastrology.ai',
        full_name: 'Admin User',
        role: 'admin',
        is_superuser: true,
      });
      vi.mocked(useAuth).mockReturnValue(createMockAuthContext(user, true));
    });

    it('should return isFree as false', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isFree).toBe(false);
    });

    it('should return isPremium as true (admin has premium access)', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isPremium).toBe(true);
    });

    it('should return isAdmin as true', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isAdmin).toBe(true);
    });

    it('should return role as "admin"', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.role).toBe('admin');
    });

    it('should return isAuthenticated as true', () => {
      const { result } = renderHook(() => usePermissions());
      expect(result.current.isAuthenticated).toBe(true);
    });
  });
});
