/**
 * TypeScript types for Admin Portal
 *
 * These types correspond to the backend Pydantic schemas in:
 * apps/api/app/schemas/admin.py
 */

// ============================================================================
// User Types
// ============================================================================

export type UserRole = 'free' | 'premium' | 'admin';

export interface AdminUserSummary {
  id: string;
  email: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  last_login_at: string | null;
}

export interface AdminUserList {
  total: number;
  users: AdminUserSummary[];
  skip: number;
  limit: number;
}

export interface AdminUserDetail {
  id: string;
  email: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
  is_superuser: boolean;
  email_verified: boolean;
  locale: string;
  timezone: string | null;
  avatar_url: string | null;
  bio: string | null;
  profile_public: boolean;
  created_at: string;
  updated_at: string;
  last_login_at: string | null;
  last_activity_at: string | null;
  chart_count: number;
}

// ============================================================================
// Stats Types
// ============================================================================

export interface SystemStats {
  total_users: number;
  total_charts: number;
  active_users: number;
  verified_users: number;
  users_by_role: Record<string, number>;
}

// ============================================================================
// Request/Response Types
// ============================================================================

export interface UpdateUserRoleRequest {
  role: UserRole;
}

export interface UpdateUserRoleResponse {
  message: string;
  new_role: string;
}

// ============================================================================
// Query Params Types
// ============================================================================

export interface AdminUsersParams {
  skip?: number;
  limit?: number;
  search?: string;
  role?: UserRole;
  is_active?: boolean;
}
