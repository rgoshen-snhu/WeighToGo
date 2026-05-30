import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import * as dashboardClientModule from '../api/dashboard-client';
import { useDashboardSummary } from './useDashboardSummary';

const mockSummary: dashboardClientModule.DashboardSummaryResponse = {
  latest_entry: null,
  total_entries: 0,
  active_goal: null,
  rate_of_change: { weekly_rate: null, unit: null, reason: 'insufficient_data' },
  trend: [],
};

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}

describe('useDashboardSummary', () => {
  beforeEach(() => {
    vi.spyOn(dashboardClientModule.dashboardClient, 'summary').mockResolvedValue(mockSummary);
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('returns summary data on success', async () => {
    const { result } = renderHook(() => useDashboardSummary(), { wrapper });
    await waitFor(() => expect(result.current.data).toBeDefined());
    expect(result.current.data?.total_entries).toBe(0);
  });

  it('is loading initially', () => {
    const { result } = renderHook(() => useDashboardSummary(), { wrapper });
    expect(result.current.isLoading).toBe(true);
  });
});
