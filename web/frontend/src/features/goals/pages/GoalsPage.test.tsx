import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import * as goalClientModule from '../api/goal-client';
import * as weightClientModule from '../../weight/api/weight-client';
import { GoalsPage } from './GoalsPage';

const prefs = { current: 'lbs' as 'lbs' | 'kg' };
vi.mock('../../../contexts/PreferencesContext', () => ({
  usePreferences: () => ({
    preferences: {
      weightUnit: prefs.current,
      notifyAchievement: true,
      notifyMilestone: true,
      notifyStreak: true,
    },
    isLoading: false,
    setPreference: vi.fn(),
  }),
}));

// Re-used mock to suppress abandon/update mutations
function mockMutations() {
  vi.spyOn(goalClientModule.goalClient, 'abandon').mockResolvedValue(undefined);
  vi.spyOn(goalClientModule.goalClient, 'update').mockResolvedValue({
    goal_id: 1,
    user_id: 1,
    target_value: 145,
    target_unit: 'lbs',
    start_value: 200,
    goal_type: 'lose',
    target_date: null,
    is_active: true,
    is_achieved: false,
    achieved_at: null,
    created_at: '2026-05-28T00:00:00Z',
    updated_at: '2026-05-28T00:00:00Z',
  });
}

function Wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <MemoryRouter>
      <QueryClientProvider client={qc}>{children}</QueryClientProvider>
    </MemoryRouter>
  );
}

const MOCK_ACTIVE_GOAL: goalClientModule.GoalRecord = {
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
};

beforeEach(() => {
  prefs.current = 'lbs';
  vi.spyOn(weightClientModule.weightClient, 'list').mockResolvedValue({
    items: [],
    next_cursor: null,
  });
  // GoalsPage now fetches goal history via goalClient.list({ history: true });
  // default to an empty history so existing tests don't hit an unstubbed call.
  vi.spyOn(goalClientModule.goalClient, 'list').mockResolvedValue({ goals: [] });
});

describe('GoalsPage', () => {
  it('shows goal creation form when no active goal', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: null,
      progress_percent: null,
      current_value: null,
    });
    render(<GoalsPage />, { wrapper: Wrapper });
    await screen.findByRole('button', { name: /set goal/i });
    expect(screen.getByRole('button', { name: /set goal/i })).toBeInTheDocument();
  });

  it('fetches the latest entry to pre-populate start_value in create mode', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: null,
      progress_percent: null,
      current_value: null,
    });
    const listSpy = vi.spyOn(weightClientModule.weightClient, 'list').mockResolvedValue({
      items: [
        {
          entry_id: 1,
          weight_value: 185,
          weight_unit: 'lbs',
          observation_date: '2026-05-28',
          notes: null,
          created_at: '2026-05-28T00:00:00Z',
          updated_at: '2026-05-28T00:00:00Z',
        },
      ],
      next_cursor: null,
    });
    render(<GoalsPage />, { wrapper: Wrapper });
    await screen.findByRole('button', { name: /set goal/i });
    // The useEffect fires and calls weightClient.list with limit=1
    expect(listSpy).toHaveBeenCalledWith({ limit: 1 });
  });

  it('shows goal details and progress bar when active goal exists', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: MOCK_ACTIVE_GOAL,
      progress_percent: 50,
      current_value: 175,
    });
    render(<GoalsPage />, { wrapper: Wrapper });
    await screen.findByText(/200/);
    expect(screen.getByText(/150/)).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('converts the active-goal summary weights to the preferred unit (kg)', async () => {
    prefs.current = 'kg';
    // Goal stored in lbs (start 200, target 150) must render in kg so the
    // summary is unit-consistent with the rest of the session after a switch:
    // 200 lb -> 90.7 kg, 150 lb -> 68.0 kg.
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: MOCK_ACTIVE_GOAL,
      progress_percent: 50,
      current_value: 175,
    });
    render(<GoalsPage />, { wrapper: Wrapper });
    await screen.findByText(/90\.7 kg → 68\.0 kg/);
    expect(screen.queryByText(/200 lbs/)).not.toBeInTheDocument();
  });

  it('shows error alert when the query fails', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockRejectedValue(new Error('Network'));
    render(<GoalsPage />, { wrapper: Wrapper });
    await screen.findByText(/failed to load/i);
  });

  it('shows edit form when edit goal button is clicked', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: MOCK_ACTIVE_GOAL,
      progress_percent: null,
      current_value: null,
    });
    render(<GoalsPage />, { wrapper: Wrapper });
    const editBtn = await screen.findByRole('button', { name: /edit goal/i });
    await userEvent.click(editBtn);
    expect(screen.getByRole('button', { name: /update goal/i })).toBeInTheDocument();
  });

  it('returns to goal view when cancel is clicked in edit mode', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: MOCK_ACTIVE_GOAL,
      progress_percent: null,
      current_value: null,
    });
    render(<GoalsPage />, { wrapper: Wrapper });
    const editBtn = await screen.findByRole('button', { name: /edit goal/i });
    await userEvent.click(editBtn);
    const cancelBtn = screen.getByRole('button', { name: /cancel/i });
    await userEvent.click(cancelBtn);
    expect(screen.getByRole('button', { name: /edit goal/i })).toBeInTheDocument();
  });

  it('shows null-progress bar when active goal but no entries', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: MOCK_ACTIVE_GOAL,
      progress_percent: null,
      current_value: null,
    });
    render(<GoalsPage />, { wrapper: Wrapper });
    await screen.findByText(/200/);
    expect(screen.getByText(/no entries yet/i)).toBeInTheDocument();
  });

  it('shows target date when goal has one', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: { ...MOCK_ACTIVE_GOAL, target_date: '2026-12-31' },
      progress_percent: null,
      current_value: null,
    });
    render(<GoalsPage />, { wrapper: Wrapper });
    await screen.findByText(/2026-12-31/);
  });

  it('calls goalClient.update when edit form is submitted', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: MOCK_ACTIVE_GOAL,
      progress_percent: null,
      current_value: null,
    });
    mockMutations();
    render(<GoalsPage />, { wrapper: Wrapper });
    const editBtn = await screen.findByRole('button', { name: /edit goal/i });
    await userEvent.click(editBtn);
    const targetInput = screen.getByLabelText(/target weight/i);
    await userEvent.clear(targetInput);
    await userEvent.type(targetInput, '145');
    await userEvent.click(screen.getByRole('button', { name: /update goal/i }));
    expect(goalClientModule.goalClient.update).toHaveBeenCalled();
  });

  it('calls goalClient.abandon when Abandon goal is clicked', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: MOCK_ACTIVE_GOAL,
      progress_percent: null,
      current_value: null,
    });
    mockMutations();
    render(<GoalsPage />, { wrapper: Wrapper });
    const abandonBtn = await screen.findByRole('button', { name: /abandon goal/i });
    await userEvent.click(abandonBtn);
    expect(goalClientModule.goalClient.abandon).toHaveBeenCalledWith(1);
  });

  it('shows action error when handleCreate fails with non-409', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: null,
      progress_percent: null,
      current_value: null,
    });
    vi.spyOn(goalClientModule.goalClient, 'create').mockRejectedValue(
      Object.assign(new Error('Server error'), { status: 500 }),
    );
    render(<GoalsPage />, { wrapper: Wrapper });
    const submitBtn = await screen.findByRole('button', { name: /set goal/i });
    // Fill required fields so the form passes Zod validation
    await userEvent.type(screen.getByLabelText(/starting weight/i), '200');
    await userEvent.type(screen.getByLabelText(/target weight/i), '150');
    await userEvent.click(submitBtn);
    await screen.findByText(/server error|unexpected error/i);
  });

  it('shows action error when handleUpdate fails', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: MOCK_ACTIVE_GOAL,
      progress_percent: null,
      current_value: null,
    });
    vi.spyOn(goalClientModule.goalClient, 'update').mockRejectedValue(
      Object.assign(new Error('Update failed'), { status: 500 }),
    );
    render(<GoalsPage />, { wrapper: Wrapper });
    const editBtn = await screen.findByRole('button', { name: /edit goal/i });
    await userEvent.click(editBtn);
    const targetInput = screen.getByLabelText(/target weight/i);
    await userEvent.clear(targetInput);
    await userEvent.type(targetInput, '145');
    await userEvent.click(screen.getByRole('button', { name: /update goal/i }));
    await screen.findByText(/server error|unexpected error/i);
  });

  it('shows action error when handleAbandon fails', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: MOCK_ACTIVE_GOAL,
      progress_percent: null,
      current_value: null,
    });
    vi.spyOn(goalClientModule.goalClient, 'abandon').mockRejectedValue(
      Object.assign(new Error('Abandon failed'), { status: 500 }),
    );
    render(<GoalsPage />, { wrapper: Wrapper });
    const abandonBtn = await screen.findByRole('button', { name: /abandon goal/i });
    await userEvent.click(abandonBtn);
    await screen.findByText(/server error|unexpected error/i);
  });

  it('renders past goals in a history section', async () => {
    vi.spyOn(goalClientModule.goalClient, 'getActive').mockResolvedValue({
      goal: null,
      progress_percent: null,
      current_value: null,
    });
    vi.spyOn(goalClientModule.goalClient, 'list').mockResolvedValue({
      goals: [
        {
          goal_id: 99,
          user_id: 1,
          target_value: 150,
          target_unit: 'lbs',
          start_value: 200,
          goal_type: 'lose',
          target_date: null,
          is_active: false,
          is_achieved: true,
          achieved_at: '2026-02-01T00:00:00Z',
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-02-01T00:00:00Z',
        },
      ],
    });
    render(<GoalsPage />, { wrapper: Wrapper });
    expect(await screen.findByRole('list', { name: /goal history/i })).toBeInTheDocument();
    expect(screen.getByText(/achieved/i)).toBeInTheDocument();
  });
});
