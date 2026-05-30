import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import type { GoalRecord } from '../api/goal-client';
import { GoalHistoryList } from './GoalHistoryList';

const ACHIEVED: GoalRecord = {
  goal_id: 1,
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
};

const ABANDONED: GoalRecord = {
  ...ACHIEVED,
  goal_id: 2,
  is_achieved: false,
  achieved_at: null,
};

describe('GoalHistoryList', () => {
  it('shows an empty-state message when there are no past goals', () => {
    render(<GoalHistoryList goals={[]} />);
    expect(screen.getByText(/no past goals/i)).toBeInTheDocument();
  });

  it('renders an achieved goal with an "Achieved" outcome label', () => {
    render(<GoalHistoryList goals={[ACHIEVED]} />);
    expect(screen.getByText(/achieved/i)).toBeInTheDocument();
    expect(screen.getByText(/200/)).toBeInTheDocument();
    expect(screen.getByText(/150/)).toBeInTheDocument();
  });

  it('renders an abandoned goal with an "Abandoned" outcome label', () => {
    render(<GoalHistoryList goals={[ABANDONED]} />);
    expect(screen.getByText(/abandoned/i)).toBeInTheDocument();
  });

  it('exposes the history as an accessible list', () => {
    render(<GoalHistoryList goals={[ACHIEVED, ABANDONED]} />);
    expect(screen.getByRole('list', { name: /goal history/i })).toBeInTheDocument();
    expect(screen.getAllByRole('listitem')).toHaveLength(2);
  });
});
