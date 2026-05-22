/**
 * User preferences context for the Weigh to Go! web application.
 *
 * Tracks display preferences (weight unit and colour scheme). Phase 6 will
 * persist these to localStorage and sync them with the user's API profile.
 *
 * SRS §10.4 governs the preferences management strategy.
 */

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

export interface Preferences {
  /**
   * Unit used for weight display and entry throughout the application.
   * Defaults to 'lbs' per the SRS default locale assumption.
   */
  weightUnit: 'lbs' | 'kg';
  /**
   * UI colour scheme preference.
   * Defaults to 'light'; dark mode is implemented in Phase 7.
   */
  colorScheme: 'light' | 'dark';
}

export interface PreferencesContextValue {
  preferences: Preferences;
  /**
   * Merge a partial preferences object into the current state.
   * Fields not included in the update are preserved unchanged.
   */
  setPreferences: (partial: Partial<Preferences>) => void;
}

const DEFAULT_PREFERENCES: Preferences = {
  weightUnit: 'lbs',
  colorScheme: 'light',
};

const PreferencesContext = createContext<PreferencesContextValue | undefined>(
  undefined,
);

/**
 * Wrap the component tree that needs access to user preferences.
 */
export function PreferencesProvider({ children }: { children: ReactNode }) {
  const [preferences, setPreferencesState] =
    useState<Preferences>(DEFAULT_PREFERENCES);

  const setPreferences = useCallback((partial: Partial<Preferences>) => {
    setPreferencesState((prev) => ({ ...prev, ...partial }));
  }, []);

  const value = useMemo<PreferencesContextValue>(
    () => ({ preferences, setPreferences }),
    [preferences, setPreferences],
  );

  return (
    <PreferencesContext.Provider value={value}>
      {children}
    </PreferencesContext.Provider>
  );
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
