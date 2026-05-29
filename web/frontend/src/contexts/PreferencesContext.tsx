/**
 * User preferences context for the Weigh to Go! web application.
 *
 * Backed by TanStack Query (ADR-0014: Query = server state).
 * Falls back to DEFAULT_PREFERENCES while the initial fetch is in flight.
 * Query is scoped to the authenticated user — prevents /login from firing
 * an unauthenticated fetch and prevents stale data after user switching.
 * colorScheme (FR-P-2 / theme) is deferred to the Final enhancement.
 *
 * SRS §10.4 governs the preferences management strategy.
 */

import { createContext, useContext, useMemo, type ReactNode } from 'react';

import { useAuth } from './AuthContext';
import { usePreferencesQuery } from '../features/settings/hooks/usePreferencesQuery';
import { useUpdatePreference } from '../features/settings/hooks/useUpdatePreference';
import {
  DEFAULT_PREFERENCES,
  type Preferences,
} from '../features/settings/schemas/preferences-schemas';

export type { Preferences };

export interface PreferencesContextValue {
  preferences: Preferences;
  /** Whether the initial preferences fetch is in flight. */
  isLoading: boolean;
  /**
   * Update a single preference key.
   * Optimistic — immediately reflects the new value; rolls back on error.
   *
   * @param key   - The snake_case API key (e.g. 'weight_unit').
   * @param value - The new value (boolean or string).
   */
  setPreference: (key: string, value: boolean | string) => void;
}

const PreferencesContext = createContext<PreferencesContextValue | undefined>(undefined);

/**
 * Wrap the component tree that needs access to user preferences.
 * Requires QueryClientProvider and AuthProvider ancestors.
 */
export function PreferencesProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const query = usePreferencesQuery(user?.user_id ?? null);
  const mutation = useUpdatePreference();

  const setPreference = useMemo(
    () => (key: string, value: boolean | string) => {
      mutation.mutate({ key: key as Parameters<typeof mutation.mutate>[0]['key'], value });
    },
    [mutation],
  );

  const value = useMemo<PreferencesContextValue>(
    () => ({
      preferences: query.data ?? DEFAULT_PREFERENCES,
      isLoading: query.isLoading,
      setPreference,
    }),
    [query.data, query.isLoading, setPreference],
  );

  return <PreferencesContext.Provider value={value}>{children}</PreferencesContext.Provider>;
}

/**
 * Access user preferences from any component inside PreferencesProvider.
 *
 * @throws {Error} When called outside a PreferencesProvider.
 */
export function usePreferences(): PreferencesContextValue {
  const ctx = useContext(PreferencesContext);
  if (ctx === undefined) {
    throw new Error('usePreferences must be used inside a PreferencesProvider');
  }
  return ctx;
}
