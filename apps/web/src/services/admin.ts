/**
 * Admin portal service for administrative operations
 */

import { apiClient } from './api';
import type {
  AdminUserList,
  AdminUserDetail,
  AdminUsersParams,
  SystemStats,
  UpdateUserRoleRequest,
  UpdateUserRoleResponse,
} from '@/types/admin';

export const adminService = {
  /**
   * Get system statistics for admin dashboard
   */
  async getStats(token: string): Promise<SystemStats> {
    return apiClient.get<SystemStats>('/api/v1/admin/stats', token);
  },

  /**
   * Get paginated list of users
   */
  async getUsers(token: string, params?: AdminUsersParams): Promise<AdminUserList> {
    const searchParams = new URLSearchParams();

    if (params?.skip !== undefined) {
      searchParams.set('skip', String(params.skip));
    }
    if (params?.limit !== undefined) {
      searchParams.set('limit', String(params.limit));
    }
    if (params?.search) {
      searchParams.set('search', params.search);
    }
    if (params?.role) {
      searchParams.set('role', params.role);
    }
    if (params?.is_active !== undefined) {
      searchParams.set('is_active', String(params.is_active));
    }

    const queryString = searchParams.toString();
    const url = queryString ? `/api/v1/admin/users?${queryString}` : '/api/v1/admin/users';

    return apiClient.get<AdminUserList>(url, token);
  },

  /**
   * Get detailed user information
   */
  async getUser(userId: string, token: string): Promise<AdminUserDetail> {
    return apiClient.get<AdminUserDetail>(`/api/v1/admin/users/${userId}`, token);
  },

  /**
   * Update user role
   */
  async updateUserRole(
    userId: string,
    data: UpdateUserRoleRequest,
    token: string
  ): Promise<UpdateUserRoleResponse> {
    return apiClient.patch<UpdateUserRoleResponse>(
      `/api/v1/admin/users/${userId}/role`,
      data,
      token
    );
  },
};
