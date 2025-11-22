/**
 * Authentication service
 */

import { apiClient } from './api';

export interface RegisterData {
  email: string;
  full_name: string;
  password: string;
  password_confirm: string;
  accept_terms?: boolean;
}

export interface LoginData {
  email: string;
  password: string;
}

export type UserType = 'professional' | 'student' | 'curious';

export interface User {
  id: string;
  email: string;
  full_name: string;
  locale: string;
  timezone: string | null;
  avatar_url: string | null;
  email_verified: boolean;
  is_active: boolean;
  is_superuser: boolean;
  bio: string | null;
  profile_public: boolean;
  user_type: UserType;
  // Social links
  website: string | null;
  instagram: string | null;
  twitter: string | null;
  // Professional info
  location: string | null;
  professional_since: number | null;
  specializations: string[] | null;
  // Settings
  allow_email_notifications: boolean;
  analytics_consent: boolean;
  last_login_at: string | null;
  last_activity_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string | null;
  token_type: string;
}

export const authService = {
  /**
   * Register a new user
   */
  async register(data: RegisterData): Promise<User> {
    return apiClient.post<User>('/api/v1/auth/register', data);
  },

  /**
   * Login with email and password
   */
  async login(data: LoginData): Promise<AuthTokens> {
    return apiClient.post<AuthTokens>('/api/v1/auth/login', data);
  },

  /**
   * Get current user information
   */
  async getCurrentUser(token: string): Promise<User> {
    return apiClient.get<User>('/api/v1/auth/me', token);
  },

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    return apiClient.post<AuthTokens>('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
  },

  /**
   * Logout user
   */
  async logout(token: string): Promise<void> {
    return apiClient.post<void>('/api/v1/auth/logout', undefined, token);
  },
};
