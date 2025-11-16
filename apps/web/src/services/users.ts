/**
 * User profile and account management service
 */

import { apiClient } from './api';
import type { User } from './auth';

export interface UserUpdate {
  full_name?: string;
  locale?: string;
  timezone?: string;
  avatar_url?: string;
  bio?: string;
  profile_public?: boolean;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}

export interface UserStats {
  total_charts: number;
  account_age_days: number;
  last_login_at: string | null;
  last_activity_at: string | null;
}

export interface UserActivity {
  id: string;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  ip_address: string | null;
  created_at: string;
}

export interface UserActivityList {
  activities: UserActivity[];
  total: number;
}

export interface OAuthConnection {
  provider: string;
  provider_user_id: string;
  connected_at: string;
}

export interface UserDataExport {
  user: User;
  birth_charts: unknown[];
  oauth_connections: OAuthConnection[];
  activity_log: UserActivity[];
}

export const userService = {
  /**
   * Update user profile
   */
  async updateProfile(data: UserUpdate, token: string): Promise<User> {
    return apiClient.put<User>('/api/v1/users/me', data, token);
  },

  /**
   * Change user password
   */
  async changePassword(data: PasswordChange, token: string): Promise<void> {
    return apiClient.put('/api/v1/users/me/password', data, token);
  },

  /**
   * Get user statistics
   */
  async getStats(token: string): Promise<UserStats> {
    return apiClient.get<UserStats>('/api/v1/users/me/stats', token);
  },

  /**
   * Get user activity log
   */
  async getActivity(
    token: string,
    limit = 50,
    offset = 0
  ): Promise<UserActivityList> {
    return apiClient.get<UserActivityList>(
      `/api/v1/users/me/activity?limit=${limit}&offset=${offset}`,
      token
    );
  },

  /**
   * Export all user data (LGPD/GDPR)
   */
  async exportData(token: string): Promise<UserDataExport> {
    return apiClient.get<UserDataExport>('/api/v1/users/me/export', token);
  },

  /**
   * Soft delete user account
   */
  async deleteAccount(token: string): Promise<void> {
    return apiClient.delete('/api/v1/users/me', token);
  },

  /**
   * Get OAuth connections
   */
  async getOAuthConnections(token: string): Promise<OAuthConnection[]> {
    return apiClient.get<OAuthConnection[]>(
      '/api/v1/users/me/oauth-connections',
      token
    );
  },

  /**
   * Disconnect OAuth provider
   */
  async disconnectOAuth(provider: string, token: string): Promise<void> {
    return apiClient.delete(
      `/api/v1/users/me/oauth-connections/${provider}`,
      token
    );
  },
};
