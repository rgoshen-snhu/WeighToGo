import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import * as weightClientModule from '../api/weight-client';
import { useWeightEntries } from './useWeightEntries';

const mockList: weightClientModule.WeightEntryListResponse = {
  items: [
    {
      entry_id: 1,
      weight_value: 175.5,
      weight_unit: 'lbs',
      observation_date: '2026-05-20',
      notes: null,
      created_at: '2026-05-20T12:00:00Z',
      updated_at: '2026-05-20T12:00:00Z',
    },
  ],
  next_cursor: null,
};

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}

describe('useWeightEntries', () => {
  beforeEach(() => {
    vi.spyOn(weightClientModule.weightClient, 'list').mockResolvedValue(mockList);
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('returns items on success', async () => {
    const { result } = renderHook(() => useWeightEntries(), { wrapper });
    await waitFor(() => expect(result.current.data).toBeDefined());
    expect(result.current.data?.pages[0]?.items).toHaveLength(1);
  });

  it('sets isLoading=true while fetching', () => {
    const { result } = renderHook(() => useWeightEntries(), { wrapper });
    expect(result.current.isLoading).toBe(true);
  });

  it('exposes hasNextPage=false when next_cursor is null', async () => {
    const { result } = renderHook(() => useWeightEntries(), { wrapper });
    await waitFor(() => expect(result.current.data).toBeDefined());
    expect(result.current.hasNextPage).toBe(false);
  });
});
