/**
 * Tests for useUpdatePreference — mutation with optimistic update + rollback.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, renderHook, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { describe, expect, it, vi } from 'vitest';

import { AUTH_QUERY_KEY } from '../../../contexts/AuthContext';
import type { Preferences } from '../schemas/preferences-schemas';
import { preferencesQueryKey } from './usePreferencesQuery';
import { useUpdatePreference } from './useUpdatePreference';

const mockUpdate = vi.fn();

vi.mock('../api/preferences-client', () => ({
  preferencesClient: {
    update: (...args: unknown[]) => mockUpdate(...args),
  },
}));

const USER_ID = 1;

const seedPrefs: Preferences = {
  weightUnit: 'lbs',
  notifyAchievement: true,
  notifyMilestone: true,
  notifyStreak: false,
};

function wrapper({ children }: { children: ReactNode }) {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  // Seed auth so the mutation can resolve the user-scoped preferences key.
  qc.setQueryData(AUTH_QUERY_KEY, { user_id: USER_ID });
  qc.setQueryData(preferencesQueryKey(USER_ID), seedPrefs);
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}

describe('useUpdatePreference', () => {
  it('calls preferencesClient.update with key and value', async () => {
    mockUpdate.mockResolvedValue({
      weight_unit: 'kg',
      notify_achievement: true,
      notify_milestone: true,
      notify_streak: false,
    });

    const { result } = renderHook(() => useUpdatePreference(), { wrapper });
    act(() => {
      result.current.mutate({ key: 'weight_unit', value: 'kg' });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockUpdate).toHaveBeenCalledWith('weight_unit', 'kg');
  });

  it('rolls back optimistic update on error', async () => {
    mockUpdate.mockRejectedValue(new Error('Network failure'));

    const { result } = renderHook(() => useUpdatePreference(), { wrapper });
    act(() => {
      result.current.mutate({ key: 'weight_unit', value: 'kg' });
    });
    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.isError).toBe(true);
  });

  it('uses null userId when auth cache is empty', async () => {
    mockUpdate.mockResolvedValue({
      weight_unit: 'lbs',
      notify_achievement: true,
      notify_milestone: true,
      notify_streak: true,
    });
    // No AUTH_QUERY_KEY seeded — userId will be null, scoping to ['preferences', null].
    function wrapperNoAuth({ children }: { children: ReactNode }) {
      const qc = new QueryClient({
        defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
      });
      return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
    }
    const { result } = renderHook(() => useUpdatePreference(), { wrapper: wrapperNoAuth });
    act(() => {
      result.current.mutate({ key: 'weight_unit', value: 'lbs' });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockUpdate).toHaveBeenCalledWith('weight_unit', 'lbs');
  });

  it('handles error gracefully when there is no cached snapshot', async () => {
    mockUpdate.mockRejectedValue(new Error('Network failure'));
    // Wrapper with no preferences seeded — snapshot will be undefined on onMutate.
    function wrapperNoPrefs({ children }: { children: ReactNode }) {
      const qc = new QueryClient({
        defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
      });
      qc.setQueryData(AUTH_QUERY_KEY, { user_id: USER_ID });
      return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
    }

    const { result } = renderHook(() => useUpdatePreference(), { wrapper: wrapperNoPrefs });
    act(() => {
      result.current.mutate({ key: 'weight_unit', value: 'kg' });
    });
    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.isError).toBe(true);
  });
});
