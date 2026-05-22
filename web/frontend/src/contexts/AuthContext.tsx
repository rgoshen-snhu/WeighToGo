/**
 * Authentication context for the Weigh to Go! web application.
 *
 * Provides a React context that tracks the current authenticated user and
 * exposes login / logout functions. Phase 6 will connect these to the API;
 * for now the state is in-memory only.
 *
 * SRS §10.4 governs the auth-state management strategy.
 */

import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';

/**
 * Minimal representation of an authenticated user.
 *
 * The full user object (profile fields, preferences) is deferred to Phase 6
 * when the API contracts are finalised.
 */
export interface User {
  id: string;
  email: string;
  displayName: string;
}

export interface AuthContextValue {
  /** The currently authenticated user, or null when no session exists. */
  user: User | null;
  /** Derived convenience flag — true when user is non-null. */
  isAuthenticated: boolean;
  /**
   * Record a successful login. Accepts the user object returned by the API.
   * Phase 6 will call this after a successful credentials exchange.
   */
  login: (user: User) => void;
  /**
   * Clear the session. Phase 6 will also call the backend /auth/logout
   * endpoint before clearing local state.
   */
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * Wrap the component tree that needs access to auth state.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = useCallback((newUser: User) => {
    setUser(newUser);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      login,
      logout,
    }),
    [user, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Access auth state and actions from any component inside AuthProvider.
 *
 * @throws {Error} When called outside an AuthProvider.
 */
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (ctx === undefined) {
    throw new Error('useAuth must be used inside an AuthProvider');
  }
  return ctx;
}
