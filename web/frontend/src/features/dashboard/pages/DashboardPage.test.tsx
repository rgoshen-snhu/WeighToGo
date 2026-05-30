import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { dashboardClient } from '../api/dashboard-client';
import type { DashboardSummaryResponse } from '../api/dashboard-client';
import { DashboardPage } from './DashboardPage';

const noTrend = {
  rate_of_change: { weekly_rate: null, unit: null, reason: 'insufficient_data' },
  trend: [],
} satisfies Pick<DashboardSummaryResponse, 'rate_of_change' | 'trend'>;

const emptySummary: DashboardSummaryResponse = {
  latest_entry: null,
  total_entries: 0,
  active_goal: null,
  ...noTrend,
};

const populatedSummary: DashboardSummaryResponse = {
  latest_entry: {
    entry_id: 1,
    weight_value: 175.5,
    weight_unit: 'lbs',
    observation_date: '2026-05-20',
    notes: null,
    created_at: '2026-05-20T12:00:00Z',
    updated_at: '2026-05-20T12:00:00Z',
  },
  total_entries: 1,
  active_goal: null,
  rate_of_change: { weekly_rate: -0.8, unit: 'lbs', reason: null },
  trend: [{ observation_date: '2026-05-20', weight_value: 175.5, weight_unit: 'lbs' }],
};

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe('DashboardPage', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows empty state CTA when total_entries is 0', async () => {
    vi.spyOn(dashboardClient, 'summary').mockResolvedValue(emptySummary);
    render(<DashboardPage />, { wrapper });
    await waitFor(() => expect(screen.getByText(/add your first entry/i)).toBeInTheDocument());
  });

  it('shows the three cards when entries exist', async () => {
    vi.spyOn(dashboardClient, 'summary').mockResolvedValue(populatedSummary);
    render(<DashboardPage />, { wrapper });
    await waitFor(() =>
      expect(screen.getByRole('heading', { name: /175\.5 lbs/i })).toBeInTheDocument(),
    );
    expect(screen.getByText(/goal progress/i)).toBeInTheDocument();
  });

  it('shows the rate-of-change card and trend chart when entries exist', async () => {
    vi.spyOn(dashboardClient, 'summary').mockResolvedValue(populatedSummary);
    render(<DashboardPage />, { wrapper });
    await waitFor(() => expect(screen.getByText(/rate of change/i)).toBeInTheDocument());
    expect(screen.getByRole('figure', { name: /weight trend/i })).toBeInTheDocument();
  });

  it('has an accessible heading', async () => {
    vi.spyOn(dashboardClient, 'summary').mockResolvedValue(emptySummary);
    render(<DashboardPage />, { wrapper });
    expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
  });

  it('passes the loading state through to the trend chart', () => {
    // Never resolves, so the query stays in its loading state.
    vi.spyOn(dashboardClient, 'summary').mockReturnValue(new Promise(() => {}));
    render(<DashboardPage />, { wrapper });
    // While loading, the chart renders its loading state, not the figure.
    expect(screen.queryByRole('figure', { name: /weight trend/i })).not.toBeInTheDocument();
  });

  it('passes the error state through to the trend chart', async () => {
    vi.spyOn(dashboardClient, 'summary').mockRejectedValue(new Error('boom'));
    render(<DashboardPage />, { wrapper });
    await waitFor(() => expect(screen.getByText(/failed to load trend data/i)).toBeInTheDocument());
  });

  it('shows goal card when total_entries is 0 but active_goal is set', async () => {
    const summaryWithGoalNoEntries: DashboardSummaryResponse = {
      latest_entry: null,
      total_entries: 0,
      active_goal: {
        goal: {
          goal_id: 1,
          user_id: 1,
          target_value: 150,
          target_unit: 'lbs',
          start_value: 200,
          goal_type: 'lose',
          target_date: null,
          is_active: true,
          is_achieved: false,
          achieved_at: null,
          created_at: '2026-05-28T00:00:00Z',
          updated_at: '2026-05-28T00:00:00Z',
        },
        progress_percent: null,
        current_value: null,
      },
      ...noTrend,
    };
    vi.spyOn(dashboardClient, 'summary').mockResolvedValue(summaryWithGoalNoEntries);
    render(<DashboardPage />, { wrapper });
    await waitFor(() => expect(screen.getByText(/goal progress/i)).toBeInTheDocument());
    expect(screen.queryByText(/add your first entry/i)).not.toBeInTheDocument();
  });
});
