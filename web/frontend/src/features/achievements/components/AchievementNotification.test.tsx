import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import type { AchievementRecord } from '../schemas/achievement';
import { AchievementNotification } from './AchievementNotification';

const milestone5: AchievementRecord = {
  achievement_id: 1,
  goal_id: 7,
  achievement_type: 'milestone',
  threshold: 5,
  earned_at: '2026-01-01T00:00:00Z',
};

const goalReached: AchievementRecord = {
  achievement_id: 2,
  goal_id: 7,
  achievement_type: 'goal_reached',
  threshold: null,
  earned_at: '2026-01-01T00:00:00Z',
};

const streak7: AchievementRecord = {
  achievement_id: 4,
  goal_id: 7,
  achievement_type: 'streak',
  threshold: 7,
  earned_at: '2026-01-07T00:00:00Z',
};

describe('AchievementNotification', () => {
  it('renders nothing when achievements array is empty', () => {
    const { container } = render(
      <AchievementNotification achievements={[]} onDismissOne={() => undefined} />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('shows milestone toast copy when first achievement is a milestone', () => {
    render(<AchievementNotification achievements={[milestone5]} onDismissOne={() => undefined} />);
    expect(screen.getByText(/5 lb milestone/i)).toBeInTheDocument();
  });

  it('shows goal reached copy for goal_reached achievement', () => {
    render(<AchievementNotification achievements={[goalReached]} onDismissOne={() => undefined} />);
    expect(screen.getByText(/goal reached/i)).toBeInTheDocument();
  });

  it('shows streak toast copy for a streak achievement', () => {
    render(<AchievementNotification achievements={[streak7]} onDismissOne={() => undefined} />);
    expect(screen.getByText(/7-day logging streak/i)).toBeInTheDocument();
  });

  it('falls back to plain streak copy when threshold is null (no NaN)', () => {
    const nullStreak: AchievementRecord = { ...streak7, achievement_id: 5, threshold: null };
    render(<AchievementNotification achievements={[nullStreak]} onDismissOne={() => undefined} />);
    expect(screen.getByText('Logging streak! Keep it up.')).toBeInTheDocument();
  });

  it('falls back to plain milestone copy when threshold is null (no NaN)', () => {
    const nullMilestone: AchievementRecord = { ...milestone5, achievement_id: 6, threshold: null };
    render(
      <AchievementNotification achievements={[nullMilestone]} onDismissOne={() => undefined} />,
    );
    expect(screen.getByText('Milestone reached!')).toBeInTheDocument();
  });

  it('has role status for ARIA live region (NFR-A-3)', () => {
    render(<AchievementNotification achievements={[milestone5]} onDismissOne={() => undefined} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('does not call onDismissOne when there are no achievements', () => {
    const onDismissOne = vi.fn();
    render(<AchievementNotification achievements={[]} onDismissOne={onDismissOne} />);
    expect(onDismissOne).not.toHaveBeenCalled();
  });
});
