/**
 * Credits context for managing user credit state
 */

/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { useAuth } from './AuthContext';
import { getCredits, type UserCreditsResponse } from '@/services/credits';

interface CreditsContextType {
  credits: UserCreditsResponse | null;
  isLoading: boolean;
  error: string | null;
  refreshCredits: () => Promise<void>;
  hasCredits: (amount: number) => boolean;
}

const CreditsContext = createContext<CreditsContextType | undefined>(undefined);

export function CreditsProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [credits, setCredits] = useState<UserCreditsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshCredits = useCallback(async () => {
    if (!isAuthenticated) {
      setCredits(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await getCredits();
      setCredits(data);
    } catch (err) {
      console.error('Failed to fetch credits:', err);
      setError('Failed to load credits');
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // Load credits when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      refreshCredits();
    } else {
      setCredits(null);
    }
  }, [isAuthenticated, refreshCredits]);

  const hasCredits = useCallback(
    (amount: number): boolean => {
      if (!credits) return false;
      if (credits.is_unlimited) return true;
      return credits.credits_balance >= amount;
    },
    [credits]
  );

  const value = useMemo(
    () => ({
      credits,
      isLoading,
      error,
      refreshCredits,
      hasCredits,
    }),
    [credits, isLoading, error, refreshCredits, hasCredits]
  );

  return <CreditsContext.Provider value={value}>{children}</CreditsContext.Provider>;
}

export function useCredits(): CreditsContextType {
  const context = useContext(CreditsContext);
  if (context === undefined) {
    throw new Error('useCredits must be used within a CreditsProvider');
  }
  return context;
}
