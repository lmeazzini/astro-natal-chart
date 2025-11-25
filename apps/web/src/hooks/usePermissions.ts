/**
 * Hook for role-based permission checks.
 *
 * Provides a simple API to check user permissions based on their role.
 *
 * Role hierarchy (lowest to highest):
 * - free: Default for new users, basic features only
 * - premium: Paying subscribers, access to premium features (e.g., horary)
 * - admin: System administrators, full access + admin panel
 */

import { useAuth } from '../contexts/AuthContext';
import type { UserRole } from '../services/auth';

interface PermissionFlags {
  /** User has free role (or no account) */
  isFree: boolean;
  /** User has premium or admin role */
  isPremium: boolean;
  /** User has admin role */
  isAdmin: boolean;
  /** User's current role (null if not authenticated) */
  role: UserRole | null;
  /** User is authenticated */
  isAuthenticated: boolean;
}

/**
 * Hook to check user permissions based on their role.
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { isPremium, isAdmin } = usePermissions();
 *
 *   return (
 *     <div>
 *       {isPremium ? <PremiumFeature /> : <PremiumUpsell />}
 *       {isAdmin && <AdminPanel />}
 *     </div>
 *   );
 * }
 * ```
 */
export function usePermissions(): PermissionFlags {
  const { user, isAuthenticated } = useAuth();

  const role = user?.role ?? null;

  return {
    isFree: role === 'free' || role === null,
    isPremium: role === 'premium' || role === 'admin',
    isAdmin: role === 'admin',
    role,
    isAuthenticated,
  };
}
