/**
 * TanStack Query mutation hook for updating a single preference.
 *
 * Optimistic update: immediately reflects the new value in the Query cache.
 * On error: rolls back to the snapshot taken before the mutation started.
 *
 * The cache key is user-scoped (resolved from the auth cache at call time)
 * so mutations never touch another user's cached preferences.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';

import { AUTH_QUERY_KEY } from '../../../contexts/AuthContext';
import type { AuthUser } from '../../auth/api/auth-client';
import { preferencesClient } from '../api/preferences-client';
import { apiToPreferences, type Preferences } from '../schemas/preferences-schemas';
import { preferencesQueryKey } from './usePreferencesQuery';

interface UpdatePreferenceVariables {
  key: keyof Preferences extends infer K
    ? K extends string
      ? 'weight_unit' | 'notify_achievement' | 'notify_milestone' | 'notify_streak'
      : never
    : never;
  value: boolean | string;
}

/** Mutate one preference. Optimistic update with rollback on error. */
export function useUpdatePreference() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ key, value }: UpdatePreferenceVariables) => preferencesClient.update(key, value),

    onMutate: async ({ key, value }: UpdatePreferenceVariables) => {
      const userId = queryClient.getQueryData<AuthUser | null>(AUTH_QUERY_KEY)?.user_id ?? null;
      const qKey = preferencesQueryKey(userId);

      await queryClient.cancelQueries({ queryKey: qKey });
      const snapshot = queryClient.getQueryData<Preferences>(qKey);

      const camelKey = key.replace(/_([a-z])/g, (_, c: string) =>
        c.toUpperCase(),
      ) as keyof Preferences;
      queryClient.setQueryData<Preferences>(qKey, (prev) =>
        prev ? { ...prev, [camelKey]: value } : prev,
      );

      return { snapshot, qKey };
    },

    onError: (_err, _vars, context) => {
      // context is always defined when onMutate returns; restore snapshot.
      if (context) queryClient.setQueryData(context.qKey, context.snapshot);
    },

    onSuccess: (raw, _vars, context) => {
      // context is always defined when onMutate returns; update cache.
      if (context) queryClient.setQueryData(context.qKey, apiToPreferences(raw));
    },
  });
}
