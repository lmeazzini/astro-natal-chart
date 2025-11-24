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
}

export function useEmailVerification(): UseEmailVerificationReturn {
  const { user } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [featureName, setFeatureName] = useState<string | undefined>();

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

  return {
    isEmailVerified,
    showModal,
    setShowModal,
    requireEmailVerification,
    featureName,
  };
}
