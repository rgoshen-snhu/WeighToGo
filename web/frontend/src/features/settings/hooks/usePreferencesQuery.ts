/**
 * TanStack Query hook for fetching user preferences (ADR-0014: Query = server state).
 *
 * Cache key includes the user's ID so that logging in as a different user
 * never reuses a previous user's cached preferences. Query is disabled when
 * userId is null (unauthenticated), preventing spurious 401 fetches on /login.
 */

import { useQuery } from '@tanstack/react-query';

import { preferencesClient } from '../api/preferences-client';
import { apiToPreferences, type Preferences } from '../schemas/preferences-schemas';

/** Returns a query key scoped to the authenticated user. */
export const preferencesQueryKey = (userId: number | null) => ['preferences', userId] as const;

/** Fetch and cache the authenticated user's preferences. */
export function usePreferencesQuery(userId: number | null) {
  return useQuery<Preferences>({
    queryKey: preferencesQueryKey(userId),
    queryFn: async () => {
      const raw = await preferencesClient.fetch();
      return apiToPreferences(raw);
    },
    enabled: userId !== null,
  });
}
