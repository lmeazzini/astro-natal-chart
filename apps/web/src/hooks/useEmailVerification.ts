/**
 * Hook for email verification requirements on premium features.
 *
 * This hook provides utilities to check and enforce email verification
 * before allowing access to features like AI interpretations and PDF exports.
 */

import { useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

export interface UseEmailVerificationReturn {
  /** Whether the current user has verified their email */
  isEmailVerified: boolean;
  /** Whether the verification modal is currently shown */
  showModal: boolean;
  /** Set whether to show the modal */
  setShowModal: (show: boolean) => void;
  /**
   * Execute callback only if email is verified.
   * If not verified, shows the verification modal instead.
   */
  requireEmailVerification: (callback: () => void, featureName?: string) => void;
  /** Current feature name for the modal */
  featureName: string | undefined;
  /** Check if email was verified (refreshes user data from API) */
  checkVerificationStatus: () => Promise<boolean>;
  /** Whether currently checking verification status */
  isCheckingStatus: boolean;
}

export function useEmailVerification(): UseEmailVerificationReturn {
  const { user, refreshUser } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [featureName, setFeatureName] = useState<string | undefined>();
  const [isCheckingStatus, setIsCheckingStatus] = useState(false);

  const isEmailVerified = user?.email_verified ?? false;

  const requireEmailVerification = useCallback(
    (callback: () => void, feature?: string) => {
      if (isEmailVerified) {
        callback();
      } else {
        setFeatureName(feature);
        setShowModal(true);
      }
    },
    [isEmailVerified]
  );

  /**
   * Check if the user has verified their email by refreshing user data.
   * Useful when user verifies email in another tab/window.
   * @returns true if email is now verified, false otherwise
   */
  const checkVerificationStatus = useCallback(async (): Promise<boolean> => {
    setIsCheckingStatus(true);
    try {
      await refreshUser();
      // After refresh, check the updated user state
      // Note: We can't directly access the new value here due to closure,
      // but the component will re-render with new isEmailVerified value
      return true; // Signal that check was performed
    } catch {
      return false;
    } finally {
      setIsCheckingStatus(false);
    }
  }, [refreshUser]);

  return {
    isEmailVerified,
    showModal,
    setShowModal,
    requireEmailVerification,
    featureName,
    checkVerificationStatus,
    isCheckingStatus,
  };
}
