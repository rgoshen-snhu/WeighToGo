import { useInfiniteQuery } from '@tanstack/react-query';
import { weightClient } from '../api/weight-client';
import type { WeightEntryListResponse } from '../api/weight-client';

export const WEIGHT_ENTRIES_KEY = ['weight-entries'] as const;

/**
 * Return all loaded pages of weight entries for the current user.
 *
 * Uses TanStack Query's `useInfiniteQuery` so the page can render every
 * loaded page and request the next one by passing the previously returned
 * opaque `next_cursor` (ADR-0015).
 */
export function useWeightEntries(params?: { limit?: number }) {
  return useInfiniteQuery<WeightEntryListResponse>({
    queryKey: [...WEIGHT_ENTRIES_KEY, params],
    queryFn: ({ pageParam }) =>
      weightClient.list({
        limit: params?.limit,
        cursor: pageParam as string | undefined,
      }),
    initialPageParam: undefined,
    getNextPageParam: (lastPage) => lastPage.next_cursor ?? undefined,
  });
}
