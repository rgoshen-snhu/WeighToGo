/**
 * Authentication context for the Weigh to Go! web application.
 *
 * Provides a React context backed by TanStack Query that tracks the current
 * authenticated user via the /api/v1/auth/me endpoint. Auth state is
 * server-cache-backed with stale-while-revalidate semantics.
 *
 * SRS §10.4 governs the auth-state management strategy.
 */

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { createContext, useCallback, useContext, useMemo, type ReactNode } from 'react';
import { authClient, type AuthUser } from '../features/auth/api/auth-client';

/** Query key for the authenticated-user cache entry. */
export const AUTH_QUERY_KEY = ['auth', 'me'] as const;

export interface AuthContextValue {
  /** The currently authenticated user, or null when no session exists. */
  user: AuthUser | null;
  /** Derived convenience flag — true when user is non-null. */
  isAuthenticated: boolean;
  /** True while the initial /me request is in-flight. */
  isLoading: boolean;
  /**
   * Write a user directly into the cache. Used by login / register flows to
   * update auth state without a round-trip to /me.
   */
  setUser: (user: AuthUser) => void;
  /**
   * Remove the cached user. Called after logout or session expiry so that all
   * consumers see an unauthenticated state immediately.
   */
  clearAuth: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * Wrap the component tree that needs access to auth state.
 *
 * Must be rendered inside a QueryClientProvider.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();

  const query = useQuery<AuthUser | null>({
    queryKey: AUTH_QUERY_KEY,
    queryFn: async () => {
      try {
        return await authClient.me();
      } catch {
        // Treat any error (including 401) as unauthenticated rather than an
        // error state — the user simply has no active session.
        return null;
      }
    },
    staleTime: 30_000,
    retry: false,
  });

  const setUser = useCallback(
    (u: AuthUser) => {
      queryClient.setQueryData<AuthUser | null>(AUTH_QUERY_KEY, u);
    },
    [queryClient],
  );

  const clearAuth = useCallback(() => {
    queryClient.setQueryData<AuthUser | null>(AUTH_QUERY_KEY, null);
    // Remove all user-scoped preference caches so the next authenticated user
    // does not see the previous user's preferences (P2-1 fix).
    queryClient.removeQueries({ queryKey: ['preferences'] });
  }, [queryClient]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user: query.data ?? null,
      isAuthenticated: !!query.data,
      isLoading: query.isLoading,
      setUser,
      clearAuth,
    }),
    [query.data, query.isLoading, setUser, clearAuth],
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
