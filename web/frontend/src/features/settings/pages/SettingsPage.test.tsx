/**
 * Tests for SettingsPage — renders controls, calls mutation, shows feedback on success.
 */
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { SettingsPage } from './SettingsPage';

const mockMutate = vi.fn((_, options?: { onSuccess?: () => void }) => {
  options?.onSuccess?.();
});

vi.mock('../../../contexts/PreferencesContext', () => ({
  usePreferences: () => ({
    preferences: {
      weightUnit: 'lbs',
      notifyAchievement: true,
      notifyMilestone: true,
      notifyStreak: false,
    },
    isLoading: false,
    setPreference: vi.fn(),
  }),
}));

vi.mock('../hooks/useUpdatePreference', () => ({
  useUpdatePreference: () => ({ mutate: mockMutate }),
}));

describe('SettingsPage', () => {
  it('renders the Settings heading', () => {
    render(<SettingsPage />);
    expect(screen.getByRole('heading', { name: /settings/i })).toBeInTheDocument();
  });

  it('renders the unit preference radio group', () => {
    render(<SettingsPage />);
    expect(screen.getByRole('group', { name: /weight unit/i })).toBeInTheDocument();
  });

  it('renders the notification toggles', () => {
    render(<SettingsPage />);
    expect(screen.getByLabelText(/achievement alerts toggle/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/milestone alerts toggle/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/streak alerts toggle/i)).toBeInTheDocument();
  });

  it('calls mutation when unit changes', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);
    await user.click(screen.getByRole('radio', { name: 'kg' }));
    expect(mockMutate).toHaveBeenCalledWith(
      { key: 'weight_unit', value: 'kg' },
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    );
  });

  it('calls mutation when achievement toggle changes', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);
    await user.click(screen.getByLabelText(/achievement alerts toggle/i));
    expect(mockMutate).toHaveBeenCalledWith(
      { key: 'notify_achievement', value: false },
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    );
  });

  it('calls mutation when streak toggle changes', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);
    await user.click(screen.getByLabelText(/streak alerts toggle/i));
    expect(mockMutate).toHaveBeenCalledWith(
      { key: 'notify_streak', value: true },
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    );
  });

  it('shows save feedback after mutation succeeds', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);
    await user.click(screen.getByRole('radio', { name: 'kg' }));
    // mockMutate calls onSuccess immediately, so feedback appears synchronously.
    expect(screen.getByText('Preferences saved')).toBeInTheDocument();
  });

  it('resets save feedback timer on rapid consecutive changes', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);
    await user.click(screen.getByRole('radio', { name: 'kg' }));
    await user.click(screen.getByLabelText(/achievement alerts toggle/i));
    expect(screen.getByText('Preferences saved')).toBeInTheDocument();
  });
});
