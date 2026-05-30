/**
 * Tests for useVisibleAchievements — the single toggle-enforcement home [G10].
 */
import { renderHook } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import type { AchievementRecord } from '../schemas/achievement';
import { useVisibleAchievements } from './useVisibleAchievements';

const mockPreferences = {
  weightUnit: 'lbs' as const,
  notifyAchievement: true,
  notifyMilestone: true,
  notifyStreak: true,
};

vi.mock('../../../contexts/PreferencesContext', () => ({
  usePreferences: () => ({ preferences: mockPreferences }),
}));

const goalReached: AchievementRecord = {
  achievement_id: 1,
  goal_id: 10,
  achievement_type: 'goal_reached',
  threshold: null,
  earned_at: '2026-05-29T07:00:00Z',
};

const milestone: AchievementRecord = {
  achievement_id: 2,
  goal_id: 10,
  achievement_type: 'milestone',
  threshold: 5,
  earned_at: '2026-05-29T07:00:00Z',
};

const streak: AchievementRecord = {
  achievement_id: 3,
  goal_id: 10,
  achievement_type: 'streak',
  threshold: 7,
  earned_at: '2026-05-29T07:00:00Z',
};

describe('useVisibleAchievements', () => {
  it('returns all achievements when both toggles are on', () => {
    mockPreferences.notifyAchievement = true;
    mockPreferences.notifyMilestone = true;
    const { result } = renderHook(() => useVisibleAchievements([goalReached, milestone]));
    expect(result.current).toHaveLength(2);
  });

  it('suppresses goal_reached when notifyAchievement is false', () => {
    mockPreferences.notifyAchievement = false;
    mockPreferences.notifyMilestone = true;
    const { result } = renderHook(() => useVisibleAchievements([goalReached, milestone]));
    expect(result.current.find((a) => a.achievement_type === 'goal_reached')).toBeUndefined();
    expect(result.current.find((a) => a.achievement_type === 'milestone')).toBeDefined();
  });

  it('suppresses milestone when notifyMilestone is false', () => {
    mockPreferences.notifyAchievement = true;
    mockPreferences.notifyMilestone = false;
    const { result } = renderHook(() => useVisibleAchievements([goalReached, milestone]));
    expect(result.current.find((a) => a.achievement_type === 'milestone')).toBeUndefined();
    expect(result.current.find((a) => a.achievement_type === 'goal_reached')).toBeDefined();
  });

  it('returns empty list when both toggles are off', () => {
    mockPreferences.notifyAchievement = false;
    mockPreferences.notifyMilestone = false;
    const { result } = renderHook(() => useVisibleAchievements([goalReached, milestone]));
    expect(result.current).toHaveLength(0);
  });

  it('returns empty list when input is empty', () => {
    mockPreferences.notifyAchievement = true;
    mockPreferences.notifyMilestone = true;
    const { result } = renderHook(() => useVisibleAchievements([]));
    expect(result.current).toHaveLength(0);
  });

  it('shows streak when notifyStreak is on', () => {
    mockPreferences.notifyStreak = true;
    const { result } = renderHook(() => useVisibleAchievements([streak]));
    expect(result.current).toHaveLength(1);
  });

  it('suppresses streak when notifyStreak is false', () => {
    mockPreferences.notifyStreak = false;
    const { result } = renderHook(() => useVisibleAchievements([streak]));
    expect(result.current).toHaveLength(0);
    mockPreferences.notifyStreak = true; // restore for subsequent tests
  });

  it('passes through unknown achievement types (future-proofing)', () => {
    mockPreferences.notifyAchievement = true;
    mockPreferences.notifyMilestone = true;
    // Cast to AchievementRecord for test purposes — covers the fallback `return true` branch.
    const unknown = {
      ...goalReached,
      achievement_id: 99,
      achievement_type: 'future_type' as unknown as AchievementRecord['achievement_type'],
    } as AchievementRecord;
    const { result } = renderHook(() => useVisibleAchievements([unknown]));
    expect(result.current).toHaveLength(1);
  });
});
